import customtkinter as ctk
from tkinter import messagebox, filedialog
import psycopg2
import pandas as pd
from datetime import datetime, timedelta
import os
from PIL import Image as PILImage
import matplotlib.pyplot as plt
import numpy as np

# Librerías para PDF Profesional
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image as RLImage, PageBreak
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

class ModuloInformes:
    def __init__(self, master, db_config):
        self.master = master
        self.db_config = db_config
        self.archivo_grafico_temp = "temp_chart_report.png"
        self.df_actual = None

    def mostrar(self, volver_callback):
        """Renderiza la interfaz del módulo"""
        for widget in self.master.winfo_children():
            widget.destroy()

        # CABECERA
        header = ctk.CTkFrame(self.master, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=15)
        ctk.CTkButton(header, text="← Volver", command=volver_callback, width=90).pack(side="left")
        ctk.CTkLabel(header, text="UNIDAD DE INTELIGENCIA Y ANÁLISIS VIAL", 
                     font=ctk.CTkFont(size=22, weight="bold"), text_color="#0B3526").pack(side="left", padx=20)

        # MARCO PRINCIPAL
        main_frame = ctk.CTkFrame(self.master, fg_color="white", corner_radius=15)
        main_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # PANEL IZQUIERDO: CONFIGURACIÓN
        left_panel = ctk.CTkFrame(main_frame, fg_color="#f0f0f0", width=300)
        left_panel.pack(side="left", fill="y", padx=10, pady=10)
        left_panel.pack_propagate(False)

        ctk.CTkLabel(left_panel, text="CONFIGURACIÓN", font=("Arial", 14, "bold")).pack(pady=10)
        
        self.combo_tipo = self.crear_item(left_panel, "Enfoque del Análisis:", 
            ["General de Seguridad", "Puntos Negros", "Factores Climatológicos", 
             "Análisis de Gravedad", "Por Causa de Accidente", "Por Franja Horaria"])
        
        self.combo_rango = self.crear_item(left_panel, "Periodo de Datos:", 
            ["Todo el histórico", "Última Semana", "Último Mes", "Últimos 3 Meses"])

        ctk.CTkButton(left_panel, text="GENERAR ANÁLISIS 🖥️", fg_color="#1b5e46", height=45,
                     font=("Arial", 12, "bold"), command=self.analizar_en_pantalla).pack(pady=20, padx=20, fill="x")

        ctk.CTkLabel(left_panel, text="EXPORTAR RECURSOS", font=("Arial", 12, "bold"), text_color="#555").pack(pady=(10, 5))
        self.btn_pdf = ctk.CTkButton(left_panel, text="Informe PDF 📄", fg_color="#444", state="disabled", command=self.exportar_pdf_accion)
        self.btn_pdf.pack(pady=5, padx=20, fill="x")
        self.btn_excel = ctk.CTkButton(left_panel, text="Informe Excel 📊", fg_color="#444", state="disabled", command=self.exportar_excel_accion)
        self.btn_excel.pack(pady=5, padx=20, fill="x")

        # PANEL DERECHO: VISUALIZACIÓN DINÁMICA
        self.right_container = ctk.CTkFrame(main_frame, fg_color="#1e1e1e", corner_radius=10)
        self.right_container.pack(side="right", fill="both", expand=True, padx=10, pady=10)
        
        self.mostrar_imagen_bienvenida()

    def crear_item(self, p, t, v):
        ctk.CTkLabel(p, text=t, font=("Arial", 12)).pack(pady=(10,0), padx=20, anchor="w")
        cb = ctk.CTkComboBox(p, values=v, width=240)
        cb.set(v[0])
        cb.pack(pady=5, padx=20)
        return cb

    def mostrar_imagen_bienvenida(self):
        """Muestra la imagen ajustada dinámicamente al contenedor"""
        for widget in self.right_container.winfo_children():
            widget.destroy()
        self.right_container.grid_rowconfigure(0, weight=1)
        self.right_container.grid_columnconfigure(0, weight=1)

        ruta_img = os.path.join(os.path.dirname(__file__), "imagen_modulo_informes.png") 
        if os.path.exists(ruta_img):
            img_pil = PILImage.open(ruta_img)
            img_ctk = ctk.CTkImage(light_image=img_pil, dark_image=img_pil)
            label_img = ctk.CTkLabel(self.right_container, image=img_ctk, text="")
            label_img.grid(row=0, column=0, sticky="nsew")
            
            def redimensionar(event):
                img_ctk.configure(size=(event.width, event.height))
            label_img.image = img_ctk 
            self.right_container.bind("<Configure>", redimensionar)
        else:
            ctk.CTkLabel(self.right_container, text="CENTRO DE ANÁLISIS\nSeleccione un enfoque para comenzar", 
                         text_color="white", font=("Arial", 16)).grid(row=0, column=0)

    def obtener_datos(self):
        """Extracción total de datos según periodo"""
        rango = self.combo_rango.get()
        filtro = ""
        hoy = datetime.now()
        if rango == "Última Semana": filtro = f" AND a.fecha >= '{(hoy - timedelta(days=7)).date()}'"
        elif rango == "Último Mes": filtro = f" AND a.fecha >= '{(hoy - timedelta(days=30)).date()}'"
        elif rango == "Últimos 3 Meses": filtro = f" AND a.fecha >= '{(hoy - timedelta(days=90)).date()}'"

        query = f"""SELECT a.fecha, a.hora, carr.nombre as carretera, cau.descripcion as causa, 
                           cl.descripcion as clima, g.nivel as gravedad, a.num_fallecidos, a.num_heridos
                    FROM accidentes a 
                    LEFT JOIN carreteras carr ON a.carretera_id = carr.id
                    LEFT JOIN causas cau ON a.causa_id = cau.id
                    LEFT JOIN clima cl ON a.clima_id = cl.id
                    LEFT JOIN gravedad g ON a.gravedad_id = g.id
                    WHERE 1=1 {filtro}"""
        try:
            conn = psycopg2.connect(**self.db_config)
            df = pd.read_sql(query, conn)
            conn.close()
            return df
        except Exception as e:
            messagebox.showerror("Error DB", f"No se pudo conectar: {e}")
            return None

    def asignar_franja(self, hora_obj):
        """Asignación de franjas horarias"""
        h = hora_obj.hour
        if 8 <= h < 14: return "Mañana"
        elif 14 <= h < 22: return "Tarde"
        else: return "Noche"

    def generar_estudio_profundo(self, df):
        """Generador lógico de informes técnicos detallados"""
        tipo = self.combo_tipo.get()
        total_acc = len(df)
        fallecidos = df['num_fallecidos'].sum()
        heridos = df['num_heridos'].sum()
        
        texto = f"INFORME TÉCNICO DE SEGURIDAD VIAL | ÁVILA | {datetime.now().strftime('%d/%m/%Y')}\n"
        texto += "="*85 + "\n"
        texto += f"ENFOQUE SELECCIONADO: {tipo.upper()}\n"
        texto += f"VOLUMEN DE DATOS PROCESADOS: {total_acc} incidentes\n"
        texto += f"BALANCE DE VÍCTIMAS: {fallecidos} fallecidos y {heridos} heridos totales.\n"
        texto += "="*85 + "\n\n"

        if tipo == "General de Seguridad":
            texto += "1. ANÁLISIS MULTIVARIABLE DEL PERIODO\n"
            texto += f"- Siniestralidad por Vías: Se han visto afectadas {df['carretera'].nunique()} carreteras.\n"
            texto += f"- Factor Meteorológico: El clima '{df['clima'].mode()[0]}' está presente en la mayoría de casos.\n"
            texto += f"- Gravedad Media: La categoría predominante es '{df['gravedad'].mode()[0]}'.\n"
            texto += f"- Causa Raíz: La mayoría de incidentes se atribuyen a '{df['causa'].mode()[0]}'.\n\n"
            texto += "2. VALORACIÓN TÉCNICA\nSe observa una correlación directa entre los factores de la vía y la lesividad."

        elif tipo == "Puntos Negros":
            texto += "1. IDENTIFICACIÓN DE TRAMOS DE ALTA SINIESTRALIDAD (TAS)\n"
            texto += "Se listan las 5 vías con mayor concentración de incidentes en el periodo:\n\n"
            top_5 = df['carretera'].value_counts().head(5)
            for i, (via, count) in enumerate(top_5.items(), 1):
                f_via = df[df['carretera'] == via]['num_fallecidos'].sum()
                h_via = df[df['carretera'] == via]['num_heridos'].sum()
                texto += f"   [{i}] VÍA: {via} -> {count} accidentes ({f_via} fallecidos / {h_via} heridos)\n"
            texto += "\n2. RECOMENDACIÓN: Se sugiere auditoría de infraestructura en los puntos señalados."

        elif tipo == "Factores Climatológicos":
            texto += "1. ESTUDIO DE SINIESTRALIDAD POR CONDICIÓN METEOROLÓGICA\n"
            stats = df.groupby('clima').agg({'fecha':'count', 'num_fallecidos':'sum', 'num_heridos':'sum'})
            for clima, row in stats.iterrows():
                texto += f"- Condición: {clima}\n"
                texto += f"  Accidentes: {row['fecha']} | Fallecidos: {row['num_fallecidos']} | Heridos: {row['num_heridos']}\n"
            texto += "\n2. CONCLUSIÓN: Las condiciones adversas elevan el riesgo de accidentes mortales."

        elif tipo == "Análisis de Gravedad":
            texto += "1. DESGLOSE DE GRAVEDAD Y LESIVIDAD\n"
            grav_counts = df['gravedad'].value_counts()
            for g_tipo, count in grav_counts.items():
                texto += f"- Nivel {g_tipo}: {count} accidentes registrados.\n"
            texto += f"\n2. ACLARACIÓN TÉCNICA DE VÍCTIMAS\n"
            texto += f"Se han procesado {total_acc} incidentes. El total de {fallecidos} fallecidos indica una\n"
            texto += "tasa de letalidad de " + str(round(fallecidos/total_acc, 2)) + " víctimas por cada accidente.\n"

        elif tipo == "Por Causa de Accidente":
            texto += "1. ESTADÍSTICA DE CAUSALIDAD VS LESIVIDAD\n"
            causas = df.groupby('causa').agg({'num_fallecidos':'sum', 'num_heridos':'sum', 'fecha':'count'})
            for c, r in causas.sort_values(by='fecha', ascending=False).iterrows():
                texto += f"- {c}: {r['fecha']} casos. Impacto: {r['num_fallecidos']} muertos / {r['num_heridos']} heridos.\n"
            texto += "\n2. IMPACTO SOCIAL: Las causas humanas siguen siendo el factor crítico de riesgo."

        elif tipo == "Por Franja Horaria":
            df['franja'] = df['hora'].apply(self.asignar_franja)
            texto += "1. DISTRIBUCIÓN HORARIA ESTRATÉGICA\n"
            for f in ["Mañana", "Tarde", "Noche"]:
                sub = df[df['franja'] == f]
                texto += f"\n>>> FRANJA: {f.upper()} "
                if f == "Mañana": texto += "(08:00 - 14:00)\n"
                elif f == "Tarde": texto += "(14:00 - 22:00)\n"
                else: texto += "(22:00 - 08:00)\n"
                
                if not sub.empty:
                    texto += f"    * Incidentes: {len(sub)}\n"
                    texto += f"    * Causa Mayoritaria: {sub['causa'].mode()[0]}\n"
                    texto += f"    * Gravedad Crítica: {sub['gravedad'].mode()[0]}\n"
                    texto += f"    * Víctimas: {sub['num_fallecidos'].sum()} fallecidos / {sub['num_heridos'].sum()} heridos.\n"
            texto += "\n2. CONCLUSIÓN: Los picos de gravedad varían según la visibilidad y el flujo circulatorio."

        return texto

    def analizar_en_pantalla(self):
        """Muestra los resultados en la caja de texto"""
        self.df_actual = self.obtener_datos()
        if self.df_actual is None or self.df_actual.empty:
            messagebox.showwarning("Sin Datos", "No hay registros para este periodo.")
            return
            
        for widget in self.right_container.winfo_children():
            widget.destroy()
            
        self.right_panel = ctk.CTkTextbox(self.right_container, font=("Consolas", 12), 
                                         fg_color="#1e1e1e", text_color="#adff2f", border_width=1)
        self.right_panel.pack(fill="both", expand=True)
        self.right_panel.insert("0.0", self.generar_estudio_profundo(self.df_actual))
        
        self.btn_pdf.configure(state="normal", fg_color="#1b5e46")
        self.btn_excel.configure(state="normal", fg_color="#1b5e46")

    def exportar_excel_accion(self):
        """Genera un Excel profesional con formatos condicionales, anchos automáticos y colores pastel"""
        ruta = filedialog.asksaveasfilename(defaultextension=".xlsx", title="Guardar Informe Excel")
        if not ruta or self.df_actual is None: return

        tipo = self.combo_tipo.get()
        
        try:
            with pd.ExcelWriter(ruta, engine='xlsxwriter') as writer:
                # 1. PREPARACIÓN DE DATOS
                resumen_data = {
                    "INDICADOR": ["Tipo de Análisis", "Periodo Seleccionado", "Total Accidentes", "Total Fallecidos", "Total Heridos"],
                    "VALOR": [tipo, self.combo_rango.get(), len(self.df_actual), self.df_actual['num_fallecidos'].sum(), self.df_actual['num_heridos'].sum()]
                }
                df_resumen = pd.DataFrame(resumen_data)

                if tipo == "Puntos Negros":
                    df_analisis = self.df_actual.groupby('carretera').agg({'fecha':'count', 'num_fallecidos':'sum', 'num_heridos':'sum'}).sort_values(by='fecha', ascending=False).head(10)
                elif tipo == "Factores Climatológicos":
                    df_analisis = self.df_actual.groupby('clima').agg({'fecha':'count', 'num_fallecidos':'sum', 'num_heridos':'sum'})
                elif tipo == "Por Causa de Accidente":
                    df_analisis = self.df_actual.groupby('causa').agg({'fecha':'count', 'num_fallecidos':'sum', 'num_heridos':'sum'})
                elif tipo == "Por Franja Horaria":
                    self.df_actual['franja'] = self.df_actual['hora'].apply(self.asignar_franja)
                    df_analisis = self.df_actual.groupby('franja').agg({'fecha':'count', 'num_fallecidos':'sum', 'num_heridos':'sum'})
                else:
                    df_analisis = self.df_actual.groupby('gravedad').agg({'fecha':'count', 'num_fallecidos':'sum', 'num_heridos':'sum'})
                
                df_analisis = df_analisis.rename(columns={'fecha': 'Total Accidentes'}).reset_index()

                df_listado = self.df_actual.copy()
                df_listado['fecha'] = pd.to_datetime(df_listado['fecha']).dt.strftime('%d/%m/%Y')

                # 2. ESCRITURA DE HOJAS
                df_resumen.to_excel(writer, sheet_name='Resumen Ejecutivo', index=False)
                df_analisis.to_excel(writer, sheet_name='Análisis Detallado', index=False)
                df_listado.to_excel(writer, sheet_name='Listado Completo', index=False)

                workbook = writer.book
                colores_pastel = ['#FFD1DC', '#E0BBE4', '#BFFCC6', '#FFF5BA', '#FFDFBA', '#BAE1FF', '#F0EAD6']
                
                def aplicar_formato_profesional(sheet_name, df):
                    worksheet = writer.sheets[sheet_name]
                    for col_num, value in enumerate(df.columns.values):
                        column_len = max(len(str(value)), 10)
                        worksheet.set_column(col_num, col_num, column_len + 2)
                        color = colores_pastel[col_num % len(colores_pastel)]
                        formato_header = workbook.add_format({'bold': True, 'bg_color': color, 'border': 1, 'align': 'center'})
                        worksheet.write(0, col_num, value, formato_header)

                aplicar_formato_profesional('Resumen Ejecutivo', df_resumen)
                aplicar_formato_profesional('Análisis Detallado', df_analisis)
                aplicar_formato_profesional('Listado Completo', df_listado)

                # 4. ADJUNTAR GRÁFICO
                self.generar_grafico_para_archivo()
                worksheet_img = workbook.add_worksheet('Gráfico Estratégico')
                worksheet_img.insert_image('B2', self.archivo_grafico_temp)

            messagebox.showinfo("Éxito", f"Informe Excel '{tipo}' generado con éxito.")
            if os.path.exists(self.archivo_grafico_temp): os.remove(self.archivo_grafico_temp)
            
        except Exception as e:
            messagebox.showerror("Error Excel", f"No se pudo generar: {e}")

    def generar_grafico_para_archivo(self):
        """Genera el gráfico actual con colores variados para cada barra"""
        tipo = self.combo_tipo.get()
        plt.figure(figsize=(10, 6))
        
        # Lógica para obtener series y colores
        if tipo == "Por Franja Horaria":
            self.df_actual['franja'] = self.df_actual['hora'].apply(self.asignar_franja)
            serie = self.df_actual['franja'].value_counts().reindex(["Mañana", "Tarde", "Noche"]).dropna()
            colores = plt.cm.viridis(np.linspace(0, 1, len(serie)))
            serie.plot(kind='bar', color=colores, edgecolor='black')
        elif tipo == "Puntos Negros":
            serie = self.df_actual['carretera'].value_counts().head(8)
            colores = plt.cm.plasma(np.linspace(0, 1, len(serie)))
            serie.plot(kind='barh', color=colores, edgecolor='black')
        elif tipo == "Factores Climatológicos":
            serie = self.df_actual['clima'].value_counts()
            colores = plt.cm.Set3(np.linspace(0, 1, len(serie)))
            serie.plot(kind='pie', autopct='%1.1f%%', colors=colores, startangle=140)
        elif tipo == "Por Causa de Accidente":
            serie = self.df_actual['causa'].value_counts().head(10)
            colores = plt.cm.tab10(np.linspace(0, 1, len(serie)))
            serie.plot(kind='bar', color=colores, edgecolor='black')
        else:
            serie = self.df_actual['gravedad'].value_counts()
            colores = plt.cm.coolwarm(np.linspace(0, 1, len(serie)))
            serie.plot(kind='bar', color=colores, edgecolor='black')
            
        plt.title(f"Distribución: {tipo}", fontsize=14, fontweight='bold')
        plt.tight_layout()
        plt.savefig(self.archivo_grafico_temp, dpi=100)
        plt.close()

    def exportar_pdf_accion(self):
        ruta = filedialog.asksaveasfilename(defaultextension=".pdf", title="Guardar Informe PDF")
        if ruta and self.df_actual is not None:
            self.construir_pdf_profesional(ruta)
            messagebox.showinfo("Éxito", "Informe técnico PDF generado con éxito.")

    def construir_pdf_profesional(self, ruta):
        """Generación de PDF profesional"""
        doc = SimpleDocTemplate(ruta, pagesize=A4, rightMargin=50, leftMargin=50, topMargin=60, bottomMargin=50)
        styles = getSampleStyleSheet()
        elements = []

        style_title = ParagraphStyle(name='T', fontSize=24, alignment=1, fontName='Helvetica-Bold', leading=32, spaceAfter=40)
        style_h1 = ParagraphStyle(name='H1', fontSize=14, fontName='Helvetica-Bold', color=colors.HexColor("#0B3526"), spaceBefore=15, spaceAfter=10)
        style_body = ParagraphStyle(name='B', fontSize=10, fontName='Helvetica', alignment=4, leading=12)

        elements.append(Spacer(1, 2*inch))
        elements.append(Paragraph("INFORME ESTRATÉGICO DE SEGURIDAD VIAL", style_title))
        elements.append(Paragraph(f"TIPO: {self.combo_tipo.get().upper()}", styles['Normal']))
        elements.append(Paragraph(f"Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}", styles['Normal']))
        elements.append(PageBreak())

        elements.append(Paragraph("1. RESUMEN DE MAGNITUDES", style_h1))
        data = [["INDICADOR", "VALOR"], 
                ["Incidentes", len(self.df_actual)], 
                ["Fallecidos", self.df_actual['num_fallecidos'].sum()], 
                ["Heridos", self.df_actual['num_heridos'].sum()]]
        t = Table(data, colWidths=[3.2*inch, 2*inch])
        t.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#0B3526")), ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke), ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)]))
        elements.append(t)

        elements.append(Spacer(1, 20))
        self.generar_grafico_para_archivo()
        elements.append(RLImage(self.archivo_grafico_temp, width=5.5*inch, height=3.2*inch))

        elements.append(PageBreak())
        elements.append(Paragraph("3. DIAGNÓSTICO TÉCNICO", style_h1))
        analisis_txt = self.generar_estudio_profundo(self.df_actual)
        for line in analisis_txt.split('\n'):
            if line.strip(): elements.append(Paragraph(line, style_body))

        def pie_pagina(canvas, doc):
            canvas.saveState()
            canvas.setFont('Helvetica', 8)
            canvas.drawString(inch, 0.75*inch, "UNIDAD DE INTELIGENCIA VIAL - ÁVILA")
            canvas.drawRightString(A4[0]-inch, 0.75*inch, f"Página {doc.page}")
            canvas.restoreState()

        doc.build(elements, onFirstPage=pie_pagina, onLaterPages=pie_pagina)
        if os.path.exists(self.archivo_grafico_temp): os.remove(self.archivo_grafico_temp)
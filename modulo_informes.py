# ============================================================
# MÓDULO DE INFORMES - modulo_informes.py
# Genera informes técnicos detallados de seguridad vial con
# seis enfoques de análisis distintos. Permite visualizar el
# informe en pantalla y exportarlo en formato PDF profesional
# o Excel con múltiples hojas y gráfico estratégico adjunto.
# ============================================================

import customtkinter as ctk                    # Librería para interfaz gráfica moderna
from tkinter import messagebox, filedialog     # Ventanas emergentes y diálogo para guardar archivos
import psycopg2                                # Conector con la base de datos PostgreSQL
import pandas as pd                            # Manipulación y análisis de datos en DataFrames
from datetime import datetime, timedelta       # Manejo de fechas para calcular rangos temporales
import os                                      # Operaciones del sistema de archivos (rutas, existencia, borrado)
from PIL import Image as PILImage              # Carga de imágenes para la pantalla de bienvenida
import matplotlib.pyplot as plt                # Generación de gráficos para PDF y Excel
import numpy as np                             # Generación de rangos de colores para los gráficos

# Componentes de ReportLab para generación del PDF profesional
from reportlab.lib.pagesizes import A4                                          # Tamaño de página A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image as RLImage, PageBreak  # Elementos del PDF
from reportlab.lib import colors                                                # Colores para estilos del PDF
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle           # Estilos de texto para el PDF
from reportlab.lib.units import inch                                            # Unidad de medida en pulgadas para el PDF

class ModuloInformes:
    def __init__(self, master, db_config):
        """
        Constructor del módulo. Se ejecuta al instanciarlo desde main.py.
        Parámetros:
            master    -- Frame padre donde se renderizará la interfaz
            db_config -- Diccionario con los parámetros de conexión a PostgreSQL
        """
        self.master = master          # Referencia al contenedor padre
        self.db_config = db_config    # Credenciales de conexión a la base de datos
        # Nombre del archivo temporal donde se guarda el gráfico antes de insertarlo en PDF o Excel
        # Se crea y se borra automáticamente durante cada exportación
        self.archivo_grafico_temp = "temp_chart_report.png"
        # DataFrame que almacena los datos consultados del periodo seleccionado
        # Es None hasta que el usuario pulsa "Generar Análisis"
        # Se reutiliza por los métodos de exportación sin necesidad de reconectar a la BD
        self.df_actual = None

    def mostrar(self, volver_callback):
        """
        Construye y muestra toda la interfaz del módulo de informes.
        Parámetros:
            volver_callback -- Función de main.py que se ejecuta al pulsar el botón Volver
        """
        # Limpia cualquier widget previo del contenedor antes de construir la interfaz
        for widget in self.master.winfo_children():
            widget.destroy()

        # --- CABECERA ---
        header = ctk.CTkFrame(self.master, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=15)
        ctk.CTkButton(header, text="← Volver", command=volver_callback, width=90).pack(side="left")
        ctk.CTkLabel(header, text="UNIDAD DE INTELIGENCIA Y ANÁLISIS VIAL",
                     font=ctk.CTkFont(size=22, weight="bold"), text_color="#0B3526").pack(side="left", padx=20)

        # --- MARCO PRINCIPAL ---
        # Frame blanco que divide la pantalla en panel izquierdo (configuración) y derecho (visualización)
        main_frame = ctk.CTkFrame(self.master, fg_color="white", corner_radius=15)
        main_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # --- PANEL IZQUIERDO: CONFIGURACIÓN ---
        # Panel gris claro de ancho fijo con los controles de configuración del informe
        left_panel = ctk.CTkFrame(main_frame, fg_color="#f0f0f0", width=300)
        left_panel.pack(side="left", fill="y", padx=10, pady=10)
        left_panel.pack_propagate(False)  # Mantiene el ancho fijo de 300px

        ctk.CTkLabel(left_panel, text="CONFIGURACIÓN", font=("Arial", 14, "bold")).pack(pady=10)
        
        # Desplegable para seleccionar el tipo de análisis que determinará el contenido del informe
        self.combo_tipo = self.crear_item(left_panel, "Enfoque del Análisis:",
            ["General de Seguridad", "Puntos Negros", "Factores Climatológicos",
             "Análisis de Gravedad", "Por Causa de Accidente", "Por Franja Horaria"])
        
        # Desplegable para seleccionar el rango de fechas de los datos a analizar
        self.combo_rango = self.crear_item(left_panel, "Periodo de Datos:",
            ["Todo el histórico", "Última Semana", "Último Mes", "Últimos 3 Meses"])

        # Botón principal que ejecuta la consulta y muestra el análisis en pantalla
        ctk.CTkButton(left_panel, text="GENERAR ANÁLISIS 🖥️", fg_color="#1b5e46", height=45,
                     font=("Arial", 12, "bold"), command=self.analizar_en_pantalla).pack(pady=20, padx=20, fill="x")

        ctk.CTkLabel(left_panel, text="EXPORTAR RECURSOS", font=("Arial", 12, "bold"), text_color="#555").pack(pady=(10, 5))
        
        # Botones de exportación: deshabilitados por defecto y se activan tras generar el análisis
        # Esto evita que el usuario intente exportar sin datos cargados
        self.btn_pdf = ctk.CTkButton(left_panel, text="Informe PDF 📄", fg_color="#444",
                                     state="disabled", command=self.exportar_pdf_accion)
        self.btn_pdf.pack(pady=5, padx=20, fill="x")
        self.btn_excel = ctk.CTkButton(left_panel, text="Informe Excel 📊", fg_color="#444",
                                       state="disabled", command=self.exportar_excel_accion)
        self.btn_excel.pack(pady=5, padx=20, fill="x")

        # --- PANEL DERECHO: VISUALIZACIÓN ---
        # Fondo oscuro donde se muestra la imagen de bienvenida o el texto del análisis
        self.right_container = ctk.CTkFrame(main_frame, fg_color="#1e1e1e", corner_radius=10)
        self.right_container.pack(side="right", fill="both", expand=True, padx=10, pady=10)
        
        # Muestra la imagen de bienvenida del módulo al cargarse por primera vez
        self.mostrar_imagen_bienvenida()

    def crear_item(self, p, t, v):
        """
        Crea una etiqueta y un desplegable en el panel de configuración.
        Parámetros:
            p -- Frame padre donde se añaden los elementos
            t -- Texto de la etiqueta descriptiva
            v -- Lista de valores del desplegable
        Retorna el objeto CTkComboBox creado para poder leer su valor después.
        """
        ctk.CTkLabel(p, text=t, font=("Arial", 12)).pack(pady=(10, 0), padx=20, anchor="w")
        cb = ctk.CTkComboBox(p, values=v, width=240)
        cb.set(v[0])   # Selecciona el primer valor por defecto
        cb.pack(pady=5, padx=20)
        return cb

    def mostrar_imagen_bienvenida(self):
        """
        Muestra la imagen corporativa del módulo en el panel derecho.
        La imagen se redimensiona dinámicamente al cambiar el tamaño del contenedor
        mediante el evento <Configure> de Tkinter.
        Si no existe el archivo de imagen, muestra un texto de instrucción.
        """
        # Limpia el panel derecho antes de mostrar la imagen
        for widget in self.right_container.winfo_children():
            widget.destroy()
        # Configura el grid para que la imagen ocupe todo el espacio disponible
        self.right_container.grid_rowconfigure(0, weight=1)
        self.right_container.grid_columnconfigure(0, weight=1)

        ruta_img = os.path.join(os.path.dirname(__file__), "imagen_modulo_informes.png")
        if os.path.exists(ruta_img):
            img_pil = PILImage.open(ruta_img)
            img_ctk = ctk.CTkImage(light_image=img_pil, dark_image=img_pil)
            label_img = ctk.CTkLabel(self.right_container, image=img_ctk, text="")
            label_img.grid(row=0, column=0, sticky="nsew")
            
            def redimensionar(event):
                # Cada vez que cambia el tamaño del contenedor, ajusta la imagen al nuevo tamaño
                img_ctk.configure(size=(event.width, event.height))
            
            label_img.image = img_ctk  # Referencia necesaria para evitar que el garbage collector elimine la imagen
            self.right_container.bind("<Configure>", redimensionar)
        else:
            # Texto alternativo si no existe el archivo de imagen
            ctk.CTkLabel(self.right_container,
                         text="CENTRO DE ANÁLISIS\nSeleccione un enfoque para comenzar",
                         text_color="white", font=("Arial", 16)).grid(row=0, column=0)

    def obtener_datos(self):
        """
        Consulta la base de datos y devuelve un DataFrame con todos los accidentes
        del periodo seleccionado, con los campos de todas las tablas de referencia.
        Retorna None si hay error de conexión o si no hay datos.
        """
        rango = self.combo_rango.get()
        filtro = ""  # Sin filtro = histórico completo
        hoy = datetime.now()

        # Construye el fragmento SQL de filtro de fechas según el periodo seleccionado
        if rango == "Última Semana":
            filtro = f" AND a.fecha >= '{(hoy - timedelta(days=7)).date()}'"
        elif rango == "Último Mes":
            filtro = f" AND a.fecha >= '{(hoy - timedelta(days=30)).date()}'"
        elif rango == "Últimos 3 Meses":
            filtro = f" AND a.fecha >= '{(hoy - timedelta(days=90)).date()}'"

        # Consulta todos los campos necesarios para todos los tipos de análisis
        # Se hace una sola consulta amplia y después cada análisis filtra el DataFrame en memoria
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
            df = pd.read_sql(query, conn)  # Carga directamente el resultado en un DataFrame de pandas
            conn.close()
            return df
        except Exception as e:
            messagebox.showerror("Error DB", f"No se pudo conectar: {e}")
            return None

    def asignar_franja(self, hora_obj):
        """
        Clasifica un objeto hora en una de las tres franjas horarias del sistema.
        Se usa como función de mapeo en df.apply() para crear la columna 'franja'.
        Parámetros:
            hora_obj -- Objeto time de Python con la hora del accidente
        Retorna: 'Mañana' (08-14h), 'Tarde' (14-22h) o 'Noche' (22-08h)
        """
        h = hora_obj.hour  # Extrae solo el número de hora (0-23)
        if 8 <= h < 14:
            return "Mañana"
        elif 14 <= h < 22:
            return "Tarde"
        else:
            return "Noche"

    def generar_estudio_profundo(self, df):
        """
        Genera el texto completo del informe técnico según el enfoque seleccionado.
        Analiza el DataFrame recibido y construye un texto estructurado con estadísticas,
        identificación de puntos críticos y conclusiones técnicas.
        Parámetros:
            df -- DataFrame con los datos del periodo seleccionado
        Retorna el texto completo del informe como cadena de texto.
        """
        tipo = self.combo_tipo.get()
        # Calcula los indicadores globales comunes a todos los tipos de informe
        total_acc = len(df)
        fallecidos = df['num_fallecidos'].sum()
        heridos    = df['num_heridos'].sum()
        
        # Cabecera común a todos los informes con fecha, tipo y volumen de datos
        texto  = f"INFORME TÉCNICO DE SEGURIDAD VIAL | ÁVILA | {datetime.now().strftime('%d/%m/%Y')}\n"
        texto += "=" * 85 + "\n"
        texto += f"ENFOQUE SELECCIONADO: {tipo.upper()}\n"
        texto += f"VOLUMEN DE DATOS PROCESADOS: {total_acc} incidentes\n"
        texto += f"BALANCE DE VÍCTIMAS: {fallecidos} fallecidos y {heridos} heridos totales.\n"
        texto += "=" * 85 + "\n\n"

        if tipo == "General de Seguridad":
            # Análisis multivariable: resume los valores más frecuentes de cada variable
            texto += "1. ANÁLISIS MULTIVARIABLE DEL PERIODO\n"
            texto += f"- Siniestralidad por Vías: Se han visto afectadas {df['carretera'].nunique()} carreteras.\n"
            texto += f"- Factor Meteorológico: El clima '{df['clima'].mode()[0]}' está presente en la mayoría de casos.\n"
            texto += f"- Gravedad Media: La categoría predominante es '{df['gravedad'].mode()[0]}'.\n"
            texto += f"- Causa Raíz: La mayoría de incidentes se atribuyen a '{df['causa'].mode()[0]}'.\n\n"
            texto += "2. VALORACIÓN TÉCNICA\nSe observa una correlación directa entre los factores de la vía y la lesividad."

        elif tipo == "Puntos Negros":
            # Identifica las 5 carreteras con más accidentes y muestra sus víctimas
            texto += "1. IDENTIFICACIÓN DE TRAMOS DE ALTA SINIESTRALIDAD (TAS)\n"
            texto += "Se listan las 5 vías con mayor concentración de incidentes en el periodo:\n\n"
            top_5 = df['carretera'].value_counts().head(5)
            for i, (via, count) in enumerate(top_5.items(), 1):
                f_via = df[df['carretera'] == via]['num_fallecidos'].sum()
                h_via = df[df['carretera'] == via]['num_heridos'].sum()
                texto += f"   [{i}] VÍA: {via} -> {count} accidentes ({f_via} fallecidos / {h_via} heridos)\n"
            texto += "\n2. RECOMENDACIÓN: Se sugiere auditoría de infraestructura en los puntos señalados."

        elif tipo == "Factores Climatológicos":
            # Agrupa los accidentes por condición meteorológica y muestra víctimas por cada una
            texto += "1. ESTUDIO DE SINIESTRALIDAD POR CONDICIÓN METEOROLÓGICA\n"
            stats = df.groupby('clima').agg({'fecha': 'count', 'num_fallecidos': 'sum', 'num_heridos': 'sum'})
            for clima, row in stats.iterrows():
                texto += f"- Condición: {clima}\n"
                texto += f"  Accidentes: {row['fecha']} | Fallecidos: {row['num_fallecidos']} | Heridos: {row['num_heridos']}\n"
            texto += "\n2. CONCLUSIÓN: Las condiciones adversas elevan el riesgo de accidentes mortales."

        elif tipo == "Análisis de Gravedad":
            # Desglosa el número de accidentes por nivel de gravedad y calcula la tasa de letalidad
            texto += "1. DESGLOSE DE GRAVEDAD Y LESIVIDAD\n"
            grav_counts = df['gravedad'].value_counts()
            for g_tipo, count in grav_counts.items():
                texto += f"- Nivel {g_tipo}: {count} accidentes registrados.\n"
            texto += f"\n2. ACLARACIÓN TÉCNICA DE VÍCTIMAS\n"
            texto += f"Se han procesado {total_acc} incidentes. El total de {fallecidos} fallecidos indica una\n"
            # Tasa de letalidad: fallecidos por cada accidente (redondeado a 2 decimales)
            texto += "tasa de letalidad de " + str(round(fallecidos / total_acc, 2)) + " víctimas por cada accidente.\n"

        elif tipo == "Por Causa de Accidente":
            # Agrupa por causa y muestra el impacto en víctimas de cada una, ordenado por frecuencia
            texto += "1. ESTADÍSTICA DE CAUSALIDAD VS LESIVIDAD\n"
            causas = df.groupby('causa').agg({'num_fallecidos': 'sum', 'num_heridos': 'sum', 'fecha': 'count'})
            for c, r in causas.sort_values(by='fecha', ascending=False).iterrows():
                texto += f"- {c}: {r['fecha']} casos. Impacto: {r['num_fallecidos']} muertos / {r['num_heridos']} heridos.\n"
            texto += "\n2. IMPACTO SOCIAL: Las causas humanas siguen siendo el factor crítico de riesgo."

        elif tipo == "Por Franja Horaria":
            # Crea la columna franja aplicando asignar_franja() a cada fila del campo hora
            df['franja'] = df['hora'].apply(self.asignar_franja)
            texto += "1. DISTRIBUCIÓN HORARIA ESTRATÉGICA\n"
            for f in ["Mañana", "Tarde", "Noche"]:
                sub = df[df['franja'] == f]  # Filtra solo los accidentes de esa franja
                texto += f"\n>>> FRANJA: {f.upper()} "
                if f == "Mañana":   texto += "(08:00 - 14:00)\n"
                elif f == "Tarde":  texto += "(14:00 - 22:00)\n"
                else:               texto += "(22:00 - 08:00)\n"
                
                if not sub.empty:
                    texto += f"    * Incidentes: {len(sub)}\n"
                    texto += f"    * Causa Mayoritaria: {sub['causa'].mode()[0]}\n"
                    texto += f"    * Gravedad Crítica: {sub['gravedad'].mode()[0]}\n"
                    texto += f"    * Víctimas: {sub['num_fallecidos'].sum()} fallecidos / {sub['num_heridos'].sum()} heridos.\n"
            texto += "\n2. CONCLUSIÓN: Los picos de gravedad varían según la visibilidad y el flujo circulatorio."

        return texto

    def analizar_en_pantalla(self):
        """
        Ejecuta el análisis al pulsar 'Generar Análisis':
        - Consulta los datos con obtener_datos()
        - Genera el texto del informe con generar_estudio_profundo()
        - Lo muestra en un cuadro de texto de estilo terminal (fondo negro, texto verde)
        - Activa los botones de exportación PDF y Excel
        """
        self.df_actual = self.obtener_datos()
        if self.df_actual is None or self.df_actual.empty:
            messagebox.showwarning("Sin Datos", "No hay registros para este periodo.")
            return
            
        # Limpia el panel derecho para mostrar el texto del análisis
        for widget in self.right_container.winfo_children():
            widget.destroy()
            
        # Cuadro de texto con estilo de terminal (fondo oscuro, texto verde fluorescente)
        # Consolas es una fuente monoespaciada que mejora la legibilidad del informe técnico
        self.right_panel = ctk.CTkTextbox(self.right_container, font=("Consolas", 12),
                                         fg_color="#1e1e1e", text_color="#adff2f", border_width=1)
        self.right_panel.pack(fill="both", expand=True)
        self.right_panel.insert("0.0", self.generar_estudio_profundo(self.df_actual))
        
        # Activa los botones de exportación en verde ahora que hay datos disponibles
        self.btn_pdf.configure(state="normal", fg_color="#1b5e46")
        self.btn_excel.configure(state="normal", fg_color="#1b5e46")

    def exportar_excel_accion(self):
        """
        Genera un archivo Excel profesional con cuatro hojas:
          - Resumen Ejecutivo: indicadores globales del análisis
          - Análisis Detallado: tabla agrupada según el enfoque seleccionado
          - Listado Completo: todos los registros del periodo con fechas formateadas
          - Gráfico Estratégico: imagen del gráfico generado automáticamente
        Usa xlsxwriter para aplicar colores pastel en las cabeceras y anchos automáticos.
        Al finalizar, elimina el archivo temporal del gráfico.
        """
        ruta = filedialog.asksaveasfilename(defaultextension=".xlsx", title="Guardar Informe Excel")
        if not ruta or self.df_actual is None: return

        tipo = self.combo_tipo.get()
        
        try:
            with pd.ExcelWriter(ruta, engine='xlsxwriter') as writer:
                
                # --- HOJA 1: RESUMEN EJECUTIVO ---
                # Tabla de dos columnas con los indicadores globales del análisis
                resumen_data = {
                    "INDICADOR": ["Tipo de Análisis", "Periodo Seleccionado", "Total Accidentes",
                                  "Total Fallecidos", "Total Heridos"],
                    "VALOR": [tipo, self.combo_rango.get(), len(self.df_actual),
                              self.df_actual['num_fallecidos'].sum(), self.df_actual['num_heridos'].sum()]
                }
                df_resumen = pd.DataFrame(resumen_data)

                # --- HOJA 2: ANÁLISIS DETALLADO ---
                # La agrupación varía según el tipo de análisis seleccionado
                if tipo == "Puntos Negros":
                    # Top 10 carreteras con más accidentes
                    df_analisis = self.df_actual.groupby('carretera').agg(
                        {'fecha': 'count', 'num_fallecidos': 'sum', 'num_heridos': 'sum'}
                    ).sort_values(by='fecha', ascending=False).head(10)
                elif tipo == "Factores Climatológicos":
                    df_analisis = self.df_actual.groupby('clima').agg(
                        {'fecha': 'count', 'num_fallecidos': 'sum', 'num_heridos': 'sum'})
                elif tipo == "Por Causa de Accidente":
                    df_analisis = self.df_actual.groupby('causa').agg(
                        {'fecha': 'count', 'num_fallecidos': 'sum', 'num_heridos': 'sum'})
                elif tipo == "Por Franja Horaria":
                    # Crea la columna franja si aún no existe
                    self.df_actual['franja'] = self.df_actual['hora'].apply(self.asignar_franja)
                    df_analisis = self.df_actual.groupby('franja').agg(
                        {'fecha': 'count', 'num_fallecidos': 'sum', 'num_heridos': 'sum'})
                else:
                    # Para General de Seguridad y Análisis de Gravedad: agrupa por nivel de gravedad
                    df_analisis = self.df_actual.groupby('gravedad').agg(
                        {'fecha': 'count', 'num_fallecidos': 'sum', 'num_heridos': 'sum'})
                
                # Renombra la columna 'fecha' (que contiene el conteo) a un nombre más descriptivo
                df_analisis = df_analisis.rename(columns={'fecha': 'Total Accidentes'}).reset_index()

                # --- HOJA 3: LISTADO COMPLETO ---
                # Copia de todos los registros con las fechas en formato español (DD/MM/AAAA)
                df_listado = self.df_actual.copy()
                df_listado['fecha'] = pd.to_datetime(df_listado['fecha']).dt.strftime('%d/%m/%Y')

                # Escribe las tres hojas en el archivo Excel
                df_resumen.to_excel(writer, sheet_name='Resumen Ejecutivo', index=False)
                df_analisis.to_excel(writer, sheet_name='Análisis Detallado', index=False)
                df_listado.to_excel(writer, sheet_name='Listado Completo', index=False)

                workbook = writer.book
                # Paleta de colores pastel que se aplica rotativamente a cada columna
                colores_pastel = ['#FFD1DC', '#E0BBE4', '#BFFCC6', '#FFF5BA', '#FFDFBA', '#BAE1FF', '#F0EAD6']
                
                def aplicar_formato_profesional(sheet_name, df):
                    """
                    Aplica formato visual a la cabecera de una hoja Excel:
                    ajusta el ancho de cada columna al contenido y aplica color pastel rotativo.
                    Parámetros:
                        sheet_name -- Nombre de la hoja a formatear
                        df         -- DataFrame cuyas columnas se van a formatear
                    """
                    worksheet = writer.sheets[sheet_name]
                    for col_num, value in enumerate(df.columns.values):
                        # Calcula el ancho mínimo como el mayor entre la longitud del nombre y 10 caracteres
                        column_len = max(len(str(value)), 10)
                        worksheet.set_column(col_num, col_num, column_len + 2)  # +2 de margen
                        color = colores_pastel[col_num % len(colores_pastel)]   # Color rotativo
                        formato_header = workbook.add_format({
                            'bold': True, 'bg_color': color, 'border': 1, 'align': 'center'
                        })
                        worksheet.write(0, col_num, value, formato_header)

                # Aplica el formato profesional a las tres hojas
                aplicar_formato_profesional('Resumen Ejecutivo', df_resumen)
                aplicar_formato_profesional('Análisis Detallado', df_analisis)
                aplicar_formato_profesional('Listado Completo', df_listado)

                # --- HOJA 4: GRÁFICO ESTRATÉGICO ---
                # Genera el gráfico como imagen temporal y lo inserta en una hoja nueva
                self.generar_grafico_para_archivo()
                worksheet_img = workbook.add_worksheet('Gráfico Estratégico')
                worksheet_img.insert_image('B2', self.archivo_grafico_temp)

            messagebox.showinfo("Éxito", f"Informe Excel '{tipo}' generado con éxito.")
            # Elimina el archivo temporal del gráfico una vez insertado en el Excel
            if os.path.exists(self.archivo_grafico_temp):
                os.remove(self.archivo_grafico_temp)
            
        except Exception as e:
            messagebox.showerror("Error Excel", f"No se pudo generar: {e}")

    def generar_grafico_para_archivo(self):
        """
        Genera un gráfico matplotlib adaptado al tipo de análisis seleccionado
        y lo guarda como imagen PNG temporal en self.archivo_grafico_temp.
        Cada tipo de análisis usa un tipo de gráfico y paleta de colores diferente:
          - Por Franja Horaria: barras verticales con paleta viridis
          - Puntos Negros: barras horizontales con paleta plasma
          - Factores Climatológicos: gráfico de tarta con paleta Set3
          - Por Causa de Accidente: barras verticales top 10 con paleta tab10
          - General/Gravedad: barras verticales con paleta coolwarm
        np.linspace genera una gama de colores distribuida uniformemente según el número de categorías.
        """
        tipo = self.combo_tipo.get()
        plt.figure(figsize=(10, 6))
        
        if tipo == "Por Franja Horaria":
            self.df_actual['franja'] = self.df_actual['hora'].apply(self.asignar_franja)
            # reindex garantiza que las franjas aparezcan siempre en orden cronológico
            serie = self.df_actual['franja'].value_counts().reindex(["Mañana", "Tarde", "Noche"]).dropna()
            colores = plt.cm.viridis(np.linspace(0, 1, len(serie)))
            serie.plot(kind='bar', color=colores, edgecolor='black')
        elif tipo == "Puntos Negros":
            serie = self.df_actual['carretera'].value_counts().head(8)
            colores = plt.cm.plasma(np.linspace(0, 1, len(serie)))
            serie.plot(kind='barh', color=colores, edgecolor='black')  # barh = barras horizontales
        elif tipo == "Factores Climatológicos":
            serie = self.df_actual['clima'].value_counts()
            colores = plt.cm.Set3(np.linspace(0, 1, len(serie)))
            serie.plot(kind='pie', autopct='%1.1f%%', colors=colores, startangle=140)
        elif tipo == "Por Causa de Accidente":
            serie = self.df_actual['causa'].value_counts().head(10)
            colores = plt.cm.tab10(np.linspace(0, 1, len(serie)))
            serie.plot(kind='bar', color=colores, edgecolor='black')
        else:
            # General de Seguridad y Análisis de Gravedad: barras por nivel de gravedad
            serie = self.df_actual['gravedad'].value_counts()
            colores = plt.cm.coolwarm(np.linspace(0, 1, len(serie)))
            serie.plot(kind='bar', color=colores, edgecolor='black')
            
        plt.title(f"Distribución: {tipo}", fontsize=14, fontweight='bold')
        plt.tight_layout()
        plt.savefig(self.archivo_grafico_temp, dpi=100)  # Guarda el gráfico como imagen temporal
        plt.close()  # Cierra la figura para liberar memoria

    def exportar_pdf_accion(self):
        """
        Abre el diálogo para guardar el PDF y llama al constructor del informe.
        Solo se ejecuta si hay datos cargados en self.df_actual.
        """
        ruta = filedialog.asksaveasfilename(defaultextension=".pdf", title="Guardar Informe PDF")
        if ruta and self.df_actual is not None:
            self.construir_pdf_profesional(ruta)
            messagebox.showinfo("Éxito", "Informe técnico PDF generado con éxito.")

    def construir_pdf_profesional(self, ruta):
        """
        Genera el PDF profesional completo con tres secciones:
          - Portada: título institucional, tipo de análisis y fecha de generación
          - Página 2: tabla de indicadores globales y gráfico estratégico
          - Página 3: texto completo del diagnóstico técnico
        Incluye pie de página en todas las páginas con el nombre de la unidad y número de página.
        Al finalizar, elimina el archivo temporal del gráfico generado.
        """
        # Márgenes del documento en puntos tipográficos
        doc = SimpleDocTemplate(ruta, pagesize=A4,
                                rightMargin=50, leftMargin=50,
                                topMargin=60, bottomMargin=50)
        styles = getSampleStyleSheet()
        elements = []  # Lista de elementos que se añaden al PDF en orden

        # Definición de estilos personalizados para el PDF
        style_title = ParagraphStyle(name='T', fontSize=24, alignment=1,
                                     fontName='Helvetica-Bold', leading=32, spaceAfter=40)
        style_h1 = ParagraphStyle(name='H1', fontSize=14, fontName='Helvetica-Bold',
                                  color=colors.HexColor("#0B3526"), spaceBefore=15, spaceAfter=10)
        style_body = ParagraphStyle(name='B', fontSize=10, fontName='Helvetica',
                                    alignment=4, leading=12)  # alignment=4 = justificado

        # --- PORTADA ---
        elements.append(Spacer(1, 2*inch))  # Espacio superior para centrar el título verticalmente
        elements.append(Paragraph("INFORME ESTRATÉGICO DE SEGURIDAD VIAL", style_title))
        elements.append(Paragraph(f"TIPO: {self.combo_tipo.get().upper()}", styles['Normal']))
        elements.append(Paragraph(f"Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}", styles['Normal']))
        elements.append(PageBreak())  # Salto de página para separar la portada del contenido

        # --- PÁGINA 2: RESUMEN E INDICADORES ---
        elements.append(Paragraph("1. RESUMEN DE MAGNITUDES", style_h1))
        # Tabla de dos columnas con los tres indicadores globales
        data = [["INDICADOR", "VALOR"],
                ["Incidentes",  len(self.df_actual)],
                ["Fallecidos",  self.df_actual['num_fallecidos'].sum()],
                ["Heridos",     self.df_actual['num_heridos'].sum()]]
        t = Table(data, colWidths=[3.2*inch, 2*inch])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#0B3526")),  # Cabecera verde oscuro
            ('TEXTCOLOR',  (0, 0), (-1, 0), colors.whitesmoke),           # Texto blanco en cabecera
            ('GRID',       (0, 0), (-1, -1), 0.5, colors.grey)            # Rejilla gris
        ]))
        elements.append(t)

        elements.append(Spacer(1, 20))
        # Genera el gráfico temporal e inserta la imagen en el PDF con tamaño definido en pulgadas
        self.generar_grafico_para_archivo()
        elements.append(RLImage(self.archivo_grafico_temp, width=5.5*inch, height=3.2*inch))

        # --- PÁGINA 3: DIAGNÓSTICO TÉCNICO ---
        elements.append(PageBreak())
        elements.append(Paragraph("3. DIAGNÓSTICO TÉCNICO", style_h1))
        # Convierte cada línea del texto del informe en un Paragraph de ReportLab
        # Las líneas vacías se omiten para evitar espacios en blanco innecesarios
        analisis_txt = self.generar_estudio_profundo(self.df_actual)
        for line in analisis_txt.split('\n'):
            if line.strip():
                elements.append(Paragraph(line, style_body))

        def pie_pagina(canvas, doc):
            """
            Función que ReportLab ejecuta en cada página para dibujar el pie de página.
            Muestra el nombre de la unidad a la izquierda y el número de página a la derecha.
            Parámetros:
                canvas -- Objeto de dibujo de ReportLab
                doc    -- Documento actual con información de la página
            """
            canvas.saveState()   # Guarda el estado del canvas para no afectar al contenido principal
            canvas.setFont('Helvetica', 8)
            canvas.drawString(inch, 0.75*inch, "UNIDAD DE INTELIGENCIA VIAL - ÁVILA")
            canvas.drawRightString(A4[0]-inch, 0.75*inch, f"Página {doc.page}")
            canvas.restoreState()  # Restaura el estado del canvas

        # Construye el PDF aplicando el pie de página en todas las páginas
        doc.build(elements, onFirstPage=pie_pagina, onLaterPages=pie_pagina)
        
        # Elimina el archivo temporal del gráfico una vez insertado en el PDF
        if os.path.exists(self.archivo_grafico_temp):
            os.remove(self.archivo_grafico_temp)
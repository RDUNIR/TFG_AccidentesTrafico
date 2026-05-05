import customtkinter as ctk
import psycopg2
from tkinter import messagebox, filedialog
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from datetime import datetime

class ModuloControles:
    def __init__(self, master, db_config):
        self.master = master
        self.db_config = db_config
        self.resultados_actuales = []
        # Configuración de filtros
        self.filtro_tipo_via = "Todas"
        self.filtro_periodo = "Semana"
        self.filtro_control = "Todos"

    def mostrar(self, volver_callback):
        for widget in self.master.winfo_children():
            widget.destroy()

        self.master.configure(fg_color="#F2F2F2")

        # CABECERA Y FILTROS
        header = ctk.CTkFrame(self.master, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkButton(header, text="← Volver", fg_color="#555", width=90, command=volver_callback).pack(side="left")
        ctk.CTkLabel(header, text="UNIDAD DE PLANIFICACIÓN OPERATIVA", text_color="#0B3526", 
                     font=ctk.CTkFont(size=22, weight="bold")).pack(side="left", padx=20)

        # Panel de Filtros
        filter_bar = ctk.CTkFrame(self.master, fg_color="#E0E0E0", height=50)
        filter_bar.pack(fill="x", padx=20, pady=5)

        ctk.CTkLabel(filter_bar, text="Tipo de Vía:", text_color="black").pack(side="left", padx=(15, 5))
        self.combo_via = ctk.CTkComboBox(filter_bar, values=["Todas", "Autovía/Autopista", "Convencional"], 
                                         command=self.actualizar_filtros, width=140)
        self.combo_via.pack(side="left", padx=5)

        ctk.CTkLabel(filter_bar, text="Periodo:", text_color="black").pack(side="left", padx=(10, 5))
        self.combo_periodo = ctk.CTkComboBox(filter_bar, values=["Semana", "Fin de Semana"], 
                                             command=self.actualizar_filtros, width=130)
        self.combo_periodo.pack(side="left", padx=5)

        # CORRECCIÓN: Nombres de dispositivo alineados con las tarjetas
        ctk.CTkLabel(filter_bar, text="Dispositivo:", text_color="black").pack(side="left", padx=(10, 5))
        self.combo_control = ctk.CTkComboBox(filter_bar, 
                                             values=["Todos", "ALCOHOLEMIA / DROGAS", "RADAR MÓVIL", "VIGILANCIA DRON/TEL", "VIGILANCIA PREVENTIVA", "VIGILANCIA GENÉRICA"], 
                                             command=self.actualizar_filtros, width=180)
        self.combo_control.pack(side="left", padx=5)

        ctk.CTkButton(filter_bar, text="📥 Orden de Servicio", fg_color="#2c3e50", width=140,
                     command=self.exportar_orden_pdf).pack(side="right", padx=15)

        # Contenedor principal con scroll
        self.scroll_cont = ctk.CTkScrollableFrame(self.master, fg_color="transparent")
        self.scroll_cont.pack(fill="both", expand=True, padx=20, pady=10)

        self.generar_analisis()

    def actualizar_filtros(self, _=None):
        self.filtro_tipo_via = self.combo_via.get()
        self.filtro_periodo = self.combo_periodo.get()
        self.filtro_control = self.combo_control.get()
        self.generar_analisis()

    def generar_analisis(self):
        for widget in self.scroll_cont.winfo_children():
            widget.destroy()

        try:
            conn = psycopg2.connect(**self.db_config)
            cur = conn.cursor()

            where_clause = "WHERE (g.nivel ILIKE '%Mortal%' OR g.nivel ILIKE '%Grave%')"
            if self.filtro_tipo_via == "Autovía/Autopista":
                where_clause += " AND (c.nombre ILIKE 'A-%' OR c.nombre ILIKE 'AP-%')"
            elif self.filtro_tipo_via == "Convencional":
                where_clause += " AND NOT (c.nombre ILIKE 'A-%' OR c.nombre ILIKE 'AP-%')"
            
            if self.filtro_periodo == "Fin de Semana":
                where_clause += " AND EXTRACT(DOW FROM a.fecha) IN (0, 6)"

            # CORRECCIÓN: Orden secundario por c.nombre para evitar resultados aleatorios en empates
            query = f"""
            WITH TopCarreteras AS (
                SELECT a.carretera_id, COUNT(*) as total,
                       SUM(CASE WHEN a.fecha >= CURRENT_DATE - INTERVAL '30 days' THEN 1 ELSE 0 END) as mes_actual,
                       SUM(CASE WHEN a.fecha BETWEEN CURRENT_DATE - INTERVAL '60 days' AND CURRENT_DATE - INTERVAL '30 days' THEN 1 ELSE 0 END) as mes_anterior
                FROM accidentes a
                JOIN gravedad g ON a.gravedad_id = g.id
                JOIN carreteras c ON a.carretera_id = c.id
                {where_clause}
                GROUP BY a.carretera_id
                ORDER BY total DESC, a.carretera_id ASC LIMIT 20
            ),
            CausaPrincipal AS (
                SELECT DISTINCT ON (carretera_id) carretera_id, causa_id, COUNT(*) as freq
                FROM accidentes GROUP BY carretera_id, causa_id ORDER BY carretera_id, freq DESC
            ),
            HoraPrincipal AS (
                SELECT DISTINCT ON (carretera_id) carretera_id, EXTRACT(HOUR FROM hora) as franja
                FROM accidentes GROUP BY carretera_id, franja ORDER BY carretera_id, COUNT(*) DESC
            ),
            ClimaFrecuente AS (
                SELECT DISTINCT ON (carretera_id) carretera_id, cli.descripcion as clima, COUNT(*) as freq
                FROM accidentes acc
                JOIN clima cli ON acc.clima_id = cli.id
                GROUP BY carretera_id, clima ORDER BY carretera_id, freq DESC
            )
            SELECT c.nombre, tc.total, cau.descripcion, hp.franja, tc.mes_actual, tc.mes_anterior, cl.clima
            FROM TopCarreteras tc
            JOIN carreteras c ON tc.carretera_id = c.id
            JOIN CausaPrincipal cp ON tc.carretera_id = cp.carretera_id
            JOIN causas cau ON cp.causa_id = cau.id
            JOIN HoraPrincipal hp ON tc.carretera_id = hp.carretera_id
            JOIN ClimaFrecuente cl ON tc.carretera_id = cl.carretera_id
            ORDER BY tc.total DESC, c.nombre ASC;
            """
            
            cur.execute(query)
            datos_brutos = cur.fetchall()
            
            self.resultados_actuales = []
            for res in datos_brutos:
                tipo, _, _ = self.obtener_metadatos_control(res[2])
                if self.filtro_control == "Todos" or self.filtro_control == tipo:
                    self.resultados_actuales.append(res)
            
            self.resultados_actuales = self.resultados_actuales[:10]

            if not self.resultados_actuales:
                ctk.CTkLabel(self.scroll_cont, text="No hay datos para esta combinación de filtros.", text_color="grey").pack(pady=50)
                return

            max_acc = max([r[1] for r in self.resultados_actuales]) if self.resultados_actuales else 1

            for i, res in enumerate(self.resultados_actuales):
                self.crear_tarjeta_avanzada(res, i + 1, max_acc)

            cur.close()
            conn.close()
        except Exception as e:
            messagebox.showerror("Error", f"Error en análisis: {e}")

    def obtener_metadatos_control(self, causa):
        c = causa.lower()
        if "alcohol" in c or "drogas" in c:
            return "ALCOHOLEMIA / DROGAS", "#C62828", "🍷"
        elif "velocidad" in c:
            return "RADAR MÓVIL", "#1565C0", "📸"
        elif "distracción" in c or "teléfono" in c:
            return "VIGILANCIA DRON/TEL", "#1565C0", "📱"
        elif "clima" in c or "visibilidad" in c:
            return "VIGILANCIA PREVENTIVA", "#2E7D32", "🌧️"
        else:
            return "VIGILANCIA GENÉRICA", "#37474F", "🚔"

    def crear_tarjeta_avanzada(self, datos, ranking, max_acc):
        nombre, total, causa, hora, m_actual, m_anterior, clima_top = datos
        tipo_ctrl, color, icono = self.obtener_metadatos_control(causa)
        
        es_prioridad = (m_actual > m_anterior) and ranking <= 3
        
        card = ctk.CTkFrame(self.scroll_cont, fg_color="white", corner_radius=12, border_width=1, border_color="#DDD", height=110)
        card.pack(fill="x", pady=5, padx=5)
        card.pack_propagate(False) 

        left = ctk.CTkFrame(card, fg_color="transparent", width=220)
        left.pack(side="left", padx=15, pady=10)
        left.pack_propagate(False)
        
        header_v = ctk.CTkFrame(left, fg_color="transparent")
        header_v.pack(fill="x")
        ctk.CTkLabel(header_v, text=f"{ranking}º", font=("Arial", 20, "bold"), text_color="#0B3526").pack(side="left")
        if es_prioridad:
            ctk.CTkLabel(header_v, text="⚠️ ALTA", fg_color="#FFEBEE", text_color="#C62828", 
                         font=("Arial", 9, "bold"), corner_radius=5).pack(side="left", padx=5)

        ctk.CTkLabel(left, text=nombre, font=("Arial", 15, "bold"), text_color="black").pack(anchor="w")
        
        porcentaje = total / max_acc
        bar_bg = ctk.CTkFrame(left, fg_color="#EEE", height=6, width=160)
        bar_bg.pack(anchor="w", pady=(5,0))
        bar_fill = ctk.CTkFrame(bar_bg, fg_color="#C62828" if ranking <=3 else "#FBC02D", height=6, width=160 * porcentaje)
        bar_fill.place(x=0, y=0)
        ctk.CTkLabel(left, text=f"{total} incidentes críticos", font=("Arial", 10), text_color="#666").pack(anchor="w")

        center = ctk.CTkFrame(card, fg_color="transparent")
        center.pack(side="left", expand=True, fill="both", padx=10, pady=10)
        
        ctk.CTkLabel(center, text=f"{icono} {causa}", font=("Arial", 12), text_color="#333").pack(anchor="w")
        ctk.CTkLabel(center, text=f"🕒 Crítico: {int(hora):02d}:00h a {int(hora+1)%24:02d}:00h", 
                     font=("Arial", 12, "bold"), text_color="black").pack(anchor="w")
        
        msg_clima = f"💡 Rec. Clima: {clima_top.lower()}"
        ctk.CTkLabel(center, text=msg_clima, text_color="#1B5E20", font=("Arial", 10, "italic")).pack(anchor="w")

        right = ctk.CTkFrame(card, fg_color=color, corner_radius=8, width=210)
        right.pack(side="right", padx=10, pady=10, fill="y")
        right.pack_propagate(False)
        
        ctk.CTkLabel(right, text="DISPOSITIVO PROPUESTO", text_color="white", font=("Arial", 9, "bold")).pack(pady=(12,0))
        ctk.CTkLabel(right, text=tipo_ctrl, text_color="white", font=("Arial", 11, "bold"), wraplength=180).pack(expand=True)

    def exportar_orden_pdf(self):
        if not self.resultados_actuales: return
        
        path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF", "*.pdf")])
        if not path: return

        doc = SimpleDocTemplate(path, pagesize=A4)
        estilos = getSampleStyleSheet()
        elements = []

        # TÍTULO PROFESIONAL
        style_title = ParagraphStyle('Title', parent=estilos['Heading1'], alignment=1, fontSize=20, textColor=colors.HexColor("#0B3526"), spaceAfter=20)
        elements.append(Paragraph("ORDEN DE SERVICIO OPERATIVO", style_title))
        
        # DATOS DE CABECERA
        info_header = [
            [Paragraph("<b>UNIDAD:</b> Tráfico / Seguridad Vial", estilos['Normal']), Paragraph(f"<b>FECHA:</b> {datetime.now().strftime('%d/%m/%Y')}", estilos['Normal'])],
            [Paragraph(f"<b>TIPO VÍA:</b> {self.filtro_tipo_via}", estilos['Normal']), Paragraph(f"<b>PERIODO:</b> {self.filtro_periodo}", estilos['Normal'])]
        ]
        head_table = Table(info_header, colWidths=[250, 250])
        head_table.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'TOP')]))
        elements.append(head_table)
        elements.append(Spacer(1, 20))

        # TABLA DE DISPOSITIVOS (MÁS GRÁFICA)
        # Añadimos colores de fondo según el tipo de riesgo para que el oficial lo vea rápido
        data = [["POS.", "LOCALIZACIÓN", "DISPOSITIVO RECOMENDADO", "HORARIO CRÍTICO", "FACTOR RIESGO"]]
        
        for i, res in enumerate(self.resultados_actuales):
            tipo, _, _ = self.obtener_metadatos_control(res[2])
            data.append([
                i+1, 
                res[0], 
                tipo, 
                f"{int(res[3]):02d}:00h - {int(res[3]+1)%24:02d}:00h", 
                res[2].upper()
            ])

        t = Table(data, colWidths=[35, 110, 160, 100, 115])
        
        # Estilo de tabla con colores "de mando"
        estilo_tabla = [
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#0B3526")), # Cabecera oscura
            ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,-1), 8),
            ('BOTTOMPADDING', (0,0), (-1,0), 10),
            ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ]
        
        # Aplicar colores de alerta a las filas superiores (Top 3)
        for row in range(1, 4):
            if row < len(data):
                estilo_tabla.append(('BACKGROUND', (0, row), (0, row), colors.HexColor("#FFEBEE"))) # Resaltar Rank
                estilo_tabla.append(('TEXTCOLOR', (0, row), (0, row), colors.red))

        t.setStyle(TableStyle(estilo_tabla))
        elements.append(t)
        
        elements.append(Spacer(1, 30))
        
        # SECCIÓN DE NOTAS TÉCNICAS
        elements.append(Paragraph("<b>OBSERVACIONES TÉCNICAS PARA PATRULLAS:</b>", estilos['Normal']))
        elementos_notas = [
            "• La prioridad 1-3 presenta repuntes de siniestralidad en el último ciclo mensual.",
            "• Los horarios críticos indican el inicio del despliegue del dispositivo.",
            "• En caso de climatología adversa, priorizar la Vigilancia Preventiva sobre el uso de drones."
        ]
        for nota in elementos_notas:
            elements.append(Paragraph(nota, estilos['Normal']))

        try:
            doc.build(elements)
            messagebox.showinfo("Éxito", "Orden de Servicio generada con diseño operativo.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo generar el archivo: {e}")
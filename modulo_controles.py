# ============================================================
# MÓDULO DE CONTROLES - modulo_controles.py
# Analiza las carreteras con mayor siniestralidad grave y mortal
# y propone dispositivos policiales específicos según la causa
# principal de cada tramo. Permite exportar una orden de servicio
# operativa en PDF para las patrullas de la Guardia Civil.
# ============================================================

import customtkinter as ctk # Librería para interfaz gráfica moderna
import psycopg2 # Conector con la base de datos PostgreSQL
from tkinter import messagebox, filedialog # Ventanas emergentes y diálogo para guardar archivos
from reportlab.lib.pagesizes import A4 # Tamaño de página PDF en vertical
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image # Componentes del PDF
from reportlab.lib import colors # Colores para el estilo de la tabla PDF
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle # Estilos de texto para el PDF
from datetime import datetime # Para obtener la fecha actual en la orden de servicio

class ModuloControles:
    def __init__(self, master, db_config):
        """
        Constructor del módulo. Se ejecuta al instanciarlo desde main.py.
        Parámetros:
            master    -- Frame padre donde se renderizará la interfaz
            db_config -- Diccionario con los parámetros de conexión a PostgreSQL
        """
        self.master = master # Referencia al contenedor padre
        self.db_config = db_config # Credenciales de conexión a la base de datos
        self.resultados_actuales = [] # Lista que almacenará los resultados del análisis para usarlos en la exportación PDF
        # Valores por defecto de los tres filtros del panel superior
        self.filtro_tipo_via = "Todas" # Filtra por tipo de carretera: Todas, Autovía/Autopista o Convencional
        self.filtro_periodo = "Semana" # Filtra por periodo: Semana completa o solo Fin de Semana
        self.filtro_control = "Todos" # Filtra por tipo de dispositivo policial propuesto

    def mostrar(self, volver_callback):
        """
        Construye y muestra toda la interfaz del módulo de controles.
        Parámetros:
            volver_callback -- Función de main.py que se ejecuta al pulsar el botón Volver
        """
        # Limpia cualquier widget previo del contenedor antes de construir la interfaz
        for widget in self.master.winfo_children():
            widget.destroy()

        # Fondo gris claro para el área de contenido
        self.master.configure(fg_color="#F2F2F2")

        # --- CABECERA ---
        # Frame transparente que contiene el botón Volver y el título del módulo
        header = ctk.CTkFrame(self.master, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkButton(header, text="← Volver", fg_color="#555", width=90, command=volver_callback).pack(side="left")
        ctk.CTkLabel(header, text="UNIDAD DE PLANIFICACIÓN OPERATIVA", text_color="#0B3526", 
                     font=ctk.CTkFont(size=22, weight="bold")).pack(side="left", padx=20)

        # --- PANEL DE FILTROS ---
        # Barra gris clara con los tres desplegables de filtrado y el botón de exportar
        filter_bar = ctk.CTkFrame(self.master, fg_color="#E0E0E0", height=50)
        filter_bar.pack(fill="x", padx=20, pady=5)

        # Filtro por tipo de vía: permite centrar el análisis en autovías/autopistas o carreteras convencionales
        ctk.CTkLabel(filter_bar, text="Tipo de Vía:", text_color="black").pack(side="left", padx=(15, 5))
        self.combo_via = ctk.CTkComboBox(filter_bar, values=["Todas", "Autovía/Autopista", "Convencional"], 
                                         command=self.actualizar_filtros, width=140)
        self.combo_via.pack(side="left", padx=5)

        # Filtro por periodo: permite analizar si los accidentes ocurren más en días laborables o en fin de semana
        ctk.CTkLabel(filter_bar, text="Periodo:", text_color="black").pack(side="left", padx=(10, 5))
        self.combo_periodo = ctk.CTkComboBox(filter_bar, values=["Semana", "Fin de Semana"], 
                                             command=self.actualizar_filtros, width=130)
        self.combo_periodo.pack(side="left", padx=5)

        # Filtro por tipo de dispositivo: muestra solo las carreteras que requieren ese dispositivo concreto
        # Los valores deben coincidir exactamente con los devueltos por obtener_metadatos_control()
        ctk.CTkLabel(filter_bar, text="Dispositivo:", text_color="black").pack(side="left", padx=(10, 5))
        self.combo_control = ctk.CTkComboBox(filter_bar, 
                                             values=["Todos", "ALCOHOLEMIA / DROGAS", "RADAR MÓVIL", "VIGILANCIA DRON/TEL", "VIGILANCIA PREVENTIVA", "VIGILANCIA GENÉRICA"], 
                                             command=self.actualizar_filtros, width=180)
        self.combo_control.pack(side="left", padx=5)

        # Botón para exportar la orden de servicio en PDF, alineado a la derecha de la barra
        ctk.CTkButton(filter_bar, text="📥 Orden de Servicio", fg_color="#2c3e50", width=140,
                     command=self.exportar_orden_pdf).pack(side="right", padx=15)

        # Contenedor con scroll donde se renderizan las tarjetas de análisis
        # Se guarda en self.scroll_cont para poder limpiarlo y regenerarlo al cambiar filtros
        self.scroll_cont = ctk.CTkScrollableFrame(self.master, fg_color="transparent")
        self.scroll_cont.pack(fill="both", expand=True, padx=20, pady=10)

        # Genera el análisis inicial con los filtros por defecto
        self.generar_analisis()

    def actualizar_filtros(self, _=None):
        """
        Se ejecuta automáticamente cada vez que el usuario cambia cualquier desplegable.
        Actualiza las tres variables de filtro con los valores actuales de los combos
        y regenera el análisis completo.
        Parámetros:
            _ -- Parámetro ignorado que CTkComboBox pasa automáticamente al ejecutar el command
        """
        self.filtro_tipo_via = self.combo_via.get()
        self.filtro_periodo = self.combo_periodo.get()
        self.filtro_control = self.combo_control.get()
        self.generar_analisis()

    def generar_analisis(self):
        """
        Consulta la base de datos con una query avanzada usando CTEs (Common Table Expressions)
        para obtener las carreteras con mayor número de accidentes graves y mortales,
        junto con la causa principal, la hora crítica y el clima más frecuente de cada tramo.
        Aplica los filtros activos de tipo de vía y periodo, filtra por tipo de dispositivo
        si está seleccionado uno concreto, y genera una tarjeta visual por cada resultado.
        """
        # Limpia las tarjetas del análisis anterior antes de generar las nuevas
        for widget in self.scroll_cont.winfo_children():
            widget.destroy()

        try:
            conn = psycopg2.connect(**self.db_config)
            cur = conn.cursor()

            # La cláusula WHERE base filtra solo accidentes graves o mortales
            # ya que son los que justifican un dispositivo policial
            where_clause = "WHERE (g.nivel ILIKE '%Mortal%' OR g.nivel ILIKE '%Grave%')"
            
            # Añade condición de tipo de vía según el filtro seleccionado
            # Las autovías y autopistas se identifican porque su nombre empieza por A- o AP-
            if self.filtro_tipo_via == "Autovía/Autopista":
                where_clause += " AND (c.nombre ILIKE 'A-%' OR c.nombre ILIKE 'AP-%')"
            elif self.filtro_tipo_via == "Convencional":
                where_clause += " AND NOT (c.nombre ILIKE 'A-%' OR c.nombre ILIKE 'AP-%')"
            
            # Filtra por fin de semana usando EXTRACT(DOW): 0=domingo, 6=sábado
            if self.filtro_periodo == "Fin de Semana":
                where_clause += " AND EXTRACT(DOW FROM a.fecha) IN (0, 6)"

            # Consulta principal usando cuatro CTEs encadenadas:
            # - TopCarreteras: las 20 carreteras con más accidentes graves/mortales,
            #   incluyendo contadores del mes actual y anterior para detectar tendencias
            # - CausaPrincipal: la causa más frecuente de accidente por carretera
            # - HoraPrincipal: la hora del día con más accidentes por carretera
            # - ClimaFrecuente: la condición climática más habitual por carretera
            # El ORDER secundario por c.nombre garantiza resultados consistentes en caso de empate
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
            datos_brutos = cur.fetchall() # Lista de tuplas con los resultados del análisis
            
            # Filtra los resultados por tipo de dispositivo si hay uno concreto seleccionado
            # obtener_metadatos_control() determina el tipo de dispositivo según la causa del accidente
            self.resultados_actuales = []
            for res in datos_brutos:
                tipo, _, _ = self.obtener_metadatos_control(res[2])
                if self.filtro_control == "Todos" or self.filtro_control == tipo:
                    self.resultados_actuales.append(res)
            
            # Limita a las 10 carreteras con mayor siniestralidad para no saturar la vista
            self.resultados_actuales = self.resultados_actuales[:10]

            if not self.resultados_actuales:
                ctk.CTkLabel(self.scroll_cont, text="No hay datos para esta combinación de filtros.", text_color="grey").pack(pady=50)
                return

            # Valor máximo de accidentes entre todos los resultados, usado para calcular
            # el porcentaje de la barra de progreso de cada tarjeta de forma proporcional
            max_acc = max([r[1] for r in self.resultados_actuales]) if self.resultados_actuales else 1

            # Genera una tarjeta visual por cada resultado, pasando el ranking (1-10) y el máximo
            for i, res in enumerate(self.resultados_actuales):
                self.crear_tarjeta_avanzada(res, i + 1, max_acc)

            cur.close()
            conn.close()
        except Exception as e:
            messagebox.showerror("Error", f"Error en análisis: {e}")

    def obtener_metadatos_control(self, causa):
        """
        Determina el tipo de dispositivo policial más adecuado según la causa principal
        del accidente, y devuelve también el color corporativo y el icono asociado.
        Parámetros:
            causa -- Texto descriptivo de la causa del accidente (de la tabla causas)
        Retorna:
            Tupla (tipo_dispositivo, color_hex, icono_emoji)
        """
        c = causa.lower() # Convierte a minúsculas para que la comparación no distinga mayúsculas
        if "alcohol" in c or "drogas" in c:
            return "ALCOHOLEMIA / DROGAS", "#C62828", "🍷" # Rojo: control de alcoholemia y drogas
        elif "velocidad" in c:
            return "RADAR MÓVIL", "#1565C0", "📸" # Azul: control de velocidad con radar
        elif "distracción" in c or "teléfono" in c:
            return "VIGILANCIA DRON/TEL", "#1565C0", "📱" # Azul: vigilancia de uso del teléfono al volante
        elif "clima" in c or "visibilidad" in c:
            return "VIGILANCIA PREVENTIVA", "#2E7D32", "🌧️" # Verde: vigilancia en condiciones adversas
        else:
            return "VIGILANCIA GENÉRICA", "#37474F", "🚔" # Gris oscuro: patrulla genérica de tráfico

    def crear_tarjeta_avanzada(self, datos, ranking, max_acc):
        """
        Construye y muestra una tarjeta visual para una carretera del análisis.
        Cada tarjeta tiene tres secciones:
          - Izquierda: ranking, nombre de la carretera y barra de siniestralidad proporcional
          - Centro: causa principal, hora crítica y recomendación de clima
          - Derecha: panel de color con el dispositivo policial propuesto
        Parámetros:
            datos   -- Tupla con los datos de la carretera (nombre, total, causa, hora, mes_actual, mes_anterior, clima)
            ranking -- Posición en el ranking (1 al 10)
            max_acc -- Número máximo de accidentes del resultado con mayor siniestralidad (para la barra proporcional)
        """
        # Desempaqueta la tupla de datos en variables con nombre
        nombre, total, causa, hora, m_actual, m_anterior, clima_top = datos
        # Obtiene el tipo de dispositivo, color y emoji según la causa
        tipo_ctrl, color, icono = self.obtener_metadatos_control(causa)
        
        # Una carretera es de ALTA prioridad si ha aumentado su siniestralidad en el último mes
        # y además está entre las tres primeras del ranking
        es_prioridad = (m_actual > m_anterior) and ranking <= 3
        
        # Frame principal de la tarjeta con borde gris y altura fija
        card = ctk.CTkFrame(self.scroll_cont, fg_color="white", corner_radius=12, border_width=1, border_color="#DDD", height=110)
        card.pack(fill="x", pady=5, padx=5)
        card.pack_propagate(False) # Impide que el contenido modifique la altura fija de la tarjeta

        # --- SECCIÓN IZQUIERDA: ranking y barra de siniestralidad ---
        left = ctk.CTkFrame(card, fg_color="transparent", width=220)
        left.pack(side="left", padx=15, pady=10)
        left.pack_propagate(False)
        
        # Fila superior con número de ranking y etiqueta de alerta si es prioritaria
        header_v = ctk.CTkFrame(left, fg_color="transparent")
        header_v.pack(fill="x")
        ctk.CTkLabel(header_v, text=f"{ranking}º", font=("Arial", 20, "bold"), text_color="#0B3526").pack(side="left")
        if es_prioridad:
            # Etiqueta roja de advertencia que solo aparece si hay repunte reciente y está en el top 3
            ctk.CTkLabel(header_v, text="⚠️ ALTA", fg_color="#FFEBEE", text_color="#C62828", 
                         font=("Arial", 9, "bold"), corner_radius=5).pack(side="left", padx=5)

        # Nombre de la carretera en negrita
        ctk.CTkLabel(left, text=nombre, font=("Arial", 15, "bold"), text_color="black").pack(anchor="w")
        
        # Barra de progreso proporcional: muestra visualmente el peso relativo de esta carretera
        # respecto a la de mayor siniestralidad del análisis actual
        porcentaje = total / max_acc # Valor entre 0 y 1
        bar_bg = ctk.CTkFrame(left, fg_color="#EEE", height=6, width=160)
        bar_bg.pack(anchor="w", pady=(5,0))
        # La barra roja para el top 3 y amarilla para el resto. El ancho es proporcional al porcentaje
        bar_fill = ctk.CTkFrame(bar_bg, fg_color="#C62828" if ranking <=3 else "#FBC02D", height=6, width=160 * porcentaje)
        bar_fill.place(x=0, y=0) # Se posiciona con place para controlar el ancho exacto en píxeles
        ctk.CTkLabel(left, text=f"{total} incidentes críticos", font=("Arial", 10), text_color="#666").pack(anchor="w")

        # --- SECCIÓN CENTRAL: causa, hora crítica y recomendación de clima ---
        center = ctk.CTkFrame(card, fg_color="transparent")
        center.pack(side="left", expand=True, fill="both", padx=10, pady=10)
        
        # Causa principal del accidente con su icono representativo
        ctk.CTkLabel(center, text=f"{icono} {causa}", font=("Arial", 12), text_color="#333").pack(anchor="w")
        # Hora crítica: franja de una hora con mayor concentración de accidentes en esa carretera
        # El % 24 gestiona correctamente la medianoche (hora 23 → franja 23:00h a 00:00h)
        ctk.CTkLabel(center, text=f"🕒 Crítico: {int(hora):02d}:00h a {int(hora+1)%24:02d}:00h", 
                     font=("Arial", 12, "bold"), text_color="black").pack(anchor="w")
        
        # Clima más frecuente en los accidentes de esa carretera como recomendación operativa
        msg_clima = f"💡 Rec. Clima: {clima_top.lower()}"
        ctk.CTkLabel(center, text=msg_clima, text_color="#1B5E20", font=("Arial", 10, "italic")).pack(anchor="w")

        # --- SECCIÓN DERECHA: panel de color con el dispositivo propuesto ---
        # El color de fondo varía según el tipo de dispositivo (rojo, azul, verde o gris)
        right = ctk.CTkFrame(card, fg_color=color, corner_radius=8, width=210)
        right.pack(side="right", padx=10, pady=10, fill="y")
        right.pack_propagate(False)
        
        ctk.CTkLabel(right, text="DISPOSITIVO PROPUESTO", text_color="white", font=("Arial", 9, "bold")).pack(pady=(12,0))
        # Nombre del dispositivo con wraplength para que el texto largo se ajuste dentro del panel
        ctk.CTkLabel(right, text=tipo_ctrl, text_color="white", font=("Arial", 11, "bold"), wraplength=180).pack(expand=True)

    def exportar_orden_pdf(self):
        """
        Genera y exporta un PDF con formato de orden de servicio operativa para las patrullas.
        El documento incluye una cabecera institucional con fecha y filtros aplicados,
        una tabla de dispositivos con los 10 resultados del análisis,
        y una sección de observaciones técnicas para el mando.
        Solo se ejecuta si hay resultados en el análisis actual.
        """
        # No hace nada si no hay resultados que exportar
        if not self.resultados_actuales: return
        
        # Abre el diálogo para que el usuario elija dónde guardar el PDF
        path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF", "*.pdf")])
        if not path: return # Sale si el usuario cancela el diálogo

        doc = SimpleDocTemplate(path, pagesize=A4)
        estilos = getSampleStyleSheet()
        elements = [] # Lista de elementos que se añadirán al PDF en orden

        # --- TÍTULO ---
        # Estilo personalizado centrado en verde oscuro corporativo
        style_title = ParagraphStyle('Title', parent=estilos['Heading1'], alignment=1, fontSize=20, textColor=colors.HexColor("#0B3526"), spaceAfter=20)
        elements.append(Paragraph("ORDEN DE SERVICIO OPERATIVO", style_title))
        
        # --- CABECERA INFORMATIVA ---
        # Tabla de dos columnas con los metadatos del servicio: unidad, fecha, tipo de vía y periodo
        # Usa los filtros activos en el momento de exportar para reflejar el contexto del análisis
        info_header = [
            [Paragraph("<b>UNIDAD:</b> Tráfico / Seguridad Vial", estilos['Normal']), Paragraph(f"<b>FECHA:</b> {datetime.now().strftime('%d/%m/%Y')}", estilos['Normal'])],
            [Paragraph(f"<b>TIPO VÍA:</b> {self.filtro_tipo_via}", estilos['Normal']), Paragraph(f"<b>PERIODO:</b> {self.filtro_periodo}", estilos['Normal'])]
        ]
        head_table = Table(info_header, colWidths=[250, 250])
        head_table.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'TOP')]))
        elements.append(head_table)
        elements.append(Spacer(1, 20)) # Espacio vertical de separación entre secciones

        # TABLA DE DISPOSITIVOS (MÁS GRÁFICA)
        # Añadimos colores de fondo según el tipo de riesgo para que el oficial lo vea rápido
        data = [["POS.", "LOCALIZACIÓN", "DISPOSITIVO RECOMENDADO", "HORARIO CRÍTICO", "FACTOR RIESGO"]]
        
        # Rellena la tabla con los resultados del análisis actual
        for i, res in enumerate(self.resultados_actuales):
            tipo, _, _ = self.obtener_metadatos_control(res[2]) # Determina el dispositivo según la causa
            data.append([
                i+1, # Posición en el ranking
                res[0], # Nombre de la carretera
                tipo, # Tipo de dispositivo policial propuesto
                f"{int(res[3]):02d}:00h - {int(res[3]+1)%24:02d}:00h", #Franja horaria crítica
                res[2].upper() #Causa principal en mayúsculas como factor de riesgo
            ])

        # Anchos de columna en puntos tipográficos, ajustados al contenido de cada campo
        t = Table(data, colWidths=[35, 110, 160, 100, 115])
        
        # Estilo de tabla con colores "de mando"
        estilo_tabla = [
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#0B3526")), # Cabecera verde oscura
            ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke), # Texto blanco en cabecera
            ('ALIGN', (0,0), (-1,-1), 'CENTER'), # Centrado en todas las celdas
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'), # Negrita en la cabecera
            ('FONTSIZE', (0,0), (-1,-1), 8), # Tamaño de fuente reducido
            ('BOTTOMPADDING', (0,0), (-1,0), 10), # Margen inferior en cabecera
            ('GRID', (0,0), (-1,-1), 0.5, colors.grey), # Rejilla gris en todas las celdas
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'), # Alineación vertical centrada
        ]
        
        # Resalta en rojo la columna de posición de las tres primeras filas
        # para que el mando identifique visualmente las zonas de máxima prioridad
        for row in range(1, 4):
            if row < len(data):
                estilo_tabla.append(('BACKGROUND', (0, row), (0, row), colors.HexColor("#FFEBEE"))) # Resaltar Rank
                estilo_tabla.append(('TEXTCOLOR', (0, row), (0, row), colors.red))

        t.setStyle(TableStyle(estilo_tabla))
        elements.append(t)
        
        elements.append(Spacer(1, 30)) # Espacio de separación antes de las notas técnicas
        
        # --- NOTAS TÉCNICAS ---
        # Instrucciones fijas para las patrullas sobre cómo interpretar y ejecutar la orden
        elements.append(Paragraph("<b>OBSERVACIONES TÉCNICAS PARA PATRULLAS:</b>", estilos['Normal']))
        elementos_notas = [
            "• La prioridad 1-3 presenta repuntes de siniestralidad en el último ciclo mensual.",
            "• Los horarios críticos indican el inicio del despliegue del dispositivo.",
            "• En caso de climatología adversa, priorizar la Vigilancia Preventiva sobre el uso de drones."
        ]
        for nota in elementos_notas:
            elements.append(Paragraph(nota, estilos['Normal']))

        try:
            doc.build(elements) # Genera y escribe el archivo PDF en disco con todos los elementos
            messagebox.showinfo("Éxito", "Orden de Servicio generada con diseño operativo.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo generar el archivo: {e}")
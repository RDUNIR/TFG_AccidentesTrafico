# ============================================================
# MÓDULO DE GRÁFICOS - modulo_graficos.py
# Genera análisis estadísticos visuales sobre los accidentes
# de tráfico mediante cinco tipos de gráficos configurables.
# Incluye tarjetas KPI con totales globales y exportación
# de los gráficos generados como imagen PNG.
# ============================================================

import customtkinter as ctk                              # Librería para interfaz gráfica moderna
from tkinter import messagebox, filedialog               # Ventanas emergentes y diálogo para guardar archivos
import psycopg2                                          # Conector con la base de datos PostgreSQL
import pandas as pd                                      # Manipulación de datos en forma de DataFrame para los gráficos
import matplotlib.pyplot as plt                          # Generación de figuras y ejes para los gráficos
from matplotlib.backends.backend_agg import FigureCanvasAgg      # Backend de renderizado (no interactivo, para exportar)
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg  # Backend para incrustar gráficos en la interfaz Tkinter
import seaborn as sns                                    # Librería de visualización estadística sobre matplotlib
from datetime import datetime, timedelta                 # Manejo de fechas para calcular los rangos temporales
import tkinter as tk                                     # Librería base de interfaz gráfica
from tkinter import ttk                                  # Widgets adicionales de Tkinter (no se usa directamente pero se importa por compatibilidad)

class ModuloGraficos:
    def __init__(self, master, db_config):
        """
        Constructor del módulo. Se ejecuta al instanciarlo desde main.py.
        Parámetros:
            master    -- Frame padre donde se renderizará la interfaz
            db_config -- Diccionario con los parámetros de conexión a PostgreSQL
        """
        self.master = master      # Referencia al contenedor padre
        self.db_config = db_config  # Credenciales de conexión a la base de datos
        self.canvas = None        # Referencia al canvas de matplotlib incrustado en la interfaz (None hasta que se genera el primer gráfico)
        self.fig = None           # Referencia a la figura de matplotlib activa (None hasta que se genera el primer gráfico)

    def mostrar(self, volver_callback):
        """
        Construye y muestra toda la interfaz del módulo de gráficos.
        Parámetros:
            volver_callback -- Función de main.py que se ejecuta al pulsar el botón Volver
        """
        # Limpia cualquier widget previo del contenedor antes de construir la interfaz
        for widget in self.master.winfo_children():
            widget.destroy()

        # --- CABECERA ---
        header = ctk.CTkFrame(self.master, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(15, 5))
        
        ctk.CTkButton(header, text="← Volver", fg_color="#555", width=90, command=volver_callback).pack(side="left")
        ctk.CTkLabel(header, text="CENTRO DE ANÁLISIS ESTADÍSTICO - ÁVILA", text_color="#0B3526", 
                     font=ctk.CTkFont(size=24, weight="bold")).pack(side="left", padx=20)

        # --- TARJETAS KPI ---
        # Frame horizontal donde se muestran las tres tarjetas de totales globales
        # Se guarda en self.kpi_frame para poder regenerarlas al cambiar el periodo temporal
        self.kpi_frame = ctk.CTkFrame(self.master, fg_color="transparent")
        self.kpi_frame.pack(fill="x", padx=20, pady=10)
        # Carga inicial de los KPI sin filtro temporal (muestra totales históricos)
        self.actualizar_kpis("")

        # --- CONTENEDOR PRINCIPAL ---
        # Divide la pantalla en dos zonas: panel de configuración (izquierda) y área del gráfico (derecha)
        main_container = ctk.CTkFrame(self.master, fg_color="transparent")
        main_container.pack(fill="both", expand=True, padx=20, pady=10)

        # --- PANEL DE CONFIGURACIÓN ---
        # Panel verde oscuro fijo de 280px en el lado izquierdo con todos los controles
        control_panel = ctk.CTkFrame(main_container, width=280, fg_color="#0B3526", corner_radius=15)
        control_panel.pack(side="left", fill="y", padx=(0, 10), pady=0)
        control_panel.pack_propagate(False) # Impide que el contenido modifique el ancho fijo

        ctk.CTkLabel(control_panel, text="CONFIGURACIÓN", font=("Arial", 16, "bold"), text_color="#DAA520").pack(pady=20)

        # Desplegable de periodo temporal: determina el rango de fechas de la consulta
        self.crear_label_control(control_panel, "Periodo Temporal:")
        self.combo_periodo = self.crear_combo(control_panel, ["Todo el histórico", "Últimos 7 días", "Últimos 30 días", "Año actual"])
        
        # Desplegable de variable de análisis: determina qué columna se analiza en el gráfico
        # Se deshabilita automáticamente en los gráficos que tienen variable fija
        self.crear_label_control(control_panel, "Variable de Análisis:")
        self.combo_dato = self.crear_combo(control_panel, ["Gravedad", "Causa", "Clima", "Carretera"])
        
        # Desplegable de tipo de visualización: determina qué tipo de gráfico se genera
        # Al cambiar, llama a gestionar_bloqueo_variables para habilitar o deshabilitar combo_dato
        self.crear_label_control(control_panel, "Tipo de Visualización:")
        self.combo_tipo = ctk.CTkComboBox(control_panel, width=220, fg_color="white", text_color="black",
                                         values=["Barras (Interactivo)", "Donut (Proporción)", "Mapa de Calor (Día/Hora)", "Análisis por Franja Horaria", "Índice de Letalidad (PRO)"],
                                         command=self.gestionar_bloqueo_variables)
        self.combo_tipo.set("Barras (Interactivo)")
        self.combo_tipo.pack(pady=5)

        # Botón principal que ejecuta la consulta y genera el gráfico con la configuración actual
        ctk.CTkButton(control_panel, text="GENERAR ANÁLISIS 📊", fg_color="#1b5e46", hover_color="#144d37", 
                     height=45, font=("Arial", 13, "bold"), command=self.actualizar_todo).pack(pady=30, padx=20, fill="x")
        
        # Botón para guardar el gráfico actual como imagen PNG en disco
        ctk.CTkLabel(control_panel, text="Exportar:", text_color="#BDC3C7").pack(pady=(10,0))
        ctk.CTkButton(control_panel, text="Guardar Imagen 💾", fg_color="#555", height=35, command=self.exportar_grafico).pack(pady=5, padx=40, fill="x")

        # --- ÁREA DEL GRÁFICO ---
        # Frame blanco que ocupa todo el espacio restante a la derecha del panel de configuración
        self.graph_frame = ctk.CTkFrame(main_container, fg_color="white", corner_radius=15, border_width=1, border_color="#E0E0E0")
        self.graph_frame.pack(side="right", fill="both", expand=True)
        
        # Mensaje de instrucción inicial que se muestra hasta que el usuario genera el primer gráfico
        self.info_label = ctk.CTkLabel(self.graph_frame, text="Configure los filtros y pulse 'Generar Análisis'", text_color="grey", font=("Arial", 12, "italic"))
        self.info_label.pack(pady=(10, 0))
        
        # Subframe transparente dentro del área del gráfico donde se incrusta el canvas de matplotlib
        self.canvas_container = ctk.CTkFrame(self.graph_frame, fg_color="transparent")
        self.canvas_container.pack(fill="both", expand=True)

    def gestionar_bloqueo_variables(self, seleccion):
        """
        Habilita o deshabilita el desplegable de variable de análisis según el tipo de gráfico
        seleccionado. Los gráficos de Mapa de Calor e Índice de Letalidad tienen variable fija
        y no permiten elegir, por lo que se deshabilita el combo para evitar confusión.
        Parámetros:
            seleccion -- Valor del tipo de gráfico seleccionado, pasado automáticamente por CTkComboBox
        """
        # Estos dos tipos de gráfico tienen variable fija y no usan el combo_dato
        graficos_fijos = ["Mapa de Calor (Día/Hora)", "Índice de Letalidad (PRO)"]
        if seleccion in graficos_fijos:
            # Deshabilita el combo y lo oscurece visualmente para indicar que no está disponible
            self.combo_dato.configure(state="disabled", fg_color="#333", text_color="grey")
        else:
            # Reactiva el combo con su estilo normal cuando se selecciona un gráfico configurable
            self.combo_dato.configure(state="normal", fg_color="white", text_color="black")

    def crear_label_control(self, p, t):
        """
        Crea una etiqueta de sección en el panel de configuración.
        Parámetros:
            p -- Frame padre donde se añade la etiqueta (el panel de configuración)
            t -- Texto de la etiqueta
        """
        ctk.CTkLabel(p, text=t, text_color="#BDC3C7", font=("Arial", 12)).pack(pady=(10, 0), padx=25, anchor="w")

    def crear_combo(self, p, v):
        """
        Crea un desplegable estilizado en el panel de configuración,
        lo inicializa con el primer valor de la lista y lo devuelve.
        Parámetros:
            p -- Frame padre donde se añade el desplegable
            v -- Lista de valores del desplegable
        """
        cb = ctk.CTkComboBox(p, values=v, width=220, fg_color="white", text_color="black")
        cb.set(v[0]); # Selecciona el primer valor por defecto
        cb.pack(pady=5); 
        return cb

    def crear_tarjeta_kpi(self, titulo, valor, color_borde):
        """
        Crea una tarjeta KPI individual con un título y un valor numérico grande.
        Se usa para mostrar los totales de accidentes, fallecidos y heridos.
        Parámetros:
            titulo      -- Nombre del indicador (ej: 'ACCIDENTES', 'FALLECIDOS')
            valor       -- Valor numérico a mostrar en grande
            color_borde -- Color hexadecimal del borde de la tarjeta para identificación visual
        """
        card = ctk.CTkFrame(self.kpi_frame, fg_color="white", corner_radius=12, border_width=2, border_color=color_borde, height=80)
        card.pack(side="left", padx=10, expand=True, fill="both")
        card.pack_propagate(False) # Mantiene la altura fija de 80px
        ctk.CTkLabel(card, text=titulo, font=("Arial", 11, "bold"), text_color="grey").pack(pady=(10,0))
        ctk.CTkLabel(card, text=valor, font=("Arial", 26, "bold"), text_color="black").pack()

    def actualizar_kpis(self, filtro):
        """
        Consulta la base de datos y actualiza las tres tarjetas KPI con los totales
        del periodo temporal seleccionado. Si hay error de conexión, no muestra nada.
        Parámetros:
            filtro -- Fragmento SQL con la condición de fecha (ej: " AND fecha >= '2024-01-01'")
                      o cadena vacía para mostrar el histórico completo
        """
        # Elimina las tarjetas KPI anteriores antes de regenerarlas con los nuevos valores
        for w in self.kpi_frame.winfo_children(): w.destroy()
        try:
            conn = psycopg2.connect(**self.db_config); cur = conn.cursor()
            # WHERE 1=1 permite añadir el filtro dinámicamente sin problema de sintaxis
            cur.execute(f"SELECT COUNT(*), SUM(num_fallecidos), SUM(num_heridos) FROM accidentes WHERE 1=1 {filtro}")
            res = cur.fetchone()
            # Crea las tres tarjetas con sus colores corporativos: verde, rojo oscuro y dorado
            self.crear_tarjeta_kpi("ACCIDENTES", str(res[0] or 0), "#0B3526") # or 0 evita mostrar None si no hay datos
            self.crear_tarjeta_kpi("FALLECIDOS", str(res[1] or 0), "#8B0000")
            self.crear_tarjeta_kpi("HERIDOS", str(res[2] or 0), "#DAA520")
            cur.close(); conn.close()
        except: pass # Si falla la conexión simplemente no muestra las tarjetas

    def actualizar_todo(self):
        """
        Se ejecuta al pulsar 'Generar Análisis'. Construye el fragmento SQL de filtro
        de fechas según el periodo seleccionado, actualiza los KPI y regenera el gráfico.
        """
        periodo = self.combo_periodo.get()
        filtro = "" # Cadena vacía = sin filtro de fecha = histórico completo
        # Calcula la fecha de inicio según el periodo seleccionado
        if periodo == "Últimos 7 días": filtro = f" AND fecha >= '{(datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')}'"
        elif periodo == "Últimos 30 días": filtro = f" AND fecha >= '{(datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')}'"
        elif periodo == "Año actual": filtro = f" AND fecha >= '{datetime.now().year}-01-01'"
        
        # Actualiza primero los KPI y luego el gráfico con el mismo filtro
        self.actualizar_kpis(filtro)
        self.actualizar_grafico(filtro)

    def actualizar_grafico(self, filtro):
        """
        Genera el gráfico seleccionado consultando la base de datos con el filtro temporal.
        Implementa cinco tipos de gráfico distintos según la selección del usuario:
          - Barras (Interactivo): barras agrupadas por la variable seleccionada
          - Donut (Proporción): gráfico de donut con proporciones por categoría
          - Mapa de Calor (Día/Hora): matriz de riesgo que cruza día de la semana y hora del día
          - Análisis por Franja Horaria: barras agrupadas por mañana/tarde/noche y subcategoría
          - Índice de Letalidad (PRO): porcentaje de accidentes con fallecidos por causa
        Parámetros:
            filtro -- Fragmento SQL con la condición de fecha temporal
        """
        tipo = self.combo_tipo.get() # Tipo de gráfico seleccionado
        variable = self.combo_dato.get() # Variable de análisis seleccionada
        self.info_label.configure(text="", text_color="grey") # Limpia el mensaje de instrucción
        
        try:
            # Si ya hay un gráfico anterior, destruye su canvas para evitar superposición
            if self.canvas: self.canvas.get_tk_widget().destroy()
            # Crea una nueva figura de matplotlib con tamaño y resolución definidos
            self.fig, ax = plt.subplots(figsize=(7, 5.5), dpi=100)
            conn = psycopg2.connect(**self.db_config)

            # ================================================================
            # GRÁFICO 1: ANÁLISIS POR FRANJA HORARIA
            # Barras agrupadas que muestran la distribución de accidentes por
            # franja horaria (Mañana/Tarde/Noche) y la variable seleccionada
            # ================================================================
            if "Franja Horaria" in tipo:
                # Mapeo de variable legible a columna SQL correspondiente
                mapeo = {"Gravedad": "g.nivel", "Causa": "cau.descripcion", "Clima": "cl.descripcion", "Carretera": "carr.nombre"}
                col_variable = mapeo[variable]
                
                filtro_adicional = ""
                if variable == "Carretera":
                    # Para carreteras, primero obtiene el Top 10 para no saturar el gráfico
                    query_top = f"SELECT {col_variable} as nombre FROM accidentes a LEFT JOIN carreteras carr ON a.carretera_id = carr.id WHERE 1=1 {filtro} GROUP BY {col_variable} ORDER BY COUNT(*) DESC LIMIT 10"
                    df_top = pd.read_sql(query_top, conn)
                    
                    if not df_top.empty:
                        nombres_top = df_top['nombre'].dropna().unique().tolist()
                        if nombres_top:
                            # Construye un filtro IN con los nombres del top 10
                            formato_nombres = "', '".join(nombres_top)
                            filtro_adicional = f" AND {col_variable} IN ('{formato_nombres}')"
                            self.info_label.configure(text="Mostrando Top 10 carreteras con más accidentes", text_color="#1b5e46")
                    else:
                        self.info_label.configure(text="No se encontraron carreteras en este periodo", text_color="red")
                # Consulta principal: agrupa por franja horaria y subcategoría
                # orden_num es un número auxiliar para ordenar las franjas cronológicamente (0=Mañana, 1=Tarde, 2=Noche)
                query = f"""SELECT 
                            CASE 
                                WHEN hora >= '08:00:00' AND hora < '14:00:00' THEN 'Mañana'
                                WHEN hora >= '14:00:00' AND hora < '22:00:00' THEN 'Tarde'
                                ELSE 'Noche'
                            END as franja, 
                            {col_variable} as subcategoria,
                            COUNT(*) as cantidad,
                            CASE 
                                WHEN hora >= '08:00:00' AND hora < '14:00:00' THEN 0
                                WHEN hora >= '14:00:00' AND hora < '22:00:00' THEN 1
                                ELSE 2
                            END as orden_num
                            FROM accidentes a
                            LEFT JOIN carreteras carr ON a.carretera_id = carr.id 
                            LEFT JOIN gravedad g ON a.gravedad_id = g.id 
                            LEFT JOIN clima cl ON a.clima_id = cl.id 
                            LEFT JOIN causas cau ON a.causa_id = cau.id 
                            WHERE 1=1 {filtro} {filtro_adicional}
                            GROUP BY franja, subcategoria, orden_num 
                            ORDER BY orden_num ASC, cantidad DESC"""
                
                df = pd.read_sql(query, conn)
                if not df.empty:
                    # hue=subcategoria agrupa las barras por la variable seleccionada dentro de cada franja
                    sns.barplot(data=df, x="franja", y="cantidad", hue="subcategoria", ax=ax, palette="viridis")
                    titulo = f"ANÁLISIS DE {variable.upper()} POR FRANJA"
                    if variable == "Carretera": titulo += " (TOP 10)"
                    ax.set_title(titulo, weight='bold', pad=15)
                    # Leyenda fuera del gráfico para no tapar las barras
                    ax.legend(title=variable, bbox_to_anchor=(1.05, 1), loc='upper left')
                    ax.set_xlabel("")
                    ax.set_ylabel("Nº de Accidentes")
                else: 
                    self.info_label.configure(text="Sin datos suficientes para generar el gráfico", text_color="grey")

            # ================================================================
            # GRÁFICO 2: ÍNDICE DE LETALIDAD
            # Barras que muestran el porcentaje de accidentes con fallecidos
            # por causa, para identificar las causas más mortales
            # ================================================================
            elif "Letalidad" in tipo:
                col_db = "cau.descripcion"
                # Calcula la letalidad como: (nº accidentes con fallecidos / total accidentes) * 100
                # NULLIF evita división por cero en causas sin accidentes
                # ::float convierte el entero a decimal para obtener porcentaje con decimales
                query = f"""SELECT {col_db} as etiqueta, 
                            (SUM(CASE WHEN num_fallecidos > 0 THEN 1 ELSE 0 END)::float / NULLIF(COUNT(*),0)) * 100 as letalidad
                            FROM accidentes a 
                            LEFT JOIN causas cau ON a.causa_id = cau.id 
                            WHERE 1=1 {filtro} GROUP BY {col_db} HAVING COUNT(*) > 0"""
                df = pd.read_sql(query, conn)
                if not df.empty:
                    # Reds_r: paleta de rojos invertida (más intenso = mayor letalidad)
                    sns.barplot(data=df, x="etiqueta", y="letalidad", ax=ax, palette="Reds_r")
                    ax.set_title("ÍNDICE DE LETALIDAD POR CAUSA", weight='bold', pad=15)
                    ax.set_xlabel("") 
                    ax.set_ylabel("Letalidad (%)")
                    plt.xticks(rotation=30, ha='right')
                else: self.info_label.configure(text="Datos insuficientes")

            # ================================================================
            # GRÁFICO 3: MAPA DE CALOR DÍA VS HORA
            # Matriz donde cada celda muestra el número de accidentes para
            # cada combinación de día de la semana y hora del día
            # ================================================================
            elif "Mapa de Calor" in tipo:
                # DOW = Day Of Week: 0=domingo, 1=lunes, ..., 6=sábado
                query = f"SELECT EXTRACT(DOW FROM fecha) as dia, EXTRACT(HOUR FROM hora) as hora_num, COUNT(*) FROM accidentes WHERE 1=1 {filtro} GROUP BY dia, hora_num"
                df = pd.read_sql(query, conn)
                if not df.empty:
                    # pivot convierte el DataFrame a matriz 2D (días x horas) para el heatmap
                    pivot = df.pivot(index='dia', columns='hora_num', values='count').fillna(0)
                    dias_nombre = ['Dom', 'Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb']
                    # annot=True muestra el valor numérico dentro de cada celda
                    # cmap="YlGn": paleta de amarillo a verde (más oscuro = más accidentes)
                    sns.heatmap(pivot, annot=True, fmt=".0f", cmap="YlGn", ax=ax, cbar=False)
                    # Sustituye los números de día (0-6) por sus nombres abreviados
                    ax.set_yticklabels([dias_nombre[int(i)] for i in pivot.index if int(i) < 7], rotation=0)
                    ax.set_title("MAPA DE RIESGO: DÍA VS HORA", weight='bold', pad=15)
                    ax.set_xlabel("Hora del Día")
                    ax.set_ylabel("")

            # ================================================================
            # GRÁFICOS 4 y 5: BARRAS Y DONUT
            # Gráficos simples agrupados por la variable seleccionada
            # ================================================================
            else:
                # Mapeo de variable legible a columna SQL correspondiente
                mapeo = {"Gravedad": "g.nivel", "Causa": "cau.descripcion", "Clima": "cl.descripcion", "Carretera": "carr.nombre"}
                col = mapeo[variable]
                query = f"SELECT {col} as etiqueta, COUNT(*) as cantidad FROM accidentes a LEFT JOIN carreteras carr ON a.carretera_id = carr.id LEFT JOIN gravedad g ON a.gravedad_id = g.id LEFT JOIN clima cl ON a.clima_id = cl.id LEFT JOIN causas cau ON a.causa_id = cau.id WHERE 1=1 {filtro} GROUP BY {col}"
                df = pd.read_sql(query, conn)
                if not df.empty:
                    if "Barras" in tipo:
                        # Gráfico de barras vertical con paleta de colores variados
                        sns.barplot(data=df, x="etiqueta", y="cantidad", ax=ax, palette="Paired")
                        ax.set_title(f"ACCIDENTES POR {variable.upper()}", weight='bold', pad=15)
                        ax.set_xlabel("")
                        plt.xticks(rotation=30, ha='right') # Rota etiquetas para evitar solapamiento
                    else:
                        # Gráfico de donut: pie chart con un agujero en el centro (width=0.4)
                        # autopct muestra el porcentaje dentro de cada sector
                        colores = sns.color_palette("viridis", n_colors=len(df))
                        ax.pie(df["cantidad"], labels=None, autopct='%1.1f%%', startangle=140, 
                               wedgeprops={'width':0.4, 'edgecolor':'w'}, colors=colores,
                               pctdistance=0.82, textprops={'fontsize': 10, 'weight': 'bold'})
                        # Leyenda debajo del gráfico en dos columnas para no tapar el donut
                        ax.legend(df["etiqueta"], title=variable, loc="upper center", 
                                  bbox_to_anchor=(0.5, -0.05), ncol=2, frameon=False)
                        ax.set_title(f"PROPORCIÓN POR {variable.upper()}", weight='bold', pad=20)

            conn.close()
            # tight_layout ajusta automáticamente los márgenes para evitar que las etiquetas se corten
            self.fig.tight_layout()
            # Incrusta la figura de matplotlib dentro del frame de la interfaz Tkinter
            self.canvas = FigureCanvasTkAgg(self.fig, master=self.canvas_container)
            self.canvas.draw()
            self.canvas.get_tk_widget().pack(fill="both", expand=True, padx=15, pady=5)
        except Exception as e: 
            messagebox.showerror("Error", f"Error al generar gráfico: {str(e)}")

    def exportar_grafico(self):
        """
        Guarda el gráfico actualmente visible como imagen PNG en la ruta elegida por el usuario.
        Solo se ejecuta si hay una figura generada (self.fig no es None).
        dpi=300 genera una imagen de alta resolución apta para documentos e informes.
        bbox_inches='tight' recorta los márgenes sobrantes de la imagen exportada.
        """
        if self.fig:
            ruta = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("Imagen PNG", "*.png")])
            if ruta: self.fig.savefig(ruta, dpi=300, bbox_inches='tight'); messagebox.showinfo("Éxito", "Exportado.")
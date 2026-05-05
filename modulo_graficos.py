import customtkinter as ctk
from tkinter import messagebox, filedialog
import psycopg2
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg 
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import seaborn as sns
from datetime import datetime, timedelta
import tkinter as tk
from tkinter import ttk

class ModuloGraficos:
    def __init__(self, master, db_config):
        self.master = master
        self.db_config = db_config
        self.canvas = None
        self.fig = None

    def mostrar(self, volver_callback):
        for widget in self.master.winfo_children():
            widget.destroy()

        header = ctk.CTkFrame(self.master, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(15, 5))
        
        ctk.CTkButton(header, text="← Volver", fg_color="#555", width=90, command=volver_callback).pack(side="left")
        ctk.CTkLabel(header, text="CENTRO DE ANÁLISIS ESTADÍSTICO - ÁVILA", text_color="#0B3526", 
                     font=ctk.CTkFont(size=24, weight="bold")).pack(side="left", padx=20)

        self.kpi_frame = ctk.CTkFrame(self.master, fg_color="transparent")
        self.kpi_frame.pack(fill="x", padx=20, pady=10)
        self.actualizar_kpis("")

        main_container = ctk.CTkFrame(self.master, fg_color="transparent")
        main_container.pack(fill="both", expand=True, padx=20, pady=10)

        control_panel = ctk.CTkFrame(main_container, width=280, fg_color="#0B3526", corner_radius=15)
        control_panel.pack(side="left", fill="y", padx=(0, 10), pady=0)
        control_panel.pack_propagate(False)

        ctk.CTkLabel(control_panel, text="CONFIGURACIÓN", font=("Arial", 16, "bold"), text_color="#DAA520").pack(pady=20)

        self.crear_label_control(control_panel, "Periodo Temporal:")
        self.combo_periodo = self.crear_combo(control_panel, ["Todo el histórico", "Últimos 7 días", "Últimos 30 días", "Año actual"])
        
        self.crear_label_control(control_panel, "Variable de Análisis:")
        self.combo_dato = self.crear_combo(control_panel, ["Gravedad", "Causa", "Clima", "Carretera"])
        
        self.crear_label_control(control_panel, "Tipo de Visualización:")
        self.combo_tipo = ctk.CTkComboBox(control_panel, width=220, fg_color="white", text_color="black",
                                         values=["Barras (Interactivo)", "Donut (Proporción)", "Mapa de Calor (Día/Hora)", "Análisis por Franja Horaria", "Índice de Letalidad (PRO)"],
                                         command=self.gestionar_bloqueo_variables)
        self.combo_tipo.set("Barras (Interactivo)")
        self.combo_tipo.pack(pady=5)

        ctk.CTkButton(control_panel, text="GENERAR ANÁLISIS 📊", fg_color="#1b5e46", hover_color="#144d37", 
                     height=45, font=("Arial", 13, "bold"), command=self.actualizar_todo).pack(pady=30, padx=20, fill="x")
        
        ctk.CTkLabel(control_panel, text="Exportar:", text_color="#BDC3C7").pack(pady=(10,0))
        ctk.CTkButton(control_panel, text="Guardar Imagen 💾", fg_color="#555", height=35, command=self.exportar_grafico).pack(pady=5, padx=40, fill="x")

        self.graph_frame = ctk.CTkFrame(main_container, fg_color="white", corner_radius=15, border_width=1, border_color="#E0E0E0")
        self.graph_frame.pack(side="right", fill="both", expand=True)
        
        self.info_label = ctk.CTkLabel(self.graph_frame, text="Configure los filtros y pulse 'Generar Análisis'", text_color="grey", font=("Arial", 12, "italic"))
        self.info_label.pack(pady=(10, 0))
        
        self.canvas_container = ctk.CTkFrame(self.graph_frame, fg_color="transparent")
        self.canvas_container.pack(fill="both", expand=True)

    def gestionar_bloqueo_variables(self, seleccion):
        graficos_fijos = ["Mapa de Calor (Día/Hora)", "Índice de Letalidad (PRO)"]
        if seleccion in graficos_fijos:
            self.combo_dato.configure(state="disabled", fg_color="#333", text_color="grey")
        else:
            self.combo_dato.configure(state="normal", fg_color="white", text_color="black")

    def crear_label_control(self, p, t):
        ctk.CTkLabel(p, text=t, text_color="#BDC3C7", font=("Arial", 12)).pack(pady=(10, 0), padx=25, anchor="w")

    def crear_combo(self, p, v):
        cb = ctk.CTkComboBox(p, values=v, width=220, fg_color="white", text_color="black")
        cb.set(v[0]); cb.pack(pady=5); return cb

    def crear_tarjeta_kpi(self, titulo, valor, color_borde):
        card = ctk.CTkFrame(self.kpi_frame, fg_color="white", corner_radius=12, border_width=2, border_color=color_borde, height=80)
        card.pack(side="left", padx=10, expand=True, fill="both")
        card.pack_propagate(False)
        ctk.CTkLabel(card, text=titulo, font=("Arial", 11, "bold"), text_color="grey").pack(pady=(10,0))
        ctk.CTkLabel(card, text=valor, font=("Arial", 26, "bold"), text_color="black").pack()

    def actualizar_kpis(self, filtro):
        for w in self.kpi_frame.winfo_children(): w.destroy()
        try:
            conn = psycopg2.connect(**self.db_config); cur = conn.cursor()
            cur.execute(f"SELECT COUNT(*), SUM(num_fallecidos), SUM(num_heridos) FROM accidentes WHERE 1=1 {filtro}")
            res = cur.fetchone()
            self.crear_tarjeta_kpi("ACCIDENTES", str(res[0] or 0), "#0B3526")
            self.crear_tarjeta_kpi("FALLECIDOS", str(res[1] or 0), "#8B0000")
            self.crear_tarjeta_kpi("HERIDOS", str(res[2] or 0), "#DAA520")
            cur.close(); conn.close()
        except: pass

    def actualizar_todo(self):
        periodo = self.combo_periodo.get()
        filtro = ""
        if periodo == "Últimos 7 días": filtro = f" AND fecha >= '{(datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')}'"
        elif periodo == "Últimos 30 días": filtro = f" AND fecha >= '{(datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')}'"
        elif periodo == "Año actual": filtro = f" AND fecha >= '{datetime.now().year}-01-01'"
        
        self.actualizar_kpis(filtro)
        self.actualizar_grafico(filtro)

    def actualizar_grafico(self, filtro):
        tipo = self.combo_tipo.get()
        variable = self.combo_dato.get()
        self.info_label.configure(text="", text_color="grey")
        
        try:
            if self.canvas: self.canvas.get_tk_widget().destroy()
            self.fig, ax = plt.subplots(figsize=(7, 5.5), dpi=100)
            conn = psycopg2.connect(**self.db_config)

            if "Franja Horaria" in tipo:
                mapeo = {"Gravedad": "g.nivel", "Causa": "cau.descripcion", "Clima": "cl.descripcion", "Carretera": "carr.nombre"}
                col_variable = mapeo[variable]
                
                filtro_adicional = ""
                if variable == "Carretera":
                    # Cambiado LIMIT 5 a LIMIT 10
                    query_top = f"SELECT {col_variable} as nombre FROM accidentes a LEFT JOIN carreteras carr ON a.carretera_id = carr.id WHERE 1=1 {filtro} GROUP BY {col_variable} ORDER BY COUNT(*) DESC LIMIT 10"
                    df_top = pd.read_sql(query_top, conn)
                    
                    if not df_top.empty:
                        nombres_top = df_top['nombre'].dropna().unique().tolist()
                        if nombres_top:
                            formato_nombres = "', '".join(nombres_top)
                            filtro_adicional = f" AND {col_variable} IN ('{formato_nombres}')"
                            self.info_label.configure(text="Mostrando Top 10 carreteras con más accidentes", text_color="#1b5e46")
                    else:
                        self.info_label.configure(text="No se encontraron carreteras en este periodo", text_color="red")

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
                    sns.barplot(data=df, x="franja", y="cantidad", hue="subcategoria", ax=ax, palette="viridis")
                    titulo = f"ANÁLISIS DE {variable.upper()} POR FRANJA"
                    if variable == "Carretera": titulo += " (TOP 10)"
                    ax.set_title(titulo, weight='bold', pad=15)
                    ax.legend(title=variable, bbox_to_anchor=(1.05, 1), loc='upper left')
                    ax.set_xlabel("")
                    ax.set_ylabel("Nº de Accidentes")
                else: 
                    self.info_label.configure(text="Sin datos suficientes para generar el gráfico", text_color="grey")

            elif "Letalidad" in tipo:
                col_db = "cau.descripcion"
                query = f"""SELECT {col_db} as etiqueta, 
                            (SUM(CASE WHEN num_fallecidos > 0 THEN 1 ELSE 0 END)::float / NULLIF(COUNT(*),0)) * 100 as letalidad
                            FROM accidentes a 
                            LEFT JOIN causas cau ON a.causa_id = cau.id 
                            WHERE 1=1 {filtro} GROUP BY {col_db} HAVING COUNT(*) > 0"""
                df = pd.read_sql(query, conn)
                if not df.empty:
                    sns.barplot(data=df, x="etiqueta", y="letalidad", ax=ax, palette="Reds_r")
                    ax.set_title("ÍNDICE DE LETALIDAD POR CAUSA", weight='bold', pad=15)
                    ax.set_xlabel("") 
                    ax.set_ylabel("Letalidad (%)")
                    plt.xticks(rotation=30, ha='right')
                else: self.info_label.configure(text="Datos insuficientes")

            elif "Mapa de Calor" in tipo:
                query = f"SELECT EXTRACT(DOW FROM fecha) as dia, EXTRACT(HOUR FROM hora) as hora_num, COUNT(*) FROM accidentes WHERE 1=1 {filtro} GROUP BY dia, hora_num"
                df = pd.read_sql(query, conn)
                if not df.empty:
                    pivot = df.pivot(index='dia', columns='hora_num', values='count').fillna(0)
                    dias_nombre = ['Dom', 'Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb']
                    sns.heatmap(pivot, annot=True, fmt=".0f", cmap="YlGn", ax=ax, cbar=False)
                    ax.set_yticklabels([dias_nombre[int(i)] for i in pivot.index if int(i) < 7], rotation=0)
                    ax.set_title("MAPA DE RIESGO: DÍA VS HORA", weight='bold', pad=15)
                    ax.set_xlabel("Hora del Día")
                    ax.set_ylabel("")

            else:
                mapeo = {"Gravedad": "g.nivel", "Causa": "cau.descripcion", "Clima": "cl.descripcion", "Carretera": "carr.nombre"}
                col = mapeo[variable]
                query = f"SELECT {col} as etiqueta, COUNT(*) as cantidad FROM accidentes a LEFT JOIN carreteras carr ON a.carretera_id = carr.id LEFT JOIN gravedad g ON a.gravedad_id = g.id LEFT JOIN clima cl ON a.clima_id = cl.id LEFT JOIN causas cau ON a.causa_id = cau.id WHERE 1=1 {filtro} GROUP BY {col}"
                df = pd.read_sql(query, conn)
                if not df.empty:
                    if "Barras" in tipo:
                        sns.barplot(data=df, x="etiqueta", y="cantidad", ax=ax, palette="Paired")
                        ax.set_title(f"ACCIDENTES POR {variable.upper()}", weight='bold', pad=15)
                        ax.set_xlabel("")
                        plt.xticks(rotation=30, ha='right')
                    else:
                        colores = sns.color_palette("viridis", n_colors=len(df))
                        ax.pie(df["cantidad"], labels=None, autopct='%1.1f%%', startangle=140, 
                               wedgeprops={'width':0.4, 'edgecolor':'w'}, colors=colores,
                               pctdistance=0.82, textprops={'fontsize': 10, 'weight': 'bold'})
                        ax.legend(df["etiqueta"], title=variable, loc="upper center", 
                                  bbox_to_anchor=(0.5, -0.05), ncol=2, frameon=False)
                        ax.set_title(f"PROPORCIÓN POR {variable.upper()}", weight='bold', pad=20)

            conn.close()
            self.fig.tight_layout()
            self.canvas = FigureCanvasTkAgg(self.fig, master=self.canvas_container)
            self.canvas.draw()
            self.canvas.get_tk_widget().pack(fill="both", expand=True, padx=15, pady=5)
        except Exception as e: 
            messagebox.showerror("Error", f"Error al generar gráfico: {str(e)}")

    def exportar_grafico(self):
        if self.fig:
            ruta = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("Imagen PNG", "*.png")])
            if ruta: self.fig.savefig(ruta, dpi=300, bbox_inches='tight'); messagebox.showinfo("Éxito", "Exportado.")
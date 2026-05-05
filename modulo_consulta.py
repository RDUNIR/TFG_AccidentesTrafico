import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import psycopg2
import csv
from datetime import datetime
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet

class ModuloConsulta:
    def __init__(self, master, db_config):
        self.master = master
        self.db_config = db_config
        self.filtros_activos = {}
        self.search_timer = None

    def mostrar(self, volver_callback):
        for widget in self.master.winfo_children():
            widget.destroy()

        # --- CABECERA ---
        header = ctk.CTkFrame(self.master, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(15, 5))
        
        ctk.CTkButton(header, text="← Volver", fg_color="#555", width=90, command=volver_callback).pack(side="left")
        ctk.CTkLabel(header, text="PANEL DE CONTROL DE ACCIDENTES", text_color="black", 
                     font=ctk.CTkFont(size=22, weight="bold")).pack(side="left", padx=20)

        # --- BARRA DE HERRAMIENTAS ---
        toolbar = ctk.CTkFrame(self.master, fg_color="#E0E0E0", corner_radius=10)
        toolbar.pack(fill="x", padx=20, pady=5)

        # Buscador Live
        ctk.CTkLabel(toolbar, text="🔍", text_color="black").pack(side="left", padx=(15, 5))
        self.ent_busqueda = ctk.CTkEntry(toolbar, placeholder_text="Buscar en observaciones...", width=200)
        self.ent_busqueda.pack(side="left", padx=5, pady=10)
        self.ent_busqueda.bind("<KeyRelease>", self.on_search_key)

        ctk.CTkButton(toolbar, text="Filtros ⚙️", fg_color="#1b5e46", width=100, command=self.ventana_filtros).pack(side="left", padx=5)
        ctk.CTkButton(toolbar, text="🔄", fg_color="#777", width=40, command=self.limpiar_todo).pack(side="left", padx=5)
        
        # Botones de Acción
        ctk.CTkButton(toolbar, text="Excel 📊", fg_color="#1f6aa5", width=90, command=self.exportar_excel).pack(side="right", padx=(5, 15))
        ctk.CTkButton(toolbar, text="PDF 📄", fg_color="#A52A2A", width=80, command=self.exportar_pdf).pack(side="right", padx=5)
        ctk.CTkButton(toolbar, text="Editar 📝", fg_color="#DAA520", width=90, command=self.editar_registro).pack(side="right", padx=5)
        ctk.CTkButton(toolbar, text="Eliminar 🗑️", fg_color="#8B0000", width=90, command=self.eliminar_registro).pack(side="right", padx=5)

        # --- TABLA ---
        t_frame = tk.Frame(self.master, bg="white")
        t_frame.pack(expand=True, fill="both", padx=20, pady=(5, 0))

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", rowheight=35, font=("Arial", 10), background="white", fieldbackground="white")
        style.map("Treeview", background=[('selected', '#347083')])

        columnas_config = [
            ("ID", 40), ("Fecha", 85), ("Hora", 55), ("Carretera", 100),
            ("Gravedad", 160), ("Fall.", 45), ("Her.", 45), ("Veh.", 45),
            ("Clima", 100), ("Causa", 150)
        ]

        self.cols = [c[0] for c in columnas_config]
        self.tree = ttk.Treeview(t_frame, columns=self.cols, show='headings')
        self.tree.bind("<Double-1>", self.ver_detalles)

        scroll_y = ttk.Scrollbar(t_frame, orient="vertical", command=self.tree.yview)
        scroll_x = ttk.Scrollbar(t_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)
        
        scroll_y.pack(side="right", fill="y")
        scroll_x.pack(side="bottom", fill="x")
        self.tree.pack(side="left", expand=True, fill="both")

        for col, ancho in columnas_config:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=ancho, anchor="center")

        # --- BARRA DE ESTADÍSTICAS ---
        self.status_bar = ctk.CTkFrame(self.master, fg_color="#222", height=30)
        self.status_bar.pack(fill="x", side="bottom", padx=20, pady=(0, 10))
        self.lbl_stats = ctk.CTkLabel(self.status_bar, text="", text_color="white", font=("Arial", 11, "bold"))
        self.lbl_stats.pack(pady=2, padx=20, side="left")

        self.cargar_datos()

    def on_search_key(self, event):
        if self.search_timer:
            self.master.after_cancel(self.search_timer)
        self.search_timer = self.master.after(300, self.cargar_datos)

    def cargar_datos(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        total_f, total_h, total_acc = 0, 0, 0
        
        try:
            conn = psycopg2.connect(**self.db_config)
            cur = conn.cursor()
            query = """
                SELECT a.id, a.fecha, a.hora, carr.nombre, g.nivel, a.num_fallecidos, 
                       a.num_heridos, a.num_vehiculos, cl.descripcion, cau.descripcion, a.observaciones
                FROM accidentes a
                LEFT JOIN carreteras carr ON a.carretera_id = carr.id
                LEFT JOIN gravedad g ON a.gravedad_id = g.id
                LEFT JOIN clima cl ON a.clima_id = cl.id
                LEFT JOIN causas cau ON a.causa_id = cau.id
                WHERE 1=1
            """
            params = []
            
            # Buscador Live
            busqueda = self.ent_busqueda.get()
            if busqueda:
                query += " AND a.observaciones ILIKE %s"
                params.append(f"%{busqueda}%")
            
            # Filtros Avanzados
            f = self.filtros_activos
            if f.get("fecha_inicio"):
                query += " AND a.fecha >= %s"; params.append(f["fecha_inicio"])
            if f.get("fecha_fin"):
                query += " AND a.fecha <= %s"; params.append(f["fecha_fin"])
            if f.get("carr") and f["carr"] != "Todas":
                query += " AND carr.nombre = %s"; params.append(f["carr"])
            if f.get("grav") and f["grav"] != "Todas":
                query += " AND g.nivel = %s"; params.append(f["grav"])
            if f.get("clima") and f["clima"] != "Todos":
                query += " AND cl.descripcion = %s"; params.append(f["clima"])
            if f.get("causa") and f["causa"] != "Todas":
                query += " AND cau.descripcion = %s"; params.append(f["causa"])
            
            # Numéricos
            if f.get("veh") and str(f["veh"]).isdigit():
                query += " AND a.num_vehiculos = %s"; params.append(int(f["veh"]))
            if f.get("fall") and str(f["fall"]).isdigit():
                query += " AND a.num_fallecidos = %s"; params.append(int(f["fall"]))
            if f.get("her") and str(f["her"]).isdigit():
                query += " AND a.num_heridos = %s"; params.append(int(f["her"]))

            query += " ORDER BY a.id DESC"
            cur.execute(query, params)
            
            for row in cur.fetchall():
                r = list(row)
                nivel = r[4] if r[4] else "N/A"
                icono = "🔴 " if "Mortal" in nivel else "🟠 " if "Grave" in nivel else "🟢 "
                r[4] = f"{icono}{nivel}"
                
                total_acc += 1
                total_f += r[5] if r[5] else 0
                total_h += r[6] if r[6] else 0
                r[1] = r[1].strftime("%d/%m/%Y") if r[1] else ""
                self.tree.insert("", "end", values=r[:10])
            
            self.lbl_stats.configure(text=f"📊 RESULTADOS: {total_acc} | 💀 Fallecidos: {total_f} | 🤕 Heridos: {total_h}")
            cur.close(); conn.close()
        except Exception as e:
            messagebox.showerror("Error SQL", str(e))

    def ventana_filtros(self):
        v = ctk.CTkToplevel(self.master)
        v.title("Configuración de Filtros")
        v.geometry("450x750")
        v.attributes('-topmost', True)
        v.grab_set()

        scroll = ctk.CTkScrollableFrame(v, width=420, height=700)
        scroll.pack(fill="both", expand=True, padx=5, pady=5)

        ctk.CTkLabel(scroll, text="Filtros de Búsqueda", font=("Arial", 18, "bold")).pack(pady=15)

        # --- SECCIÓN FECHAS ---
        ctk.CTkLabel(scroll, text="Rango de Fechas (DD/MM/AAAA):", font=("Arial", 12, "bold")).pack(pady=(10, 0))
        f_date = ctk.CTkFrame(scroll, fg_color="transparent")
        f_date.pack(pady=5)
        
        ent_f_inicio = ctk.CTkEntry(f_date, placeholder_text="Inicio", width=120)
        ent_f_inicio.insert(0, self.filtros_activos.get("f_ini_raw", ""))
        ent_f_inicio.pack(side="left", padx=5)
        
        ent_f_fin = ctk.CTkEntry(f_date, placeholder_text="Fin", width=120)
        ent_f_fin.insert(0, self.filtros_activos.get("f_fin_raw", ""))
        ent_f_fin.pack(side="left", padx=5)

        # --- SECCIÓN COMBOS ---
        try:
            conn = psycopg2.connect(**self.db_config); cur = conn.cursor()
            cur.execute("SELECT nombre FROM carreteras ORDER BY nombre"); lista_carr = ["Todas"] + [r[0] for r in cur.fetchall()]
            cur.execute("SELECT nivel FROM gravedad ORDER BY id"); lista_grav = ["Todas"] + [r[0] for r in cur.fetchall()]
            cur.execute("SELECT descripcion FROM clima ORDER BY descripcion"); lista_clima = ["Todos"] + [r[0] for r in cur.fetchall()]
            cur.execute("SELECT descripcion FROM causas ORDER BY descripcion"); lista_causa = ["Todas"] + [r[0] for r in cur.fetchall()]
            cur.close(); conn.close()
        except:
            lista_carr, lista_grav, lista_clima, lista_causa = ["Todas"], ["Todas"], ["Todos"], ["Todas"]

        def crear_filtro(label, lista, clave):
            ctk.CTkLabel(scroll, text=f"{label}:", font=("Arial", 12, "bold")).pack(pady=(10, 0))
            cb = ctk.CTkComboBox(scroll, values=lista, width=250)
            cb.set(self.filtros_activos.get(clave, lista[0]))
            cb.pack(pady=5)
            return cb

        cb_carr = crear_filtro("Carretera", lista_carr, "carr")
        cb_grav = crear_filtro("Gravedad", lista_grav, "grav")
        cb_clima = crear_filtro("Clima", lista_clima, "clima")
        cb_causa = crear_filtro("Causa principal", lista_causa, "causa")

        # --- SECCIÓN NUMÉRICA ---
        ctk.CTkLabel(scroll, text="Cantidades exactas:", font=("Arial", 14, "bold"), text_color="#1b5e46").pack(pady=(20, 5))
        def crear_entry_num(label, clave):
            f = ctk.CTkFrame(scroll, fg_color="transparent"); f.pack(fill="x", padx=50)
            ctk.CTkLabel(f, text=label, width=120, anchor="w").pack(side="left")
            ent = ctk.CTkEntry(f, width=60)
            ent.insert(0, self.filtros_activos.get(clave, ""))
            ent.pack(side="right", pady=2)
            return ent

        ent_veh = crear_entry_num("Nº Vehículos:", "veh")
        ent_fall = crear_entry_num("Nº Fallecidos:", "fall")
        ent_her = crear_entry_num("Nº Heridos:", "her")

        # --- FUNCIONES DE BOTONES ---
        def limpiar_campos():
            self.filtros_activos = {}
            ent_f_inicio.delete(0, tk.END)
            ent_f_fin.delete(0, tk.END)
            cb_carr.set("Todas")
            cb_grav.set("Todas")
            cb_clima.set("Todos")
            cb_causa.set("Todas")
            ent_veh.delete(0, tk.END)
            ent_fall.delete(0, tk.END)
            ent_her.delete(0, tk.END)
            self.cargar_datos()

        def aplicar():
            f_inicio, f_fin = None, None
            raw_ini = ent_f_inicio.get().strip()
            raw_fin = ent_f_fin.get().strip()
            
            val_veh = ent_veh.get().strip()
            val_fall = ent_fall.get().strip()
            val_her = ent_her.get().strip()

            try:
                if raw_ini:
                    f_inicio = datetime.strptime(raw_ini, "%d/%m/%Y").date()
                if raw_fin:
                    f_fin = datetime.strptime(raw_fin, "%d/%m/%Y").date()
                
                if f_inicio and f_fin and f_inicio > f_fin:
                    messagebox.showerror("Error de Rango", "La fecha de inicio no puede ser posterior a la fecha de fin.")
                    return

                for nombre, valor in [("Vehículos", val_veh), ("Fallecidos", val_fall), ("Heridos", val_her)]:
                    if valor and not valor.isdigit():
                        messagebox.showerror("Error de Dato", f"El campo '{nombre}' debe contener solo números.")
                        return

            except ValueError:
                messagebox.showerror("Error de Formato", "Formato de fecha incorrecto.\nUse el formato: DD/MM/AAAA")
                return

            self.filtros_activos = {
                "fecha_inicio": f_inicio,
                "fecha_fin": f_fin,
                "f_ini_raw": raw_ini,
                "f_fin_raw": raw_fin,
                "carr": cb_carr.get(),
                "grav": cb_grav.get(),
                "clima": cb_clima.get(),
                "causa": cb_causa.get(),
                "veh": val_veh,
                "fall": val_fall,
                "her": val_her
            }
            self.cargar_datos()
            v.destroy()

        btn_f = ctk.CTkFrame(scroll, fg_color="transparent")
        btn_f.pack(pady=30)
        ctk.CTkButton(btn_f, text="Aplicar Filtros", fg_color="#1b5e46", height=40, width=150, command=aplicar).pack(side="left", padx=5)
        ctk.CTkButton(btn_f, text="Limpiar Filtros", fg_color="#777", height=40, width=120, command=limpiar_campos).pack(side="left", padx=5)

    def editar_registro(self):
        item = self.tree.selection()
        if not item:
            messagebox.showwarning("Atención", "Seleccione un registro para editar.")
            return
        
        id_acc = self.tree.item(item)['values'][0]
        try:
            from modulo_registro import ModuloRegistro 
            conn = psycopg2.connect(**self.db_config); cur = conn.cursor()
            # Consultamos todos los campos del registro para pasarlos a la ventana de edición
            cur.execute("SELECT * FROM accidentes WHERE id = %s", (id_acc,))
            datos_accidente = cur.fetchone(); cur.close(); conn.close()
            
            if datos_accidente:
                ventana_edit = ctk.CTkToplevel(self.master)
                ventana_edit.title(f"Editando Registro #{id_acc}")
                ventana_edit.grab_set()
                # Recargamos la tabla al cerrar la ventana de edición para ver los cambios
                ventana_edit.bind("<Destroy>", lambda e: self.cargar_datos())
                
                app_registro = ModuloRegistro(ventana_edit, self.db_config)
                
                # Pasamos los datos al módulo de registro ANTES de mostrar la interfaz
                if hasattr(app_registro, 'cargar_datos_para_editar'):
                    app_registro.cargar_datos_para_editar(datos_accidente)
                
                app_registro.mostrar(volver_callback=ventana_edit.destroy)
        except Exception as e: 
            messagebox.showerror("Error", f"No se pudo cargar el editor: {e}")

    def ver_detalles(self, event):
        item = self.tree.selection()
        if not item: return
        id_acc = self.tree.item(item)['values'][0]
        try:
            conn = psycopg2.connect(**self.db_config); cur = conn.cursor()
            cur.execute("""
                SELECT a.id, a.fecha, a.hora, carr.nombre, g.nivel, cl.descripcion, cau.descripcion,
                       a.num_vehiculos, a.num_fallecidos, a.num_heridos, a.observaciones
                FROM accidentes a
                LEFT JOIN carreteras carr ON a.carretera_id = carr.id
                LEFT JOIN gravedad g ON a.gravedad_id = g.id
                LEFT JOIN clima cl ON a.clima_id = cl.id
                LEFT JOIN causas cau ON a.causa_id = cau.id
                WHERE a.id = %s
            """, (id_acc,))
            res = cur.fetchone(); cur.close(); conn.close()
            vd = ctk.CTkToplevel(self.master)
            vd.title(f"Información Completa - #{id_acc}")
            vd.geometry("550x650"); vd.attributes('-topmost', True)
            cont = ctk.CTkScrollableFrame(vd, width=500, height=600)
            cont.pack(padx=10, pady=10, fill="both", expand=True)
            def add_dato(titulo, valor):
                f = ctk.CTkFrame(cont, fg_color="transparent"); f.pack(fill="x", pady=2)
                ctk.CTkLabel(f, text=f"{titulo}:", font=("Arial", 12, "bold"), width=120, anchor="w").pack(side="left")
                ctk.CTkLabel(f, text=str(valor), font=("Arial", 12)).pack(side="left", padx=5)
            ctk.CTkLabel(cont, text="DETALLES GENERALES", font=("Arial", 16, "bold"), text_color="#1b5e46").pack(pady=10)
            add_dato("ID REGISTRO", res[0]); add_dato("FECHA", res[1].strftime("%d/%m/%Y") if res[1] else ""); add_dato("HORA", res[2])
            add_dato("CARRETERA", res[3]); add_dato("GRAVEDAD", res[4])
            ctk.CTkLabel(cont, text="CONDICIONES Y VÍCTIMAS", font=("Arial", 16, "bold"), text_color="#1b5e46").pack(pady=10)
            add_dato("CLIMA", res[5]); add_dato("CAUSA", res[6]); add_dato("VEHÍCULOS", res[7]); add_dato("FALLECIDOS", res[8]); add_dato("HERIDOS", res[9])
            ctk.CTkLabel(cont, text="OBSERVACIONES", font=("Arial", 16, "bold"), text_color="#1b5e46").pack(pady=10)
            txt = ctk.CTkTextbox(cont, width=450, height=150, font=("Arial", 11))
            txt.insert("0.0", res[10] if res[10] else "Sin observaciones.")
            txt.configure(state="disabled"); txt.pack(pady=5)
        except Exception as e: messagebox.showerror("Error", str(e))

    def eliminar_registro(self):
        item = self.tree.selection()
        if not item: return
        id_acc = self.tree.item(item)['values'][0]
        if messagebox.askyesno("Confirmar", f"¿Desea eliminar el registro #{id_acc}?"):
            try:
                conn = psycopg2.connect(**self.db_config); cur = conn.cursor()
                cur.execute("DELETE FROM accidentes WHERE id = %s", (id_acc,)); conn.commit()
                cur.close(); conn.close(); self.cargar_datos()
            except Exception as e: messagebox.showerror("Error", str(e))

    def limpiar_todo(self):
        self.filtros_activos = {}; self.ent_busqueda.delete(0, tk.END); self.cargar_datos()

    def exportar_excel(self):
        archivo = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("Excel CSV", "*.csv")])
        if not archivo: return
        try:
            cabeceras_ext = self.cols + ["Observaciones"]
            with open(archivo, mode='w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f, delimiter=';'); writer.writerow(cabeceras_ext)
                conn = psycopg2.connect(**self.db_config); cur = conn.cursor()
                for item in self.tree.get_children():
                    valores = list(self.tree.item(item)['values'])
                    id_reg = valores[0]
                    cur.execute("SELECT observaciones FROM accidentes WHERE id = %s", (id_reg,))
                    obs = cur.fetchone()
                    valores[4] = valores[4].replace("🔴 ", "").replace("🟠 ", "").replace("🟢 ", "")
                    valores.append(obs[0] if obs and obs[0] else "")
                    writer.writerow(valores)
                cur.close(); conn.close()
            messagebox.showinfo("Éxito", "Excel exportado correctamente con observaciones.")
        except Exception as e: messagebox.showerror("Error Excel", str(e))

    def exportar_pdf(self):
        archivo = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF", "*.pdf")])
        if not archivo: return
        try:
            doc = SimpleDocTemplate(archivo, pagesize=landscape(A4))
            elementos = []; estilos = getSampleStyleSheet()
            estilo_obs = estilos["BodyText"]
            estilo_obs.fontSize = 6; estilo_obs.leading = 8 
            elementos.append(Paragraph("REPORTE DETALLADO DE ACCIDENTES", estilos['Title']))
            cabeceras_pdf = self.cols + ["Observaciones"]
            data = [cabeceras_pdf]
            conn = psycopg2.connect(**self.db_config); cur = conn.cursor()
            for item in self.tree.get_children():
                fila = list(self.tree.item(item)['values'])
                fila[4] = fila[4].replace("🔴 ", "").replace("🟠 ", "").replace("🟢 ", "")
                id_reg = fila[0]
                cur.execute("SELECT observaciones FROM accidentes WHERE id = %s", (id_reg,))
                obs = cur.fetchone()
                obs_texto = obs[0] if obs and obs[0] else ""
                fila.append(Paragraph(obs_texto, estilo_obs))
                data.append(fila)
            cur.close(); conn.close()
            anchos = [30, 60, 40, 80, 80, 30, 30, 30, 70, 90, 240]
            tabla = Table(data, colWidths=anchos)
            tabla.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.darkgreen),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('FONTSIZE', (0, 0), (-1, -1), 7),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('LEFTPADDING', (0, 0), (-1, -1), 3),
                ('RIGHTPADDING', (0, 0), (-1, -1), 3),
            ]))
            elementos.append(tabla); doc.build(elementos)
            messagebox.showinfo("Éxito", "PDF exportado correctamente con observaciones.")
        except Exception as e: messagebox.showerror("Error PDF", str(e))
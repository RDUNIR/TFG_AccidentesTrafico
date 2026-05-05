import customtkinter as ctk
import psycopg2
from tkinter import messagebox
from datetime import datetime

class ModuloRegistro:
    def __init__(self, master, db_config):
        self.master = master
        self.db_config = db_config
        self.id_edicion = None # Guardará el ID si estamos editando
        self.datos_precargados = None # Temporal para guardar datos antes de mostrar()
        self.volver_actual = None # Para guardar la referencia a la navegación

    def cargar_datos_para_editar(self, datos):
        """ Recibe la tupla de la DB y la prepara para mostrarla """
        self.id_edicion = datos[0]
        self.datos_precargados = datos

    def mostrar(self, volver_callback):
        self.volver_actual = volver_callback 
        
        for widget in self.master.winfo_children():
            widget.destroy()

        self.master.configure(fg_color="#F2F2F2", border_width=1, border_color="#CCCCCC")
        
        titulo = f"EDITAR REGISTRO #{self.id_edicion}" if self.id_edicion else "NUEVO REGISTRO"
        
        ctk.CTkButton(self.master, text="← Volver", fg_color="#555", width=100, command=volver_callback).pack(anchor="nw", padx=20, pady=10)
        ctk.CTkLabel(self.master, text=titulo, text_color="black", font=ctk.CTkFont(size=30, weight="bold")).pack(pady=(5, 10))

        scroll_frame = ctk.CTkScrollableFrame(self.master, fg_color="transparent", width=500, height=550)
        scroll_frame.pack(pady=10, padx=20, fill="both", expand=True)

        # --- SECCIÓN FECHA ---
        ctk.CTkLabel(scroll_frame, text="Fecha del accidente:", text_color="black", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=(10, 0))
        frame_fecha = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        frame_fecha.pack(pady=5)

        dias = [str(i).zfill(2) for i in range(1, 32)]
        meses = [str(i).zfill(2) for i in range(1, 13)]
        anios = [str(i) for i in range(2020, 2031)]

        self.combo_dia = ctk.CTkComboBox(frame_fecha, values=dias, width=70)
        self.combo_mes = ctk.CTkComboBox(frame_fecha, values=meses, width=70)
        self.combo_anio = ctk.CTkComboBox(frame_fecha, values=anios, width=90)

        # --- SECCIÓN HORA ---
        ctk.CTkLabel(scroll_frame, text="Hora del accidente:", text_color="black", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=(10, 0))
        frame_hora = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        frame_hora.pack(pady=5)

        horas = [str(i).zfill(2) for i in range(0, 24)]
        minutos = [str(i).zfill(2) for i in range(0, 60)]

        self.combo_hora = ctk.CTkComboBox(frame_hora, values=horas, width=70)
        self.combo_minuto = ctk.CTkComboBox(frame_hora, values=minutos, width=70)

        # --- CAMPOS DESPLEGABLES (Dinámicos desde DB) ---
        self.combo_carretera = self.crear_campo(scroll_frame, "Carretera:", "SELECT nombre FROM carreteras ORDER BY nombre ASC")
        self.combo_clima = self.crear_campo(scroll_frame, "Clima:", "SELECT descripcion FROM clima")
        self.combo_causa = self.crear_campo(scroll_frame, "Causa:", "SELECT descripcion FROM causas")
        self.combo_gravedad = self.crear_campo(scroll_frame, "Gravedad:", "SELECT nivel FROM gravedad")
        
        self.entry_vehiculos = self.crear_entrada(scroll_frame, "Número de vehículos:", "1")
        self.entry_heridos = self.crear_entrada(scroll_frame, "Número de heridos:", "0")
        self.entry_fallecidos = self.crear_entrada(scroll_frame, "Número de fallecidos:", "0")

        ctk.CTkLabel(scroll_frame, text="Observaciones:", text_color="black", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=(10, 0))
        self.text_obs = ctk.CTkTextbox(scroll_frame, width=380, height=80, border_width=1)
        self.text_obs.pack(pady=5)

        # --- CARGA DE VALORES Y CONFIGURACIÓN FINAL ---
        if self.datos_precargados:
            d = self.datos_precargados
            self.combo_dia.set(d[1].strftime("%d"))
            self.combo_mes.set(d[1].strftime("%m"))
            self.combo_anio.set(d[1].strftime("%Y"))
            
            h_obj = d[2] if isinstance(d[2], datetime) else datetime.strptime(str(d[2]), "%H:%M:%S")
            self.combo_hora.set(h_obj.strftime("%H"))
            self.combo_minuto.set(h_obj.strftime("%M"))

            self.combo_carretera.set(self.obtener_texto("carreteras", "nombre", d[3]))
            self.combo_gravedad.set(self.obtener_texto("gravedad", "nivel", d[4]))
            self.combo_causa.set(self.obtener_texto("causas", "descripcion", d[5]))
            self.combo_clima.set(self.obtener_texto("clima", "descripcion", d[6]))

            self.entry_vehiculos.delete(0, 'end'); self.entry_vehiculos.insert(0, str(d[7]))
            self.entry_heridos.delete(0, 'end'); self.entry_heridos.insert(0, str(d[8]))
            self.entry_fallecidos.delete(0, 'end'); self.entry_fallecidos.insert(0, str(d[9]))
            self.text_obs.insert("1.0", d[10] if d[10] else "")
        else:
            ahora = datetime.now()
            self.combo_dia.set(ahora.strftime("%d"))
            self.combo_mes.set(ahora.strftime("%m"))
            self.combo_anio.set(ahora.strftime("%Y"))
            self.combo_hora.set(ahora.strftime("%H"))
            self.combo_minuto.set(ahora.strftime("%M"))

        self.combo_dia.pack(side="left", padx=5)
        self.combo_mes.pack(side="left", padx=5)
        self.combo_anio.pack(side="left", padx=5)
        self.combo_hora.pack(side="left", padx=5)
        ctk.CTkLabel(frame_hora, text=":", text_color="black", font=ctk.CTkFont(size=18, weight="bold")).pack(side="left")
        self.combo_minuto.pack(side="left", padx=5)

        btn_texto = "ACTUALIZAR CAMBIOS" if self.id_edicion else "GUARDAR REGISTRO"
        ctk.CTkButton(scroll_frame, text=btn_texto, fg_color="#1f6aa5", height=50, command=self.proceso_guardado).pack(pady=30)

    def obtener_texto(self, tabla, campo, id_valor):
        try:
            conn = psycopg2.connect(**self.db_config); cur = conn.cursor()
            cur.execute(f"SELECT {campo} FROM {tabla} WHERE id = %s", (id_valor,))
            res = cur.fetchone(); cur.close(); conn.close()
            return res[0] if res else ""
        except: return ""

    def crear_campo(self, parent, texto, query):
        ctk.CTkLabel(parent, text=texto, text_color="black", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=(5,0))
        valores = ["-- Seleccione un valor --"] + self.ejecutar_consulta(query)
        combo = ctk.CTkComboBox(parent, values=valores, width=380)
        combo.set("-- Seleccione un valor --")
        combo.pack(pady=5)
        return combo

    def crear_entrada(self, parent, texto, placeholder):
        ctk.CTkLabel(parent, text=texto, text_color="black", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=(5,0))
        entry = ctk.CTkEntry(parent, placeholder_text=placeholder, width=380)
        entry.pack(pady=5)
        return entry

    def ejecutar_consulta(self, sql):
        try:
            conn = psycopg2.connect(**self.db_config); cur = conn.cursor()
            cur.execute(sql)
            res = [str(f[0]) for f in cur.fetchall()]
            cur.close(); conn.close()
            return res if res else ["Sin datos"]
        except: return ["Error"]

    def obtener_id(self, tabla, campo_texto, valor_texto):
        try:
            conn = psycopg2.connect(**self.db_config); cur = conn.cursor()
            cur.execute(f"SELECT id FROM {tabla} WHERE {campo_texto} = %s", (valor_texto,))
            res = cur.fetchone(); cur.close(); conn.close()
            return res[0] if res else None
        except: return None

    def proceso_guardado(self):
        try:
            # 1. Validación de selección obligatoria
            if "-- Seleccione un valor --" in [self.combo_carretera.get(), self.combo_clima.get(), 
                                               self.combo_causa.get(), self.combo_gravedad.get()]:
                messagebox.showwarning("Campo incompleto", "Por favor, seleccione una opción en todos los desplegables.")
                return

            # Captura de valores numéricos
            n_vehiculos = int(self.entry_vehiculos.get() or 0)
            n_heridos = int(self.entry_heridos.get() or 0)
            n_fallecidos = int(self.entry_fallecidos.get() or 0)
            gravedad_texto = self.combo_gravedad.get().lower()
            observaciones = self.text_obs.get("1.0", "end").strip()

            # 2. Validaciones de Seguridad y Coherencia Lógica
            if n_vehiculos < 1:
                messagebox.showwarning("Incoherencia", "Debe haber al menos 1 vehículo involucrado.")
                return
            
            if n_heridos < 0 or n_fallecidos < 0:
                messagebox.showwarning("Valor inválido", "Las víctimas no pueden ser números negativos.")
                return

            # --- LÓGICA CORREGIDA: Relación Gravedad vs Víctimas ---
            
            # Caso Mortal: Obligatorio fallecidos > 0
            if "mortal" in gravedad_texto:
                if n_fallecidos == 0:
                    messagebox.showwarning("Incoherencia", "Si el accidente es 'Mortal', el número de fallecidos debe ser mayor a 0.")
                    return
            
            # Si hay fallecidos, la gravedad DEBE ser Mortal
            elif n_fallecidos > 0:
                messagebox.showwarning("Incoherencia", "Hay fallecidos registrados. La gravedad debe marcarse como 'Mortal'.")
                return

            # Casos que REQUIEREN heridos (Grave o Leve con heridos)
            # Excluimos explícitamente "sin heridos" para que no salte el error
            requiere_heridos = ("grave" in gravedad_texto or "con heridos" in gravedad_texto)
            if requiere_heridos and n_heridos == 0:
                messagebox.showwarning("Incoherencia", f"Ha seleccionado '{self.combo_gravedad.get()}', por lo que el número de heridos debe ser mayor a 0.")
                return

            # Caso Sólo Daños o Leve sin heridos: No pueden tener heridos ni fallecidos
            # Nota: 'Leve sin heridos' no requiere heridos, pero tampoco debería permitirlos si se llama así.
            if ("sólo daños" in gravedad_texto or "sin heridos" in gravedad_texto) and (n_heridos > 0 or n_fallecidos > 0):
                messagebox.showwarning("Incoherencia", f"La gravedad es '{self.combo_gravedad.get()}', pero hay víctimas registradas.")
                return

            # 3. Validación de fecha futura
            fecha_str = f"{self.combo_anio.get()}-{self.combo_mes.get()}-{self.combo_dia.get()}"
            hora_str = f"{self.combo_hora.get()}:{self.combo_minuto.get()}"
            if datetime.strptime(f"{fecha_str} {hora_str}", "%Y-%m-%d %H:%M") > datetime.now():
                messagebox.showwarning("Fecha inválida", "No se puede registrar un accidente con fecha u hora futura.")
                return

            # --- PROCESO DE BASE DE DATOS ---
            id_carr = self.obtener_id("carreteras", "nombre", self.combo_carretera.get())
            id_clim = self.obtener_id("clima", "descripcion", self.combo_clima.get())
            id_caus = self.obtener_id("causas", "descripcion", self.combo_causa.get())
            id_grav = self.obtener_id("gravedad", "nivel", self.combo_gravedad.get())

            conn = psycopg2.connect(**self.db_config); cur = conn.cursor()
            if self.id_edicion:
                sql = """UPDATE accidentes SET fecha=%s, hora=%s, carretera_id=%s, gravedad_id=%s, 
                         causa_id=%s, clima_id=%s, num_vehiculos=%s, num_heridos=%s, num_fallecidos=%s, 
                         observaciones=%s WHERE id=%s"""
                cur.execute(sql, (fecha_str, hora_str, id_carr, id_grav, id_caus, id_clim,
                                  n_vehiculos, n_heridos, n_fallecidos, observaciones, self.id_edicion))
            else:
                sql = """INSERT INTO accidentes (fecha, hora, carretera_id, gravedad_id, causa_id, 
                         clima_id, num_vehiculos, num_heridos, num_fallecidos, observaciones) 
                         VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
                cur.execute(sql, (fecha_str, hora_str, id_carr, id_grav, id_caus, id_clim,
                                  n_vehiculos, n_heridos, n_fallecidos, observaciones))
            
            conn.commit(); cur.close(); conn.close()
            messagebox.showinfo("Éxito", "El registro se ha guardado correctamente.")
            if self.volver_actual: self.volver_actual()

        except ValueError:
            messagebox.showerror("Error", "Los campos numéricos deben contener valores válidos.")
        except Exception as e:
            messagebox.showerror("Error", f"Error en la base de datos: {str(e)}")

    def obtener_texto(self, tabla, campo, id_valor):
        try:
            conn = psycopg2.connect(**self.db_config); cur = conn.cursor()
            cur.execute(f"SELECT {campo} FROM {tabla} WHERE id = %s", (id_valor,))
            res = cur.fetchone(); cur.close(); conn.close()
            return res[0] if res else ""
        except: return ""

    def crear_campo(self, parent, texto, query):
        ctk.CTkLabel(parent, text=texto, text_color="black", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=(5,0))
        valores = ["-- Seleccione un valor --"] + self.ejecutar_consulta(query)
        combo = ctk.CTkComboBox(parent, values=valores, width=380)
        combo.set("-- Seleccione un valor --")
        combo.pack(pady=5)
        return combo

    def crear_entrada(self, parent, texto, placeholder):
        ctk.CTkLabel(parent, text=texto, text_color="black", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=(5,0))
        entry = ctk.CTkEntry(parent, placeholder_text=placeholder, width=380)
        entry.pack(pady=5)
        return entry

    def ejecutar_consulta(self, sql):
        try:
            conn = psycopg2.connect(**self.db_config); cur = conn.cursor()
            cur.execute(sql)
            res = [str(f[0]) for f in cur.fetchall()]
            cur.close(); conn.close()
            return res if res else ["Sin datos"]
        except: return ["Error"]

    def obtener_id(self, tabla, campo_texto, valor_texto):
        try:
            conn = psycopg2.connect(**self.db_config); cur = conn.cursor()
            cur.execute(f"SELECT id FROM {tabla} WHERE {campo_texto} = %s", (valor_texto,))
            res = cur.fetchone(); cur.close(); conn.close()
            return res[0] if res else None
        except: return None
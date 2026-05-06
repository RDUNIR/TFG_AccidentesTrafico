# ============================================================
# MÓDULO DE REGISTRO - modulo_registro.py
# Gestiona el formulario de alta y edición de accidentes.
# Carga dinámicamente los desplegables desde la base de datos,
# aplica validaciones de coherencia entre gravedad y víctimas,
# y guarda o actualiza los registros en la tabla accidentes.
# ============================================================

import customtkinter as ctk    # Librería para interfaz gráfica moderna
import psycopg2                # Conector con la base de datos PostgreSQL
from tkinter import messagebox # Ventanas emergentes de avisos y errores
from datetime import datetime  # Manejo de fechas para validación y formateo

class ModuloRegistro:
    def __init__(self, master, db_config):
        """
        Constructor del módulo. Se ejecuta al instanciarlo desde main.py o modulo_consulta.py.
        Parámetros:
            master    -- Frame padre donde se renderizará la interfaz
            db_config -- Diccionario con los parámetros de conexión a PostgreSQL
        """
        self.master = master          # Referencia al contenedor padre
        self.db_config = db_config    # Credenciales de conexión a la base de datos
        self.id_edicion = None        # Almacena el ID del accidente si estamos en modo edición, None si es alta nueva
        self.datos_precargados = None # Almacena la tupla completa del accidente antes de mostrar el formulario en modo edición
        self.volver_actual = None     # Guarda la referencia al callback de navegación para poder llamarlo tras guardar

    def cargar_datos_para_editar(self, datos):
        """
        Recibe la tupla completa del accidente desde modulo_consulta.py
        y la almacena para que mostrar() precargue el formulario con esos valores.
        Se llama ANTES de mostrar() para que los datos estén disponibles al construir la interfaz.
        Parámetros:
            datos -- Tupla con todos los campos del accidente devuelta por SELECT * FROM accidentes
        """
        self.id_edicion = datos[0]    # El primer campo es siempre el ID del accidente
        self.datos_precargados = datos # Guarda la tupla completa para usarla en mostrar()

    def mostrar(self, volver_callback):
        """
        Construye y muestra el formulario de alta o edición de accidentes.
        Si self.datos_precargados tiene valor, precarga todos los campos con los datos del accidente.
        Si no, inicializa el formulario con la fecha y hora actuales.
        Parámetros:
            volver_callback -- Función que se ejecuta al pulsar Volver o tras guardar correctamente
        """
        self.volver_actual = volver_callback  # Guarda el callback para usarlo tras guardar

        # Limpia cualquier widget previo del contenedor antes de construir la interfaz
        for widget in self.master.winfo_children():
            widget.destroy()

        # Fondo gris claro con borde para delimitar visualmente el formulario
        self.master.configure(fg_color="#F2F2F2", border_width=1, border_color="#CCCCCC")
        
        # El título cambia según si estamos editando un registro existente o creando uno nuevo
        titulo = f"EDITAR REGISTRO #{self.id_edicion}" if self.id_edicion else "NUEVO REGISTRO"
        
        ctk.CTkButton(self.master, text="← Volver", fg_color="#555", width=100,
                      command=volver_callback).pack(anchor="nw", padx=20, pady=10)
        ctk.CTkLabel(self.master, text=titulo, text_color="black",
                     font=ctk.CTkFont(size=30, weight="bold")).pack(pady=(5, 10))

        # Frame con scroll para que el formulario sea accesible aunque la ventana sea pequeña
        scroll_frame = ctk.CTkScrollableFrame(self.master, fg_color="transparent", width=500, height=550)
        scroll_frame.pack(pady=10, padx=20, fill="both", expand=True)

        # --- SECCIÓN FECHA ---
        # Tres desplegables independientes para día, mes y año
        # zfill(2) garantiza formato de dos dígitos (ej: "01", "09")
        ctk.CTkLabel(scroll_frame, text="Fecha del accidente:", text_color="black",
                     font=ctk.CTkFont(size=14, weight="bold")).pack(pady=(10, 0))
        frame_fecha = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        frame_fecha.pack(pady=5)

        dias   = [str(i).zfill(2) for i in range(1, 32)]   # "01" a "31"
        meses  = [str(i).zfill(2) for i in range(1, 13)]   # "01" a "12"
        anios  = [str(i) for i in range(2020, 2031)]        # "2020" a "2030"

        self.combo_dia  = ctk.CTkComboBox(frame_fecha, values=dias,   width=70)
        self.combo_mes  = ctk.CTkComboBox(frame_fecha, values=meses,  width=70)
        self.combo_anio = ctk.CTkComboBox(frame_fecha, values=anios,  width=90)

        # --- SECCIÓN HORA ---
        # Dos desplegables para hora y minuto
        ctk.CTkLabel(scroll_frame, text="Hora del accidente:", text_color="black",
                     font=ctk.CTkFont(size=14, weight="bold")).pack(pady=(10, 0))
        frame_hora = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        frame_hora.pack(pady=5)

        horas   = [str(i).zfill(2) for i in range(0, 24)]  # "00" a "23"
        minutos = [str(i).zfill(2) for i in range(0, 60)]  # "00" a "59"

        self.combo_hora   = ctk.CTkComboBox(frame_hora, values=horas,   width=70)
        self.combo_minuto = ctk.CTkComboBox(frame_hora, values=minutos, width=70)

        # --- CAMPOS DESPLEGABLES DINÁMICOS ---
        # Cada campo consulta su tabla de referencia en la BD para cargar los valores disponibles
        # Esto garantiza que los desplegables reflejan siempre el estado actual de la base de datos
        self.combo_carretera = self.crear_campo(scroll_frame, "Carretera:", "SELECT nombre FROM carreteras ORDER BY nombre ASC")
        self.combo_clima     = self.crear_campo(scroll_frame, "Clima:",     "SELECT descripcion FROM clima")
        self.combo_causa     = self.crear_campo(scroll_frame, "Causa:",     "SELECT descripcion FROM causas")
        self.combo_gravedad  = self.crear_campo(scroll_frame, "Gravedad:",  "SELECT nivel FROM gravedad")
        
        # Campos numéricos con valor por defecto indicado como placeholder
        self.entry_vehiculos  = self.crear_entrada(scroll_frame, "Número de vehículos:",  "1")
        self.entry_heridos    = self.crear_entrada(scroll_frame, "Número de heridos:",    "0")
        self.entry_fallecidos = self.crear_entrada(scroll_frame, "Número de fallecidos:", "0")

        # Campo de texto libre para observaciones adicionales
        ctk.CTkLabel(scroll_frame, text="Observaciones:", text_color="black",
                     font=ctk.CTkFont(size=14, weight="bold")).pack(pady=(10, 0))
        self.text_obs = ctk.CTkTextbox(scroll_frame, width=380, height=80, border_width=1)
        self.text_obs.pack(pady=5)

        # --- PRECARGA DE VALORES EN MODO EDICIÓN ---
        if self.datos_precargados:
            d = self.datos_precargados
            # Extrae día, mes y año del objeto date devuelto por la BD
            self.combo_dia.set(d[1].strftime("%d"))
            self.combo_mes.set(d[1].strftime("%m"))
            self.combo_anio.set(d[1].strftime("%Y"))
            
            # La hora puede venir como objeto datetime o como string "HH:MM:SS" según el driver
            h_obj = d[2] if isinstance(d[2], datetime) else datetime.strptime(str(d[2]), "%H:%M:%S")
            self.combo_hora.set(h_obj.strftime("%H"))
            self.combo_minuto.set(h_obj.strftime("%M"))

            # Los campos de referencia están almacenados como IDs en la BD
            # obtener_texto() convierte esos IDs al texto visible del desplegable
            self.combo_carretera.set(self.obtener_texto("carreteras", "nombre",       d[3]))
            self.combo_gravedad.set(self.obtener_texto("gravedad",    "nivel",        d[4]))
            self.combo_causa.set(self.obtener_texto("causas",         "descripcion",  d[5]))
            self.combo_clima.set(self.obtener_texto("clima",          "descripcion",  d[6]))

            # Limpia el valor por defecto del entry y lo rellena con el valor del registro
            self.entry_vehiculos.delete(0, 'end');  self.entry_vehiculos.insert(0,  str(d[7]))
            self.entry_heridos.delete(0, 'end');    self.entry_heridos.insert(0,    str(d[8]))
            self.entry_fallecidos.delete(0, 'end'); self.entry_fallecidos.insert(0, str(d[9]))
            self.text_obs.insert("1.0", d[10] if d[10] else "")
        else:
            # En modo alta nueva, inicializa la fecha y hora con el momento actual
            ahora = datetime.now()
            self.combo_dia.set(ahora.strftime("%d"))
            self.combo_mes.set(ahora.strftime("%m"))
            self.combo_anio.set(ahora.strftime("%Y"))
            self.combo_hora.set(ahora.strftime("%H"))
            self.combo_minuto.set(ahora.strftime("%M"))

        # Posiciona los combos de fecha y hora dentro de sus frames horizontales
        # Nota: se hace aquí y no al crearlos porque necesitan estar creados antes de llamar a pack()
        self.combo_dia.pack(side="left", padx=5)
        self.combo_mes.pack(side="left", padx=5)
        self.combo_anio.pack(side="left", padx=5)
        self.combo_hora.pack(side="left", padx=5)
        ctk.CTkLabel(frame_hora, text=":", text_color="black",
                     font=ctk.CTkFont(size=18, weight="bold")).pack(side="left")
        self.combo_minuto.pack(side="left", padx=5)

        # El texto del botón cambia según el modo: edición o alta nueva
        btn_texto = "ACTUALIZAR CAMBIOS" if self.id_edicion else "GUARDAR REGISTRO"
        ctk.CTkButton(scroll_frame, text=btn_texto, fg_color="#1f6aa5",
                      height=50, command=self.proceso_guardado).pack(pady=30)

    def obtener_texto(self, tabla, campo, id_valor):
        """
        Consulta la tabla de referencia y devuelve el texto correspondiente a un ID.
        Se usa para convertir los IDs almacenados en accidentes al texto visible en los desplegables.
        Parámetros:
            tabla    -- Nombre de la tabla de referencia (ej: 'carreteras', 'gravedad')
            campo    -- Nombre del campo de texto a recuperar (ej: 'nombre', 'nivel')
            id_valor -- ID numérico cuyo texto se quiere obtener
        Retorna el texto encontrado o cadena vacía si no existe.
        """
        try:
            conn = psycopg2.connect(**self.db_config)
            cur = conn.cursor()
            cur.execute(f"SELECT {campo} FROM {tabla} WHERE id = %s", (id_valor,))
            res = cur.fetchone()
            cur.close(); conn.close()
            return res[0] if res else ""
        except:
            return ""

    def crear_campo(self, parent, texto, query):
        """
        Crea una etiqueta y un desplegable cargado dinámicamente desde la base de datos.
        Añade "-- Seleccione un valor --" como primera opción para forzar una selección explícita.
        Parámetros:
            parent -- Frame padre donde se añaden los elementos
            texto  -- Etiqueta descriptiva del campo
            query  -- Consulta SQL que devuelve los valores del desplegable
        Retorna el objeto CTkComboBox creado.
        """
        ctk.CTkLabel(parent, text=texto, text_color="black",
                     font=ctk.CTkFont(size=14, weight="bold")).pack(pady=(5, 0))
        # Añade la opción vacía al principio para obligar al usuario a elegir un valor real
        valores = ["-- Seleccione un valor --"] + self.ejecutar_consulta(query)
        combo = ctk.CTkComboBox(parent, values=valores, width=380)
        combo.set("-- Seleccione un valor --")
        combo.pack(pady=5)
        return combo

    def crear_entrada(self, parent, texto, placeholder):
        """
        Crea una etiqueta y un campo de texto numérico.
        Parámetros:
            parent      -- Frame padre donde se añaden los elementos
            texto       -- Etiqueta descriptiva del campo
            placeholder -- Texto de ayuda que aparece cuando el campo está vacío
        Retorna el objeto CTkEntry creado.
        """
        ctk.CTkLabel(parent, text=texto, text_color="black",
                     font=ctk.CTkFont(size=14, weight="bold")).pack(pady=(5, 0))
        entry = ctk.CTkEntry(parent, placeholder_text=placeholder, width=380)
        entry.pack(pady=5)
        return entry

    def ejecutar_consulta(self, sql):
        """
        Ejecuta una consulta SQL y devuelve los resultados como lista de strings.
        Se usa para cargar los valores de los desplegables dinámicos desde la BD.
        Parámetros:
            sql -- Consulta SQL que devuelve una columna de valores
        Retorna lista de strings con los valores, o ["Sin datos"] / ["Error"] si falla.
        """
        try:
            conn = psycopg2.connect(**self.db_config)
            cur = conn.cursor()
            cur.execute(sql)
            res = [str(f[0]) for f in cur.fetchall()]  # Convierte cada resultado a string
            cur.close(); conn.close()
            return res if res else ["Sin datos"]
        except:
            return ["Error"]

    def obtener_id(self, tabla, campo_texto, valor_texto):
        """
        Convierte el texto seleccionado en un desplegable al ID correspondiente en la BD.
        Es la operación inversa a obtener_texto(): se usa antes de guardar en la BD.
        Parámetros:
            tabla       -- Nombre de la tabla de referencia
            campo_texto -- Nombre del campo de texto donde buscar
            valor_texto -- Texto seleccionado en el desplegable
        Retorna el ID numérico encontrado o None si no existe.
        """
        try:
            conn = psycopg2.connect(**self.db_config)
            cur = conn.cursor()
            cur.execute(f"SELECT id FROM {tabla} WHERE {campo_texto} = %s", (valor_texto,))
            res = cur.fetchone()
            cur.close(); conn.close()
            return res[0] if res else None
        except:
            return None

    def proceso_guardado(self):
        """
        Valida todos los campos del formulario y guarda o actualiza el registro en la BD.
        Realiza las siguientes validaciones en orden:
          1. Todos los desplegables tienen un valor seleccionado (no la opción por defecto)
          2. El número de vehículos es al menos 1
          3. Fallecidos y heridos no son negativos
          4. Si la gravedad es 'Mortal', debe haber al menos 1 fallecido
          5. Si hay fallecidos, la gravedad debe ser 'Mortal'
          6. Si la gravedad requiere heridos (Grave o Con heridos), debe haber al menos 1
          7. Si la gravedad es 'Sólo daños' o 'Sin heridos', no puede haber víctimas
          8. La fecha y hora no pueden ser futuras
        Si todas las validaciones pasan, ejecuta INSERT o UPDATE según el modo.
        """
        try:
            # --- VALIDACIÓN 1: Todos los desplegables seleccionados ---
            if "-- Seleccione un valor --" in [self.combo_carretera.get(), self.combo_clima.get(),
                                               self.combo_causa.get(), self.combo_gravedad.get()]:
                messagebox.showwarning("Campo incompleto", "Por favor, seleccione una opción en todos los desplegables.")
                return

            # Captura los valores numéricos convirtiendo a int (or 0 evita error si el campo está vacío)
            n_vehiculos  = int(self.entry_vehiculos.get() or 0)
            n_heridos    = int(self.entry_heridos.get() or 0)
            n_fallecidos = int(self.entry_fallecidos.get() or 0)
            gravedad_texto = self.combo_gravedad.get().lower()  # En minúsculas para comparaciones sin distinción de mayúsculas
            observaciones  = self.text_obs.get("1.0", "end").strip()

            # --- VALIDACIÓN 2: Al menos 1 vehículo ---
            if n_vehiculos < 1:
                messagebox.showwarning("Incoherencia", "Debe haber al menos 1 vehículo involucrado.")
                return
            
            # --- VALIDACIÓN 3: No negativos ---
            if n_heridos < 0 or n_fallecidos < 0:
                messagebox.showwarning("Valor inválido", "Las víctimas no pueden ser números negativos.")
                return

            # --- VALIDACIONES 4 y 5: Coherencia gravedad vs fallecidos ---
            if "mortal" in gravedad_texto:
                # Si la gravedad es mortal DEBE haber al menos un fallecido
                if n_fallecidos == 0:
                    messagebox.showwarning("Incoherencia", "Si el accidente es 'Mortal', el número de fallecidos debe ser mayor a 0.")
                    return
            elif n_fallecidos > 0:
                # Si hay fallecidos la gravedad DEBE ser mortal
                messagebox.showwarning("Incoherencia", "Hay fallecidos registrados. La gravedad debe marcarse como 'Mortal'.")
                return

            # --- VALIDACIÓN 6: Gravedad grave o con heridos requiere heridos > 0 ---
            # "sin heridos" se excluye explícitamente para no disparar este error en ese caso
            requiere_heridos = ("grave" in gravedad_texto or "con heridos" in gravedad_texto)
            if requiere_heridos and n_heridos == 0:
                messagebox.showwarning("Incoherencia", f"Ha seleccionado '{self.combo_gravedad.get()}', por lo que el número de heridos debe ser mayor a 0.")
                return

            # --- VALIDACIÓN 7: Sólo daños o sin heridos no puede tener víctimas ---
            if ("sólo daños" in gravedad_texto or "sin heridos" in gravedad_texto) and (n_heridos > 0 or n_fallecidos > 0):
                messagebox.showwarning("Incoherencia", f"La gravedad es '{self.combo_gravedad.get()}', pero hay víctimas registradas.")
                return

            # --- VALIDACIÓN 8: Fecha y hora no pueden ser futuras ---
            fecha_str = f"{self.combo_anio.get()}-{self.combo_mes.get()}-{self.combo_dia.get()}"
            hora_str  = f"{self.combo_hora.get()}:{self.combo_minuto.get()}"
            if datetime.strptime(f"{fecha_str} {hora_str}", "%Y-%m-%d %H:%M") > datetime.now():
                messagebox.showwarning("Fecha inválida", "No se puede registrar un accidente con fecha u hora futura.")
                return

            # --- PROCESO DE BASE DE DATOS ---
            # Convierte los textos de los desplegables a sus IDs en las tablas de referencia
            id_carr = self.obtener_id("carreteras", "nombre",       self.combo_carretera.get())
            id_clim = self.obtener_id("clima",       "descripcion", self.combo_clima.get())
            id_caus = self.obtener_id("causas",      "descripcion", self.combo_causa.get())
            id_grav = self.obtener_id("gravedad",    "nivel",       self.combo_gravedad.get())

            conn = psycopg2.connect(**self.db_config)
            cur = conn.cursor()

            if self.id_edicion:
                # Modo edición: actualiza todos los campos del registro existente por su ID
                sql = """UPDATE accidentes SET fecha=%s, hora=%s, carretera_id=%s, gravedad_id=%s, 
                         causa_id=%s, clima_id=%s, num_vehiculos=%s, num_heridos=%s, num_fallecidos=%s, 
                         observaciones=%s WHERE id=%s"""
                cur.execute(sql, (fecha_str, hora_str, id_carr, id_grav, id_caus, id_clim,
                                  n_vehiculos, n_heridos, n_fallecidos, observaciones, self.id_edicion))
            else:
                # Modo alta nueva: inserta un nuevo registro en la tabla accidentes
                sql = """INSERT INTO accidentes (fecha, hora, carretera_id, gravedad_id, causa_id, 
                         clima_id, num_vehiculos, num_heridos, num_fallecidos, observaciones) 
                         VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
                cur.execute(sql, (fecha_str, hora_str, id_carr, id_grav, id_caus, id_clim,
                                  n_vehiculos, n_heridos, n_fallecidos, observaciones))
            
            conn.commit()  # Confirma la transacción para que los cambios sean permanentes
            cur.close(); conn.close()
            messagebox.showinfo("Éxito", "El registro se ha guardado correctamente.")
            # Vuelve a la pantalla anterior (bienvenida o módulo de consulta según desde dónde se abrió)
            if self.volver_actual:
                self.volver_actual()

        except ValueError:
            # Se lanza si el usuario escribe texto no numérico en los campos de vehículos/heridos/fallecidos
            messagebox.showerror("Error", "Los campos numéricos deben contener valores válidos.")
        except Exception as e:
            messagebox.showerror("Error", f"Error en la base de datos: {str(e)}")
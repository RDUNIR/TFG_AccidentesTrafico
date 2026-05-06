# ============================================================
# MÓDULO DE CONSULTA - modulo_consulta.py
# Permite buscar, filtrar, visualizar, editar, eliminar y
# exportar los registros de accidentes almacenados en la BD.
# ============================================================

import customtkinter as ctk # Librería para interfaz gráfica moderna
import tkinter as tk # Librería base de interfaz gráfica (para el frame de la tabla)
from tkinter import ttk, filedialog, messagebox # ttk: tabla con scroll | filedialog: diálogos de archivo | messagebox: ventanas emergentes
import psycopg2 # Conector con la base de datos PostgreSQL
import csv # Escritura de archivos CSV (exportación Excel)
from datetime import datetime # Manejo de fechas para formateo en pantalla
from reportlab.lib.pagesizes import A4, landscape # Tamaño de página PDF en horizontal
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph # Componentes del PDF
from reportlab.lib import colors # Colores para el estilo de la tabla PDF
from reportlab.lib.styles import getSampleStyleSheet  #Estilos de texto predefinidos para el PDF

class ModuloConsulta:
    def __init__(self, master, db_config):
        """
        Constructor del módulo. Se ejecuta al instanciarlo desde main.py.
        Parámetros:
            master    -- Frame padre donde se renderizará la interfaz
            db_config -- Diccionario con los parámetros de conexión a PostgreSQL
        """
        self.master = master # Referencia al contenedor padre
        self.db_config = db_config # Credenciales de conexión a la base de datos
        self.filtros_activos = {} # Diccionario vacío que almacenará los filtros avanzados aplicados
        self.search_timer = None # Temporizador para el debounce del buscador en tiempo real

    def mostrar(self, volver_callback):
        """
        Construye y muestra toda la interfaz del módulo de consulta.
        Parámetros:
            volver_callback -- Función de main.py que se ejecuta al pulsar el botón Volver
        """
        # Limpia cualquier widget previo del contenedor antes de construir la interfaz
        for widget in self.master.winfo_children():
            widget.destroy()

        # --- CABECERA ---
        # Frame transparente que contiene el botón Volver y el título del módulo
        header = ctk.CTkFrame(self.master, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(15, 5))
        
        # Botón Volver: ejecuta la función recibida como parámetro para volver a la pantalla inicial
        ctk.CTkButton(header, text="← Volver", fg_color="#555", width=90, command=volver_callback).pack(side="left")
        ctk.CTkLabel(header, text="PANEL DE CONTROL DE ACCIDENTES", text_color="black", 
                     font=ctk.CTkFont(size=22, weight="bold")).pack(side="left", padx=20)

        # --- BARRA DE HERRAMIENTAS ---
        # Panel gris claro con todos los controles de búsqueda, filtrado y exportación
        toolbar = ctk.CTkFrame(self.master, fg_color="#E0E0E0", corner_radius=10)
        toolbar.pack(fill="x", padx=20, pady=5)

        # Icono de lupa y campo de búsqueda en tiempo real sobre el campo observaciones
        ctk.CTkLabel(toolbar, text="🔍", text_color="black").pack(side="left", padx=(15, 5))
        self.ent_busqueda = ctk.CTkEntry(toolbar, placeholder_text="Buscar en observaciones...", width=200)
        self.ent_busqueda.pack(side="left", padx=5, pady=10)
        # Vincula el evento de soltar una tecla al método on_search_key para activar el debounce
        self.ent_busqueda.bind("<KeyRelease>", self.on_search_key)

        # Botón para abrir la ventana de filtros avanzados
        ctk.CTkButton(toolbar, text="Filtros ⚙️", fg_color="#1b5e46", width=100, command=self.ventana_filtros).pack(side="left", padx=5)
        # Botón para limpiar todos los filtros y el buscador y recargar todos los datos
        ctk.CTkButton(toolbar, text="🔄", fg_color="#777", width=40, command=self.limpiar_todo).pack(side="left", padx=5)
        
        # Botones de acción sobre registros, alineados a la derecha de la toolbar
        ctk.CTkButton(toolbar, text="Excel 📊", fg_color="#1f6aa5", width=90, command=self.exportar_excel).pack(side="right", padx=(5, 15))
        ctk.CTkButton(toolbar, text="PDF 📄", fg_color="#A52A2A", width=80, command=self.exportar_pdf).pack(side="right", padx=5)
        ctk.CTkButton(toolbar, text="Editar 📝", fg_color="#DAA520", width=90, command=self.editar_registro).pack(side="right", padx=5)
        ctk.CTkButton(toolbar, text="Eliminar 🗑️", fg_color="#8B0000", width=90, command=self.eliminar_registro).pack(side="right", padx=5)

        # --- TABLA DE DATOS ---
        # Se usa tk.Frame estándar (no CTk) porque ttk.Treeview no es compatible con CustomTkinter
        t_frame = tk.Frame(self.master, bg="white")
        t_frame.pack(expand=True, fill="both", padx=20, pady=(5, 0))

        # Configuración del estilo visual de la tabla Treeview
        style = ttk.Style() 
        style.theme_use("clam") # Tema base necesario para que los estilos personalizados funcionen
        style.configure("Treeview", rowheight=35, font=("Arial", 10), background="white", fieldbackground="white")
        style.map("Treeview", background=[('selected', '#347083')]) # Color azul al seleccionar una fila

        # Definición de columnas: nombre visible y ancho en píxeles
        columnas_config = [
            ("ID", 40), ("Fecha", 85), ("Hora", 55), ("Carretera", 100),
            ("Gravedad", 160), ("Fall.", 45), ("Her.", 45), ("Veh.", 45),
            ("Clima", 100), ("Causa", 150)
        ]

        # Extrae solo los nombres de columna para usarlos en el Treeview
        self.cols = [c[0] for c in columnas_config]
        # Crea la tabla Treeview con las columnas definidas, sin mostrar la columna de árbol (#0)
        self.tree = ttk.Treeview(t_frame, columns=self.cols, show='headings')
        # Vincula el doble clic sobre una fila al método ver_detalles
        self.tree.bind("<Double-1>", self.ver_detalles)

        # Barras de desplazamiento vertical y horizontal vinculadas a la tabla
        scroll_y = ttk.Scrollbar(t_frame, orient="vertical", command=self.tree.yview)
        scroll_x = ttk.Scrollbar(t_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)
        
        # Posicionamiento de scrollbars y tabla dentro del frame
        scroll_y.pack(side="right", fill="y")
        scroll_x.pack(side="bottom", fill="x")
        self.tree.pack(side="left", expand=True, fill="both")

        # Configura cada columna con su cabecera y ancho definidos en columnas_config
        for col, ancho in columnas_config:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=ancho, anchor="center")

        # --- BARRA DE ESTADÍSTICAS ---
        # Barra oscura en la parte inferior que muestra totales de la consulta actual
        self.status_bar = ctk.CTkFrame(self.master, fg_color="#222", height=30)
        self.status_bar.pack(fill="x", side="bottom", padx=20, pady=(0, 10))
        self.lbl_stats = ctk.CTkLabel(self.status_bar, text="", text_color="white", font=("Arial", 11, "bold"))
        self.lbl_stats.pack(pady=2, padx=20, side="left")

        # Carga inicial de todos los datos de la base de datos en la tabla
        self.cargar_datos()

    def on_search_key(self, event):
        """
        Implementa el patrón debounce para la búsqueda en tiempo real.
        Cada vez que el usuario pulsa una tecla, cancela el temporizador anterior
        y programa uno nuevo de 300ms. Solo cuando el usuario deja de escribir
        durante 300ms se ejecuta cargar_datos(), evitando consultas innecesarias.
        Parámetros:
            event -- Evento de teclado generado automáticamente por el bind
        """
        if self.search_timer:
            self.master.after_cancel(self.search_timer) # Cancela la consulta pendiente anterior
        # Programa una nueva consulta para ejecutarse 300ms después
        self.search_timer = self.master.after(300, self.cargar_datos)

    def cargar_datos(self):
        """
        Consulta la base de datos aplicando todos los filtros activos y el texto
        de búsqueda, y rellena la tabla Treeview con los resultados obtenidos.
        También actualiza la barra de estadísticas con los totales de la consulta.
        """
        # Limpia todas las filas actuales de la tabla antes de cargar los nuevos datos
        for item in self.tree.get_children():
            self.tree.delete(item)
        total_f, total_h, total_acc = 0, 0, 0 # Contadores para la barra de estadísticas
        
        try:
            conn = psycopg2.connect(**self.db_config)
            cur = conn.cursor()
            # Consulta base con JOIN a todas las tablas de referencia
            # WHERE 1=1 permite añadir condiciones dinámicamente con AND sin preocuparse por la sintaxis
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
            params = [] # Lista de parámetros que se pasarán a la consulta de forma segura (evita SQL injection)
            # Si hay texto en el buscador, filtra los registros cuyas observaciones contengan ese texto
            # ILIKE realiza la búsqueda sin distinguir mayúsculas/minúsculas
            # Los % alrededor del texto permiten buscar en cualquier posición del campo
            busqueda = self.ent_busqueda.get()
            if busqueda:
                query += " AND a.observaciones ILIKE %s"
                params.append(f"%{busqueda}%")
            
            # Aplica los filtros avanzados almacenados en self.filtros_activos
            # Solo se añade la condición si el filtro tiene valor y no es la opción "Todas/Todos"
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
            
            # Filtros Numéricos: se valida que el valor sea un número antes de añadirlo
            if f.get("veh") and str(f["veh"]).isdigit():
                query += " AND a.num_vehiculos = %s"; params.append(int(f["veh"]))
            if f.get("fall") and str(f["fall"]).isdigit():
                query += " AND a.num_fallecidos = %s"; params.append(int(f["fall"]))
            if f.get("her") and str(f["her"]).isdigit():
                query += " AND a.num_heridos = %s"; params.append(int(f["her"]))

            # Ordena los resultados por ID descendente (más recientes primero)
            query += " ORDER BY a.id DESC"
            cur.execute(query, params) # Ejecuta la consulta con los parámetros de forma segura
            
            for row in cur.fetchall():
                r = list(row) # Convierte la tupla en lista para poder modificarla
                nivel = r[4] if r[4] else "N/A"
                # Añade un icono de color según la gravedad del accidente para identificación visual rápida
                icono = "🔴 " if "Mortal" in nivel else "🟠 " if "Grave" in nivel else "🟢 "
                r[4] = f"{icono}{nivel}" # Reemplaza el texto de gravedad por el texto con icono
                
                # Acumula los totales para la barra de estadísticas
                total_acc += 1
                total_f += r[5] if r[5] else 0 # r[5] = num_fallecidos
                total_h += r[6] if r[6] else 0 # r[6] = num_heridos
                r[1] = r[1].strftime("%d/%m/%Y") if r[1] else ""
                self.tree.insert("", "end", values=r[:10]) # Inserta la fila en la tabla (sin la columna observaciones que es la posición 10)
            
            # Actualiza la barra de estadísticas con los totales calculados
            self.lbl_stats.configure(text=f"📊 RESULTADOS: {total_acc} | 💀 Fallecidos: {total_f} | 🤕 Heridos: {total_h}")
            cur.close(); conn.close()
        except Exception as e:
            messagebox.showerror("Error SQL", str(e))

    def ventana_filtros(self):
        """
        Abre una ventana emergente con controles para aplicar filtros avanzados
        de búsqueda: rango de fechas, carretera, gravedad, clima, causa
        y valores numéricos exactos de vehículos, fallecidos y heridos.
        Los valores seleccionados se guardan en self.filtros_activos y se aplican
        al pulsar 'Aplicar Filtros'. Incluye validación de formato de fechas y
        coherencia del rango (inicio no puede ser posterior a fin).
        """
        v = ctk.CTkToplevel(self.master)
        v.title("Configuración de Filtros")
        v.geometry("450x750")
        v.attributes('-topmost', True) # Mantiene la ventana siempre encima de la principal
        v.grab_set() # Bloquea la interacción con la ventana principal mientras está abierta

        scroll = ctk.CTkScrollableFrame(v, width=420, height=700)
        scroll.pack(fill="both", expand=True, padx=5, pady=5)

        ctk.CTkLabel(scroll, text="Filtros de Búsqueda", font=("Arial", 18, "bold")).pack(pady=15)

        # --- SECCIÓN FECHAS ---
        # Los campos de fecha aceptan el formato DD/MM/AAAA y se precargan con el valor
        # ya aplicado si el usuario abre la ventana con filtros activos
        ctk.CTkLabel(scroll, text="Rango de Fechas (DD/MM/AAAA):", font=("Arial", 12, "bold")).pack(pady=(10, 0))
        f_date = ctk.CTkFrame(scroll, fg_color="transparent")
        f_date.pack(pady=5)
        
        ent_f_inicio = ctk.CTkEntry(f_date, placeholder_text="Inicio", width=120)
        # Precarga el valor de texto que el usuario escribió antes (f_ini_raw) para no perderlo al reabrir
        ent_f_inicio.insert(0, self.filtros_activos.get("f_ini_raw", ""))
        ent_f_inicio.pack(side="left", padx=5)
        
        ent_f_fin = ctk.CTkEntry(f_date, placeholder_text="Fin", width=120)
        ent_f_fin.insert(0, self.filtros_activos.get("f_fin_raw", ""))
        ent_f_fin.pack(side="left", padx=5)

        # --- SECCIÓN COMBOS ---
        # Carga dinámicamente desde la BD los valores reales de cada desplegable
        # Si la conexión falla, usa listas con solo la opción "Todas/Todos" como fallback
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
            """
            Función auxiliar interna que crea una etiqueta y un desplegable de filtro.
            Precarga el valor que estaba seleccionado si ya había un filtro activo para esa clave.
            Parámetros:
                label -- Texto de la etiqueta que se muestra encima del desplegable
                lista -- Lista de valores para el desplegable (incluye opción "Todas/Todos")
                clave -- Clave del diccionario filtros_activos donde se guarda el valor seleccionado
            """
            ctk.CTkLabel(scroll, text=f"{label}:", font=("Arial", 12, "bold")).pack(pady=(10, 0))
            cb = ctk.CTkComboBox(scroll, values=lista, width=250)
            cb.set(self.filtros_activos.get(clave, lista[0])) # Precarga el filtro activo o el primero de la lista
            cb.pack(pady=5)
            return cb

        # Crea los cuatro desplegables de filtro usando la función auxiliar
        cb_carr = crear_filtro("Carretera", lista_carr, "carr")
        cb_grav = crear_filtro("Gravedad", lista_grav, "grav")
        cb_clima = crear_filtro("Clima", lista_clima, "clima")
        cb_causa = crear_filtro("Causa principal", lista_causa, "causa")

        # --- SECCIÓN NUMÉRICA ---
        ctk.CTkLabel(scroll, text="Cantidades exactas:", font=("Arial", 14, "bold"), text_color="#1b5e46").pack(pady=(20, 5))
        def crear_entry_num(label, clave):
            """
            Función auxiliar interna que crea una fila con etiqueta y campo numérico.
            Precarga el valor ya aplicado si había un filtro activo para esa clave.
            Parámetros:
                label -- Texto descriptivo del campo
                clave -- Clave del diccionario filtros_activos donde se guarda el valor
            """
            f = ctk.CTkFrame(scroll, fg_color="transparent"); f.pack(fill="x", padx=50)
            ctk.CTkLabel(f, text=label, width=120, anchor="w").pack(side="left")
            ent = ctk.CTkEntry(f, width=60)
            ent.insert(0, self.filtros_activos.get(clave, "")) # Precarga el valor activo si existe
            ent.pack(side="right", pady=2)
            return ent

        # Crea los tres campos numéricos de filtro exacto
        ent_veh = crear_entry_num("Nº Vehículos:", "veh")
        ent_fall = crear_entry_num("Nº Fallecidos:", "fall")
        ent_her = crear_entry_num("Nº Heridos:", "her")

        # --- FUNCIONES DE BOTONES ---
        def limpiar_campos():
            """
            Vacía todos los controles de la ventana, restablece los desplegables
            a su opción por defecto, borra los filtros activos y recarga la tabla
            sin ningún filtro aplicado.
            """
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
            self.cargar_datos() # Recarga sin filtros para mostrar todos los registros

        def aplicar():
            """
            Lee y valida todos los valores introducidos en los controles.
            Validaciones que realiza:
              - Convierte las fechas de texto DD/MM/AAAA a objetos date de Python
              - Comprueba que la fecha inicio no sea posterior a la fecha fin
              - Verifica que los campos numéricos contengan solo dígitos
            Si todo es correcto, guarda los filtros en self.filtros_activos,
            recarga la tabla con los nuevos filtros y cierra la ventana.
            """
            f_inicio, f_fin = None, None
            raw_ini = ent_f_inicio.get().strip() # Texto original de la fecha inicio para guardarlo y poder recargarlo
            raw_fin = ent_f_fin.get().strip() # Texto original de la fecha fin
            
            val_veh = ent_veh.get().strip()
            val_fall = ent_fall.get().strip()
            val_her = ent_her.get().strip()

            try:
                # Convierte el texto de fecha al formato date de Python para usarlo en la consulta SQL
                if raw_ini:
                    f_inicio = datetime.strptime(raw_ini, "%d/%m/%Y").date()
                if raw_fin:
                    f_fin = datetime.strptime(raw_fin, "%d/%m/%Y").date()
                
                # Valida que el rango de fechas sea coherente
                if f_inicio and f_fin and f_inicio > f_fin:
                    messagebox.showerror("Error de Rango", "La fecha de inicio no puede ser posterior a la fecha de fin.")
                    return

                # Valida que los campos numéricos contengan solo dígitos
                for nombre, valor in [("Vehículos", val_veh), ("Fallecidos", val_fall), ("Heridos", val_her)]:
                    if valor and not valor.isdigit():
                        messagebox.showerror("Error de Dato", f"El campo '{nombre}' debe contener solo números.")
                        return

            except ValueError:
                # Se lanza si el formato de fecha no coincide con DD/MM/AAAA
                messagebox.showerror("Error de Formato", "Formato de fecha incorrecto.\nUse el formato: DD/MM/AAAA")
                return

            # Guarda todos los filtros en el diccionario de la instancia
            # f_ini_raw y f_fin_raw guardan el texto original para precargarlo si se reabre la ventana
            self.filtros_activos = {
                "fecha_inicio": f_inicio, # Objeto date para la consulta SQL
                "fecha_fin": f_fin, # Objeto date para la consulta SQL
                "f_ini_raw": raw_ini, # Texto original para precargar el campo al reabrir
                "f_fin_raw": raw_fin, # Texto original para precargar el campo al reabrir
                "carr": cb_carr.get(),
                "grav": cb_grav.get(),
                "clima": cb_clima.get(),
                "causa": cb_causa.get(),
                "veh": val_veh,
                "fall": val_fall,
                "her": val_her
            }
            self.cargar_datos() # Recarga la tabla con los nuevos filtros aplicados
            v.destroy() #Cierra la ventana de filtros

        # Botones de acción de la ventana de filtros
        btn_f = ctk.CTkFrame(scroll, fg_color="transparent")
        btn_f.pack(pady=30)
        ctk.CTkButton(btn_f, text="Aplicar Filtros", fg_color="#1b5e46", height=40, width=150, command=aplicar).pack(side="left", padx=5)
        ctk.CTkButton(btn_f, text="Limpiar Filtros", fg_color="#777", height=40, width=120, command=limpiar_campos).pack(side="left", padx=5)

    def editar_registro(self):
        """
        Abre una ventana emergente con el formulario de registro precargado
        con los datos del accidente seleccionado en la tabla para su edición.
        Si no hay ninguna fila seleccionada, muestra un aviso al usuario.
        Al cerrar la ventana de edición, recarga la tabla para mostrar los cambios.
        """
        item = self.tree.selection() # Obtiene la fila seleccionada en la tabla (devuelve tupla vacía si no hay selección)
        if not item:
            messagebox.showwarning("Atención", "Seleccione un registro para editar.")
            return
        
        # Extrae el ID del accidente de la primera columna (posición 0) de la fila seleccionada
        id_acc = self.tree.item(item)['values'][0] 
        try:
            # Importación local para evitar dependencias circulares entre módulos
            from modulo_registro import ModuloRegistro 
            conn = psycopg2.connect(**self.db_config); cur = conn.cursor()
            # Consultamos todos los campos del registro para pasarlos a la ventana de edición
            cur.execute("SELECT * FROM accidentes WHERE id = %s", (id_acc,))
            datos_accidente = cur.fetchone(); cur.close(); conn.close()
            
            if datos_accidente:
                # Crea una ventana emergente secundaria encima de la principal para el formulario de edición
                ventana_edit = ctk.CTkToplevel(self.master)
                ventana_edit.title(f"Editando Registro #{id_acc}")
                ventana_edit.grab_set() # Bloquea la interacción con la ventana principal mientras se edita
                # Cuando el usuario cierra la ventana de edición, recarga automáticamente
                # la tabla para que los cambios guardados sean visibles de inmediato
                ventana_edit.bind("<Destroy>", lambda e: self.cargar_datos())
                
                # Instancia el módulo de registro dentro de la ventana emergente
                app_registro = ModuloRegistro(ventana_edit, self.db_config)
                
                # Comprueba que el método existe antes de llamarlo
                # y le pasa los datos del accidente para que precargue el formulario
                if hasattr(app_registro, 'cargar_datos_para_editar'):
                    app_registro.cargar_datos_para_editar(datos_accidente)
                
                # Muestra el formulario; al pulsar Volver destruye la ventana emergente
                app_registro.mostrar(volver_callback=ventana_edit.destroy)
        except Exception as e: 
            messagebox.showerror("Error", f"No se pudo cargar el editor: {e}")

    def ver_detalles(self, event):
        """
        Se activa con doble clic sobre una fila de la tabla.
        Abre una ventana emergente de solo lectura con todos los campos
        del accidente seleccionado, incluyendo las observaciones completas.
        Parámetros:
            event -- Evento de doble clic generado automáticamente por el bind
        """
        item = self.tree.selection()
        if not item: return # No hace nada si no hay fila seleccionada
        # Extrae el ID del accidente de la primera columna de la fila seleccionada
        id_acc = self.tree.item(item)['values'][0]
        try:
            conn = psycopg2.connect(**self.db_config); cur = conn.cursor() # Consulta todos los campos del accidente incluyendo observaciones completas
            # que no se muestran en la tabla principal por falta de espacio
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
            res = cur.fetchone(); cur.close(); conn.close() # Devuelve una única tupla con todos los campos del accidente
            # Crea la ventana de detalles siempre visible encima de la principal
            vd = ctk.CTkToplevel(self.master)
            vd.title(f"Información Completa - #{id_acc}")
            vd.geometry("550x650"); vd.attributes('-topmost', True) # Siempre encima para no perderse entre ventanas
            cont = ctk.CTkScrollableFrame(vd, width=500, height=600) # Frame con scroll para que el contenido sea accesible aunque sea largo
            cont.pack(padx=10, pady=10, fill="both", expand=True)

            def add_dato(titulo, valor):
                """
                Función auxiliar interna que añade una fila con título en negrita
                y valor al lado dentro del frame de detalles.
                Parámetros:
                    titulo -- Nombre del campo (ej: 'FECHA', 'GRAVEDAD')
                    valor  -- Valor a mostrar junto al título
                """
                f = ctk.CTkFrame(cont, fg_color="transparent"); f.pack(fill="x", pady=2)
                ctk.CTkLabel(f, text=f"{titulo}:", font=("Arial", 12, "bold"), width=120, anchor="w").pack(side="left")
                ctk.CTkLabel(f, text=str(valor), font=("Arial", 12)).pack(side="left", padx=5)
            # Sección de datos generales del accidente
            ctk.CTkLabel(cont, text="DETALLES GENERALES", font=("Arial", 16, "bold"), text_color="#1b5e46").pack(pady=10)
            add_dato("ID REGISTRO", res[0]); add_dato("FECHA", res[1].strftime("%d/%m/%Y") if res[1] else ""); add_dato("HORA", res[2])
            add_dato("CARRETERA", res[3]); add_dato("GRAVEDAD", res[4])
            # Sección de condiciones del accidente y recuento de víctimas
            ctk.CTkLabel(cont, text="CONDICIONES Y VÍCTIMAS", font=("Arial", 16, "bold"), text_color="#1b5e46").pack(pady=10)
            add_dato("CLIMA", res[5]); add_dato("CAUSA", res[6]); add_dato("VEHÍCULOS", res[7]); add_dato("FALLECIDOS", res[8]); add_dato("HERIDOS", res[9])
            # Sección de observaciones en cuadro de texto de solo lectura
            ctk.CTkLabel(cont, text="OBSERVACIONES", font=("Arial", 16, "bold"), text_color="#1b5e46").pack(pady=10)
            txt = ctk.CTkTextbox(cont, width=450, height=150, font=("Arial", 11))
            txt.insert("0.0", res[10] if res[10] else "Sin observaciones.")
            txt.configure(state="disabled"); txt.pack(pady=5) # Solo lectura para evitar modificaciones accidentales
        except Exception as e: messagebox.showerror("Error", str(e))

    def eliminar_registro(self):
        """
        Elimina de la base de datos el registro seleccionado en la tabla,
        previa confirmación del usuario mediante un cuadro de diálogo.
        Si no hay ninguna fila seleccionada no hace nada.
        Tras eliminar, recarga la tabla para reflejar el cambio.
        """
        item = self.tree.selection()
        if not item: return # Sale sin hacer nada si no hay fila seleccionada
        id_acc = self.tree.item(item)['values'][0]
        # Pide confirmación antes de borrar para evitar eliminaciones accidentales
        if messagebox.askyesno("Confirmar", f"¿Desea eliminar el registro #{id_acc}?"):
            try:
                conn = psycopg2.connect(**self.db_config); cur = conn.cursor()
                cur.execute("DELETE FROM accidentes WHERE id = %s", (id_acc,)); conn.commit() # Confirma la transacción para que el borrado sea permanente en la BD
                cur.close(); conn.close(); self.cargar_datos() # Recarga la tabla para reflejar la eliminación
            except Exception as e: messagebox.showerror("Error", str(e))

    def limpiar_todo(self):
        """
        Restablece el estado inicial del módulo: vacía el diccionario de filtros activos,
        borra el texto del campo de búsqueda y recarga todos los registros sin filtros.
        """
        self.filtros_activos = {}; # Vacía todos los filtros avanzados aplicados
        self.ent_busqueda.delete(0, tk.END); # Borra el texto del campo de búsqueda en tiempo real
        self.cargar_datos() # Recarga la tabla mostrando todos los registros

    def exportar_excel(self):
        """
        Exporta los registros actualmente visibles en la tabla a un archivo CSV
        compatible con Excel. Añade la columna de observaciones completas consultándola
        directamente en la BD, ya que no se muestra en la tabla por falta de espacio.
        Usa separador ; y codificación utf-8-sig para compatibilidad con Excel en español.
        Los emojis del campo gravedad se eliminan del archivo para evitar problemas de formato.
        """
        # Abre el diálogo para que el usuario elija dónde guardar el archivo
        archivo = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("Excel CSV", "*.csv")])
        if not archivo: return # Sale si el usuario cancela el diálogo
        try:
            # Añade la columna de observaciones a las cabeceras de la tabla visible
            cabeceras_ext = self.cols + ["Observaciones"]
            with open(archivo, mode='w', newline='', encoding='utf-8-sig') as f:
                # utf-8-sig añade el BOM (Byte Order Mark) necesario para que Excel
                # reconozca correctamente los caracteres especiales en español
                writer = csv.writer(f, delimiter=';'); writer.writerow(cabeceras_ext) # Escribe la fila de cabeceras
                conn = psycopg2.connect(**self.db_config); cur = conn.cursor()
                # Recorre cada fila visible en la tabla y la escribe en el CSV
                for item in self.tree.get_children():
                    valores = list(self.tree.item(item)['values'])
                    id_reg = valores[0]
                    # Consulta las observaciones del registro desde la BD para incluirlas
                    cur.execute("SELECT observaciones FROM accidentes WHERE id = %s", (id_reg,))
                    obs = cur.fetchone()
                    # Elimina los emojis de colores del campo gravedad para el archivo exportado
                    valores[4] = valores[4].replace("🔴 ", "").replace("🟠 ", "").replace("🟢 ", "")
                    # Añade las observaciones al final de la fila (cadena vacía si no hay)
                    valores.append(obs[0] if obs and obs[0] else "")
                    writer.writerow(valores)
                cur.close(); conn.close()
            messagebox.showinfo("Éxito", "Excel exportado correctamente con observaciones.")
        except Exception as e: messagebox.showerror("Error Excel", str(e))

    def exportar_pdf(self):
        """
        Exporta los registros actualmente visibles en la tabla a un archivo PDF
        en formato horizontal (landscape A4) incluyendo todas las columnas y observaciones.
        Usa la librería ReportLab para generar la tabla con cabecera verde oscura y rejilla gris.
        Los emojis del campo gravedad se eliminan para compatibilidad con el renderizador PDF.
        Las observaciones se envuelven en un objeto Paragraph para permitir saltos de línea.
        """
        # Abre el diálogo para que el usuario elija dónde guardar el archivo
        archivo = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF", "*.pdf")])
        if not archivo: return # Sale si el usuario cancela el diálogo
        try:
            doc = SimpleDocTemplate(archivo, pagesize=landscape(A4)) # Crea el documento PDF en orientación horizontal para aprovechar el ancho de página
            elementos = []; estilos = getSampleStyleSheet()
            # Estilo de texto reducido para el campo observaciones, que puede ser texto largo
            estilo_obs = estilos["BodyText"]
            estilo_obs.fontSize = 6; # Fuente pequeña para que quepa en la celda
            estilo_obs.leading = 8 # Interlineado reducido para observaciones de varias líneas
            # Título del informe en la parte superior del PDF
            elementos.append(Paragraph("REPORTE DETALLADO DE ACCIDENTES", estilos['Title']))
            # Construye la matriz de datos: primera fila son las cabeceras, resto son los registros
            cabeceras_pdf = self.cols + ["Observaciones"]
            data = [cabeceras_pdf] # Primera fila: cabeceras de columna
            conn = psycopg2.connect(**self.db_config); 
            cur = conn.cursor() # Recorre cada fila visible en la tabla y la añade a la matriz de datos del PDF
            for item in self.tree.get_children():
                fila = list(self.tree.item(item)['values'])
                # Elimina los emojis del campo gravedad para evitar problemas de renderizado en PDF
                fila[4] = fila[4].replace("🔴 ", "").replace("🟠 ", "").replace("🟢 ", "")
                id_reg = fila[0] 
                # Consulta las observaciones desde la BD y las envuelve en Paragraph
                # para que ReportLab gestione automáticamente los saltos de línea dentro de la celda
                cur.execute("SELECT observaciones FROM accidentes WHERE id = %s", (id_reg,))
                obs = cur.fetchone()
                obs_texto = obs[0] if obs and obs[0] else ""
                fila.append(Paragraph(obs_texto, estilo_obs))
                data.append(fila)
            cur.close(); conn.close()
            # Anchos de cada columna en puntos tipográficos
            # La última columna (observaciones) recibe el mayor espacio: 240 puntos
            anchos = [30, 60, 40, 80, 80, 30, 30, 30, 70, 90, 240]
            tabla = Table(data, colWidths=anchos)
            tabla.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.darkgreen), # Fondo verde oscuro en la cabecera
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke), # Texto blanco en la cabecera
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey), # Rejilla gris en todas las celdas
                ('FONTSIZE', (0, 0), (-1, -1), 7), # Tamaño de fuente reducido en todo el documento
                ('VALIGN', (0, 0), (-1, -1), 'TOP'), # Alineación vertical arriba en todas las celdas
                ('LEFTPADDING', (0, 0), (-1, -1), 3), # Margen interno izquierdo reducido
                ('RIGHTPADDING', (0, 0), (-1, -1), 3), # Margen interno derecho reducido
            ]))
            elementos.append(tabla); 
            doc.build(elementos) # Genera y escribe el archivo PDF en disco
            messagebox.showinfo("Éxito", "PDF exportado correctamente con observaciones.")
        except Exception as e: messagebox.showerror("Error PDF", str(e))
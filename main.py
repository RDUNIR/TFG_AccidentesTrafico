# ============================================================
# MÓDULO PRINCIPAL - main.py
# Punto de entrada de la aplicación. Configura la ventana
# principal, la barra lateral de navegación y gestiona la
# transición entre los distintos módulos del sistema.
# ============================================================

import customtkinter as ctk # Librería para interfaz gráfica moderna
from PIL import Image, ImageEnhance # Manejo y ajuste de imágenes (fondo y logo)
import os # Acceso a variables de entorno y rutas de archivos
import psycopg2 # Conector con la base de datos PostgreSQL
from dotenv import load_dotenv # Carga de credenciales desde el archivo .env
from tkinter import messagebox # Ventanas emergentes de avisos y errores

# Importación a continuación de los módulos funcionales del sistema
from modulo_registro import ModuloRegistro
from modulo_consulta import ModuloConsulta
from modulo_graficos import ModuloGraficos
from modulo_informes import ModuloInformes
from modulo_controles import ModuloControles

# Carga las variables del archivo .env (credenciales de base de datos)
load_dotenv()

# Configuración global del tema visual de la aplicación
ctk.set_appearance_mode("light") # Modo claro
ctk.set_default_color_theme("blue") # Tema de color base azul

class AppNavTFE(ctk.CTk):
    """
    Clase principal de la aplicación. Hereda de CTk (CustomTkinter)
    y construye la ventana principal con sidebar y área de contenido.
    """
    def __init__(self):
        super().__init__()
        self.title("Sistema de Gestión de Accidentes - Ávila (TFE-RDG)")
        
        # Dimensiones fijas de la ventana principal
        self.width = 1250
        self.height = 850
        self.geometry(f"{self.width}x{self.height}")

        # --- CONFIGURACIÓN SEGURA DESDE .ENV para cargar las variables ya que nunca se ponen en el codigo ---
        self.db_config = {
            "host": os.getenv("DB_HOST"),
            "database": os.getenv("DB_NAME"),
            "user": os.getenv("DB_USER"),
            "password": os.getenv("DB_PASSWORD"), 
            "port": os.getenv("DB_PORT")
        }

        # --- 1. CONFIGURACIÓN DE ESPACIOS ---
        self.sidebar_width = 300
        self.bg_width = self.width - self.sidebar_width

        # Carga la imagen de fondo de Ávila con brillo reducido al 85%
        # Si no existe el archivo, muestra un fondo negro como alternativa
        ruta_img = os.path.join(os.path.dirname(__file__), "fondo_avila.jpg")
        if os.path.exists(ruta_img):
            img = Image.open(ruta_img)
            enhancer = ImageEnhance.Brightness(img)
            img = enhancer.enhance(0.85) # Reduce el brillo para mejorar la legibilidad
            self.bg_img = ctk.CTkImage(img, size=(self.bg_width, self.height))
            self.bg_label = ctk.CTkLabel(self, image=self.bg_img, text="", width=self.bg_width, height=self.height)
            self.bg_label.place(x=self.sidebar_width, y=0) # Posiciona el fondo a la derecha del sidebar
        else:
            # Fondo alternativo oscuro si no se encuentra la imagen
            self.bg_label = ctk.CTkLabel(self, text="", fg_color="#1a1a1a", width=self.bg_width, height=self.height)
            self.bg_label.place(x=self.sidebar_width, y=0)

        # --- 3. SIDEBAR VERDE OSCURO ---
        self.sidebar_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="#0B3526", width=self.sidebar_width)
        self.sidebar_frame.place(x=0, y=0, relheight=1) # Ocupa toda la altura de la ventana
        self.sidebar_frame.pack_propagate(False) # Evita que el contenido modifique el tamaño del frame

        # Carga y muestra el icono de la Guardia Civil en el sidebar
        # Si no existe el archivo, simplemente no muestra ningún icono
        ruta_icono = os.path.join(os.path.dirname(__file__), "icono_guardia_civil.png")
        if os.path.exists(ruta_icono):
            img_gc = Image.open(ruta_icono)
            self.icon_gc = ctk.CTkImage(img_gc, size=(140, 110))
            self.label_icono = ctk.CTkLabel(self.sidebar_frame, image=self.icon_gc, text="")
            self.label_icono.pack(pady=(40, 10))

        # TÍTULO Institucional en el SIDEBAR
        ctk.CTkLabel(self.sidebar_frame, text="GUARDIA CIVIL ÁVILA", text_color="white",
                     font=ctk.CTkFont(size=26, weight="bold")).pack(pady=(0, 60))

        # Creación de los botones de navegación del sidebar
        # Cada botón llama a su método mostrar_* correspondiente
        self.btn_registrar = self.crear_boton_nav("📝 Registrar nuevo accidente", self.mostrar_form_registro)
        self.btn_consultar = self.crear_boton_nav("🔍 Consultar accidentes", self.mostrar_consulta)
        self.btn_graficos = self.crear_boton_nav("📊 Generar gráficos", self.mostrar_graficos)
        self.btn_informes = self.crear_boton_nav("📋 Generar informes", self.mostrar_informes)
        self.btn_dispositivos = self.crear_boton_nav("🚔 Propuestas dispositivos", self.mostrar_controles)

        # Lista de botones de navegación para gestionar el estado activo
        self.nav_buttons = [self.btn_registrar, self.btn_consultar, self.btn_graficos, self.btn_informes, self.btn_dispositivos]

        # Botón de salida anclado en la parte inferior del sidebar
        ctk.CTkButton(self.sidebar_frame, text="Salir", fg_color="black", text_color="white", command=self.destroy).pack(side="bottom", pady=50)

        # Inicializa el contenedor de contenido y muestra la pantalla de bienvenida
        self.crear_contenedor_principal()
        self.mostrar_bienvenida()

    def crear_contenedor_principal(self):
        """
        Crea el frame central donde se renderizan los módulos,
        e instancia cada módulo pasándole la configuración de BD.
        """
        self.content_frame = ctk.CTkFrame(self, corner_radius=25, fg_color="transparent")
        self.modulo_registro = ModuloRegistro(self.content_frame, self.db_config)
        self.modulo_consulta = ModuloConsulta(self.content_frame, self.db_config)
        self.modulo_graficos = ModuloGraficos(self.content_frame, self.db_config)
        self.modulo_informes = ModuloInformes(self.content_frame, self.db_config)
        self.modulo_controles = ModuloControles(self.content_frame, self.db_config)

    def crear_boton_nav(self, texto, command):
        """
        Crea y devuelve un botón de navegación estilizado para el sidebar.
        Parámetros:
            texto   -- Etiqueta visible del botón
            command -- Función a ejecutar al pulsar el botón
        """
        btn = ctk.CTkButton(self.sidebar_frame, text=texto, fg_color="transparent", text_color="white",
                            hover_color="#144d37", anchor="w", height=50, corner_radius=15,
                            font=ctk.CTkFont(size=15, weight="bold"), command=command)
        btn.pack(pady=8, padx=25, fill="x")
        return btn

    def set_active_button(self, active_button):
        """
        Resalta visualmente el botón del módulo activo en el sidebar.
        El botón activo se pone en verde oscuro, el resto en transparente.
        Parámetros:
            active_button -- Botón que debe quedar resaltado (None para ninguno)
        """
        for btn in self.nav_buttons:
            btn.configure(fg_color="#1b5e46" if btn == active_button else "transparent")

    def limpiar_pantalla(self):
        """
        Oculta el contenedor de contenido actual y destruye sus widgets hijos
        para preparar la pantalla antes de mostrar un nuevo módulo.
        Si el frame no existe, lo recrea desde cero.
        """
        try:
            if hasattr(self, 'content_frame') and self.content_frame.winfo_exists():
                self.content_frame.place_forget() # Oculta el frame sin destruirlo
                for widget in self.content_frame.winfo_children():
                    widget.destroy() # Limpia los widgets del módulo anterior
            else:
                self.crear_contenedor_principal() # Recreación de emergencia si el frame no existe
        except Exception:
            self.crear_contenedor_principal()

    def mostrar_bienvenida(self):
        """Limpia la pantalla y desactiva todos los botones del sidebar (pantalla inicial)."""
        self.limpiar_pantalla()
        self.set_active_button(None)

    def mostrar_form_registro(self):
        """Muestra el módulo de registro de accidentes en modo alta (sin datos precargados)."""
        self.limpiar_pantalla()
        self.set_active_button(self.btn_registrar)
        self.modulo_registro.id_edicion = None # Asegura que no está en modo edición
        self.modulo_registro.datos_precargados = None # Sin datos precargados (alta nueva)
        self.content_frame.place(relx=0.62, rely=0.5, anchor="center", relwidth=0.6, relheight=0.88)
        self.modulo_registro.mostrar(volver_callback=self.mostrar_bienvenida)

    def mostrar_consulta(self):
        """Muestra el módulo de consulta y filtrado de accidentes."""
        self.limpiar_pantalla()
        self.set_active_button(self.btn_consultar)
        self.content_frame.place(relx=0.63, rely=0.5, anchor="center", relwidth=0.7, relheight=0.88)
        self.modulo_consulta.mostrar(volver_callback=self.mostrar_bienvenida)

    def mostrar_graficos(self):
        """Muestra el módulo de análisis estadístico y gráficos."""
        self.limpiar_pantalla()
        self.set_active_button(self.btn_graficos)
        self.content_frame.place(relx=0.63, rely=0.5, anchor="center", relwidth=0.75, relheight=0.88)
        self.modulo_graficos.mostrar(volver_callback=self.mostrar_bienvenida)

    def mostrar_informes(self):
        """Muestra el módulo de generación de informes en PDF y Excel."""
        self.limpiar_pantalla()
        self.set_active_button(self.btn_informes)
        self.content_frame.place(relx=0.63, rely=0.5, anchor="center", relwidth=0.75, relheight=0.88)
        self.modulo_informes.mostrar(volver_callback=self.mostrar_bienvenida)

    def mostrar_controles(self):
        """Muestra el módulo de planificación operativa de dispositivos de control."""
        self.limpiar_pantalla()
        self.set_active_button(self.btn_dispositivos)
        self.content_frame.place(relx=0.63, rely=0.5, anchor="center", relwidth=0.75, relheight=0.88)
        self.modulo_controles.mostrar(volver_callback=self.mostrar_bienvenida)

# Punto de entrada del programa
# Solo se ejecuta si el archivo se lanza directamente, no si se importa como módulo
if __name__ == "__main__":
    app = AppNavTFE()
    app.mainloop() # Inicia el bucle principal de la interfaz gráfica
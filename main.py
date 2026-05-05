import customtkinter as ctk
from PIL import Image, ImageEnhance
import os
import psycopg2
from dotenv import load_dotenv
from tkinter import messagebox

# Importamos los módulos externos
from modulo_registro import ModuloRegistro
from modulo_consulta import ModuloConsulta
from modulo_graficos import ModuloGraficos
from modulo_informes import ModuloInformes
from modulo_controles import ModuloControles

# CARGAR EL ARCHIVO .ENV
load_dotenv()

ctk.set_appearance_mode("light") 
ctk.set_default_color_theme("blue")

class AppNavTFE(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Sistema de Gestión de Accidentes - Ávila (TFE)")
        
        self.width = 1250
        self.height = 850
        self.geometry(f"{self.width}x{self.height}")

        # --- CONFIGURACIÓN SEGURA DESDE .ENV ---
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

        # --- 2. FONDO AJUSTADO A LA DERECHA ---
        ruta_img = os.path.join(os.path.dirname(__file__), "fondo_avila.jpg")
        if os.path.exists(ruta_img):
            img = Image.open(ruta_img)
            enhancer = ImageEnhance.Brightness(img)
            img = enhancer.enhance(0.85)
            self.bg_img = ctk.CTkImage(img, size=(self.bg_width, self.height))
            self.bg_label = ctk.CTkLabel(self, image=self.bg_img, text="", width=self.bg_width, height=self.height)
            self.bg_label.place(x=self.sidebar_width, y=0)
        else:
            self.bg_label = ctk.CTkLabel(self, text="", fg_color="#1a1a1a", width=self.bg_width, height=self.height)
            self.bg_label.place(x=self.sidebar_width, y=0)

        # --- 3. SIDEBAR VERDE OSCURO ---
        self.sidebar_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="#0B3526", width=self.sidebar_width)
        self.sidebar_frame.place(x=0, y=0, relheight=1)
        self.sidebar_frame.pack_propagate(False)

        # ICONO
        ruta_icono = os.path.join(os.path.dirname(__file__), "icono_guardia_civil.png")
        if os.path.exists(ruta_icono):
            img_gc = Image.open(ruta_icono)
            self.icon_gc = ctk.CTkImage(img_gc, size=(140, 110))
            self.label_icono = ctk.CTkLabel(self.sidebar_frame, image=self.icon_gc, text="")
            self.label_icono.pack(pady=(40, 10))

        # TÍTULO SIDEBAR
        ctk.CTkLabel(self.sidebar_frame, text="GUARDIA CIVIL ÁVILA", text_color="white",
                     font=ctk.CTkFont(size=26, weight="bold")).pack(pady=(0, 60))

        # BOTONES DE NAVEGACIÓN
        self.btn_registrar = self.crear_boton_nav("📝 Registrar nuevo accidente", self.mostrar_form_registro)
        self.btn_consultar = self.crear_boton_nav("🔍 Consultar accidentes", self.mostrar_consulta)
        self.btn_graficos = self.crear_boton_nav("📊 Generar gráficos", self.mostrar_graficos)
        self.btn_informes = self.crear_boton_nav("📋 Generar informes", self.mostrar_informes)
        self.btn_dispositivos = self.crear_boton_nav("🚔 Propuestas dispositivos", self.mostrar_controles)

        self.nav_buttons = [self.btn_registrar, self.btn_consultar, self.btn_graficos, self.btn_informes, self.btn_dispositivos]

        ctk.CTkButton(self.sidebar_frame, text="Salir", fg_color="black", text_color="white", command=self.destroy).pack(side="bottom", pady=50)

        # --- 4. CONTENEDOR DE CONTENIDO ---
        self.crear_contenedor_principal()
        self.mostrar_bienvenida()

    def crear_contenedor_principal(self):
        self.content_frame = ctk.CTkFrame(self, corner_radius=25, fg_color="transparent")
        self.modulo_registro = ModuloRegistro(self.content_frame, self.db_config)
        self.modulo_consulta = ModuloConsulta(self.content_frame, self.db_config)
        self.modulo_graficos = ModuloGraficos(self.content_frame, self.db_config)
        self.modulo_informes = ModuloInformes(self.content_frame, self.db_config)
        self.modulo_controles = ModuloControles(self.content_frame, self.db_config)

    def crear_boton_nav(self, texto, command):
        btn = ctk.CTkButton(self.sidebar_frame, text=texto, fg_color="transparent", text_color="white",
                            hover_color="#144d37", anchor="w", height=50, corner_radius=15,
                            font=ctk.CTkFont(size=15, weight="bold"), command=command)
        btn.pack(pady=8, padx=25, fill="x")
        return btn

    def set_active_button(self, active_button):
        for btn in self.nav_buttons:
            btn.configure(fg_color="#1b5e46" if btn == active_button else "transparent")

    def limpiar_pantalla(self):
        try:
            if hasattr(self, 'content_frame') and self.content_frame.winfo_exists():
                self.content_frame.place_forget()
                for widget in self.content_frame.winfo_children():
                    widget.destroy()
            else:
                self.crear_contenedor_principal()
        except Exception:
            self.crear_contenedor_principal()

    def mostrar_bienvenida(self):
        self.limpiar_pantalla()
        self.set_active_button(None)

    def mostrar_form_registro(self):
        self.limpiar_pantalla()
        self.set_active_button(self.btn_registrar)
        self.modulo_registro.id_edicion = None
        self.modulo_registro.datos_precargados = None
        self.content_frame.place(relx=0.62, rely=0.5, anchor="center", relwidth=0.6, relheight=0.88)
        self.modulo_registro.mostrar(volver_callback=self.mostrar_bienvenida)

    def mostrar_consulta(self):
        self.limpiar_pantalla()
        self.set_active_button(self.btn_consultar)
        self.content_frame.place(relx=0.63, rely=0.5, anchor="center", relwidth=0.7, relheight=0.88)
        self.modulo_consulta.mostrar(volver_callback=self.mostrar_bienvenida)

    def mostrar_graficos(self):
        self.limpiar_pantalla()
        self.set_active_button(self.btn_graficos)
        self.content_frame.place(relx=0.63, rely=0.5, anchor="center", relwidth=0.75, relheight=0.88)
        self.modulo_graficos.mostrar(volver_callback=self.mostrar_bienvenida)

    def mostrar_informes(self):
        self.limpiar_pantalla()
        self.set_active_button(self.btn_informes)
        self.content_frame.place(relx=0.63, rely=0.5, anchor="center", relwidth=0.75, relheight=0.88)
        self.modulo_informes.mostrar(volver_callback=self.mostrar_bienvenida)

    def mostrar_controles(self):
        self.limpiar_pantalla()
        self.set_active_button(self.btn_dispositivos)
        self.content_frame.place(relx=0.63, rely=0.5, anchor="center", relwidth=0.75, relheight=0.88)
        self.modulo_controles.mostrar(volver_callback=self.mostrar_bienvenida)

if __name__ == "__main__":
    app = AppNavTFE()
    app.mainloop()
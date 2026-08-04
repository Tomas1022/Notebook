###dibujo.py
import tkinter as tk
from tkinter import colorchooser


class DibujoFrame(tk.Frame):
    def __init__(self, parent, theme_manager):
        super().__init__(parent)
        self.theme_manager = theme_manager

        self.color_actual = "black"
        self.color_es_por_defecto = True  # True mientras el usuario no elija un color manualmente
        self.grosor_actual = 3
        self.ultimo_x = None
        self.ultimo_y = None

        self.barra = tk.Frame(self)
        self.barra.pack(fill="x", padx=14, pady=14)

        self.btn_color = tk.Button(self.barra, text="Color", relief="flat", bd=0,
                                    cursor="hand2", command=self.elegir_color)
        self.btn_color.pack(side="left", padx=5)

        self.btn_borrar = tk.Button(self.barra, text="Borrar todo", relief="flat", bd=0,
                                     cursor="hand2", command=self.borrar_todo)
        self.btn_borrar.pack(side="left", padx=5)

        self.label_grosor = tk.Label(self.barra, text="Grosor:")
        self.label_grosor.pack(side="left", padx=(15, 5))
        self.slider_grosor = tk.Scale(
            self.barra, from_=1, to=20, orient="horizontal",
            command=self.cambiar_grosor, length=120, bd=0, highlightthickness=0
        )
        self.slider_grosor.set(self.grosor_actual)
        self.slider_grosor.pack(side="left")

        self.muestra_color = tk.Label(self.barra, text="  ", bg=self.color_actual,
                                       relief="flat", width=3)
        self.muestra_color.pack(side="left", padx=15)

        self.canvas = tk.Canvas(self, cursor="cross", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True, padx=14, pady=(0, 14))

        self.canvas.bind("<Button-1>", self.iniciar_trazo)
        self.canvas.bind("<B1-Motion>", self.dibujar)
        self.canvas.bind("<ButtonRelease-1>", self.terminar_trazo)

        theme_manager.registrar(self._aplicar_tema)

    def _aplicar_tema(self, paleta):
        p = paleta
        self.configure(bg=p["bg"])
        self.barra.configure(bg=p["bg"])
        self.label_grosor.configure(bg=p["bg"], fg=p["fg"])
        self.slider_grosor.configure(bg=p["bg"], fg=p["fg"], troughcolor=p["borde"],
                                      activebackground=p["accent"])

        for btn in (self.btn_color, self.btn_borrar):
            btn.configure(bg=p["bg_secundario"], fg=p["fg"], activebackground=p["accent_suave"])

        # Canvas de dibujo: fondo claro en tema claro, "pizarra" oscura en tema oscuro
        self.canvas.configure(bg=p["bg_secundario"])

        # Si el usuario no eligio un color manualmente, el color por defecto
        # se ajusta para que siempre se vea bien sobre el nuevo fondo
        if self.color_es_por_defecto:
            self.color_actual = "#ffffff" if self.theme_manager.modo == "dark" else "#000000"
            self.muestra_color.configure(bg=self.color_actual)

    def elegir_color(self):
        color = colorchooser.askcolor(title="Elige un color")[1]
        if color:
            self.color_actual = color
            self.color_es_por_defecto = False
            self.muestra_color.config(bg=color)

    def cambiar_grosor(self, valor):
        self.grosor_actual = int(valor)

    def iniciar_trazo(self, event):
        self.ultimo_x, self.ultimo_y = event.x, event.y

    def dibujar(self, event):
        if self.ultimo_x is not None:
            self.canvas.create_line(
                self.ultimo_x, self.ultimo_y, event.x, event.y,
                fill=self.color_actual, width=self.grosor_actual,
                capstyle="round", smooth=True
            )
        self.ultimo_x, self.ultimo_y = event.x, event.y

    def terminar_trazo(self, event):
        self.ultimo_x, self.ultimo_y = None, None

    def borrar_todo(self):
        self.canvas.delete("all")

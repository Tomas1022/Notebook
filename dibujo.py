import tkinter as tk
from tkinter import colorchooser


class DibujoFrame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        self.color_actual = "black"
        self.grosor_actual = 3
        self.ultimo_x = None
        self.ultimo_y = None

        # --- Barra de herramientas ---
        barra = tk.Frame(self)
        barra.pack(fill="x", padx=10, pady=10)

        tk.Button(barra, text="🎨 Color", command=self.elegir_color).pack(side="left", padx=5)
        tk.Button(barra, text="🗑️ Borrar todo", command=self.borrar_todo).pack(side="left", padx=5)

        tk.Label(barra, text="Grosor:").pack(side="left", padx=(15, 5))
        self.slider_grosor = tk.Scale(
            barra, from_=1, to=20, orient="horizontal",
            command=self.cambiar_grosor, length=120
        )
        self.slider_grosor.set(self.grosor_actual)
        self.slider_grosor.pack(side="left")

        self.muestra_color = tk.Label(barra, text="  ", bg=self.color_actual, relief="sunken", width=3)
        self.muestra_color.pack(side="left", padx=15)

        # --- Zona de dibujo (Canvas) ---
        self.canvas = tk.Canvas(self, bg="white", cursor="cross")
        self.canvas.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # Eventos del mouse: presionar, arrastrar, soltar
        self.canvas.bind("<Button-1>", self.iniciar_trazo)
        self.canvas.bind("<B1-Motion>", self.dibujar)
        self.canvas.bind("<ButtonRelease-1>", self.terminar_trazo)

    def elegir_color(self):
        color = colorchooser.askcolor(title="Elige un color")[1]  # [1] = código hex
        if color:
            self.color_actual = color
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
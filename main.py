import tkinter as tk
from tkinter import ttk

from calculator.calculadora import CalculadoraFrame
from dibujo import DibujoFrame
from notas import NotasFrame

class App(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Notebook - Notas, Calculadora y Dibujo")
        self.geometry("800x600")
        self.minsize(600, 450)

        # Notebook = contenedor de pestañas
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True)

        # Cada pestaña es un Frame independiente (su propio archivo/módulo)
        self.notas_tab = NotasFrame(self.notebook)
        self.calculadora_tab = CalculadoraFrame(self.notebook)
        self.dibujo_tab = DibujoFrame(self.notebook)

        self.notebook.add(self.notas_tab, text="📝 Notas")
        self.notebook.add(self.calculadora_tab, text="🧮 Calculadora")
        self.notebook.add(self.dibujo_tab, text="🎨 Dibujo")


if __name__ == "__main__":
    app = App()
    app.mainloop()
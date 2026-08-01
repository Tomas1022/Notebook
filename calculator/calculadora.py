import tkinter as tk
from tkinter import ttk

from calculator.matrices import MatricesFrame
from calculator.conjuntos import ConjuntosFrame


class BasicaFrame(tk.Frame):
    """Calculadora simple de escritorio (suma, resta, multiplicación, división)."""

    def __init__(self, parent):
        super().__init__(parent)
        self.expresion = ""

        self.display = tk.Entry(self, font=("Arial", 20), justify="right", bd=5, relief="ridge")
        self.display.pack(fill="x", padx=10, pady=10, ipady=10)

        botones_frame = tk.Frame(self)
        botones_frame.pack(padx=10, pady=10)

        botones = [
            ("7", "8", "9", "/"),
            ("4", "5", "6", "*"),
            ("1", "2", "3", "-"),
            ("C", "0", "=", "+"),
        ]

        for fila_idx, fila in enumerate(botones):
            for col_idx, texto in enumerate(fila):
                btn = tk.Button(
                    botones_frame, text=texto, width=6, height=2, font=("Arial", 14),
                    command=lambda t=texto: self.click_boton(t)
                )
                btn.grid(row=fila_idx, column=col_idx, padx=3, pady=3)

    def click_boton(self, texto):
        if texto == "C":
            self.expresion = ""
        elif texto == "=":
            try:
                caracteres_validos = set("0123456789+-*/. ")
                if all(c in caracteres_validos for c in self.expresion):
                    resultado = eval(self.expresion, {"__builtins__": None}, {})
                    self.expresion = str(resultado)
                else:
                    self.expresion = "Error"
            except (ZeroDivisionError, SyntaxError):
                self.expresion = "Error"
        else:
            self.expresion += texto

        self.display.delete(0, "end")
        self.display.insert(0, self.expresion)


class CalculadoraFrame(tk.Frame):
    """Contenedor con sub-pestañas: Básica, Matrices, Conjuntos."""

    def __init__(self, parent):
        super().__init__(parent)

        sub_notebook = ttk.Notebook(self)
        sub_notebook.pack(fill="both", expand=True)

        sub_notebook.add(BasicaFrame(sub_notebook), text="Básica")
        sub_notebook.add(MatricesFrame(sub_notebook), text="Matrices")
        sub_notebook.add(ConjuntosFrame(sub_notebook), text="Conjuntos")
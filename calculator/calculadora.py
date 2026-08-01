##calculadora.py

import tkinter as tk
from tkinter import ttk

from calculator.conjuntos import ConjuntosFrame
from calculator.matrices import MatricesFrame


class BasicaFrame(tk.Frame):
    """Calculadora simple de escritorio (suma, resta, multiplicacion, division)."""

    def __init__(self, parent, theme_manager):
        super().__init__(parent)
        self.theme_manager = theme_manager
        self.expresion = ""

        self.display = tk.Entry(self, font=("Arial", 20), justify="right", bd=0, relief="flat")
        self.display.pack(fill="x", padx=14, pady=14, ipady=12)

        self.botones_frame = tk.Frame(self)
        self.botones_frame.pack(padx=14, pady=10)

        botones = [
            ("7", "8", "9", "/"),
            ("4", "5", "6", "*"),
            ("1", "2", "3", "-"),
            ("C", "0", "=", "+"),
        ]

        self.botones = []
        for fila_idx, fila in enumerate(botones):
            for col_idx, texto in enumerate(fila):
                btn = tk.Button(
                    self.botones_frame, text=texto, width=6, height=2, font=("Arial", 14),
                    relief="flat", bd=0, cursor="hand2",
                    command=lambda t=texto: self.click_boton(t)
                )
                btn.grid(row=fila_idx, column=col_idx, padx=3, pady=3)
                self.botones.append((btn, texto))

        theme_manager.registrar(self._aplicar_tema)

    def _aplicar_tema(self, paleta):
        p = paleta
        self.configure(bg=p["bg"])
        self.botones_frame.configure(bg=p["bg"])
        self.display.configure(bg=p["bg_secundario"], fg=p["fg"], insertbackground=p["fg"],
                                highlightthickness=1, highlightbackground=p["borde"],
                                highlightcolor=p["accent"])

        for btn, texto in self.botones:
            if texto == "=":
                btn.configure(bg=p["accent"], fg="#ffffff", activebackground=p["accent_hover"])
            elif texto in ("/", "*", "-", "+", "C"):
                btn.configure(bg=p["bg_secundario"], fg=p["accent"], activebackground=p["accent_suave"])
            else:
                btn.configure(bg=p["bg_secundario"], fg=p["fg"], activebackground=p["accent_suave"])

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
    """Contenedor con sub-pestañas: Basica, Matrices, Conjuntos."""

    def __init__(self, parent, theme_manager):
        super().__init__(parent)
        self.theme_manager = theme_manager

        sub_notebook = ttk.Notebook(self)
        sub_notebook.pack(fill="both", expand=True)

        sub_notebook.add(BasicaFrame(sub_notebook, theme_manager), text=" Básica")
        sub_notebook.add(MatricesFrame(sub_notebook, theme_manager), text=" Matrices")
        sub_notebook.add(ConjuntosFrame(sub_notebook, theme_manager), text=" Conjuntos")

        theme_manager.registrar(self._aplicar_tema)

    def _aplicar_tema(self, paleta):
        self.configure(bg=paleta["bg"])

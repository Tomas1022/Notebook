import ctypes
import sys
import tkinter as tk
from typing import ClassVar

from calculator.calculadora import CalculadoraFrame
from dibujo import DibujoFrame
from notas import NotasFrame
from theme import ThemeManager, ThemeSwitch


if sys.platform == "win32":
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        try:
            ctypes.windll.user32.SetProcessDPIAware()
        except Exception:
            pass


class App(tk.Tk):

    TABS: ClassVar[tuple[tuple[str, str], ...]] = (
        ("notas", "▤  Notas"),
        ("calculadora", "▦  Calculadora"),
        ("dibujo", "✎  Dibujo"),
    )

    def __init__(self):
        super().__init__()

        self._ajustar_escala_tk()

        self.title("Notebook - Notas, Calculadora y Dibujo")
        self.geometry("900x650")
        self.minsize(650, 480)

        self.theme_manager = ThemeManager()
        self.tab_actual = 0

        self.barra_superior = tk.Frame(self)
        self.barra_superior.pack(fill="x", side="top")

        self.label_titulo = tk.Label(
            self.barra_superior,
            text="Notebook",
            font=("Arial", 12, "bold")
        )
        self.label_titulo.pack(
            side="left",
            padx=16,
            pady=8
        )

        self.switch_tema = ThemeSwitch(
            self.barra_superior,
            self.theme_manager
        )
        self.switch_tema.pack(
            side="right",
            padx=14,
            pady=8
        )

        self.barra_tabs = tk.Frame(self)
        self.barra_tabs.pack(
            fill="x",
            side="top"
        )

        self.botones_tabs = {}
        self.indicadores_tabs = {}

        self.contenedor = tk.Frame(self)
        self.contenedor.pack(
            fill="both",
            expand=True
        )

        self.notas_tab = NotasFrame(
            self.contenedor,
            self.theme_manager
        )

        self.calculadora_tab = CalculadoraFrame(
            self.contenedor,
            self.theme_manager
        )

        self.dibujo_tab = DibujoFrame(
            self.contenedor,
            self.theme_manager
        )

        self.contenidos = (
            self.notas_tab,
            self.calculadora_tab,
            self.dibujo_tab
        )

        self._crear_tabs()

        self.theme_manager.registrar(
            self._aplicar_tema
        )

        self._seleccionar_tab(0)

    def _ajustar_escala_tk(self):
        try:
            dpi = self.winfo_fpixels("1i")
            self.tk.call(
                "tk",
                "scaling",
                dpi / 72.0
            )
        except Exception:
            pass

    def _crear_tabs(self):
        for indice, (tipo, texto) in enumerate(self.TABS):

            contenedor = tk.Frame(
                self.barra_tabs
            )

            contenedor.pack(
                side="left",
                padx=(8 if indice == 0 else 0, 0)
            )

            boton = tk.Button(
                contenedor,
                text=texto,
                font=("Arial", 10),
                relief="flat",
                bd=0,
                highlightthickness=0,
                cursor="hand2",
                padx=14,
                pady=10,
                command=lambda i=indice:
                    self._seleccionar_tab(i)
            )

            boton.pack()

            indicador = tk.Frame(
                contenedor,
                height=2
            )

            indicador.pack(
                fill="x",
                side="bottom"
            )

            self.botones_tabs[tipo] = boton
            self.indicadores_tabs[tipo] = indicador

    def _seleccionar_tab(self, indice):
        if indice < 0 or indice >= len(self.contenidos):
            return

        self.tab_actual = indice

        for contenido in self.contenidos:
            contenido.pack_forget()

        self.contenidos[indice].pack(
            fill="both",
            expand=True
        )

        p = self.theme_manager.paleta

        for i, (tipo, _) in enumerate(self.TABS):

            boton = self.botones_tabs[tipo]
            indicador = self.indicadores_tabs[tipo]

            if i == indice:
                boton.configure(
                    bg=p["bg"],
                    fg=p["accent"],
                    activebackground=p["bg"],
                    activeforeground=p["accent"]
                )

                indicador.configure(
                    bg=p["accent"]
                )
            else:
                boton.configure(
                    bg=p["bg"],
                    fg=p["fg_suave"],
                    activebackground=p["bg"],
                    activeforeground=p["fg"]
                )

                indicador.configure(
                    bg=p["bg"]
                )

    def _aplicar_tema(self, paleta):
        self.configure(
            bg=paleta["bg"]
        )

        self.barra_superior.configure(
            bg=paleta["bg"]
        )

        self.label_titulo.configure(
            bg=paleta["bg"],
            fg=paleta["fg"]
        )

        self.barra_tabs.configure(
            bg=paleta["bg"]
        )

        self.contenedor.configure(
            bg=paleta["bg"]
        )

        self.switch_tema.configure(
            bg=paleta["bg"]
        )

        self.switch_tema._bg_padre = paleta["bg"]

        self._seleccionar_tab(
            self.tab_actual
        )


if __name__ == "__main__":
    app = App()
    app.mainloop()
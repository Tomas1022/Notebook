##main.py
import ctypes
import sys
import tkinter as tk
from tkinter import ttk

from calculator.calculadora import CalculadoraFrame
from dibujo import DibujoFrame
from notas import NotasFrame
from theme import ThemeManager, ThemeSwitch, crear_icono_tab, mezclar_color

# --- Fix de nitidez en pantallas con escalado (Windows) ---
# Sin esto, Windows "estira" la ventana como si fuera una imagen de baja
# resolucion en monitores con escalado >100%, y todo se ve borroso/pixelado.
if sys.platform == "win32":
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        try:
            ctypes.windll.user32.SetProcessDPIAware()
        except Exception:
            pass


class App(tk.Tk):
    TABS = [
        ("notas", "Notas"),
        ("calculadora", "Calculadora"),
        ("dibujo", "Dibujo"),
    ]

    def __init__(self):
        super().__init__()

        self._ajustar_escala_tk()

        self.title("Notebook - Notas, Calculadora y Dibujo")
        self.geometry("900x650")
        self.minsize(650, 480)

        self.theme_manager = ThemeManager()

        # --- Barra superior: titulo + switch de tema ---
        self.barra_superior = tk.Frame(self, height=44)
        self.barra_superior.pack(fill="x", side="top")

        self.label_titulo = tk.Label(self.barra_superior, text="  Notebook", font=("Arial", 12, "bold"))
        self.label_titulo.pack(side="left", pady=8)

        self.switch_tema = ThemeSwitch(self.barra_superior, self.theme_manager)
        self.switch_tema.pack(side="right", padx=14, pady=8)

        # --- Notebook = contenedor de pestañas ---
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True)

        self.notas_tab = NotasFrame(self.notebook, self.theme_manager)
        self.calculadora_tab = CalculadoraFrame(self.notebook, self.theme_manager)
        self.dibujo_tab = DibujoFrame(self.notebook, self.theme_manager)

        self.notebook.add(self.notas_tab, text=" Notas")
        self.notebook.add(self.calculadora_tab, text=" Calculadora")
        self.notebook.add(self.dibujo_tab, text=" Dibujo")

        self.iconos_normal = {}
        self.iconos_seleccion = {}

        self.notebook.bind("<<NotebookTabChanged>>", self._al_cambiar_tab)
        self.theme_manager.registrar(self._aplicar_tema)

    def _ajustar_escala_tk(self):
        """Sincroniza el escalado interno de Tk con el DPI real del sistema."""
        try:
            dpi = self.winfo_fpixels("1i")
            self.tk.call("tk", "scaling", dpi / 72.0)
        except Exception:
            pass

    def _al_cambiar_tab(self, _event=None):
        seleccionado = self.notebook.index(self.notebook.select())
        p = self.theme_manager.paleta
        self._animar_seleccion_tab(seleccionado, p["fg_suave"], p["accent"])

    def _animar_seleccion_tab(self, seleccionado, color_inicio, color_fin, paso=0, pasos_totales=8):
        t = (paso + 1) / pasos_totales
        color_actual = mezclar_color(color_inicio, color_fin, t)

        for i, (tipo, _texto) in enumerate(self.TABS):
            if i == seleccionado:
                icono = crear_icono_tab(tipo, color_actual)
                self.iconos_seleccion[tipo] = icono  # mantener referencia viva
            else:
                icono = self.iconos_normal[tipo]
            self.notebook.tab(i, image=icono, compound="left")

        if paso < pasos_totales - 1:
            self.after(12, lambda: self._animar_seleccion_tab(
                seleccionado, color_inicio, color_fin, paso + 1, pasos_totales
            ))

    def _aplicar_tema(self, paleta):
        self.configure(bg=paleta["bg"])
        self.barra_superior.configure(bg=paleta["bg"])
        self.label_titulo.configure(bg=paleta["bg"], fg=paleta["fg"])
        self.switch_tema.configure(bg=paleta["bg"])
        self.switch_tema._bg_padre = paleta["bg"]

        for tipo, _texto in self.TABS:
            self.iconos_normal[tipo] = crear_icono_tab(tipo, paleta["fg_suave"])

        self._al_cambiar_tab()


if __name__ == "__main__":
    app = App()
    app.mainloop()

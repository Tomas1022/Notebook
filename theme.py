##theme.py

"""
Modulo central de temas para toda la app.

Patron usado: "observador" (observer pattern).
- ThemeManager guarda el modo actual (light/dark) y la paleta de colores.
- Cualquier parte de la app puede "suscribirse" con theme_manager.registrar(callback).
- Cuando el tema cambia, se llama automaticamente a todos los callbacks
  suscritos, pasandoles la nueva paleta para que se repinten.
"""
import tkinter as tk
from tkinter import ttk

PALETAS = {
    "light": {
        "bg": "#f5f7fa",           # fondo general
        "bg_secundario": "#ffffff",  # tarjetas, paneles de texto
        "fg": "#1f2937",           # texto principal
        "fg_suave": "#6b7280",     # texto secundario
        "accent": "#2f6fed",       # azul: color de acento en modo claro
        "accent_hover": "#255bc4",
        "accent_suave": "#dbe7ff",
        "borde": "#d0d5dd",
        "exito": "#1f9d55",
    },
    "dark": {
        "bg": "#202124",
        "bg_secundario": "#2b2d30",
        "fg": "#e8e6e3",
        "fg_suave": "#a0a0a0",
        "accent": "#ff8a3d",       # naranja: color de acento en modo oscuro
        "accent_hover": "#e6752b",
        "accent_suave": "#4a3a2c",
        "borde": "#3d3f43",
        "exito": "#4caf75",
    },
}


class ThemeManager:
    def __init__(self):
        self.modo = "light"
        self._listeners = []
        self._style = ttk.Style()
        try:
            self._style.theme_use("clam")  # base que permite personalizar mejor los colores
        except tk.TclError:
            pass
        self._configurar_estilos_ttk()

    @property
    def paleta(self):
        return PALETAS[self.modo]

    def registrar(self, callback):
        """Suscribe un callback(paleta) que se llama ahora mismo y cada vez que cambie el tema."""
        self._listeners.append(callback)
        callback(self.paleta)

    def alternar(self):
        self.modo = "dark" if self.modo == "light" else "light"
        self._configurar_estilos_ttk()
        for callback in self._listeners:
            callback(self.paleta)

    def _configurar_estilos_ttk(self):
        """Los widgets ttk (Combobox, Notebook) se pintan con ttk.Style, no con bg=/fg= directo."""
        p = self.paleta
        s = self._style

        # Sin borde/marco alrededor del area de contenido del Notebook
        s.layout("TNotebook", [
            ("Notebook.client", {"sticky": "nswe"})
        ])

        # Tab minimalista: mismo fondo siempre, el seleccionado solo "brilla"
        # en el color de acento (sin bloque solido ni anillo de foco viejo)
        s.layout("TNotebook.Tab", [
            ("Notebook.tab", {"sticky": "nswe", "children": [
                ("Notebook.padding", {"side": "top", "sticky": "nswe", "children": [
                    ("Notebook.label", {"side": "left", "sticky": ""})
                ]})
            ]})
        ])

        s.configure("TNotebook", background=p["bg"], borderwidth=0)
        s.configure("TNotebook.Tab", background=p["bg"], foreground=p["fg_suave"],
                    borderwidth=0, font=("Arial", 10))
        s.map(
            "TNotebook.Tab",
            background=[("selected", p["bg"]), ("!selected", p["bg"])],
            foreground=[("selected", p["accent"]), ("!selected", p["fg_suave"])],
            padding=[("selected", (16, 10)), ("!selected", (16, 10))],
        )

        s.configure("TCombobox", fieldbackground=p["bg_secundario"], background=p["bg_secundario"],
                    foreground=p["fg"], arrowcolor=p["fg"], borderwidth=1)
        s.map("TCombobox", fieldbackground=[("readonly", p["bg_secundario"])])


def mezclar_color(color1, color2, t):
    """Interpola linealmente entre dos colores hex (#rrggbb). t va de 0.0 a 1.0."""
    def a_rgb(c):
        c = c.lstrip("#")
        return tuple(int(c[i:i + 2], 16) for i in (0, 2, 4))

    r1, g1, b1 = a_rgb(color1)
    r2, g2, b2 = a_rgb(color2)
    r = round(r1 + (r2 - r1) * t)
    g = round(g1 + (g2 - g1) * t)
    b = round(b1 + (b2 - b1) * t)
    return f"#{r:02x}{g:02x}{b:02x}"


def _mapa_icono_tab(tipo):
    """Devuelve una matriz 16x16 de 0/1: 1 = pixel encendido del icono."""
    TAM = 16
    grid = [[0] * TAM for _ in range(TAM)]

    def rect(x0, y0, x1, y1):
        for y in range(y0, y1):
            for x in range(x0, x1):
                if 0 <= x < TAM and 0 <= y < TAM:
                    grid[y][x] = 1

    def circulo(cx, cy, r):
        for y in range(TAM):
            for x in range(TAM):
                if (x - cx) ** 2 + (y - cy) ** 2 <= r * r:
                    grid[y][x] = 1

    if tipo == "notas":
        rect(3, 2, 13, 3)
        rect(3, 13, 13, 14)
        rect(3, 2, 4, 14)
        rect(12, 2, 13, 14)
        rect(5, 5, 11, 6)
        rect(5, 8, 11, 9)
        rect(5, 11, 11, 12)

    elif tipo == "calculadora":
        rect(3, 2, 13, 6)
        for fila in range(2):
            for col in range(3):
                x0 = 3 + col * 3
                y0 = 8 + fila * 4
                rect(x0, y0, x0 + 2, y0 + 2)

    else:  # "dibujo"
        for i in range(8):
            rect(3 + i, 3 + i, 5 + i, 5 + i)
        circulo(12, 12, 2)

    return grid


def crear_icono_tab(tipo, color, tamano=16):
    """Crea una PhotoImage con fondo transparente para usar como icono de pestaña."""
    grid = _mapa_icono_tab(tipo)
    marcador = "#010203"  # color placeholder que luego se vuelve transparente

    filas = []
    for y in range(tamano):
        fila = " ".join(color if grid[y][x] else marcador for x in range(tamano))
        filas.append("{" + fila + "}")

    img = tk.PhotoImage(width=tamano, height=tamano)
    img.put(" ".join(filas))

    for y in range(tamano):
        for x in range(tamano):
            if not grid[y][x]:
                img.transparency_set(x, y, True)

    return img


class ThemeSwitch(tk.Canvas):
    """Switch animado tipo iOS para alternar entre modo claro y oscuro."""

    def __init__(self, parent, theme_manager, width=52, height=26):
        self._bg_padre = parent["bg"] if "bg" in parent.keys() else None
        super().__init__(parent, width=width, height=height, highlightthickness=0,
                            bg=self._bg_padre, cursor="hand2")
        self.theme_manager = theme_manager
        self.w, self.h = width, height
        self.radio_knob = height // 2 - 3
        self.pos = 0.0  # 0.0 = claro (izquierda), 1.0 = oscuro (derecha)
        self.animando = False
        self.paleta = theme_manager.paleta

        self.bind("<Button-1>", self._on_click)
        theme_manager.registrar(self._al_cambiar_tema)

    def _al_cambiar_tema(self, paleta):
        self.paleta = paleta
        objetivo = 1.0 if self.theme_manager.modo == "dark" else 0.0
        if not self.animando:
            self._animar(objetivo)

    def _on_click(self, _event):
        if self.animando:
            return
        self.theme_manager.alternar()

    def _animar(self, objetivo, paso=0, pasos_totales=8):
        self.animando = True
        self.pos += (objetivo - self.pos) * 0.4
        self._dibujar()
        if paso < pasos_totales - 1 and abs(self.pos - objetivo) > 0.01:
            self.after(15, lambda: self._animar(objetivo, paso + 1, pasos_totales))
        else:
            self.pos = objetivo
            self._dibujar()
            self.animando = False

    def _dibujar(self):
        self.delete("all")
        p = self.paleta
        color_track = p["accent"] if self.pos > 0.5 else p["borde"]
        r = self.h / 2

        self.create_oval(0, 0, self.h, self.h, fill=color_track, outline="")
        self.create_oval(self.w - self.h, 0, self.w, self.h, fill=color_track, outline="")
        self.create_rectangle(r, 0, self.w - r, self.h, fill=color_track, outline="")

        cx = r + self.pos * (self.w - self.h)
        cy = self.h / 2
        self.create_oval(cx - self.radio_knob, cy - self.radio_knob,
                            cx + self.radio_knob, cy + self.radio_knob,
                            fill="#ffffff", outline="")

        icono = "🌙" if self.pos > 0.5 else "☀"
        self.create_text(cx, cy, text=icono, font=("Arial", 9))

###dibujo.py

import math
import tkinter as tk
from tkinter import colorchooser, filedialog, messagebox

try:
    from PIL import Image, ImageTk, ImageGrab
    PIL_DISPONIBLE = True
except ImportError:
    PIL_DISPONIBLE = False


PALETA_COLORES = [
    ["#000000", "#7f7f7f", "#880015", "#ed1c24", "#ff7f27", "#fff200", "#22b14c", "#00a2e8", "#3f48cc", "#a349a4"],
    ["#ffffff", "#c3c3c3", "#b97a57", "#ffaec9", "#ffc90e", "#efe4b0", "#b5e61d", "#99d9ea", "#7092be", "#c8bfe7"],
]

HERRAMIENTAS = [
    ("lapiz", "✏"),
    ("borrador", "🧹"),
    ("balde", "🪣"),
    ("texto", "A"),
    ("gotero", "💧"),
    ("zoom", "🔍"),
]

FORMAS = [
    ("linea", "╱"),
    ("curva", "﹏"),
    ("rectangulo", "▭"),
    ("cuadrado", "▢"),
    ("elipse", "⬭"),
    ("circulo", "◯"),
    ("triangulo", "△"),
    ("pentagono", "⬠"),
    ("hexagono", "⬡"),
    ("flecha", "➔"),
    ("globo", "💬"),
]


class ImagenInsertada:
    """
    Representa una imagen pegada/insertada en el canvas.
    Guarda la imagen PIL original (para redimensionar sin perder calidad
    al hacerlo varias veces) y maneja su propio item de canvas + manijas.
    """

    TAMANO_MANIJA = 8

    def __init__(self, canvas, imagen_pil, x, y):
        self.canvas = canvas
        self.imagen_original = imagen_pil
        self.x = x
        self.y = y
        self.ancho = imagen_pil.width
        self.alto = imagen_pil.height
        self.photo = None
        self.item_id = None
        self.manijas = {}
        self.seleccionada = False
        self._crear_item()

    def _crear_item(self):
        self.photo = ImageTk.PhotoImage(
            self.imagen_original.resize((max(1, int(self.ancho)), max(1, int(self.alto))))
        )
        self.item_id = self.canvas.create_image(
            self.x, self.y, image=self.photo, anchor="nw", tags=("imagen",)
        )

    def redibujar(self):
        self.photo = ImageTk.PhotoImage(
            self.imagen_original.resize((max(1, int(self.ancho)), max(1, int(self.alto))))
        )
        self.canvas.itemconfig(self.item_id, image=self.photo)
        self.canvas.coords(self.item_id, self.x, self.y)
        if self.seleccionada:
            self._actualizar_manijas()

    def bbox(self):
        return (self.x, self.y, self.x + self.ancho, self.y + self.alto)

    def contiene_punto(self, px, py):
        x0, y0, x1, y1 = self.bbox()
        return x0 <= px <= x1 and y0 <= py <= y1

    def seleccionar(self, color_manija):
        self.seleccionada = True
        self._crear_manijas(color_manija)

    def deseleccionar(self):
        self.seleccionada = False
        for mid in self.manijas.values():
            self.canvas.delete(mid)
        self.manijas = {}

    def _crear_manijas(self, color):
        m = self.TAMANO_MANIJA / 2
        x0, y0, x1, y1 = self.bbox()
        posiciones = {"nw": (x0, y0), "ne": (x1, y0), "sw": (x0, y1), "se": (x1, y1)}
        for pos, (px, py) in posiciones.items():
            mid = self.canvas.create_rectangle(
                px - m, py - m, px + m, py + m,
                fill=color, outline="#ffffff", tags=("manija", f"manija_{pos}")
            )
            self.manijas[pos] = mid

    def _actualizar_manijas(self):
        m = self.TAMANO_MANIJA / 2
        x0, y0, x1, y1 = self.bbox()
        posiciones = {"nw": (x0, y0), "ne": (x1, y0), "sw": (x0, y1), "se": (x1, y1)}
        for pos, (px, py) in posiciones.items():
            if pos in self.manijas:
                self.canvas.coords(self.manijas[pos], px - m, py - m, px + m, py + m)

    def redimensionar_desde(self, esquina, nx, ny, mantener_aspecto=False):
        x0, y0, x1, y1 = self.bbox()

        if esquina == "se":
            nuevo_ancho = max(10, nx - x0)
            nuevo_alto = max(10, ny - y0)
        elif esquina == "nw":
            nuevo_ancho = max(10, x1 - nx)
            nuevo_alto = max(10, y1 - ny)
            self.x = min(nx, x1 - 10)
            self.y = min(ny, y1 - 10)
        elif esquina == "ne":
            nuevo_ancho = max(10, nx - x0)
            nuevo_alto = max(10, y1 - ny)
            self.y = min(ny, y1 - 10)
        else:  # sw
            nuevo_ancho = max(10, x1 - nx)
            nuevo_alto = max(10, ny - y0)
            self.x = min(nx, x1 - 10)

        if mantener_aspecto:
            relacion = self.imagen_original.width / self.imagen_original.height
            nuevo_alto = nuevo_ancho / relacion

        self.ancho, self.alto = nuevo_ancho, nuevo_alto
        self.redibujar()

    def elevar(self):
        self.canvas.tag_raise(self.item_id)
        for mid in self.manijas.values():
            self.canvas.tag_raise(mid)

    def eliminar(self):
        self.canvas.delete(self.item_id)
        self.deseleccionar()


class DibujoFrame(tk.Frame):
    def __init__(self, parent, theme_manager):
        super().__init__(parent)
        self.theme_manager = theme_manager

        self.color_actual = "black"
        self.color_es_por_defecto = True
        self.grosor_actual = 3
        self.herramienta_actual = "lapiz"
        self.forma_actual = "rectangulo"
        self.modo_relleno = False

        self.ultimo_x = None
        self.ultimo_y = None
        self.punto_inicio_forma = None
        self.item_temporal = None

        self.imagenes = []
        self.imagen_seleccionada = None
        self.arrastrando_manija = None
        self.arrastrando_imagen = False
        self._offset_arrastre = (0, 0)

        self._grupos = []
        self._separadores = []

        self._construir_ui()
        self._configurar_eventos()

        theme_manager.registrar(self._aplicar_tema)

    # ======================================================
    # CONSTRUCCION DE LA INTERFAZ
    # ======================================================

    def _crear_grupo(self, parent, titulo):
        contenedor = tk.Frame(parent)
        contenedor.pack(side="left", padx=6, pady=2)

        etiqueta = tk.Label(contenedor, text=titulo, font=("Arial", 8))
        etiqueta.pack(side="top")

        contenido = tk.Frame(contenedor)
        contenido.pack(side="top", pady=(2, 0))

        grupo = {"contenedor": contenedor, "titulo": etiqueta, "contenido": contenido}
        self._grupos.append(grupo)
        return grupo

    def _crear_separador(self, parent):
        sep = tk.Frame(parent, width=1)
        sep.pack(side="left", fill="y", padx=6, pady=4)
        self._separadores.append(sep)

    def _construir_ui(self):
        self.barra = tk.Frame(self)
        self.barra.pack(fill="x", padx=10, pady=10)

        # --- Herramientas ---
        grupo_h = self._crear_grupo(self.barra, "Herramientas")
        self.botones_herramientas = {}
        for i, (clave, icono) in enumerate(HERRAMIENTAS):
            btn = tk.Button(
                grupo_h["contenido"], text=icono, width=3, font=("Arial", 13),
                relief="flat", bd=0, cursor="hand2",
                command=lambda c=clave: self._elegir_herramienta(c)
            )
            btn.grid(row=i // 3, column=i % 3, padx=2, pady=1)
            self.botones_herramientas[clave] = btn

        self._crear_separador(self.barra)

        # --- Pinceles (grosor) ---
        grupo_p = self._crear_grupo(self.barra, "Pinceles")
        self.slider_grosor = tk.Scale(
            grupo_p["contenido"], from_=1, to=40, orient="horizontal",
            command=self._cambiar_grosor, length=90, bd=0, highlightthickness=0
        )
        self.slider_grosor.set(self.grosor_actual)
        self.slider_grosor.pack()

        self._crear_separador(self.barra)

        # --- Formas ---
        grupo_f = self._crear_grupo(self.barra, "Formas")
        self.botones_formas = {}
        for i, (clave, etiqueta) in enumerate(FORMAS):
            btn = tk.Button(
                grupo_f["contenido"], text=etiqueta, width=3, font=("Arial", 12),
                relief="flat", bd=0, cursor="hand2",
                command=lambda c=clave: self._elegir_forma(c)
            )
            btn.grid(row=i // 6, column=i % 6, padx=2, pady=1)
            self.botones_formas[clave] = btn

        self.btn_relleno = tk.Button(
            grupo_f["contenido"], text="Relleno: No", font=("Arial", 8),
            relief="flat", bd=0, cursor="hand2", command=self._toggle_relleno
        )
        self.btn_relleno.grid(row=2, column=0, columnspan=6, pady=(4, 0), sticky="w")

        self._crear_separador(self.barra)

        # --- Colores ---
        grupo_c = self._crear_grupo(self.barra, "Colores")
        self.botones_colores = []
        for fila_idx, fila_colores in enumerate(PALETA_COLORES):
            for col_idx, color in enumerate(fila_colores):
                sw = tk.Label(
                    grupo_c["contenido"], bg=color, width=2, height=1,
                    relief="flat", cursor="hand2",
                    highlightthickness=1, highlightbackground="#888888"
                )
                sw.grid(row=fila_idx, column=col_idx, padx=1, pady=1)
                sw.bind("<Button-1>", lambda e, c=color: self._elegir_color(c))
                self.botones_colores.append(sw)

        self.muestra_color_actual = tk.Label(
            grupo_c["contenido"], width=3, height=2, relief="flat", highlightthickness=2
        )
        self.muestra_color_actual.grid(row=0, column=10, rowspan=2, padx=(10, 4))

        self.btn_color_personalizado = tk.Button(
            grupo_c["contenido"], text="🎨", font=("Arial", 14),
            relief="flat", bd=0, cursor="hand2", command=self.elegir_color_personalizado
        )
        self.btn_color_personalizado.grid(row=0, column=11, rowspan=2, padx=4)

        self._crear_separador(self.barra)

        # --- Imagen / acciones ---
        grupo_a = self._crear_grupo(self.barra, "Imagen")
        self.btn_insertar_imagen = tk.Button(
            grupo_a["contenido"], text="🖼 Insertar", relief="flat", bd=0,
            cursor="hand2", command=self.insertar_imagen_desde_archivo
        )
        self.btn_insertar_imagen.pack(side="top", pady=(0, 2))

        self.btn_borrar_todo = tk.Button(
            grupo_a["contenido"], text="🗑 Borrar todo", relief="flat", bd=0,
            cursor="hand2", command=self.borrar_todo
        )
        self.btn_borrar_todo.pack(side="top")

        if not PIL_DISPONIBLE:
            self.btn_insertar_imagen.configure(state="disabled")

        # --- Canvas ---
        self.canvas = tk.Canvas(self, cursor="pencil", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True, padx=14, pady=(0, 14))

        self._resaltar_boton(self.botones_herramientas["lapiz"], True)

    # ======================================================
    # EVENTOS
    # ======================================================

    def _configurar_eventos(self):
        self.canvas.bind("<Button-1>", self._click_canvas)
        self.canvas.bind("<B1-Motion>", self._arrastrar_canvas)
        self.canvas.bind("<ButtonRelease-1>", self._soltar_canvas)
        self.canvas.bind("<Delete>", self._eliminar_seleccion)
        self.canvas.bind("<BackSpace>", self._eliminar_seleccion)

        # El canvas toma el foco al pasar el mouse, asi Ctrl+V / Delete
        # funcionan sin tener que hacer click primero -- y como los binds
        # son sobre el canvas (no bind_all), no interfieren con otras pestañas.
        self.canvas.bind("<Enter>", lambda e: self.canvas.focus_set())
        self.canvas.bind("<Control-v>", self._pegar_imagen_portapapeles)

    # ======================================================
    # HERRAMIENTAS Y FORMAS: SELECCION
    # ======================================================

    def _elegir_herramienta(self, clave):
        self.herramienta_actual = clave
        self._deseleccionar_imagen()

        for k, btn in self.botones_herramientas.items():
            self._resaltar_boton(btn, k == clave)
        for btn in self.botones_formas.values():
            self._resaltar_boton(btn, False)

        cursores = {
            "lapiz": "pencil", "borrador": "dotbox", "balde": "spraycan",
            "texto": "xterm", "gotero": "target", "zoom": "sizing",
        }
        self.canvas.configure(cursor=cursores.get(clave, "cross"))

    def _elegir_forma(self, clave):
        self.forma_actual = clave
        self.herramienta_actual = "forma"
        self._deseleccionar_imagen()

        for btn in self.botones_herramientas.values():
            self._resaltar_boton(btn, False)
        for k, btn in self.botones_formas.items():
            self._resaltar_boton(btn, k == clave)

        self.canvas.configure(cursor="cross")

    def _resaltar_boton(self, btn, activo):
        p = self.theme_manager.paleta
        if activo:
            btn.configure(bg=p["accent"], fg="#ffffff", activebackground=p["accent_hover"])
        else:
            btn.configure(bg=p["bg_secundario"], fg=p["fg"], activebackground=p["accent_suave"])

    def _toggle_relleno(self):
        self.modo_relleno = not self.modo_relleno
        self.btn_relleno.configure(text=f"Relleno: {'Sí' if self.modo_relleno else 'No'}")

    # ======================================================
    # COLOR Y GROSOR
    # ======================================================

    def _elegir_color(self, color):
        self.color_actual = color
        self.color_es_por_defecto = False
        self.muestra_color_actual.configure(bg=color)

    def elegir_color_personalizado(self):
        color = colorchooser.askcolor(title="Elige un color")[1]
        if color:
            self._elegir_color(color)

    def _cambiar_grosor(self, valor):
        self.grosor_actual = int(valor)

    # ======================================================
    # CLICK / ARRASTRAR / SOLTAR EN EL CANVAS
    # ======================================================

    def _click_canvas(self, event):
        self.canvas.focus_set()
        x, y = event.x, event.y

        esquina = self._detectar_manija(x, y)
        if esquina:
            self.arrastrando_manija = (self.imagen_seleccionada, esquina)
            return

        imagen_clickeada = self._imagen_en_punto(x, y)
        if imagen_clickeada:
            self._seleccionar_imagen(imagen_clickeada)
            self.arrastrando_imagen = True
            self._offset_arrastre = (x - imagen_clickeada.x, y - imagen_clickeada.y)
            return

        self._deseleccionar_imagen()

        if self.herramienta_actual in ("lapiz", "borrador"):
            self.ultimo_x, self.ultimo_y = x, y

        elif self.herramienta_actual == "balde":
            self._aplicar_balde(x, y)

        elif self.herramienta_actual == "gotero":
            self._usar_gotero(x, y)

        elif self.herramienta_actual == "texto":
            self._agregar_texto(x, y)

        elif self.herramienta_actual == "zoom":
            self._zoom_en_punto(x, y)

        elif self.herramienta_actual == "forma":
            self.punto_inicio_forma = (x, y)
            self.item_temporal = None

    def _arrastrar_canvas(self, event):
        x, y = event.x, event.y

        if self.arrastrando_manija:
            imagen, esquina = self.arrastrando_manija
            mantener_aspecto = (event.state & 0x0001) != 0  # Shift
            imagen.redimensionar_desde(esquina, x, y, mantener_aspecto)
            return

        if self.arrastrando_imagen and self.imagen_seleccionada:
            offx, offy = self._offset_arrastre
            self.imagen_seleccionada.x = x - offx
            self.imagen_seleccionada.y = y - offy
            self.imagen_seleccionada.redibujar()
            return

        if self.herramienta_actual == "lapiz":
            if self.ultimo_x is not None:
                self.canvas.create_line(
                    self.ultimo_x, self.ultimo_y, x, y,
                    fill=self.color_actual, width=self.grosor_actual,
                    capstyle="round", smooth=True, tags=("trazo",)
                )
            self.ultimo_x, self.ultimo_y = x, y

        elif self.herramienta_actual == "borrador":
            if self.ultimo_x is not None:
                self.canvas.create_line(
                    self.ultimo_x, self.ultimo_y, x, y,
                    fill=self.canvas["bg"], width=self.grosor_actual * 2,
                    capstyle="round", smooth=True, tags=("trazo", "borrado")
                )
            self.ultimo_x, self.ultimo_y = x, y

        elif self.herramienta_actual == "forma" and self.punto_inicio_forma:
            if self.item_temporal:
                self.canvas.delete(self.item_temporal)
            self.item_temporal = self._crear_forma(self.punto_inicio_forma, (x, y), preliminar=True)

    def _soltar_canvas(self, event):
        x, y = event.x, event.y

        if self.arrastrando_manija:
            self.arrastrando_manija = None
            return

        if self.arrastrando_imagen:
            self.arrastrando_imagen = False
            return

        if self.herramienta_actual in ("lapiz", "borrador"):
            self.ultimo_x, self.ultimo_y = None, None

        elif self.herramienta_actual == "forma" and self.punto_inicio_forma:
            if self.item_temporal:
                self.canvas.delete(self.item_temporal)
                self.item_temporal = None
            if self.punto_inicio_forma != (x, y):
                self._crear_forma(self.punto_inicio_forma, (x, y), preliminar=False)
            self.punto_inicio_forma = None

    # ======================================================
    # FORMAS
    # ======================================================

    def _crear_forma(self, inicio, fin, preliminar):
        x0, y0 = inicio
        x1, y1 = fin
        color = self.color_actual
        ancho = self.grosor_actual
        relleno = color if self.modo_relleno else ""
        tags = ("preview",) if preliminar else ("trazo", "forma")
        dash = (4, 3) if preliminar else None
        forma = self.forma_actual

        if forma == "linea":
            return self.canvas.create_line(
                x0, y0, x1, y1, fill=color, width=ancho,
                capstyle="round", tags=tags, dash=dash
            )

        if forma == "curva":
            mx = (x0 + x1) / 2
            my = min(y0, y1) - abs(x1 - x0) / 4
            return self.canvas.create_line(
                x0, y0, mx, my, x1, y1, fill=color, width=ancho,
                smooth=True, tags=tags, dash=dash
            )

        if forma == "flecha":
            return self.canvas.create_line(
                x0, y0, x1, y1, fill=color, width=ancho,
                arrow="last", arrowshape=(10, 12, 5), tags=tags, dash=dash
            )

        if forma == "rectangulo":
            return self.canvas.create_rectangle(
                x0, y0, x1, y1, outline=color, width=ancho, fill=relleno, tags=tags, dash=dash
            )

        if forma == "cuadrado":
            lado = max(abs(x1 - x0), abs(y1 - y0))
            x1 = x0 + lado if x1 >= x0 else x0 - lado
            y1 = y0 + lado if y1 >= y0 else y0 - lado
            return self.canvas.create_rectangle(
                x0, y0, x1, y1, outline=color, width=ancho, fill=relleno, tags=tags, dash=dash
            )

        if forma == "elipse":
            return self.canvas.create_oval(
                x0, y0, x1, y1, outline=color, width=ancho, fill=relleno, tags=tags, dash=dash
            )

        if forma == "circulo":
            radio = max(abs(x1 - x0), abs(y1 - y0))
            x1 = x0 + radio if x1 >= x0 else x0 - radio
            y1 = y0 + radio if y1 >= y0 else y0 - radio
            return self.canvas.create_oval(
                x0, y0, x1, y1, outline=color, width=ancho, fill=relleno, tags=tags, dash=dash
            )

        if forma == "triangulo":
            puntos = [(x0 + x1) / 2, y0, x0, y1, x1, y1]
            return self.canvas.create_polygon(
                puntos, outline=color, width=ancho, fill=relleno, tags=tags, dash=dash
            )

        if forma in ("pentagono", "hexagono"):
            lados = 5 if forma == "pentagono" else 6
            cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
            radio = max(abs(x1 - x0), abs(y1 - y0)) / 2
            puntos = []
            for i in range(lados):
                angulo = math.radians(90 + i * 360 / lados)
                puntos.append(cx + radio * math.cos(angulo))
                puntos.append(cy - radio * math.sin(angulo))
            return self.canvas.create_polygon(
                puntos, outline=color, width=ancho, fill=relleno, tags=tags, dash=dash
            )

        if forma == "globo":
            return self._crear_globo(x0, y0, x1, y1, color, ancho, relleno, tags, dash)

        return None

    def _crear_globo(self, x0, y0, x1, y1, color, ancho, relleno, tags, dash):
        radio = min(20, abs(x1 - x0) / 4, abs(y1 - y0) / 4)
        puntos = [
            x0 + radio, y0,
            x1 - radio, y0,
            x1, y0 + radio,
            x1, y1 - radio,
            x1 - radio, y1,
            x0 + radio * 3, y1,
            x0 + radio, y1 + radio * 1.5,
            x0 + radio * 2, y1,
            x0, y1 - radio,
            x0, y0 + radio,
        ]
        return self.canvas.create_polygon(
            puntos, outline=color, width=ancho, fill=relleno,
            smooth=True, tags=tags, dash=dash
        )

    # ======================================================
    # BALDE / GOTERO / TEXTO / ZOOM
    # ======================================================

    def _item_en_punto(self, x, y):
        # Primero, deteccion nativa de Tk (funciona bien para lineas,
        # texto, y formas que ya tienen relleno)
        candidatos = self.canvas.find_overlapping(x - 2, y - 2, x + 2, y + 2)
        for item in reversed(candidatos):
            tags = self.canvas.gettags(item)
            if "manija" in tags or "imagen" in tags:
                continue
            return item

        # Respaldo: Tk NO detecta clics dentro de formas sin relleno
        # (rectangulo/ovalo/poligono con fill=""), solo sobre su borde.
        # Para que el balde funcione igual, revisamos el bounding box.
        for item in reversed(self.canvas.find_all()):
            tags = self.canvas.gettags(item)
            if "manija" in tags or "imagen" in tags:
                continue
            if self.canvas.type(item) in ("rectangle", "oval", "polygon"):
                bbox = self.canvas.bbox(item)
                if bbox and bbox[0] <= x <= bbox[2] and bbox[1] <= y <= bbox[3]:
                    return item

        return None

    def _aplicar_balde(self, x, y):
        item = self._item_en_punto(x, y)
        if item is None:
            self.canvas.configure(bg=self.color_actual)
            return
        if self.canvas.type(item) in ("rectangle", "oval", "polygon", "line"):
            self.canvas.itemconfig(item, fill=self.color_actual)

    def _usar_gotero(self, x, y):
        item = self._item_en_punto(x, y)
        if item is None:
            return
        try:
            color = self.canvas.itemcget(item, "fill") or self.canvas.itemcget(item, "outline")
        except tk.TclError:
            color = None
        if color:
            self._elegir_color(color)

    def _agregar_texto(self, x, y):
        tamano_fuente = max(10, self.grosor_actual * 4)
        entrada = tk.Entry(self.canvas, font=("Arial", tamano_fuente), bd=0)
        ventana_id = self.canvas.create_window(x, y, window=entrada, anchor="nw")
        entrada.focus_set()

        def confirmar(event=None):
            texto = entrada.get()
            self.canvas.delete(ventana_id)
            entrada.destroy()
            if texto:
                self.canvas.create_text(
                    x, y, text=texto, fill=self.color_actual,
                    font=("Arial", tamano_fuente), anchor="nw", tags=("trazo", "texto")
                )

        entrada.bind("<Return>", confirmar)
        entrada.bind("<FocusOut>", confirmar)

    def _zoom_en_punto(self, x, y):
        factor = 1.2
        self.canvas.scale("all", x, y, factor, factor)

    # ======================================================
    # IMAGENES: INSERTAR, MOVER, REDIMENSIONAR, ELIMINAR
    # ======================================================

    def insertar_imagen_desde_archivo(self):
        if not PIL_DISPONIBLE:
            messagebox.showwarning(
                "Falta Pillow",
                "Instala Pillow para insertar imagenes:\n    pip install Pillow"
            )
            return

        ruta = filedialog.askopenfilename(
            title="Selecciona una imagen",
            filetypes=[("Imagenes", "*.png *.jpg *.jpeg *.gif *.bmp"), ("Todos los archivos", "*.*")]
        )
        if not ruta:
            return

        try:
            imagen = Image.open(ruta)
            imagen.load()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir la imagen:\n{e}")
            return

        self._insertar_imagen_pil(imagen)

    def _pegar_imagen_portapapeles(self, event=None):
        if not PIL_DISPONIBLE:
            return "break"

        try:
            contenido = ImageGrab.grabclipboard()
        except Exception:
            contenido = None

        if isinstance(contenido, Image.Image):
            self._insertar_imagen_pil(contenido)
        elif isinstance(contenido, list) and contenido:
            try:
                imagen = Image.open(contenido[0])
                self._insertar_imagen_pil(imagen)
            except Exception:
                pass

        return "break"

    def _insertar_imagen_pil(self, imagen_pil, x=40, y=40):
        ancho_canvas = self.canvas.winfo_width() or 600
        alto_canvas = self.canvas.winfo_height() or 400

        max_ancho, max_alto = ancho_canvas * 0.8, alto_canvas * 0.8
        if imagen_pil.width > max_ancho or imagen_pil.height > max_alto:
            proporcion = min(max_ancho / imagen_pil.width, max_alto / imagen_pil.height)
            nuevo_tamano = (
                max(1, int(imagen_pil.width * proporcion)),
                max(1, int(imagen_pil.height * proporcion)),
            )
            imagen_pil = imagen_pil.resize(nuevo_tamano)

        imagen_pil = imagen_pil.convert("RGBA")
        nueva = ImagenInsertada(self.canvas, imagen_pil, x, y)
        self.imagenes.append(nueva)
        self._seleccionar_imagen(nueva)

    def _imagen_en_punto(self, x, y):
        for imagen in reversed(self.imagenes):
            if imagen.contiene_punto(x, y):
                return imagen
        return None

    def _detectar_manija(self, x, y):
        if not self.imagen_seleccionada:
            return None
        for pos, mid in self.imagen_seleccionada.manijas.items():
            coords = self.canvas.coords(mid)
            if coords and coords[0] - 2 <= x <= coords[2] + 2 and coords[1] - 2 <= y <= coords[3] + 2:
                return pos
        return None

    def _seleccionar_imagen(self, imagen):
        self._deseleccionar_imagen()
        self.imagen_seleccionada = imagen
        imagen.seleccionar(self.theme_manager.paleta["accent"])
        imagen.elevar()

    def _deseleccionar_imagen(self):
        if self.imagen_seleccionada:
            self.imagen_seleccionada.deseleccionar()
            self.imagen_seleccionada = None

    def _eliminar_seleccion(self, event=None):
        if self.imagen_seleccionada:
            self.imagenes.remove(self.imagen_seleccionada)
            self.imagen_seleccionada.eliminar()
            self.imagen_seleccionada = None

    # ======================================================
    # BORRAR TODO
    # ======================================================

    def borrar_todo(self):
        self.canvas.delete("all")
        self.imagenes = []
        self.imagen_seleccionada = None

    # ======================================================
    # TEMA
    # ======================================================

    def _aplicar_tema(self, paleta):
        p = paleta
        self.configure(bg=p["bg"])
        self.barra.configure(bg=p["bg"])

        for grupo in self._grupos:
            grupo["contenedor"].configure(bg=p["bg"])
            grupo["titulo"].configure(bg=p["bg"], fg=p["fg_suave"])
            grupo["contenido"].configure(bg=p["bg"])

        for sep in self._separadores:
            sep.configure(bg=p["borde"])

        self.slider_grosor.configure(
            bg=p["bg"], fg=p["fg"], troughcolor=p["borde"], activebackground=p["accent"]
        )

        for k, btn in self.botones_herramientas.items():
            self._resaltar_boton(btn, k == self.herramienta_actual)
        for k, btn in self.botones_formas.items():
            self._resaltar_boton(btn, self.herramienta_actual == "forma" and k == self.forma_actual)

        self.btn_relleno.configure(bg=p["bg_secundario"], fg=p["fg"], activebackground=p["accent_suave"])

        self.muestra_color_actual.configure(
            bg=self.color_actual, highlightbackground=p["borde"], highlightcolor=p["borde"]
        )
        self.btn_color_personalizado.configure(bg=p["bg_secundario"], fg=p["fg"], activebackground=p["accent_suave"])

        self.btn_insertar_imagen.configure(bg=p["bg_secundario"], fg=p["fg"], activebackground=p["accent_suave"])
        self.btn_borrar_todo.configure(bg=p["bg_secundario"], fg=p["fg"], activebackground=p["accent_suave"])

        self.canvas.configure(bg=p["bg_secundario"])

        if self.color_es_por_defecto:
            self.color_actual = "#ffffff" if self.theme_manager.modo == "dark" else "#000000"
            self.muestra_color_actual.configure(bg=self.color_actual)
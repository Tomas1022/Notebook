import tkinter as tk

from calculator.conjuntos import ConjuntosFrame
from calculator.matrices import MatricesFrame
from calculator.calculo import CalculoFrame
from calculator.historial import HistorialManager


class BasicaFrame(tk.Frame):

    def __init__(
        self,
        parent,
        theme_manager,
        historial
    ):
        super().__init__(parent)

        self.theme_manager = theme_manager
        self.historial = historial
        self.expresion = ""

        self.display = tk.Entry(
            self,
            font=("Arial", 20),
            justify="right",
            bd=0,
            relief="flat"
        )

        self.display.pack(
            fill="x",
            padx=14,
            pady=14,
            ipady=12
        )

        self.botones_frame = tk.Frame(self)

        self.botones_frame.pack(
            padx=14,
            pady=10
        )

        botones = [
            ("7", "8", "9", "/"),
            ("4", "5", "6", "*"),
            ("1", "2", "3", "-"),
            ("C", "0", "=", "+")
        ]

        self.botones = []

        for fila_idx, fila in enumerate(botones):

            for col_idx, texto in enumerate(fila):

                btn = tk.Button(
                    self.botones_frame,
                    text=texto,
                    width=6,
                    height=2,
                    font=("Arial", 14),
                    relief="flat",
                    bd=0,
                    cursor="hand2",
                    command=lambda t=texto:
                    self.click_boton(t)
                )

                btn.grid(
                    row=fila_idx,
                    column=col_idx,
                    padx=3,
                    pady=3
                )

                self.botones.append(
                    (btn, texto)
                )

        self.bind_all(
            "<Key>",
            self._teclado
        )

        theme_manager.registrar(
            self._aplicar_tema
        )

    def _teclado(self, event):

        if not self.winfo_ismapped():
            return

        tecla = event.keysym

        if event.char in "0123456789+-*/.":

            self.click_boton(
                event.char
            )

            return "break"

        if tecla in (
            "Return",
            "KP_Enter"
        ):

            self.click_boton("=")

            return "break"

        if tecla in (
            "Escape",
            "Delete"
        ):

            self.click_boton("C")

            return "break"

        if tecla == "BackSpace":

            self.expresion = (
                self.expresion[:-1]
            )

            self._actualizar_display()

            return "break"

    def click_boton(self, texto):

        if texto == "C":

            self.expresion = ""

        elif texto == "=":

            if not self.expresion:
                return

            try:

                caracteres_validos = set(
                    "0123456789+-*/. "
                )

                if not all(
                    c in caracteres_validos
                    for c in self.expresion
                ):
                    raise ValueError

                expresion_original = (
                    self.expresion
                )

                resultado = eval(
                    self.expresion,
                    {"__builtins__": None},
                    {}
                )

                self.expresion = str(
                    resultado
                )

                self.historial.registrar(
                    "Básica",
                    "Operación",
                    expresion_original,
                    self.expresion,
                    [
                        f"{expresion_original} = "
                        f"{self.expresion}"
                    ]
                )

            except (
                ZeroDivisionError,
                SyntaxError,
                TypeError,
                ValueError
            ):

                self.expresion = "Error"

        else:

            if self.expresion == "Error":
                self.expresion = ""

            self.expresion += texto

        self._actualizar_display()

    def _actualizar_display(self):

        self.display.delete(
            0,
            "end"
        )

        self.display.insert(
            0,
            self.expresion
        )

    def _aplicar_tema(self, p):

        self.configure(
            bg=p["bg"]
        )

        self.botones_frame.configure(
            bg=p["bg"]
        )

        self.display.configure(
            bg=p["bg_secundario"],
            fg=p["fg"],
            insertbackground=p["fg"],
            highlightthickness=1,
            highlightbackground=p["borde"],
            highlightcolor=p["accent"]
        )

        for btn, texto in self.botones:

            if texto == "=":

                btn.configure(
                    bg=p["accent"],
                    fg="#ffffff",
                    activebackground=p["accent_hover"]
                )

            elif texto in (
                "/",
                "*",
                "-",
                "+",
                "C"
            ):

                btn.configure(
                    bg=p["bg_secundario"],
                    fg=p["accent"],
                    activebackground=p["accent_suave"]
                )

            else:

                btn.configure(
                    bg=p["bg_secundario"],
                    fg=p["fg"],
                    activebackground=p["accent_suave"]
                )


class CalculadoraFrame(tk.Frame):

    def __init__(
        self,
        parent,
        theme_manager
    ):
        super().__init__(parent)

        self.theme_manager = theme_manager

        self.historial = HistorialManager(
            theme_manager
        )

        self.historial_abierto = False
        self.animando_historial = False
        self.animacion_id = None

        self.ancho_historial = 390
        self.velocidad_historial = 25

        self.barra = tk.Frame(self)

        self.barra.pack(
            fill="x",
            padx=8,
            pady=(8, 0)
        )

        self.btn_historial = tk.Button(
            self.barra,
            text="Historial ▼",
            relief="flat",
            bd=0,
            cursor="hand2",
            padx=14,
            pady=7,
            command=self.toggle_historial
        )

        self.btn_historial.pack(
            side="right"
        )

        self.tabs_frame = tk.Frame(self)

        self.tabs_frame.pack(
            fill="x",
            padx=8,
            pady=(8, 0)
        )

        self.contenedor = tk.Frame(self)

        self.contenedor.pack(
            fill="both",
            expand=True
        )

        self.botones = {}
        self.frames = {}

        self._crear_pestanas()

        self.historial_frame = (
            self.historial.crear_panel(
                self
            )
        )

        self.historial_frame.place(
            x=0,
            y=0,
            width=0,
            relheight=1
        )

        theme_manager.registrar(
            self._aplicar_tema
        )

        self._seleccionar(
            "Básica"
        )

    def _crear_pestanas(self):

        nombres = (
            "Básica",
            "Matrices",
            "Conjuntos",
            "Cálculo"
        )

        self.frames["Básica"] = BasicaFrame(
            self.contenedor,
            self.theme_manager,
            self.historial
        )

        self.frames["Matrices"] = MatricesFrame(
            self.contenedor,
            self.theme_manager,
            self.historial
        )

        self.frames["Conjuntos"] = ConjuntosFrame(
            self.contenedor,
            self.theme_manager,
            self.historial
        )

        self.frames["Cálculo"] = CalculoFrame(
            self.contenedor,
            self.theme_manager,
            self.historial
        )

        for nombre in nombres:

            boton = tk.Button(
                self.tabs_frame,
                text=nombre,
                relief="flat",
                bd=0,
                cursor="hand2",
                padx=16,
                pady=9,
                command=lambda n=nombre:
                self._seleccionar(n)
            )

            boton.pack(
                side="left",
                padx=2
            )

            self.botones[nombre] = boton

    def _seleccionar(self, nombre):

        for frame in self.frames.values():

            frame.pack_forget()

        self.frames[nombre].pack(
            fill="both",
            expand=True
        )

        p = self.theme_manager.paleta

        for nombre_tab, boton in self.botones.items():

            if nombre_tab == nombre:

                boton.configure(
                    bg=p["accent"],
                    fg="#ffffff",
                    activebackground=p["accent_hover"]
                )

            else:

                boton.configure(
                    bg=p["bg"],
                    fg=p["fg_suave"],
                    activebackground=p["bg"]
                )

    def toggle_historial(self):

        if self.animando_historial:
            return

        if self.historial_abierto:
            self._cerrar_historial()
        else:
            self._abrir_historial()

    def _abrir_historial(self):

        if self.historial_frame is None:
            return

        self._cancelar_animacion()

        self.update_idletasks()

        ancho_total = self.winfo_width()
        alto_total = self.winfo_height()

        if ancho_total <= 0:
            ancho_total = self.winfo_reqwidth()

        if alto_total <= 0:
            alto_total = 500

        ancho = min(
            self.ancho_historial,
            ancho_total
        )

        x_inicio = ancho_total
        x_final = ancho_total - ancho

        self.historial_frame.place(
            x=x_inicio,
            y=0,
            width=ancho,
            height=alto_total
        )

        self.historial_frame.lift()

        self.historial.actualizar()

        self.historial_abierto = True
        self.animando_historial = True

        self.btn_historial.configure(
            text="Historial ▲"
        )

        self._animar_historial(
            x_inicio,
            x_final,
            "abrir"
        )

    def _cerrar_historial(self):

        if self.historial_frame is None:
            return

        self._cancelar_animacion()

        self.update_idletasks()

        ancho_total = self.winfo_width()

        if ancho_total <= 0:
            ancho_total = self.winfo_reqwidth()

        ancho = self.historial_frame.winfo_width()

        if ancho <= 0:
            ancho = self.ancho_historial

        x_inicio = ancho_total - ancho
        x_final = ancho_total

        self.historial_abierto = False
        self.animando_historial = True

        self._animar_historial(
            x_inicio,
            x_final,
            "cerrar"
        )

    def _animar_historial(
        self,
        x_actual,
        x_objetivo,
        accion
    ):

        if self.historial_frame is None:
            self.animando_historial = False
            return

        if not self.historial_frame.winfo_exists():
            self.animando_historial = False
            return

        distancia = x_objetivo - x_actual

        if abs(distancia) <= 3:

            self.historial_frame.place_configure(
                x=x_objetivo
            )

            self.animacion_id = None
            self.animando_historial = False

            if accion == "abrir":

                self.historial_frame.lift()

                self.historial_abierto = True

            else:

                self.historial_frame.place_configure(
                    x=self.winfo_width(),
                    width=self.ancho_historial
                )

                self.historial_abierto = False

                self.btn_historial.configure(
                    text="Historial ▼"
                )

                self.historial._limpiar_detalle()

            return

        paso = min(
            self.velocidad_historial,
            abs(distancia)
        )

        if distancia > 0:
            siguiente = x_actual + paso
        else:
            siguiente = x_actual - paso

        self.historial_frame.place_configure(
            x=siguiente
        )

        self.historial_frame.lift()

        self.animacion_id = self.after(
            10,
            lambda: self._animar_historial(
                siguiente,
                x_objetivo,
                accion
            )
        )

    def _cancelar_animacion(self):

        if self.animacion_id is not None:

            try:

                self.after_cancel(
                    self.animacion_id
                )

            except tk.TclError:
                pass

        self.animacion_id = None
        self.animando_historial = False

    def _aplicar_tema(self, p):

        self.configure(
            bg=p["bg"]
        )

        self.barra.configure(
            bg=p["bg"]
        )

        self.tabs_frame.configure(
            bg=p["bg"]
        )

        self.contenedor.configure(
            bg=p["bg"]
        )

        self.btn_historial.configure(
            bg=p["bg_secundario"],
            fg=p["accent"],
            activebackground=p["accent_suave"],
            activeforeground=p["accent"]
        )

        nombre_actual = "Básica"

        for nombre, frame in self.frames.items():

            if frame.winfo_ismapped():

                nombre_actual = nombre
                break

        self._seleccionar(
            nombre_actual
        )
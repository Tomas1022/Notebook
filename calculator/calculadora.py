import ast
import math
import operator
import tkinter as tk
from typing import ClassVar

from calculator.conjuntos import ConjuntosFrame
from calculator.matrices import MatricesFrame
from calculator.calculo import CalculoFrame


class EvaluadorMatematico:
    """
    Evaluador limitado para operaciones matemáticas.

    Operaciones permitidas:
        +
        -
        *
        /
        %
        **
        paréntesis
        números decimales
    """

    OPERADORES: ClassVar[dict[type[ast.operator], object]] = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.Mod: operator.mod,
        ast.Pow: operator.pow,
        ast.USub: operator.neg,
        ast.UAdd: operator.pos,
    }

    @classmethod
    def evaluar(cls, expresion):
        expresion = expresion.strip()

        if not expresion:
            return ""

        # Evitar expresiones excesivamente grandes
        if len(expresion) > 200:
            raise ValueError("Expresión demasiado larga.")

        try:
            arbol = ast.parse(
                expresion,
                mode="eval"
            )

            resultado = cls._evaluar_nodo(
                arbol.body
            )

            if not math.isfinite(resultado):
                raise ValueError("Resultado no válido.")

            return resultado

        except SyntaxError:
            raise ValueError("Expresión inválida.")

    @classmethod
    def _evaluar_nodo(cls, nodo):

        if isinstance(nodo, ast.Constant):

            if isinstance(
                nodo.value,
                (int, float)
            ):
                return nodo.value

            raise ValueError(
                "Valor no permitido."
            )

        if isinstance(nodo, ast.BinOp):

            operador = cls.OPERADORES.get(
                type(nodo.op)
            )

            if operador is None:
                raise ValueError(
                    "Operador no permitido."
                )

            izquierdo = cls._evaluar_nodo(
                nodo.left
            )

            derecho = cls._evaluar_nodo(
                nodo.right
            )

            # Evitar exponentes exagerados
            if (
                isinstance(nodo.op, ast.Pow)
                and abs(derecho) > 100
            ):
                raise ValueError(
                    "Exponente demasiado grande."
                )

            return operador(
                izquierdo,
                derecho
            )

        if isinstance(nodo, ast.UnaryOp):

            operador = cls.OPERADORES.get(
                type(nodo.op)
            )

            if operador is None:
                raise ValueError(
                    "Operador no permitido."
                )

            valor = cls._evaluar_nodo(
                nodo.operand
            )

            return operador(valor)

        raise ValueError(
            "Operación no permitida."
        )

class BasicaFrame(tk.Frame):
    """
    Calculadora básica.

    Soporta:

        + - * / %
        paréntesis
        decimales
        cambio de signo
        borrar carácter
        limpiar
        teclado físico
        Enter
        Escape
        Backspace
        Delete
    """

    def __init__(
        self,
        parent,
        theme_manager
    ):

        super().__init__(parent)

        self.theme_manager = theme_manager
        self.expresion = ""

        self.display = tk.Entry(
            self,
            font=("Arial", 22),
            justify="right",
            bd=0,
            relief="flat"
        )

        self.display.pack(
            fill="x",
            padx=24,
            pady=(24, 12),
            ipady=14
        )

        self.botones_frame = tk.Frame(
            self
        )

        self.botones_frame.pack(
            padx=24,
            pady=12
        )

        for columna in range(4):

            self.botones_frame.grid_columnconfigure(
                columna,
                weight=1
            )

        botones = [
            ("C", "⌫", "(", ")"),
            ("7", "8", "9", "/"),
            ("4", "5", "6", "*"),
            ("1", "2", "3", "-"),
            ("±", "0", ".", "+"),
            ("%", "", "=", ""),
        ]

        self.botones = []

        for fila_idx, fila in enumerate(botones):

            for col_idx, texto in enumerate(fila):

                if texto == "":
                    continue

                btn = tk.Button(
                    self.botones_frame,
                    text=texto,
                    width=6,
                    height=2,
                    font=("Arial", 14),
                    relief="flat",
                    bd=0,
                    highlightthickness=0,
                    cursor="hand2",
                    command=lambda t=texto:
                        self.click_boton(t)
                )

                btn.grid(
                    row=fila_idx,
                    column=col_idx,
                    padx=4,
                    pady=4,
                    sticky="nsew"
                )

                self.botones.append(
                    (btn, texto)
                )

        self._configurar_teclado()

        theme_manager.registrar(
            self._aplicar_tema
        )

        self.after(
            100,
            self._enfocar_display
        )

    def _configurar_teclado(self):

        self.display.bind(
            "<FocusIn>",
            self._activar_teclado
        )

        self.display.bind(
            "<FocusOut>",
            self._desactivar_teclado
        )

    def _activar_teclado(self, event=None):

        self.bind_all(
            "<Key>",
            self._tecla_presionada
        )

        self.bind_all(
            "<Return>",
            self._tecla_enter
        )

        self.bind_all(
            "<KP_Enter>",
            self._tecla_enter
        )

        self.bind_all(
            "<Escape>",
            self._tecla_escape
        )

        self.bind_all(
            "<BackSpace>",
            self._tecla_backspace
        )

        self.bind_all(
            "<Delete>",
            self._tecla_delete
        )

    def _desactivar_teclado(self, event=None):

        self.unbind_all("<Key>")
        self.unbind_all("<Return>")
        self.unbind_all("<KP_Enter>")
        self.unbind_all("<Escape>")
        self.unbind_all("<BackSpace>")
        self.unbind_all("<Delete>")

    def _tecla_presionada(self, event):

        tecla = event.keysym
        caracter = event.char

        permitidos = (
            "0123456789"
            "+-*/().%"
        )

        if caracter in permitidos:

            self._agregar(
                caracter
            )

            return "break"

        # Teclado numérico
        mapa = {
            "KP_Add": "+",
            "KP_Subtract": "-",
            "KP_Multiply": "*",
            "KP_Divide": "/",
            "KP_Decimal": ".",
        }

        if tecla in mapa:

            self._agregar(
                mapa[tecla]
            )

            return "break"

        return None

    def _tecla_enter(self, event=None):

        self.click_boton("=")

        return "break"

    def _tecla_escape(self, event=None):

        self.click_boton("C")

        return "break"

    def _tecla_backspace(self, event=None):

        self.click_boton("⌫")

        return "break"

    def _tecla_delete(self, event=None):

        self.click_boton("C")

        return "break"

    def _agregar(self, caracter):

        # Si había un error, empezar de nuevo
        if self.expresion == "Error":
            self.expresion = ""

        self.expresion += caracter

        self._actualizar_display()

    def click_boton(self, texto):

        if texto == "C":
            self.expresion = ""

        elif texto == "⌫":
            self.expresion = (
                self.expresion[:-1]
            )

        elif texto == "=":
            self._calcular()
            return

        elif texto == "±":
            self._cambiar_signo()
        elif texto == "%":

            self._porcentaje()

        else:
            self._agregar(
                texto
            )

            return

        self._actualizar_display()

    def _calcular(self):

        if not self.expresion:
            return

        try:

            resultado = EvaluadorMatematico.evaluar(
                self.expresion
            )

            self.expresion = (
                self._formatear_resultado(
                    resultado
                )
            )

        except (
            ValueError,
            ZeroDivisionError,
            OverflowError
        ):

            self.expresion = "Error"

        self._actualizar_display()

    def _formatear_resultado(
        self,
        resultado
    ):

        if isinstance(
            resultado,
            float
        ):

            if resultado.is_integer():

                return str(
                    int(resultado)
                )

            return f"{resultado:.10g}"

        return str(resultado)

    def _cambiar_signo(self):

        if not self.expresion:
            return

        if self.expresion == "Error":

            self.expresion = ""

            return

        # Si solamente tenemos un número
        try:

            valor = float(
                self.expresion
            )

            self.expresion = (
                self._formatear_resultado(
                    -valor
                )
            )

            return

        except ValueError:
            pass

        # Si tenemos una expresión completa
        if (
            self.expresion.startswith("-(")
            and self.expresion.endswith(")")
        ):

            self.expresion = (
                self.expresion[2:-1]
            )

        else:

            self.expresion = (
                "-("
                + self.expresion
                + ")"
            )

    # ======================================================
    # PORCENTAJE
    # ======================================================

    def _porcentaje(self):

        if not self.expresion:
            return

        if self.expresion == "Error":

            self.expresion = ""

            return

        import re

        coincidencias = list(
            re.finditer(
                r"(\d+(?:\.\d+)?)$",
                self.expresion
            )
        )

        if not coincidencias:
            return

        match = coincidencias[-1]

        numero = float(
            match.group(1)
        )

        porcentaje = numero / 100

        reemplazo = (
            self._formatear_resultado(
                porcentaje
            )
        )

        self.expresion = (
            self.expresion[:match.start()]
            + reemplazo
        )

    def _actualizar_display(self):

        self.display.delete(
            0,
            "end"
        )

        self.display.insert(
            0,
            self.expresion
        )

        self.display.icursor(
            "end"
        )
    def _enfocar_display(self):

        try:

            self.display.focus_set()

        except tk.TclError:

            pass

    def _aplicar_tema(
        self,
        paleta
    ):

        p = paleta

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
                    activebackground=p["accent_hover"],
                    activeforeground="#ffffff"
                )


            elif texto in (
                "/",
                "*",
                "-",
                "+",
                "%",
                "±",
                "(",
                ")",
                "C",
                "⌫"
            ):

                btn.configure(
                    bg=p["bg_secundario"],
                    fg=p["accent"],
                    activebackground=p["accent_suave"],
                    activeforeground=p["accent"]
                )


            else:

                btn.configure(
                    bg=p["bg_secundario"],
                    fg=p["fg"],
                    activebackground=p["accent_suave"],
                    activeforeground=p["fg"]
                )



class CalculadoraFrame(tk.Frame):
    """
    Contenedor principal de la calculadora.

    Pestañas:
        Básica
        Matrices
        Conjuntos
    """

    TABS: ClassVar[
        tuple[tuple[str, str], ...]
    ] = (
        ("basica", "Básica"),
        ("matrices", "Matrices"),
        ("conjuntos", "Conjuntos"),
        ("calculo", "Cálculo"),
    )

    def __init__(
        self,
        parent,
        theme_manager
    ):

        super().__init__(parent)

        self.theme_manager = theme_manager

        self.tab_actual = 0


        self.barra_tabs = tk.Frame(
            self
        )

        self.barra_tabs.pack(
            fill="x",
            side="top"
        )

        self.botones_tabs = {}
        self.indicadores_tabs = {}

        self.contenedor = tk.Frame(
            self
        )

        self.contenedor.pack(
            fill="both",
            expand=True
        )


        self.basica_tab = BasicaFrame(
            self.contenedor,
            theme_manager
        )

        self.matrices_tab = MatricesFrame(
            self.contenedor,
            theme_manager
        )

        self.conjuntos_tab = ConjuntosFrame(
            self.contenedor,
            theme_manager
        )
        self.calculo_tab = CalculoFrame(
            self.contenedor,
            theme_manager
        )

        self.contenidos = [
            self.basica_tab,
            self.matrices_tab,
            self.conjuntos_tab,
            self.calculo_tab
        ]


        for indice, (tipo, texto) in enumerate(
            self.TABS
        ):

            contenedor_tab = tk.Frame(
                self.barra_tabs
            )

            contenedor_tab.pack(
                side="left",
                padx=(
                    8 if indice == 0 else 0,
                    0
                )
            )

            boton = tk.Button(
                contenedor_tab,
                text=texto,
                font=("Arial", 10),
                relief="flat",
                bd=0,
                borderwidth=0,
                highlightthickness=0,
                cursor="hand2",
                padx=16,
                pady=10,
                command=lambda i=indice:
                    self._seleccionar_tab(i)
            )

            boton.pack(
                side="top"
            )

            # Línea inferior que indica la pestaña activa
            indicador = tk.Frame(
                contenedor_tab,
                height=2
            )

            indicador.pack(
                fill="x",
                side="bottom"
            )

            self.botones_tabs[tipo] = boton
            self.indicadores_tabs[tipo] = indicador

 
        theme_manager.registrar(
            self._aplicar_tema
        )

        self._seleccionar_tab(
            0
        )

 
    def _seleccionar_tab(
        self,
        indice
    ):

        if (
            indice < 0
            or indice >= len(self.contenidos)
        ):
            return

        self.tab_actual = indice

        # Ocultar todas
        for contenido in self.contenidos:

            contenido.pack_forget()

        # Mostrar la seleccionada
        self.contenidos[indice].pack(
            fill="both",
            expand=True
        )

        p = self.theme_manager.paleta

        # Actualizar apariencia de tabs
        for i, (tipo, _texto) in enumerate(
            self.TABS
        ):

            boton = self.botones_tabs[tipo]
            indicador = self.indicadores_tabs[tipo]

            if i == indice:

                # Pestaña seleccionada
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

                # Pestaña normal
                boton.configure(
                    bg=p["bg"],
                    fg=p["fg_suave"],
                    activebackground=p["bg"],
                    activeforeground=p["fg"]
                )

                indicador.configure(
                    bg=p["bg"]
                )


    def _aplicar_tema(
        self,
        paleta
    ):

        p = paleta

        self.configure(
            bg=p["bg"]
        )

        self.barra_tabs.configure(
            bg=p["bg"]
        )

        self.contenedor.configure(
            bg=p["bg"]
        )

        self._seleccionar_tab(
            self.tab_actual
        )
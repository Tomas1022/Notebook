import math
import tkinter as tk
from tkinter import ttk, messagebox

try:
    import sympy as sp
    from sympy.parsing.sympy_parser import (
        parse_expr,
        standard_transformations,
        implicit_multiplication_application,
        convert_xor,
    )
    SYMPY_DISPONIBLE = True
except ImportError:
    SYMPY_DISPONIBLE = False

try:
    import matplotlib
    matplotlib.use("TkAgg")
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    import numpy as np
    MATPLOTLIB_DISPONIBLE = True
except ImportError:
    MATPLOTLIB_DISPONIBLE = False


if SYMPY_DISPONIBLE:
    X = sp.symbols("x")
    TRANSFORMACIONES = standard_transformations + (
        implicit_multiplication_application,
        convert_xor,
    )


def parsear_funcion(texto):
    texto = texto.strip()

    if not texto:
        raise ValueError(
            "Escribe una funcion, por ejemplo: x^2 + 3x"
        )

    reemplazos = {
        "infinito": "oo",
        "inf": "oo",
        "-infinito": "-oo",
    }

    texto_normalizado = texto

    for viejo, nuevo in reemplazos.items():
        texto_normalizado = texto_normalizado.replace(
            viejo,
            nuevo
        )

    try:
        expr = parse_expr(
            texto_normalizado,
            transformations=TRANSFORMACIONES,
            local_dict={"x": X}
        )
    except Exception as error:
        raise ValueError(
            f"No se pudo interpretar la funcion: {error}"
        )

    return expr


def parsear_valor(texto):
    texto = (
        texto
        .strip()
        .replace("infinito", "oo")
        .replace("inf", "oo")
    )

    if not texto:
        raise ValueError("Debes indicar un valor.")

    try:
        return parse_expr(
            texto,
            transformations=TRANSFORMACIONES
        )
    except Exception as error:
        raise ValueError(
            f"Valor invalido: {error}"
        )


def calcular_derivada(expr, orden=1):
    pasos = [
        f"f(x) = {expr}"
    ]

    resultado = expr

    for i in range(orden):
        resultado = sp.diff(
            resultado,
            X
        )

        etiqueta = (
            "f'(x)"
            if orden == 1
            else f"derivada #{i + 1}"
        )

        pasos.append(
            f"{etiqueta} = {resultado}"
        )

    simplificado = sp.simplify(
        resultado
    )

    if simplificado != resultado:
        pasos.append(
            f"Simplificando -> {simplificado}"
        )

    return simplificado, pasos


def calcular_limite(expr, punto, direccion="Ambos"):
    pasos = [
        f"f(x) = {expr}",
        f"Limite cuando x -> {punto}"
    ]

    mapa_direccion = {
        "Ambos": "+-",
        "Izquierda": "-",
        "Derecha": "+"
    }

    resultado = sp.limit(
        expr,
        X,
        punto,
        dir=mapa_direccion.get(
            direccion,
            "+-"
        )
    )

    pasos.append(
        f"Resultado = {resultado}"
    )

    return resultado, pasos


def calcular_integral(
    expr,
    definida=False,
    a=None,
    b=None
):
    pasos = [
        f"f(x) = {expr}"
    ]

    if not definida:
        resultado = sp.integrate(
            expr,
            X
        )

        pasos.append(
            "Integral indefinida:"
        )

        pasos.append(
            f"F(x) = {resultado} + C"
        )

        return resultado, pasos

    pasos.append(
        f"Integral definida entre x = {a} y x = {b}"
    )

    resultado = sp.integrate(
        expr,
        (X, a, b)
    )

    pasos.append(
        f"Resultado = {resultado}"
    )

    try:
        valor_decimal = float(resultado)

        pasos.append(
            f"Valor decimal ~ {valor_decimal:.6g}"
        )
    except (TypeError, ValueError):
        pass

    return resultado, pasos


def evaluar_funcion(expr, valor):
    pasos = [
        f"f(x) = {expr}",
        f"Sustituyendo x = {valor}"
    ]

    resultado = sp.simplify(
        expr.subs(
            X,
            valor
        )
    )

    pasos.append(
        f"f({valor}) = {resultado}"
    )

    try:
        valor_decimal = float(resultado)

        pasos.append(
            f"Valor decimal ~ {valor_decimal:.6g}"
        )
    except (TypeError, ValueError):
        pass

    return resultado, pasos


def _fmt_num(x):
    """Formatea un numero para mostrarlo en la grafica (sin decimales largos)."""
    if abs(x - round(x)) < 1e-9:
        return str(int(round(x)))
    return f"{x:.4g}"


def _generar_puntos(expr, x_min, x_max, n=400):
    """
    Convierte una expresion sympy en puntos (xs, ys) numericos para graficar,
    usando numpy para que sea rapido. Los valores donde la funcion no esta
    definida (raiz de negativo, division por cero, etc.) quedan como NaN,
    asi matplotlib simplemente corta la curva ahi en vez de fallar.
    """
    f_num = sp.lambdify(X, expr, modules=["numpy"])
    xs = np.linspace(x_min, x_max, n)
    ys = np.full(n, np.nan)

    with np.errstate(all="ignore"):
        try:
            resultado = f_num(xs)
            resultado = np.broadcast_to(np.asarray(resultado, dtype=complex), xs.shape).copy()
            reales = np.isclose(resultado.imag, 0, atol=1e-9)
            ys = np.where(reales, resultado.real, np.nan)
        except Exception:
            for i, xv in enumerate(xs):
                try:
                    val = complex(f_num(xv))
                    if abs(val.imag) < 1e-9:
                        ys[i] = val.real
                except Exception:
                    pass

    return xs, ys


class CalculoFrame(tk.Frame):
    OPERACIONES = [
        "Derivada",
        "Límite",
        "Integral",
        "Evaluar en un punto"
    ]

    def __init__(
        self,
        parent,
        theme_manager,
        historial=None
    ):
        super().__init__(parent)

        self.theme_manager = theme_manager
        self.historial = historial

        # Datos del ultimo calculo exitoso (para poder graficarlo despues)
        self._ultima_expr = None
        self._ultimo_resultado = None
        self._ultima_operacion = None
        self._ultimos_datos = None

        if not SYMPY_DISPONIBLE:
            self.label_error = tk.Label(
                self,
                text=(
                    "Falta instalar 'sympy' para usar esta pestaña.\n\n"
                    "Ejecuta en tu terminal:\n"
                    "    pip install sympy"
                ),
                font=("Arial", 11),
                justify="center"
            )

            self.label_error.pack(
                expand=True
            )

            theme_manager.registrar(
                self._aplicar_tema_error
            )

            return

        self.fila_funcion = tk.Frame(
            self
        )

        self.fila_funcion.pack(
            fill="x",
            padx=14,
            pady=(14, 6)
        )

        self.label_funcion = tk.Label(
            self.fila_funcion,
            text="f(x) ="
        )

        self.label_funcion.pack(
            side="left"
        )

        self.entry_funcion = tk.Entry(
            self.fila_funcion,
            bd=0,
            relief="flat"
        )

        self.entry_funcion.pack(
            side="left",
            fill="x",
            expand=True,
            padx=8
        )

        self.entry_funcion.insert(
            0,
            "x^2 + 3x"
        )

        self.entry_funcion.bind(
            "<Return>",
            lambda event: self.calcular()
        )

        self.entry_funcion.bind(
            "<KeyRelease>",
            lambda event: self._invalidar_grafica()
        )

        self.fila_operacion = tk.Frame(
            self
        )

        self.fila_operacion.pack(
            fill="x",
            padx=14,
            pady=6
        )

        self.label_operacion = tk.Label(
            self.fila_operacion,
            text="Operación:"
        )

        self.label_operacion.pack(
            side="left"
        )

        self.combo_operacion = ttk.Combobox(
            self.fila_operacion,
            state="readonly",
            values=self.OPERACIONES
        )

        self.combo_operacion.current(0)

        self.combo_operacion.pack(
            side="left",
            padx=8
        )

        self.combo_operacion.bind(
            "<<ComboboxSelected>>",
            self._cambiar_operacion
        )

        self.frame_extra = tk.Frame(
            self
        )

        self.frame_extra.pack(
            fill="x",
            padx=14,
            pady=6
        )

        self._crear_campos_derivada()
        self._crear_campos_limite()
        self._crear_campos_integral()
        self._crear_campos_evaluar()

        self.btn_calcular = tk.Button(
            self,
            text="Calcular",
            relief="flat",
            bd=0,
            cursor="hand2",
            command=self.calcular
        )

        self.btn_calcular.pack(
            padx=14,
            pady=6,
            anchor="w"
        )

        # Boton para ver la grafica -- se crea aca pero NO se empaqueta

        self.btn_graficar = tk.Button(
            self,
            text="📈 Ver gráfica",
            relief="flat",
            bd=0,
            cursor="hand2",
            command=self._abrir_grafica
        )

        self.label_resultado = tk.Label(
            self,
            text="Resultado:"
        )

        self.label_resultado.pack(
            anchor="w",
            padx=14
        )

        self.text_resultado = tk.Text(
            self,
            height=3,
            font=("Consolas", 12),
            bd=0
        )

        self.text_resultado.pack(
            fill="x",
            padx=14,
            pady=(0, 10)
        )

        self.label_proceso = tk.Label(
            self,
            text="Proceso:"
        )

        self.label_proceso.pack(
            anchor="w",
            padx=14
        )

        self.text_proceso = tk.Text(
            self,
            font=("Consolas", 10),
            bd=0
        )

        self.text_proceso.pack(
            fill="both",
            expand=True,
            padx=14,
            pady=(0, 14)
        )

        self._cambiar_operacion()

        theme_manager.registrar(
            self._aplicar_tema
        )

    def _crear_campos_derivada(self):
        self.frame_derivada = tk.Frame(
            self.frame_extra
        )

        self.label_orden = tk.Label(
            self.frame_derivada,
            text="Orden:"
        )

        self.label_orden.pack(
            side="left"
        )

        self.spin_orden = tk.Spinbox(
            self.frame_derivada,
            from_=1,
            to=5,
            width=3,
            command=self._invalidar_grafica
        )

        self.spin_orden.bind(
            "<KeyRelease>",
            lambda event: self._invalidar_grafica()
        )

        self.spin_orden.pack(
            side="left",
            padx=6
        )

    def _crear_campos_limite(self):
        self.frame_limite = tk.Frame(
            self.frame_extra
        )

        self.label_tiende_a = tk.Label(
            self.frame_limite,
            text="x tiende a:"
        )

        self.label_tiende_a.pack(
            side="left"
        )

        self.entry_punto_limite = tk.Entry(
            self.frame_limite,
            width=10,
            bd=0,
            relief="flat"
        )

        self.entry_punto_limite.insert(
            0,
            "0"
        )

        self.entry_punto_limite.bind(
            "<KeyRelease>",
            lambda event: self._invalidar_grafica()
        )

        self.entry_punto_limite.pack(
            side="left",
            padx=6
        )

        self.label_direccion = tk.Label(
            self.frame_limite,
            text="Dirección:"
        )

        self.label_direccion.pack(
            side="left",
            padx=(12, 0)
        )

        self.combo_direccion = ttk.Combobox(
            self.frame_limite,
            state="readonly",
            values=[
                "Ambos",
                "Izquierda",
                "Derecha"
            ],
            width=10
        )

        self.combo_direccion.current(0)

        self.combo_direccion.bind(
            "<<ComboboxSelected>>",
            lambda event: self._invalidar_grafica()
        )

        self.combo_direccion.pack(
            side="left",
            padx=6
        )

    def _crear_campos_integral(self):
        self.frame_integral = tk.Frame(
            self.frame_extra
        )

        self.tipo_integral = tk.StringVar(
            value="Indefinida"
        )

        self.radio_indefinida = tk.Radiobutton(
            self.frame_integral,
            text="Indefinida",
            variable=self.tipo_integral,
            value="Indefinida",
            command=self._actualizar_campos_integral,
            bd=0
        )

        self.radio_definida = tk.Radiobutton(
            self.frame_integral,
            text="Definida",
            variable=self.tipo_integral,
            value="Definida",
            command=self._actualizar_campos_integral,
            bd=0
        )

        self.radio_indefinida.pack(
            side="left"
        )

        self.radio_definida.pack(
            side="left",
            padx=(10, 0)
        )

        self.label_a = tk.Label(
            self.frame_integral,
            text="  a:"
        )

        self.entry_a = tk.Entry(
            self.frame_integral,
            width=6,
            bd=0,
            relief="flat"
        )

        self.entry_a.insert(
            0,
            "0"
        )

        self.entry_a.bind(
            "<KeyRelease>",
            lambda event: self._invalidar_grafica()
        )

        self.label_b = tk.Label(
            self.frame_integral,
            text="b:"
        )

        self.entry_b = tk.Entry(
            self.frame_integral,
            width=6,
            bd=0,
            relief="flat"
        )

        self.entry_b.insert(
            0,
            "1"
        )

        self.entry_b.bind(
            "<KeyRelease>",
            lambda event: self._invalidar_grafica()
        )

    def _actualizar_campos_integral(self):
        if self.tipo_integral.get() == "Definida":
            self.label_a.pack(
                side="left"
            )

            self.entry_a.pack(
                side="left",
                padx=4
            )

            self.label_b.pack(
                side="left"
            )

            self.entry_b.pack(
                side="left",
                padx=4
            )

        else:
            for widget in (
                self.label_a,
                self.entry_a,
                self.label_b,
                self.entry_b
            ):
                widget.pack_forget()

        self._invalidar_grafica()

    def _crear_campos_evaluar(self):
        self.frame_evaluar = tk.Frame(
            self.frame_extra
        )

        self.label_valor_x = tk.Label(
            self.frame_evaluar,
            text="x ="
        )

        self.label_valor_x.pack(
            side="left"
        )

        self.entry_valor_x = tk.Entry(
            self.frame_evaluar,
            width=10,
            bd=0,
            relief="flat"
        )

        self.entry_valor_x.insert(
            0,
            "1"
        )

        self.entry_valor_x.bind(
            "<KeyRelease>",
            lambda event: self._invalidar_grafica()
        )

        self.entry_valor_x.pack(
            side="left",
            padx=6
        )

    def _cambiar_operacion(self, event=None):
        for frame in (
            self.frame_derivada,
            self.frame_limite,
            self.frame_integral,
            self.frame_evaluar
        ):
            frame.pack_forget()

        op = self.combo_operacion.get()

        if op == "Derivada":
            self.frame_derivada.pack(
                fill="x"
            )

        elif op == "Límite":
            self.frame_limite.pack(
                fill="x"
            )

        elif op == "Integral":
            self.frame_integral.pack(
                fill="x"
            )

            self._actualizar_campos_integral()

        else:
            self.frame_evaluar.pack(
                fill="x"
            )

        self._invalidar_grafica()

    def calcular(self):
        try:
            expr = parsear_funcion(
                self.entry_funcion.get()
            )

            op = self.combo_operacion.get()

            datos = {
                "funcion": str(expr)
            }

            if op == "Derivada":
                orden = int(
                    self.spin_orden.get()
                )

                resultado, pasos = calcular_derivada(
                    expr,
                    orden
                )

                datos["orden"] = orden

            elif op == "Límite":
                punto = parsear_valor(
                    self.entry_punto_limite.get()
                )

                direccion = self.combo_direccion.get()

                resultado, pasos = calcular_limite(
                    expr,
                    punto,
                    direccion
                )

                datos["punto"] = str(punto)
                datos["direccion"] = direccion

            elif op == "Integral":
                if self.tipo_integral.get() == "Definida":
                    a = parsear_valor(
                        self.entry_a.get()
                    )

                    b = parsear_valor(
                        self.entry_b.get()
                    )

                    resultado, pasos = calcular_integral(
                        expr,
                        definida=True,
                        a=a,
                        b=b
                    )

                    datos["tipo"] = "Definida"
                    datos["a"] = str(a)
                    datos["b"] = str(b)

                else:
                    resultado, pasos = calcular_integral(
                        expr,
                        definida=False
                    )

                    datos["tipo"] = "Indefinida"

            else:
                valor = parsear_valor(
                    self.entry_valor_x.get()
                )

                resultado, pasos = evaluar_funcion(
                    expr,
                    valor
                )

                datos["valor"] = str(valor)

            resultado_texto = str(
                sp.simplify(resultado)
            )

            self.text_resultado.delete(
                "1.0",
                "end"
            )

            self.text_proceso.delete(
                "1.0",
                "end"
            )

            self.text_resultado.insert(
                "1.0",
                resultado_texto
            )

            self.text_proceso.insert(
                "1.0",
                "\n".join(pasos)
            )

            if self.historial:
                self.historial.registrar(
                    "Cálculo",
                    op,
                    datos,
                    resultado_texto,
                    pasos
                )

            # Muestra boton despues de un calculo exitoso, y guarda los datos para poder graficar

            self._ultima_expr = expr
            self._ultimo_resultado = resultado
            self._ultima_operacion = op
            self._ultimos_datos = datos

            self._mostrar_boton_graficar(op, datos)

        except ValueError as error:
            self._invalidar_grafica()

            messagebox.showerror(
                "Error",
                str(error)
            )

        except Exception as error:
            self._invalidar_grafica()

            messagebox.showerror(
                "Error",
                f"No se pudo calcular: {error}"
            )

    # Grafica

    def _texto_boton_grafica(self, op, datos):
        if op == "Derivada":
            return "📈 Ver gráfica de f(x) y f'(x)"
        if op == "Límite":
            return "📈 Ver gráfica cerca del punto"
        if op == "Integral" and datos.get("tipo") == "Definida":
            return "📈 Ver gráfica y área"
        if op == "Integral":
            return "📈 Ver gráfica"
        if op == "Evaluar en un punto":
            return "📈 Ver gráfica con el punto"
        return "📈 Ver gráfica"

    def _mostrar_boton_graficar(self, op, datos):
        self.btn_graficar.configure(
            text=self._texto_boton_grafica(op, datos)
        )

        if not self.btn_graficar.winfo_ismapped():
            self.btn_graficar.pack(
                padx=14,
                pady=(0, 6),
                anchor="w",
                before=self.label_resultado
            )

        p = getattr(self, "paleta", None)
        if p:
            self.btn_graficar.configure(
                bg=p["bg_secundario"],
                fg=p["accent"],
                activebackground=p["accent_suave"],
                activeforeground=p["accent"]
            )

    def _invalidar_grafica(self):
        """Se llama cuando el usuario cambia algo despues de calcular,
        para que no pueda graficar un resultado que ya no corresponde."""
        if hasattr(self, "btn_graficar") and self.btn_graficar.winfo_ismapped():
            self.btn_graficar.pack_forget()

        self._ultima_expr = None

    def _rango_para_operacion(self):
        op = self._ultima_operacion
        datos = self._ultimos_datos

        try:
            if op == "Evaluar en un punto":
                v = float(sp.N(sp.sympify(datos["valor"])))
                return v - 6, v + 6

            if op == "Límite":
                p_val = sp.sympify(datos["punto"])
                if p_val.is_finite:
                    v = float(p_val)
                    return v - 6, v + 6

            if op == "Integral" and datos.get("tipo") == "Definida":
                a = float(sp.N(sp.sympify(datos["a"])))
                b = float(sp.N(sp.sympify(datos["b"])))
                margen = max(1.0, abs(b - a) * 0.3)
                return min(a, b) - margen, max(a, b) + margen

        except Exception:
            pass

        return -10.0, 10.0

    def _construir_figura(self):
        p = self.theme_manager.paleta
        x_min, x_max = self._rango_para_operacion()

        fig = Figure(figsize=(6.4, 4.8), dpi=100)
        fig.patch.set_facecolor(p["bg"])
        ax = fig.add_subplot(111)
        ax.set_facecolor(p["bg_secundario"])

        xs, ys = _generar_puntos(self._ultima_expr, x_min, x_max)

        if np.all(np.isnan(ys)):
            ax.text(
                0.5, 0.5,
                "No se pudo graficar esta función\nen el rango mostrado.",
                ha="center", va="center", color=p["fg"], transform=ax.transAxes
            )
        else:
            ax.plot(xs, ys, color=p["accent"], linewidth=2, label="f(x)")

        op = self._ultima_operacion
        datos = self._ultimos_datos

        if op == "Evaluar en un punto":
            try:
                v = float(sp.N(sp.sympify(datos["valor"])))
                fv = float(sp.N(self._ultima_expr.subs(X, v)))
                ax.plot([v], [fv], "o", color="#ff4d4d", markersize=8, zorder=5)
                ax.annotate(
                    f"({_fmt_num(v)}, {_fmt_num(fv)})", (v, fv),
                    textcoords="offset points", xytext=(8, 8), color=p["fg"]
                )
            except Exception:
                pass

        elif op == "Derivada":
            try:
                xs_d, ys_d = _generar_puntos(self._ultimo_resultado, x_min, x_max)
                etiqueta_d = "f'(x)" if datos.get("orden", 1) == 1 else f"derivada orden {datos.get('orden')}"
                ax.plot(xs_d, ys_d, color="#ff8a3d", linewidth=2, linestyle="--", label=etiqueta_d)

                if datos.get("orden", 1) == 1:
                    for candidato in (1, 2, -1, 0.5, 3, -2):
                        try:
                            y0 = float(sp.N(self._ultima_expr.subs(X, candidato)))
                            m = float(sp.N(self._ultimo_resultado.subs(X, candidato)))
                            if math.isfinite(y0) and math.isfinite(m):
                                xs_t = np.array([x_min, x_max])
                                ys_t = m * (xs_t - candidato) + y0
                                ax.plot(
                                    xs_t, ys_t, color="#4caf75", linestyle=":", linewidth=1.5,
                                    label=f"tangente en x={_fmt_num(candidato)}"
                                )
                                ax.plot([candidato], [y0], "o", color="#4caf75", markersize=6)
                                break
                        except Exception:
                            continue
            except Exception:
                pass

        elif op == "Límite":
            try:
                p_val = sp.sympify(datos["punto"])
                if p_val.is_finite:
                    v = float(p_val)
                    ax.axvline(v, color="#ff4d4d", linestyle="--", linewidth=1.5, label=f"x = {_fmt_num(v)}")
            except Exception:
                pass

        elif op == "Integral" and datos.get("tipo") == "Definida":
            try:
                a = float(sp.N(sp.sympify(datos["a"])))
                b = float(sp.N(sp.sympify(datos["b"])))
                xs_area, ys_area = _generar_puntos(self._ultima_expr, min(a, b), max(a, b), 200)
                ax.fill_between(
                    xs_area, ys_area, 0, color=p["accent"], alpha=0.3,
                    label=f"Área entre {_fmt_num(a)} y {_fmt_num(b)}"
                )
            except Exception:
                pass

        ax.axhline(0, color=p["borde"], linewidth=1)
        ax.axvline(0, color=p["borde"], linewidth=1)
        ax.grid(True, color=p["borde"], alpha=0.3)
        ax.tick_params(colors=p["fg"])

        for spine in ax.spines.values():
            spine.set_color(p["borde"])

        ax.set_title(f"f(x) = {self._ultima_expr}", color=p["fg"])

        if ax.get_legend_handles_labels()[0]:
            ax.legend(
                facecolor=p["bg_secundario"], edgecolor=p["borde"],
                labelcolor=p["fg"], fontsize=9
            )

        fig.tight_layout()
        return fig

    def _abrir_grafica(self):
        if not MATPLOTLIB_DISPONIBLE:
            messagebox.showwarning(
                "Falta matplotlib",
                "Instala matplotlib para ver gráficas:\n    pip install matplotlib numpy"
            )
            return

        if self._ultima_expr is None:
            messagebox.showinfo("Sin datos", "Primero presiona Calcular.")
            return

        p = self.theme_manager.paleta

        popup = tk.Toplevel(self)
        popup.title(f"Gráfica de f(x) = {self._ultima_expr}")
        popup.configure(bg=p["bg"])
        popup.geometry("680x560")

        fig = self._construir_figura()

        canvas = FigureCanvasTkAgg(fig, master=popup)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

    #tema

    def _aplicar_tema_error(self, paleta):
        self.configure(
            bg=paleta["bg"]
        )

        self.label_error.configure(
            bg=paleta["bg"],
            fg=paleta["fg"]
        )

    def _aplicar_tema(self, paleta):
        self.paleta = paleta
        p = paleta

        for frame in (
            self,
            self.fila_funcion,
            self.fila_operacion,
            self.frame_extra,
            self.frame_derivada,
            self.frame_limite,
            self.frame_integral,
            self.frame_evaluar
        ):
            frame.configure(
                bg=p["bg"]
            )

        for label in (
            self.label_funcion,
            self.label_operacion,
            self.label_orden,
            self.label_tiende_a,
            self.label_direccion,
            self.label_a,
            self.label_b,
            self.label_valor_x,
            self.label_resultado,
            self.label_proceso
        ):
            label.configure(
                bg=p["bg"],
                fg=p["fg"]
            )

        for radio in (
            self.radio_indefinida,
            self.radio_definida
        ):
            radio.configure(
                bg=p["bg"],
                fg=p["fg"],
                selectcolor=p["bg_secundario"],
                activebackground=p["bg"],
                activeforeground=p["fg"]
            )

        for entry in (
            self.entry_funcion,
            self.entry_punto_limite,
            self.entry_a,
            self.entry_b,
            self.entry_valor_x,
            self.spin_orden
        ):
            entry.configure(
                bg=p["bg_secundario"],
                fg=p["fg"],
                insertbackground=p["fg"],
                highlightthickness=1,
                highlightbackground=p["borde"],
                highlightcolor=p["accent"]
            )

        self.btn_calcular.configure(
            bg=p["accent"],
            fg="#ffffff",
            activebackground=p["accent_hover"],
            activeforeground="#ffffff"
        )

        self.btn_graficar.configure(
            bg=p["bg_secundario"],
            fg=p["accent"],
            activebackground=p["accent_suave"],
            activeforeground=p["accent"]
        )

        for text_widget in (
            self.text_resultado,
            self.text_proceso
        ):
            text_widget.configure(
                bg=p["bg_secundario"],
                fg=p["fg"],
                insertbackground=p["fg"],
                highlightthickness=1,
                highlightbackground=p["borde"],
                highlightcolor=p["accent"]
            )
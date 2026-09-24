import tkinter as tk
from tkinter import ttk, messagebox
import math


def mcd_euclides(a, b):
    """Calcula mcd(a, b) con el algoritmo de Euclides. Devuelve (mcd, pasos)."""
    a, b = abs(int(a)), abs(int(b))

    if a < b:
        a, b = b, a  # siempre empezamos dividiendo el mayor entre el menor

    pasos = [f"mcd({a}, {b}):"]

    if b == 0:
        pasos.append(f"  mcd = {a}")
        return a, pasos

    while b != 0:
        q = a // b
        r = a % b
        pasos.append(f"  {a} = {q} x {b} + {r}")
        a, b = b, r

    pasos.append(f"  mcd = {a}")
    return a, pasos


def calcular_mcd(numeros):
    """MCD de una lista de 2 o mas numeros, reduciendo de a pares."""
    numeros = [abs(int(n)) for n in numeros]

    if len(numeros) < 2:
        return None, ["Error: ingresa al menos 2 numeros separados por comas."]

    resultado = numeros[0]
    pasos = []

    for i in range(1, len(numeros)):
        _, sub_pasos = mcd_euclides(resultado, numeros[i])
        pasos.extend(sub_pasos)
        resultado, _ = mcd_euclides(resultado, numeros[i])
        pasos.append("")

    pasos.append(f"Resultado final: mcd = {resultado}")
    return resultado, pasos


def calcular_mcm(numeros):
    """MCM de una lista de 2 o mas numeros, usando mcm(a,b) = |a*b| / mcd(a,b)."""
    numeros = [abs(int(n)) for n in numeros]

    if len(numeros) < 2:
        return None, ["Error: ingresa al menos 2 numeros separados por comas."]

    resultado = numeros[0]
    pasos = []

    for i in range(1, len(numeros)):
        b = numeros[i]
        mcd_val, sub_pasos = mcd_euclides(resultado, b)
        pasos.extend(sub_pasos)

        nuevo = abs(resultado * b) // mcd_val
        pasos.append(
            f"  mcm({resultado}, {b}) = ({resultado} x {b}) / {mcd_val} = {nuevo}"
        )
        pasos.append("")
        resultado = nuevo

    pasos.append(f"Resultado final: mcm = {resultado}")
    return resultado, pasos


def calcular_pitagoras(numeros, hallar="hipotenusa"):
    if len(numeros) != 2:
        return None, ["Error: Ingresa exactamente 2 números separados por comas."]
    
    pasos = []
    if hallar == "hipotenusa":
        a, b = numeros
        c = math.sqrt(a**2 + b**2)
        pasos.append(f"Teorema de Pitágoras: c^2 = a^2 + b^2")
        pasos.append(f"c = \u221a({a}^2 + {b}^2)")
        pasos.append(f"c = \u221a({a**2:g} + {b**2:g})")
        pasos.append(f"c = \u221a({(a**2 + b**2):g})")
        pasos.append(f"Hipotenusa c = {c:.6g}")
        return round(c, 6), pasos
    else:
        h, c1 = numeros
        if h <= c1:
            return None, ["Error: La hipotenusa debe ser estrictamente mayor que el cateto."]
        c2 = math.sqrt(h**2 - c1**2)
        pasos.append(f"Teorema de Pitágoras: a^2 = c^2 - b^2")
        pasos.append(f"a = \u221a({h}^2 - {c1}^2)")
        pasos.append(f"a = \u221a({h**2:g} - {c1**2:g})")
        pasos.append(f"a = \u221a({(h**2 - c1**2):g})")
        pasos.append(f"Cateto a = {c2:.6g}")
        return round(c2, 6), pasos


def calcular_tales(numeros):
    if len(numeros) != 3:
        return None, ["Error: Ingresa exactamente 3 números (A, B, C) separados por comas."]
    a, b, c = numeros
    if a == 0:
        return None, ["Error: El valor de A no puede ser 0 (división por cero)."]
    
    x = (b * c) / a
    pasos = [
        "Teorema de Tales: A / B = C / X",
        f"{a:g} / {b:g} = {c:g} / X",
        f"X = ({b:g} * {c:g}) / {a:g}",
        f"X = {(b*c):g} / {a:g}",
        f"X = {x:.6g}"
    ]
    return round(x, 6), pasos


def grados_a_radianes(grados):
    rad = grados * (math.pi / 180)
    pasos = [
        "Conversión de grados a radianes:",
        "Radianes = Grados * (\u03c0 / 180)",
        f"Radianes = {grados:g} * (\u03c0 / 180)",
        f"Radianes = {rad:.6g} rad"
    ]
    return round(rad, 6), pasos


def radianes_a_grados(radianes):
    grados = radianes * (180 / math.pi)
    pasos = [
        "Conversión de radianes a grados:",
        "Grados = Radianes * (180 / \u03c0)",
        f"Grados = {radianes:g} * (180 / \u03c0)",
        f"Grados = {grados:.6g}\u00b0"
    ]
    return round(grados, 6), pasos


class AritmeticaFrame(tk.Frame):
    OPERACIONES = [
        "MCD (Maximo Comun Divisor)",
        "MCM (Minimo Comun Multiplo)",
        "Ambos (MCD y MCM)",
        "Pitágoras (Hallar Hipotenusa)",
        "Pitágoras (Hallar Cateto)",
        "Teorema de Tales (A/B = C/X)",
        "Grados a Radianes",
        "Radianes a Grados"
    ]

    def __init__(self, parent, theme_manager, historial=None):
        super().__init__(parent)
        self.theme_manager = theme_manager
        self.historial = historial

        self.entradas_frame = tk.Frame(self)
        self.entradas_frame.pack(fill="x", padx=14, pady=14)

        self.label_numeros = tk.Label(
            self.entradas_frame,
            text="Numeros (separados por comas):"
        )
        self.label_numeros.pack(side="left")

        self.entry_numeros = tk.Entry(
            self.entradas_frame, width=30, bd=0, relief="flat"
        )
        self.entry_numeros.insert(0, "12, 18, 24")
        self.entry_numeros.pack(side="left", padx=8)

        self.op_frame = tk.Frame(self)
        self.op_frame.pack(fill="x", padx=14, pady=(0, 14))

        self.label_operacion = tk.Label(self.op_frame, text="Operacion:")
        self.label_operacion.pack(side="left")

        self.combo_operacion = ttk.Combobox(
            self.op_frame, state="readonly",
            values=self.OPERACIONES,
            width=28
        )
        self.combo_operacion.current(0)
        self.combo_operacion.pack(side="left", padx=5)
        self.combo_operacion.bind("<<ComboboxSelected>>", self._actualizar_label)

        self.btn_calcular = tk.Button(
            self.op_frame, text="Calcular", relief="flat", bd=0,
            cursor="hand2", command=self.calcular
        )
        self.btn_calcular.pack(side="left", padx=10)

        self.label_resultado = tk.Label(self, text="Resultado:")
        self.label_resultado.pack(anchor="w", padx=14)
        self.text_resultado = tk.Text(self, height=3, font=("Consolas", 12), bd=0)
        self.text_resultado.pack(fill="x", padx=14, pady=(0, 10))

        self.label_proceso = tk.Label(self, text="Proceso (algoritmo de Euclides):")
        self.label_proceso.pack(anchor="w", padx=14)
        self.text_proceso = tk.Text(self, font=("Consolas", 10), bd=0)
        self.text_proceso.pack(fill="both", expand=True, padx=14, pady=(0, 14))

        theme_manager.registrar(self._aplicar_tema)

    def _actualizar_label(self, event=None):
        op = self.combo_operacion.get()
        if op.startswith("MCD") or op.startswith("MCM") or op.startswith("Ambos"):
            self.label_numeros.config(text="Numeros (separados por comas):")
            self.label_proceso.config(text="Proceso (algoritmo de Euclides):")
        elif op == "Pitágoras (Hallar Hipotenusa)":
            self.label_numeros.config(text="Cateto A, Cateto B:")
            self.label_proceso.config(text="Proceso (Teorema de Pitágoras):")
        elif op == "Pitágoras (Hallar Cateto)":
            self.label_numeros.config(text="Hipotenusa, Cateto:")
            self.label_proceso.config(text="Proceso (Teorema de Pitágoras):")
        elif op.startswith("Teorema de Tales"):
            self.label_numeros.config(text="Valores A, B, C:")
            self.label_proceso.config(text="Proceso (Teorema de Tales):")
        elif op == "Grados a Radianes":
            self.label_numeros.config(text="Ángulo en grados:")
            self.label_proceso.config(text="Proceso:")
        elif op == "Radianes a Grados":
            self.label_numeros.config(text="Ángulo en radianes:")
            self.label_proceso.config(text="Proceso:")

    def _leer_numeros(self):
        texto = self.entry_numeros.get()
        partes = [p.strip() for p in texto.split(",") if p.strip() != ""]
        # Convertimos a float para soportar decimales en Pitágoras/Tales/Ángulos
        return [float(p) for p in partes]

    def calcular(self):
        try:
            numeros = self._leer_numeros()
        except ValueError:
            messagebox.showerror("Error", "Ingresa solo numeros, separados por comas.")
            return

        if not numeros:
            messagebox.showerror("Error", "Ingresa al menos un valor.")
            return

        op = self.combo_operacion.get()

        if op.startswith("MCD") or op.startswith("MCM") or op.startswith("Ambos"):
            if len(numeros) < 2:
                messagebox.showerror("Error", "Ingresa al menos 2 numeros separados por comas.")
                return
            if op.startswith("MCD"):
                resultado_mcd, pasos_mcd = calcular_mcd(numeros)
                texto_resultado = f"mcd = {resultado_mcd}"
                pasos = pasos_mcd
            elif op.startswith("MCM"):
                resultado_mcm, pasos_mcm = calcular_mcm(numeros)
                texto_resultado = f"mcm = {resultado_mcm}"
                pasos = pasos_mcm
            else:  # Ambos
                resultado_mcd, pasos_mcd = calcular_mcd(numeros)
                resultado_mcm, pasos_mcm = calcular_mcm(numeros)
                texto_resultado = f"mcd = {resultado_mcd}      mcm = {resultado_mcm}"
                pasos = (
                    ["--- MCD ---"] + pasos_mcd
                    + [""] + ["--- MCM ---"] + pasos_mcm
                )

        elif op == "Pitágoras (Hallar Hipotenusa)":
            res, pasos = calcular_pitagoras(numeros, "hipotenusa")
            if res is None:
                messagebox.showerror("Error", pasos[0])
                return
            texto_resultado = f"Hipotenusa c = {res}"

        elif op == "Pitágoras (Hallar Cateto)":
            res, pasos = calcular_pitagoras(numeros, "cateto")
            if res is None:
                messagebox.showerror("Error", pasos[0])
                return
            texto_resultado = f"Cateto a = {res}"

        elif op.startswith("Teorema de Tales"):
            res, pasos = calcular_tales(numeros)
            if res is None:
                messagebox.showerror("Error", pasos[0])
                return
            texto_resultado = f"X = {res}"

        elif op == "Grados a Radianes":
            if len(numeros) != 1:
                messagebox.showerror("Error", "Ingresa exactamente 1 número.")
                return
            res, pasos = grados_a_radianes(numeros[0])
            texto_resultado = f"{res} rad"

        elif op == "Radianes a Grados":
            if len(numeros) != 1:
                messagebox.showerror("Error", "Ingresa exactamente 1 número.")
                return
            res, pasos = radianes_a_grados(numeros[0])
            texto_resultado = f"{res}\u00b0"

        self.text_resultado.delete("1.0", "end")
        self.text_proceso.delete("1.0", "end")
        self.text_resultado.insert("1.0", texto_resultado)
        self.text_proceso.insert("1.0", "\n".join(pasos))

        if self.historial:
            self.historial.registrar(
                "Aritmetica", op, {"entrada": self.entry_numeros.get()}, texto_resultado, pasos
            )

    def _aplicar_tema(self, p):
        self.paleta = p

        for frame in (self, self.entradas_frame, self.op_frame):
            frame.configure(bg=p["bg"])

        for label in (
            self.label_numeros, self.label_operacion,
            self.label_resultado, self.label_proceso
        ):
            label.configure(bg=p["bg"], fg=p["fg"])

        self.entry_numeros.configure(
            bg=p["bg_secundario"], fg=p["fg"], insertbackground=p["fg"],
            highlightthickness=1, highlightbackground=p["borde"], highlightcolor=p["accent"]
        )

        self.btn_calcular.configure(
            bg=p["accent"], fg="#ffffff", activebackground=p["accent_hover"]
        )

        for widget in (self.text_resultado, self.text_proceso):
            widget.configure(
                bg=p["bg_secundario"], fg=p["fg"], insertbackground=p["fg"],
                highlightthickness=1, highlightbackground=p["borde"], highlightcolor=p["accent"]
            )
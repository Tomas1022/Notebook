import tkinter as tk
from tkinter import ttk, messagebox


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


class AritmeticaFrame(tk.Frame):
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
            values=["MCD (Maximo Comun Divisor)", "MCM (Minimo Comun Multiplo)", "Ambos"]
        )
        self.combo_operacion.current(0)
        self.combo_operacion.pack(side="left", padx=5)

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

    def _leer_numeros(self):
        texto = self.entry_numeros.get()
        partes = [p.strip() for p in texto.split(",") if p.strip() != ""]
        return [int(p) for p in partes]

    def calcular(self):
        try:
            numeros = self._leer_numeros()
        except ValueError:
            messagebox.showerror("Error", "Ingresa solo numeros enteros, separados por comas.")
            return

        if len(numeros) < 2:
            messagebox.showerror("Error", "Ingresa al menos 2 numeros separados por comas.")
            return

        op = self.combo_operacion.get()

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

        self.text_resultado.delete("1.0", "end")
        self.text_proceso.delete("1.0", "end")
        self.text_resultado.insert("1.0", texto_resultado)
        self.text_proceso.insert("1.0", "\n".join(pasos))

        if self.historial:
            self.historial.registrar(
                "Aritmetica", op, {"numeros": numeros}, texto_resultado, pasos
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
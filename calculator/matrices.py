"""
Modulo de algebra lineal: matrices.
Cada funcion de calculo devuelve (resultado, pasos) donde pasos es una
lista de strings explicando el proceso, para mostrarla en el area de texto.
"""
import tkinter as tk
from tkinter import ttk, messagebox


def fmt(numero):
    if abs(numero - round(numero)) < 1e-9:
        return str(int(round(numero)))
    return f"{numero:.3f}"


def matriz_a_texto(m):
    return "\n".join("  ".join(fmt(v) for v in fila) for fila in m)


def sumar_restar(A, B, operacion):
    if len(A) != len(B) or len(A[0]) != len(B[0]):
        return None, ["Error: las matrices deben tener las mismas dimensiones."]

    pasos = ["Sumando elemento por elemento (misma posicion en A y B):" if operacion == "+"
             else "Restando elemento por elemento (misma posicion en A y B):"]
    resultado = []
    for i in range(len(A)):
        fila = []
        for j in range(len(A[0])):
            if operacion == "+":
                val = A[i][j] + B[i][j]
                pasos.append(f"  R[{i+1}][{j+1}] = {fmt(A[i][j])} + {fmt(B[i][j])} = {fmt(val)}")
            else:
                val = A[i][j] - B[i][j]
                pasos.append(f"  R[{i+1}][{j+1}] = {fmt(A[i][j])} - {fmt(B[i][j])} = {fmt(val)}")
            fila.append(val)
        resultado.append(fila)
    return resultado, pasos


def multiplicar(A, B):
    filas_a, cols_a = len(A), len(A[0])
    filas_b, cols_b = len(B), len(B[0])
    if cols_a != filas_b:
        return None, [f"Error: no se puede multiplicar ({filas_a}x{cols_a}) por "
                       f"({filas_b}x{cols_b}). Las columnas de A deben ser igual a las filas de B."]

    pasos = ["Cada celda del resultado es el producto punto de una fila de A con una columna de B:"]
    resultado = [[0] * cols_b for _ in range(filas_a)]
    for i in range(filas_a):
        for j in range(cols_b):
            terminos = [f"{fmt(A[i][k])}x{fmt(B[k][j])}" for k in range(cols_a)]
            valor = sum(A[i][k] * B[k][j] for k in range(cols_a))
            resultado[i][j] = valor
            pasos.append(f"  R[{i+1}][{j+1}] = {' + '.join(terminos)} = {fmt(valor)}")
    return resultado, pasos


def transponer(A):
    filas, cols = len(A), len(A[0])
    pasos = ["Transponer: la fila i se convierte en la columna i."]
    resultado = [[A[i][j] for i in range(filas)] for j in range(cols)]
    for i in range(filas):
        pasos.append(f"  Fila {i+1} de A -> Columna {i+1} del resultado")
    return resultado, pasos


def determinante(m, nivel=0):
    n = len(m)
    pasos = []
    sangria = "  " * nivel

    if n == 1:
        return m[0][0], [f"{sangria}Matriz 1x1 -> det = {fmt(m[0][0])}"]

    if n == 2:
        det = m[0][0] * m[1][1] - m[0][1] * m[1][0]
        pasos.append(f"{sangria}Matriz 2x2 -> det = ({fmt(m[0][0])}x{fmt(m[1][1])}) - "
                      f"({fmt(m[0][1])}x{fmt(m[1][0])}) = {fmt(det)}")
        return det, pasos

    det = 0
    pasos.append(f"{sangria}Expansion por cofactores en la fila 1:")
    for j in range(n):
        menor = [fila[:j] + fila[j + 1:] for fila in m[1:]]
        signo = 1 if j % 2 == 0 else -1
        pasos.append(f"{sangria}  Cofactor (1,{j+1}), signo {'+' if signo > 0 else '-'}, "
                      f"elemento {fmt(m[0][j])}:")
        sub_det, sub_pasos = determinante(menor, nivel + 2)
        pasos.extend(sub_pasos)
        det += signo * m[0][j] * sub_det
    pasos.append(f"{sangria}Suma total -> det = {fmt(det)}")
    return det, pasos


def inversa(m):
    n = len(m)
    if n != len(m[0]):
        return None, ["Error: la matriz debe ser cuadrada para calcular la inversa."]

    pasos = ["Paso 1: calcular el determinante de A"]
    det, pasos_det = determinante(m)
    pasos.extend(pasos_det)

    if abs(det) < 1e-9:
        pasos.append("El determinante es 0 -> la matriz NO tiene inversa.")
        return None, pasos

    pasos.append("\nPaso 2: calcular la matriz de cofactores")
    cofactores = []
    for i in range(n):
        fila_cof = []
        for j in range(n):
            menor = [fila[:j] + fila[j + 1:] for k, fila in enumerate(m) if k != i]
            signo = 1 if (i + j) % 2 == 0 else -1
            menor_det, _ = determinante(menor)
            cof = signo * menor_det
            fila_cof.append(cof)
            pasos.append(f"  C[{i+1}][{j+1}] = {fmt(cof)}")
        cofactores.append(fila_cof)

    pasos.append("\nPaso 3: transponer la matriz de cofactores (matriz adjunta)")
    adjunta = [[cofactores[j][i] for j in range(n)] for i in range(n)]

    pasos.append("\nPaso 4: dividir cada elemento de la adjunta entre el determinante")
    resultado = [[adjunta[i][j] / det for j in range(n)] for i in range(n)]

    return resultado, pasos


class MatricesFrame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.entries_a = []
        self.entries_b = []

        config = tk.Frame(self)
        config.pack(fill="x", padx=10, pady=10)

        tk.Label(config, text="Matriz A: filas").grid(row=0, column=0)
        self.filas_a = tk.Spinbox(config, from_=1, to=5, width=3)
        self.filas_a.grid(row=0, column=1)
        tk.Label(config, text="cols").grid(row=0, column=2)
        self.cols_a = tk.Spinbox(config, from_=1, to=5, width=3)
        self.cols_a.grid(row=0, column=3)

        tk.Label(config, text="   Matriz B: filas").grid(row=0, column=4)
        self.filas_b = tk.Spinbox(config, from_=1, to=5, width=3)
        self.filas_b.grid(row=0, column=5)
        tk.Label(config, text="cols").grid(row=0, column=6)
        self.cols_b = tk.Spinbox(config, from_=1, to=5, width=3)
        self.cols_b.grid(row=0, column=7)

        tk.Button(config, text="Generar matrices", command=self.generar_matrices).grid(row=0, column=8, padx=10)

        grillas = tk.Frame(self)
        grillas.pack(fill="x", padx=10, pady=5)

        tk.Label(grillas, text="Matriz A").grid(row=0, column=0)
        self.frame_a = tk.Frame(grillas)
        self.frame_a.grid(row=1, column=0, padx=20)

        tk.Label(grillas, text="Matriz B").grid(row=0, column=1)
        self.frame_b = tk.Frame(grillas)
        self.frame_b.grid(row=1, column=1, padx=20)

        op_frame = tk.Frame(self)
        op_frame.pack(fill="x", padx=10, pady=10)

        tk.Label(op_frame, text="Operacion:").pack(side="left")
        self.combo_operacion = ttk.Combobox(
            op_frame, state="readonly",
            values=["Suma", "Resta", "Multiplicacion", "Determinante", "Inversa", "Transpuesta"]
        )
        self.combo_operacion.current(0)
        self.combo_operacion.pack(side="left", padx=5)

        tk.Button(op_frame, text="Calcular", command=self.calcular).pack(side="left", padx=10)

        tk.Label(self, text="Resultado:").pack(anchor="w", padx=10)
        self.text_resultado = tk.Text(self, height=4, font=("Consolas", 11), bg="#f5f5f5")
        self.text_resultado.pack(fill="x", padx=10, pady=(0, 10))

        tk.Label(self, text="Proceso:").pack(anchor="w", padx=10)
        self.text_proceso = tk.Text(self, font=("Consolas", 10), bg="white")
        self.text_proceso.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        self.generar_matrices()

    def generar_matrices(self):
        self.entries_a = self._crear_grid(self.frame_a, int(self.filas_a.get()), int(self.cols_a.get()))
        self.entries_b = self._crear_grid(self.frame_b, int(self.filas_b.get()), int(self.cols_b.get()))

    def _crear_grid(self, frame, filas, cols):
        for widget in frame.winfo_children():
            widget.destroy()
        entries = []
        for i in range(filas):
            fila_entries = []
            for j in range(cols):
                e = tk.Entry(frame, width=6, justify="center")
                e.insert(0, "0")
                e.grid(row=i, column=j, padx=2, pady=2)
                fila_entries.append(e)
            entries.append(fila_entries)
        return entries

    def _leer_matriz(self, entries):
        return [[float(e.get()) for e in fila] for fila in entries]

    def calcular(self):
        try:
            A = self._leer_matriz(self.entries_a)
            op = self.combo_operacion.get()

            if op in ("Suma", "Resta"):
                B = self._leer_matriz(self.entries_b)
                resultado, pasos = sumar_restar(A, B, "+" if op == "Suma" else "-")
            elif op == "Multiplicacion":
                B = self._leer_matriz(self.entries_b)
                resultado, pasos = multiplicar(A, B)
            elif op == "Determinante":
                det, pasos = determinante(A)
                resultado = [[det]]
            elif op == "Inversa":
                resultado, pasos = inversa(A)
            else:
                resultado, pasos = transponer(A)

            self.text_resultado.delete("1.0", "end")
            self.text_proceso.delete("1.0", "end")

            if resultado is None:
                self.text_resultado.insert("1.0", "No se pudo calcular.")
            else:
                self.text_resultado.insert("1.0", matriz_a_texto(resultado))
            self.text_proceso.insert("1.0", "\n".join(pasos))

        except ValueError:
            messagebox.showerror("Error", "Verifica que todos los valores sean numeros.")

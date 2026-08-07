import tkinter as tk
from tkinter import ttk, messagebox


def fmt(x):
    if abs(x - round(x)) < 1e-9:
        return str(int(round(x)))
    return f"{x:.6g}"


def matriz_a_texto(m):
    if m is None:
        return "No se pudo calcular."

    return "\n".join(
        "  ".join(fmt(x) for x in fila)
        for fila in m
    )


def sumar_restar(A, B, signo):
    if len(A) != len(B) or len(A[0]) != len(B[0]):
        return None, [
            "Error: las matrices deben tener las mismas dimensiones."
        ]

    resultado = []

    for i in range(len(A)):
        fila = []

        for j in range(len(A[0])):
            valor = (
                A[i][j] + B[i][j]
                if signo == "+"
                else A[i][j] - B[i][j]
            )

            fila.append(valor)

        resultado.append(fila)

    pasos = [
        f"Operacion elemento por elemento usando '{signo}'."
    ]

    return resultado, pasos


def multiplicar(A, B):
    if len(A[0]) != len(B):
        return None, [
            "Error: las columnas de A deben coincidir con las filas de B."
        ]

    resultado = []

    for i in range(len(A)):
        fila = []

        for j in range(len(B[0])):
            valor = sum(
                A[i][k] * B[k][j]
                for k in range(len(B))
            )

            fila.append(valor)

        resultado.append(fila)

    pasos = [
        "Se multiplica cada fila de A por cada columna de B."
    ]

    return resultado, pasos


def determinante(m):
    n = len(m)

    if n == 0:
        return 0, ["Matriz vacia."]

    if n != len(m[0]):
        return None, [
            "Error: la matriz debe ser cuadrada."
        ]

    if n == 1:
        return m[0][0], [
            f"Determinante 1x1 = {fmt(m[0][0])}"
        ]

    if n == 2:
        det = (
            m[0][0] * m[1][1]
            - m[0][1] * m[1][0]
        )

        return det, [
            f"det = ({fmt(m[0][0])} x {fmt(m[1][1])}) "
            f"- ({fmt(m[0][1])} x {fmt(m[1][0])})",
            f"det = {fmt(det)}"
        ]

    pasos = [
        "Expansion por cofactores."
    ]

    det = 0

    for j in range(n):
        menor = [
            fila[:j] + fila[j + 1:]
            for fila in m[1:]
        ]

        signo = 1 if j % 2 == 0 else -1

        sub_det, sub_pasos = determinante(
            menor
        )

        pasos.extend(
            sub_pasos
        )

        det += (
            signo
            * m[0][j]
            * sub_det
        )

    pasos.append(
        f"Determinante = {fmt(det)}"
    )

    return det, pasos


def matriz_cofactores(m):
    n = len(m)

    if n != len(m[0]):
        return None, [
            "Error: la matriz debe ser cuadrada para calcular sus cofactores."
        ]

    pasos = [
        "Cada elemento C[i][j] se calcula eliminando la fila i y la columna j "
        "(el 'menor'), y multiplicando su determinante por el signo (-1)^(i+j)."
    ]

    cofactores = []

    for i in range(n):
        fila = []

        for j in range(n):
            menor = [
                fila_original[:j] + fila_original[j + 1:]
                for k, fila_original in enumerate(m)
                if k != i
            ]

            signo = (
                1
                if (i + j) % 2 == 0
                else -1
            )

            menor_det, _ = determinante(
                menor
            )

            cof = signo * menor_det
            fila.append(cof)

            pasos.append(
                f"C[{i + 1}][{j + 1}]: signo (-1)^{i + j} = {'+1' if signo > 0 else '-1'}, "
                f"menor = {fmt(menor_det)}  ->  C[{i + 1}][{j + 1}] = {fmt(cof)}"
            )

        cofactores.append(fila)

    return cofactores, pasos


def inversa(m):
    n = len(m)

    if n != len(m[0]):
        return None, [
            "Error: la matriz debe ser cuadrada."
        ]

    det, pasos = determinante(m)

    if abs(det) < 1e-9:
        pasos.append(
            "El determinante es 0. La matriz no tiene inversa."
        )
        return None, pasos

    cofactores, pasos_cofactores = matriz_cofactores(m)

    pasos.append(
        "Se calcula la matriz de cofactores:"
    )
    pasos.extend(pasos_cofactores[1:])  # se omite la explicacion general, ya la sabemos

    adjunta = [
        [
            cofactores[j][i]
            for j in range(n)
        ]
        for i in range(n)
    ]

    resultado = [
        [
            adjunta[i][j] / det
            for j in range(n)
        ]
        for i in range(n)
    ]

    pasos.append(
        "Se transpone la matriz de cofactores para obtener la adjunta."
    )

    pasos.append(
        "Se divide cada elemento de la adjunta entre el determinante."
    )

    return resultado, pasos


def _euclides_extendido(a, b):
    """Devuelve (mcd, x, y) tal que a*x + b*y = mcd(a, b)."""
    if a == 0:
        return b, 0, 1
    g, x1, y1 = _euclides_extendido(b % a, a)
    x = y1 - (b // a) * x1
    y = x1
    return g, x, y


def inverso_modular(a, n):
    """Inverso multiplicativo de 'a' modulo 'n', o None si no existe."""
    a = a % n
    g, x, _ = _euclides_extendido(a, n)
    if g != 1:
        return None
    return x % n


def inversa_modular(m, n):
    n = int(round(n))
    filas = len(m)

    if n < 2:
        return None, ["Error: el modulo n debe ser mayor o igual a 2."]

    if filas != len(m[0]):
        return None, ["Error: la matriz debe ser cuadrada."]

    pasos = [f"Trabajando en aritmetica modulo {n}."]

    det, _ = determinante(m)
    det_entero = round(det)

    if abs(det - det_entero) > 1e-6:
        pasos.append(
            f"Determinante = {fmt(det)} (no es un numero entero, "
            "no se puede trabajar en modulo n)."
        )
        return None, pasos

    pasos.append(f"Determinante = {det_entero}")

    det_mod = det_entero % n
    pasos.append(f"Determinante mod {n} = {det_mod}")

    inv_det = inverso_modular(det_mod, n)

    if inv_det is None:
        pasos.append(
            f"No existe inverso modular de {det_mod} en modulo {n} "
            f"porque mcd({det_mod}, {n}) != 1. La matriz no tiene inversa modular."
        )
        return None, pasos

    pasos.append(
        f"Inverso modular del determinante: {det_mod}^-1 mod {n} = {inv_det}"
    )

    cofactores, pasos_cof = matriz_cofactores(m)
    pasos.append("Matriz de cofactores:")
    pasos.extend(pasos_cof[1:])

    adjunta = [
        [cofactores[j][i] for j in range(filas)]
        for i in range(filas)
    ]

    pasos.append("Se transpone la matriz de cofactores para obtener la adjunta.")

    resultado = [
        [int(round(adjunta[i][j])) * inv_det % n for j in range(filas)]
        for i in range(filas)
    ]

    pasos.append(
        f"Cada elemento de la adjunta se multiplica por {inv_det} y se reduce modulo {n}."
    )

    return resultado, pasos


def transponer(m):
    resultado = [
        list(fila)
        for fila in zip(*m)
    ]

    return resultado, [
        "Se intercambian filas por columnas."
    ]


class MatricesFrame(tk.Frame):
    def __init__(
        self,
        parent,
        theme_manager,
        historial=None
    ):
        super().__init__(parent)

        self.theme_manager = theme_manager
        self.historial = historial

        self.entries_a = []
        self.entries_b = []

        self.config_frame = tk.Frame(self)
        self.config_frame.pack(
            fill="x",
            padx=14,
            pady=14
        )

        self.label_a = tk.Label(
            self.config_frame,
            text="Matriz A: filas"
        )
        self.label_a.grid(
            row=0,
            column=0
        )

        self.filas_a = tk.Spinbox(
            self.config_frame,
            from_=1,
            to=5,
            width=3
        )
        self.filas_a.grid(
            row=0,
            column=1
        )

        self.label_a2 = tk.Label(
            self.config_frame,
            text="cols"
        )
        self.label_a2.grid(
            row=0,
            column=2
        )

        self.cols_a = tk.Spinbox(
            self.config_frame,
            from_=1,
            to=5,
            width=3
        )
        self.cols_a.grid(
            row=0,
            column=3
        )

        self.label_b = tk.Label(
            self.config_frame,
            text="Matriz B: filas"
        )
        self.label_b.grid(
            row=0,
            column=4,
            padx=(20, 0)
        )

        self.filas_b = tk.Spinbox(
            self.config_frame,
            from_=1,
            to=5,
            width=3
        )
        self.filas_b.grid(
            row=0,
            column=5
        )

        self.label_b2 = tk.Label(
            self.config_frame,
            text="cols"
        )
        self.label_b2.grid(
            row=0,
            column=6
        )

        self.cols_b = tk.Spinbox(
            self.config_frame,
            from_=1,
            to=5,
            width=3
        )
        self.cols_b.grid(
            row=0,
            column=7
        )

        self.btn_generar = tk.Button(
            self.config_frame,
            text="Generar matrices",
            relief="flat",
            bd=0,
            cursor="hand2",
            command=self.generar_matrices
        )
        self.btn_generar.grid(
            row=0,
            column=8,
            padx=14
        )

        self.grillas = tk.Frame(self)
        self.grillas.pack(
            fill="x",
            padx=14,
            pady=5
        )

        self.label_titulo_a = tk.Label(
            self.grillas,
            text="Matriz A"
        )
        self.label_titulo_a.grid(
            row=0,
            column=0
        )

        self.frame_a = tk.Frame(
            self.grillas
        )
        self.frame_a.grid(
            row=1,
            column=0,
            padx=20
        )

        self.label_titulo_b = tk.Label(
            self.grillas,
            text="Matriz B"
        )
        self.label_titulo_b.grid(
            row=0,
            column=1
        )

        self.frame_b = tk.Frame(
            self.grillas
        )
        self.frame_b.grid(
            row=1,
            column=1,
            padx=20
        )

        self.op_frame = tk.Frame(self)
        self.op_frame.pack(
            fill="x",
            padx=14,
            pady=14
        )

        self.label_operacion = tk.Label(
            self.op_frame,
            text="Operacion:"
        )
        self.label_operacion.pack(
            side="left"
        )

        self.combo_operacion = ttk.Combobox(
            self.op_frame,
            state="readonly",
            values=[
                "Suma",
                "Resta",
                "Multiplicacion",
                "Determinante",
                "Matriz de cofactores",
                "Inversa",
                "Inversa modular",
                "Transpuesta"
            ]
        )

        self.combo_operacion.current(0)

        self.combo_operacion.pack(
            side="left",
            padx=5
        )

        self.btn_calcular = tk.Button(
            self.op_frame,
            text="Calcular",
            relief="flat",
            bd=0,
            cursor="hand2",
            command=self.calcular
        )

        self.btn_calcular.pack(
            side="left",
            padx=10
        )

        self.label_modulo = tk.Label(
            self.op_frame,
            text="n (modulo):"
        )
        self.label_modulo.pack(
            side="left",
            padx=(10, 0)
        )

        self.entry_modulo = tk.Entry(
            self.op_frame,
            width=5,
            bd=0,
            relief="flat"
        )
        self.entry_modulo.insert(0, "26")
        self.entry_modulo.pack(
            side="left",
            padx=5
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
            height=4,
            font=("Consolas", 11),
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

        self.generar_matrices()

        theme_manager.registrar(
            self._aplicar_tema
        )

    def generar_matrices(self):
        self.entries_a = self._crear_grid(
            self.frame_a,
            int(self.filas_a.get()),
            int(self.cols_a.get())
        )

        self.entries_b = self._crear_grid(
            self.frame_b,
            int(self.filas_b.get()),
            int(self.cols_b.get())
        )

        if hasattr(self, "paleta"):
            self._aplicar_tema(
                self.paleta
            )

    def _crear_grid(
        self,
        frame,
        filas,
        cols
    ):
        for widget in frame.winfo_children():
            widget.destroy()

        entries = []

        for i in range(filas):
            fila = []

            for j in range(cols):
                entry = tk.Entry(
                    frame,
                    width=6,
                    justify="center",
                    bd=0,
                    relief="flat"
                )

                entry.insert(
                    0,
                    "0"
                )

                entry.grid(
                    row=i,
                    column=j,
                    padx=2,
                    pady=2
                )

                fila.append(entry)

            entries.append(fila)

        return entries

    def _leer_matriz(self, entries):
        return [
            [
                float(entry.get())
                for entry in fila
            ]
            for fila in entries
        ]

    def calcular(self):
        try:
            A = self._leer_matriz(
                self.entries_a
            )

            op = self.combo_operacion.get()

            B = None

            if op in (
                "Suma",
                "Resta"
            ):
                B = self._leer_matriz(
                    self.entries_b
                )

                resultado, pasos = sumar_restar(
                    A,
                    B,
                    "+" if op == "Suma" else "-"
                )

            elif op == "Multiplicacion":
                B = self._leer_matriz(
                    self.entries_b
                )

                resultado, pasos = multiplicar(
                    A,
                    B
                )

            elif op == "Determinante":
                det, pasos = determinante(A)
                resultado = [[det]]

            elif op == "Matriz de cofactores":
                resultado, pasos = matriz_cofactores(A)

            elif op == "Inversa":
                resultado, pasos = inversa(A)

            elif op == "Inversa modular":
                try:
                    n = int(self.entry_modulo.get())
                except ValueError:
                    messagebox.showerror("Error", "El modulo n debe ser un numero entero.")
                    return
                resultado, pasos = inversa_modular(A, n)

            else:
                resultado, pasos = transponer(A)

            self.text_resultado.delete(
                "1.0",
                "end"
            )

            self.text_proceso.delete(
                "1.0",
                "end"
            )

            if resultado is None:
                self.text_resultado.insert(
                    "1.0",
                    "No se pudo calcular."
                )

            else:
                self.text_resultado.insert(
                    "1.0",
                    matriz_a_texto(resultado)
                )

            self.text_proceso.insert(
                "1.0",
                "\n".join(pasos)
            )

            if self.historial:
                entrada = {
                    "A": A
                }

                if B is not None:
                    entrada["B"] = B

                self.historial.registrar(
                    "Matrices",
                    op,
                    entrada,
                    resultado,
                    pasos
                )

        except ValueError:
            messagebox.showerror(
                "Error",
                "Verifica que todos los valores sean numeros."
            )

    def _aplicar_tema(self, p):
        self.paleta = p

        for frame in (
            self,
            self.config_frame,
            self.grillas,
            self.frame_a,
            self.frame_b,
            self.op_frame
        ):
            frame.configure(
                bg=p["bg"]
            )

        for label in (
            self.label_a,
            self.label_a2,
            self.label_b,
            self.label_b2,
            self.label_titulo_a,
            self.label_titulo_b,
            self.label_operacion,
            self.label_modulo,
            self.label_resultado,
            self.label_proceso
        ):
            label.configure(
                bg=p["bg"],
                fg=p["fg"]
            )

        self.entry_modulo.configure(
            bg=p["bg_secundario"],
            fg=p["fg"],
            insertbackground=p["fg"],
            highlightthickness=1,
            highlightbackground=p["borde"]
        )

        for btn in (
            self.btn_generar,
            self.btn_calcular
        ):
            btn.configure(
                bg=p["accent"],
                fg="#ffffff",
                activebackground=p["accent_hover"]
            )

        for widget in (
            self.text_resultado,
            self.text_proceso
        ):
            widget.configure(
                bg=p["bg_secundario"],
                fg=p["fg"],
                insertbackground=p["fg"],
                highlightthickness=1,
                highlightbackground=p["borde"],
                highlightcolor=p["accent"]
            )

        for entries in (
            self.entries_a,
            self.entries_b
        ):
            for fila in entries:
                for entry in fila:
                    entry.configure(
                        bg=p["bg_secundario"],
                        fg=p["fg"],
                        insertbackground=p["fg"],
                        highlightthickness=1,
                        highlightbackground=p["borde"]
                    )
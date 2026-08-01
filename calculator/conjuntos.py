"""
Modulo de teoria de conjuntos.
Cada operacion devuelve (resultado, pasos).
"""
import tkinter as tk
from tkinter import ttk, messagebox


def parsear_conjunto(texto):
    """Convierte 'a, b, 3, 4' en un set de Python, probando int -> float -> str."""
    elementos = [e.strip() for e in texto.split(",") if e.strip() != ""]
    resultado = set()
    for e in elementos:
        try:
            resultado.add(int(e))
        except ValueError:
            try:
                resultado.add(float(e))
            except ValueError:
                resultado.add(e)
    return resultado


def formatear_conjunto(s):
    if not s:
        return "vacio"
    return "{" + ", ".join(str(x) for x in sorted(s, key=str)) + "}"


def union(A, B):
    pasos = ["A union B: todos los elementos que estan en A, en B, o en ambos."]
    return A | B, pasos


def interseccion(A, B):
    pasos = ["A interseccion B: elementos que estan en A Y en B al mismo tiempo."]
    return A & B, pasos


def diferencia(A, B):
    pasos = ["A - B: elementos que estan en A pero NO estan en B."]
    return A - B, pasos


def complemento(A, U):
    if not U:
        return None, ["Error: necesitas definir el conjunto universal U."]
    if not A.issubset(U):
        pasos = ["Advertencia: A tiene elementos que no estan en U, igual se calcula U - A."]
    else:
        pasos = ["A' = U - A: elementos del universo U que no estan en A."]
    return U - A, pasos


def producto_cartesiano(A, B):
    pares = [(a, b) for a in sorted(A, key=str) for b in sorted(B, key=str)]
    pasos = ["A x B: se forma un par (a, b) por cada combinacion de a en A con b en B."]
    pasos.append(f"Total de pares: {len(A)} x {len(B)} = {len(pares)}")
    return set(pares), pasos


class ConjuntosFrame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        entradas = tk.Frame(self)
        entradas.pack(fill="x", padx=10, pady=10)

        tk.Label(entradas, text="Conjunto A (separado por comas):").grid(row=0, column=0, sticky="w")
        self.entry_a = tk.Entry(entradas, width=40)
        self.entry_a.grid(row=0, column=1, padx=5, pady=3)
        self.entry_a.insert(0, "1, 2, 3, 4")

        tk.Label(entradas, text="Conjunto B (separado por comas):").grid(row=1, column=0, sticky="w")
        self.entry_b = tk.Entry(entradas, width=40)
        self.entry_b.grid(row=1, column=1, padx=5, pady=3)
        self.entry_b.insert(0, "3, 4, 5, 6")

        tk.Label(entradas, text="Universo U (solo para complemento):").grid(row=2, column=0, sticky="w")
        self.entry_u = tk.Entry(entradas, width=40)
        self.entry_u.grid(row=2, column=1, padx=5, pady=3)
        self.entry_u.insert(0, "1, 2, 3, 4, 5, 6, 7, 8")

        op_frame = tk.Frame(self)
        op_frame.pack(fill="x", padx=10, pady=5)
        tk.Label(op_frame, text="Operacion:").pack(side="left")
        self.combo_operacion = ttk.Combobox(
            op_frame, state="readonly",
            values=["Union", "Interseccion", "Diferencia (A-B)", "Complemento (A')", "Producto cartesiano"]
        )
        self.combo_operacion.current(0)
        self.combo_operacion.pack(side="left", padx=5)
        tk.Button(op_frame, text="Calcular", command=self.calcular).pack(side="left", padx=10)

        tk.Label(self, text="Resultado:").pack(anchor="w", padx=10)
        self.text_resultado = tk.Text(self, height=3, font=("Consolas", 11), bg="#f5f5f5")
        self.text_resultado.pack(fill="x", padx=10, pady=(0, 10))

        tk.Label(self, text="Proceso:").pack(anchor="w", padx=10)
        self.text_proceso = tk.Text(self, font=("Consolas", 10), bg="white")
        self.text_proceso.pack(fill="both", expand=True, padx=10, pady=(0, 10))

    def calcular(self):
        A = parsear_conjunto(self.entry_a.get())
        B = parsear_conjunto(self.entry_b.get())
        U = parsear_conjunto(self.entry_u.get())
        op = self.combo_operacion.get()

        if op == "Union":
            resultado, pasos = union(A, B)
        elif op == "Interseccion":
            resultado, pasos = interseccion(A, B)
        elif op == "Diferencia (A-B)":
            resultado, pasos = diferencia(A, B)
        elif op == "Complemento (A')":
            resultado, pasos = complemento(A, U)
        else:
            resultado, pasos = producto_cartesiano(A, B)

        self.text_resultado.delete("1.0", "end")
        self.text_proceso.delete("1.0", "end")

        if resultado is None:
            self.text_resultado.insert("1.0", "No se pudo calcular.")
        elif op == "Producto cartesiano":
            texto = "{" + ", ".join(f"({a}, {b})" for a, b in sorted(resultado, key=str)) + "}"
            self.text_resultado.insert("1.0", texto if resultado else "vacio")
        else:
            self.text_resultado.insert("1.0", formatear_conjunto(resultado))
        self.text_proceso.insert("1.0", "\n".join(pasos))

##conjuntos.py

"""
Modulo de teoria de conjuntos.
Cada operacion devuelve (resultado, pasos).
"""
import tkinter as tk
from tkinter import ttk


def parsear_conjunto(texto):
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
    def __init__(self, parent, theme_manager):
        super().__init__(parent)
        self.theme_manager = theme_manager

        self.entradas = tk.Frame(self)
        self.entradas.pack(fill="x", padx=14, pady=14)

        self.label_a = tk.Label(self.entradas, text="Conjunto A (separado por comas):")
        self.label_a.grid(row=0, column=0, sticky="w")
        self.entry_a = tk.Entry(self.entradas, width=40, bd=0, relief="flat")
        self.entry_a.grid(row=0, column=1, padx=5, pady=3)
        self.entry_a.insert(0, "1, 2, 3, 4")

        self.label_b = tk.Label(self.entradas, text="Conjunto B (separado por comas):")
        self.label_b.grid(row=1, column=0, sticky="w")
        self.entry_b = tk.Entry(self.entradas, width=40, bd=0, relief="flat")
        self.entry_b.grid(row=1, column=1, padx=5, pady=3)
        self.entry_b.insert(0, "3, 4, 5, 6")

        self.label_u = tk.Label(self.entradas, text="Universo U (solo para complemento):")
        self.label_u.grid(row=2, column=0, sticky="w")
        self.entry_u = tk.Entry(self.entradas, width=40, bd=0, relief="flat")
        self.entry_u.grid(row=2, column=1, padx=5, pady=3)
        self.entry_u.insert(0, "1, 2, 3, 4, 5, 6, 7, 8")

        self.op_frame = tk.Frame(self)
        self.op_frame.pack(fill="x", padx=14, pady=5)
        self.label_operacion = tk.Label(self.op_frame, text="Operacion:")
        self.label_operacion.pack(side="left")
        self.combo_operacion = ttk.Combobox(
            self.op_frame, state="readonly",
            values=["Union", "Interseccion", "Diferencia (A-B)", "Complemento (A')", "Producto cartesiano"]
        )
        self.combo_operacion.current(0)
        self.combo_operacion.pack(side="left", padx=5)
        self.btn_calcular = tk.Button(self.op_frame, text="Calcular", relief="flat", bd=0,
                                       cursor="hand2", command=self.calcular)
        self.btn_calcular.pack(side="left", padx=10)

        self.label_resultado = tk.Label(self, text="Resultado:")
        self.label_resultado.pack(anchor="w", padx=14)
        self.text_resultado = tk.Text(self, height=3, font=("Consolas", 11), bd=0)
        self.text_resultado.pack(fill="x", padx=14, pady=(0, 10))

        self.label_proceso = tk.Label(self, text="Proceso:")
        self.label_proceso.pack(anchor="w", padx=14)
        self.text_proceso = tk.Text(self, font=("Consolas", 10), bd=0)
        self.text_proceso.pack(fill="both", expand=True, padx=14, pady=(0, 14))

        theme_manager.registrar(self._aplicar_tema)

    def _aplicar_tema(self, paleta):
        p = paleta
        for frame in (self, self.entradas, self.op_frame):
            frame.configure(bg=p["bg"])
        for label in (self.label_a, self.label_b, self.label_u, self.label_operacion,
                      self.label_resultado, self.label_proceso):
            label.configure(bg=p["bg"], fg=p["fg"])
        for entry in (self.entry_a, self.entry_b, self.entry_u):
            entry.configure(bg=p["bg_secundario"], fg=p["fg"], insertbackground=p["fg"],
                             highlightthickness=1, highlightbackground=p["borde"],
                             highlightcolor=p["accent"])
        self.btn_calcular.configure(bg=p["accent"], fg="#ffffff", activebackground=p["accent_hover"])
        for text_widget in (self.text_resultado, self.text_proceso):
            text_widget.configure(bg=p["bg_secundario"], fg=p["fg"], insertbackground=p["fg"],
                                   highlightthickness=1, highlightbackground=p["borde"],
                                   highlightcolor=p["accent"])

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

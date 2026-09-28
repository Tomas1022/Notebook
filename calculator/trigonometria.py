import tkinter as tk
from tkinter import ttk, messagebox
import math

def calcular_ley_seno_lado(datos):
    if len(datos) != 3:
        return None, ["Error: Ingresa Ángulo A, Lado a, Ángulo B separados por comas."]
    
    ang_a_deg, lado_a, ang_b_deg = datos
    if ang_a_deg == 0 or ang_a_deg == 180:
        return None, ["Error: El ángulo A no puede ser 0 o 180 grados."]
    
    ang_a_rad = math.radians(ang_a_deg)
    ang_b_rad = math.radians(ang_b_deg)
    
    lado_b = (lado_a * math.sin(ang_b_rad)) / math.sin(ang_a_rad)
    
    pasos = [
        "Ley del Seno: a / sen(A) = b / sen(B)",
        f"Despejando b: b = (a * sen(B)) / sen(A)",
        f"b = ({lado_a:g} * sen({ang_b_deg:g}°)) / sen({ang_a_deg:g}°)",
        f"b = ({lado_a:g} * {math.sin(ang_b_rad):.4f}) / {math.sin(ang_a_rad):.4f}",
        f"Lado b = {lado_b:.6g}"
    ]
    return round(lado_b, 6), pasos


def calcular_ley_seno_angulo(datos):
    if len(datos) != 3:
        return None, ["Error: Ingresa Lado a, Ángulo A, Lado b separados por comas."]
    
    lado_a, ang_a_deg, lado_b = datos
    if lado_a == 0:
        return None, ["Error: El lado 'a' no puede ser 0."]
        
    ang_a_rad = math.radians(ang_a_deg)
    sen_b = (lado_b * math.sin(ang_a_rad)) / lado_a
    
    if sen_b > 1 or sen_b < -1:
        return None, ["Error: Los valores ingresados no forman un triángulo válido (seno > 1)."]
        
    ang_b_rad = math.asin(sen_b)
    ang_b_deg = math.degrees(ang_b_rad)
    
    pasos = [
        "Ley del Seno: a / sen(A) = b / sen(B)",
        f"Despejando sen(B): sen(B) = (b * sen(A)) / a",
        f"sen(B) = ({lado_b:g} * sen({ang_a_deg:g}°)) / {lado_a:g}",
        f"sen(B) = {sen_b:.4f}",
        f"B = arcsen({sen_b:.4f})",
        f"Ángulo B = {ang_b_deg:.6g}°"
    ]
    return round(ang_b_deg, 6), pasos


def calcular_ley_coseno_lado(datos):
    if len(datos) != 3:
        return None, ["Error: Ingresa Lado a, Lado b, Ángulo C separados por comas."]
    
    lado_a, lado_b, ang_c_deg = datos
    ang_c_rad = math.radians(ang_c_deg)
    
    lado_c_cuadrado = lado_a**2 + lado_b**2 - 2 * lado_a * lado_b * math.cos(ang_c_rad)
    if lado_c_cuadrado < 0:
        return None, ["Error: Raíz negativa, verifica los valores."]
        
    lado_c = math.sqrt(lado_c_cuadrado)
    
    pasos = [
        "Ley del Coseno: c² = a² + b² - 2ab * cos(C)",
        f"c² = {lado_a:g}² + {lado_b:g}² - 2({lado_a:g})({lado_b:g}) * cos({ang_c_deg:g}°)",
        f"c² = {lado_a**2:g} + {lado_b**2:g} - {2*lado_a*lado_b:g} * {math.cos(ang_c_rad):.4f}",
        f"c² = {lado_c_cuadrado:.6g}",
        f"c = √({lado_c_cuadrado:.6g})",
        f"Lado c = {lado_c:.6g}"
    ]
    return round(lado_c, 6), pasos


def calcular_ley_coseno_angulo(datos):
    if len(datos) != 3:
        return None, ["Error: Ingresa Lado a, Lado b, Lado c separados por comas."]
    
    lado_a, lado_b, lado_c = datos
    if lado_a == 0 or lado_b == 0:
        return None, ["Error: Los lados no pueden ser 0."]
        
    cos_c = (lado_a**2 + lado_b**2 - lado_c**2) / (2 * lado_a * lado_b)
    
    if cos_c > 1 or cos_c < -1:
        return None, ["Error: Los lados no forman un triángulo válido."]
        
    ang_c_rad = math.acos(cos_c)
    ang_c_deg = math.degrees(ang_c_rad)
    
    pasos = [
        "Ley del Coseno: c² = a² + b² - 2ab * cos(C)",
        f"Despejando cos(C): cos(C) = (a² + b² - c²) / 2ab",
        f"cos(C) = ({lado_a:g}² + {lado_b:g}² - {lado_c:g}²) / (2 * {lado_a:g} * {lado_b:g})",
        f"cos(C) = {cos_c:.4f}",
        f"C = arccos({cos_c:.4f})",
        f"Ángulo C = {ang_c_deg:.6g}°"
    ]
    return round(ang_c_deg, 6), pasos


def calcular_haversine(datos):
    if len(datos) != 4:
        return None, ["Error: Ingresa Latitud 1, Longitud 1, Latitud 2, Longitud 2."]
    
    lat1, lon1, lat2, lon2 = datos
    
    # Radio promedio de la Tierra en kilómetros
    R = 6371.0 
    
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)
    
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    
    a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distancia = R * c
    
    pasos = [
        "Ley de Haversine para distancias esféricas terrestres",
        f"Coordenadas 1: ({lat1:g}°, {lon1:g}°)",
        f"Coordenadas 2: ({lat2:g}°, {lon2:g}°)",
        "Convertimos coordenadas a radianes y aplicamos:",
        "a = sen²(Δlat/2) + cos(lat1) * cos(lat2) * sen²(Δlon/2)",
        f"a = {a:.6g}",
        "c = 2 * atan2(√a, √(1−a))",
        f"c = {c:.6g}",
        "Distancia = R * c  (donde R ≈ 6371 km)",
        f"Distancia = 6371 * {c:.6g}",
        f"Distancia = {distancia:.2f} km"
    ]
    return round(distancia, 2), pasos


class TrigonometriaFrame(tk.Frame):
    OPERACIONES = [
        "Ley del Seno (Hallar Lado b)",
        "Ley del Seno (Hallar Ángulo B)",
        "Ley del Coseno (Hallar Lado c)",
        "Ley del Coseno (Hallar Ángulo C)",
        "Ley de Haversine (Distancia entre Coordenadas)"
    ]

    def __init__(self, parent, theme_manager, historial=None):
        super().__init__(parent)
        self.theme_manager = theme_manager
        self.historial = historial

        self.entradas_frame = tk.Frame(self)
        self.entradas_frame.pack(fill="x", padx=14, pady=14)

        self.label_instruccion = tk.Label(
            self.entradas_frame,
            text="Datos:"
        )
        self.label_instruccion.pack(side="left")

        self.entry_datos = tk.Entry(
            self.entradas_frame, width=40, bd=0, relief="flat"
        )
        self.entry_datos.insert(0, "30, 10, 45")
        self.entry_datos.pack(side="left", padx=8)

        self.op_frame = tk.Frame(self)
        self.op_frame.pack(fill="x", padx=14, pady=(0, 14))

        self.label_operacion = tk.Label(self.op_frame, text="Operacion:")
        self.label_operacion.pack(side="left")

        self.combo_operacion = ttk.Combobox(
            self.op_frame, state="readonly",
            values=self.OPERACIONES,
            width=40
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
        self.text_resultado = tk.Text(self, height=2, font=("Consolas", 12), bd=0)
        self.text_resultado.pack(fill="x", padx=14, pady=(0, 10))

        self.label_proceso = tk.Label(self, text="Proceso:")
        self.label_proceso.pack(anchor="w", padx=14)
        self.text_proceso = tk.Text(self, font=("Consolas", 10), bd=0)
        self.text_proceso.pack(fill="both", expand=True, padx=14, pady=(0, 14))

        theme_manager.registrar(self._aplicar_tema)
        self._actualizar_label()

    def _actualizar_label(self, event=None):
        op = self.combo_operacion.get()
        if op == "Ley del Seno (Hallar Lado b)":
            self.label_instruccion.config(text="Ángulo A, Lado a, Ángulo B:")
        elif op == "Ley del Seno (Hallar Ángulo B)":
            self.label_instruccion.config(text="Lado a, Ángulo A, Lado b:")
        elif op == "Ley del Coseno (Hallar Lado c)":
            self.label_instruccion.config(text="Lado a, Lado b, Ángulo C:")
        elif op == "Ley del Coseno (Hallar Ángulo C)":
            self.label_instruccion.config(text="Lado a, Lado b, Lado c:")
        elif op == "Ley de Haversine (Distancia entre Coordenadas)":
            self.label_instruccion.config(text="Lat1, Lon1, Lat2, Lon2:")

    def _leer_datos(self):
        texto = self.entry_datos.get()
        partes = [p.strip() for p in texto.split(",") if p.strip() != ""]
        return [float(p) for p in partes]

    def calcular(self):
        try:
            datos = self._leer_datos()
        except ValueError:
            messagebox.showerror("Error", "Ingresa solo números decimales separados por comas.")
            return

        if not datos:
            messagebox.showerror("Error", "Ingresa los valores requeridos.")
            return

        op = self.combo_operacion.get()

        if op == "Ley del Seno (Hallar Lado b)":
            res, pasos = calcular_ley_seno_lado(datos)
            prefijo = "Lado b = "
            sufijo = ""
        elif op == "Ley del Seno (Hallar Ángulo B)":
            res, pasos = calcular_ley_seno_angulo(datos)
            prefijo = "Ángulo B = "
            sufijo = "°"
        elif op == "Ley del Coseno (Hallar Lado c)":
            res, pasos = calcular_ley_coseno_lado(datos)
            prefijo = "Lado c = "
            sufijo = ""
        elif op == "Ley del Coseno (Hallar Ángulo C)":
            res, pasos = calcular_ley_coseno_angulo(datos)
            prefijo = "Ángulo C = "
            sufijo = "°"
        elif op == "Ley de Haversine (Distancia entre Coordenadas)":
            res, pasos = calcular_haversine(datos)
            prefijo = "Distancia = "
            sufijo = " km"

        if res is None:
            messagebox.showerror("Error", pasos[0])
            return

        texto_resultado = f"{prefijo}{res}{sufijo}"

        self.text_resultado.delete("1.0", "end")
        self.text_proceso.delete("1.0", "end")
        self.text_resultado.insert("1.0", texto_resultado)
        self.text_proceso.insert("1.0", "\n".join(pasos))

        if self.historial:
            self.historial.registrar(
                "Trigonometría", op, {"entrada": self.entry_datos.get()}, texto_resultado, pasos
            )

    def _aplicar_tema(self, p):
        for frame in (self, self.entradas_frame, self.op_frame):
            frame.configure(bg=p["bg"])

        for label in (self.label_instruccion, self.label_operacion, self.label_resultado, self.label_proceso):
            label.configure(bg=p["bg"], fg=p["fg"])

        self.entry_datos.configure(
            bg=p["bg_secundario"], fg=p["fg"], insertbackground=p["fg"],
            highlightthickness=1, highlightbackground=p["borde"], highlightcolor=p["accent"]
        )

        self.btn_calcular.configure(bg=p["accent"], fg="#ffffff", activebackground=p["accent_hover"])

        for widget in (self.text_resultado, self.text_proceso):
            widget.configure(
                bg=p["bg_secundario"], fg=p["fg"], insertbackground=p["fg"],
                highlightthickness=1, highlightbackground=p["borde"], highlightcolor=p["accent"]
            )
import json
import os
import tkinter as tk

ARCHIVO_NOTAS = "notas_guardadas.json"


class NotasFrame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        # --- Barra de botones arriba ---
        barra_botones = tk.Frame(self)
        barra_botones.pack(fill="x", padx=10, pady=10)

        btn_guardar = tk.Button(barra_botones, text="💾 Guardar", command=self.guardar_nota)
        btn_guardar.pack(side="left", padx=5)

        btn_limpiar = tk.Button(barra_botones, text="🗑️ Limpiar", command=self.limpiar_nota)
        btn_limpiar.pack(side="left", padx=5)

        self.label_estado = tk.Label(barra_botones, text="", fg="green")
        self.label_estado.pack(side="left", padx=10)

        # --- Área de texto principal ---
        self.text_area = tk.Text(self, wrap="word", font=("Arial", 12))
        self.text_area.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # Cargar la nota guardada al abrir la app (si existe)
        self.cargar_nota()

    def guardar_nota(self):
        contenido = self.text_area.get("1.0", "end-1c")
        with open(ARCHIVO_NOTAS, "w", encoding="utf-8") as f:
            json.dump({"contenido": contenido}, f, ensure_ascii=False, indent=2)

        self.label_estado.config(text="Guardado ✓")
        self.after(2000, lambda: self.label_estado.config(text=""))

    def cargar_nota(self):
        if os.path.exists(ARCHIVO_NOTAS):
            with open(ARCHIVO_NOTAS, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.text_area.insert("1.0", data.get("contenido", ""))

    def limpiar_nota(self):
        self.text_area.delete("1.0", "end")
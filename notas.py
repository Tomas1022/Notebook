import json
import os
import tkinter as tk
from tkinter import font as tkfont
from tkinter import messagebox
from tkinter import ttk

ARCHIVO_NOTAS = "notas_guardadas.json"
FUENTE_BASE = "Arial"
TAMANOS_DISPONIBLES = [8, 9, 10, 11, 12, 14, 16, 18, 20, 24, 28, 32]


class NotasFrame(tk.Frame):
    LAYOUTS = ["1", "2", "3", "4"]

    def __init__(self, parent):
        super().__init__(parent)

        self.layout_actual = "1"
        self.paneles = []
        self.pane_activo = None
        self.tag_attrs = {}  # nombre_de_tag -> (tamano, negrita, cursiva, subrayado)

        self.tamano_actual = 11
        self.negrita_activa = False
        self.cursiva_activa = False
        self.subrayado_activa = False

        # --- Menu superior tipo "Archivo" ---
        menu_bar = tk.Frame(self, bg="#e0e0e0")
        menu_bar.pack(fill="x")

        menubutton_archivo = tk.Menubutton(
            menu_bar, text="Archivo", relief="flat", bg="#e0e0e0",
            activebackground="#c0c0ff", padx=10, pady=4
        )
        menubutton_archivo.pack(side="left")

        menu_archivo = tk.Menu(menubutton_archivo, tearoff=0)
        menu_archivo.add_command(label="Guardar", command=self.guardar_notas)
        menu_archivo.add_command(label="Limpiar", command=self.limpiar_pane_activo)
        menu_archivo.add_separator()

        submenu_dividir = tk.Menu(menu_archivo, tearoff=0)
        self.iconos_layout = {}  # hay que mantener referencias vivas o Tkinter las borra
        etiquetas = {
            "1": "1 panel",
            "2": "2 paneles (lado a lado)",
            "3": "3 paneles",
            "4": "4 paneles (cuadricula)",
        }
        for n in self.LAYOUTS:
            icono = self._generar_icono_layout(n)
            self.iconos_layout[n] = icono
            submenu_dividir.add_command(
                label=etiquetas[n], image=icono, compound="left",
                command=lambda n=n: self.cambiar_layout(n)
            )
        menu_archivo.add_cascade(label="Dividir pantalla", menu=submenu_dividir)

        menubutton_archivo.config(menu=menu_archivo)

        self.label_estado = tk.Label(menu_bar, text="", fg="green", bg="#e0e0e0")
        self.label_estado.pack(side="left", padx=10)

        # --- Barra de formato: tamano, negrita, cursiva, subrayado ---
        barra_formato = tk.Frame(self)
        barra_formato.pack(fill="x", padx=10, pady=(8, 8))

        tk.Label(barra_formato, text="Tamaño:").pack(side="left")
        tk.Button(barra_formato, text="-", width=2, command=self.disminuir_tamano).pack(side="left", padx=(3, 0))
        self.combo_tamano = ttk.Combobox(
            barra_formato, values=TAMANOS_DISPONIBLES, state="readonly", width=4
        )
        self.combo_tamano.set(self.tamano_actual)
        self.combo_tamano.pack(side="left", padx=2)
        self.combo_tamano.bind("<<ComboboxSelected>>", self.cambiar_tamano)
        tk.Button(barra_formato, text="+", width=2, command=self.aumentar_tamano).pack(side="left", padx=(0, 12))

        self.btn_negrita = tk.Button(barra_formato, text="N", font=("Arial", 10, "bold"),
                                      width=3, command=self.toggle_negrita)
        self.btn_negrita.pack(side="left", padx=2)

        self.btn_cursiva = tk.Button(barra_formato, text="K", font=("Arial", 10, "italic"),
                                      width=3, command=self.toggle_cursiva)
        self.btn_cursiva.pack(side="left", padx=2)

        self.btn_subrayado = tk.Button(barra_formato, text="S", font=("Arial", 10, "underline"),
                                        width=3, command=self.toggle_subrayado)
        self.btn_subrayado.pack(side="left", padx=2)

        # --- Contenedor de paneles de texto ---
        self.container = tk.Frame(self)
        self.container.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        self.cargar_notas()

    # ---------- Manejo de paneles ----------

    def _generar_icono_layout(self, n):
        """Crea una PhotoImage pequeña que representa el layout n (1,2,3,4) para el menu."""
        ANCHO, ALTO, M = 20, 14, 2
        img = tk.PhotoImage(width=ANCHO, height=ALTO)
        img.put("#888888", to=(0, 0, ANCHO, ALTO))

        if n == "1":
            img.put("white", to=(M, M, ANCHO - M, ALTO - M))

        elif n == "2":
            mitad = (ANCHO - M * 2) // 2
            img.put("white", to=(M, M, M + mitad - 1, ALTO - M))
            img.put("white", to=(M + mitad + 1, M, ANCHO - M, ALTO - M))

        elif n == "3":
            mitad_a = (ANCHO - M * 2) // 2
            mitad_h = (ALTO - M * 2) // 2
            img.put("white", to=(M, M, M + mitad_a - 1, ALTO - M))
            img.put("white", to=(M + mitad_a + 1, M, ANCHO - M, M + mitad_h - 1))
            img.put("white", to=(M + mitad_a + 1, M + mitad_h + 1, ANCHO - M, ALTO - M))

        else:
            mitad_a = (ANCHO - M * 2) // 2
            mitad_h = (ALTO - M * 2) // 2
            for fila in range(2):
                for col in range(2):
                    x0 = M + col * (mitad_a + 1)
                    y0 = M + fila * (mitad_h + 1)
                    img.put("white", to=(x0, y0, x0 + mitad_a - 1, y0 + mitad_h - 1))

        return img

    def _crear_panel(self, parent):
        t = tk.Text(parent, wrap="word", font=(FUENTE_BASE, self.tamano_actual), bd=1, relief="solid")
        t.bind("<FocusIn>", lambda e, widget=t: self._marcar_activo(widget))
        t.bind("<KeyRelease>", lambda e, widget=t: self._al_escribir(e, widget))
        return t

    def _marcar_activo(self, widget):
        self.pane_activo = widget

    def _al_escribir(self, event, pane):
        if not event.char:
            return
        attrs = (self.tamano_actual, self.negrita_activa, self.cursiva_activa, self.subrayado_activa)
        nombre_tag = self._asegurar_tag(pane, attrs)
        try:
            for t in list(self.tag_attrs.keys()):
                if t != nombre_tag:
                    pane.tag_remove(t, "insert-1c", "insert")
            pane.tag_add(nombre_tag, "insert-1c", "insert")
        except tk.TclError:
            pass

    def cambiar_layout(self, n, contenido_inicial=None):
        contenidos_previos = [p.get("1.0", "end-1c") for p in self.paneles]

        for widget in self.container.winfo_children():
            widget.destroy()
        self.paneles = []
        self.layout_actual = n

        if n == "1":
            self.container.grid_rowconfigure(0, weight=1)
            self.container.grid_columnconfigure(0, weight=1)
            t = self._crear_panel(self.container)
            t.grid(row=0, column=0, sticky="nsew")
            self.paneles = [t]

        elif n == "2":
            self.container.grid_rowconfigure(0, weight=1)
            for c in range(2):
                self.container.grid_columnconfigure(c, weight=1)
                t = self._crear_panel(self.container)
                t.grid(row=0, column=c, sticky="nsew", padx=2)
                self.paneles.append(t)

        elif n == "3":
            self.container.grid_rowconfigure(0, weight=1)
            self.container.grid_rowconfigure(1, weight=1)
            self.container.grid_columnconfigure(0, weight=1)
            self.container.grid_columnconfigure(1, weight=1)

            t1 = self._crear_panel(self.container)
            t1.grid(row=0, column=0, rowspan=2, sticky="nsew", padx=2, pady=1)
            t2 = self._crear_panel(self.container)
            t2.grid(row=0, column=1, sticky="nsew", padx=2, pady=1)
            t3 = self._crear_panel(self.container)
            t3.grid(row=1, column=1, sticky="nsew", padx=2, pady=1)
            self.paneles = [t1, t2, t3]

        else:
            self.container.grid_rowconfigure(0, weight=1)
            self.container.grid_rowconfigure(1, weight=1)
            self.container.grid_columnconfigure(0, weight=1)
            self.container.grid_columnconfigure(1, weight=1)
            for i in range(4):
                t = self._crear_panel(self.container)
                t.grid(row=i // 2, column=i % 2, sticky="nsew", padx=2, pady=1)
                self.paneles.append(t)

        contenidos = contenido_inicial if contenido_inicial is not None else contenidos_previos
        for i, t in enumerate(self.paneles):
            if i < len(contenidos):
                t.insert("1.0", contenidos[i])

        self.pane_activo = self.paneles[0] if self.paneles else None

    # ---------- Formato de texto (tamano, negrita, cursiva, subrayado) ----------

    def _asegurar_tag(self, pane, attrs):
        for nombre, valores in self.tag_attrs.items():
            if valores == attrs:
                return nombre

        nombre = f"fmt_{len(self.tag_attrs)}"
        tamano, negrita, cursiva, subrayado = attrs
        f = tkfont.Font(
            family=FUENTE_BASE, size=tamano,
            weight="bold" if negrita else "normal",
            slant="italic" if cursiva else "roman",
            underline=subrayado,
        )
        pane.tag_configure(nombre, font=f)
        self.tag_attrs[nombre] = attrs
        return nombre

    def _hay_seleccion(self, pane):
        try:
            pane.index("sel.first")
            return True
        except tk.TclError:
            return False

    def _atributos_en_indice(self, pane, index):
        for t in pane.tag_names(index):
            if t in self.tag_attrs:
                return self.tag_attrs[t]
        return (self.tamano_actual, self.negrita_activa, self.cursiva_activa, self.subrayado_activa)

    def _aplicar_formato_a_seleccion(self, transformar):
        pane = self.pane_activo
        inicio = pane.index("sel.first")
        fin = pane.index("sel.last")

        attrs_actuales = self._atributos_en_indice(pane, inicio)
        nuevos_attrs = transformar(attrs_actuales)

        for tag_existente in list(self.tag_attrs.keys()):
            pane.tag_remove(tag_existente, inicio, fin)

        nombre_tag = self._asegurar_tag(pane, nuevos_attrs)
        pane.tag_add(nombre_tag, inicio, fin)

    def _actualizar_boton(self, boton, activo):
        boton.config(relief="sunken" if activo else "raised",
                     bg="#cce5ff" if activo else "SystemButtonFace")

    def toggle_negrita(self):
        pane = self.pane_activo
        if pane and self._hay_seleccion(pane):
            self._aplicar_formato_a_seleccion(lambda a: (a[0], not a[1], a[2], a[3]))
        else:
            self.negrita_activa = not self.negrita_activa
            self._actualizar_boton(self.btn_negrita, self.negrita_activa)

    def toggle_cursiva(self):
        pane = self.pane_activo
        if pane and self._hay_seleccion(pane):
            self._aplicar_formato_a_seleccion(lambda a: (a[0], a[1], not a[2], a[3]))
        else:
            self.cursiva_activa = not self.cursiva_activa
            self._actualizar_boton(self.btn_cursiva, self.cursiva_activa)

    def toggle_subrayado(self):
        pane = self.pane_activo
        if pane and self._hay_seleccion(pane):
            self._aplicar_formato_a_seleccion(lambda a: (a[0], a[1], a[2], not a[3]))
        else:
            self.subrayado_activa = not self.subrayado_activa
            self._actualizar_boton(self.btn_subrayado, self.subrayado_activa)

    def cambiar_tamano(self, event=None):
        nuevo_tamano = int(self.combo_tamano.get())
        pane = self.pane_activo
        if pane and self._hay_seleccion(pane):
            self._aplicar_formato_a_seleccion(lambda a: (nuevo_tamano, a[1], a[2], a[3]))
        else:
            self.tamano_actual = nuevo_tamano

    def _cambiar_tamano_relativo(self, delta):
        actual = int(self.combo_tamano.get())
        if actual in TAMANOS_DISPONIBLES:
            idx = TAMANOS_DISPONIBLES.index(actual)
        else:
            idx = min(range(len(TAMANOS_DISPONIBLES)), key=lambda i: abs(TAMANOS_DISPONIBLES[i] - actual))
        nuevo_idx = max(0, min(len(TAMANOS_DISPONIBLES) - 1, idx + delta))
        self.combo_tamano.set(TAMANOS_DISPONIBLES[nuevo_idx])
        self.cambiar_tamano()

    def disminuir_tamano(self):
        self._cambiar_tamano_relativo(-1)

    def aumentar_tamano(self):
        self._cambiar_tamano_relativo(1)

    # ---------- Guardar / cargar ----------

    def guardar_notas(self):
        contenidos = [p.get("1.0", "end-1c") for p in self.paneles]
        data = {"layout": self.layout_actual, "contenidos": contenidos}
        with open(ARCHIVO_NOTAS, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        self.label_estado.config(text="Guardado")
        self.after(2000, lambda: self.label_estado.config(text=""))

    def cargar_notas(self):
        if os.path.exists(ARCHIVO_NOTAS):
            with open(ARCHIVO_NOTAS, "r", encoding="utf-8") as f:
                data = json.load(f)
            layout = data.get("layout", "1")
            contenidos = data.get("contenidos", [])
            self.cambiar_layout(layout, contenido_inicial=contenidos)
        else:
            self.cambiar_layout("1", contenido_inicial=[])

    def limpiar_pane_activo(self):
        pane = self.pane_activo if self.pane_activo in self.paneles else (
            self.paneles[0] if self.paneles else None
        )
        if pane:
            pane.delete("1.0", "end")
import json
import tkinter as tk
from tkinter import filedialog, messagebox


class HistorialManager:

    def __init__(self, theme_manager):

        self.theme_manager = theme_manager
        self.operaciones = []

        self.panel = None
        self.parent = None

        self.encabezado = None
        self.titulo = None
        self.btn_cerrar = None

        self.lista = None
        self.detalle = None

        self.botones = None
        self.btn_guardar = None
        self.btn_cargar = None
        self.btn_limpiar = None

        self.theme_manager.registrar(
            self._aplicar_tema
        )

    def registrar(
        self,
        categoria,
        operacion,
        entrada,
        resultado,
        pasos=None
    ):

        registro = {
            "categoria": categoria,
            "operacion": operacion,
            "entrada": entrada,
            "resultado": resultado,
            "pasos": pasos or []
        }

        self.operaciones.insert(
            0,
            registro
        )

        self.actualizar()

    def limpiar(self):

        if not self.operaciones:
            return

        respuesta = messagebox.askyesno(
            "Limpiar historial",
            "¿Seguro que quieres eliminar todo el historial?"
        )

        if not respuesta:
            return

        self.operaciones.clear()

        self.actualizar()
        self._limpiar_detalle()

    def guardar(self):

        if not self.operaciones:

            messagebox.showinfo(
                "Historial",
                "No hay operaciones para guardar."
            )

            return

        ruta = filedialog.asksaveasfilename(
            title="Guardar historial",
            defaultextension=".json",
            filetypes=[
                ("Archivo JSON", "*.json"),
                ("Archivo de texto", "*.txt")
            ]
        )

        if not ruta:
            return

        try:

            with open(
                ruta,
                "w",
                encoding="utf-8"
            ) as archivo:

                json.dump(
                    self.operaciones,
                    archivo,
                    ensure_ascii=False,
                    indent=4
                )

            messagebox.showinfo(
                "Historial",
                "Historial guardado correctamente."
            )

        except OSError as error:

            messagebox.showerror(
                "Error",
                f"No se pudo guardar el historial:\n{error}"
            )

    def cargar(self):

        ruta = filedialog.askopenfilename(
            title="Cargar historial",
            filetypes=[
                ("Archivo JSON", "*.json"),
                ("Archivo de texto", "*.txt")
            ]
        )

        if not ruta:
            return

        try:

            with open(
                ruta,
                "r",
                encoding="utf-8"
            ) as archivo:

                datos = json.load(archivo)

            if not isinstance(datos, list):

                raise ValueError(
                    "El archivo no contiene un historial válido."
                )

            self.operaciones = datos

            self.actualizar()

            messagebox.showinfo(
                "Historial",
                "Historial cargado correctamente."
            )

        except (
            OSError,
            json.JSONDecodeError,
            ValueError
        ) as error:

            messagebox.showerror(
                "Error",
                f"No se pudo cargar el historial:\n{error}"
            )

    def crear_panel(self, parent):

        self.parent = parent

        self.panel = tk.Frame(
            parent,
            bd=0,
            highlightthickness=1
        )

        self.encabezado = tk.Frame(
            self.panel,
            height=54
        )

        self.encabezado.pack(
            fill="x"
        )

        self.encabezado.pack_propagate(False)

        self.titulo = tk.Label(
            self.encabezado,
            text="Historial",
            font=("Arial", 15, "bold"),
            anchor="w"
        )

        self.titulo.pack(
            side="left",
            fill="both",
            expand=True,
            padx=(16, 0)
        )

        self.btn_cerrar = tk.Button(
            self.encabezado,
            text="×",
            font=("Arial", 20),
            relief="flat",
            bd=0,
            cursor="hand2",
            padx=14,
            command=self._cerrar_desde_boton
        )

        self.btn_cerrar.pack(
            side="right",
            fill="y"
        )

        contenido = tk.Frame(
            self.panel
        )

        contenido.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=10
        )

        self.lista = tk.Listbox(
            contenido,
            font=("Consolas", 9),
            bd=0,
            relief="flat",
            highlightthickness=1,
            activestyle="none"
        )

        self.lista.pack(
            fill="both",
            expand=True
        )

        self.lista.bind(
            "<Double-Button-1>",
            self._mostrar_detalle
        )

        detalle_frame = tk.Frame(
            self.panel
        )

        detalle_frame.pack(
            fill="x",
            padx=10,
            pady=(0, 8)
        )

        self.detalle = tk.Text(
            detalle_frame,
            height=6,
            font=("Consolas", 9),
            bd=0,
            relief="flat",
            wrap="word",
            state="disabled"
        )

        self.detalle.pack(
            fill="x"
        )

        self.botones = tk.Frame(
            self.panel,
            height=55
        )

        self.botones.pack(
            fill="x",
            padx=10,
            pady=(2, 10)
        )

        self.botones.pack_propagate(False)

        self.btn_guardar = tk.Button(
            self.botones,
            text="Guardar",
            relief="flat",
            bd=0,
            cursor="hand2",
            padx=12,
            command=self.guardar
        )

        self.btn_guardar.pack(
            side="left",
            fill="y"
        )

        self.btn_cargar = tk.Button(
            self.botones,
            text="Cargar",
            relief="flat",
            bd=0,
            cursor="hand2",
            padx=12,
            command=self.cargar
        )

        self.btn_cargar.pack(
            side="left",
            fill="y",
            padx=6
        )

        self.btn_limpiar = tk.Button(
            self.botones,
            text="Limpiar",
            relief="flat",
            bd=0,
            cursor="hand2",
            padx=12,
            command=self.limpiar
        )

        self.btn_limpiar.pack(
            side="right",
            fill="y"
        )

        self._aplicar_tema(
            self.theme_manager.paleta
        )

        self.actualizar()

        return self.panel

    def _cerrar_desde_boton(self):

        if self.parent is None:
            return

        if hasattr(
            self.parent,
            "toggle_historial"
        ):

            self.parent.toggle_historial()

    def actualizar(self):

        if self.lista is None:
            return

        self.lista.delete(
            0,
            "end"
        )

        for i, registro in enumerate(
            self.operaciones,
            start=1
        ):

            categoria = registro.get(
                "categoria",
                "Desconocido"
            )

            operacion = registro.get(
                "operacion",
                "Operación"
            )

            entrada = str(
                registro.get(
                    "entrada",
                    ""
                )
            )

            resultado = str(
                registro.get(
                    "resultado",
                    ""
                )
            )

            texto = (
                f"{i}. [{categoria}] "
                f"{operacion}\n"
                f"   {entrada} → {resultado}"
            )

            self.lista.insert(
                "end",
                texto
            )

    def _mostrar_detalle(
        self,
        event=None
    ):

        if self.lista is None:
            return

        seleccion = self.lista.curselection()

        if not seleccion:
            return

        indice = seleccion[0]

        if indice >= len(
            self.operaciones
        ):
            return

        registro = self.operaciones[
            indice
        ]

        texto = self._formatear_detalle(
            registro
        )

        self.detalle.configure(
            state="normal"
        )

        self.detalle.delete(
            "1.0",
            "end"
        )

        self.detalle.insert(
            "1.0",
            texto
        )

        self.detalle.configure(
            state="disabled"
        )

    def _limpiar_detalle(self):

        if self.detalle is None:
            return

        self.detalle.configure(
            state="normal"
        )

        self.detalle.delete(
            "1.0",
            "end"
        )

        self.detalle.configure(
            state="disabled"
        )

    def _formatear_detalle(
        self,
        registro
    ):

        partes = [
            f"Categoría: {registro.get('categoria', '')}",
            f"Operación: {registro.get('operacion', '')}",
            "",
            "Entrada:",
            str(
                registro.get(
                    "entrada",
                    ""
                )
            ),
            "",
            "Resultado:",
            str(
                registro.get(
                    "resultado",
                    ""
                )
            ),
            "",
            "Proceso:"
        ]

        pasos = registro.get(
            "pasos",
            []
        )

        if pasos:

            partes.extend(
                str(paso)
                for paso in pasos
            )

        else:

            partes.append(
                "Sin pasos registrados."
            )

        return "\n".join(
            partes
        )

    def _aplicar_tema(self, p):

        if self.panel is None:
            return

        self.panel.configure(
            bg=p["bg"],
            highlightbackground=p["borde"]
        )

        self.encabezado.configure(
            bg=p["bg_secundario"]
        )

        self.titulo.configure(
            bg=p["bg_secundario"],
            fg=p["fg"]
        )

        self.btn_cerrar.configure(
            bg=p["bg_secundario"],
            fg=p["fg_suave"],
            activebackground=p["accent_suave"],
            activeforeground=p["accent"]
        )

        self.lista.configure(
            bg=p["bg_secundario"],
            fg=p["fg"],
            selectbackground=p["accent"],
            selectforeground="#ffffff",
            highlightbackground=p["borde"],
            highlightcolor=p["accent"]
        )

        self.detalle.configure(
            bg=p["bg_secundario"],
            fg=p["fg"],
            insertbackground=p["fg"],
            highlightbackground=p["borde"],
            highlightcolor=p["accent"]
        )

        self.botones.configure(
            bg=p["bg"]
        )

        self.btn_guardar.configure(
            bg=p["accent"],
            fg="#ffffff",
            activebackground=p["accent_hover"],
            activeforeground="#ffffff"
        )

        self.btn_cargar.configure(
            bg=p["accent"],
            fg="#ffffff",
            activebackground=p["accent_hover"],
            activeforeground="#ffffff"
        )

        self.btn_limpiar.configure(
            bg=p["bg_secundario"],
            fg=p["accent"],
            activebackground=p["accent_suave"],
            activeforeground=p["accent"]
        )
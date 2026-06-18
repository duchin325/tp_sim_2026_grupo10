import tkinter as tk
from tkinter import ttk, messagebox

from core.simulacion import simular
from utils.validaciones import validar_inputs_simulacion


class AplicacionPeluqueria:
    def __init__(self):
        self.ventana = tk.Tk()
        self.ventana.title("Simulación Peluquería Look")
        self.ventana.resizable(True, True)
        self.ventana.minsize(900, 650)
        self._construir_ui()

    # ------------------------------------------------------------------
    # Construcción de la interfaz
    # ------------------------------------------------------------------

    def _construir_ui(self):
        self._construir_encabezado()
        self._construir_panel_inputs()
        self._construir_panel_resultados()
        self._construir_tabla_eventos()

    def _construir_encabezado(self):
        frame = tk.Frame(self.ventana, bg="#2c3e50", pady=12)
        frame.pack(fill=tk.X)
        tk.Label(
            frame,
            text="Simulación Peluquería Look",
            font=("Helvetica", 18, "bold"),
            bg="#2c3e50",
            fg="white",
        ).pack()

    def _construir_panel_inputs(self):
        frame = tk.LabelFrame(self.ventana, text="Parámetros de entrada", padx=10, pady=10)
        frame.pack(fill=tk.X, padx=15, pady=(12, 6))

        # Días a simular
        tk.Label(frame, text="Días a simular:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=4)
        self.entrada_dias = tk.Entry(frame, width=12)
        self.entrada_dias.insert(0, "100")
        self.entrada_dias.grid(row=0, column=1, sticky=tk.W, padx=5)

        # Valor de X
        tk.Label(frame, text="Valor de X (P(cola > X)):").grid(row=0, column=2, sticky=tk.W, padx=5)
        self.entrada_x = tk.Entry(frame, width=12)
        self.entrada_x.insert(0, "3")
        self.entrada_x.grid(row=0, column=3, sticky=tk.W, padx=5)

        # Cantidad de filas
        tk.Label(frame, text="Filas a mostrar:").grid(row=0, column=4, sticky=tk.W, padx=5)
        self.entrada_filas = tk.Entry(frame, width=12)
        self.entrada_filas.insert(0, "100")
        self.entrada_filas.grid(row=0, column=5, sticky=tk.W, padx=5)

        # Botón Simular
        tk.Button(
            frame,
            text="Simular",
            command=self._on_simular,
            bg="#27ae60",
            fg="white",
            font=("Helvetica", 10, "bold"),
            padx=14,
            pady=4,
            relief=tk.FLAT,
            cursor="hand2",
        ).grid(row=0, column=6, padx=20, pady=4)

    def _construir_panel_resultados(self):
        frame = tk.LabelFrame(self.ventana, text="Resultados", padx=10, pady=10)
        frame.pack(fill=tk.X, padx=15, pady=6)

        definiciones = [
            ("Promedio de recaudación diaria:", "label_recaudacion", "$0.00"),
            (f"P(cola > X personas):",          "label_probabilidad", "0.00%"),
            ("Clientes atendidos (total):",      "label_clientes",     "0"),
            ("Bebidas entregadas (total):",       "label_bebidas",      "0"),
            ("Costo total de bebidas:",           "label_costo_bebidas","$0.00"),
        ]

        for col, (texto, atributo, placeholder) in enumerate(definiciones):
            sub = tk.Frame(frame)
            sub.grid(row=0, column=col, padx=16, sticky=tk.W)
            tk.Label(sub, text=texto, font=("Helvetica", 9, "bold")).pack(anchor=tk.W)
            label = tk.Label(sub, text=placeholder, font=("Helvetica", 11), fg="#2980b9")
            label.pack(anchor=tk.W)
            setattr(self, atributo, label)

    def _construir_tabla_eventos(self):
        frame = tk.LabelFrame(self.ventana, text="Tabla de eventos simulados", padx=8, pady=8)
        frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=(6, 12))

        # Scrollbars
        scroll_y = tk.Scrollbar(frame, orient=tk.VERTICAL)
        scroll_x = tk.Scrollbar(frame, orient=tk.HORIZONTAL)

        self.tabla = ttk.Treeview(
            frame,
            yscrollcommand=scroll_y.set,
            xscrollcommand=scroll_x.set,
            show="headings",
            height=14,
        )
        scroll_y.config(command=self.tabla.yview)
        scroll_x.config(command=self.tabla.xview)

        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        self.tabla.pack(fill=tk.BOTH, expand=True)

        self._configurar_columnas_tabla([
            "Evento", "Reloj", "RND Llegada", "Próx. Llegada",
            "Colorista Estado", "Colorista Fin", "Cola Colorista",
            "Pel.A Estado", "Pel.A Fin", "Cola Pel.A",
            "Pel.B Estado", "Pel.B Fin", "Cola Pel.B",
        ])

    def _configurar_columnas_tabla(self, columnas: list):
        self.tabla["columns"] = columnas
        for col in columnas:
            self.tabla.heading(col, text=col)
            self.tabla.column(col, width=110, anchor=tk.CENTER, minwidth=80)

    # ------------------------------------------------------------------
    # Lógica de la UI
    # ------------------------------------------------------------------

    def _on_simular(self):
        dias_str = self.entrada_dias.get().strip()
        x_str = self.entrada_x.get().strip()
        filas_str = self.entrada_filas.get().strip()

        valido, mensaje_error = validar_inputs_simulacion(dias_str, x_str, filas_str)
        if not valido:
            messagebox.showerror("Error de validación", mensaje_error)
            return

        dias = int(dias_str)
        x = int(x_str)
        cantidad_filas = int(filas_str)

        resultados = simular(dias, x, cantidad_filas)
        self._actualizar_resultados(resultados, x)
        self._actualizar_tabla(resultados.get("filas_tabla", []))

    def _actualizar_resultados(self, resultados: dict, x: int):
        self.label_recaudacion.config(
            text=f"${resultados['promedio_recaudacion']:,.2f}"
        )
        self.label_probabilidad.config(
            text=f"{resultados['probabilidad_mas_de_x'] * 100:.2f}%"
        )
        self.label_clientes.config(text=str(resultados["clientes_atendidos"]))
        self.label_bebidas.config(text=str(resultados["bebidas_entregadas"]))
        self.label_costo_bebidas.config(
            text=f"${resultados['costo_total_bebidas']:,.2f}"
        )
        # Actualizar etiqueta dinámica con el valor de X actual
        self.label_probabilidad.master.winfo_children()[0].config(
            text=f"P(cola > {x} personas):"
        )

    def _actualizar_tabla(self, filas: list):
        self.tabla.delete(*self.tabla.get_children())

        if not filas:
            return

        encabezados = filas[0]
        self._configurar_columnas_tabla(encabezados)

        for fila in filas[1:]:
            self.tabla.insert("", tk.END, values=fila)

    # ------------------------------------------------------------------

    def ejecutar(self):
        self.ventana.mainloop()

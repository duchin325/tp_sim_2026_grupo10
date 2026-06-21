import tkinter as tk
from tkinter import ttk, messagebox

from core.simulacion import simular
from utils.validaciones import validar_inputs_simulacion, validar_entero_positivo


class AplicacionPeluqueria:
    def __init__(self):
        # Estado de paginación
        self.filas_simuladas: list = []  
        self.encabezados: list = []       
        self.pagina_actual: int = 1
        self.filas_por_pagina: int = 10
        self.total_paginas: int = 0

        self.ventana = tk.Tk()
        self.ventana.title("Simulación Peluquería Look")
        self.ventana.resizable(True, True)
        self.ventana.minsize(900, 680)
        self._construir_ui()

    # ------------------------------------------------------------------
    # Construcción de la interfaz
    # ------------------------------------------------------------------

    def _construir_ui(self):
        self._construir_encabezado()
        self._construir_panel_inputs()
        self._construir_panel_resultados()
        self._construir_tabla_eventos()
        self._construir_controles_paginacion()

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

            # --- FILA 0: Parámetros del Sistema (X y N) ---
            tk.Label(frame, text="Tiempo X a simular (Días):").grid(row=0, column=0, sticky=tk.W, padx=5, pady=4)
            self.entrada_dias = tk.Entry(frame, width=12)
            self.entrada_dias.insert(0, "100")
            self.entrada_dias.grid(row=0, column=1, sticky=tk.W, padx=5)

            # Límite de iteraciones N
            tk.Label(frame, text="Iteraciones máximas (N):").grid(row=0, column=2, sticky=tk.W, padx=5)
            self.entrada_n = tk.Entry(frame, width=12)
            self.entrada_n.insert(0, "100000")
            self.entrada_n.grid(row=0, column=3, sticky=tk.W, padx=5)

            tk.Label(frame, text="Umbral de cola (x personas):").grid(row=0, column=4, sticky=tk.W, padx=5)
            self.entrada_x = tk.Entry(frame, width=12)
            self.entrada_x.insert(0, "3")
            self.entrada_x.grid(row=0, column=5, sticky=tk.W, padx=5)

            # --- FILA 1: Visualización e Integración (i, j, h) ---
            tk.Label(frame, text="Iteraciones a mostrar (i):").grid(row=1, column=0, sticky=tk.W, padx=5, pady=4)
            self.entrada_i = tk.Entry(frame, width=12)
            self.entrada_i.insert(0, "100")
            self.entrada_i.grid(row=1, column=1, sticky=tk.W, padx=5)

            tk.Label(frame, text="Hora inicio (j) min:").grid(row=1, column=2, sticky=tk.W, padx=5)
            self.entrada_j = tk.Entry(frame, width=12)
            self.entrada_j.insert(0, "0")
            self.entrada_j.grid(row=1, column=3, sticky=tk.W, padx=5)

            tk.Label(frame, text="Paso Euler (h):").grid(row=1, column=4, sticky=tk.W, padx=5)
            self.entrada_h = tk.Entry(frame, width=12)
            self.entrada_h.insert(0, "1.0")
            self.entrada_h.grid(row=1, column=5, sticky=tk.W, padx=5)

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
            ).grid(row=1, column=6, padx=20, pady=4)

    def _construir_panel_resultados(self):
        frame = tk.LabelFrame(self.ventana, text="Resultados", padx=10, pady=10)
        frame.pack(fill=tk.X, padx=15, pady=6)

        definiciones = [
            ("Promedio de recaudación diaria:", "label_recaudacion",  "$0.00"),
            ("P(cola > X personas):",           "label_probabilidad", "0.00%"),
            ("Clientes atendidos (total):",      "label_clientes",     "0"),
            ("Bebidas entregadas (total):",      "label_bebidas",      "0"),
            ("Costo total de bebidas:",          "label_costo_bebidas","$0.00"),
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
        frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=(6, 2))

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
            "Nº Fila", "Día", "Evento", "Reloj", 
            "RND Lleg.", "Próx. Llegada", 
            "RND Tipo", "Serv. Elegido", 
            "Color. Est", "Color. Fin", "Cola C",
            "Pel.A Est", "Pel.A Fin", "Cola A",
            "Pel.B Est", "Pel.B Fin", "Cola B",
            "Euler t", "Euler D", "Euler dD/dt",
            "Acum. Recaud.", "Cont. Clientes", "Cont. Bebidas"
        ])

        self.tabla.tag_configure(
            "fila_final", 
            background="#eaff00",   
            foreground="#ff1900",   
            font=("Helvetica", 9, "bold") 
        )

    def _construir_controles_paginacion(self):
        frame = tk.Frame(self.ventana, pady=6)
        frame.pack(fill=tk.X, padx=15, pady=(2, 10))

        self.btn_primera = tk.Button(
            frame, text="« Primera", command=self._on_primera_pagina,
            width=9, relief=tk.FLAT, bg="#bdc3c7", cursor="hand2",
        )
        self.btn_primera.pack(side=tk.LEFT, padx=3)

        self.btn_anterior = tk.Button(
            frame, text="‹ Anterior", command=self._on_pagina_anterior,
            width=9, relief=tk.FLAT, bg="#bdc3c7", cursor="hand2",
        )
        self.btn_anterior.pack(side=tk.LEFT, padx=3)

        self.label_pagina = tk.Label(
            frame, text="Página — de —",
            font=("Helvetica", 10), width=18,
        )
        self.label_pagina.pack(side=tk.LEFT, padx=10)

        self.btn_siguiente = tk.Button(
            frame, text="Siguiente ›", command=self._on_pagina_siguiente,
            width=9, relief=tk.FLAT, bg="#bdc3c7", cursor="hand2",
        )
        self.btn_siguiente.pack(side=tk.LEFT, padx=3)

        self.btn_ultima = tk.Button(
            frame, text="Última »", command=self._on_ultima_pagina,
            width=9, relief=tk.FLAT, bg="#bdc3c7", cursor="hand2",
        )
        self.btn_ultima.pack(side=tk.LEFT, padx=3)

        # Deshabilitar hasta que haya resultados
        self._actualizar_controles_paginacion()

    def _configurar_columnas_tabla(self, columnas: list):
        self.tabla["columns"] = columnas
        for col in columnas:
            self.tabla.heading(col, text=col)
            self.tabla.column(col, width=110, anchor=tk.CENTER, minwidth=80)

    # ------------------------------------------------------------------
    # Lógica de la UI — simulación
    # ------------------------------------------------------------------

    def _on_simular(self):
        try:
            dias = int(self.entrada_dias.get().strip())
            n_iteraciones = int(self.entrada_n.get().strip()) 
            x = int(self.entrada_x.get().strip())
            iteraciones_i = int(self.entrada_i.get().strip())
            hora_inicio_j = float(self.entrada_j.get().strip())
            paso_h = float(self.entrada_h.get().strip())
            
            if dias <= 0 or iteraciones_i <= 0 or paso_h <= 0 or hora_inicio_j < 0 or x < 0 or n_iteraciones <= 0:
                raise ValueError()
        except ValueError:
            messagebox.showerror("Error", "Por favor, ingrese valores numéricos válidos. Los días, iteraciones, N y 'h' deben ser mayores a 0.")
            return

        self.filas_por_pagina = 15

        resultados = simular(dias, n_iteraciones, x, iteraciones_i, hora_inicio_j, paso_h)
        self._actualizar_resultados(resultados, x)

        filas_completas = resultados.get("filas_tabla", [])
        if filas_completas:
            self.encabezados = filas_completas[0]
            self.filas_simuladas = filas_completas[1:]
        else:
            self.encabezados = []
            self.filas_simuladas = []

        total = len(self.filas_simuladas)
        self.total_paginas = max(1, -(-total // self.filas_por_pagina)) 
        self._ir_a_pagina(1)

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
        self.label_probabilidad.master.winfo_children()[0].config(
            text=f"P(cola > {x} personas):"
        )

    # ------------------------------------------------------------------
    # Lógica de paginación
    # ------------------------------------------------------------------

    def _ir_a_pagina(self, pagina: int):
        if self.total_paginas == 0:
            return
        self.pagina_actual = max(1, min(pagina, self.total_paginas))

        inicio = (self.pagina_actual - 1) * self.filas_por_pagina
        fin = inicio + self.filas_por_pagina
        filas_visibles = self.filas_simuladas[inicio:fin]

        self._renderizar_tabla(filas_visibles)
        self._actualizar_controles_paginacion()

    def _on_primera_pagina(self):
        self._ir_a_pagina(1)

    def _on_pagina_anterior(self):
        self._ir_a_pagina(self.pagina_actual - 1)

    def _on_pagina_siguiente(self):
        self._ir_a_pagina(self.pagina_actual + 1)

    def _on_ultima_pagina(self):
        self._ir_a_pagina(self.total_paginas)

    def _renderizar_tabla(self, filas: list):
        self.tabla.delete(*self.tabla.get_children())
        if self.encabezados:
            self._configurar_columnas_tabla(self.encabezados)
            
        for fila in filas:
            if len(fila) > 2 and fila[2] == "FIN SIMULACIÓN":
                self.tabla.insert("", tk.END, values=fila, tags=("fila_final",))
            else:
                self.tabla.insert("", tk.END, values=fila)

    def _actualizar_controles_paginacion(self):
        hay_resultados = self.total_paginas > 0

        if hay_resultados:
            self.label_pagina.config(
                text=f"Página {self.pagina_actual} de {self.total_paginas}"
            )
        else:
            self.label_pagina.config(text="Página — de —")

        es_primera = (not hay_resultados) or (self.pagina_actual <= 1)
        es_ultima = (not hay_resultados) or (self.pagina_actual >= self.total_paginas)

        self.btn_primera.config(state=tk.DISABLED if es_primera else tk.NORMAL)
        self.btn_anterior.config(state=tk.DISABLED if es_primera else tk.NORMAL)
        self.btn_siguiente.config(state=tk.DISABLED if es_ultima else tk.NORMAL)
        self.btn_ultima.config(state=tk.DISABLED if es_ultima else tk.NORMAL)

    def ejecutar(self):
        self.ventana.mainloop()

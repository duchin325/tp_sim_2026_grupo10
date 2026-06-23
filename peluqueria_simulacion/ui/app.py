import tkinter as tk
from tkinter import ttk, messagebox

from core.simulacion import simular
from ui.euler_dialog import EulerDialog
from utils.validaciones import validar_inputs_simulacion, validar_entero_positivo


# Nombre legible para cada tipo de servidor
_NOMBRE_TIPO = {
    "colorista": "Colorista",
    "peluquero_a": "Peluquero A",
    "peluquero_b": "Peluquero B",
}


class AplicacionPeluqueria:
    def __init__(self):
        # Estado de paginación
        self.filas_simuladas: list = []   # filas filtradas (sin encabezado)
        self.encabezados: list = []        # fila 0 de la tabla
        self.pagina_actual: int = 1
        self.filas_por_pagina: int = 50
        self.total_paginas: int = 0

        # Datos de objetos temporales (nro_fila -> lista de clientes)
        self.objetos_por_fila: dict = {}
        self.h_euler_actual: float = 1.0

        self.ventana = tk.Tk()
        self.ventana.title("Simulación Peluquería Look — TP5 Grupo 10")
        self.ventana.resizable(True, True)
        self.ventana.minsize(1100, 800)
        self._configurar_estilos()
        self._construir_ui()

    # ------------------------------------------------------------------
    # Construcción de la interfaz
    # ------------------------------------------------------------------

    def _configurar_estilos(self):
        """Configura el tema y estilos de la tabla para bordes visibles."""
        estilo = ttk.Style()
        estilo.theme_use("clam")

        # Encabezados con fondo oscuro, texto blanco y borde negro sólido
        estilo.configure(
            "Treeview.Heading",
            background="#2c3e50",
            foreground="white",
            font=("Helvetica", 8, "bold"),
            relief="solid",
            borderwidth=1,
            bordercolor="black",
        )
        estilo.map(
            "Treeview.Heading",
            background=[("active", "#34495e")],
        )

        # Celdas con bordes negros visibles entre filas y columnas
        estilo.configure(
            "Treeview",
            background="white",
            fieldbackground="white",
            foreground="black",
            rowheight=24,
            borderwidth=1,
            relief="solid",
            font=("Helvetica", 8),
        )
        # Configurar el layout del item para agregar bordes a cada celda
        estilo.layout("Treeview", [
            ("Treeview.treearea", {"sticky": "nswe", "border": 1}),
        ])

        # Filas alternas para mejor legibilidad
        estilo.map(
            "Treeview",
            background=[("selected", "#3498db")],
            foreground=[("selected", "white")],
        )

    def _construir_ui(self):
        self._construir_encabezado()
        self._construir_panel_inputs()
        self._construir_panel_formulas()
        self._construir_panel_resultados()
        self._construir_tabla_eventos()
        self._construir_controles_paginacion()
        self._construir_panel_objetos_temporales()

    def _construir_encabezado(self):
        frame = tk.Frame(self.ventana, bg="#2c3e50", pady=10)
        frame.pack(fill=tk.X)
        tk.Label(
            frame,
            text="Simulación Peluquería Look",
            font=("Helvetica", 16, "bold"),
            bg="#2c3e50",
            fg="white",
        ).pack()
        tk.Label(
            frame,
            text="TP5 — Simulación de Eventos Discretos + Integración Euler",
            font=("Helvetica", 9),
            bg="#2c3e50",
            fg="#bdc3c7",
        ).pack()

    def _construir_panel_inputs(self):
        frame = tk.LabelFrame(self.ventana, text="Parámetros de entrada", padx=10, pady=8)
        frame.pack(fill=tk.X, padx=12, pady=(8, 4))

        # --- Fila 1: Parámetros de simulación ---
        lbl_style = {"font": ("Helvetica", 9)}
        entry_width = 10

        # N Días
        tk.Label(frame, text="N (Días a simular):", **lbl_style).grid(row=0, column=0, sticky=tk.W, padx=4, pady=3)
        self.entrada_n_dias = tk.Entry(frame, width=entry_width)
        self.entrada_n_dias.insert(0, "100")
        self.entrada_n_dias.grid(row=0, column=1, sticky=tk.W, padx=4)

        # X cola
        tk.Label(frame, text="X (Umbral cola):", **lbl_style).grid(row=0, column=2, sticky=tk.W, padx=4)
        self.entrada_x_cola = tk.Entry(frame, width=entry_width)
        self.entrada_x_cola.insert(0, "3")
        self.entrada_x_cola.grid(row=0, column=3, sticky=tk.W, padx=4)

        # h Euler
        tk.Label(frame, text="h (Paso Euler):", **lbl_style).grid(row=0, column=4, sticky=tk.W, padx=4)
        self.entrada_h_euler = tk.Entry(frame, width=entry_width)
        self.entrada_h_euler.insert(0, "1")
        self.entrada_h_euler.grid(row=0, column=5, sticky=tk.W, padx=4)

        # --- Fila 2: Parámetros de visualización ---

        # j hora
        tk.Label(frame, text="j (Minuto desde):", **lbl_style).grid(row=1, column=0, sticky=tk.W, padx=4, pady=3)
        self.entrada_hora_j = tk.Entry(frame, width=entry_width)
        self.entrada_hora_j.insert(0, "0")
        self.entrada_hora_j.grid(row=1, column=1, sticky=tk.W, padx=4)

        # i iteraciones
        tk.Label(frame, text="i (Filas a mostrar):", **lbl_style).grid(row=1, column=2, sticky=tk.W, padx=4)
        self.entrada_iter_i = tk.Entry(frame, width=entry_width)
        self.entrada_iter_i.insert(0, "100")
        self.entrada_iter_i.grid(row=1, column=3, sticky=tk.W, padx=4)

        # Filas por página
        tk.Label(frame, text="Filas por página:", **lbl_style).grid(row=1, column=4, sticky=tk.W, padx=4)
        self.entrada_filas_por_pagina = tk.Entry(frame, width=entry_width)
        self.entrada_filas_por_pagina.insert(0, "50")
        self.entrada_filas_por_pagina.grid(row=1, column=5, sticky=tk.W, padx=4)

        # Botón Simular
        tk.Button(
            frame,
            text="▶  Simular",
            command=self._on_simular,
            bg="#27ae60",
            fg="white",
            font=("Helvetica", 10, "bold"),
            padx=16,
            pady=8,
            relief=tk.FLAT,
            cursor="hand2",
        ).grid(row=0, column=6, rowspan=2, padx=16, pady=4, sticky="ns")

    def _construir_panel_formulas(self):
        frame = tk.LabelFrame(self.ventana, text="Fórmulas utilizadas", padx=10, pady=6)
        frame.pack(fill=tk.X, padx=12, pady=2)

        formulas = [
            "Recaudación promedio:  R̄ = (1/N) · Σ Rₖ",
            "P(cola > X):  P = (días con máx_cola > X) / N",
            "ED demora:  dD/dt = C + 0.2·T + t²",
            "Euler:  D_{n+1} = D_n + h · f(t_n, D_n),  hasta D ≥ T",
        ]
        texto = "    |    ".join(formulas)
        tk.Label(frame, text=texto, font=("Consolas", 8), fg="#555555").pack(anchor=tk.W)

    def _construir_panel_resultados(self):
        frame = tk.LabelFrame(self.ventana, text="Resultados de la simulación", padx=10, pady=8)
        frame.pack(fill=tk.X, padx=12, pady=2)

        definiciones = [
            ("Recaudación diaria promedio:", "label_recaudacion",  "$0.00"),
            ("P(cola > X personas):",        "label_probabilidad", "0.00%"),
            ("Clientes atendidos (total):",   "label_clientes",     "0"),
            ("Bebidas entregadas (total):",   "label_bebidas",      "0"),
            ("Costo total de bebidas:",       "label_costo_bebidas","$0.00"),
            ("Iteraciones totales:",          "label_iteraciones",  "0"),
            ("Días simulados:",               "label_dias_sim",     "0"),
        ]

        for col, (texto, atributo, placeholder) in enumerate(definiciones):
            sub = tk.Frame(frame)
            sub.grid(row=0, column=col, padx=10, sticky=tk.W)
            tk.Label(sub, text=texto, font=("Helvetica", 8, "bold")).pack(anchor=tk.W)
            label = tk.Label(sub, text=placeholder, font=("Helvetica", 10), fg="#2980b9")
            label.pack(anchor=tk.W)
            setattr(self, atributo, label)

    def _construir_tabla_eventos(self):
        frame = tk.LabelFrame(self.ventana, text="Vector de Estado — Tabla de eventos", padx=6, pady=6)
        frame.pack(fill=tk.BOTH, expand=True, padx=12, pady=(2, 2))

        scroll_y = tk.Scrollbar(frame, orient=tk.VERTICAL)
        scroll_x = tk.Scrollbar(frame, orient=tk.HORIZONTAL)

        self.tabla = ttk.Treeview(
            frame,
            yscrollcommand=scroll_y.set,
            xscrollcommand=scroll_x.set,
            show="headings",
            height=12,
        )
        scroll_y.config(command=self.tabla.yview)
        scroll_x.config(command=self.tabla.xview)

        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        self.tabla.pack(fill=tk.BOTH, expand=True)

        # Placeholder columns
        self._configurar_columnas_tabla([
            "Nro", "Día", "Evento", "Reloj (min)", "Reloj (HH:MM)",
            "RND Llegada", "T. Entre Lleg.", "Próx. Llegada",
            "RND Tipo", "Tipo Asignado",
            "Col. Estado", "Col. Cola", "Col. Fin At.",
            "PA Estado", "PA Cola", "PA Fin At.",
            "PB Estado", "PB Cola", "PB Fin At.",
            "Próx. Eventos",
            "Acum. Recaud.", "Acum. Bebidas", "Acum. Costo Beb.",
            "Clientes Atend.", "Máx Cola Total",
        ])

        # Vincular selección de fila al panel de objetos temporales
        self.tabla.bind("<<TreeviewSelect>>", self._on_seleccion_fila)

        # Label informativo
        tk.Label(
            frame,
            text="Seleccioná una fila para ver los objetos temporales (clientes) presentes en ese instante.",
            font=("Helvetica", 8, "italic"), fg="#7f8c8d",
        ).pack(anchor=tk.W, pady=(2, 0))

    def _construir_controles_paginacion(self):
        frame = tk.Frame(self.ventana, pady=4)
        frame.pack(fill=tk.X, padx=12, pady=(0, 2))

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

        # Info de filtrado
        self.label_filtro_info = tk.Label(
            frame, text="",
            font=("Helvetica", 9), fg="#7f8c8d",
        )
        self.label_filtro_info.pack(side=tk.RIGHT, padx=10)

        self._actualizar_controles_paginacion()

    def _construir_panel_objetos_temporales(self):
        """Panel inferior que muestra tarjetas de clientes activos en la fila seleccionada."""
        self.frame_objetos = tk.LabelFrame(
            self.ventana,
            text="Objetos temporales presentes",
            padx=8, pady=6,
        )
        self.frame_objetos.pack(fill=tk.X, padx=12, pady=(0, 8))

        # Título dinámico
        self.label_objetos_titulo = tk.Label(
            self.frame_objetos,
            text="Seleccioná una fila del vector de estado para ver los clientes activos.",
            font=("Helvetica", 9, "italic"), fg="#7f8c8d",
        )
        self.label_objetos_titulo.pack(anchor=tk.W, pady=(0, 4))

        # Canvas con scroll horizontal para las tarjetas
        canvas_frame = tk.Frame(self.frame_objetos)
        canvas_frame.pack(fill=tk.X, expand=False)

        self.canvas_objetos = tk.Canvas(canvas_frame, height=170, bg="#f0f0f0", highlightthickness=0)
        scroll_x_obj = tk.Scrollbar(canvas_frame, orient=tk.HORIZONTAL, command=self.canvas_objetos.xview)
        self.canvas_objetos.configure(xscrollcommand=scroll_x_obj.set)

        scroll_x_obj.pack(side=tk.BOTTOM, fill=tk.X)
        self.canvas_objetos.pack(fill=tk.X, expand=True)

        # Frame interno dentro del canvas
        self.frame_tarjetas = tk.Frame(self.canvas_objetos, bg="#f0f0f0")
        self.canvas_window = self.canvas_objetos.create_window(
            (0, 0), window=self.frame_tarjetas, anchor=tk.NW
        )

        self.frame_tarjetas.bind("<Configure>", self._on_tarjetas_configure)

    def _on_tarjetas_configure(self, event=None):
        """Actualiza la región de scroll del canvas cuando cambian las tarjetas."""
        self.canvas_objetos.configure(scrollregion=self.canvas_objetos.bbox("all"))

    def _configurar_columnas_tabla(self, columnas: list):
        self.tabla["columns"] = columnas

        # Anchos personalizados por tipo de columna
        anchos = {
            "Nro": 50, "Día": 40, "Evento": 110,
            "Reloj (min)": 80, "Reloj (HH:MM)": 80,
            "Próx. Eventos": 200,
        }

        for col in columnas:
            self.tabla.heading(col, text=col)
            ancho = anchos.get(col, 95)
            self.tabla.column(col, width=ancho, anchor=tk.CENTER, minwidth=60, stretch=False)

    # ------------------------------------------------------------------
    # Lógica de la UI — simulación
    # ------------------------------------------------------------------

    def _on_simular(self):
        n_dias_str = self.entrada_n_dias.get().strip()
        x_cola_str = self.entrada_x_cola.get().strip()
        h_euler_str = self.entrada_h_euler.get().strip()
        hora_j_str = self.entrada_hora_j.get().strip()
        iter_i_str = self.entrada_iter_i.get().strip()
        filas_pp_str = self.entrada_filas_por_pagina.get().strip()

        # Validar inputs de simulación
        valido, error = validar_inputs_simulacion(
            n_dias_str, x_cola_str, h_euler_str, hora_j_str, iter_i_str
        )
        if not valido:
            messagebox.showerror("Error de validación", error)
            return

        valido, error = validar_entero_positivo(filas_pp_str, "Filas por página")
        if not valido:
            messagebox.showerror("Error de validación", error)
            return

        n_dias = int(n_dias_str)
        x_cola = int(x_cola_str)
        h_euler = float(h_euler_str)
        hora_j = int(hora_j_str)
        iter_i = int(iter_i_str)
        self.filas_por_pagina = int(filas_pp_str)
        self.h_euler_actual = h_euler

        # Ejecutar simulación
        resultados = simular(n_dias, x_cola, h_euler)

        # Actualizar panel de resultados
        self._actualizar_resultados(resultados, x_cola)

        # Guardar objetos temporales
        self.objetos_por_fila = resultados.get("objetos_por_fila", {})

        # Separar encabezados del resto
        filas_completas = resultados.get("filas_tabla", [])
        if filas_completas:
            self.encabezados = filas_completas[0]
            todas_las_filas = filas_completas[1:]
        else:
            self.encabezados = []
            todas_las_filas = []

        # --- Filtrado: i filas desde minuto j + última fila ---
        if todas_las_filas:
            # Columna "Reloj (min)" es el índice 3 (0-indexed)
            filas_desde_j = [f for f in todas_las_filas if float(f[3]) >= hora_j]
            filas_filtradas = filas_desde_j[:iter_i]

            # Agregar última fila si no está incluida
            ultima_fila = todas_las_filas[-1]
            if not filas_filtradas or filas_filtradas[-1] != ultima_fila:
                filas_filtradas.append(ultima_fila)

            self.filas_simuladas = filas_filtradas
            self.label_filtro_info.config(
                text=f"Mostrando {len(filas_filtradas)} filas (desde min {hora_j}, "
                     f"máx {iter_i}) de {len(todas_las_filas)} totales"
            )
        else:
            self.filas_simuladas = []
            self.label_filtro_info.config(text="")

        total = len(self.filas_simuladas)
        self.total_paginas = max(1, -(-total // self.filas_por_pagina))
        self._ir_a_pagina(1)

        # Limpiar panel de objetos
        self._limpiar_tarjetas()
        self.label_objetos_titulo.config(
            text="Seleccioná una fila del vector de estado para ver los clientes activos."
        )

    def _actualizar_resultados(self, resultados: dict, x_cola: int):
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
        self.label_iteraciones.config(text=str(resultados.get("iteraciones_totales", "?")))
        self.label_dias_sim.config(text=str(resultados.get("dias_simulados", "?")))

        # Actualizar label de probabilidad con el valor de X
        self.label_probabilidad.master.winfo_children()[0].config(
            text=f"P(cola > {x_cola} personas):"
        )

    # ------------------------------------------------------------------
    # Panel de objetos temporales
    # ------------------------------------------------------------------

    def _on_seleccion_fila(self, event=None):
        """Cuando se selecciona una fila, mostrar tarjetas de clientes activos."""
        seleccion = self.tabla.selection()
        if not seleccion:
            return

        item = seleccion[0]
        valores = self.tabla.item(item, "values")
        if not valores:
            return

        nro_fila = int(valores[0])
        reloj = valores[3]
        dia = valores[1]

        clientes = self.objetos_por_fila.get(nro_fila, [])

        self._limpiar_tarjetas()

        if not clientes:
            self.label_objetos_titulo.config(
                text=f"No hay objetos temporales en T = {reloj} min (Iteración {nro_fila}) — Día {dia}",
                fg="#e74c3c",
            )
            return

        self.label_objetos_titulo.config(
            text=f"OBJETOS PRESENTES EN T = {reloj} MIN (ITERACIÓN {nro_fila}) — Día {dia}",
            font=("Helvetica", 9, "bold"), fg="#2c3e50",
        )

        for cliente in clientes:
            self._crear_tarjeta_cliente(cliente)

        self._on_tarjetas_configure()

    def _limpiar_tarjetas(self):
        """Elimina todas las tarjetas del panel."""
        for widget in self.frame_tarjetas.winfo_children():
            widget.destroy()

    def _crear_tarjeta_cliente(self, cliente):
        """Crea una tarjeta visual para un cliente."""
        tipo_nombre = _NOMBRE_TIPO.get(cliente.tipo, cliente.tipo)

        # Colores según estado
        colores_estado = {
            "en_cola": ("#f39c12", "#fef9e7"),      # naranja
            "siendo_atendido": ("#27ae60", "#eafaf1"), # verde
            "atendido": ("#95a5a6", "#f2f3f4"),       # gris
        }
        color_borde, color_fondo = colores_estado.get(
            cliente.estado, ("#3498db", "#eaf2f8")
        )

        estado_texto = {
            "en_cola": f"En cola {tipo_nombre}",
            "siendo_atendido": f"Atendido por {tipo_nombre}",
            "atendido": "Atendido",
        }

        tarjeta = tk.Frame(
            self.frame_tarjetas,
            bg=color_fondo, bd=2,
            relief=tk.SOLID,
            highlightbackground=color_borde,
            highlightthickness=2,
            padx=10, pady=8,
        )
        tarjeta.pack(side=tk.LEFT, padx=5, pady=4)

        # Título
        tk.Label(
            tarjeta, text=f"Cliente #{cliente.numero}",
            font=("Helvetica", 10, "bold"), bg=color_fondo, fg="#2c3e50",
        ).pack(anchor=tk.W)

        # Estado con color
        tk.Label(
            tarjeta,
            text=estado_texto.get(cliente.estado, cliente.estado),
            font=("Helvetica", 9, "bold"), bg=color_fondo, fg=color_borde,
        ).pack(anchor=tk.W, pady=(2, 4))

        # Atributos
        atributos = [
            f"Llegó: {cliente.tiempo_llegada:.2f} min",
        ]

        if cliente.estado == "en_cola":
            espera = cliente.tiempo_espera
            atributos.append(f"Esperando: {espera:.2f} min")
            hora_ini_refrig = cliente.tiempo_llegada + 30  # 30 minutos después de llegar
            atributos.append(f"Hora Ini. Refrig: {hora_ini_refrig:.2f} min")
        elif cliente.estado == "siendo_atendido":
            atributos.append(f"Inicio at.: {cliente.tiempo_inicio_atencion:.2f} min")
            if cliente.demora_calculada > 0:
                atributos.append(f"Demora Euler: {cliente.demora_calculada:.2f} min")
                atributos.append(f"C={cliente.longitud_cola_al_inicio}")

        for attr in atributos:
            tk.Label(
                tarjeta, text=attr,
                font=("Helvetica", 8), bg=color_fondo, fg="#555555",
            ).pack(anchor=tk.W)

        # Botón "Ver tabla Euler" solo si tiene pasos
        if cliente.pasos_euler:
            tk.Button(
                tarjeta,
                text="Ver tabla Euler",
                command=lambda c=cliente: self._abrir_euler_dialog(c),
                bg=color_borde, fg="white",
                font=("Helvetica", 8, "bold"),
                relief=tk.FLAT, cursor="hand2",
                padx=8, pady=2,
            ).pack(anchor=tk.W, pady=(6, 0))

    def _abrir_euler_dialog(self, cliente):
        """Abre la ventana de detalle de integración Euler para un cliente."""
        EulerDialog(self.ventana, cliente, self.h_euler_actual)

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

        # Configurar colores alternados (zebra striping)
        self.tabla.tag_configure("par", background="#e8ecf1")
        self.tabla.tag_configure("impar", background="white")
        self.tabla.tag_configure("ultima", background="#d5f5e3", font=("Helvetica", 8, "bold"))

        for i, fila in enumerate(filas):
            # Marcar la última fila de la simulación con color distinto
            es_ultima = (fila == self.filas_simuladas[-1]) if self.filas_simuladas else False
            if es_ultima:
                tag = "ultima"
            else:
                tag = "par" if i % 2 == 0 else "impar"
            self.tabla.insert("", tk.END, values=fila, tags=(tag,))

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

    # ------------------------------------------------------------------

    def ejecutar(self):
        self.ventana.mainloop()

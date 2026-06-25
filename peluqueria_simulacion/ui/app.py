import re
import tkinter as tk
from tkinter import ttk, messagebox

from core.simulacion import simular
from ui.euler_dialog import EulerDialog
from utils.validaciones import (
    validar_inputs_simulacion,
    validar_entero_positivo,
    validar_porcentajes,
    validar_limites_llegada,
    validar_t_euler,
)


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

        # Cache de encabezados para evitar reconfigurar columnas en cada página
        self._ultimo_encabezados: list = []

        self.ventana = tk.Tk()
        self.ventana.geometry("1600x1000")
        self.ventana.title("Simulación Peluquería Look — TP5 Grupo 10")
        self.ventana.resizable(True, True)
        self.ventana.minsize(1400, 900)
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
        # Contenedor principal con grid para alinear cajas + botón
        contenedor = tk.Frame(self.ventana)
        contenedor.pack(fill=tk.X, padx=12, pady=(8, 4))
        contenedor.columnconfigure(0, weight=1)  # Cajas de parámetros
        contenedor.columnconfigure(1, weight=0)  # Botón

        # --- Frame izquierdo: todas las cajas de parámetros ---
        frame_params = tk.Frame(contenedor)
        frame_params.grid(row=0, column=0, sticky="nsew")

        lbl_style = {"font": ("Helvetica", 9)}
        entry_width = 10

        # ═══════════════════════════════════════════════════════
        # Caja 1: Parámetros de simulación
        # ═══════════════════════════════════════════════════════
        caja_sim = tk.LabelFrame(frame_params, text="Parámetros de simulación", padx=8, pady=6)
        caja_sim.grid(row=0, column=0, padx=(0, 6), pady=2, sticky="nsew")

        # N Días
        tk.Label(caja_sim, text="N (Días):", **lbl_style).grid(row=0, column=0, sticky=tk.W, padx=3, pady=2)
        self.entrada_n_dias = tk.Entry(caja_sim, width=entry_width)
        self.entrada_n_dias.insert(0, "100")
        self.entrada_n_dias.grid(row=0, column=1, sticky=tk.W, padx=3)

        # X cola
        tk.Label(caja_sim, text="X (Umbral cola):", **lbl_style).grid(row=1, column=0, sticky=tk.W, padx=3, pady=2)
        self.entrada_x_cola = tk.Entry(caja_sim, width=entry_width)
        self.entrada_x_cola.insert(0, "3")
        self.entrada_x_cola.grid(row=1, column=1, sticky=tk.W, padx=3)

        # h Euler
        tk.Label(caja_sim, text="h (Paso Euler):", **lbl_style).grid(row=2, column=0, sticky=tk.W, padx=3, pady=2)
        self.entrada_h_euler = tk.Entry(caja_sim, width=entry_width)
        self.entrada_h_euler.insert(0, "1")
        self.entrada_h_euler.grid(row=2, column=1, sticky=tk.W, padx=3)

        # ═══════════════════════════════════════════════════════
        # Caja 2: Parámetros de visualización
        # ═══════════════════════════════════════════════════════
        caja_vis = tk.LabelFrame(frame_params, text="Visualización", padx=8, pady=6)
        caja_vis.grid(row=0, column=1, padx=6, pady=2, sticky="nsew")

        # j hora
        tk.Label(caja_vis, text="j (Minuto desde):", **lbl_style).grid(row=0, column=0, sticky=tk.W, padx=3, pady=2)
        self.entrada_hora_j = tk.Entry(caja_vis, width=entry_width)
        self.entrada_hora_j.insert(0, "0")
        self.entrada_hora_j.grid(row=0, column=1, sticky=tk.W, padx=3)

        # i iteraciones
        tk.Label(caja_vis, text="i (Filas a mostrar):", **lbl_style).grid(row=1, column=0, sticky=tk.W, padx=3, pady=2)
        self.entrada_iter_i = tk.Entry(caja_vis, width=entry_width)
        self.entrada_iter_i.insert(0, "500")
        self.entrada_iter_i.grid(row=1, column=1, sticky=tk.W, padx=3)

        # Filas por página
        tk.Label(caja_vis, text="Filas por página:", **lbl_style).grid(row=2, column=0, sticky=tk.W, padx=3, pady=2)
        self.entrada_filas_por_pagina = tk.Entry(caja_vis, width=entry_width)
        self.entrada_filas_por_pagina.insert(0, "50")
        self.entrada_filas_por_pagina.grid(row=2, column=1, sticky=tk.W, padx=3)

        # ═══════════════════════════════════════════════════════
        # Caja 3: Porcentajes de atención
        # ═══════════════════════════════════════════════════════
        caja_porc = tk.LabelFrame(frame_params, text="Porcentajes de atención", padx=8, pady=6)
        caja_porc.grid(row=0, column=2, padx=6, pady=2, sticky="nsew")

        # % Colorista
        tk.Label(caja_porc, text="% Colorista:", **lbl_style).grid(row=0, column=0, sticky=tk.W, padx=3, pady=2)
        self.entrada_porc_colorista = tk.Entry(caja_porc, width=entry_width)
        self.entrada_porc_colorista.insert(0, "15")
        self.entrada_porc_colorista.grid(row=0, column=1, sticky=tk.W, padx=3)
        self.entrada_porc_colorista.bind("<KeyRelease>", self._actualizar_porc_pb)

        # % Peluquero A
        tk.Label(caja_porc, text="% Peluquero A:", **lbl_style).grid(row=1, column=0, sticky=tk.W, padx=3, pady=2)
        self.entrada_porc_peluquero_a = tk.Entry(caja_porc, width=entry_width)
        self.entrada_porc_peluquero_a.insert(0, "45")
        self.entrada_porc_peluquero_a.grid(row=1, column=1, sticky=tk.W, padx=3)
        self.entrada_porc_peluquero_a.bind("<KeyRelease>", self._actualizar_porc_pb)

        # % Peluquero B (label calculado)
        tk.Label(caja_porc, text="% Peluquero B:", **lbl_style).grid(row=2, column=0, sticky=tk.W, padx=3, pady=2)
        self.label_porc_peluquero_b = tk.Label(caja_porc, text="40.0%", font=("Helvetica", 10, "bold"), fg="#2980b9")
        self.label_porc_peluquero_b.grid(row=2, column=1, sticky=tk.W, padx=3)

        # ═══════════════════════════════════════════════════════
        # Caja 4: Tiempo entre llegadas
        # ═══════════════════════════════════════════════════════
        caja_lleg = tk.LabelFrame(frame_params, text="Tiempo entre llegadas U(A,B)", padx=8, pady=6)
        caja_lleg.grid(row=0, column=3, padx=6, pady=2, sticky="nsew")

        # A (Llegada mín)
        tk.Label(caja_lleg, text="A (mín):", **lbl_style).grid(row=0, column=0, sticky=tk.W, padx=3, pady=2)
        self.entrada_llegada_min = tk.Entry(caja_lleg, width=entry_width)
        self.entrada_llegada_min.insert(0, "2")
        self.entrada_llegada_min.grid(row=0, column=1, sticky=tk.W, padx=3)

        # B (Llegada máx)
        tk.Label(caja_lleg, text="B (máx):", **lbl_style).grid(row=1, column=0, sticky=tk.W, padx=3, pady=2)
        self.entrada_llegada_max = tk.Entry(caja_lleg, width=entry_width)
        self.entrada_llegada_max.insert(0, "12")
        self.entrada_llegada_max.grid(row=1, column=1, sticky=tk.W, padx=3)

        # ═══════════════════════════════════════════════════════
        # Caja 5: Constantes T (Euler)
        # ═══════════════════════════════════════════════════════
        caja_t = tk.LabelFrame(frame_params, text="Constantes T (Euler)", padx=8, pady=6)
        caja_t.grid(row=0, column=4, padx=(6, 0), pady=2, sticky="nsew")

        # T Colorista
        tk.Label(caja_t, text="T Colorista:", **lbl_style).grid(row=0, column=0, sticky=tk.W, padx=3, pady=2)
        self.entrada_t_colorista = tk.Entry(caja_t, width=entry_width)
        self.entrada_t_colorista.insert(0, "180")
        self.entrada_t_colorista.grid(row=0, column=1, sticky=tk.W, padx=3)

        # T Peluqueros
        tk.Label(caja_t, text="T Peluqueros:", **lbl_style).grid(row=1, column=0, sticky=tk.W, padx=3, pady=2)
        self.entrada_t_peluqueros = tk.Entry(caja_t, width=entry_width)
        self.entrada_t_peluqueros.insert(0, "130")
        self.entrada_t_peluqueros.grid(row=1, column=1, sticky=tk.W, padx=3)

        # --- Botón Simular (a la derecha, separado) ---
        frame_boton = tk.Frame(contenedor)
        frame_boton.grid(row=0, column=1, padx=(20, 0), sticky="ns")

        self.btn_simular = tk.Button(
            frame_boton,
            text="▶  Simular",
            command=self._on_simular,
            bg="#27ae60",
            fg="white",
            font=("Helvetica", 12, "bold"),
            padx=24,
            pady=16,
            relief=tk.FLAT,
            cursor="hand2",
        )
        self.btn_simular.pack(expand=True, fill=tk.BOTH, padx=4, pady=4)

    def _actualizar_porc_pb(self, event=None):
        """Actualiza en tiempo real el label de % Peluquero B."""
        try:
            porc_col = float(self.entrada_porc_colorista.get().strip() or "0")
            porc_pa = float(self.entrada_porc_peluquero_a.get().strip() or "0")
            porc_pb = 100 - porc_col - porc_pa
            if porc_pb < 0:
                self.label_porc_peluquero_b.config(text="Error!", fg="#e74c3c")
            else:
                self.label_porc_peluquero_b.config(text=f"{porc_pb:.1f}%", fg="#2980b9")
        except ValueError:
            self.label_porc_peluquero_b.config(text="—", fg="#e74c3c")

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
        """Construye la tabla única del vector de estado con scroll horizontal y vertical."""
        frame = tk.LabelFrame(self.ventana, text="Vector de Estado — Tabla de eventos", padx=6, pady=6)
        frame.pack(fill=tk.BOTH, expand=True, padx=12, pady=(2, 2))

        # --- Barra de encabezados de grupo (para clientes) ---
        self.frame_grupo_header = tk.Frame(frame, height=22)
        self.frame_grupo_header.pack(fill=tk.X)
        self.frame_grupo_header.pack_propagate(False)

        self.canvas_grupo = tk.Canvas(self.frame_grupo_header, height=22, bg="#2c3e50", highlightthickness=0)
        self.canvas_grupo.pack(fill=tk.BOTH, expand=True)

        # Frame interno del canvas para los labels de grupo
        self.frame_grupo_labels = tk.Frame(self.canvas_grupo, bg="#2c3e50")
        self.canvas_grupo_window = self.canvas_grupo.create_window((0, 0), window=self.frame_grupo_labels, anchor=tk.NW)

        # --- Tabla principal ---
        scroll_y = tk.Scrollbar(frame, orient=tk.VERTICAL)
        scroll_x = tk.Scrollbar(frame, orient=tk.HORIZONTAL)

        self.tabla = ttk.Treeview(
            frame,
            yscrollcommand=scroll_y.set,
            show="headings",
            height=4,
        )
        scroll_y.config(command=self.tabla.yview)

        # Scroll horizontal sincronizado: tabla + encabezados de grupo
        def _on_scroll_x(*args):
            self.tabla.xview(*args)
            self.canvas_grupo.xview(*args)

        scroll_x.config(command=_on_scroll_x)
        self.tabla.config(xscrollcommand=lambda *args: (scroll_x.set(*args), self._sincronizar_grupo_scroll()))

        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        self.tabla.pack(fill=tk.BOTH, expand=True)

        # Barra de detalle de celda
        frame_detalle = tk.Frame(frame, bg="#ecf0f1", bd=1, relief=tk.SUNKEN)
        frame_detalle.pack(fill=tk.X, pady=(4, 0))

        tk.Label(
            frame_detalle, text="📋", font=("Helvetica", 10), bg="#ecf0f1",
        ).pack(side=tk.LEFT, padx=(6, 2))

        self.label_detalle_celda = tk.Label(
            frame_detalle,
            text="Hacé click en una celda para ver su contenido completo.",
            font=("Consolas", 9), bg="#ecf0f1", fg="#555555",
            anchor=tk.W,
        )
        self.label_detalle_celda.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=4, pady=3)

        # Bind clicks
        self.tabla.bind("<ButtonRelease-1>", self._on_click_celda)
        self.tabla.bind("<Button-3>", self._on_right_click_celda)
        self.tabla.bind("<<TreeviewSelect>>", self._on_seleccionar_fila)

        # Placeholder columns
        self._configurar_columnas_tabla([
            "Nro", "Día", "Evento", "Reloj (min)", "Reloj (HH:MM)",
            "RND Llegada", "T. Entre Lleg.", "Próx. Llegada",
            "RND Tipo", "Tipo Asignado",
            "Col. Estado", "Col. T.At.", "Col. Fin At.", "Col. Cola",
            "PA Estado", "PA T.At.", "PA Fin At.", "PA Cola",
            "PB Estado", "PB T.At.", "PB Fin At.", "PB Cola",
            "Próx. Eventos",
            "Acum. Recaud.", "Acum. Bebidas", "Acum. Costo Beb.",
            "Clientes Atend.", "Máx Cola Total",
        ])

    def _on_seleccionar_fila(self, event):
        pass
    
    def _actualizar_textos_grupo(self, clientes_en_fila):
        pass

    def _sincronizar_grupo_scroll(self):
        """Sincroniza la posición del canvas de grupo con la tabla."""
        try:
            x_pos = self.tabla.xview()
            self.canvas_grupo.xview_moveto(x_pos[0])
        except Exception:
            pass

    def _on_click_celda(self, event):
        """Muestra el contenido completo de la celda clickeada en la barra de detalle."""
        # Identificar fila y columna clickeada
        item = self.tabla.identify_row(event.y)
        col_id = self.tabla.identify_column(event.x)

        if not item or not col_id:
            return

        # col_id es "#1", "#2", etc. Extraer índice
        try:
            col_idx = int(col_id.replace("#", "")) - 1
        except ValueError:
            return

        valores = self.tabla.item(item, "values")
        if not valores or col_idx >= len(valores):
            return

        # Obtener nombre completo de la columna (incluyendo grupo si es cliente)
        columnas = self.tabla["columns"]
        col_id_name = columnas[col_idx] if col_idx < len(columnas) else f"Col {col_idx}"
        nombre_display = getattr(self, '_nombre_completo_columna', {}).get(col_id_name, col_id_name)
        valor = valores[col_idx]

        self.label_detalle_celda.config(
            text=f"{nombre_display}:  {valor}",
            fg="#2c3e50",
        )

    def _on_right_click_celda(self, event):
        """Muestra menú contextual para abrir tabla de Euler si corresponde."""
        item = self.tabla.identify_row(event.y)
        col_id = self.tabla.identify_column(event.x)

        if not item or not col_id:
            return

        self.tabla.selection_set(item)

        try:
            col_idx = int(col_id.replace("#", "")) - 1
        except ValueError:
            return

        valores = self.tabla.item(item, "values")
        if not valores or col_idx >= len(valores):
            return

        columnas = self.tabla["columns"]
        col_id_name = columnas[col_idx] if col_idx < len(columnas) else f"Col {col_idx}"

        # Verificar si es una columna de T.At. (Tiempo Atención) para abrir Euler
        _t_at_tipo = {
            "Col. T.At.": "colorista",
            "PA T.At.": "peluquero_a",
            "PB T.At.": "peluquero_b",
        }
        if col_id_name in _t_at_tipo:
            tipo_servidor = _t_at_tipo[col_id_name]
            try:
                nro_evento = int(valores[0])
            except ValueError:
                return
            clientes_en_fila = self.objetos_por_fila.get(nro_evento, [])
            cliente_atendido = None
            for c in clientes_en_fila:
                if c.estado == "siendo_atendido" and c.tipo == tipo_servidor:
                    cliente_atendido = c
                    break

            menu = tk.Menu(self.ventana, tearoff=0)
            if cliente_atendido and getattr(cliente_atendido, "pasos_euler", []):
                menu.add_command(
                    label=f"Ver tabla Euler (Cliente {cliente_atendido.numero})",
                    command=lambda c=cliente_atendido: self._abrir_dialogo_euler(c)
                )
            else:
                menu.add_command(
                    label="Sin datos de Euler disponibles",
                    state=tk.DISABLED
                )
            menu.tk_popup(event.x_root, event.y_root)
            return

        match = re.match(r"^Cli (\d+) (.+)$", col_id_name)
        if not match:
            return
            
        idx_grupo = int(match.group(1)) - 1  # Índice 0-based del cliente activo en esa fila

        try:
            nro_evento = int(valores[0])
        except ValueError:
            return

        # Buscar el cliente en objetos_por_fila por su posición
        clientes_en_fila = self.objetos_por_fila.get(nro_evento, [])
        if idx_grupo < 0 or idx_grupo >= len(clientes_en_fila):
            return
            
        cliente_obj = clientes_en_fila[idx_grupo]
        numero_real_cliente = getattr(cliente_obj, "numero", "?")

        # Validar si tiene pasos de Euler
        pasos = getattr(cliente_obj, "pasos_euler", [])
        
        # Crear y mostrar menú contextual
        menu = tk.Menu(self.ventana, tearoff=0)
        
        if pasos:
            menu.add_command(
                label=f"Ver tabla Euler (Cliente {numero_real_cliente})",
                command=lambda: self._abrir_dialogo_euler(cliente_obj)
            )
        else:
            menu.add_command(
                label=f"Euler no calculado aún (en cola)",
                state=tk.DISABLED
            )
            
        menu.tk_popup(event.x_root, event.y_root)

    def _abrir_dialogo_euler(self, cliente):
        EulerDialog(self.ventana, cliente, self.h_euler_actual)

    def _construir_controles_paginacion(self):
        frame = tk.Frame(self.ventana, pady=4)
        frame.pack(fill=tk.X, padx=12, pady=(0, 8))

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

    def _configurar_columnas_tabla(self, columnas: list):
        """Configura columnas de la tabla y genera encabezados de grupo para clientes."""
        self.tabla["columns"] = columnas

        # Mapeo de ID de columna -> nombre completo para la barra de detalle
        self._nombre_completo_columna = {}

        # Anchos personalizados por tipo de columna
        anchos = {
            "Nro": 50, "Día": 40, "Evento": 190,
            "Reloj (min)": 80, "Reloj (HH:MM)": 85,
            "Próx. Eventos": 200,
            "Col. T.At.": 75, "PA T.At.": 75, "PB T.At.": 75,
        }

        import re

        # Info de grupos de clientes: [(nro_cliente, col_inicio_idx, col_fin_idx), ...]
        grupos_clientes = []
        cliente_actual_grp = None
        col_inicio_grp = None

        for idx, col in enumerate(columnas):
            # Detectar columnas de clientes: "Cli N Atributo"
            match = re.match(r"^Cli (\d+) (.+)$", col)
            if match:
                nro_cli = int(match.group(1))
                atributo = match.group(2)

                # Guardar nombre completo para la barra de detalle
                self._nombre_completo_columna[col] = f"Cliente {nro_cli} — {atributo}"

                # Heading muestra solo el atributo
                self.tabla.heading(col, text=atributo)
                self.tabla.column(col, width=80, anchor=tk.CENTER, minwidth=60, stretch=False)

                # Tracking de grupos
                if nro_cli != cliente_actual_grp:
                    if cliente_actual_grp is not None:
                        grupos_clientes.append((cliente_actual_grp, col_inicio_grp, idx - 1))
                    cliente_actual_grp = nro_cli
                    col_inicio_grp = idx
            else:
                # Cerrar grupo anterior si existía
                if cliente_actual_grp is not None:
                    grupos_clientes.append((cliente_actual_grp, col_inicio_grp, idx - 1))
                    cliente_actual_grp = None
                    col_inicio_grp = None

                self._nombre_completo_columna[col] = col
                self.tabla.heading(col, text=col)
                ancho = anchos.get(col, 95)
                self.tabla.column(col, width=ancho, anchor=tk.CENTER, minwidth=60, stretch=False)

        # Cerrar último grupo si la tabla termina con columnas de cliente
        if cliente_actual_grp is not None:
            grupos_clientes.append((cliente_actual_grp, col_inicio_grp, len(columnas) - 1))

        # Construir encabezados de grupo
        self._construir_grupo_headers(columnas, grupos_clientes, anchos)

    def _construir_grupo_headers(self, columnas: list, grupos_clientes: list, anchos: dict):
        # Limpiar labels de grupo existentes antes de reconstruir
        for widget in self.frame_grupo_labels.winfo_children():
            widget.destroy()

        if not grupos_clientes:
            return

        # Mapear qué columnas pertenecen a qué cliente
        grupo_dict = {}
        for nro_cli, col_ini, col_fin in grupos_clientes:
            for i in range(col_ini, col_fin + 1):
                grupo_dict[i] = nro_cli

        # Colores alternados para grupos de clientes
        colores_grupo = ["#1a5276", "#1e8449", "#7d3c98", "#b9770e", "#922b21", "#148f77"]

        self._labels_grupo_refs = []
        idx = 0
        while idx < len(columnas):
            if idx in grupo_dict:
                # Inicio de un grupo de cliente
                nro_cli = grupo_dict[idx]
                ancho_total = 0
                count = 0
                while idx + count < len(columnas) and grupo_dict.get(idx + count) == nro_cli:
                    ancho_total += 80  # ancho de columna de cliente
                    count += 1

                color = colores_grupo[(nro_cli - 1) % len(colores_grupo)]
                lbl_frame = tk.Frame(self.frame_grupo_labels, bg=color, width=ancho_total, height=22,
                                     relief=tk.RIDGE, bd=1)
                lbl_frame.pack(side=tk.LEFT)
                lbl_frame.pack_propagate(False)
                
                lbl = tk.Label(
                    lbl_frame,
                    text=f"Cliente {nro_cli}", # Texto estático (fallback)
                    bg=color, fg="white",
                    font=("Helvetica", 8, "bold"),
                )
                lbl.pack(expand=True)
                self._labels_grupo_refs.append(lbl)

                idx += count
            else:
                # Columna normal — spacer
                col = columnas[idx]
                match = re.match(r"^Cli (\d+) (.+)$", col)
                ancho = anchos.get(col, 95) if not match else 80
                spacer = tk.Frame(self.frame_grupo_labels, bg="#2c3e50", width=ancho, height=22)
                spacer.pack(side=tk.LEFT)
                spacer.pack_propagate(False)
                idx += 1

        # Actualizar scroll region del canvas de grupo
        self.frame_grupo_labels.update_idletasks()
        self.canvas_grupo.config(scrollregion=self.canvas_grupo.bbox("all"))

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
        porc_col_str = self.entrada_porc_colorista.get().strip()
        porc_pa_str = self.entrada_porc_peluquero_a.get().strip()
        llegada_min_str = self.entrada_llegada_min.get().strip()
        llegada_max_str = self.entrada_llegada_max.get().strip()
        t_col_str = self.entrada_t_colorista.get().strip()
        t_pel_str = self.entrada_t_peluqueros.get().strip()

        # Validar inputs básicos
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

        # Validar porcentajes
        valido, error = validar_porcentajes(porc_col_str, porc_pa_str)
        if not valido:
            messagebox.showerror("Error de validación", error)
            return

        # Validar límites de llegada
        valido, error = validar_limites_llegada(llegada_min_str, llegada_max_str)
        if not valido:
            messagebox.showerror("Error de validación", error)
            return

        # Validar T Euler
        valido, error = validar_t_euler(t_col_str, t_pel_str)
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

        prob_colorista = float(porc_col_str) / 100.0
        prob_peluquero_a = float(porc_pa_str) / 100.0
        llegada_min = float(llegada_min_str)
        llegada_max = float(llegada_max_str)
        t_colorista = int(t_col_str)
        t_peluqueros = int(t_pel_str)

        # Mostrar cursor de espera y desactivar botón durante simulación
        self.ventana.config(cursor="wait")
        self.btn_simular.config(text="⏳ Simulando...", state=tk.DISABLED, bg="#2ecc71")
        self.ventana.update_idletasks()

        try:
            self._ejecutar_simulacion(
                n_dias, x_cola, h_euler, hora_j, iter_i,
                prob_colorista, prob_peluquero_a,
                llegada_min, llegada_max,
                t_colorista, t_peluqueros,
            )
        except Exception as e:
            messagebox.showerror("Error de simulación", str(e))
        finally:
            self.ventana.config(cursor="")
            self.btn_simular.config(text="▶  Simular", state=tk.NORMAL, bg="#27ae60")

    def _ejecutar_simulacion(self, n_dias, x_cola, h_euler, hora_j, iter_i,
                              prob_colorista, prob_peluquero_a,
                              llegada_min, llegada_max,
                              t_colorista, t_peluqueros):
        """Lógica de simulación separada para manejar cursor de espera."""
        # Ejecutar simulación
        resultados = simular(
            n_dias, x_cola, h_euler,
            prob_colorista=prob_colorista,
            prob_peluquero_a=prob_peluquero_a,
            llegada_min=llegada_min,
            llegada_max=llegada_max,
            t_colorista=t_colorista,
            t_peluqueros=t_peluqueros,
        )

        # Actualizar panel de resultados
        self._actualizar_resultados(resultados, x_cola)

        # Guardar objetos temporales
        self.objetos_por_fila = resultados.get("objetos_por_fila", {})

        # Separar encabezados del resto
        filas_completas = resultados.get("filas_tabla", [])
        if filas_completas:
            encabezados_raw = filas_completas[0]
            filas_raw = filas_completas[1:]
            self.encabezados, todas_las_filas = self._agregar_columna_contador_dias_supera_x(
                encabezados_raw, filas_raw, x_cola
            )
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

            # Guardar encabezados completos (sin recortar) para recorte por página
            self.encabezados_completos = list(self.encabezados)

            self.label_filtro_info.config(
                text=f"Mostrando {len(filas_filtradas)} filas (desde min {hora_j}, "
                     f"máx {iter_i}) de {len(todas_las_filas)} totales"
            )
        else:
            self.filas_simuladas = []
            self.encabezados_completos = []
            self.label_filtro_info.config(text="")

        # Forzar reconfiguración de columnas en la próxima renderización
        self._ultimo_encabezados = []

        total = len(self.filas_simuladas)
        self.total_paginas = max(1, -(-total // self.filas_por_pagina))
        self._ir_a_pagina(1)

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

    def _agregar_columna_contador_dias_supera_x(self, encabezados: list, filas: list, x_cola: int):
        """Agrega una columna de contador por día para el umbral de cola X."""
        if "Máx Cola Total" not in encabezados:
            return encabezados, filas

        encabezados_actualizados = list(encabezados)
        max_cola_idx = encabezados.index("Máx Cola Total")
        contador_col = f"Días cola > {x_cola}"
        insert_idx = max_cola_idx + 1
        encabezados_actualizados.insert(insert_idx, contador_col)

        filas_actualizadas = []
        dia_actual = None
        dia_supero_umbral = False
        contador_dias = 0

        for fila in filas:
            # Resetear por día
            try:
                dia = int(fila[1])
            except (ValueError, TypeError):
                dia = dia_actual

            if dia != dia_actual:
                dia_actual = dia
                dia_supero_umbral = False

            try:
                valor_max = int(fila[max_cola_idx])
            except (ValueError, TypeError):
                valor_max = 0

            if valor_max > x_cola and not dia_supero_umbral:
                contador_dias += 1
                dia_supero_umbral = True

            fila_actualizada = list(fila)
            fila_actualizada.insert(insert_idx, str(contador_dias))
            filas_actualizadas.append(fila_actualizada)

        return encabezados_actualizados, filas_actualizadas

    # ------------------------------------------------------------------
    # Lógica de paginación
    # ------------------------------------------------------------------

    def _ir_a_pagina(self, pagina: int):
        if self.total_paginas == 0:
            return
        self.pagina_actual = max(1, min(pagina, self.total_paginas))

        inicio = (self.pagina_actual - 1) * self.filas_por_pagina
        fin = inicio + self.filas_por_pagina
        filas_pagina = self.filas_simuladas[inicio:fin]

        # Recortar columnas de clientes vacías para ESTA página solamente
        enc_pagina, filas_recortadas = self._recortar_columnas_vacias(
            self.encabezados_completos, filas_pagina
        )
        self.encabezados = enc_pagina

        self._renderizar_tabla(filas_recortadas)
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
        # Solo reconfigurar columnas si los encabezados cambiaron (evita rebuild costoso por página)
        if self.encabezados and self.encabezados != self._ultimo_encabezados:
            self._configurar_columnas_tabla(self.encabezados)
            self._ultimo_encabezados = list(self.encabezados)

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

    def _recortar_columnas_vacias(self, encabezados: list, filas: list):
        """Elimina grupos de columnas de clientes que están completamente vacíos
        en las filas visibles.  Reduce drásticamente la cantidad de columnas
        del Treeview y mejora el rendimiento de renderizado."""
        if not encabezados or not filas:
            return encabezados, filas

        # Encontrar dónde empiezan las columnas de clientes
        primer_cli_idx = None
        for i, col in enumerate(encabezados):
            if re.match(r"^Cli \d+ ", col):
                primer_cli_idx = i
                break

        if primer_cli_idx is None:
            return encabezados, filas  # Sin columnas de clientes

        cols_por_cliente = 4  # Estado, Hs Refrig, ¿Refrig?, Costo
        num_cols_cli = len(encabezados) - primer_cli_idx
        num_grupos = num_cols_cli // cols_por_cliente

        # Determinar qué grupos tienen al menos un dato no vacío
        grupos_con_datos = set()
        for fila in filas:
            for g in range(num_grupos):
                inicio = primer_cli_idx + g * cols_por_cliente
                if inicio < len(fila):
                    vals = fila[inicio:inicio + cols_por_cliente]
                    if any(v and str(v).strip() for v in vals):
                        grupos_con_datos.add(g)
            # Optimización: si ya encontramos todos, salir temprano
            if len(grupos_con_datos) == num_grupos:
                break

        if len(grupos_con_datos) == num_grupos:
            return encabezados, filas  # Todos tienen datos, no recortar

        # Construir lista de índices a mantener (base + grupos con datos)
        indices = list(range(primer_cli_idx))
        for g in sorted(grupos_con_datos):
            inicio = primer_cli_idx + g * cols_por_cliente
            indices.extend(range(inicio, inicio + cols_por_cliente))

        nuevos_enc = [encabezados[i] for i in indices]
        nuevas_filas = [
            [fila[i] if i < len(fila) else "" for i in indices]
            for fila in filas
        ]

        return nuevos_enc, nuevas_filas

    def ejecutar(self):
        self.ventana.mainloop()

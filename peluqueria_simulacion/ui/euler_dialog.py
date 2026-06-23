"""
Ventana emergente para mostrar la tabla paso a paso de la integración
numérica por el método de Euler para un corte específico.
"""

import tkinter as tk
from tkinter import ttk, filedialog
import csv
import os

from core.euler import T_COLORISTA, T_PELUQUEROS


_NOMBRE_TIPO = {
    "colorista": "Colorista",
    "peluquero_a": "Peluquero A",
    "peluquero_b": "Peluquero B",
}


class EulerDialog(tk.Toplevel):
    """Ventana que muestra el detalle paso a paso de la integración Euler."""

    def __init__(self, parent, cliente, h_euler: float):
        super().__init__(parent)
        self.cliente = cliente
        self.h_euler = h_euler

        tipo_nombre = _NOMBRE_TIPO.get(cliente.tipo, cliente.tipo)
        self.title(f"Integración Euler — Cliente #{cliente.numero} ({tipo_nombre})")
        self.geometry("720x480")
        self.resizable(True, True)
        self.transient(parent)

        self._construir_ui()

    def _construir_ui(self):
        c = self.cliente
        tipo_nombre = _NOMBRE_TIPO.get(c.tipo, c.tipo)

        if c.tipo == "colorista":
            T = T_COLORISTA
        else:
            T = T_PELUQUEROS

        C = c.longitud_cola_al_inicio

        # ---- Encabezado con info del cliente y la ED ----
        frame_info = tk.Frame(self, bg="#2c3e50", padx=15, pady=10)
        frame_info.pack(fill=tk.X)

        tk.Label(
            frame_info,
            text=f"Integración Euler — Cliente #{c.numero} ({tipo_nombre})",
            font=("Helvetica", 13, "bold"), bg="#2c3e50", fg="white",
        ).pack(anchor=tk.W)

        tk.Label(
            frame_info,
            text=f"ED: dD/dt = C + 0.2·T + t²    |    C = {C}    |    T = {T}    |    h = {self.h_euler}",
            font=("Consolas", 10), bg="#2c3e50", fg="#ecf0f1",
        ).pack(anchor=tk.W, pady=(4, 0))

        tk.Label(
            frame_info,
            text=f"Condición de fin: D ≥ T = {T}",
            font=("Consolas", 10), bg="#2c3e50", fg="#ecf0f1",
        ).pack(anchor=tk.W, pady=(2, 0))

        # ---- Tabla de pasos ----
        frame_tabla = tk.Frame(self, padx=10, pady=8)
        frame_tabla.pack(fill=tk.BOTH, expand=True)

        columnas = ["Paso", "t", "D (antes)", "dD/dt", "D (después)"]
        scroll_y = tk.Scrollbar(frame_tabla, orient=tk.VERTICAL)

        self.tabla = ttk.Treeview(
            frame_tabla,
            columns=columnas,
            show="headings",
            yscrollcommand=scroll_y.set,
            height=12,
        )
        scroll_y.config(command=self.tabla.yview)
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        self.tabla.pack(fill=tk.BOTH, expand=True)

        anchos = [60, 80, 100, 100, 100]
        for col, ancho in zip(columnas, anchos):
            self.tabla.heading(col, text=col)
            self.tabla.column(col, width=ancho, anchor=tk.CENTER, minwidth=60)

        # Estilos
        estilo = ttk.Style()
        estilo.configure("euler.Treeview", rowheight=24)
        self.tabla.tag_configure("par", background="#e8ecf1")
        self.tabla.tag_configure("impar", background="white")
        self.tabla.tag_configure("final", background="#d5f5e3", font=("Helvetica", 9, "bold"))

        # Llenar tabla
        pasos = c.pasos_euler
        for i, (paso, t, D_antes, dDdt, D_despues) in enumerate(pasos):
            es_ultimo = (i == len(pasos) - 1)
            if es_ultimo:
                tag = "final"
            else:
                tag = "par" if i % 2 == 0 else "impar"

            self.tabla.insert("", tk.END, values=(
                str(paso),
                f"{t:.4f}",
                f"{D_antes:.4f}",
                f"{dDdt:.4f}",
                f"{D_despues:.4f}",
            ), tags=(tag,))

        # ---- Resultado y botones ----
        frame_bottom = tk.Frame(self, padx=10, pady=8)
        frame_bottom.pack(fill=tk.X)

        tk.Label(
            frame_bottom,
            text=f"Resultado: Demora del corte = {c.demora_calculada:.4f} minutos",
            font=("Helvetica", 11, "bold"), fg="#27ae60",
        ).pack(side=tk.LEFT)

        tk.Button(
            frame_bottom,
            text="Exportar CSV",
            command=self._exportar_csv,
            bg="#3498db", fg="white",
            font=("Helvetica", 9, "bold"),
            relief=tk.FLAT, cursor="hand2",
            padx=10, pady=4,
        ).pack(side=tk.RIGHT, padx=5)

        tk.Button(
            frame_bottom,
            text="Cerrar",
            command=self.destroy,
            bg="#95a5a6", fg="white",
            font=("Helvetica", 9, "bold"),
            relief=tk.FLAT, cursor="hand2",
            padx=10, pady=4,
        ).pack(side=tk.RIGHT, padx=5)

    def _exportar_csv(self):
        """Exporta la tabla de pasos Euler a un archivo CSV."""
        filepath = filedialog.asksaveasfilename(
            parent=self,
            title="Exportar tabla Euler",
            defaultextension=".csv",
            filetypes=[("CSV", "*.csv"), ("Todos", "*.*")],
            initialfile=f"euler_cliente_{self.cliente.numero}.csv",
        )
        if not filepath:
            return

        c = self.cliente
        T = T_COLORISTA if c.tipo == "colorista" else T_PELUQUEROS

        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Integración Euler - Cliente", c.numero])
            writer.writerow(["Tipo servidor", _NOMBRE_TIPO.get(c.tipo, c.tipo)])
            writer.writerow(["C (cola al inicio)", c.longitud_cola_al_inicio])
            writer.writerow(["T (constante servidor)", T])
            writer.writerow(["h (paso)", self.h_euler])
            writer.writerow(["ED", "dD/dt = C + 0.2*T + t^2"])
            writer.writerow([])
            writer.writerow(["Paso", "t", "D (antes)", "dD/dt", "D (después)"])
            for paso, t, D_antes, dDdt, D_despues in c.pasos_euler:
                writer.writerow([paso, f"{t:.4f}", f"{D_antes:.4f}", f"{dDdt:.4f}", f"{D_despues:.4f}"])
            writer.writerow([])
            writer.writerow(["Resultado", f"{c.demora_calculada:.4f}", "minutos"])

        tk.messagebox.showinfo("Exportado", f"Archivo guardado en:\n{filepath}", parent=self)

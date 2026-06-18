# Simulación Peluquería Look

Simulación de eventos discretos para una peluquería con 3 servidores:
- **Colorista** (1 servidor)
- **Peluquero A** (1 servidor)
- **Peluquero B** (1 servidor)

Los clientes llegan durante 8 horas de recepción y la atención continúa hasta que no queden clientes en cola.

---

## Cómo ejecutar

```bash
cd peluqueria_simulacion
python main.py
```

Requiere Python 3.10 o superior. No se necesitan dependencias externas (usa `tkinter` de la biblioteca estándar).

---

## Estructura del proyecto

```
peluqueria_simulacion/
│
├── main.py                  # Punto de entrada
│
├── ui/
│   ├── __init__.py
│   └── app.py               # Ventana principal (Tkinter)
│
├── core/
│   ├── __init__.py
│   ├── simulacion.py        # Función simular() — orquesta la simulación
│   ├── entidades.py         # Dataclasses: Cliente, Servidor, Evento, ResultadoDia
│   ├── distribuciones.py    # Funciones de generación de tiempos aleatorios
│   └── resultados.py        # Cálculo de indicadores finales
│
├── utils/
│   ├── __init__.py
│   └── validaciones.py      # Validación de inputs de la UI
│
└── README.md
```

---

## Distribuciones planificadas

| Variable              | Distribución   |
|-----------------------|----------------|
| Tiempo entre llegadas | U(2, 12) min   |
| Tiempo colorista      | U(30, 50) min  |
| Tiempo Peluquero A    | U(21, 25) min  |
| Tiempo Peluquero B    | U(22, 38) min  |
| Tipo de cliente       | 15% colorista · 40% Pel. A · 45% Pel. B |

---

## Pendiente de implementar

- [ ] **`core/simulacion.py`** — lógica completa del bucle de eventos:
  - Priority queue de eventos
  - Manejo de llegadas y generación de siguiente llegada
  - Asignación de servidores y colas de espera
  - Registro de snapshots del estado para la tabla
- [ ] **`core/simulacion.py`** — cálculo de recaudación por cliente según tipo
- [ ] **`core/simulacion.py`** — lógica de entrega de bebidas (condición a definir)
- [ ] **`core/resultados.py`** — `calcular_probabilidad_mas_de_x()` recorriendo snapshots
- [ ] **`ui/app.py`** — indicador de progreso durante la simulación (puede ser largo)
- [ ] Definir precios de servicios y costo de bebidas

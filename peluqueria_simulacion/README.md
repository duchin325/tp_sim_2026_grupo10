# Simulación Peluquería Look

Simulación de eventos discretos de una peluquería que cuenta con 3 servidores:

| Servidor    | Cantidad | Precio por servicio |
|-------------|----------|---------------------|
| Colorista   | 1        | $35.000             |
| Peluquero A | 1        | $18.000             |
| Peluquero B | 1        | $18.000             |

---

## Cómo ejecutar

```bash
cd peluqueria_simulacion
python main.py
```

Requiere Python 3.10 o superior. No se necesitan dependencias externas (usa `tkinter` de la biblioteca estándar).

---

## Descripción del problema

Una peluquería atiende clientes durante **8 horas** (jornada de recepción). Al cerrar la recepción se deja de admitir nuevos clientes, pero la atención continúa hasta que no quede nadie en cola ni siendo atendido.

Cada cliente que llega requiere uno de los tres servidores según las siguientes probabilidades:

| Tipo de cliente | Probabilidad |
|-----------------|:------------:|
| Colorista       | 15 %         |
| Peluquero A     | 45 %         |
| Peluquero B     | 40 %         |

### Llegadas

Los clientes llegan con tiempos entre llegadas distribuidos **uniformemente U(2, 12) minutos**.

### Tiempo de atención — Ecuación diferencial

El tiempo de demora de un corte **no** sigue una distribución uniforme. Está dado por la ecuación diferencial:

```
dD/dt = C + 0.2·T + t²
```

| Variable | Significado |
|----------|-------------|
| `D`      | Demora acumulada del corte (minutos) |
| `t`      | Tiempo transcurrido desde el inicio del corte (minutos) |
| `C`      | Longitud de la cola del servidor al momento de **iniciar** el corte |
| `T`      | Constante del servidor: **180** para el colorista, **130** para los peluqueros |

### Método numérico: Runge-Kutta de cuarto orden

La ecuación diferencial se resuelve numéricamente con **RK4** y paso de integración **h = 1 minuto**.

Implementado en `core/runge_kutta.py`:
- `derivada_demora(t, D, C, T)` — define la ED
- `runge_kutta_4(f, t0, y0, h, pasos, C, T)` — integrador genérico RK4
- `calcular_demora_corte(tipo_servidor, longitud_cola_inicial, pasos)` — función principal

> **TODO**: el criterio de finalización de la integración (número de pasos) está pendiente de confirmar con el enunciado.

### Reglas económicas

| Concepto                                    | Valor    |
|---------------------------------------------|----------|
| Servicio colorista                          | $35.000  |
| Servicio peluquero (A o B)                  | $18.000  |
| Bebida gratis (si espera > 30 min)          | —        |
| Costo de la bebida (descuenta de ganancia)  | $6.500   |

---

## Objetivos de la simulación

1. **Recaudación diaria promedio** sobre N días simulados.
2. **Probabilidad** de que en algún momento del día haya más de X personas esperando (en cualquier cola).
3. Totales: clientes atendidos, bebidas entregadas, costo total de bebidas.

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
│   ├── simulacion.py        # Orquesta la simulación; constantes del dominio
│   ├── entidades.py         # Dataclasses: Cliente, Servidor, Evento, ResultadoDia
│   ├── distribuciones.py    # Llegadas U(2,12) y selección de tipo de cliente
│   ├── runge_kutta.py       # Ecuación diferencial + integrador RK4
│   └── resultados.py        # Cálculo de indicadores finales
│
├── utils/
│   ├── __init__.py
│   └── validaciones.py      # Validación de inputs de la UI
│
└── README.md
```

---

## Estado actual del proyecto

- [x] Estructura de módulos creada
- [x] Interfaz gráfica inicial (Tkinter) con inputs y tabla placeholder
- [x] Distribuciones de llegada y selección de tipo de cliente
- [x] Módulo `runge_kutta.py` preparado (ED + RK4 + `calcular_demora_corte`)
- [x] Constantes del dominio centralizadas en `simulacion.py`
- [ ] Lógica completa de eventos discretos (bucle principal, priority queue)
- [ ] Colas de espera por servidor
- [ ] Recaudación y bebidas por cliente
- [ ] Cálculo de probabilidad P(cola > X)
- [ ] Tabla de eventos con snapshots del estado
- [ ] Simulación de múltiples días

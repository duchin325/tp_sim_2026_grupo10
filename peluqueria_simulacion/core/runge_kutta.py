"""
Módulo de integración numérica por Runge-Kutta de cuarto orden (RK4).

Ecuación diferencial del tiempo de demora de un corte:

    dD/dt = C + 0.2·T + t²

Donde:
    C  — longitud de la cola al momento de iniciar el corte (clientes esperando)
    T  — constante del servidor:
             T = 180 para el colorista
             T = 130 para los peluqueros (A y B)
    t  — tiempo transcurrido desde el inicio del corte (en minutos)
    D  — demora acumulada (en minutos)

La integración se realiza con paso h = 1 minuto.
"""

# Constantes de cada servidor
T_COLORISTA = 180
T_PELUQUEROS = 130


def derivada_demora(t: float, D: float, C: int, T: int) -> float:
    """
    Derivada dD/dt de la ecuación diferencial del tiempo de demora.

    Parámetros:
        t  -- tiempo actual dentro del corte (minutos)
        D  -- valor acumulado de D en el instante t (no se usa en la ED, pero
               se incluye para mantener la firma estándar f(t, y) de RK4)
        C  -- longitud de la cola al iniciar el corte
        T  -- constante del servidor (180 colorista / 130 peluqueros)
    """
    return C + 0.2 * T + t ** 2


def runge_kutta_4(f, t0: float, y0: float, h: float, pasos: int, C: int, T: int) -> float:
    """
    Aplica el método de Runge-Kutta de cuarto orden para integrar f(t, y)
    desde t0 durante `pasos` pasos de tamaño h.

    Parámetros:
        f      -- función derivada con firma f(t, y, C, T)
        t0     -- tiempo inicial
        y0     -- valor inicial de y (D₀ = 0 al comenzar el corte)
        h      -- paso de integración (1 minuto)
        pasos  -- número de pasos a integrar
        C      -- longitud de cola al iniciar el corte
        T      -- constante del servidor

    Retorna:
        Valor de y (demora acumulada D) al final de la integración.
    """
    t = t0
    y = y0
    for _ in range(pasos):
        k1 = f(t,           y,           C, T)
        k2 = f(t + h / 2,  y + h * k1 / 2, C, T)
        k3 = f(t + h / 2,  y + h * k2 / 2, C, T)
        k4 = f(t + h,      y + h * k3,  C, T)
        y = y + (h / 6) * (k1 + 2 * k2 + 2 * k3 + k4)
        t = t + h
    return y


def calcular_demora_corte(tipo_servidor: str, longitud_cola_inicial: int, pasos: int = None) -> float:
    """
    Calcula la demora total de un corte integrando la ecuación diferencial
    dD/dt = C + 0.2·T + t² mediante RK4 con h = 1 minuto.

    Parámetros:
        tipo_servidor          -- "colorista", "peluquero_a" o "peluquero_b"
        longitud_cola_inicial  -- cantidad de clientes en cola al iniciar el corte (C)
        pasos                  -- número de pasos de integración
                                  TODO: definir el criterio de finalización exacto.
                                  Por ahora se requiere que el llamador lo provea.
                                  Opciones posibles a confirmar con el enunciado:
                                    a) pasos fijo según tipo de servidor
                                    b) integrar hasta que dD/dt < umbral
                                    c) integrar hasta que D converja

    Retorna:
        Demora total D calculada por RK4 (en minutos).

    Raises:
        ValueError  si tipo_servidor no es reconocido o si pasos es None
                    (mientras no se defina el criterio de parada).
    """
    if tipo_servidor == "colorista":
        T = T_COLORISTA
    elif tipo_servidor in ("peluquero_a", "peluquero_b"):
        T = T_PELUQUEROS
    else:
        raise ValueError(f"Tipo de servidor desconocido: '{tipo_servidor}'")

    # TODO: Definir el criterio de finalización de la integración.
    #       Hasta que se aclare, `pasos` debe ser provisto por el llamador.
    if pasos is None:
        raise ValueError(
            "El parámetro 'pasos' es requerido hasta que se defina el criterio "
            "de finalización de la integración (ver TODO en este módulo)."
        )

    C = longitud_cola_inicial
    h = 1.0   # paso de integración: 1 minuto
    t0 = 0.0
    D0 = 0.0  # demora inicial: 0 al comenzar el corte

    return runge_kutta_4(derivada_demora, t0, D0, h, pasos, C, T)

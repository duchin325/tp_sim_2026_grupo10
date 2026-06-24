"""
Módulo de integración numérica por el método de Euler.

Ecuación diferencial del tiempo de demora de un corte:

    dD/dt = C + 0.2·T + t²

Donde:
    C  — longitud de la cola al momento de iniciar el corte (clientes esperando)
    T  — constante del servidor:
             T = 180 para el colorista
             T = 130 para los peluqueros (A y B)
    t  — tiempo transcurrido desde el inicio del corte (en minutos)
    D  — demora acumulada (en minutos)

La integración se realiza con paso h parametrizable (default 1 minuto).
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
               se incluye para mantener la firma estándar f(t, y))
        C  -- longitud de la cola al iniciar el corte
        T  -- constante del servidor (180 colorista / 130 peluqueros)
    """
    return C + 0.2 * T + t ** 2


def euler(f, t0: float, y0: float, h: float, C: int, T: int) -> float:
    """
    Aplica el método de Euler para integrar f(t, y) desde t0
    hasta que el valor acumulado (y) sea mayor o igual a T.

    Fórmula iterativa:
        y_{n+1} = y_n + h · f(t_n, y_n)

    Parámetros:
        f      -- función derivada con firma f(t, y, C, T)
        t0     -- tiempo inicial
        y0     -- valor inicial de y (D₀ = 0 al comenzar el corte)
        h      -- paso de integración (parametrizable)
        C      -- longitud de cola al iniciar el corte
        T      -- constante del servidor

    Retorna:
        El tiempo `t` necesario para que la demora acumulada alcance o supere T.
    """
    t = t0
    y = y0
    while y < T:
        y = y + h* f(t, y, C, T)
        t = t + h
    return t


def euler_con_detalle(f, t0: float, y0: float, h: float, C: int, T: int):
    """
    Aplica el método de Euler igual que euler(), pero además retorna la tabla
    paso a paso de la integración.

    Retorna:
        (t_final, lista_pasos)
        donde lista_pasos es [(paso, t, D_antes, dD_dt, D_despues), ...]
    """
    t = t0
    y = y0
    pasos = []
    paso_num = 0
    while y < T:
        dDdt = f(t, y, C, T)
        y_nuevo = y + h *dDdt
        pasos.append((paso_num, t, y, dDdt, y_nuevo))
        y = y_nuevo
        t = t + h
        paso_num += 1
    return t, pasos


def calcular_demora_corte(tipo_servidor: str, longitud_cola_inicial: int, h: float = 1.0,
                          con_detalle: bool = False,
                          t_colorista: int = T_COLORISTA,
                          t_peluqueros: int = T_PELUQUEROS):
    """
    Calcula el tiempo de atención de un corte integrando la ecuación diferencial
    dD/dt = C + 0.2·T + t² mediante el método de Euler con paso h parametrizable.

    La integración se detiene cuando D >= T, y se retorna el tiempo transcurrido (t).

    Parámetros:
        tipo_servidor          -- "colorista", "peluquero_a" o "peluquero_b"
        longitud_cola_inicial  -- cantidad de clientes en cola al iniciar el corte (C)
        h                      -- número máximo de iteraciones (default 1.0)
                                  Se calcula el paso real como: paso = T / (h * dDdt_inicial)
        con_detalle            -- si True, retorna (demora, pasos); si False, solo demora
        t_colorista            -- constante T para el colorista (default 180)
        t_peluqueros           -- constante T para los peluqueros (default 130)

    Retorna:
        Si con_detalle=False: float con el tiempo total de atención.
        Si con_detalle=True:  (float, list) con el tiempo y la tabla de pasos Euler.

    Raises:
        ValueError  si tipo_servidor no es reconocido.
    """
    if tipo_servidor == "colorista":
        T = t_colorista
    elif tipo_servidor in ("peluquero_a", "peluquero_b"):
        T = t_peluqueros
    else:
        raise ValueError(f"Tipo de servidor desconocido: '{tipo_servidor}'")

    C = longitud_cola_inicial
    t0 = 0.0
    D0 = 0.0  # demora inicial: 0 al comenzar el corte

    # Calcular dD/dt inicial (en t=0, D=0)
    dDdt_inicial = derivada_demora(0, 0, C, T)
    
    # Calcular paso adaptativo basado en h (número de iteraciones máximo)
    # paso = T / (h * dDdt_inicial) asegura que no requiera más de h iteraciones
    if dDdt_inicial > 0:
        paso = T / (max(h, 1) * dDdt_inicial)
    else:
        paso = 1.0  # fallback si dDdt_inicial == 0

    if con_detalle:
        t_final, pasos = euler_con_detalle(derivada_demora, t0, D0, h, C, T)
        return t_final, pasos
    else:
        return euler(derivada_demora, t0, D0, h, C, T)


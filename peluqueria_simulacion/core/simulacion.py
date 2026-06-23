import heapq
import random
from collections import deque
from typing import List

from core.entidades import Cliente, Servidor, Evento, ResultadoDia
from core.distribuciones import PROB_COLORISTA, PROB_PELUQUERO_A, LLEGADA_MIN, LLEGADA_MAX
from core.euler import calcular_demora_corte
from core.resultados import generar_resumen

# Constantes del dominio
DURACION_RECEPCION_MIN = 480   # 8 horas en minutos
TIEMPO_ESPERA_BEBIDA = 30      # minutos; si el cliente espera más, recibe bebida gratis
PRECIO_COLORISTA = 35_000
PRECIO_PELUQUERO = 18_000
COSTO_BEBIDA = 6_500
MAX_ITERACIONES = 100000

# Nombre legible para cada tipo de servidor (usado en la tabla de eventos)
_NOMBRE_TIPO = {
    "colorista": "Colorista",
    "peluquero_a": "Pel.A",
    "peluquero_b": "Pel.B",
}

# Encabezados de la tabla de eventos
_COLUMNAS_TABLA = [
    "Iteración", "Día", "Evento", "Reloj", "Nro. Cliente", "RND Llegada", "T. Entre", "Próx. Llegada", "RND Tipo", "Tipo Asignado",
    "Col. Estado", "Col. T.At", "Col. Fin", "Cola Col.",
    "Pel.A Estado", "Pel.A T.At", "Pel.A Fin", "Cola Pel.A",
    "Pel.B Estado", "Pel.B T.At", "Pel.B Fin", "Cola Pel.B", "Cola Total",
    "Cola Máxima", "Hora Refrigerio",
    "Acum. Recaud.", "Acum. Refrig."
]


def simular(dias: int, x: int, h: float = 1.0) -> dict:
    resultados: List[ResultadoDia] = []
    todas_las_filas: list = []
    iteracion_global = 0  # Contador global de iteraciones a través de todos los días

    for numero_dia in range(1, dias + 1):
        resultado, iteracion_global = _simular_dia(numero_dia, iteracion_global, h)
        resultados.append(resultado)
        todas_las_filas.extend(resultado.filas_tabla)

    resumen = generar_resumen(resultados, x)

    max_clientes = max(r.max_clientes for r in resultados)

    columnas_clientes = []

    for i in range(1, max_clientes + 1):
        columnas_clientes.extend([
            f"Cliente {i} Estado",
            f"Cliente {i} Hora Ref.",
            f"Cliente {i} Refrigerio",
            f"Cliente {i} Costo"
        ])

    filas_tabla = [
        _COLUMNAS_TABLA + columnas_clientes
    ] + todas_las_filas

    return {
        "promedio_recaudacion": resumen["promedio_recaudacion"],
        "probabilidad_mas_de_x": resumen["probabilidad_mas_de_x"],
        "clientes_atendidos": resumen["clientes_atendidos"],
        "bebidas_entregadas": resumen["bebidas_entregadas"],
        "costo_total_bebidas": resumen["costo_total_bebidas"],
        "filas_tabla": filas_tabla,
    }


def _seleccionar_tipo_con_rnd(rnd: float) -> str:
    """Selecciona el tipo de cliente basándose en un RND dado."""
    if rnd < PROB_COLORISTA:
        return "colorista"
    elif rnd < PROB_COLORISTA + PROB_PELUQUERO_A:
        return "peluquero_a"
    else:
        return "peluquero_b"

def _estado_cliente(cliente):

    mapa = {
        "colorista": "C",
        "peluquero_a": "PA",
        "peluquero_b": "PB"
    }

    sufijo = mapa[cliente.tipo]

    if cliente.en_cola:
        return f"EA({sufijo})"

    if cliente.tiempo_fin_atencion > 0:
        return "FA"

    return f"SA({sufijo})"

def _generar_snapshot(iteracion, dia, tipo_evento, reloj, nro_cliente, rnd_llegada, t_entre, prox_llegada,
                      rnd_tipo, tipo_asignado, servidores, colas, t_atencion_servidores, fin_atencion_servidores, cola_total, cola_maxima, hora_refrigerio,
                      acum_recaud, acum_refrig, clientes_dia ):
    """Genera una fila de la tabla con el estado actual de la simulación."""
    fila = [
        str(iteracion),
        str(dia),
        tipo_evento,
        f"{reloj:.2f}",
        str(nro_cliente) if nro_cliente else "-",
        f"{rnd_llegada:.4f}" if rnd_llegada is not None else "-",
        f"{t_entre:.2f}" if t_entre is not None else "-",
        f"{prox_llegada:.2f}" if prox_llegada is not None else "-",
        f"{rnd_tipo:.4f}" if rnd_tipo is not None else "-",
        _NOMBRE_TIPO.get(tipo_asignado, "-") if tipo_asignado else "-",
    ]

    for tipo in ["colorista", "peluquero_a", "peluquero_b"]:
        s = servidores[tipo]

        estado = "Ocupado" if s.ocupado else "Libre"
        t_at = f"{t_atencion_servidores[tipo]:.2f}" if s.ocupado else "-"
        fin = f"{fin_atencion_servidores[tipo]:.2f}" if s.ocupado else "-"
        cola_len = str(len(colas[tipo]))

        fila.extend([estado, t_at, fin, cola_len])

    fila.extend([
        str(cola_total),
        str(cola_maxima),
        f"{hora_refrigerio:.2f}",
        f"${acum_recaud:,.2f}",
        f"${acum_refrig:,.2f}"
    ])

    for cliente in clientes_dia:

        fila.extend([
            _estado_cliente(cliente),

            f"{cliente.hora_refrigerio:.2f}"
            if cliente.hora_refrigerio > 0
            else "",

            "SI" if cliente.recibio_bebida else "NO",

            str(f"${COSTO_BEBIDA:,.2f}")
            if cliente.recibio_bebida
            else "0"
        ])

    return fila


def _simular_dia(numero_dia: int, iteracion_global: int, h: float = 1.0) -> tuple[ResultadoDia, int]:
    resultado = ResultadoDia(numero_dia=numero_dia)
    clientes_dia = []

    servidores = {
        "colorista": Servidor("Colorista", "colorista"),
        "peluquero_a": Servidor("Peluquero A", "peluquero_a"),
        "peluquero_b": Servidor("Peluquero B", "peluquero_b"),
    }

    colas = {
        "colorista": deque(),
        "peluquero_a": deque(),
        "peluquero_b": deque(),
    }

    fin_atencion = {
        "colorista": 0.0,
        "peluquero_a": 0.0,
        "peluquero_b": 0.0,
    }

    tiempo_atencion = {
        "colorista": 0.0,
        "peluquero_a": 0.0,
        "peluquero_b": 0.0,
    }

    reloj = 0.0
    iteracion = iteracion_global
    recaudacion = 0.0
    bebidas = 0
    costo_bebidas = 0.0
    numero_cliente = 0
    clientes_atendidos = 0
    max_total_en_espera = 0
    hora_refrigerio = 0.0
    total_en_espera = 0

    eventos: list = []

    # ---- Generar primera llegada ----
    rnd_llegada = random.random()
    tiempo_entre = LLEGADA_MIN + (LLEGADA_MAX - LLEGADA_MIN) * rnd_llegada
    prox_llegada = tiempo_entre

    iteracion += 1

    resultado.filas_tabla.append(
        _generar_snapshot(
            iteracion, numero_dia, "Inicial", 0.0, None, rnd_llegada, tiempo_entre, prox_llegada,
            None, None, servidores, colas, tiempo_atencion, fin_atencion,  total_en_espera, max_total_en_espera, hora_refrigerio ,recaudacion, costo_bebidas, clientes_dia
        )
    )

    heapq.heappush(eventos, Evento(tiempo=prox_llegada, tipo="llegada"))

    while eventos and iteracion < MAX_ITERACIONES:
        evento = heapq.heappop(eventos)
        reloj = evento.tiempo
        iteracion += 1

        if evento.tipo == "llegada":
            if reloj >= DURACION_RECEPCION_MIN:
                continue

            numero_cliente += 1
            rnd_tipo = random.random()
            tipo_cliente = _seleccionar_tipo_con_rnd(rnd_tipo)

            cliente = Cliente(
                numero=numero_cliente,
                tipo=tipo_cliente,
                tiempo_llegada=reloj,
            )

            clientes_dia.append(cliente)

            servidor = servidores[tipo_cliente]
            cola = colas[tipo_cliente]

            if not servidor.ocupado:
                servidor.ocupado = True
                cliente.hora_refrigerio = 0.0
                cliente.tiempo_inicio_atencion = reloj
                cliente.longitud_cola_al_inicio = len(cola)
                demora = calcular_demora_corte(tipo_cliente, len(cola), h)
                cliente.demora_calculada = demora
                fin = reloj + demora
                tiempo_atencion[tipo_cliente] = demora
                fin_atencion[tipo_cliente] = fin
                heapq.heappush(eventos, Evento(
                    tiempo=fin,
                    tipo=f"fin_atencion_{tipo_cliente}",
                    cliente=cliente,
                    servidor=servidor,
                ))
            else:
                cola.append(cliente)
                cliente.en_cola = True

                cliente.hora_refrigerio = reloj + TIEMPO_ESPERA_BEBIDA

                heapq.heappush(
                    eventos,
                    Evento(
                        tiempo=cliente.hora_refrigerio,
                        tipo="refrigerio_cliente",
                        cliente=cliente
                    )
                )

            total_en_espera = total_en_espera = (
                len(colas["colorista"])
                + len(colas["peluquero_a"])
                + len(colas["peluquero_b"])
            )
            max_total_en_espera = max(max_total_en_espera, total_en_espera)

            rnd_llegada_display = random.random()
            t_entre = LLEGADA_MIN + (LLEGADA_MAX - LLEGADA_MIN) * rnd_llegada_display
            prox_llegada = reloj + t_entre

            if prox_llegada < DURACION_RECEPCION_MIN:
                heapq.heappush(eventos, Evento(tiempo=prox_llegada, tipo="llegada"))

            resultado.filas_tabla.append(
                _generar_snapshot(
                    iteracion, numero_dia, "Llegada Cliente", reloj, numero_cliente, rnd_llegada_display, t_entre, prox_llegada,
                    rnd_tipo, tipo_cliente, servidores, colas, tiempo_atencion, fin_atencion,  total_en_espera, max_total_en_espera, cliente.hora_refrigerio, recaudacion, costo_bebidas, clientes_dia
                )
            )

        elif evento.tipo == "refrigerio_cliente":

            cliente = evento.cliente

            if not cliente.en_cola: 
                continue  # El cliente ya fue atendido, no necesita refrigerio

            if (
                cliente.en_cola
                and not cliente.recibio_bebida
            ):

                cliente.recibio_bebida = True
                cliente.hora_refrigerio = 0.0

                bebidas += 1
                costo_bebidas += COSTO_BEBIDA

                total_en_espera = sum(len(c) for c in colas.values())
                max_total_en_espera = max(
                max_total_en_espera,
                total_en_espera
                )

            resultado.filas_tabla.append(
                _generar_snapshot(
                    iteracion, 
                    numero_dia,
                    f"Refrigerio Cliente {cliente.numero}",
                    reloj,
                    cliente.numero,
                    None,
                    None,
                    None,
                    None,
                    None,
                    servidores,
                    colas,
                    tiempo_atencion,
                    fin_atencion,
                    total_en_espera,
                    max_total_en_espera,
                    cliente.hora_refrigerio,
                    recaudacion,
                    costo_bebidas,
                    clientes_dia
                )
            )

        elif evento.tipo.startswith("fin_atencion_"):
            tipo_servidor = evento.tipo.replace("fin_atencion_", "")
            cliente = evento.cliente
            servidor = servidores[tipo_servidor]
            cola = colas[tipo_servidor]

            cliente.tiempo_fin_atencion = reloj
            cliente.tiempo_espera = cliente.tiempo_inicio_atencion - cliente.tiempo_llegada

            if tipo_servidor == "colorista":
                recaudacion += PRECIO_COLORISTA
            else:
                recaudacion += PRECIO_PELUQUERO

            servidor.clientes_atendidos += 1
            clientes_atendidos += 1

            if cola:
                next_cliente = cola.popleft()
                next_cliente.en_cola = False
                next_cliente.hora_refrigerio = 0.0
                next_cliente.tiempo_inicio_atencion = reloj
                next_cliente.longitud_cola_al_inicio = len(cola)
                demora = calcular_demora_corte(tipo_servidor, len(cola), h)
                next_cliente.demora_calculada = demora
                fin = reloj + demora
                tiempo_atencion[tipo_servidor] = demora
                fin_atencion[tipo_servidor] = fin
                heapq.heappush(eventos, Evento(
                    tiempo=fin,
                    tipo=f"fin_atencion_{tipo_servidor}",
                    cliente=next_cliente,
                    servidor=servidor,
                ))
            else:
                servidor.ocupado = False
                tiempo_atencion[tipo_servidor] = 0.0
                fin_atencion[tipo_servidor] = 0.0

            total_en_espera = sum(len(c) for c in colas.values())
            max_total_en_espera = max(max_total_en_espera, total_en_espera)

            nombre = _NOMBRE_TIPO.get(tipo_servidor, tipo_servidor)
            resultado.filas_tabla.append(
                _generar_snapshot(
                    iteracion, numero_dia, f"Fin At. {nombre}", reloj, cliente.numero, None, None, None,
                    None, None, servidores, colas, tiempo_atencion, fin_atencion, total_en_espera, max_total_en_espera, cliente.hora_refrigerio,recaudacion, costo_bebidas, clientes_dia
                )
            )

    resultado.recaudacion = recaudacion
    resultado.clientes_atendidos = clientes_atendidos
    resultado.bebidas_entregadas = bebidas
    resultado.costo_bebidas = costo_bebidas
    resultado.max_cola_espera = max_total_en_espera
    resultado.max_clientes = numero_cliente

    return resultado, iteracion

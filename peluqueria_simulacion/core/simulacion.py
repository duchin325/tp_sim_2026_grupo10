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

# Nombre legible para cada tipo de servidor (usado en la tabla de eventos)
_NOMBRE_TIPO = {
    "colorista": "Colorista",
    "peluquero_a": "Pel.A",
    "peluquero_b": "Pel.B",
}

# Encabezados de la tabla de eventos
_COLUMNAS_TABLA = [
    "Día", "Evento", "Reloj", "Nro. Cliente", "RND Llegada", "T. Entre", "Próx. Llegada", "RND Tipo", "Tipo Asignado",
    "Col. Estado", "Col. T.At", "Col. Fin", "Cola Col.",
    "Pel.A Estado", "Pel.A T.At", "Pel.A Fin", "Cola Pel.A",
    "Pel.B Estado", "Pel.B T.At", "Pel.B Fin", "Cola Pel.B",
    "Acum. Recaud.", "Acum. Refrig."
]


def simular(dias: int, x: int) -> dict:
    resultados: List[ResultadoDia] = []
    todas_las_filas: list = []

    for numero_dia in range(1, dias + 1):
        resultado = _simular_dia(numero_dia)
        resultados.append(resultado)
        todas_las_filas.extend(resultado.filas_tabla)

    resumen = generar_resumen(resultados, x)

    filas_tabla = [_COLUMNAS_TABLA] + todas_las_filas

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


def _generar_snapshot(dia, tipo_evento, reloj, nro_cliente, rnd_llegada, t_entre, prox_llegada,
                      rnd_tipo, tipo_asignado, servidores, colas, t_atencion_servidores, fin_atencion_servidores,
                      acum_recaud, acum_refrig):
    """Genera una fila de la tabla con el estado actual de la simulación."""
    fila = [
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

    fila.extend([f"${acum_recaud:,.2f}", f"${acum_refrig:,.2f}"])
    return fila


def _simular_dia(numero_dia: int) -> ResultadoDia:
    resultado = ResultadoDia(numero_dia=numero_dia)

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
    recaudacion = 0.0
    bebidas = 0
    costo_bebidas = 0.0
    numero_cliente = 0
    clientes_atendidos = 0
    max_total_en_espera = 0

    eventos: list = []

    # ---- Generar primera llegada ----
    rnd_llegada = random.random()
    tiempo_entre = LLEGADA_MIN + (LLEGADA_MAX - LLEGADA_MIN) * rnd_llegada
    prox_llegada = tiempo_entre

    resultado.filas_tabla.append(
        _generar_snapshot(
            numero_dia, "Inicial", 0.0, None, rnd_llegada, tiempo_entre, prox_llegada,
            None, None, servidores, colas, tiempo_atencion, fin_atencion, recaudacion, costo_bebidas
        )
    )

    heapq.heappush(eventos, Evento(tiempo=prox_llegada, tipo="llegada"))

    while eventos:
        evento = heapq.heappop(eventos)
        reloj = evento.tiempo

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

            servidor = servidores[tipo_cliente]
            cola = colas[tipo_cliente]

            if not servidor.ocupado:
                servidor.ocupado = True
                cliente.tiempo_inicio_atencion = reloj
                cliente.longitud_cola_al_inicio = len(cola)
                demora = calcular_demora_corte(tipo_cliente, len(cola))
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

            total_en_espera = sum(len(c) for c in colas.values())
            max_total_en_espera = max(max_total_en_espera, total_en_espera)

            rnd_llegada_display = random.random()
            t_entre = LLEGADA_MIN + (LLEGADA_MAX - LLEGADA_MIN) * rnd_llegada_display
            prox_llegada = reloj + t_entre

            if prox_llegada < DURACION_RECEPCION_MIN:
                heapq.heappush(eventos, Evento(tiempo=prox_llegada, tipo="llegada"))

            resultado.filas_tabla.append(
                _generar_snapshot(
                    numero_dia, "Llegada Cliente", reloj, numero_cliente, rnd_llegada_display, t_entre, prox_llegada,
                    rnd_tipo, tipo_cliente, servidores, colas, tiempo_atencion, fin_atencion, recaudacion, costo_bebidas
                )
            )

        elif evento.tipo.startswith("fin_atencion_"):
            tipo_servidor = evento.tipo.replace("fin_atencion_", "")
            cliente = evento.cliente
            servidor = servidores[tipo_servidor]
            cola = colas[tipo_servidor]

            cliente.tiempo_fin_atencion = reloj
            cliente.tiempo_espera = cliente.tiempo_inicio_atencion - cliente.tiempo_llegada

            if cliente.tiempo_espera > TIEMPO_ESPERA_BEBIDA:
                cliente.recibio_bebida = True
                bebidas += 1
                costo_bebidas += COSTO_BEBIDA

            if tipo_servidor == "colorista":
                recaudacion += PRECIO_COLORISTA
            else:
                recaudacion += PRECIO_PELUQUERO

            servidor.clientes_atendidos += 1
            clientes_atendidos += 1

            if cola:
                next_cliente = cola.popleft()
                next_cliente.tiempo_inicio_atencion = reloj
                next_cliente.longitud_cola_al_inicio = len(cola)
                demora = calcular_demora_corte(tipo_servidor, len(cola))
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
                    numero_dia, f"Fin At. {nombre}", reloj, cliente.numero, None, None, None,
                    None, None, servidores, colas, tiempo_atencion, fin_atencion, recaudacion, costo_bebidas
                )
            )

    resultado.recaudacion = recaudacion
    resultado.clientes_atendidos = clientes_atendidos
    resultado.bebidas_entregadas = bebidas
    resultado.costo_bebidas = costo_bebidas
    resultado.max_cola_espera = max_total_en_espera

    return resultado

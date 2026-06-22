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
    "Día", "Evento", "Reloj", "RND Llegada", "Próx. Llegada",
    "Colorista Estado", "Colorista Fin", "Cola Colorista",
    "Pel.A Estado", "Pel.A Fin", "Cola Pel.A",
    "Pel.B Estado", "Pel.B Fin", "Cola Pel.B",
]


def simular(dias: int, x: int) -> dict:
    """
    Punto de entrada principal de la simulación.

    Parámetros:
        dias  -- cantidad de días a simular
        x     -- umbral para calcular P(cola > x personas) en cualquier momento del día

    Retorna un diccionario con los resultados agregados y todas las filas para la tabla.
    La cantidad de filas es determinada por la simulación (total de eventos generados),
    no por la UI. La paginación es responsabilidad exclusiva de la interfaz.
    """
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


# ------------------------------------------------------------------
# Funciones auxiliares
# ------------------------------------------------------------------

def _seleccionar_tipo_con_rnd(rnd: float) -> str:
    """Selecciona el tipo de cliente basándose en un RND dado."""
    if rnd < PROB_COLORISTA:
        return "colorista"
    elif rnd < PROB_COLORISTA + PROB_PELUQUERO_A:
        return "peluquero_a"
    else:
        return "peluquero_b"


def _generar_snapshot(dia, tipo_evento, reloj, rnd_llegada, prox_llegada,
                      servidores, colas, fin_atencion_servidores):
    """Genera una fila de la tabla con el estado actual de la simulación."""
    fila = [
        str(dia),
        tipo_evento,
        f"{reloj:.2f}",
        f"{rnd_llegada:.4f}" if rnd_llegada is not None else "-",
        f"{prox_llegada:.2f}" if prox_llegada is not None else "-",
    ]

    for tipo in ["colorista", "peluquero_a", "peluquero_b"]:
        s = servidores[tipo]
        estado = "Ocupado" if s.ocupado else "Libre"
        fin = f"{fin_atencion_servidores[tipo]:.2f}" if s.ocupado else "-"
        cola_len = str(len(colas[tipo]))
        fila.extend([estado, fin, cola_len])

    return fila


# ------------------------------------------------------------------
# Simulación de un día
# ------------------------------------------------------------------

def _simular_dia(numero_dia: int) -> ResultadoDia:
    """
    Simula un único día de operación de la peluquería.

    Fases del día:
      1. Recepción activa: 480 minutos (8 horas) en que llegan nuevos clientes.
         Las llegadas se generan con tiempo entre llegadas U(2, 12).
      2. Cierre: se deja de recibir clientes pero se atiende a todos los que
         quedaron en cola o siendo atendidos.

    Tiempo de atención (demora del corte):
      - Se calcula con calcular_demora_corte(tipo_servidor, C)
        donde C = longitud de la cola al momento de iniciar la atención.
      - Método numérico: Euler con h = 1 min, 1 paso.

    Lógica de bebida:
      - Si cliente.tiempo_espera > 30 min → recibio_bebida = True

    Recaudación por cliente:
      - Colorista: $35.000
      - Peluquero A o B: $18.000
    """
    resultado = ResultadoDia(numero_dia=numero_dia)

    # Inicializar los 3 servidores
    servidores = {
        "colorista": Servidor("Colorista", "colorista"),
        "peluquero_a": Servidor("Peluquero A", "peluquero_a"),
        "peluquero_b": Servidor("Peluquero B", "peluquero_b"),
    }

    # Colas de espera (una por servidor)
    colas = {
        "colorista": deque(),
        "peluquero_a": deque(),
        "peluquero_b": deque(),
    }

    # Tiempo de fin de atención de cada servidor (para la tabla de eventos)
    fin_atencion = {
        "colorista": 0.0,
        "peluquero_a": 0.0,
        "peluquero_b": 0.0,
    }

    # Contadores del día
    reloj = 0.0
    recaudacion = 0.0
    bebidas = 0
    costo_bebidas = 0.0
    numero_cliente = 0
    clientes_atendidos = 0
    max_total_en_espera = 0   # máximo simultáneo de personas en todas las colas

    # Cola de prioridad de eventos (heapq ordena por Evento.tiempo via __lt__)
    eventos: list = []

    # ---- Generar primera llegada ----
    rnd_llegada = random.random()
    tiempo_entre = LLEGADA_MIN + (LLEGADA_MAX - LLEGADA_MIN) * rnd_llegada
    primera_llegada = tiempo_entre

    # Fila de inicialización (estado del sistema al comienzo del día)
    resultado.filas_tabla.append(
        _generar_snapshot(
            numero_dia, "Inicio", 0.0, rnd_llegada, primera_llegada,
            servidores, colas, fin_atencion,
        )
    )

    heapq.heappush(eventos, Evento(tiempo=primera_llegada, tipo="llegada"))

    # ================================================================
    # BUCLE PRINCIPAL — mientras haya eventos en la priority queue
    # ================================================================
    while eventos:
        evento = heapq.heappop(eventos)
        reloj = evento.tiempo

        # --------------------------------------------------------
        # EVENTO: LLEGADA
        # --------------------------------------------------------
        if evento.tipo == "llegada":
            # Si la recepción ya cerró, no admitir al cliente
            if reloj >= DURACION_RECEPCION_MIN:
                continue

            # Crear el cliente
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
                # Servidor libre → atender inmediatamente
                servidor.ocupado = True
                cliente.tiempo_inicio_atencion = reloj
                cliente.longitud_cola_al_inicio = len(cola)
                demora = calcular_demora_corte(tipo_cliente, len(cola))
                cliente.demora_calculada = demora
                fin = reloj + demora
                fin_atencion[tipo_cliente] = fin
                heapq.heappush(eventos, Evento(
                    tiempo=fin,
                    tipo=f"fin_atencion_{tipo_cliente}",
                    cliente=cliente,
                    servidor=servidor,
                ))
            else:
                # Servidor ocupado → encolar
                cola.append(cliente)

            # Actualizar máximo de personas en espera (suma de todas las colas)
            total_en_espera = sum(len(c) for c in colas.values())
            max_total_en_espera = max(max_total_en_espera, total_en_espera)

            # Generar próxima llegada (siempre se calcula para la tabla)
            rnd_llegada_display = random.random()
            tiempo_entre = LLEGADA_MIN + (LLEGADA_MAX - LLEGADA_MIN) * rnd_llegada_display
            prox_llegada = reloj + tiempo_entre

            # Solo programar si llega dentro del horario de recepción
            if prox_llegada < DURACION_RECEPCION_MIN:
                heapq.heappush(eventos, Evento(tiempo=prox_llegada, tipo="llegada"))

            # Snapshot de la tabla
            nombre = _NOMBRE_TIPO.get(tipo_cliente, tipo_cliente)
            evento_desc = f"Llegada C{numero_cliente} ({nombre})"
            resultado.filas_tabla.append(
                _generar_snapshot(
                    numero_dia, evento_desc, reloj, rnd_llegada_display, prox_llegada,
                    servidores, colas, fin_atencion,
                )
            )

        # --------------------------------------------------------
        # EVENTO: FIN DE ATENCIÓN
        # --------------------------------------------------------
        elif evento.tipo.startswith("fin_atencion_"):
            tipo_servidor = evento.tipo.replace("fin_atencion_", "")
            cliente = evento.cliente
            servidor = servidores[tipo_servidor]
            cola = colas[tipo_servidor]

            # Registrar fin de atención del cliente
            cliente.tiempo_fin_atencion = reloj
            cliente.tiempo_espera = cliente.tiempo_inicio_atencion - cliente.tiempo_llegada

            # ¿Recibe bebida gratis? (esperó más de 30 minutos)
            if cliente.tiempo_espera > TIEMPO_ESPERA_BEBIDA:
                cliente.recibio_bebida = True
                bebidas += 1
                costo_bebidas += COSTO_BEBIDA

            # Sumar recaudación según tipo de servicio
            if tipo_servidor == "colorista":
                recaudacion += PRECIO_COLORISTA
            else:
                recaudacion += PRECIO_PELUQUERO

            servidor.clientes_atendidos += 1
            clientes_atendidos += 1

            # Atender al siguiente de la cola (si hay)
            if cola:
                next_cliente = cola.popleft()
                next_cliente.tiempo_inicio_atencion = reloj
                next_cliente.longitud_cola_al_inicio = len(cola)   # longitud DESPUÉS del popleft
                demora = calcular_demora_corte(tipo_servidor, len(cola))
                next_cliente.demora_calculada = demora
                fin = reloj + demora
                fin_atencion[tipo_servidor] = fin
                heapq.heappush(eventos, Evento(
                    tiempo=fin,
                    tipo=f"fin_atencion_{tipo_servidor}",
                    cliente=next_cliente,
                    servidor=servidor,
                ))
            else:
                # Cola vacía → servidor queda libre
                servidor.ocupado = False
                fin_atencion[tipo_servidor] = 0.0

            # Actualizar máximo de personas en espera
            total_en_espera = sum(len(c) for c in colas.values())
            max_total_en_espera = max(max_total_en_espera, total_en_espera)

            # Snapshot de la tabla
            nombre = _NOMBRE_TIPO.get(tipo_servidor, tipo_servidor)
            evento_desc = f"Fin At. C{cliente.numero} ({nombre})"
            resultado.filas_tabla.append(
                _generar_snapshot(
                    numero_dia, evento_desc, reloj, None, None,
                    servidores, colas, fin_atencion,
                )
            )

    # ---- Guardar resultados del día ----
    resultado.recaudacion = recaudacion
    resultado.clientes_atendidos = clientes_atendidos
    resultado.bebidas_entregadas = bebidas
    resultado.costo_bebidas = costo_bebidas
    resultado.max_cola_espera = max_total_en_espera

    return resultado

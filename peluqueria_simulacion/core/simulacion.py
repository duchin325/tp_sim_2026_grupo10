import heapq
import random
import copy
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
MAX_ITERACIONES = 100_000

# Nombre legible para cada tipo de servidor (usado en la tabla de eventos)
_NOMBRE_TIPO = {
    "colorista": "Colorista",
    "peluquero_a": "Pel.A",
    "peluquero_b": "Pel.B",
}

# Encabezados base de la tabla de eventos (sin columnas de clientes)
_COLUMNAS_TABLA_BASE = [
    "Nro", "Día", "Evento", "Reloj (min)", "Reloj (HH:MM)",
    "RND Llegada", "T. Entre Lleg.", "Próx. Llegada",
    "RND Tipo", "Tipo Asignado",
    "Col. Estado", "Col. Cola", "Col. Fin At.",
    "PA Estado", "PA Cola", "PA Fin At.",
    "PB Estado", "PB Cola", "PB Fin At.",
    "Próx. Eventos",
    "Acum. Recaud.", "Acum. Bebidas", "Acum. Costo Beb.",
    "Clientes Atend.", "Máx Cola Total",
]

# Columnas por cada cliente temporal
_COLS_POR_CLIENTE = ["Estado", "Llegada", "Ini. At."]


def simular(n_dias: int, x_cola: int, h_euler: float = 1.0,
            prob_colorista: float = PROB_COLORISTA,
            prob_peluquero_a: float = PROB_PELUQUERO_A,
            llegada_min: float = LLEGADA_MIN,
            llegada_max: float = LLEGADA_MAX,
            t_colorista: int = 180,
            t_peluqueros: int = 130) -> dict:
    """
    Ejecuta la simulación de N días de la peluquería.

    Parámetros:
        n_dias           -- cantidad de días a simular
        x_cola           -- umbral para calcular P(cola > x_cola)
        h_euler          -- paso de integración Euler (default 1.0)
        prob_colorista   -- probabilidad de ser atendido por el Colorista
        prob_peluquero_a -- probabilidad de ser atendido por el Peluquero A
        llegada_min      -- límite inferior de U(A, B) para tiempo entre llegadas
        llegada_max      -- límite superior de U(A, B) para tiempo entre llegadas
        t_colorista      -- constante T de la ED para el Colorista
        t_peluqueros     -- constante T de la ED para los Peluqueros

    Retorna:
        Diccionario con resultados estadísticos, filas de la tabla,
        y objetos temporales por fila.
    """
    resultados: List[ResultadoDia] = []
    todas_las_filas: list = []
    todos_los_objetos: dict = {}  # nro_fila_global -> lista de clientes activos
    nro_fila_global = 0
    iteraciones_totales = 0

    recaudacion_acumulada = 0.0
    bebidas_acumuladas = 0
    costo_bebidas_acumulado = 0.0

    for numero_dia in range(1, n_dias + 1):
        resultado, iteraciones_dia, recaudacion_acumulada, bebidas_acumuladas, costo_bebidas_acumulado = _simular_dia(
            numero_dia,
            h_euler,
            nro_fila_offset=nro_fila_global,
            iteraciones_previas=iteraciones_totales,
            recaudacion_inicial=recaudacion_acumulada,
            bebidas_inicial=bebidas_acumuladas,
            costo_bebidas_inicial=costo_bebidas_acumulado,
            prob_colorista=prob_colorista,
            prob_peluquero_a=prob_peluquero_a,
            llegada_min=llegada_min,
            llegada_max=llegada_max,
            t_colorista=t_colorista,
            t_peluqueros=t_peluqueros,
        )
        resultados.append(resultado)

        # Re-numerar filas globalmente y consolidar objetos temporales
        for fila in resultado.filas_tabla:
            todas_las_filas.append(fila)

        for nro_local, clientes in resultado.objetos_por_fila.items():
            todos_los_objetos[nro_local] = clientes

        nro_fila_global += len(resultado.filas_tabla)
        iteraciones_totales += iteraciones_dia

        # Cap de 100K iteraciones totales
        if iteraciones_totales >= MAX_ITERACIONES:
            break

    resumen = generar_resumen(recaudacion_acumulada, len(resultados), resultados, x_cola)

    # --- Post-proceso: agregar columnas de clientes temporales ---
    filas_con_clientes, encabezados_completos = _agregar_columnas_clientes(
        todas_las_filas, todos_los_objetos
    )

    filas_tabla = [encabezados_completos] + filas_con_clientes

    return {
        "promedio_recaudacion": resumen["promedio_recaudacion"],
        "probabilidad_mas_de_x": resumen["probabilidad_mas_de_x"],
        "clientes_atendidos": resumen["clientes_atendidos"],
        "bebidas_entregadas": resumen["bebidas_entregadas"],
        "costo_total_bebidas": resumen["costo_total_bebidas"],
        "filas_tabla": filas_tabla,
        "objetos_por_fila": todos_los_objetos,
        "iteraciones_totales": iteraciones_totales,
        "dias_simulados": len(resultados),
    }


def _agregar_columnas_clientes(filas: list, objetos_por_fila: dict) -> tuple:
    """
    Post-procesa las filas de la tabla para agregar columnas de clientes temporales.

    Para cada fila, agrega 3 columnas por cada cliente activo en ese instante:
    - Estado, Llegada, Ini. At.

    Retorna:
        (filas_extendidas, encabezados_completos)
    """
    # Determinar el máximo de clientes simultáneos en cualquier fila
    max_clientes = 0
    for clientes in objetos_por_fila.values():
        if len(clientes) > max_clientes:
            max_clientes = len(clientes)

    # Generar encabezados dinámicos
    encabezados_clientes = []
    for i in range(1, max_clientes + 1):
        for col in _COLS_POR_CLIENTE:
            encabezados_clientes.append(f"Cli {i} {col}")

    encabezados_completos = list(_COLUMNAS_TABLA_BASE) + encabezados_clientes

    cols_vacias = ["-"] * (max_clientes * len(_COLS_POR_CLIENTE))

    filas_extendidas = []
    for fila in filas:
        nro_fila = int(fila[0])
        clientes = objetos_por_fila.get(nro_fila, [])

        columnas_clientes = []
        for cliente in clientes:
            tipo_nombre = _NOMBRE_TIPO.get(cliente.tipo, cliente.tipo)

            # Estado
            if cliente.estado == "en_cola":
                estado_txt = f"Cola {tipo_nombre}"
            elif cliente.estado == "siendo_atendido":
                estado_txt = f"Atend. {tipo_nombre}"
            else:
                estado_txt = "Atendido"

            columnas_clientes.append(estado_txt)
            columnas_clientes.append(f"{cliente.tiempo_llegada:.2f}")

            if cliente.estado == "siendo_atendido" and cliente.tiempo_inicio_atencion > 0:
                columnas_clientes.append(f"{cliente.tiempo_inicio_atencion:.2f}")
            else:
                columnas_clientes.append("-")

        # Rellenar columnas faltantes con "-"
        faltan = (max_clientes * len(_COLS_POR_CLIENTE)) - len(columnas_clientes)
        if faltan > 0:
            columnas_clientes.extend(["-"] * faltan)

        filas_extendidas.append(list(fila) + columnas_clientes)

    return filas_extendidas, encabezados_completos


def _seleccionar_tipo_con_rnd(rnd: float, prob_colorista: float, prob_peluquero_a: float) -> str:
    """Selecciona el tipo de cliente basándose en un RND dado."""
    if rnd < prob_colorista:
        return "colorista"
    elif rnd < prob_colorista + prob_peluquero_a:
        return "peluquero_a"
    else:
        return "peluquero_b"


def _formato_hhmm(minutos: float) -> str:
    """Convierte minutos a formato HH:MM."""
    h = int(minutos // 60)
    m = int(minutos % 60)
    return f"{h:02d}:{m:02d}"


def _formato_proximos_eventos(eventos_heap: list) -> str:
    """Genera un string resumen de los próximos eventos programados."""
    if not eventos_heap:
        return "-"
    partes = []
    # Copiar y ordenar sin alterar el heap
    eventos_ordenados = sorted(eventos_heap, key=lambda e: e.tiempo)
    for ev in eventos_ordenados[:5]:  # Mostrar máximo 5 próximos
        nombre = ev.tipo.replace("fin_atencion_", "Fin ")
        nombre = nombre.replace("colorista", "Col.").replace("peluquero_a", "PA").replace("peluquero_b", "PB")
        nombre = nombre.replace("llegada", "Lleg.")
        partes.append(f"{nombre}:{ev.tiempo:.1f}")
    return " | ".join(partes)


def _capturar_objetos_temporales(servidores: dict, colas: dict, reloj: float) -> list:
    """
    Captura una copia de todos los clientes activos en el sistema
    (siendo atendidos + en cola) en el instante actual.
    """
    clientes_activos = []

    for tipo in ["colorista", "peluquero_a", "peluquero_b"]:
        servidor = servidores[tipo]
        # Cliente siendo atendido
        if servidor.ocupado and servidor.cliente_actual is not None:
            c = copy.copy(servidor.cliente_actual)
            c.estado = "siendo_atendido"
            clientes_activos.append(c)

        # Clientes en cola
        for cliente_cola in colas[tipo]:
            c = copy.copy(cliente_cola)
            c.estado = "en_cola"
            c.tiempo_espera = reloj - c.tiempo_llegada
            clientes_activos.append(c)

    return clientes_activos


def _generar_snapshot(nro_fila, dia, tipo_evento, reloj,
                      nro_cliente, rnd_llegada, t_entre, prox_llegada,
                      rnd_tipo, tipo_asignado,
                      servidores, colas, fin_atencion,
                      eventos_heap,
                      acum_recaud, acum_bebidas, acum_costo_beb,
                      clientes_atendidos, max_cola_total):
    """Genera una fila de la tabla con el estado actual de la simulación."""
    fila = [
        str(nro_fila),
        str(dia),
        tipo_evento,
        f"{reloj:.2f}",
        _formato_hhmm(reloj),
        f"{rnd_llegada:.4f}" if rnd_llegada is not None else "-",
        f"{t_entre:.2f}" if t_entre is not None else "-",
        f"{prox_llegada:.2f}" if prox_llegada is not None else "-",
        f"{rnd_tipo:.4f}" if rnd_tipo is not None else "-",
        _NOMBRE_TIPO.get(tipo_asignado, "-") if tipo_asignado else "-",
    ]

    for tipo in ["colorista", "peluquero_a", "peluquero_b"]:
        s = servidores[tipo]
        estado = "Ocupado" if s.ocupado else "Libre"
        cola_len = str(len(colas[tipo]))
        fin = f"{fin_atencion[tipo]:.2f}" if s.ocupado else "-"
        fila.extend([estado, cola_len, fin])

    # Próximos eventos programados
    fila.append(_formato_proximos_eventos(eventos_heap))

    # Variables auxiliares
    fila.extend([
        f"${acum_recaud:,.2f}",
        str(acum_bebidas),
        f"${acum_costo_beb:,.2f}",
        str(clientes_atendidos),
        str(max_cola_total),
    ])

    return fila


def _simular_dia(numero_dia: int, h_euler: float,
                 nro_fila_offset: int, iteraciones_previas: int,
                 recaudacion_inicial: float, bebidas_inicial: int,
                 costo_bebidas_inicial: float,
                 prob_colorista: float = PROB_COLORISTA,
                 prob_peluquero_a: float = PROB_PELUQUERO_A,
                 llegada_min: float = LLEGADA_MIN,
                 llegada_max: float = LLEGADA_MAX,
                 t_colorista: int = 180,
                 t_peluqueros: int = 130) -> tuple:
    """
    Simula un día completo de la peluquería.

    Retorna:
        (ResultadoDia, iteraciones_dia, recaudacion_acumulada, bebidas_acumuladas,
         costo_bebidas_acumulado)
    """
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

    reloj = 0.0
    recaudacion = 0.0
    bebidas = 0
    costo_bebidas = 0.0
    recaudacion_acumulada = recaudacion_inicial
    bebidas_acumuladas = bebidas_inicial
    costo_bebidas_acumulado = costo_bebidas_inicial
    numero_cliente = 0
    clientes_atendidos = 0
    max_total_en_espera = 0
    nro_fila_local = 0
    iteraciones_dia = 0

    eventos: list = []

    # ---- Generar primera llegada ----
    rnd_llegada = random.random()
    tiempo_entre = llegada_min + (llegada_max - llegada_min) * rnd_llegada
    prox_llegada = tiempo_entre

    nro_fila_actual = nro_fila_offset + nro_fila_local
    resultado.filas_tabla.append(
        _generar_snapshot(
            nro_fila_actual, numero_dia, "Inicialización", 0.0,
            None, rnd_llegada, tiempo_entre, prox_llegada,
            None, None, servidores, colas, fin_atencion,
            [],  # sin eventos aún en el heap
            recaudacion_acumulada, bebidas_acumuladas, costo_bebidas_acumulado,
            clientes_atendidos, max_total_en_espera
        )
    )
    resultado.objetos_por_fila[nro_fila_actual] = _capturar_objetos_temporales(
        servidores, colas, 0.0
    )
    nro_fila_local += 1

    heapq.heappush(eventos, Evento(tiempo=prox_llegada, tipo="llegada"))

    while eventos:
        # Cap de iteraciones
        if (iteraciones_previas + iteraciones_dia) >= MAX_ITERACIONES:
            break

        evento = heapq.heappop(eventos)
        reloj = evento.tiempo
        iteraciones_dia += 1

        if evento.tipo == "llegada":
            if reloj >= DURACION_RECEPCION_MIN:
                continue

            numero_cliente += 1
            rnd_tipo = random.random()
            tipo_cliente = _seleccionar_tipo_con_rnd(rnd_tipo, prob_colorista, prob_peluquero_a)

            cliente = Cliente(
                numero=numero_cliente,
                tipo=tipo_cliente,
                tiempo_llegada=reloj,
                estado="en_cola",
            )

            servidor = servidores[tipo_cliente]
            cola = colas[tipo_cliente]

            if not servidor.ocupado:
                servidor.ocupado = True
                servidor.cliente_actual = cliente
                cliente.tiempo_inicio_atencion = reloj
                cliente.estado = "siendo_atendido"
                cliente.longitud_cola_al_inicio = len(cola)

                demora, pasos = calcular_demora_corte(
                    tipo_cliente, len(cola), h=h_euler, con_detalle=True,
                    t_colorista=t_colorista, t_peluqueros=t_peluqueros,
                )
                cliente.demora_calculada = demora
                cliente.pasos_euler = pasos

                fin = reloj + demora
                fin_atencion[tipo_cliente] = fin
                heapq.heappush(eventos, Evento(
                    tiempo=fin,
                    tipo=f"fin_atencion_{tipo_cliente}",
                    cliente=cliente,
                    servidor=servidor,
                ))
            else:
                cola.append(cliente)
                # Programar evento de comienzo de refrigerio (30 minutos después de llegar)
                tiempo_comienzo_refrig = reloj + TIEMPO_ESPERA_BEBIDA
                heapq.heappush(eventos, Evento(
                    tiempo=tiempo_comienzo_refrig,
                    tipo=f"comienzo_refrigerio_{tipo_cliente}",
                    cliente=cliente,
                ))

            total_en_espera = sum(len(c) for c in colas.values())
            max_total_en_espera = max(max_total_en_espera, total_en_espera)

            # Generar próxima llegada
            rnd_llegada_sig = random.random()
            t_entre = llegada_min + (llegada_max - llegada_min) * rnd_llegada_sig
            prox_llegada = reloj + t_entre

            if prox_llegada < DURACION_RECEPCION_MIN:
                heapq.heappush(eventos, Evento(tiempo=prox_llegada, tipo="llegada"))

            nro_fila_actual = nro_fila_offset + nro_fila_local
            resultado.filas_tabla.append(
                _generar_snapshot(
                    nro_fila_actual, numero_dia, "Llegada Cliente", reloj,
                    numero_cliente, rnd_llegada_sig, t_entre, prox_llegada,
                    rnd_tipo, tipo_cliente, servidores, colas, fin_atencion,
                    eventos,
                    recaudacion_acumulada, bebidas_acumuladas, costo_bebidas_acumulado,
                    clientes_atendidos, max_total_en_espera
                )
            )
            resultado.objetos_por_fila[nro_fila_actual] = _capturar_objetos_temporales(
                servidores, colas, reloj
            )
            nro_fila_local += 1

        elif evento.tipo.startswith("fin_atencion_"):
            tipo_servidor = evento.tipo.replace("fin_atencion_", "")
            cliente = evento.cliente
            servidor = servidores[tipo_servidor]
            cola = colas[tipo_servidor]

            cliente.tiempo_fin_atencion = reloj
            cliente.estado = "atendido"
            cliente.tiempo_espera = cliente.tiempo_inicio_atencion - cliente.tiempo_llegada

            # El refresco ya se cuenta cuando el cliente supera 30 minutos en cola.
            if cliente.elegible_refrigerio and not cliente.recibio_bebida:
                cliente.recibio_bebida = True
                bebidas += 1
                costo_bebidas += COSTO_BEBIDA
                bebidas_acumuladas += 1
                costo_bebidas_acumulado += COSTO_BEBIDA

            if tipo_servidor == "colorista":
                recaudacion += PRECIO_COLORISTA
                recaudacion_acumulada += PRECIO_COLORISTA
            else:
                recaudacion += PRECIO_PELUQUERO
                recaudacion_acumulada += PRECIO_PELUQUERO

            servidor.clientes_atendidos += 1
            clientes_atendidos += 1

            if cola:
                # Sacar el siguiente cliente de la cola
                next_cliente = cola.popleft()
                # La longitud de cola es lo que queda esperando
                longitud_cola = len(cola)
                
                next_cliente.tiempo_inicio_atencion = reloj
                next_cliente.estado = "siendo_atendido"
                next_cliente.longitud_cola_al_inicio = longitud_cola

                demora, pasos = calcular_demora_corte(
                    tipo_servidor, longitud_cola, h=h_euler, con_detalle=True,
                    t_colorista=t_colorista, t_peluqueros=t_peluqueros,
                )
                next_cliente.demora_calculada = demora
                next_cliente.pasos_euler = pasos

                fin = reloj + demora
                fin_atencion[tipo_servidor] = fin
                servidor.cliente_actual = next_cliente
                heapq.heappush(eventos, Evento(
                    tiempo=fin,
                    tipo=f"fin_atencion_{tipo_servidor}",
                    cliente=next_cliente,
                    servidor=servidor,
                ))
            else:
                servidor.ocupado = False
                servidor.cliente_actual = None
                fin_atencion[tipo_servidor] = 0.0

            total_en_espera = sum(len(c) for c in colas.values())
            max_total_en_espera = max(max_total_en_espera, total_en_espera)

            nombre = _NOMBRE_TIPO.get(tipo_servidor, tipo_servidor)
            nro_fila_actual = nro_fila_offset + nro_fila_local
            resultado.filas_tabla.append(
                _generar_snapshot(
                    nro_fila_actual, numero_dia, f"Fin At. {nombre} (Cli {cliente.numero})", reloj,
                    cliente.numero, None, None, None,
                    None, None, servidores, colas, fin_atencion,
                    eventos,
                    recaudacion_acumulada, bebidas_acumuladas, costo_bebidas_acumulado,
                    clientes_atendidos, max_total_en_espera
                )
            )
            resultado.objetos_por_fila[nro_fila_actual] = _capturar_objetos_temporales(
                servidores, colas, reloj
            )
            nro_fila_local += 1

        elif evento.tipo.startswith("comienzo_refrigerio_"):
            # Evento cuando un cliente alcanza 30 minutos de espera en la cola
            tipo_servidor = evento.tipo.replace("comienzo_refrigerio_", "")
            cliente = evento.cliente
            cola = colas[tipo_servidor]

            # Verificar si el cliente aún está en la cola (no ha sido atendido)
            if cliente in cola and not cliente.elegible_refrigerio:
                cliente.elegible_refrigerio = True
                cliente.recibio_bebida = True
                cliente.tiempo_comienzo_refrigerio = reloj
                bebidas += 1
                costo_bebidas += COSTO_BEBIDA
                bebidas_acumuladas += 1
                costo_bebidas_acumulado += COSTO_BEBIDA
                recaudacion_acumulada -= COSTO_BEBIDA

                nro_fila_actual = nro_fila_offset + nro_fila_local
                resultado.filas_tabla.append(
                    _generar_snapshot(
                        nro_fila_actual, numero_dia, f"Comienzo Refrig {cliente.numero}", reloj,
                        cliente.numero, None, None, None,
                        None, None, servidores, colas, fin_atencion,
                        eventos,
                        recaudacion_acumulada, bebidas_acumuladas, costo_bebidas_acumulado,
                        clientes_atendidos, max_total_en_espera
                    )
                )
                resultado.objetos_por_fila[nro_fila_actual] = _capturar_objetos_temporales(
                    servidores, colas, reloj
                )
                nro_fila_local += 1

    resultado.recaudacion = recaudacion - costo_bebidas  # Recaudación neta (ingresos - costo refrigerios)
    resultado.clientes_atendidos = clientes_atendidos
    resultado.bebidas_entregadas = bebidas
    resultado.costo_bebidas = costo_bebidas
    resultado.max_cola_espera = max_total_en_espera

    return (
        resultado,
        iteraciones_dia,
        recaudacion_acumulada,
        bebidas_acumuladas,
        costo_bebidas_acumulado,
    )

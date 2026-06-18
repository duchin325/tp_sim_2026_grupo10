from typing import List
from core.entidades import ResultadoDia

# Importaciones que se usarán cuando se implemente la simulación completa:
#   from core.distribuciones import generar_tiempo_llegada, seleccionar_tipo_cliente
#   from core.runge_kutta import calcular_demora_corte
#   from core.resultados import generar_resumen

# Constantes del dominio
DURACION_RECEPCION_MIN = 480   # 8 horas en minutos
TIEMPO_ESPERA_BEBIDA = 30      # minutos; si el cliente espera más, recibe bebida gratis
PRECIO_COLORISTA = 35_000
PRECIO_PELUQUERO = 18_000
COSTO_BEBIDA = 6_500


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
    # TODO: Ejecutar _simular_dia() para cada día y acumular ResultadoDia en una lista
    resultados: List[ResultadoDia] = []
    for numero_dia in range(1, dias + 1):
        resultado = _simular_dia(numero_dia)
        resultados.append(resultado)

    # TODO: Llamar a core.resultados.generar_resumen(resultados, x) con la lista real
    # Mock: ~10 eventos por día para que la paginación pueda demostrarse
    filas_mock = _generar_filas_mock(dias * 10)

    return {
        "promedio_recaudacion": 0.0,    # TODO: reemplazar con generar_resumen()["promedio_recaudacion"]
        "probabilidad_mas_de_x": 0.0,   # TODO: reemplazar con generar_resumen()["probabilidad_mas_de_x"]
        "clientes_atendidos": 0,         # TODO: reemplazar con total real
        "bebidas_entregadas": 0,         # TODO: reemplazar con total real
        "costo_total_bebidas": 0.0,      # TODO: reemplazar con total real
        "filas_tabla": filas_mock,
    }


def _simular_dia(numero_dia: int) -> ResultadoDia:
    """
    Simula un único día de operación de la peluquería.

    Fases del día:
      1. Recepción activa: 480 minutos (8 horas) en que llegan nuevos clientes.
         Las llegadas se generan con generar_tiempo_llegada() → U(2, 12).
      2. Cierre: se deja de recibir clientes pero se atiende a todos los que quedaron.

    Tiempo de atención (demora del corte):
      - Se calcula con calcular_demora_corte(tipo_servidor, C, pasos)
        donde C = longitud_cola_al_inicio del cliente que comienza a ser atendido.
      - T = 180 para el colorista; T = 130 para Peluquero A y Peluquero B.
      - TODO: definir el valor de `pasos` una vez que se aclare el criterio de
              finalización de la integración RK4.

    Lógica de bebida:
      - Si cliente.tiempo_espera > TIEMPO_ESPERA_BEBIDA (30 min) → recibio_bebida = True
      - Cada bebida tiene costo COSTO_BEBIDA ($6.500)

    Recaudación por cliente:
      - Colorista: PRECIO_COLORISTA ($35.000)
      - Peluquero A o B: PRECIO_PELUQUERO ($18.000)
    """
    resultado = ResultadoDia(numero_dia=numero_dia)

    # TODO: Inicializar el reloj de simulación en 0
    # TODO: Generar primer evento de llegada con generar_tiempo_llegada()
    # TODO: Inicializar los 3 servidores usando la clase Servidor:
    #         - Servidor("Colorista",   "colorista")
    #         - Servidor("Peluquero A", "peluquero_a")
    #         - Servidor("Peluquero B", "peluquero_b")
    # TODO: Inicializar una cola de espera (list o deque) por cada servidor
    # TODO: Inicializar contadores de recaudación, bebidas y cola máxima

    # TODO: Bucle principal — mientras haya eventos en la priority queue (heapq):
    #
    #   [EVENTO LLEGADA]
    #   - Avanzar reloj al tiempo del evento
    #   - Crear Cliente con tipo = seleccionar_tipo_cliente()
    #   - Registrar cliente.tiempo_llegada = reloj
    #   - Si el servidor correspondiente está libre:
    #       · cliente.longitud_cola_al_inicio = 0
    #       · cliente.demora_calculada = calcular_demora_corte(tipo, 0, pasos)
    #       · marcar servidor ocupado, programar evento "fin_atencion"
    #   - Si está ocupado:
    #       · encolar el cliente en la cola del servidor
    #   - Si reloj < DURACION_RECEPCION_MIN: generar y encolar próxima llegada
    #   - Guardar snapshot en resultado.filas_tabla si el índice de fila corresponde
    #
    #   [EVENTO FIN_ATENCION]
    #   - Avanzar reloj al tiempo del evento
    #   - Calcular cliente.tiempo_espera = cliente.tiempo_inicio_atencion - cliente.tiempo_llegada
    #   - Si tiempo_espera > TIEMPO_ESPERA_BEBIDA → recibio_bebida = True, sumar a resultado
    #   - Sumar recaudación según tipo de cliente (PRECIO_COLORISTA o PRECIO_PELUQUERO)
    #   - Si la cola del servidor no está vacía:
    #       · Sacar siguiente cliente de la cola
    #       · cliente.longitud_cola_al_inicio = len(cola) al momento de iniciar
    #       · cliente.demora_calculada = calcular_demora_corte(tipo, C, pasos)
    #       · Programar nuevo evento "fin_atencion"
    #   - Si la cola está vacía: marcar servidor como libre

    return resultado


def _generar_filas_mock(cantidad_filas: int) -> list:
    """Genera filas de ejemplo para la tabla mientras no hay simulación real."""
    columnas = [
        "Evento", "Reloj", "RND Llegada", "Próx. Llegada",
        "Colorista Estado", "Colorista Fin", "Cola Colorista",
        "Pel.A Estado", "Pel.A Fin", "Cola Pel.A",
        "Pel.B Estado", "Pel.B Fin", "Cola Pel.B",
    ]
    filas = [columnas]
    for i in range(1, cantidad_filas + 1):
        fila = [str(i), "-", "-", "-", "Libre", "-", "0", "Libre", "-", "0", "Libre", "-", "0"]
        filas.append(fila)
    return filas

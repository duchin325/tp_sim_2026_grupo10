from typing import List
from core.entidades import ResultadoDia

def calcular_promedio_recaudacion(resultados: List[ResultadoDia]) -> float:
    """Calcula el promedio de recaudación diaria sobre todos los días simulados."""
    if not resultados:
        return 0.0
    recaudacion_total = sum(r.recaudacion for r in resultados)
    return recaudacion_total / len(resultados)


def calcular_probabilidad_mas_de_x(resultados: List[ResultadoDia], x: int) -> float:
    """
    Calcula la probabilidad de que en algún día la cola haya superado las X personas.
    Se define como: (Casos favorables) / (Casos posibles)
    Casos favorables = Días donde la cola máxima fue estrictamente mayor a X.
    Casos posibles = Total de días simulados.
    """
    if not resultados:
        return 0.0
    
    dias_con_cola_excedida = 0
    for dia in resultados:
        if dia.max_cola_espera > x:
            dias_con_cola_excedida += 1
            
    return dias_con_cola_excedida / len(resultados)


def calcular_total_clientes_atendidos(resultados: List[ResultadoDia]) -> int:
    """Suma los clientes atendidos en todos los días simulados."""
    return sum(r.clientes_atendidos for r in resultados)


def calcular_total_bebidas(resultados: List[ResultadoDia]) -> int:
    """Suma las bebidas entregadas (por espera > 30 min) en todos los días simulados."""
    return sum(r.bebidas_entregadas for r in resultados)


def calcular_costo_total_bebidas(resultados: List[ResultadoDia]) -> float:
    """Suma el costo total de las bebidas entregadas en todos los días simulados."""
    return sum(r.costo_bebidas for r in resultados)


def generar_resumen(resultados: List[ResultadoDia], x: int) -> dict:
    """
    Consolida todos los indicadores en un único diccionario para que
    la interfaz gráfica (UI) pueda mostrarlos fácilmente.
    """
    return {
        "promedio_recaudacion": calcular_promedio_recaudacion(resultados),
        "probabilidad_mas_de_x": calcular_probabilidad_mas_de_x(resultados, x),
        "clientes_atendidos": calcular_total_clientes_atendidos(resultados),
        "bebidas_entregadas": calcular_total_bebidas(resultados),
        "costo_total_bebidas": calcular_costo_total_bebidas(resultados),
    }
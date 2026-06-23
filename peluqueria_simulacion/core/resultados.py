from typing import List
from core.entidades import ResultadoDia


def calcular_promedio_recaudacion(total_recaudacion: float, n_dias: int) -> float:
    """Promedio de recaudación diaria: R̄ = acumulado / N días simulados."""
    if n_dias <= 0:
        return 0.0
    return total_recaudacion / n_dias


def calcular_probabilidad_mas_de_x(resultados: List[ResultadoDia], x: int) -> float:
    """
    Calcula la proporción de días en que, en algún momento,
    la cantidad total de personas esperando en cola superó X.

    P(cola > X) = días_superado / N
    """
    if not resultados:
        return 0.0
    dias_superado = sum(1 for r in resultados if r.max_cola_espera > x)
    return dias_superado / len(resultados)


def calcular_total_clientes_atendidos(resultados: List[ResultadoDia]) -> int:
    """Suma clientes atendidos en todos los días simulados."""
    return sum(r.clientes_atendidos for r in resultados)


def calcular_total_bebidas(resultados: List[ResultadoDia]) -> int:
    """Suma bebidas entregadas en todos los días simulados."""
    return sum(r.bebidas_entregadas for r in resultados)


def calcular_costo_total_bebidas(resultados: List[ResultadoDia]) -> float:
    """Suma el costo de bebidas de todos los días simulados."""
    return sum(r.costo_bebidas for r in resultados)


def generar_resumen(total_recaudacion: float, n_dias: int,
                     resultados: List[ResultadoDia], x: int) -> dict:
    """Consolida todos los indicadores en un único diccionario de resultados."""
    return {
        "promedio_recaudacion": calcular_promedio_recaudacion(total_recaudacion, n_dias),
        "probabilidad_mas_de_x": calcular_probabilidad_mas_de_x(resultados, x),
        "clientes_atendidos": calcular_total_clientes_atendidos(resultados),
        "bebidas_entregadas": calcular_total_bebidas(resultados),
        "costo_total_bebidas": calcular_costo_total_bebidas(resultados),
    }

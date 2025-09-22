# -*- coding: utf-8 -*-
"""
Parámetros del análisis de sensibilidad para el parque - ESCENARIO ADMINISTRACIÓN PROPIA.
Edita libremente los valores, probabilidades y horizontes.
Las cifras de 'npv' se interpretan como valores presentes (VPN) ya descontados.
"""

# Tasa de descuento opcional para análisis alternativo (no usada en el cálculo base)
discount_rate = 0.12  # 12% anual (solo informativo en este borrador)

# Definición de actividades - ESCENARIO ADMINISTRACIÓN PROPIA
# Cada actividad posee:
# - decision_key: nombre corto para la decisión binaria (1 = se mantiene / se invierte, 0 = no)
# - horizon_years: horizonte temporal de evaluación (informativo)
# - outcomes: lista de escenarios con 'label', 'prob' (0-1) y 'npv' (valor presente del resultado)
#
# Nota: Puedes ajustar probabilidades y montos. Deben sumar 1.0 por actividad.
activities = [
    {
        "name": "Alojamiento (Lodge)",
        "decision_key": "lodge",
        "horizon_years": 2,
        "outcomes": [
            {"label": "Éxito", "prob": 0.10, "npv": 100000.0},
            {"label": "Fracaso", "prob": 0.90, "npv": -10000.0},
        ],
    },
    {
        "name": "Cabalgatas",
        "decision_key": "cabalgatas",
        "horizon_years": 3,
        "outcomes": [
            {"label": "Éxito", "prob": 0.30, "npv": 15000.0},
            {"label": "Fracaso", "prob": 0.70, "npv": -60000.0},
        ],
    },
    {
        "name": "Trekking",
        "decision_key": "trekking",
        "horizon_years": 2,
        "outcomes": [
            {"label": "Éxito Alto", "prob": 0.20, "npv": 25000.0},
            {"label": "Éxito Moderado", "prob": 0.50, "npv": 8000.0},
            {"label": "Fracaso", "prob": 0.30, "npv": -12000.0},
        ],
    },
    {
        "name": "Mountain Bike",
        "decision_key": "mtb",
        "horizon_years": 3,
        "outcomes": [
            {"label": "Éxito", "prob": 0.35, "npv": 30000.0},
            {"label": "Neutro", "prob": 0.25, "npv": 0.0},
            {"label": "Fracaso", "prob": 0.40, "npv": -20000.0},
        ],
    },
    {
        "name": "Kayak",
        "decision_key": "kayak",
        "horizon_years": 2,
        "outcomes": [
            {"label": "Éxito", "prob": 0.25, "npv": 18000.0},
            {"label": "Neutro", "prob": 0.25, "npv": 2000.0},
            {"label": "Fracaso", "prob": 0.50, "npv": -9000.0},
        ],
    },
    {
        "name": "Tours Guiados",
        "decision_key": "tours_guiados",
        "horizon_years": 3,
        "outcomes": [
            {"label": "Alta Demanda", "prob": 0.25, "npv": 35000.0},
            {"label": "Demanda Moderada", "prob": 0.45, "npv": 12000.0},
            {"label": "Baja Demanda", "prob": 0.30, "npv": -8000.0},
        ],
    },
    {
        "name": "Jornadas de Educación",
        "decision_key": "jornadas_educacion",
        "horizon_years": 2,
        "outcomes": [
            {"label": "Éxito Académico", "prob": 0.40, "npv": 20000.0},
            {"label": "Participación Regular", "prob": 0.35, "npv": 6000.0},
            {"label": "Baja Participación", "prob": 0.25, "npv": -15000.0},
        ],
    },
    {
        "name": "Eventos Especiales",
        "decision_key": "eventos_especiales",
        "horizon_years": 2,
        "outcomes": [
            {"label": "Evento Exitoso", "prob": 0.30, "npv": 28000.0},
            {"label": "Evento Regular", "prob": 0.40, "npv": 8000.0},
            {"label": "Evento Fallido", "prob": 0.30, "npv": -12000.0},
        ],
    },
    {
        "name": "Arriendo de Espacios",
        "decision_key": "arriendo_espacios",
        "horizon_years": 4,
        "outcomes": [
            {"label": "Alta Ocupación", "prob": 0.35, "npv": 40000.0},
            {"label": "Ocupación Moderada", "prob": 0.45, "npv": 15000.0},
            {"label": "Baja Ocupación", "prob": 0.20, "npv": -5000.0},
        ],
    },
    {
        "name": "Señaléticas",
        "decision_key": "senaleticas",
        "horizon_years": 1,
        "outcomes": [
            {"label": "Beneficio", "prob": 0.70, "npv": 5000.0},
            {"label": "Pérdida", "prob": 0.30, "npv": -5000.0},
        ],
    },
]

# Orden consistente de las decisiones para construir combinaciones (2^10)
decision_order = [a["decision_key"] for a in activities]

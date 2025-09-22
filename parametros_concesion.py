# -*- coding: utf-8 -*-
"""
Parámetros del análisis de sensibilidad para el parque - ESCENARIO CONCESIÓN.
Edita libremente los valores, probabilidades y horizontes.
Las cifras de 'npv' representan flujos futuros al final del horizonte temporal.
El código descontará automáticamente estos flujos al presente usando la tasa de descuento.
"""

# Tasa de descuento para descontar flujos futuros al presente
discount_rate = 0.06  # 12% anual

# Definición de actividades - ESCENARIO CONCESIÓN
# Cada actividad posee:
# - decision_key: nombre corto para la decisión binaria (1 = se mantiene / se invierte, 0 = no)
# - horizon_years: horizonte temporal de evaluación (informativo)
# - outcomes: lista de escenarios con 'label', 'prob' (0-1) y 'npv' (flujo futuro al final del horizonte)
#
# Nota: Puedes ajustar probabilidades y montos. Deben sumar 1.0 por actividad.
activities = [
    {
        "name": "Alojamiento (Lodge)",
        "decision_key": "lodge",
        "horizon_years": 2,
        "outcomes": [
            {"label": "Éxito Alto", "prob": 0.0625, "npv": 33147321.4},
            {"label": "Éxito Moderado", "prob": 0.0625, "npv": 11732142.9},
            {"label": "Fracaso", "prob": 0.875, "npv": 5866071.43},
        ],
    },
    {
        "name": "Cabalgatas",
        "decision_key": "cabalgatas",
        "horizon_years": 3,
        "outcomes": [
            {"label": "Alta Demanda", "prob": 0.1875, "npv": -39750000.0},
            {"label": "Demanda Regular", "prob": 0.3125, "npv": -66750000.0},
            {"label": "Baja Demanda", "prob": 0.50, "npv": -82950000.0},
        ],
    },
    {
        "name": "Trekking",
        "decision_key": "trekking",
        "horizon_years": 2,
        "outcomes": [
            {"label": "Éxito Alto", "prob": 0.25, "npv": 262500000.0},
            {"label": "Éxito Moderado", "prob": 0.4375, "npv": 131250000.0},
            {"label": "Fracaso", "prob": 0.3125, "npv": 37500000.0},
        ],
    },
    {
        "name": "Mountain Bike",
        "decision_key": "mtb",
        "horizon_years": 3,
        "outcomes": [
            {"label": "Éxito", "prob": 0.1875, "npv": 18750000.0},
            {"label": "Neutro", "prob": 0.3125, "npv": 9375000.0},
            {"label": "Fracaso", "prob": 0.50, "npv": 4687500.0},
        ],
    },
    {
        "name": "Kayak",
        "decision_key": "kayak",
        "horizon_years": 2,
        "outcomes": [
            {"label": "Éxito", "prob": 0.25, "npv": 1125000.0},
            {"label": "Neutro", "prob": 0.4375, "npv": 562500.0},
            {"label": "Fracaso", "prob": 0.3125, "npv": 187500.0},
        ],
    },
    {
        "name": "Tours Guiados",
        "decision_key": "tours_guiados",
        "horizon_years": 3,
        "outcomes": [
            {"label": "Alta Demanda", "prob": 0.25, "npv": 108750000.0},
            {"label": "Demanda Moderada", "prob": 0.4375, "npv": 54375000.0},
            {"label": "Baja Demanda", "prob": 0.3125, "npv": 27187500.0},
        ],
    },
    {
        "name": "Jornadas de Educación",
        "decision_key": "jornadas_educacion",
        "horizon_years": 2,
        "outcomes": [
            {"label": "Éxito Académico", "prob": 0.1875, "npv": 62100000.0},
            {"label": "Participación Regular", "prob": 0.3125, "npv": 31050000.0},
            {"label": "Baja Participación", "prob": 0.50, "npv": 20700000.0},
        ],
    },
    {
        "name": "Eventos Especiales",
        "decision_key": "eventos_especiales",
        "horizon_years": 2,
        "outcomes": [
            {"label": "Evento Exitoso", "prob": 0.125, "npv": 89250000.0},
            {"label": "Evento Regular", "prob": 0.1875, "npv": 44250000.0},
            {"label": "Evento Fallido", "prob": 0.6875, "npv": 14250000.0},
        ],
    },
    {
        "name": "Arriendo de Espacios",
        "decision_key": "arriendo_espacios",
        "horizon_years": 4,
        "outcomes": [
            {"label": "Alta Ocupación", "prob": 0.1875, "npv": 33750000.0},
            {"label": "Ocupación Moderada", "prob": 0.3125, "npv": 16875000.0},
            {"label": "Baja Ocupación", "prob": 0.50, "npv": 8437500.0},
        ],
    },

]

# Orden consistente de las decisiones para construir combinaciones (2^10)
decision_order = [a["decision_key"] for a in activities]

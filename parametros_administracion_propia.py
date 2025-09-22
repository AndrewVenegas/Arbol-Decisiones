# -*- coding: utf-8 -*-
"""
Parámetros del análisis de sensibilidad para el parque - ESCENARIO ADMINISTRACIÓN PROPIA.
Edita libremente los valores, probabilidades y horizontes.
Las cifras de 'npv' representan flujos futuros al final del horizonte temporal.
El código descontará automáticamente estos flujos al presente usando la tasa de descuento.
"""

# Tasa de descuento para descontar flujos futuros al presente
discount_rate = 0.06  # 12% anual

# Definición de actividades - ESCENARIO ADMINISTRACIÓN PROPIA
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
            {"label": "Éxito Alto", "prob": 0.10, "npv": 44196428.6},
            {"label": "Éxito Moderado", "prob": 0.30, "npv": 15642857.1},
            {"label": "Fracaso", "prob": 0.60, "npv": 7821428.57},
        ],
    },
    {
        "name": "Cabalgatas",
        "decision_key": "cabalgatas",
        "horizon_years": 3,
        "outcomes": [
            {"label": "Alta Demanda", "prob": 0.30, "npv": -53000000.0},
            {"label": "Demanda Regular", "prob": 0.40, "npv": -89000000.0},
            {"label": "Baja Demanda", "prob": 0.30, "npv": -110600000.0},
        ],
    },
    {
        "name": "Trekking",
        "decision_key": "trekking",
        "horizon_years": 2,
        "outcomes": [
            {"label": "Éxito Alto", "prob": 0.20, "npv": 350000000.0},
            {"label": "Éxito Moderado", "prob": 0.50, "npv": 175000000.0},
            {"label": "Fracaso", "prob": 0.30, "npv": 50000000.0},
        ],
    },
    {
        "name": "Mountain Bike",
        "decision_key": "mtb",
        "horizon_years": 3,
        "outcomes": [
            {"label": "Éxito", "prob": 0.35, "npv": 25000000.0},
            {"label": "Neutro", "prob": 0.25, "npv": 12500000.0},
            {"label": "Fracaso", "prob": 0.40, "npv": 6250000.0},
        ],
    },
    {
        "name": "Kayak",
        "decision_key": "kayak",
        "horizon_years": 2,
        "outcomes": [
            {"label": "Éxito", "prob": 0.25, "npv": 1500000.0},
            {"label": "Neutro", "prob": 0.25, "npv": 750000.0},
            {"label": "Fracaso", "prob": 0.50, "npv": 250000.0},
        ],
    },
    {
        "name": "Tours Guiados",
        "decision_key": "tours_guiados",
        "horizon_years": 3,
        "outcomes": [
            {"label": "Alta Demanda", "prob": 0.25, "npv": 145000000.0},
            {"label": "Demanda Moderada", "prob": 0.45, "npv": 72500000.0},
            {"label": "Baja Demanda", "prob": 0.30, "npv": 36250000.0},
        ],
    },
    {
        "name": "Jornadas de Educación",
        "decision_key": "jornadas_educacion",
        "horizon_years": 2,
        "outcomes": [
            {"label": "Éxito Académico", "prob": 0.40, "npv": 82800000.0},
            {"label": "Participación Regular", "prob": 0.35, "npv": 41400000.0},
            {"label": "Baja Participación", "prob": 0.25, "npv": 27600000.0},
        ],
    },
    {
        "name": "Eventos Especiales",
        "decision_key": "eventos_especiales",
        "horizon_years": 2,
        "outcomes": [
            {"label": "Evento Exitoso", "prob": 0.30, "npv": 119000000.0},
            {"label": "Evento Regular", "prob": 0.40, "npv": 59000000.0},
            {"label": "Evento Fallido", "prob": 0.30, "npv": 19000000.0},
        ],
    },
    {
        "name": "Arriendo de Espacios",
        "decision_key": "arriendo_espacios",
        "horizon_years": 4,
        "outcomes": [
            {"label": "Alta Ocupación", "prob": 0.35, "npv": 45000000.0},
            {"label": "Ocupación Moderada", "prob": 0.45, "npv": 22500000.0},
            {"label": "Baja Ocupación", "prob": 0.20, "npv": 11250000.0},
        ],
    },

]

# Orden consistente de las decisiones para construir combinaciones (2^10)
decision_order = [a["decision_key"] for a in activities]

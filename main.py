
# -*- coding: utf-8 -*-
import itertools
from dataclasses import dataclass
from typing import Dict, List, Tuple
import math
import os

import matplotlib.pyplot as plt
import pandas as pd
import networkx as nx

import parametros as P

@dataclass
class ActivityOutcome:
    label: str
    prob: float
    npv: float

@dataclass
class Activity:
    name: str
    decision_key: str
    horizon_years: int
    outcomes: List[ActivityOutcome]

def load_activities() -> List[Activity]:
    acts = []
    for a in P.activities:
        outcomes = [ActivityOutcome(**o) for o in a['outcomes']]
        acts.append(Activity(a['name'], a['decision_key'], a['horizon_years'], outcomes))
    return acts

def expected_npv(activity: Activity) -> float:
    return sum(o.prob * o.npv for o in activity.outcomes)

def enumerate_combinations(decision_order: List[str]) -> List[Tuple[Tuple[int, ...], Dict[str, int]]]:
    combos = []
    for bits in itertools.product([0,1], repeat=len(decision_order)):
        mapping = dict(zip(decision_order, bits))
        combos.append((bits, mapping))
    return combos

def eval_combo(bits: Tuple[int, ...], activities: List[Activity]) -> float:
    # Suma de VPN esperados por actividad mantenida/invertida
    total = 0.0
    for bit, act in zip(bits, activities):
        if bit == 1:
            total += expected_npv(act)
    return total

def tornado_data(activities: List[Activity]) -> pd.DataFrame:
    rows = []
    for act in activities:
        on_val = expected_npv(act)
        off_val = 0.0
        delta = on_val - off_val
        rows.append({
            'actividad': act.name,
            'impacto_EV_mantener_vs_no': delta
        })
    df = pd.DataFrame(rows).sort_values('impacto_EV_mantener_vs_no', key=abs, ascending=False)
    return df

def build_decision_tree_graph(activities: List[Activity]) -> nx.DiGraph:
    """
    Árbol de decisión simple:
    - Nodo de decisión por actividad (0/1)
    - Si 1 (mantener), nodo de azar con ramas según outcomes con prob.
    - Si 0 (no), pasa directo al siguiente.
    El gráfico mostrará etiquetas con la última decisión tomada y, en ramas de azar,
    la etiqueta del escenario y su probabilidad.
    """
    G = nx.DiGraph()
    root = ('D', 0, 'root')  # (tipo, profundidad, etiqueta)
    G.add_node(root, label='Inicio')
    frontier = [root]
    for depth, act in enumerate(activities, start=1):
        new_frontier = []
        for node in frontier:
            # Decisión: 0 (no mantener)
            d0 = ('D', depth, f"{act.decision_key}=0")
            G.add_edge(node, d0, label='0')
            G.nodes[d0]['label'] = f"{act.name}: NO"
            new_frontier.append(d0)
            # Decisión: 1 (mantener) -> chance node
            d1 = ('D', depth, f"{act.decision_key}=1")
            G.add_edge(node, d1, label='1')
            G.nodes[d1]['label'] = f"{act.name}: SÍ"
            # Chance outcomes
            for i, o in enumerate(act.outcomes):
                cnode = ('C', depth, f"{act.decision_key}_o{i}")
                G.add_edge(d1, cnode, label=f"p={o.prob:.2f}")
                G.nodes[cnode]['label'] = f"{o.label} (p={o.prob:.2f}, VPN={o.npv:,.0f})"
                new_frontier.append(cnode)
        frontier = new_frontier
    return G

def plot_tornado(df: pd.DataFrame, outfile: str):
    plt.figure(figsize=(8, 5))
    y = list(df['actividad'])
    x = list(df['impacto_EV_mantener_vs_no'])
    y_pos = range(len(y))
    plt.barh(y_pos, x)
    plt.yticks(list(y_pos), y)
    plt.xlabel('Impacto en EV (mantener vs no)')
    plt.title('Tornado (impacto marginal por actividad)')
    plt.tight_layout()
    plt.savefig(outfile, dpi=150)
    plt.close()

def plot_tree(G: nx.DiGraph, outfile: str):
    # Layout jerárquico aproximado
    pos = nx.spring_layout(G, k=0.9, iterations=400)
    labels = nx.get_node_attributes(G, 'label')
    edge_labels = nx.get_edge_attributes(G, 'label')

    plt.figure(figsize=(12, 10))
    nx.draw(G, pos, with_labels=False, node_size=800, font_size=8)
    nx.draw_networkx_labels(G, pos, labels, font_size=7)
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=7)
    plt.title('Árbol de decisión con probabilidades (borrador)')
    plt.tight_layout()
    plt.savefig(outfile, dpi=150)
    plt.close()

def plot_top_combinations(df_sorted: pd.DataFrame, outfile: str):
    """Gráfico de las 10 mejores combinaciones por EV total"""
    top_10 = df_sorted.head(10)
    
    plt.figure(figsize=(12, 8))
    y_pos = range(len(top_10))
    
    # Crear etiquetas para cada combinación
    labels = []
    for _, row in top_10.iterrows():
        combo_label = []
        for col in df_sorted.columns[:-1]:  # Excluir EV_total
            if row[col] == 1:
                combo_label.append(col)
        if combo_label:
            labels.append(', '.join(combo_label))
        else:
            labels.append('Ninguna actividad')
    
    bars = plt.barh(y_pos, top_10['EV_total'])
    plt.yticks(y_pos, labels)
    plt.xlabel('EV Total')
    plt.title('Top 10 Mejores Combinaciones por Valor Esperado')
    
    # Agregar valores en las barras
    for i, (bar, value) in enumerate(zip(bars, top_10['EV_total'])):
        plt.text(value + 50, i, f'${value:,.0f}', va='center', fontsize=9)
    
    plt.tight_layout()
    plt.savefig(outfile, dpi=150)
    plt.close()

def plot_worst_combinations(df_sorted: pd.DataFrame, outfile: str):
    """Gráfico de las 10 peores combinaciones por EV total"""
    worst_10 = df_sorted.tail(10)
    
    plt.figure(figsize=(12, 8))
    y_pos = range(len(worst_10))
    
    # Crear etiquetas para cada combinación
    labels = []
    for _, row in worst_10.iterrows():
        combo_label = []
        for col in df_sorted.columns[:-1]:  # Excluir EV_total
            if row[col] == 1:
                combo_label.append(col)
        if combo_label:
            labels.append(', '.join(combo_label))
        else:
            labels.append('Ninguna actividad')
    
    bars = plt.barh(y_pos, worst_10['EV_total'])
    plt.yticks(y_pos, labels)
    plt.xlabel('EV Total')
    plt.title('Top 10 Peores Combinaciones por Valor Esperado')
    
    # Agregar valores en las barras
    for i, (bar, value) in enumerate(zip(bars, worst_10['EV_total'])):
        plt.text(value - 100, i, f'${value:,.0f}', va='center', fontsize=9, ha='right')
    
    plt.tight_layout()
    plt.savefig(outfile, dpi=150)
    plt.close()

def main():
    activities = load_activities()
    decision_order = P.decision_order
    
    # Crear carpeta de resultados si no existe
    resultados_dir = "resultados"
    if not os.path.exists(resultados_dir):
        os.makedirs(resultados_dir)
    
    url_base = resultados_dir
    # 1) EV por actividad
    act_ev = {a.decision_key: expected_npv(a) for a in activities}

    # 2) Enumeración de 2^n combinaciones
    combos = enumerate_combinations(decision_order)
    rows = []
    for bits, mapping in combos:
        total_ev = eval_combo(bits, activities)
        rows.append({
            **mapping,
            'EV_total': total_ev
        })
    df = pd.DataFrame(rows)
    df_sorted = df.sort_values('EV_total', ascending=False).reset_index(drop=True)

    # 3) Tornado (impacto marginal)
    df_tornado = tornado_data(activities)
    plot_tornado(df_tornado, f'{url_base}/tornado.png')

    # 4) Árbol de decisión (borrador con nodos de decisión y azar)
    G = build_decision_tree_graph(activities)
    plot_tree(G, f'{url_base}/arbol_decision.png')  

    # 5) Exportar resultados a CSV
    df_sorted.to_csv(f'{url_base}/combinaciones_ev.csv', index=False)
    df_tornado.to_csv(f'{url_base}/tornado_data.csv', index=False)

    # 6) Gráficos de mejores y peores combinaciones
    plot_top_combinations(df_sorted, f'{url_base}/top_10_combinaciones.png')
    plot_worst_combinations(df_sorted, f'{url_base}/worst_10_combinaciones.png')

    # 6) Imprimir resumen al ejecutar
    print('=== EV por actividad (mantener) ===')
    for a in activities:
        print(f"- {a.name}: EV = {expected_npv(a):,.0f} (horizonte {a.horizon_years} años)")

    print('/n=== Top 10 combinaciones por EV_total ===')
    print(df_sorted.head(10))

    print('\nArchivos generados en la carpeta "resultados":')
    print(f' - {url_base}/combinaciones_ev.csv')
    print(f' - {url_base}/tornado.png')
    print(f' - {url_base}/tornado_data.csv')
    print(f' - {url_base}/arbol_decision.png')
    print(f' - {url_base}/top_10_combinaciones.png')
    print(f' - {url_base}/worst_10_combinaciones.png')

if __name__ == '__main__':
    main()


# -*- coding: utf-8 -*-
import itertools
from dataclasses import dataclass
from typing import Dict, List, Tuple
import math
import os
import time

import matplotlib.pyplot as plt
import pandas as pd
import networkx as nx

import parametros_concesion as P_CONCESION
import parametros_administracion_propia as P_PROPIO

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

# Función load_activities eliminada - ahora se carga directamente en analyze_scenario

def expected_npv(activity: Activity) -> float:
    return sum(o.prob * o.npv for o in activity.outcomes)

def enumerate_combinations(decision_order: List[str]) -> List[Tuple[Tuple[int, ...], Dict[str, int]]]:
    combos = []
    for bits in itertools.product([0,1], repeat=len(decision_order)):
        mapping = dict(zip(decision_order, bits))
        combos.append((bits, mapping))
    return combos

# Función eval_combo eliminada - ya no se usa con la nueva estructura

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

def compare_concession_vs_own(activities_concesion: List[Activity], activities_propio: List[Activity]) -> pd.DataFrame:
    """
    Compara el valor esperado de actividades propias vs concesionadas
    """
    comparison_data = []
    
    # Crear diccionarios para acceso rápido por nombre base
    concesion_dict = {}
    for act in activities_concesion:
        base_name = act.name.replace(' - Concesión', '')
        concesion_dict[base_name] = act
    
    propio_dict = {}
    for act in activities_propio:
        base_name = act.name.replace(' - Propio', '')
        propio_dict[base_name] = act
    
    # Obtener todos los nombres base únicos
    all_base_names = set(concesion_dict.keys()) | set(propio_dict.keys())
    
    for base_name in all_base_names:
        if base_name in concesion_dict and base_name in propio_dict:
            # Tiene ambas versiones
            propio = propio_dict[base_name]
            concesion = concesion_dict[base_name]
            
            ev_propio = expected_npv(propio)
            ev_concesion = expected_npv(concesion)
            diferencia = ev_propio - ev_concesion
            
            comparison_data.append({
                'Actividad': base_name,
                'EV_Propio': ev_propio,
                'EV_Concesion': ev_concesion,
                'Diferencia_EV': diferencia,
                'Mejor_Opcion': 'Propio' if diferencia > 0 else 'Concesión',
                'Ventaja_Propio': max(0, diferencia),
                'Ventaja_Concesion': max(0, -diferencia)
            })
        elif base_name in concesion_dict:
            # Solo tiene versión concesionada
            concesion = concesion_dict[base_name]
            ev_concesion = expected_npv(concesion)
            comparison_data.append({
                'Actividad': base_name,
                'EV_Propio': 0,
                'EV_Concesion': ev_concesion,
                'Diferencia_EV': -ev_concesion,
                'Mejor_Opcion': 'Solo Concesión',
                'Ventaja_Propio': 0,
                'Ventaja_Concesion': ev_concesion
            })
        elif base_name in propio_dict:
            # Solo tiene versión propia
            propio = propio_dict[base_name]
            ev_propio = expected_npv(propio)
            comparison_data.append({
                'Actividad': base_name,
                'EV_Propio': ev_propio,
                'EV_Concesion': 0,
                'Diferencia_EV': ev_propio,
                'Mejor_Opcion': 'Solo Propio',
                'Ventaja_Propio': ev_propio,
                'Ventaja_Concesion': 0
            })
    
    return pd.DataFrame(comparison_data).sort_values('Diferencia_EV', key=abs, ascending=False)

def plot_concession_comparison(df_comparison: pd.DataFrame, outfile: str):
    """Gráfico de comparación entre opciones propias y concesionadas"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
    
    # Gráfico 1: Comparación de EV
    x = range(len(df_comparison))
    width = 0.35
    
    ax1.bar([i - width/2 for i in x], df_comparison['EV_Propio'], width, 
            label='Administración Propia', alpha=0.8)
    ax1.bar([i + width/2 for i in x], df_comparison['EV_Concesion'], width, 
            label='Concesión', alpha=0.8)
    
    ax1.set_xlabel('Actividades')
    ax1.set_ylabel('Valor Esperado (EV)')
    ax1.set_title('Comparación: Administración Propia vs Concesión')
    ax1.set_xticks(x)
    ax1.set_xticklabels(df_comparison['Actividad'], rotation=45, ha='right')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Gráfico 2: Ventaja de cada opción
    ventaja_propio = df_comparison['Ventaja_Propio']
    ventaja_concesion = df_comparison['Ventaja_Concesion']
    
    ax2.barh(x, ventaja_propio, alpha=0.8, label='Ventaja Propia')
    ax2.barh(x, [-v for v in ventaja_concesion], alpha=0.8, label='Ventaja Concesión')
    
    ax2.set_xlabel('Ventaja en EV')
    ax2.set_ylabel('Actividades')
    ax2.set_title('Ventaja de cada Modalidad')
    ax2.set_yticks(x)
    ax2.set_yticklabels(df_comparison['Actividad'])
    ax2.legend()
    ax2.axvline(x=0, color='black', linestyle='-', alpha=0.3)
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(outfile, dpi=150)
    plt.close()

def analyze_main_scenarios(df_sorted: pd.DataFrame) -> pd.DataFrame:
    """
    Analiza los dos escenarios principales: todo concesionado vs todo propio
    """
    # Filtrar combinaciones donde concesionar_todo = 1 (todo concesionado)
    todo_concesionado = df_sorted[df_sorted['concesionar_todo'] == 1]
    
    # Filtrar combinaciones donde concesionar_todo = 0 (todo propio)
    todo_propio = df_sorted[df_sorted['concesionar_todo'] == 0]
    
    # Obtener la mejor combinación de cada escenario
    mejor_concesionado = todo_concesionado.iloc[0] if len(todo_concesionado) > 0 else None
    mejor_propio = todo_propio.iloc[0] if len(todo_propio) > 0 else None
    
    # Crear resumen
    scenarios_data = []
    
    if mejor_concesionado is not None:
        # Contar actividades seleccionadas en concesión
        actividades_concesion = []
        for col in df_sorted.columns:
            if col not in ['concesionar_todo', 'EV_total'] and mejor_concesionado[col] == 1:
                actividades_concesion.append(col)
        
        scenarios_data.append({
            'Escenario': 'Todo Concesionado',
            'EV_Total': mejor_concesionado['EV_total'],
            'Actividades_Seleccionadas': ', '.join(actividades_concesion) if actividades_concesion else 'Ninguna',
            'Num_Actividades': len(actividades_concesion)
        })
    
    if mejor_propio is not None:
        # Contar actividades seleccionadas en administración propia
        actividades_propias = []
        for col in df_sorted.columns:
            if col not in ['concesionar_todo', 'EV_total'] and mejor_propio[col] == 1:
                actividades_propias.append(col)
        
        scenarios_data.append({
            'Escenario': 'Todo Propio',
            'EV_Total': mejor_propio['EV_total'],
            'Actividades_Seleccionadas': ', '.join(actividades_propias) if actividades_propias else 'Ninguna',
            'Num_Actividades': len(actividades_propias)
        })
    
    return pd.DataFrame(scenarios_data)

def plot_main_scenarios(df_scenarios: pd.DataFrame, outfile: str):
    """Gráfico comparativo de los dos escenarios principales"""
    plt.figure(figsize=(12, 6))
    
    # Gráfico de barras
    x = range(len(df_scenarios))
    bars = plt.bar(x, df_scenarios['EV_Total'], alpha=0.8, 
                   color=['#ff7f0e', '#2ca02c'])
    
    plt.xlabel('Escenario')
    plt.ylabel('Valor Esperado Total')
    plt.title('Comparación: Todo Concesionado vs Todo Propio')
    plt.xticks(x, df_scenarios['Escenario'])
    
    # Agregar valores en las barras
    for i, (bar, value) in enumerate(zip(bars, df_scenarios['EV_Total'])):
        plt.text(bar.get_x() + bar.get_width()/2, value + 1000, 
                f'${value:,.0f}', ha='center', va='bottom', fontsize=10)
    
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(outfile, dpi=150)
    plt.close()

def analyze_scenario(parametros, scenario_name: str, resultados_base: str):
    """
    Analiza un escenario específico usando los parámetros correspondientes
    """
    print(f"\n🔍 Analizando escenario: {scenario_name}")
    
    # Cargar actividades desde los parámetros
    activities = []
    for a in parametros.activities:
        outcomes = [ActivityOutcome(**o) for o in a['outcomes']]
        activities.append(Activity(a['name'], a['decision_key'], a['horizon_years'], outcomes))
    
    decision_keys = parametros.decision_order
    
    print(f"   📊 Actividades en este escenario: {len(activities)}")
    
    # Crear carpeta específica para este escenario
    scenario_dir = f"{resultados_base}-{scenario_name.lower().replace(' ', '-')}"
    if not os.path.exists(scenario_dir):
        os.makedirs(scenario_dir)
        print(f"   📁 Carpeta creada: {scenario_dir}")
    
    # 1) EV por actividad
    print("   💰 Calculando valor esperado por actividad...")
    act_ev = {a.decision_key: expected_npv(a) for a in activities}
    print(f"   ✅ EV calculado para {len(act_ev)} actividades")
    
    # 2) Enumeración de combinaciones
    print("   🔢 Generando combinaciones de decisiones...")
    combos = enumerate_combinations(decision_keys)
    total_combos = len(combos)
    print(f"   📈 Total de combinaciones: {total_combos:,} (2^{len(decision_keys)})")
    
    print("   ⚡ Evaluando combinaciones...")
    rows = []
    for i, (bits, mapping) in enumerate(combos):
        if (i + 1) % 200 == 0 or i == 0:
            print(f"   📊 Procesando combinación {i+1:,}/{total_combos:,} ({(i+1)/total_combos*100:.1f}%)")
        
        total_ev = sum(expected_npv(act) for bit, act in zip(bits, activities) if bit == 1)
        rows.append({
            **mapping,
            'EV_total': total_ev
        })
    
    print("   📋 Organizando resultados...")
    df = pd.DataFrame(rows)
    df_sorted = df.sort_values('EV_total', ascending=False).reset_index(drop=True)
    print(f"   ✅ {len(df_sorted)} combinaciones evaluadas y ordenadas")

    # 3) Tornado (impacto marginal)
    print("   🌪️ Generando análisis tornado...")
    df_tornado = tornado_data(activities)
    plot_tornado(df_tornado, f'{scenario_dir}/tornado.png')
    print(f"   ✅ Gráfico tornado guardado: {scenario_dir}/tornado.png")

    # 4) Árbol de decisión
    print("   🌳 Construyendo árbol de decisión...")
    G = build_decision_tree_graph(activities)
    print(f"   📊 Nodos en el árbol: {G.number_of_nodes()}")
    print(f"   🔗 Conexiones en el árbol: {G.number_of_edges()}")
    plot_tree(G, f'{scenario_dir}/arbol_decision.png')
    print(f"   ✅ Árbol de decisión guardado: {scenario_dir}/arbol_decision.png")

    # 5) Exportar resultados a CSV
    print("   💾 Exportando datos a CSV...")
    df_sorted.to_csv(f'{scenario_dir}/combinaciones_ev.csv', index=False)
    df_tornado.to_csv(f'{scenario_dir}/tornado_data.csv', index=False)
    print(f"   ✅ Archivos CSV exportados")

    # 6) Gráficos de mejores y peores combinaciones
    print("   📊 Generando gráficos de combinaciones...")
    plot_top_combinations(df_sorted, f'{scenario_dir}/top_10_combinaciones.png')
    plot_worst_combinations(df_sorted, f'{scenario_dir}/worst_10_combinaciones.png')
    print(f"   ✅ Gráficos de combinaciones guardados")
    
    return df_sorted, df_tornado, activities

def main():
    print("🚀 Iniciando análisis de árbol de decisiones...")
    start_time = time.time()
    
    # Crear carpeta base de resultados
    print("📁 Preparando carpetas de resultados...")
    resultados_base = "resultados"
    if not os.path.exists(resultados_base):
        os.makedirs(resultados_base)
        print(f"   ✅ Carpeta base '{resultados_base}' creada")
    else:
        print(f"   ✅ Carpeta base '{resultados_base}' ya existe")
    
    # Analizar escenario de CONCESIÓN
    df_concesion, df_tornado_concesion, activities_concesion = analyze_scenario(
        P_CONCESION, "Concesion", resultados_base
    )
    
    # Analizar escenario de ADMINISTRACIÓN PROPIA
    df_propio, df_tornado_propio, activities_propio = analyze_scenario(
        P_PROPIO, "Administracion-Propia", resultados_base
    )
    
    # Análisis comparativo entre ambos escenarios
    print("\n⚖️ Generando análisis comparativo...")
    df_comparison = compare_concession_vs_own(activities_concesion, activities_propio)
    plot_concession_comparison(df_comparison, f'{resultados_base}/comparacion_concesion_vs_propio.png')
    df_comparison.to_csv(f'{resultados_base}/comparacion_concesion_vs_propio.csv', index=False)
    print(f"   ✅ Análisis comparativo guardado en {resultados_base}/")
    
    # Crear resumen de escenarios principales
    print("🎯 Generando resumen de escenarios principales...")
    scenarios_data = []
    
    # Mejor combinación de concesión
    mejor_concesion = df_concesion.iloc[0] if len(df_concesion) > 0 else None
    if mejor_concesion is not None:
        actividades_concesion = [col for col in df_concesion.columns if col != 'EV_total' and mejor_concesion[col] == 1]
        scenarios_data.append({
            'Escenario': 'Todo Concesionado',
            'EV_Total': mejor_concesion['EV_total'],
            'Actividades_Seleccionadas': ', '.join(actividades_concesion) if actividades_concesion else 'Ninguna',
            'Num_Actividades': len(actividades_concesion)
        })
    
    # Mejor combinación de administración propia
    mejor_propio = df_propio.iloc[0] if len(df_propio) > 0 else None
    if mejor_propio is not None:
        actividades_propias = [col for col in df_propio.columns if col != 'EV_total' and mejor_propio[col] == 1]
        scenarios_data.append({
            'Escenario': 'Todo Propio',
            'EV_Total': mejor_propio['EV_total'],
            'Actividades_Seleccionadas': ', '.join(actividades_propias) if actividades_propias else 'Ninguna',
            'Num_Actividades': len(actividades_propias)
        })
    
    df_scenarios = pd.DataFrame(scenarios_data)
    plot_main_scenarios(df_scenarios, f'{resultados_base}/escenarios_principales.png')
    df_scenarios.to_csv(f'{resultados_base}/escenarios_principales.csv', index=False)
    print(f"   ✅ Resumen de escenarios guardado en {resultados_base}/")

    # Imprimir resumen de resultados
    print('\n' + '='*60)
    print('📊 RESUMEN DE RESULTADOS')
    print('='*60)
    
    print('\n=== EV por actividad - CONCESIÓN ===')
    for a in activities_concesion:
        print(f"- {a.name}: EV = {expected_npv(a):,.0f} (horizonte {a.horizon_years} años)")
    
    print('\n=== EV por actividad - ADMINISTRACIÓN PROPIA ===')
    for a in activities_propio:
        print(f"- {a.name}: EV = {expected_npv(a):,.0f} (horizonte {a.horizon_years} años)")

    print('\n=== Top 5 combinaciones - CONCESIÓN ===')
    print(df_concesion.head(5)[['EV_total'] + [col for col in df_concesion.columns if col != 'EV_total']].to_string(index=False))

    print('\n=== Top 5 combinaciones - ADMINISTRACIÓN PROPIA ===')
    print(df_propio.head(5)[['EV_total'] + [col for col in df_propio.columns if col != 'EV_total']].to_string(index=False))

    print('\n=== Comparación: Concesión vs Administración Propia ===')
    print(df_comparison[['Actividad', 'EV_Propio', 'EV_Concesion', 'Diferencia_EV', 'Mejor_Opcion']].to_string(index=False))

    print('\n=== Escenarios Principales: Todo Concesionado vs Todo Propio ===')
    print(df_scenarios[['Escenario', 'EV_Total', 'Num_Actividades', 'Actividades_Seleccionadas']].to_string(index=False))

    # Resumen final
    end_time = time.time()
    total_time = end_time - start_time
    
    print(f"\n🎉 ¡Análisis completado exitosamente!")
    print(f"⏱️  Tiempo total: {total_time:.1f} segundos")
    print(f"📊 Combinaciones concesión: {len(df_concesion):,}")
    print(f"📊 Combinaciones administración propia: {len(df_propio):,}")
    print(f"📁 Archivos generados: 12")
    
    print('\n📋 Archivos generados:')
    print(f'\n📁 Carpeta "resultados-concesion":')
    print(f' - combinaciones_ev.csv')
    print(f' - tornado.png')
    print(f' - tornado_data.csv')
    print(f' - arbol_decision.png')
    print(f' - top_10_combinaciones.png')
    print(f' - worst_10_combinaciones.png')
    
    print(f'\n📁 Carpeta "resultados-administracion-propia":')
    print(f' - combinaciones_ev.csv')
    print(f' - tornado.png')
    print(f' - tornado_data.csv')
    print(f' - arbol_decision.png')
    print(f' - top_10_combinaciones.png')
    print(f' - worst_10_combinaciones.png')
    
    print(f'\n📁 Carpeta "resultados" (análisis comparativo):')
    print(f' - comparacion_concesion_vs_propio.png')
    print(f' - comparacion_concesion_vs_propio.csv')
    print(f' - escenarios_principales.png')
    print(f' - escenarios_principales.csv')

if __name__ == '__main__':
    main()

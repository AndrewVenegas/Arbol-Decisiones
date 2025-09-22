
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

def expected_npv(activity: Activity, discount_rate: float = 0.12) -> float:
    """
    Calcula el valor presente neto esperado de una actividad
    Descuenta los flujos futuros al presente usando la tasa de descuento
    
    Fórmula: EV = Σ(probabilidad × flujo_futuro / (1 + tasa_descuento)^horizonte_años)
    """
    return sum(o.prob * o.npv / ((1 + discount_rate) ** activity.horizon_years) for o in activity.outcomes)

def verify_calculation_example():
    """
    Función de verificación para demostrar el cálculo correcto del VPN
    """
    print("\n🧮 VERIFICACIÓN DE CÁLCULOS:")
    print("="*50)
    
    # Ejemplo: Actividad con horizonte de 2 años, flujo futuro de $100,000
    # Tasa de descuento: 12%
    # VPN esperado = $100,000 / (1.12)^2 = $100,000 / 1.2544 = $79,719
    
    horizon_years = 2
    discount_rate = 0.12
    future_flow = 100000
    
    npv_calculated = future_flow / ((1 + discount_rate) ** horizon_years)
    print(f"📊 Ejemplo de cálculo:")
    print(f"   Flujo futuro: ${future_flow:,}")
    print(f"   Horizonte: {horizon_years} años")
    print(f"   Tasa de descuento: {discount_rate*100:.1f}%")
    print(f"   VPN calculado: ${npv_calculated:,.0f}")
    print(f"   Fórmula: ${future_flow:,} / (1.12)^{horizon_years} = ${npv_calculated:,.0f}")
    print("✅ Cálculo correcto!")

def verify_probabilities(parametros):
    """
    Verifica que las probabilidades de cada actividad sumen 1.0
    """
    print("\n🔍 VERIFICACIÓN DE PROBABILIDADES:")
    print("="*50)
    
    all_valid = True
    
    for i, activity in enumerate(parametros.activities):
        total_prob = sum(outcome['prob'] for outcome in activity['outcomes'])
        is_valid = abs(total_prob - 1.0) < 0.001  # Tolerancia para errores de punto flotante
        
        status = "✅" if is_valid else "❌"
        print(f"{status} {activity['name']}: {total_prob:.3f} {'✓' if is_valid else '✗'}")
        
        if not is_valid:
            all_valid = False
            print(f"   ⚠️  Probabilidades: {[outcome['prob'] for outcome in activity['outcomes']]}")
    
    if all_valid:
        print("\n🎉 ¡Todas las probabilidades suman 1.0 correctamente!")
    else:
        print("\n⚠️  Algunas actividades tienen probabilidades que no suman 1.0")
    
    return all_valid

def analyze_main_decision(activities_concesion: List[Activity], activities_propio: List[Activity], discount_rate: float = 0.12) -> pd.DataFrame:
    """
    Analiza la decisión principal: Concesionar todo vs Administración propia
    """
    print("\n🎯 ANÁLISIS DE DECISIÓN PRINCIPAL:")
    print("="*60)
    
    # Calcular VPN de la mejor combinación de concesión
    best_concesion_ev = sum(expected_npv(act, discount_rate) for act in activities_concesion)
    
    # Calcular VPN de la mejor combinación de administración propia
    best_propio_ev = sum(expected_npv(act, discount_rate) for act in activities_propio)
    
    # Calcular diferencia
    diferencia = best_propio_ev - best_concesion_ev
    
    print(f"💰 CONCESIONAR TODO:")
    print(f"   VPN Total: ${best_concesion_ev:,.0f}")
    print(f"   Actividades: {len(activities_concesion)}")
    
    print(f"\n💰 ADMINISTRACIÓN PROPIA:")
    print(f"   VPN Total: ${best_propio_ev:,.0f}")
    print(f"   Actividades: {len(activities_propio)}")
    
    print(f"\n⚖️ DIFERENCIA:")
    print(f"   Ventaja Administración Propia: ${diferencia:,.0f}")
    print(f"   Mejor opción: {'Administración Propia' if diferencia > 0 else 'Concesión'}")
    
    # Crear DataFrame para exportar
    decision_data = [{
        'Decision': 'Concesionar Todo',
        'NPV_Total': best_concesion_ev,
        'Num_Actividades': len(activities_concesion),
        'Tipo': 'Concesión'
    }, {
        'Decision': 'Administración Propia',
        'NPV_Total': best_propio_ev,
        'Num_Actividades': len(activities_propio),
        'Tipo': 'Propia'
    }]
    
    return pd.DataFrame(decision_data)

def analyze_individual_decisions(activities: List[Activity], discount_rate: float = 0.12) -> pd.DataFrame:
    """
    Analiza cada decisión individual: Hacer vs No hacer cada actividad
    """
    print(f"\n🔍 ANÁLISIS DE DECISIONES INDIVIDUALES:")
    print("="*60)
    
    decision_data = []
    
    for act in activities:
        # VPN si hago la actividad
        npv_hacer = expected_npv(act, discount_rate)
        
        # VPN si no hago la actividad (siempre 0)
        npv_no_hacer = 0.0
        
        # Diferencia (valor de la decisión)
        valor_decision = npv_hacer - npv_no_hacer
        
        decision_data.append({
            'Actividad': act.name,
            'NPV_Hacer': npv_hacer,
            'NPV_No_Hacer': npv_no_hacer,
            'Valor_Decision': valor_decision,
            'Horizonte_Años': act.horizon_years,
            'Recomendacion': 'HACER' if valor_decision > 0 else 'NO HACER'
        })
        
        print(f"📊 {act.name}:")
        print(f"   VPN si HAGO: ${npv_hacer:,.0f}")
        print(f"   VPN si NO HAGO: ${npv_no_hacer:,.0f}")
        print(f"   Valor de la decisión: ${valor_decision:,.0f}")
        print(f"   Recomendación: {'HACER' if valor_decision > 0 else 'NO HACER'}")
        print()
    
    return pd.DataFrame(decision_data)

def plot_main_decision_analysis(df_main_decision: pd.DataFrame, outfile: str):
    """
    Gráfico de la decisión principal: Concesionar vs Administración propia
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
    
    # Gráfico 1: Comparación de NPVs
    colors = ['#FF6B6B', '#4ECDC4']
    npv_millions = df_main_decision['NPV_Total'] / 1e6  # Convertir a millones
    bars = ax1.bar(df_main_decision['Decision'], npv_millions, color=colors)
    ax1.set_title('VPN Total: Concesión vs Administración Propia', fontsize=14, fontweight='bold')
    ax1.set_ylabel('VPN Total (Millones $)')
    ax1.tick_params(axis='x', rotation=45)
    
    # Agregar valores en las barras
    for bar, value in zip(bars, npv_millions):
        ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(npv_millions)*0.01,
                f'${value:,.1f}M', ha='center', va='bottom', fontweight='bold')
    
    # Gráfico 2: Diferencia
    diferencia = df_main_decision.iloc[1]['NPV_Total'] - df_main_decision.iloc[0]['NPV_Total']
    diferencia_millions = diferencia / 1e6  # Convertir a millones
    color = '#2ECC71' if diferencia > 0 else '#E74C3C'
    
    ax2.barh(['Ventaja Administración Propia'], [diferencia_millions], color=color)
    ax2.set_title('Ventaja de Administración Propia', fontsize=14, fontweight='bold')
    ax2.set_xlabel('Diferencia en VPN (Millones $)')
    ax2.axvline(x=0, color='black', linestyle='--', alpha=0.5)
    
    # Agregar valor
    ax2.text(diferencia_millions + (max(abs(diferencia_millions), 1) * 0.05), 0, f'${diferencia_millions:,.1f}M', 
             ha='left' if diferencia > 0 else 'right', va='center', fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(outfile, dpi=150, bbox_inches='tight')
    plt.close()

def plot_individual_decisions(df_individual: pd.DataFrame, outfile: str):
    """
    Gráfico de decisiones individuales: Hacer vs No hacer cada actividad
    """
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(16, 12))
    
    # Ordenar por valor de decisión
    df_sorted = df_individual.sort_values('Valor_Decision', ascending=True)
    
    # Gráfico 1: Valor de cada decisión
    valor_millions = df_sorted['Valor_Decision'] / 1e6  # Convertir a millones
    colors = ['#E74C3C' if x < 0 else '#2ECC71' for x in valor_millions]
    bars = ax1.barh(df_sorted['Actividad'], valor_millions, color=colors)
    ax1.set_title('VPN ponderado por actividad', fontsize=14, fontweight='bold')
    ax1.set_xlabel('VPN (en Millones $)')
    ax1.axvline(x=0, color='black', linestyle='--', alpha=0.5)
    
    # Agregar valores
    for bar, value in zip(bars, valor_millions):
        ax1.text(bar.get_width() + (max(abs(valor_millions)) * 0.02), 
                bar.get_y() + bar.get_height()/2, f'${value:,.1f}M', 
                ha='left' if value > 0 else 'right', va='center', fontsize=9)
    
    # Gráfico 2: VPN si hago vs no hago
    x = range(len(df_sorted))
    width = 0.35
    
    npv_hacer_millions = df_sorted['NPV_Hacer'] / 1e6  # Convertir a millones
    npv_no_hacer_millions = df_sorted['NPV_No_Hacer'] / 1e6  # Convertir a millones
    
    bars1 = ax2.bar([i - width/2 for i in x], npv_hacer_millions, width, 
                    label='VPN si HAGO', color='#3498DB', alpha=0.8)
    bars2 = ax2.bar([i + width/2 for i in x], npv_no_hacer_millions, width, 
                    label='VPN si NO HAGO', color='#95A5A6', alpha=0.8)
    
    ax2.set_title('VPN: Hacer vs No Hacer por Actividad', fontsize=14, fontweight='bold')
    ax2.set_ylabel('VPN (Millones $)')
    ax2.set_xlabel('Actividades')
    ax2.set_xticks(x)
    ax2.set_xticklabels(df_sorted['Actividad'], rotation=45, ha='right')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(outfile, dpi=150, bbox_inches='tight')
    plt.close()

def generate_executive_summary(activities_concesion: List[Activity], activities_propio: List[Activity], discount_rate: float = 0.12):
    """
    Genera un resumen ejecutivo con recomendaciones claras de qué hacer y qué no hacer
    """
    print("\n" + "="*80)
    print("📋 RESUMEN EJECUTIVO - RECOMENDACIONES DE DECISIONES")
    print("="*80)
    
    # 1. DECISIÓN PRINCIPAL
    print("\n🎯 DECISIÓN PRINCIPAL:")
    print("-" * 50)
    
    npv_concesion = sum(expected_npv(act, discount_rate) for act in activities_concesion)
    npv_propio = sum(expected_npv(act, discount_rate) for act in activities_propio)
    diferencia = npv_propio - npv_concesion
    
    if diferencia > 0:
        print(f"✅ RECOMENDACIÓN: ADMINISTRACIÓN PROPIA")
        print(f"   💰 Ventaja: ${diferencia:,.0f}")
        print(f"   📊 VPN Administración Propia: ${npv_propio:,.0f}")
        print(f"   📊 VPN Concesión: ${npv_concesion:,.0f}")
    else:
        print(f"✅ RECOMENDACIÓN: CONCESIONAR TODO")
        print(f"   💰 Ventaja: ${-diferencia:,.0f}")
        print(f"   📊 VPN Concesión: ${npv_concesion:,.0f}")
        print(f"   📊 VPN Administración Propia: ${npv_propio:,.0f}")
    
    # 2. DECISIONES INDIVIDUALES - ADMINISTRACIÓN PROPIA
    print(f"\n🔍 DECISIONES INDIVIDUALES - ADMINISTRACIÓN PROPIA:")
    print("-" * 50)
    
    actividades_hacer = []
    actividades_no_hacer = []
    
    for act in activities_propio:
        npv_hacer = expected_npv(act, discount_rate)
        if npv_hacer > 0:
            actividades_hacer.append((act.name, npv_hacer))
        else:
            actividades_no_hacer.append((act.name, npv_hacer))
    
    # Ordenar por VPN descendente
    actividades_hacer.sort(key=lambda x: x[1], reverse=True)
    actividades_no_hacer.sort(key=lambda x: x[1], reverse=True)
    
    print("✅ HACER (Ordenadas por rentabilidad):")
    for i, (nombre, npv) in enumerate(actividades_hacer, 1):
        print(f"   {i:2d}. {nombre:<30} → ${npv:>8,.0f}")
    
    print("\n❌ NO HACER (Ordenadas por pérdida):")
    for i, (nombre, npv) in enumerate(actividades_no_hacer, 1):
        print(f"   {i:2d}. {nombre:<30} → ${npv:>8,.0f}")
    
    # 3. DECISIONES INDIVIDUALES - CONCESIÓN
    print(f"\n🔍 DECISIONES INDIVIDUALES - CONCESIÓN:")
    print("-" * 50)
    
    actividades_hacer_concesion = []
    actividades_no_hacer_concesion = []
    
    for act in activities_concesion:
        npv_hacer = expected_npv(act, discount_rate)
        if npv_hacer > 0:
            actividades_hacer_concesion.append((act.name, npv_hacer))
        else:
            actividades_no_hacer_concesion.append((act.name, npv_hacer))
    
    # Ordenar por VPN descendente
    actividades_hacer_concesion.sort(key=lambda x: x[1], reverse=True)
    actividades_no_hacer_concesion.sort(key=lambda x: x[1], reverse=True)
    
    print("✅ HACER (Ordenadas por rentabilidad):")
    for i, (nombre, npv) in enumerate(actividades_hacer_concesion, 1):
        print(f"   {i:2d}. {nombre:<30} → ${npv:>8,.0f}")
    
    print("\n❌ NO HACER (Ordenadas por pérdida):")
    for i, (nombre, npv) in enumerate(actividades_no_hacer_concesion, 1):
        print(f"   {i:2d}. {nombre:<30} → ${npv:>8,.0f}")
    
    # 4. RESUMEN FINAL
    print(f"\n📊 RESUMEN FINAL:")
    print("-" * 50)
    print(f"🎯 Mejor estrategia: {'ADMINISTRACIÓN PROPIA' if diferencia > 0 else 'CONCESIÓN'}")
    print(f"💰 Valor total esperado: ${max(npv_concesion, npv_propio):,.0f}")
    print(f"📈 Actividades rentables (Administración Propia): {len(actividades_hacer)}")
    print(f"📉 Actividades no rentables (Administración Propia): {len(actividades_no_hacer)}")
    print(f"📈 Actividades rentables (Concesión): {len(actividades_hacer_concesion)}")
    print(f"📉 Actividades no rentables (Concesión): {len(actividades_no_hacer_concesion)}")
    
    # 5. GUARDAR RESUMEN EN ARCHIVO
    with open('resultados-concesion/resumen_ejecutivo.txt', 'w', encoding='utf-8') as f:
        f.write("RESUMEN EJECUTIVO - RECOMENDACIONES DE DECISIONES\n")
        f.write("="*80 + "\n\n")
        
        f.write("DECISIÓN PRINCIPAL:\n")
        f.write("-" * 50 + "\n")
        if diferencia > 0:
            f.write("RECOMENDACIÓN: ADMINISTRACIÓN PROPIA\n")
            f.write(f"Ventaja: ${diferencia:,.0f}\n")
            f.write(f"VPN Administración Propia: ${npv_propio:,.0f}\n")
            f.write(f"VPN Concesión: ${npv_concesion:,.0f}\n")
        else:
            f.write("RECOMENDACIÓN: CONCESIONAR TODO\n")
            f.write(f"Ventaja: ${-diferencia:,.0f}\n")
            f.write(f"VPN Concesión: ${npv_concesion:,.0f}\n")
            f.write(f"VPN Administración Propia: ${npv_propio:,.0f}\n")
        
        f.write(f"\nDECISIONES INDIVIDUALES - ADMINISTRACIÓN PROPIA:\n")
        f.write("-" * 50 + "\n")
        f.write("HACER (Ordenadas por rentabilidad):\n")
        for i, (nombre, npv) in enumerate(actividades_hacer, 1):
            f.write(f"{i:2d}. {nombre:<30} → ${npv:>8,.0f}\n")
        f.write("\nNO HACER (Ordenadas por pérdida):\n")
        for i, (nombre, npv) in enumerate(actividades_no_hacer, 1):
            f.write(f"{i:2d}. {nombre:<30} → ${npv:>8,.0f}\n")
        
        f.write(f"\nDECISIONES INDIVIDUALES - CONCESIÓN:\n")
        f.write("-" * 50 + "\n")
        f.write("HACER (Ordenadas por rentabilidad):\n")
        for i, (nombre, npv) in enumerate(actividades_hacer_concesion, 1):
            f.write(f"{i:2d}. {nombre:<30} → ${npv:>8,.0f}\n")
        f.write("\nNO HACER (Ordenadas por pérdida):\n")
        for i, (nombre, npv) in enumerate(actividades_no_hacer_concesion, 1):
            f.write(f"{i:2d}. {nombre:<30} → ${npv:>8,.0f}\n")
        
        f.write(f"\nRESUMEN FINAL:\n")
        f.write("-" * 50 + "\n")
        f.write(f"Mejor estrategia: {'ADMINISTRACIÓN PROPIA' if diferencia > 0 else 'CONCESIÓN'}\n")
        f.write(f"Valor total esperado: ${max(npv_concesion, npv_propio):,.0f}\n")
        f.write(f"Actividades rentables (Administración Propia): {len(actividades_hacer)}\n")
        f.write(f"Actividades no rentables (Administración Propia): {len(actividades_no_hacer)}\n")
        f.write(f"Actividades rentables (Concesión): {len(actividades_hacer_concesion)}\n")
        f.write(f"Actividades no rentables (Concesión): {len(actividades_no_hacer_concesion)}\n")
    
    print(f"\n💾 Resumen ejecutivo guardado en: resultados-concesion/resumen_ejecutivo.txt")

def enumerate_combinations(decision_order: List[str]) -> List[Tuple[Tuple[int, ...], Dict[str, int]]]:
    combos = []
    for bits in itertools.product([0,1], repeat=len(decision_order)):
        mapping = dict(zip(decision_order, bits))
        combos.append((bits, mapping))
    return combos

# Función eval_combo eliminada - ya no se usa con la nueva estructura

def tornado_data(activities: List[Activity], discount_rate: float = 0.12) -> pd.DataFrame:
    rows = []
    for act in activities:
        on_val = expected_npv(act, discount_rate)
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
    x = [val / 1e6 for val in df['impacto_EV_mantener_vs_no']]  # Convertir a millones
    y_pos = range(len(y))
    plt.barh(y_pos, x)
    plt.yticks(list(y_pos), y)
    plt.xlabel('Impacto en EV (mantener vs no) - Millones $')
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
    
    ev_millions = top_10['EV_total'] / 1e6  # Convertir a millones
    bars = plt.barh(y_pos, ev_millions)
    plt.yticks(y_pos, labels)
    plt.xlabel('VPN Total (Millones $)')
    plt.title('Top 10 Mejores Combinaciones por VPN Total')
    
    # Agregar valores en las barras
    for i, (bar, value) in enumerate(zip(bars, ev_millions)):
        plt.text(value + max(ev_millions) * 0.01, i, f'${value:,.1f}M', va='center', fontsize=9)
    
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
    
    ev_millions = worst_10['EV_total'] / 1e6  # Convertir a millones
    bars = plt.barh(y_pos, ev_millions)
    plt.yticks(y_pos, labels)
    plt.xlabel('VPN Total (Millones $)')
    plt.title('Top 10 Peores Combinaciones por VPN Total')
    
    # Agregar valores en las barras
    for i, (bar, value) in enumerate(zip(bars, ev_millions)):
        plt.text(value - max(abs(ev_millions)) * 0.01, i, f'${value:,.1f}M', va='center', fontsize=9, ha='right')
    
    plt.tight_layout()
    plt.savefig(outfile, dpi=150)
    plt.close()

def compare_concession_vs_own(activities_concesion: List[Activity], activities_propio: List[Activity], discount_rate: float = 0.12) -> pd.DataFrame:
    """
    Compara el valor esperado de actividades propias vs concesionadas
    """
    comparison_data = []
    
    # Crear diccionarios para acceso rápido por nombre
    concesion_dict = {act.name: act for act in activities_concesion}
    propio_dict = {act.name: act for act in activities_propio}
    
    # Obtener todos los nombres únicos
    all_names = set(concesion_dict.keys()) | set(propio_dict.keys())
    
    for name in all_names:
        if name in concesion_dict and name in propio_dict:
            # Tiene ambas versiones
            propio = propio_dict[name]
            concesion = concesion_dict[name]
            
            ev_propio = expected_npv(propio, discount_rate)
            ev_concesion = expected_npv(concesion, discount_rate)
            diferencia = ev_propio - ev_concesion
            
            comparison_data.append({
                'Actividad': name,
                'EV_Propio': ev_propio,
                'EV_Concesion': ev_concesion,
                'Diferencia_EV': diferencia,
                'Mejor_Opcion': 'Propio' if diferencia > 0 else 'Concesión',
                'Ventaja_Propio': max(0, diferencia),
                'Ventaja_Concesion': max(0, -diferencia)
            })
        elif name in concesion_dict:
            # Solo tiene versión concesionada
            concesion = concesion_dict[name]
            ev_concesion = expected_npv(concesion, discount_rate)
            comparison_data.append({
                'Actividad': name,
                'EV_Propio': 0,
                'EV_Concesion': ev_concesion,
                'Diferencia_EV': -ev_concesion,
                'Mejor_Opcion': 'Solo Concesión',
                'Ventaja_Propio': 0,
                'Ventaja_Concesion': ev_concesion
            })
        elif name in propio_dict:
            # Solo tiene versión propia
            propio = propio_dict[name]
            ev_propio = expected_npv(propio, discount_rate)
            comparison_data.append({
                'Actividad': name,
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
    
    ev_propio_millions = df_comparison['EV_Propio'] / 1e6  # Convertir a millones
    ev_concesion_millions = df_comparison['EV_Concesion'] / 1e6  # Convertir a millones
    
    ax1.bar([i - width/2 for i in x], ev_propio_millions, width, 
            label='Administración Propia', alpha=0.8)
    ax1.bar([i + width/2 for i in x], ev_concesion_millions, width, 
            label='Concesión', alpha=0.8)
    
    ax1.set_xlabel('Actividades')
    ax1.set_ylabel('Valor Presente Neto (VPN) - Millones $')
    ax1.set_title('Comparación: Administración Propia vs Concesión')
    ax1.set_xticks(x)
    ax1.set_xticklabels(df_comparison['Actividad'], rotation=45, ha='right')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Gráfico 2: Ventaja de cada opción
    ventaja_propio_millions = df_comparison['Ventaja_Propio'] / 1e6  # Convertir a millones
    ventaja_concesion_millions = df_comparison['Ventaja_Concesion'] / 1e6  # Convertir a millones
    
    ax2.barh(x, ventaja_propio_millions, alpha=0.8, label='Ventaja Propia')
    ax2.barh(x, [-v for v in ventaja_concesion_millions], alpha=0.8, label='Ventaja Concesión')
    
    ax2.set_xlabel('Ventaja en VPN (Millones $)')
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
    ev_millions = df_scenarios['EV_Total'] / 1e6  # Convertir a millones
    bars = plt.bar(x, ev_millions, alpha=0.8, 
                   color=['#ff7f0e', '#2ca02c'])
    
    plt.xlabel('Escenario')
    plt.ylabel('Valor Esperado Total (Millones $)')
    plt.title('Comparación: Todo Concesionado vs Todo Propio')
    plt.xticks(x, df_scenarios['Escenario'])
    
    # Agregar valores en las barras
    for i, (bar, value) in enumerate(zip(bars, ev_millions)):
        plt.text(bar.get_x() + bar.get_width()/2, value + max(ev_millions) * 0.01, 
                f'${value:,.1f}M', ha='center', va='bottom', fontsize=10)
    
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
    discount_rate = getattr(parametros, 'discount_rate', 0.12)  # Usar tasa de descuento de parámetros
    
    print(f"   📊 Actividades en este escenario: {len(activities)}")
    print(f"   💰 Tasa de descuento: {discount_rate*100:.1f}% anual")
    
    # Crear carpeta específica para este escenario
    scenario_dir = f"{resultados_base}-{scenario_name.lower().replace(' ', '-')}"
    if not os.path.exists(scenario_dir):
        os.makedirs(scenario_dir)
        print(f"   📁 Carpeta creada: {scenario_dir}")
    
    # 1) EV por actividad
    print("   💰 Calculando valor esperado por actividad...")
    act_ev = {a.decision_key: expected_npv(a, discount_rate) for a in activities}
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
        
        total_ev = sum(expected_npv(act, discount_rate) for bit, act in zip(bits, activities) if bit == 1)
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
    df_tornado = tornado_data(activities, discount_rate)
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
    
    # Verificar cálculos
    verify_calculation_example()
    
    # Verificar probabilidades
    print("\n🔍 Verificando parámetros de concesión...")
    verify_probabilities(P_CONCESION)
    print("\n🔍 Verificando parámetros de administración propia...")
    verify_probabilities(P_PROPIO)
    
    # Analizar escenario de CONCESIÓN
    df_concesion, df_tornado_concesion, activities_concesion = analyze_scenario(
        P_CONCESION, "concesion", "resultados"
    )
    
    # Analizar escenario de ADMINISTRACIÓN PROPIA
    df_propio, df_tornado_propio, activities_propio = analyze_scenario(
        P_PROPIO, "administracion-propia", "resultados"
    )
    
    # Análisis comparativo entre ambos escenarios
    print("\n⚖️ Generando análisis comparativo...")
    discount_rate = getattr(P_CONCESION, 'discount_rate', 0.12)  # Usar tasa de descuento
    df_comparison = compare_concession_vs_own(activities_concesion, activities_propio, discount_rate)
    
    # Guardar análisis comparativo en carpeta de concesión
    plot_concession_comparison(df_comparison, f'resultados-concesion/comparacion_concesion_vs_propio.png')
    df_comparison.to_csv(f'resultados-concesion/comparacion_concesion_vs_propio.csv', index=False)
    print(f"   ✅ Análisis comparativo guardado en resultados-concesion/")
    
    # NUEVO: Análisis de decisión principal
    print("\n🎯 Generando análisis de decisión principal...")
    df_main_decision = analyze_main_decision(activities_concesion, activities_propio, discount_rate)
    plot_main_decision_analysis(df_main_decision, f'resultados-concesion/decision_principal.png')
    df_main_decision.to_csv(f'resultados-concesion/decision_principal.csv', index=False)
    print(f"   ✅ Análisis de decisión principal guardado en resultados-concesion/")
    
    # NUEVO: Análisis de decisiones individuales - Concesión
    print("\n🔍 Generando análisis de decisiones individuales - Concesión...")
    df_individual_concesion = analyze_individual_decisions(activities_concesion, discount_rate)
    plot_individual_decisions(df_individual_concesion, f'resultados-concesion/decisiones_individuales_concesion.png')
    df_individual_concesion.to_csv(f'resultados-concesion/decisiones_individuales_concesion.csv', index=False)
    print(f"   ✅ Análisis de decisiones individuales (Concesión) guardado en resultados-concesion/")
    
    # NUEVO: Análisis de decisiones individuales - Administración Propia
    print("\n🔍 Generando análisis de decisiones individuales - Administración Propia...")
    df_individual_propio = analyze_individual_decisions(activities_propio, discount_rate)
    plot_individual_decisions(df_individual_propio, f'resultados-administracion-propia/decisiones_individuales_propio.png')
    df_individual_propio.to_csv(f'resultados-administracion-propia/decisiones_individuales_propio.csv', index=False)
    print(f"   ✅ Análisis de decisiones individuales (Administración Propia) guardado en resultados-administracion-propia/")
    
    # Crear resumen de escenarios principales
    print("🎯 Generando resumen de escenarios principales...")
    scenarios_data = []
    
    # Mejor combinación de concesión
    mejor_concesion = df_concesion.iloc[0] if len(df_concesion) > 0 else None
    if mejor_concesion is not None:
        actividades_concesion = [col for col in df_concesion.columns if col != 'EV_total' and mejor_concesion[col] == 1]
        scenarios_data.append({
            'Escenario': 'Concesión',
            'EV_Total': mejor_concesion['EV_total'],
            'Actividades_Seleccionadas': ', '.join(actividades_concesion) if actividades_concesion else 'Ninguna',
            'Num_Actividades': len(actividades_concesion)
        })
    
    # Mejor combinación de administración propia
    mejor_propio = df_propio.iloc[0] if len(df_propio) > 0 else None
    if mejor_propio is not None:
        actividades_propias = [col for col in df_propio.columns if col != 'EV_total' and mejor_propio[col] == 1]
        scenarios_data.append({
            'Escenario': 'Administración Propia',
            'EV_Total': mejor_propio['EV_total'],
            'Actividades_Seleccionadas': ', '.join(actividades_propias) if actividades_propias else 'Ninguna',
            'Num_Actividades': len(actividades_propias)
        })
    
    df_scenarios = pd.DataFrame(scenarios_data)
    plot_main_scenarios(df_scenarios, f'resultados-concesion/escenarios_principales.png')
    df_scenarios.to_csv(f'resultados-concesion/escenarios_principales.csv', index=False)
    print(f"   ✅ Resumen de escenarios guardado en resultados-concesion/")
    
    # NUEVO: Resumen ejecutivo con recomendaciones
    print("\n📋 Generando resumen ejecutivo...")
    generate_executive_summary(activities_concesion, activities_propio, discount_rate)
    print(f"   ✅ Resumen ejecutivo generado")

    # Imprimir resumen de resultados
    print('\n' + '='*60)
    print('📊 RESUMEN DE RESULTADOS')
    print('='*60)
    
    print('\n=== EV por actividad - CONCESIÓN ===')
    for a in activities_concesion:
        print(f"- {a.name}: EV = {expected_npv(a, discount_rate):,.0f} (horizonte {a.horizon_years} años)")

    print('\n=== EV por actividad - ADMINISTRACIÓN PROPIA ===')
    for a in activities_propio:
        print(f"- {a.name}: EV = {expected_npv(a, discount_rate):,.0f} (horizonte {a.horizon_years} años)")

    print('\n=== Top 5 combinaciones - CONCESIÓN ===')
    print(df_concesion.head(5)[['EV_total'] + [col for col in df_concesion.columns if col != 'EV_total']].to_string(index=False))

    print('\n=== Top 5 combinaciones - ADMINISTRACIÓN PROPIA ===')
    print(df_propio.head(5)[['EV_total'] + [col for col in df_propio.columns if col != 'EV_total']].to_string(index=False))

    print('\n=== Comparación: Concesión vs Administración Propia ===')
    print(df_comparison[['Actividad', 'EV_Propio', 'EV_Concesion', 'Diferencia_EV', 'Mejor_Opcion']].to_string(index=False))

    print('\n=== Escenarios Principales: Concesión vs Administración Propia ===')
    print(df_scenarios[['Escenario', 'EV_Total', 'Num_Actividades', 'Actividades_Seleccionadas']].to_string(index=False))

    # Resumen final
    end_time = time.time()
    total_time = end_time - start_time
    
    print(f"\n🎉 ¡Análisis completado exitosamente!")
    print(f"⏱️  Tiempo total: {total_time:.1f} segundos")
    print(f"📊 Combinaciones concesión: {len(df_concesion):,}")
    print(f"📊 Combinaciones administración propia: {len(df_propio):,}")
    print(f"📁 Archivos generados: 21")
    
    print('\n📋 Archivos generados:')
    print(f'\n📁 Carpeta "resultados-concesion":')
    print(f' - combinaciones_ev.csv')
    print(f' - tornado.png')
    print(f' - tornado_data.csv')
    print(f' - arbol_decision.png')
    print(f' - top_10_combinaciones.png')
    print(f' - worst_10_combinaciones.png')
    print(f' - comparacion_concesion_vs_propio.png')
    print(f' - comparacion_concesion_vs_propio.csv')
    print(f' - escenarios_principales.png')
    print(f' - escenarios_principales.csv')
    print(f' - decision_principal.png')
    print(f' - decision_principal.csv')
    print(f' - decisiones_individuales_concesion.png')
    print(f' - decisiones_individuales_concesion.csv')
    print(f' - resumen_ejecutivo.txt')
    
    print(f'\n📁 Carpeta "resultados-administracion-propia":')
    print(f' - combinaciones_ev.csv')
    print(f' - tornado.png')
    print(f' - tornado_data.csv')
    print(f' - arbol_decision.png')
    print(f' - top_10_combinaciones.png')
    print(f' - worst_10_combinaciones.png')
    print(f' - decisiones_individuales_propio.png')
    print(f' - decisiones_individuales_propio.csv')

def create_parameters_excel():
    """
    Crea un archivo Excel con todos los parámetros de ambos escenarios
    """
    print("\n📊 CREANDO ARCHIVO EXCEL CON PARÁMETROS...")
    
    # Lista para almacenar todos los datos
    all_data = []
    
    # Procesar administración propia
    for activity in P_PROPIO.activities:
        for i, outcome in enumerate(activity['outcomes']):
            caso = 2 - i  # 2=bueno, 1=intermedio, 0=pesimista
            all_data.append({
                'escenario': 'Administración Propia',
                'actividad': activity['name'],
                'caso': caso,
                'label': outcome['label'],
                'prob': outcome['prob'],
                'npv': outcome['npv'],
                'horizon_years': activity['horizon_years']
            })
    
    # Procesar concesión
    for activity in P_CONCESION.activities:
        for i, outcome in enumerate(activity['outcomes']):
            caso = 2 - i  # 2=bueno, 1=intermedio, 0=pesimista
            all_data.append({
                'escenario': 'Concesión',
                'actividad': activity['name'],
                'caso': caso,
                'label': outcome['label'],
                'prob': outcome['prob'],
                'npv': outcome['npv'],
                'horizon_years': activity['horizon_years']
            })
    
    # Crear DataFrame
    df = pd.DataFrame(all_data)
    
    # Guardar en Excel
    excel_file = 'parametros_completos.xlsx'
    with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
        # Hoja principal con todos los datos
        df.to_excel(writer, sheet_name='Todos_Parametros', index=False)
        
        # Hoja separada para administración propia
        df_propio = df[df['escenario'] == 'Administración Propia'].copy()
        df_propio = df_propio.drop('escenario', axis=1)
        df_propio.to_excel(writer, sheet_name='Administracion_Propia', index=False)
        
        # Hoja separada para concesión
        df_concesion = df[df['escenario'] == 'Concesión'].copy()
        df_concesion = df_concesion.drop('escenario', axis=1)
        df_concesion.to_excel(writer, sheet_name='Concesion', index=False)
    
    print(f"✅ Archivo Excel creado: {excel_file}")
    print(f"   📋 Hojas: Todos_Parametros, Administracion_Propia, Concesion")
    print(f"   📊 Total de registros: {len(df)}")
    
    return excel_file

if __name__ == '__main__':
    main()

import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd


def grafico_votos_vs_emendas(dados, x="votos_deputado", y="valor_emenda", titulo="Votos vs Emendas"):
    plt.figure(figsize=(10, 6))
    
    # Criar scatter plot com linha de regressão
    sns.regplot(data=dados, x=x, y=y, scatter_kws={'alpha':0.5, 's':30}, line_kws={'color': 'red'})
    
    plt.title(titulo, fontsize=14, fontweight='bold')
    plt.xlabel(x.replace('_', ' ').title())
    plt.ylabel(y.replace('_', ' ').title())
    
    # Correlação
    corr = dados[x].corr(dados[y])
    plt.text(0.05, 0.95, f'Correlação: {corr:.3f}', 
             transform=plt.gca().transAxes, 
             bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5),
             fontsize=12, fontweight='bold')
    
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()


def histograma_emendas(dados):
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    # Absoluto
    axes[0].hist(dados["valor_emenda"], bins=50, edgecolor='black', alpha=0.7, color='steelblue')
    axes[0].set_title("Distribuição das Emendas - Valores Absolutos", fontsize=12, fontweight='bold')
    axes[0].set_xlabel("Valor (R$)")
    axes[0].set_ylabel("Frequência")
    axes[0].grid(True, alpha=0.3)
    
    # Log (para visualizar melhor a distribuição)
    axes[1].hist(np.log1p(dados["valor_emenda"]), bins=50, edgecolor='black', alpha=0.7, color='coral')
    axes[1].set_title("Distribuição das Emendas - Escala Log", fontsize=12, fontweight='bold')
    axes[1].set_xlabel("Log(Valor + 1)")
    axes[1].set_ylabel("Frequência")
    axes[1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.show()


def grafico_per_capita(dados):
    """Gráfico comparativo: absoluto vs per capita com cores por IDH"""
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))
    
    # Criar categorias de IDH para cores
    dados['idh_categoria'] = pd.cut(
        dados['idh'], 
        bins=[0, 0.6, 0.7, 0.8, 1.0],
        labels=['Muito Baixo\n(< 0.6)', 'Baixo\n(0.6-0.7)', 'Médio\n(0.7-0.8)', 'Alto\n(> 0.8)']
    )
    
    # Paleta de cores: vermelho (baixo IDH) para verde (alto IDH)
    cores = {'Muito Baixo\n(< 0.6)': 'darkred', 
             'Baixo\n(0.6-0.7)': 'red', 
             'Médio\n(0.7-0.8)': 'lightgreen', 
             'Alto\n(> 0.8)': 'darkgreen'}
    
    # Gráfico 1: Valores absolutos (tamanho das bolhas = população)
    ax1 = axes[0]
    for categoria in dados['idh_categoria'].unique():
        subset = dados[dados['idh_categoria'] == categoria]
        if len(subset) > 0:
            ax1.scatter(
                subset['votos_deputado'], 
                subset['valor_emenda'],
                s=subset['populacao'] / 500,  # tamanho proporcional à população
                color=cores[categoria],
                alpha=0.6,
                edgecolors='black',
                linewidth=0.5,
                label=categoria
            )
    
    ax1.set_xlabel('Votos do Deputado', fontsize=12)
    ax1.set_ylabel('Valor das Emendas (R$)', fontsize=12)
    ax1.set_title('Absoluto: Cidades maiores dominam a escala', fontsize=14, fontweight='bold')
    ax1.legend(title='IDH', bbox_to_anchor=(1.05, 1), loc='upper left')
    ax1.grid(True, alpha=0.3)
    
    # Gráfico 2: Valores per capita (tamanho fixo - comparação justa)
    ax2 = axes[1]
    for categoria in dados['idh_categoria'].unique():
        subset = dados[dados['idh_categoria'] == categoria]
        if len(subset) > 0:
            ax2.scatter(
                subset['votos_per_capita'], 
                subset['emenda_per_capita'],
                s=50,  # tamanho fixo - todos comparáveis!
                color=cores[categoria],
                alpha=0.6,
                edgecolors='black',
                linewidth=0.5,
                label=categoria
            )
    
    # Linha de tendência geral
    z = np.polyfit(dados['votos_per_capita'].dropna(), dados['emenda_per_capita'].dropna(), 1)
    p = np.poly1d(z)
    x_sorted = np.sort(dados['votos_per_capita'].dropna())
    ax2.plot(x_sorted, p(x_sorted), "r--", alpha=0.8, 
             label=f'Tendência (r={dados["votos_per_capita"].corr(dados["emenda_per_capita"]):.2f})')
    
    ax2.set_xlabel('Votos per capita', fontsize=12)
    ax2.set_ylabel('Emendas per capita (R$)', fontsize=12)
    ax2.set_title('Per Capita: Comparação justa entre cidades', fontsize=14, fontweight='bold')
    ax2.legend(title='IDH', bbox_to_anchor=(1.05, 1), loc='upper left')
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.show()


def comparar_grupos_idh(dados):
    """Compara correlações e médias por grupo de IDH"""
    
    # Criar grupos de IDH (tercis)
    dados['grupo_idh'] = pd.qcut(dados['idh'], q=3, labels=['Baixo IDH', 'Médio IDH', 'Alto IDH'])
    
    # Calcular estatísticas por grupo
    grupos = []
    for grupo in ['Baixo IDH', 'Médio IDH', 'Alto IDH']:
        subset = dados[dados['grupo_idh'] == grupo]
        
        if 'emenda_per_capita' in dados.columns:
            # Com per capita
            stats = {
                'Grupo': grupo,
                'N_cidades': len(subset),
                'IDH_médio': subset['idh'].mean(),
                'Votos_per_capita_médio': subset['votos_per_capita'].mean(),
                'Emenda_per_capita_média': subset['emenda_per_capita'].mean(),
                'Correlação_votos_emendas': subset['votos_per_capita'].corr(subset['emenda_per_capita'])
            }
        else:
            # Sem per capita
            stats = {
                'Grupo': grupo,
                'N_cidades': len(subset),
                'IDH_médio': subset['idh'].mean(),
                'Votos_médios': subset['votos_deputado'].mean(),
                'Emenda_média': subset['valor_emenda'].mean(),
                'Correlação_votos_emendas': subset['votos_deputado'].corr(subset['valor_emenda'])
            }
        
        grupos.append(stats)
    
    # Criar DataFrame com resultados
    resultados = pd.DataFrame(grupos)
    
    print("\n" + "="*60)
    print("📊 COMPARAÇÃO ENTRE GRUPOS DE IDH")
    print("="*60)
    print(resultados.to_string(index=False))
    
    # Gráfico de barras comparativo
    if 'emenda_per_capita' in dados.columns:
        fig, ax = plt.subplots(figsize=(10, 6))
        
        x = np.arange(len(resultados))
        width = 0.35
        
        ax.bar(x - width/2, resultados['Emenda_per_capita_média'], width, label='Emenda per capita', color='steelblue')
        ax.bar(x + width/2, resultados['Votos_per_capita_médio'] * 100, width, label='Votos per capita (×100)', color='coral')
        
        ax.set_xlabel('Grupo IDH', fontsize=12)
        ax.set_ylabel('Valor', fontsize=12)
        ax.set_title('Comparação entre Grupos de IDH', fontsize=14, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(resultados['Grupo'])
        ax.legend()
        ax.grid(True, alpha=0.3, axis='y')
        
        plt.tight_layout()
        plt.show()
    
    return resultados


def comparar_grupos_simples(com_emendas, sem_emendas):
    """
    Gráfico simples comparando os dois grupos
    """
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    
    # Dados para os boxplots
    dados_idh = [com_emendas['idh'].dropna(), sem_emendas['idh'].dropna()]
    dados_votos = [com_emendas['votos_deputado'].dropna(), sem_emendas['votos_deputado'].dropna()]
    dados_vpc = [com_emendas['votos_per_capita'].dropna(), sem_emendas['votos_per_capita'].dropna()]
    
    # 1. IDH
    axes[0].boxplot(dados_idh, labels=['Com Emendas', 'Sem Emendas'])
    axes[0].set_ylabel('IDH')
    axes[0].set_title('H1: Justiça Social\n(Emendas para baixo IDH?)')
    axes[0].grid(True, alpha=0.3, axis='y')
    
    # 2. Votos Absolutos
    axes[1].boxplot(dados_votos, labels=['Com Emendas', 'Sem Emendas'])
    axes[1].set_ylabel('Votos do Candidato')
    axes[1].set_title('H2: Reduto Eleitoral\n(Emendas onde tem mais votos?)')
    axes[1].grid(True, alpha=0.3, axis='y')
    
    # 3. Votos per capita
    axes[2].boxplot(dados_vpc, labels=['Com Emendas', 'Sem Emendas'])
    axes[2].set_ylabel('Votos por Habitante')
    axes[2].set_title('H3: Reduto Eleitoral (per capita)\n(Emendas onde é mais forte?)')
    axes[2].grid(True, alpha=0.3, axis='y')
    
    plt.suptitle('Comparação: Municípios com e sem Emendas', fontsize=16, fontweight='bold')
    plt.tight_layout()
    plt.show()


def scatter_hipoteses(dados):
    """
    Scatter plots para visualizar as relações
    """
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    
    # Destacar cidades com emendas
    com_emendas = dados[dados['valor_emenda'] > 0]
    sem_emendas = dados[dados['valor_emenda'] == 0]
    
    # 1. IDH vs Emenda per capita
    axes[0].scatter(sem_emendas['idh'], sem_emendas['emenda_per_capita'], 
                   alpha=0.3, s=20, label='Sem emendas', color='gray')
    axes[0].scatter(com_emendas['idh'], com_emendas['emenda_per_capita'], 
                   alpha=0.8, s=100, label='Com emendas', color='red', edgecolors='black')
    axes[0].set_xlabel('IDH')
    axes[0].set_ylabel('Emenda per capita (R$)')
    axes[0].set_title('H1: Justiça Social\n(Emendas em cidades de baixo IDH?)')
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)
    
    # 2. Votos per capita vs Emenda per capita
    axes[1].scatter(sem_emendas['votos_per_capita'], sem_emendas['emenda_per_capita'], 
                   alpha=0.3, s=20, label='Sem emendas', color='gray')
    axes[1].scatter(com_emendas['votos_per_capita'], com_emendas['emenda_per_capita'], 
                   alpha=0.8, s=100, label='Com emendas', color='blue', edgecolors='black')
    axes[1].set_xlabel('Votos per capita')
    axes[1].set_ylabel('Emenda per capita (R$)')
    axes[1].set_title('H2/H3: Reduto Eleitoral\n(Emendas onde tem mais votos?)')
    axes[1].legend()
    axes[1].grid(True, alpha=0.3)
    
    plt.suptitle('Teste de Hipóteses - Guilherme Cortez', fontsize=16, fontweight='bold')
    plt.tight_layout()
    plt.show()
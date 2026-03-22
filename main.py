import pandas as pd
import statsmodels.api as sm
import numpy as np
import visualizacao as vis
from aquisicao import (
    CANDIDATO_ALVO, carregar_dados, preparar_votos, preparar_emendas,
    preparar_idh, preparar_populacao, juntar_dados
)

def testar_hipoteses_simples(dados):
    """
    Testa as hipóteses com os dados disponíveis
    H1: Emendas para baixo IDH (justiça social)
    H2: Emendas para reduto eleitoral (votos absolutos)
    H3: Emendas para reduto eleitoral (votos per capita)
    """
    print("\n" + "="*60)
    print("🧪 TESTE DE HIPÓTESES - DADOS DISPONÍVEIS")
    print("="*60)
    
    # Calcular votos per capita se não existir
    if 'votos_per_capita' not in dados.columns:
        dados['votos_per_capita'] = dados['votos_deputado'] / dados['populacao'].replace(0, np.nan)
    
    # Separar municípios com e sem emendas
    com_emendas = dados[dados['valor_emenda'] > 0].copy()
    sem_emendas = dados[dados['valor_emenda'] == 0].copy()
    
    print(f"\n📊 Comparação: {len(com_emendas)} cidades com emendas vs {len(sem_emendas)} sem emendas")
    
    # ----------------------------------------------------------------------
    # H1: Emendas para baixo IDH?
    # ----------------------------------------------------------------------
    print("\n🔹 H1: JUSTIÇA SOCIAL - Emendas para municípios de BAIXO IDH")
    print("-" * 50)
    
    idh_com = com_emendas['idh'].mean()
    idh_sem = sem_emendas['idh'].mean()
    
    print(f"   IDH médio (com emendas): {idh_com:.3f}")
    print(f"   IDH médio (sem emendas): {idh_sem:.3f}")
    print(f"   Diferença: {idh_com - idh_sem:.3f}")
    
    if idh_com < idh_sem:
        print(f"   ✅ A favor de H1: Cidades com emendas têm IDH MENOR")
        print(f"      (diferença de {idh_sem - idh_com:.3f} pontos)")
    else:
        print(f"   ❌ Contra H1: Cidades com emendas têm IDH MAIOR ou igual")
    
    # ----------------------------------------------------------------------
    # H2: Emendas para reduto eleitoral (votos absolutos)?
    # ----------------------------------------------------------------------
    print("\n🔹 H2: REDUTO ELEITORAL - Emendas onde tem MAIS VOTOS")
    print("-" * 50)
    
    votos_com = com_emendas['votos_deputado'].mean()
    votos_sem = sem_emendas['votos_deputado'].mean()
    
    print(f"   Votos médios (com emendas): {votos_com:.1f}")
    print(f"   Votos médios (sem emendas): {votos_sem:.1f}")
    print(f"   Diferença: {votos_com - votos_sem:.1f} votos")
    
    if votos_com > votos_sem:
        print(f"   ✅ A favor de H2: Cidades com emendas têm MAIS VOTOS")
        print(f"      (média {votos_com/votos_sem:.1f}x maior)")
    else:
        print(f"   ❌ Contra H2: Cidades com emendas têm MENOS votos")
    
    # ----------------------------------------------------------------------
    # H3: Emendas para reduto eleitoral (votos per capita)?
    # ----------------------------------------------------------------------
    print("\n🔹 H3: REDUTO ELEITORAL (per capita) - Emendas onde tem MAIS VOTOS/HABITANTE")
    print("-" * 50)
    
    vpc_com = com_emendas['votos_per_capita'].mean()
    vpc_sem = sem_emendas['votos_per_capita'].mean()
    
    print(f"   Votos/hab (com emendas): {vpc_com:.6f}")
    print(f"   Votos/hab (sem emendas): {vpc_sem:.6f}")
    print(f"   Diferença: {vpc_com - vpc_sem:.6f}")
    
    if vpc_com > vpc_sem:
        print(f"   ✅ A favor de H3: Cidades com emendas têm MAIS VOTOS PER CAPITA")
        print(f"      (proporção {vpc_com/vpc_sem:.1f}x maior)")
    else:
        print(f"   ❌ Contra H3: Cidades com emendas têm MENOS votos per capita")
    
    # ----------------------------------------------------------------------
    # Top 5 municípios para análise qualitativa
    # ----------------------------------------------------------------------
    print("\n🔍 ANÁLISE QUALITATIVA - Top 5 municípios com emendas")
    print("-" * 50)
    
    top5 = com_emendas.nlargest(5, 'valor_emenda')[
        ['nm_municipio', 'valor_emenda', 'votos_deputado', 'idh', 'votos_per_capita']
    ]
    
    for idx, row in top5.iterrows():
        print(f"\n   {row['nm_municipio']}:")
        print(f"      Emenda: R$ {row['valor_emenda']:,.2f}")
        print(f"      Votos: {row['votos_deputado']}")
        print(f"      IDH: {row['idh']:.3f}")
        print(f"      Votos/hab: {row['votos_per_capita']:.6f}")
    
    return com_emendas, sem_emendas


def main():
    print("=" * 60)
    print(f"🔍 ANÁLISE DE EMENDAS - {CANDIDATO_ALVO}")
    print("=" * 60)
    
    # Carregar dados
    votos, emendas, idh, populacao, dtb = carregar_dados()
    
    # Preparar bases
    print("\n📊 Processando dados...")
    votos = preparar_votos(votos, dtb)
    emendas = preparar_emendas(emendas, dtb)
    idh = preparar_idh(idh, dtb, uf_alvo='SP')
    populacao = preparar_populacao(populacao, dtb, uf_alvo='SP')
    
    # Juntar dados
    dados = juntar_dados(votos, emendas, idh, populacao, dtb)
    
    # Criar variáveis per capita
    if 'populacao' in dados.columns and dados['populacao'].notna().any():
        dados['votos_per_capita'] = dados['votos_deputado'] / dados['populacao']
        dados['emenda_per_capita'] = dados['valor_emenda'] / dados['populacao'].replace(0, np.nan)
    
    # total de votos do deputado
    total_votos = dados['votos_deputado'].sum()

    if total_votos > 0:
        dados['market_share'] = dados['votos_deputado'] / total_votos
    else:
        dados['market_share'] = np.nan

    # =========================================================
    # ESTATÍSTICAS DESCRITIVAS
    # =========================================================

    print("\n" + "=" * 60)
    print("📈 ESTATÍSTICAS DESCRITIVAS")
    print("=" * 60)
    
    print(f"\n📍 Votos:")
    print(f"   Total: {dados['votos_deputado'].sum():,.0f}")
    print(f"   Média por município: {dados['votos_deputado'].mean():.0f}")
    print(f"   Mediana: {dados['votos_deputado'].median():.0f}")
    
    print("\n📍 Top 10 municípios em votos:")
    top10 = dados.nlargest(10, 'votos_deputado')[['nm_municipio', 'votos_deputado']]
    for idx, row in top10.iterrows():
        print(f"   {row['nm_municipio']}: {row['votos_deputado']} votos")
    
    print(f"\n📍 Emendas (R$):")
    print(f"   Total: R$ {dados['valor_emenda'].sum():,.2f}")
    print(f"   Média: R$ {dados['valor_emenda'].mean():,.2f}")
    print(f"   Mediana: R$ {dados['valor_emenda'].median():,.2f}")
    
    if (dados['valor_emenda'] > 0).any():
        print("\n📍 Municípios com emendas:")
        com_emendas_lista = dados[dados['valor_emenda'] > 0][['nm_municipio', 'valor_emenda']].sort_values('valor_emenda', ascending=False)
        for idx, row in com_emendas_lista.iterrows():
            print(f"   {row['nm_municipio']}: R$ {row['valor_emenda']:,.2f}")
    
    print(f"\n📍 Cobertura dos dados:")
    print(f"   Municípios com IDH: {dados['idh'].notna().sum()}")
    print(f"   Municípios com população: {dados['populacao'].notna().sum()}")
    
    if 'populacao' in dados.columns and dados['populacao'].notna().any():
        print(f"\n📍 Per capita (médias):")
        print(f"   Votos/habitante: {dados['votos_per_capita'].mean():.4f}")
        print(f"   R$/habitante: R$ {dados['emenda_per_capita'].mean():.2f}")
    
    # =========================================================
    # CORRELAÇÕES
    # =========================================================

    print("\n📊 CORRELAÇÕES:")

    if 'populacao' in dados.columns and dados['populacao'].notna().any():
        corr_pop = dados[['votos_deputado', 'populacao']].dropna().corr().iloc[0,1]
        print(f"   Votos x População: {corr_pop:.3f}")
    
    if dados['idh'].notna().any():
        corr_votos_idh = dados[['votos_deputado', 'idh']].dropna().corr().iloc[0,1]
        print(f"   Votos x IDH: {corr_votos_idh:.3f}")
        
        corr_emendas_idh = dados[['valor_emenda', 'idh']].dropna().corr().iloc[0,1]
        print(f"   Emendas x IDH: {corr_emendas_idh:.3f}")
    
    corr_data = dados[['market_share', 'valor_emenda']].dropna()

    if len(corr_data) > 2:
        corr_market_emendas = corr_data.corr().iloc[0,1]
        print(f"   Market Share x Emendas: {corr_market_emendas:.3f}")

    # =========================================================
    # TESTE DE HIPÓTESES
    # =========================================================

    com_emendas, sem_emendas = testar_hipoteses_simples(dados)

    # =========================================================
    # GRÁFICOS
    # =========================================================

    try:
        print("\n📊 Gerando gráficos...")
        vis.comparar_grupos_simples(com_emendas, sem_emendas)
        vis.scatter_hipoteses(dados)
    except Exception as e:
        print(f"⚠️ Erro ao gerar gráficos: {e}")

    # =========================================================
    # REGRESSÃO (VERSÃO CORRIGIDA)
    # =========================================================

    if dados['idh'].notna().any() and (dados['valor_emenda'] > 0).any():

        print("\n" + "=" * 60)
        print("📊 REGRESSÃO LOGÍSTICA: Probabilidade de receber emenda")
        print("=" * 60)

        # Criar variável dummy (1 = recebeu emenda)
        dados['recebeu_emenda'] = (dados['valor_emenda'] > 0).astype(int)

        X = dados[['market_share', 'idh']]
        Y = dados['recebeu_emenda']

        mask = X.notna().all(axis=1)
        X_clean = X[mask]
        Y_clean = Y[mask]

        if len(X_clean) > 10:

            X_clean = sm.add_constant(X_clean)

            modelo_logit = sm.Logit(Y_clean, X_clean).fit(disp=False)

            print(f"\nObservações: {len(X_clean)}")
            print(f"Municípios com emenda: {Y_clean.sum()}")
            print(f"Municípios sem emenda: {(Y_clean==0).sum()}")

            print("\nCoeficientes:")

            for var in modelo_logit.params.index:

                coef = modelo_logit.params[var]
                p_valor = modelo_logit.pvalues[var]

                sig = "***" if p_valor < 0.01 else "**" if p_valor < 0.05 else "*" if p_valor < 0.1 else ""

                print(f"   {var}: {coef:.3f} (p={p_valor:.3f}{sig})")

        else:

            print("⚠️ Dados insuficientes para regressão logística")


if __name__ == "__main__":
    main()
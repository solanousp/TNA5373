import pandas as pd
import unicodedata
import re
import numpy as np

CANDIDATO_ALVO = "GUILHERME CORTEZ"

UF_NOME_PARA_SIGLA = {
    'MINAS GERAIS': 'MG',
    'SÃO PAULO': 'SP',
    'RIO DE JANEIRO': 'RJ',
}

UF_PARA_CODIGO = {
    'AC': '12', 'AL': '27', 'AP': '16', 'AM': '13', 'BA': '29', 'CE': '23',
    'DF': '53', 'ES': '32', 'GO': '52', 'MA': '21', 'MT': '51', 'MS': '50',
    'MG': '31', 'PA': '15', 'PB': '25', 'PR': '41', 'PE': '26', 'PI': '22',
    'RJ': '33', 'RN': '24', 'RS': '43', 'RO': '11', 'RR': '14', 'SC': '42',
    'SP': '35', 'SE': '28', 'TO': '17'
}


def remover_acentos(texto):
    """Remove acentos de strings"""
    if pd.isna(texto):
        return texto
    texto = str(texto)
    texto = unicodedata.normalize('NFKD', texto).encode('ASCII', 'ignore').decode('ASCII')
    return texto


def ler_csv(caminho):
    return pd.read_csv(caminho, sep=";", encoding="latin1", low_memory=False)


def carregar_dados():
    """Carrega todas as bases"""
    print("\n📂 Carregando arquivos...")
    
    votos = ler_csv("dados/votacao_candidato_munzona_2022_SP.csv")
    emendas = ler_csv("dados/EmendasParlamentares.csv")
    idh = pd.read_excel("dados/IDH_municipio.xlsx")
    dtb = carregar_dtb()
    
    # Carregar população (opcional)
    populacao = None
    try:
        populacao = pd.read_excel(
            "dados/tab_Municipios_TCU.xls",
            header=6,
            dtype=str
        )
    except Exception as e:
        print(f"⚠️ População não carregada: {e}")
    
    return votos, emendas, idh, populacao, dtb


def carregar_dtb():
    """Carrega o DTB"""
    dtb = pd.read_excel(
        "dados/RELATORIO_DTB_BRASIL_2024_MUNICIPIOS.xls",
        header=None,
        dtype=str
    )
    
    dtb = dtb.iloc[:, [0, 1, 7, 8]].copy()
    dtb.columns = ['cod_uf', 'uf_nome', 'cod_ibge', 'nm_municipio']
    
    dtb['nm_municipio'] = dtb['nm_municipio'].str.upper().str.strip()
    dtb['nm_municipio'] = dtb['nm_municipio'].apply(remover_acentos)
    dtb['cod_ibge'] = dtb['cod_ibge'].astype(str).str.zfill(7)
    
    # Mapear UF
    dtb['uf'] = dtb['cod_uf'].map({
        '11': 'RO', '12': 'AC', '13': 'AM', '14': 'RR', '15': 'PA',
        '16': 'AP', '17': 'TO', '21': 'MA', '22': 'PI', '23': 'CE',
        '24': 'RN', '25': 'PB', '26': 'PE', '27': 'AL', '28': 'SE',
        '29': 'BA', '31': 'MG', '32': 'ES', '33': 'RJ', '35': 'SP',
        '41': 'PR', '42': 'SC', '43': 'RS', '50': 'MS', '51': 'MT',
        '52': 'GO', '53': 'DF'
    })
    
    dtb = dtb.dropna(subset=['cod_ibge'])
    print(f"✅ DTB carregado: {len(dtb)} municípios")
    return dtb


def preparar_votos(votos, dtb):
    """Prepara dados de votação"""
    # Filtrar candidato
    votos = votos[votos["NM_URNA_CANDIDATO"].str.contains('GUILHERME.*CORTEZ|CORTEZ', na=False, case=False, regex=True)].copy()
    votos = votos[votos["SG_UF"] == "SP"].copy()
    
    # Criar código IBGE com 7 dígitos
    votos['cod_ibge'] = (
        votos['SG_UF'].map(UF_PARA_CODIGO) + 
        votos['CD_MUNICIPIO'].astype(str).str.zfill(5)
    )
    
    # GARANTIR 7 DÍGITOS
    votos['cod_ibge'] = votos['cod_ibge'].astype(str).str.zfill(7)

    # Agrupar
    votos = votos.groupby(['cod_ibge', 'NM_MUNICIPIO'], as_index=False).agg({
        'QT_VOTOS_NOMINAIS': 'sum'
    })
    
    votos = votos.rename(columns={'QT_VOTOS_NOMINAIS': 'votos_deputado'})
    votos['nm_municipio'] = votos['NM_MUNICIPIO'].str.upper().str.strip()
    votos['nm_municipio'] = votos['nm_municipio'].apply(remover_acentos)
    
    print(f"✅ Votos: {len(votos)} municípios, {votos['votos_deputado'].sum():,.0f} votos totais")
    print(f"   Exemplos: {votos[['nm_municipio', 'votos_deputado']].head(3).to_dict('records')}")
    return votos[['nm_municipio', 'votos_deputado']]


def preparar_emendas(emendas, dtb):
    """Prepara dados de emendas"""
    # Filtrar GUILHERME CORTEZ
    emendas_cortez = emendas[emendas['Nome do Autor da Emenda'].str.contains('GUILHERME|CORTEZ', na=False, case=False)].copy()
    
    if len(emendas_cortez) == 0:
        print("⚠️ Nenhuma emenda encontrada para o candidato")
        return pd.DataFrame(columns=['nm_municipio', 'valor_emenda'])
    
    # Verificar distribuição
    multiplos = (emendas_cortez['Município'] == 'Múltiplo').sum()
    sem_info = (emendas_cortez['Município'] == 'Sem informação').sum()
    especificos = len(emendas_cortez) - multiplos - sem_info
    
    print(f"✅ Emendas do candidato: {len(emendas_cortez)} total")
    print(f"   → {especificos} município específico, {multiplos} múltiplos, {sem_info} sem informação")
    
    # VERIFICAR SE JÁ EXISTE CÓDIGO IBGE
    if 'Código IBGE' in emendas_cortez.columns:
        print("   📍 Coluna 'Código IBGE' encontrada!")
        emendas_com_ibge = emendas_cortez[emendas_cortez['Código IBGE'].notna()].copy()
        if len(emendas_com_ibge) > 0:
            print(f"   → {len(emendas_com_ibge)} emendas com código IBGE direto")
    
    if especificos == 0:
        print("   ⚠️ Todas as emendas são múltiplas ou sem informação")
        return pd.DataFrame(columns=['nm_municipio', 'valor_emenda'])
    
    # Identificar coluna de valor
    col_valor = None
    for col in emendas_cortez.columns:
        if 'VALOR' in col.upper() and ('EMPENHADO' in col.upper() or 'EMPENHAD' in col.upper()):
            col_valor = col
            break
    
    if col_valor is None:
        print("   ⚠️ Coluna de valor não encontrada")
        return pd.DataFrame(columns=['nm_municipio', 'valor_emenda'])
    
    # Extrair município da localidade
    emendas_cortez['municipio_extraido'] = None
    if 'Localidade de aplicação do recurso' in emendas_cortez.columns:
        mascara = emendas_cortez['Localidade de aplicação do recurso'].str.contains('- SP', na=False)
        emendas_cortez.loc[mascara, 'municipio_extraido'] = (
            emendas_cortez.loc[mascara, 'Localidade de aplicação do recurso']
            .str.replace('- SP', '', regex=False)
            .str.strip()
        )
    
    emendas_cortez['municipio_padronizado'] = (
        emendas_cortez['municipio_extraido']
        .fillna(emendas_cortez['Município'])
        .str.upper()
        .str.strip()
    )
    emendas_cortez['municipio_padronizado'] = emendas_cortez['municipio_padronizado'].apply(remover_acentos)
    
    # Filtrar apenas municípios específicos de SP
    mascara_validos = ~emendas_cortez['Município'].isin(['Múltiplo', 'Sem informação'])
    cidades_sp = dtb[dtb['uf'] == 'SP']['nm_municipio'].unique()
    mascara_sp = emendas_cortez['municipio_padronizado'].isin(cidades_sp)
    
    emendas_validas = emendas_cortez[mascara_validos & mascara_sp].copy()
    print(f"\n   📍 Emendas com município específico em SP: {len(emendas_validas)}")
    
    if len(emendas_validas) == 0:
        print("   ⚠️ Nenhuma correspondeu ao DTB")
        return pd.DataFrame(columns=['nm_municipio', 'valor_emenda'])
    
    # Converter valor
    emendas_validas['valor_emenda'] = pd.to_numeric(
        emendas_validas[col_valor].astype(str)
            .str.replace('.', '', regex=False)
            .str.replace(',', '.', regex=False)
            .str.replace('[^0-9.]', '', regex=True),
        errors='coerce'
    )
    
    # Juntar com DTB para código IBGE
    dtb_clean = dtb[dtb['uf'] == 'SP'][['nm_municipio', 'cod_ibge']].drop_duplicates('nm_municipio')
    dtb_clean['cod_ibge'] = dtb_clean['cod_ibge'].astype(str).str.strip().str.zfill(7)
    
    emendas_com_ibge = emendas_validas.merge(
        dtb_clean,
        left_on='municipio_padronizado',
        right_on='nm_municipio',
        how='inner'
    )
    
    print(f"   ✅ Emendas com código IBGE: {len(emendas_com_ibge)} de {len(emendas_validas)}")
    
    if len(emendas_com_ibge) == 0:
        return pd.DataFrame(columns=['nm_municipio', 'valor_emenda'])
    
    # Mostrar quais municípios foram encontrados
    print(f"\n   📋 Municípios com emendas:")
    for idx, row in emendas_com_ibge.iterrows():
        print(f"      - {row['nm_municipio']}: R$ {row['valor_emenda']:,.2f} (código: {row['cod_ibge']})")
    
    emendas_agrupadas = emendas_com_ibge.groupby(['cod_ibge', 'nm_municipio'], as_index=False).agg({
        'valor_emenda': 'sum'
    })
    
    print(f"\n   💰 TOTAL: R$ {emendas_agrupadas['valor_emenda'].sum():,.2f} em {len(emendas_agrupadas)} municípios")
    
    return emendas_agrupadas[['nm_municipio', 'valor_emenda']] 


def preparar_idh(idh, dtb, uf_alvo='SP'):
    """Prepara dados de IDH"""
    print("\n🔍 DEBUG - IDH original:")
    print(f"   Colunas: {idh.columns.tolist()}")
    print(f"   Primeiros territórios: {idh['Territorialidade'].head(10).tolist()}")
    
    # Filtrar SP
    idh = idh[idh['Territorialidade'].str.contains(uf_alvo, na=False)].copy()
    print(f"   Registros SP: {len(idh)}")
    
    # Extrair nome do município - diferentes formatos possíveis
    idh['nm_municipio'] = idh['Territorialidade'].str.replace(r'\s*\(SP\)', '', regex=True)
    idh['nm_municipio'] = idh['nm_municipio'].str.replace(r' - SP', '', regex=False)
    idh['nm_municipio'] = idh['nm_municipio'].str.upper().str.strip()
    idh['nm_municipio'] = idh['nm_municipio'].apply(remover_acentos)
    
    print(f"   Exemplos municípios extraídos: {idh['nm_municipio'].head(10).tolist()}")
    
    # Encontrar coluna IDH
    col_idh = None
    for col in idh.columns:
        if 'IDHM' in col and 'Posição' not in col:
            col_idh = col
            break
    
    if col_idh is None:
        raise KeyError("Coluna IDHM não encontrada!")
    
    idh['idh'] = idh[col_idh].astype(str).str.replace(',', '.').str.strip()
    idh['idh'] = pd.to_numeric(idh['idh'], errors='coerce')
    idh.loc[idh['idh'] > 1, 'idh'] = idh.loc[idh['idh'] > 1, 'idh'] / 1000
    print("\n🔍 VERIFICANDO CORREÇÃO DO IDH:")
    print(f"   IDH > 1 antes da correção: {(idh['idh'] > 1).sum()} municípios")
    print(f"   IDH após correção - exemplos:")
    exemplos = idh.sample(min(5, len(idh)))[['nm_municipio', 'idh']]
    for idx, row in exemplos.iterrows():
        print(f"      {row['nm_municipio']}: {row['idh']}")
    # DEBUG: Verificar DTB de SP
    dtb_sp = dtb[dtb['uf'] == 'SP'][['cod_ibge', 'nm_municipio']].drop_duplicates('nm_municipio')
    print(f"\n🔍 DTB SP: {len(dtb_sp)} municípios")
    
    # Juntar com DTB para validar (opcional - apenas para debug)
    idh_com_ibge = idh.merge(dtb_sp, on='nm_municipio', how='inner')
    print(f"\n✅ IDH com código IBGE: {len(idh_com_ibge)} municípios")
    
    # Retornar apenas as colunas necessárias, incluindo o nome do município
    return idh[['nm_municipio', 'idh']].dropna(subset=['idh'])


def preparar_populacao(populacao, dtb, uf_alvo='SP'):
    """Prepara dados de população"""
    if populacao is None or populacao.empty:
        return None
    
    # Identificar colunas
    col_nome = None
    col_pop = None
    
    for col in populacao.columns:
        col_str = str(col).upper()
        if 'NOME' in col_str and 'MUNIC' in col_str:
            col_nome = col
        if 'POPULA' in col_str:
            col_pop = col
    
    if col_nome is None or col_pop is None:
        print("⚠️ Colunas de população não identificadas")
        return None
    
    pop_df = pd.DataFrame()
    pop_df['nm_municipio'] = populacao[col_nome].astype(str).str.upper().str.strip()
    pop_df['nm_municipio'] = pop_df['nm_municipio'].apply(remover_acentos)
    
    # Converter população
    pop_df['populacao'] = populacao[col_pop].astype(str)
    pop_df['populacao'] = pop_df['populacao'].str.replace('.', '', regex=False)
    pop_df['populacao'] = pop_df['populacao'].str.replace(',', '.', regex=False)
    pop_df['populacao'] = pd.to_numeric(pop_df['populacao'], errors='coerce')
    
    # Filtrar SP
    cod_uf = '35' if uf_alvo == 'SP' else '31'
    mask_uf = populacao['COD. UF'].astype(str).str.strip() == cod_uf
    pop_df = pop_df[mask_uf].copy()
    
    # Adicionar código IBGE (opcional, mas podemos manter para referência)
    pop_df['cod_ibge'] = (
        populacao.loc[mask_uf, 'COD. UF'].astype(str).str.zfill(2) + 
        populacao.loc[mask_uf, 'COD. MUNIC'].astype(str).str.zfill(5)
    )
    
    pop_df = pop_df[pop_df['populacao'] > 0]
    pop_df = pop_df.drop_duplicates(subset=['nm_municipio'])
    
    print(f"✅ População: {len(pop_df)} municípios, {pop_df['populacao'].sum():,.0f} habitantes")
    return pop_df[['nm_municipio', 'populacao']]


def juntar_dados(votos, emendas, idh, populacao, dtb):
    """Junta todas as bases usando o nome do município como chave"""
    print("\n🔄 Juntando dados...")
    
    # Verificar o que cada base está retornando
    print("\n📊 Estrutura das bases:")
    print(f"   Votos: {votos.columns.tolist()}")
    if idh is not None:
        print(f"   IDH: {idh.columns.tolist()}")
    if populacao is not None:
        print(f"   População: {populacao.columns.tolist()}")
    if emendas is not None:
        print(f"   Emendas: {emendas.columns.tolist()}")
    
    # Começar com os votos como base
    base = votos.copy()
    print(f"\n📍 Base inicial: {len(base)} municípios")
    
    # Merge com IDH
    if idh is not None and not idh.empty:
        base = base.merge(idh, on='nm_municipio', how='left')
        print(f"   → IDH mergeado: {base['idh'].notna().sum()} municípios")
        
        # Mostrar exemplos de municípios com IDH
        if base['idh'].notna().any():
            exemplos = base[base['idh'].notna()][['nm_municipio', 'idh']].head(3)
            print(f"      Exemplos: {exemplos.to_dict('records')}")
    else:
        base['idh'] = np.nan
    
    # Merge com População
    if populacao is not None and not populacao.empty:
        base = base.merge(populacao, on='nm_municipio', how='left')
        print(f"   → População mergeada: {base['populacao'].notna().sum()} municípios")
    else:
        base['populacao'] = np.nan
    
    # Merge com Emendas
    if emendas is not None and not emendas.empty:
        base = base.merge(emendas, on='nm_municipio', how='left')
        base['valor_emenda'] = base['valor_emenda'].fillna(0)
        emendas_mergeadas = (base['valor_emenda'] > 0).sum()
        print(f"   → Emendas mergeadas: {emendas_mergeadas} municípios")
        
        # Mostrar quais municípios receberam emendas
        if emendas_mergeadas > 0:
            com_emendas = base[base['valor_emenda'] > 0][['nm_municipio', 'valor_emenda']]
            print(f"      Municípios com emendas: {com_emendas['nm_municipio'].tolist()}")
    else:
        base['valor_emenda'] = 0
    
    # Verificar especificamente Artur Nogueira
    artur = base[base['nm_municipio'] == 'ARTUR NOGUEIRA']
    if not artur.empty:
        print(f"\n📍 Dados para ARTUR NOGUEIRA:")
        print(f"   Votos: {artur['votos_deputado'].values[0]}")
        if 'idh' in artur.columns and pd.notna(artur['idh'].values[0]):
            print(f"   IDH: {artur['idh'].values[0]:.3f}")
        if 'populacao' in artur.columns and pd.notna(artur['populacao'].values[0]):
            print(f"   População: {artur['populacao'].values[0]:,.0f}")
        print(f"   Emendas: R$ {artur['valor_emenda'].values[0]:,.2f}")
    
    print(f"\n✅ Dados consolidados: {len(base)} municípios")
    print(f"   → {base['idh'].notna().sum()} com IDH")
    print(f"   → {base['populacao'].notna().sum()} com população")
    print(f"   → {(base['valor_emenda'] > 0).sum()} com emendas")
    
    return base
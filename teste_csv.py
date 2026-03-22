import pandas as pd

# Carregue seu resultado
df = pd.read_csv("dados/resultado_analise.csv")

# Verifique estatísticas do IDH
print("📊 ESTATÍSTICAS DO IDH NO SEU CSV:")
print(f"Mínimo: {df['idh'].min()}")
print(f"Máximo: {df['idh'].max()}")
print(f"Média: {df['idh'].mean():.3f}")
print(f"Mediana: {df['idh'].median():.3f}")

# Mostre exemplos de cada extremo
print("\n🔍 EXEMPLOS:")
print("5 menores IDH:")
print(df.nsmallest(5, 'idh')[['nm_municipio', 'idh']])
print("\n5 maiores IDH:")
print(df.nlargest(5, 'idh')[['nm_municipio', 'idh']])
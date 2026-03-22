# TNA5373

Projeto de análise exploratória sobre a relação entre votação municipal e emendas parlamentares do deputado estadual Guilherme Cortez no estado de São Paulo.

O pipeline consolida bases de votação, emendas, IDH e população municipal para testar três hipóteses principais:

- municípios com menor IDH recebem mais emendas;
- municípios com mais votos absolutos recebem mais emendas;
- municípios com maior votação per capita recebem mais emendas.

## Estrutura do projeto

```text
.
├── main.py
├── aquisicao.py
├── visualizacao.py
├── busca_api.py
├── analise_emendas_apresentacao_final.ipynb
└── dados/
```

Arquivos principais:

- `main.py`: ponto de entrada da análise, estatísticas descritivas, testes de hipótese, correlações e regressão logística.
- `aquisicao.py`: carga, limpeza, padronização e junção das bases.
- `visualizacao.py`: gráficos exploratórios comparando votos, emendas, IDH e medidas per capita.
- `busca_api.py`: testes isolados de acesso à API do Portal da Transparência.
- `analise_emendas_apresentacao_final.ipynb`: notebook usado para apresentação e exploração interativa.

## Bases de dados

A pasta `dados/` contém as bases usadas no projeto:

- `votacao_candidato_munzona_2022_SP.csv`
- `EmendasParlamentares.csv`
- `IDH_municipio.xlsx`
- `tab_Municipios_TCU.xls`
- `RELATORIO_DTB_BRASIL_2024_MUNICIPIOS.xls`
- `resultado_analise.csv`

Observação importante:

- `dados/votacao_candidato_munzona_2022_SP.csv` é grande e está versionado com Git LFS.

## Requisitos

O projeto foi escrito em Python e usa principalmente:

- `pandas`
- `numpy`
- `statsmodels`
- `matplotlib`
- `seaborn`
- `openpyxl`
- `xlrd`
- `requests`

Exemplo de instalação em ambiente virtual:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install pandas numpy statsmodels matplotlib seaborn openpyxl xlrd requests
```

## Como executar

Para rodar a análise principal:

```bash
python main.py
```

O script:

- carrega e padroniza as bases;
- junta os dados por município;
- calcula métricas absolutas e per capita;
- imprime estatísticas descritivas;
- testa as hipóteses do projeto;
- gera gráficos exploratórios;
- estima uma regressão logística simples para probabilidade de receber emenda.

## Notebook

Para exploração interativa:

```bash
jupyter notebook analise_emendas_apresentacao_final.ipynb
```

## API do Portal da Transparência

O arquivo `busca_api.py` depende de uma chave da API do Portal da Transparência.

Defina a variável de ambiente antes de executar:

```bash
export PORTAL_TRANSPARENCIA_TOKEN="sua_chave_aqui"
python busca_api.py
```

## Clonando o repositório

Como o projeto usa Git LFS, depois do clone execute:

```bash
git lfs install
git lfs pull
```

## Limitações atuais

- o projeto está parametrizado para o estado de São Paulo;
- o candidato-alvo está definido diretamente em `aquisicao.py`;
- parte do código imprime mensagens de depuração no terminal;
- ainda não há arquivo `requirements.txt` nem suíte de testes automatizados.

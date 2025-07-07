# Análise de Performance de Transporte (Dashboard Streamlit)

-----

## 🚚 Visão Geral do Projeto

Este projeto consiste em um dashboard interativo desenvolvido com **Streamlit** para analisar a performance de operações de transporte. Utilizando dados de entregas simuladas, o dashboard oferece uma visão clara e detalhada de Key Performance Indicators (KPIs) essenciais, como OTIF (On-Time In-Full), custo médio, distância média e percentual de atrasos. Além disso, fornece visualizações gráficas da evolução mensal do OTIF, atrasos por transportadora, distribuição de prazos de entrega e um mapa interativo das entregas.

### Recursos Principais:

  * **KPIs em Destaque:** Visualização rápida dos principais indicadores de performance.
  * **Filtros Interativos:** Capacidade de filtrar dados por Unidade Federativa (UF).
  * **Análises Gráficas:**
      * Evolução Mensal do OTIF.
      * Atrasos por Transportadora.
      * Gráficos de dispersão e barras para entender custo, distância e status.
      * Distribuição de Prazos de Entrega.
      * Proporção de Entregas OK vs. Atrasadas.
      * Número de Pedidos por Cidade.
  * **Mapa Interativo de Entregas:** Visualização das entregas no mapa, coloridas por status (OK/Atrasada), utilizando geocodificação.
  * **Insights Gerenciais:** Recomendações baseadas nos dados para auxiliar na tomada de decisão.

-----

## 🛠️ Tecnologias Utilizadas

  * **Python 3.x**
  * **Streamlit:** Para a construção do dashboard interativo.
  * **Pandas:** Para manipulação e análise de dados.
  * **Plotly Express:** Para gráficos interativos (OTIF mensal, Atrasos por Transportadora, Mapa).
  * **Matplotlib & Seaborn:** Para gráficos estáticos detalhados.
  * **geopy:** Para geocodificação de endereços (conversão de cidades em coordenadas geográficas).

-----

## 🚀 Como Executar o Projeto Localmente

Siga estes passos para ter o dashboard rodando na sua máquina:

1.  **Pré-requisitos:**

      * Certifique-se de ter o Python 3.x instalado.
      * Tenha o arquivo de dados `entregas_simuladas.csv` na mesma pasta do script Python.

2.  **Instalação das Dependências:**
    Abra seu terminal ou prompt de comando e execute:

    ```bash
    pip install streamlit pandas plotly-express matplotlib seaborn geopandas geopy
    ```

      * Se `geopandas` ou suas dependências causarem problemas na instalação, você pode tentar `pip install fiona shapely pyproj rtree` primeiro e depois `pip install geopandas`. Em alguns sistemas, `geopandas` pode exigir mais configurações.

3.  **Salvar o Código:**
    Copie todo o código-fonte do dashboard (o código `dashboard_analise.py` que foi fornecido na nossa última interação) e salve-o em um arquivo chamado `dashboard_analise.py` na pasta do seu projeto (ex: `C:\Projetos_data_science\Analise_logistica`).

4.  **Executar o Dashboard:**
    No seu terminal ou prompt de comando, navegue até o diretório onde você salvou o arquivo `dashboard_analise.py`:

    ```bash
    cd C:\Projetos_data_science\Analise_logistica
    ```

    Em seguida, execute o comando:

    ```bash
    streamlit run dashboard_analise.py
    ```

    O Streamlit abrirá automaticamente o dashboard no seu navegador padrão (geralmente em `http://localhost:8501`).

-----

## 📊 KPIs e Fórmulas

Este projeto calcula e exibe diversos KPIs (Key Performance Indicators) para avaliar a performance de entregas:

1.  **OTIF (On-Time In-Full):**

      * **Definição:** Percentual de entregas realizadas no prazo e completas. No seu contexto, "In-Full" é representado pela coluna `Entrega_OK` sendo 'Sim'.
      * **Fórmula:**
        $$\text{OTIF} = \left( \frac{\text{Número de Entregas OK}}{\text{Total de Entregas}} \right) \times 100$$
      * **No Código:** `otif = (df['Entrega_OK'] == True).mean() * 100`

2.  **Percentual de Entregas com Atraso:**

      * **Definição:** Percentual de entregas que não foram realizadas no prazo (consideradas "Não OK").
      * **Fórmula:**
        $$\text{Atraso Percentual} = \left( \frac{\text{Número de Entregas Atrasadas}}{\text{Total de Entregas}} \right) \times 100$$
      * **No Código:** `atraso_percentual = (df['Entrega_OK'] == False).mean() * 100`

3.  **Custo Médio (R$):**

      * **Definição:** O custo financeiro médio por entrega.
      * **Fórmula:**
        $$\text{Custo Médio} = \frac{\sum \text{Custo de Cada Entrega}}{\text{Total de Entregas}}$$
      * **No Código:** `custo_medio = df['Custo_R$'].mean()`

4.  **Distância Média (km):**

      * **Definição:** A distância percorrida em média por entrega.
      * **Fórmula:**
        $$\text{Distância Média} = \frac{\sum \text{Distância de Cada Entrega}}{\text{Total de Entregas}}$$
      * **No Código:** `kms_medio = df['Distancia_km'].mean()`

5.  **Prazo de Entrega (Dias):**

      * **Definição:** A diferença em dias entre a data do pedido e a data da entrega.
      * **Fórmula:**
        $$\text{Prazo de Entrega (Dias)} = \text{Data de Entrega} - \text{Data do Pedido}$$
      * **No Código:** `df['Prazo_Entrega_Dias'] = (df['Data_Entrega'] - df['Data_Pedido']).dt.days`

6.  **Custo por KM Individual:**

      * **Definição:** O custo de cada entrega dividido pela distância percorrida por aquela entrega. Usado para análises de eficiência.
      * **Fórmula:**
        $$\text{Custo por KM Individual} = \frac{\text{Custo da Entrega}}{\text{Distância da Entrega (km)}}$$
      * **No Código:** `df_filt['Custo_por_KM_Individual'] = df_filt['Custo_R$'] / df_filt['Distancia_km']`

-----

## 📁 Estrutura do Repositório (Exemplo)

```
Analise_logistica/
├── dashboard_analise.py       # O código-fonte do seu dashboard Streamlit
├── entregas_simuladas.csv     # O arquivo de dados de entrada
└── README.md                  # Este arquivo de documentação
```

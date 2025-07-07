import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
import geopandas as gpd

st.set_page_config(layout="wide")
st.title("Análise de Performance de Transporte")

@st.cache_data
def load_and_process_data(file_path):
    df = pd.read_csv(file_path, encoding='latin1', sep=';')

    df.rename(columns={
        'Data Pedido': 'Data_Pedido',
        'Data Entrega': 'Data_Entrega',
        'Entrega OK': 'Entrega_OK',
        'Custo R$': 'Custo_R$',
        'Distancia km': 'Distancia_km',
        'EntregaDK': 'Entrega_DK'
    }, inplace=True)

    df['Data_Pedido'] = pd.to_datetime(df['Data_Pedido'], errors='coerce', format='%d/%m/%Y')
    df['Data_Entrega'] = pd.to_datetime(df['Data_Entrega'], errors='coerce', format='%d/%m/%Y')

    df['Entrega_OK'] = df['Entrega_OK'].map({'Sim': True, 'Não': False, 'Nao': False})
    if 'Entrega_DK' in df.columns:
        df['Entrega_DK'] = df['Entrega_DK'].map({'Sim': True, 'Não': False, 'Nao': False})

    df['Prazo_Entrega_Dias'] = (df['Data_Entrega'] - df['Data_Pedido']).dt.days

    hoje = pd.Timestamp('2024-07-01')
    df['LeadTime'] = (hoje - df['Data_Pedido']).dt.days

    return df

df = load_and_process_data('entregas_simuladas.csv')

expected_columns = ['Entrega_OK', 'Custo_R$', 'Distancia_km', 'UF', 'Transportadora', 'Cidade', 'Data_Entrega', 'Data_Pedido', 'Prazo_Entrega_Dias']
missing_columns = [col for col in expected_columns if col not in df.columns]

if missing_columns:
    st.error(f"Erro: As seguintes colunas essenciais não foram encontradas no arquivo CSV ou após o processamento: **{', '.join(missing_columns)}**. Por favor, verifique o arquivo `entregas_simuladas.csv` e ajuste a seção de renomeação de colunas no código (`df.rename(columns=...)`).")
    st.stop()

otif = round((df['Entrega_OK'] == True).mean() * 100, 2)
atraso_percentual = round((df['Entrega_OK'] == False).mean() * 100, 2)
custo_medio = round(df['Custo_R$'].mean(), 2)
kms_medio = round(df['Distancia_km'].mean(), 1)

st.subheader("Indicadores Chave de Performance (KPIs)")
col1, col2, col3, col4 = st.columns(4)
col1.metric("OTIF (%)", f"{otif}%")
col2.metric("Custo Médio (R$)", f"R$ {custo_medio}")
col3.metric("Distância Média (km)", f"{kms_medio} km")
col4.metric("% Entregas com Atraso", f"{atraso_percentual}%")

st.markdown("---")

st.subheader("Filtros")
ufs = st.multiselect(
    "Filtrar por UF",
    options=df['UF'].unique(),
    default=list(df['UF'].unique())
)
df_filt = df[df['UF'].isin(ufs)].copy()

st.markdown("---")

st.subheader("Evolução Mensal do OTIF")
if not df_filt.empty:
    df_filt['Mes'] = df_filt['Data_Entrega'].dt.to_period('M').astype(str)
    otif_mes = df_filt.groupby('Mes')['Entrega_OK'].apply(lambda x: (x == True).mean() * 100).reset_index(name='OTIF')
    otif_mes['Mes_Ordenado'] = pd.to_datetime(otif_mes['Mes']).dt.to_period('M')
    otif_mes = otif_mes.sort_values('Mes_Ordenado')

    fig_otif = px.line(otif_mes, x='Mes', y='OTIF', title='Evolução Mensal do OTIF')
    fig_otif.update_layout(xaxis_title="Mês", yaxis_title="OTIF (%)")
    st.plotly_chart(fig_otif, use_container_width=True)
else:
    st.info("Nenhum dado filtrado para mostrar a evolução mensal do OTIF. Tente ajustar os filtros.")

st.markdown("---")

st.subheader("Atrasos por Transportadora")
if not df_filt.empty:
    atrasos = df_filt[df_filt['Entrega_OK'] == False].groupby('Transportadora').size().reset_index(name='Atrasos')
    if not atrasos.empty:
        fig_atraso = px.bar(atrasos, x='Transportadora', y='Atrasos', title='Atrasos por Transportadora', text='Atrasos')
        fig_atraso.update_traces(textposition='outside')
        fig_atraso.update_layout(xaxis_title="Transportadora", yaxis_title="Número de Atrasos")
        st.plotly_chart(fig_atraso, use_container_width=True)
    else:
        st.info("Não há entregas atrasadas registradas para as UFs selecionadas.")
else:
    st.info("Nenhum dado filtrado para mostrar atrasos por transportadora. Tente ajustar os filtros.")

st.markdown("---")

st.subheader("Visualizações Detalhadas")

plt.rcParams.update({'font.size': 10})

if not df_filt.empty:
    st.write("### Taxa de Sucesso das Entregas por Transportadora")
    fig1, ax1 = plt.subplots(figsize=(10, 6))
    taxa_sucesso_transportadora = df_filt.groupby('Transportadora')['Entrega_OK'].mean() * 100
    sns.barplot(x=taxa_sucesso_transportadora.index, y=taxa_sucesso_transportadora.values, palette='viridis', ax=ax1)
    ax1.set_title('Taxa de Sucesso das Entregas por Transportadora (%)')
    ax1.set_xlabel('Transportadora')
    ax1.set_ylabel('Taxa de Sucesso (%)')
    ax1.set_ylim(0, 100)
    for index, value in enumerate(taxa_sucesso_transportadora.values):
        ax1.text(index, value + 2, f'{value:.2f}%', ha='center', va='bottom')
    plt.tight_layout()
    st.pyplot(fig1)
    plt.close(fig1)

    st.write("### Custo vs. Distância por Status de Entrega e Transportadora")
    fig2, ax2 = plt.subplots(figsize=(10, 7))
    sns.scatterplot(
        data=df_filt,
        x='Distancia_km',
        y='Custo_R$',
        hue='Entrega_OK',
        style='Transportadora',
        size='Prazo_Entrega_Dias',
        sizes=(50, 400),
        palette={True: '#4CAF50', False: '#FF6347'},
        alpha=0.8,
        ax=ax2
    )
    ax2.set_title('Custo vs. Distância por Status de Entrega e Transportadora')
    ax2.set_xlabel('Distância (km)')
    ax2.set_ylabel('Custo (R$)')
    ax2.grid(True, linestyle='--', alpha=0.6)
    handles, labels = ax2.get_legend_handles_labels()
    new_labels = []
    for label in labels:
        if label == 'True':
            new_labels.append('Entrega OK')
        elif label == 'False':
            new_labels.append('Entrega Atrasada')
        else:
            new_labels.append(label)
    ax2.legend(handles, new_labels, title='Legenda', bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    st.pyplot(fig2)
    plt.close(fig2)

    st.write("### Custo Médio por KM por Transportadora e Status de Entrega")
    fig3, ax3 = plt.subplots(figsize=(12, 7))
    df_filt['Custo_por_KM_Individual'] = df_filt['Custo_R$'] / df_filt['Distancia_km']
    df_temp = df_filt.dropna(subset=['Custo_por_KM_Individual']).copy()

    sns.barplot(
        data=df_temp,
        x='Transportadora',
        y='Custo_por_KM_Individual',
        hue='Entrega_OK',
        palette={True: '#A2D9CE', False: '#F7CAC9'},
        errorbar=None,
        ax=ax3
    )
    ax3.set_title('Custo Médio por KM por Transportadora e Status de Entrega')
    ax3.set_xlabel('Transportadora')
    ax3.set_ylabel('Custo Médio por KM (R$/km)')
    handles, labels = ax3.get_legend_handles_labels()
    new_labels_bar = []
    for label in labels:
        if label == 'True':
            new_labels_bar.append('Entrega OK')
        elif label == 'False':
            new_labels_bar.append('Entrega Atrasada')
        else:
            new_labels_bar.append(label)
    ax3.legend(handles, new_labels_bar, title='Entrega OK', loc='upper right')
    plt.tight_layout()
    st.pyplot(fig3)
    plt.close(fig3)

    st.write("### Distribuição dos Prazos de Entrega")
    fig4, ax4 = plt.subplots(figsize=(10, 6))
    sns.histplot(df_filt['Prazo_Entrega_Dias'], bins=range(0, int(df_filt['Prazo_Entrega_Dias'].max()) + 2), kde=True, color='skyblue', ax=ax4)
    ax4.set_title('Distribuição dos Prazos de Entrega (Dias)')
    ax4.set_xlabel('Prazo de Entrega (Dias)')
    ax4.set_ylabel('Frequência')
    ax4.set_xticks(range(0, int(df_filt['Prazo_Entrega_Dias'].max()) + 2, 1))
    ax4.grid(True, linestyle='--', alpha=0.6)
    plt.tight_layout()
    st.pyplot(fig4)
    plt.close(fig4)

    st.write("### Proporção de Entregas por Status")

    df_filt['Status_Entrega_Label'] = df_filt['Entrega_OK'].map({True: 'Entrega OK', False: 'Entrega Atrasada'})

    status_proporcao = df_filt['Status_Entrega_Label'].value_counts(normalize=True).reset_index()
    status_proporcao.columns = ['Status', 'Proporcao']

    status_proporcao['Status'] = pd.Categorical(status_proporcao['Status'],
                                                 categories=['Entrega OK', 'Entrega Atrasada'],
                                                 ordered=True)
    status_proporcao = status_proporcao.sort_values('Status')

    status_proporcao['Categoria'] = 'Total'

    fig_bar_prop = px.bar(
        status_proporcao,
        x='Categoria',
        y='Proporcao',
        color='Status',
        title='Proporção Total de Entregas por Status',
        labels={'Proporcao': 'Proporção'},
        color_discrete_map={'Entrega OK': '#4CAF50', 'Entrega Atrasada': '#FF6347'},
        text_auto='.1%'
    )
    fig_bar_prop.update_layout(
        yaxis_tickformat='.0%',
        xaxis_title="",
        yaxis_title="Proporção"
    )
    fig_bar_prop.update_traces(textposition='outside')
    st.plotly_chart(fig_bar_prop, use_container_width=True)

    df_filt.drop(columns=['Status_Entrega_Label'], inplace=True)

else:
    st.info("Nenhum dado filtrado para mostrar as análises detalhadas. Tente ajustar os filtros.")

st.markdown("---")

st.subheader("Mapa de Entregas")
@st.cache_data
def geocodificar_cidades(df_input):
    geolocator = Nominatim(user_agent="streamlit_geoapp_transporte_logistica")
    geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)

    if 'Cidade' not in df_input.columns or 'UF' not in df_input.columns:
        return pd.DataFrame()

    cidades = df_input[['Cidade', 'UF']].drop_duplicates().copy()
    cidades['Endereco'] = cidades['Cidade'] + ', ' + cidades['UF'] + ', Brasil'
    
    progress_text = "Geocodificando cidades, por favor aguarde..."
    my_bar = st.progress(0, text=progress_text)
    total_cidades = len(cidades)
    
    locations = []
    for i, row in enumerate(cidades.iterrows(), start=1):
        try:
            loc = geocode(row[1]['Endereco'], addressdetails=True, timeout=5)
            locations.append(loc)
        except Exception as e:
            locations.append(None)
        
        progress_value = min(1.0, i / total_cidades)
        my_bar.progress(progress_value, text=progress_text)
        
    my_bar.empty()

    cidades['Localizacao'] = locations
    cidades['Latitude'] = cidades['Localizacao'].apply(lambda loc: loc.latitude if loc else None)
    cidades['Longitude'] = cidades['Localizacao'].apply(lambda loc: loc.longitude if loc else None)
    return cidades.drop(columns=['Localizacao'], errors='ignore')


if not df_filt.empty and 'Cidade' in df_filt.columns and 'UF' in df_filt.columns and 'Entrega_OK' in df_filt.columns:
    with st.spinner("Preparando mapa..."):
        locais = geocodificar_cidades(df_filt)

    if not locais.empty and 'Latitude' in locais.columns and 'Longitude' in locais.columns:
        df_mapa = df_filt.merge(locais, on=['Cidade', 'UF'], how='left')
        df_mapa.dropna(subset=['Latitude', 'Longitude'], inplace=True)

        if not df_mapa.empty:
            fig_mapa = px.scatter_mapbox(df_mapa,
                                         lat='Latitude', lon='Longitude',
                                         hover_name='Cidade',
                                         color='Entrega_OK',
                                         color_discrete_map={True: '#4CAF50', False: '#FF6347'},
                                         zoom=4, height=500,
                                         mapbox_style='carto-positron',
                                         title="Mapa de Entregas por Status")
            st.plotly_chart(fig_mapa, use_container_width=True)
        else:
            st.warning("Nenhuma localização válida para exibir no mapa após a filtragem e geocodificação. Tente ajustar os filtros ou verificar as cidades.")
    else:
        st.warning("Nenhum dado de localização disponível para o mapa. Verifique se as cidades foram geocodificadas corretamente ou se há dados após os filtros.")
else:
    st.info("Selecione UFs e verifique se as colunas 'Cidade', 'UF' e 'Entrega_OK' estão presentes para ver o mapa de entregas. O DataFrame filtrado está vazio.")

st.markdown("---")

st.subheader("Insights para Tomada de Decisão")

st.markdown("""
- **Transportadoras com mais atrasos** podem estar impactando o OTIF geral. Analise seus processos e termos contratuais.
- **UFs com menor desempenho** podem justificar uma revisão da malha logística ou a alocação de recursos adicionais.
- O **custo médio elevado** pode indicar a necessidade de renegociação de fretes ou otimização de rotas.
- **Rotas com alta ocorrência de atrasos** devem ser reavaliadas, considerando condições de tráfego, infraestrutura ou capacidade da transportadora.
""")

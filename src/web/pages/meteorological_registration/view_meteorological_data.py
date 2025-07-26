"""
Subpágina para visualização de dados meteorológicos

Esta página permite visualizar e filtrar dados meteorológicos salvos:
- Seleção de cidade para visualização
- Exibição dos dados em formato tabular
- Filtros por período e altura
- Ordenação e busca
"""

import streamlit as st
import sys
from pathlib import Path
from datetime import datetime, date, timedelta
import pandas as pd

# Adicionar src ao path para imports
src_path = Path(__file__).parent.parent.parent.parent / "src"
sys.path.insert(0, str(src_path))

from meteorological.meteorological_data.entity import MeteorologicalData
from meteorological.meteorological_data.repository import MeteorologicalDataRepository
from meteorological.meteorological_data_source.repository import MeteorologicalDataSourceRepository
from geographic import CidadeRepository, RegiaoRepository, PaisRepository


def formatar_cidade_display(cidade, regiao_nome, pais_codigo):
    """
    Formatar cidade para exibição no selectbox
    """
    regiao_display = f" - {regiao_nome}" if regiao_nome else ""
    return f"{cidade.nome}{regiao_display} - {pais_codigo} - lat: {cidade.latitude:.4f} - lon: {cidade.longitude:.4f}"


def obter_cidades_com_dados():
    """
    Busca todas as cidades que possuem dados meteorológicos
    """
    try:
        repo_dados = MeteorologicalDataRepository()
        cidade_repo = CidadeRepository()
        regiao_repo = RegiaoRepository()
        pais_repo = PaisRepository()
        
        # Buscar todas as cidades que têm dados meteorológicos
        cidades_com_dados = repo_dados.buscar_cidades_com_dados()
        
        if not cidades_com_dados:
            return []
        
        cidades_formatadas = []
        for cidade_id in cidades_com_dados:
            cidade = cidade_repo.buscar_por_id(cidade_id)
            if cidade:
                # Buscar nome da região e país
                regiao_nome = ""
                if cidade.regiao_id:
                    regiao = regiao_repo.buscar_por_id(cidade.regiao_id)
                    regiao_nome = regiao.nome if regiao else ""
                
                pais_codigo = ""
                if cidade.pais_id:
                    pais = pais_repo.buscar_por_id(cidade.pais_id)
                    pais_codigo = pais.codigo if pais else ""
                
                display_text = formatar_cidade_display(cidade, regiao_nome, pais_codigo)
                cidades_formatadas.append((display_text, cidade_id, cidade.nome))
        
        return sorted(cidades_formatadas, key=lambda x: x[2])  # Ordenar por nome da cidade
        
    except Exception as e:
        st.error(f"Erro ao buscar cidades: {str(e)}")
        return []


def converter_dados_para_dataframe(dados_meteorologicos, fontes_map):
    """
    Converte lista de dados meteorológicos para DataFrame do pandas
    """
    if not dados_meteorologicos:
        return pd.DataFrame()
    
    dados_lista = []
    for dado in dados_meteorologicos:
        fonte_nome = fontes_map.get(dado.meteorological_data_source_id, "Desconhecida")
        
        dados_lista.append({
            'Data/Hora': dado.data_hora.strftime('%d/%m/%Y %H:%M') if dado.data_hora else '',
            'Fonte': fonte_nome,
            'Altura (m)': dado.altura_captura,
            'Velocidade do Vento (m/s)': dado.velocidade_vento,
            'Temperatura (°C)': dado.temperatura,
            'Umidade (%)': dado.umidade
        })
    
    return pd.DataFrame(dados_lista)


def aplicar_filtros_dataframe(df, filtro_fonte, filtro_altura, data_inicio, data_fim):
    """
    Aplica filtros ao DataFrame
    """
    df_filtrado = df.copy()
    
    # Filtro por fonte
    if filtro_fonte != "Todas":
        df_filtrado = df_filtrado[df_filtrado['Fonte'] == filtro_fonte]
    
    # Filtro por altura
    if filtro_altura != "Todas":
        df_filtrado = df_filtrado[df_filtrado['Altura (m)'] == filtro_altura]
    
    # Filtro por período
    if data_inicio and data_fim:
        # Converter coluna de data para datetime para filtrar
        df_filtrado['Data_temp'] = pd.to_datetime(df_filtrado['Data/Hora'], format='%d/%m/%Y %H:%M')
        data_inicio_dt = pd.to_datetime(data_inicio)
        data_fim_dt = pd.to_datetime(data_fim) + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)
        
        df_filtrado = df_filtrado[
            (df_filtrado['Data_temp'] >= data_inicio_dt) & 
            (df_filtrado['Data_temp'] <= data_fim_dt)
        ]
        df_filtrado = df_filtrado.drop('Data_temp', axis=1)
    
    return df_filtrado


def view_meteorological_data():
    """
    Função principal da página de visualização de dados meteorológicos
    """
    # Cabeçalho da página
    st.markdown("""
    <div class="section-header">
        <h4>📊 Visualização de Dados Meteorológicos</h4>
    </div>
    """, unsafe_allow_html=True)
    
    st.info("👁️ Visualize os dados meteorológicos coletados para cada cidade cadastrada.")
    
    # Buscar cidades com dados
    cidades_com_dados = obter_cidades_com_dados()
    
    if not cidades_com_dados:
        st.warning("🔍 Nenhuma cidade com dados meteorológicos encontrada.")
        st.info("💡 **Dica:** Primeiro cadastre dados meteorológicos na aba 'Cadastrar Dados Meteorológicos'.")
        return
    
    # Seleção da cidade
    st.markdown("### 🏙️ Seleção da Cidade")
    
    opcoes_cidades = [cidade[0] for cidade in cidades_com_dados]
    cidade_selecionada = st.selectbox(
        "Escolha uma cidade:",
        opcoes_cidades,
        help="Selecione a cidade para visualizar seus dados meteorológicos"
    )
    
    if not cidade_selecionada:
        return
    
    # Encontrar o ID da cidade selecionada
    cidade_id = None
    for cidade_info in cidades_com_dados:
        if cidade_info[0] == cidade_selecionada:
            cidade_id = cidade_info[1]
            break
    
    if not cidade_id:
        st.error("Erro ao identificar a cidade selecionada.")
        return
    
    # Buscar dados da cidade
    try:
        repo_dados = MeteorologicalDataRepository()
        fonte_repo = MeteorologicalDataSourceRepository()
        
        # Buscar todos os dados da cidade
        dados_cidade = repo_dados.buscar_por_cidade(cidade_id)
        
        if not dados_cidade:
            st.warning(f"📭 Nenhum dado meteorológico encontrado para {cidade_selecionada.split(' - ')[0]}.")
            return
        
        # Buscar informações das fontes para criar mapeamento
        fontes = fonte_repo.listar_todos()
        fontes_map = {fonte.id: fonte.name for fonte in fontes}
        
        # Converter para DataFrame
        df = converter_dados_para_dataframe(dados_cidade, fontes_map)
        
        if df.empty:
            st.warning("Erro ao processar dados meteorológicos.")
            return
        
        # Seção de filtros
        st.markdown("---")
        st.markdown("### 🔧 Filtros")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            # Filtro por fonte
            fontes_unicas = ["Todas"] + sorted(df['Fonte'].unique().tolist())
            filtro_fonte = st.selectbox("Fonte de Dados:", fontes_unicas)
        
        with col2:
            # Filtro por altura
            alturas_unicas = ["Todas"] + sorted([h for h in df['Altura (m)'].unique() if pd.notna(h)])
            filtro_altura = st.selectbox("Altura (m):", alturas_unicas)
        
        with col3:
            # Filtro por data de início
            data_min = pd.to_datetime(df['Data/Hora'], format='%d/%m/%Y %H:%M').min().date()
            data_max = pd.to_datetime(df['Data/Hora'], format='%d/%m/%Y %H:%M').max().date()
            data_inicio = st.date_input("Data Início:", value=data_min, min_value=data_min, max_value=data_max)
        
        with col4:
            # Filtro por data de fim
            data_fim = st.date_input("Data Fim:", value=data_max, min_value=data_min, max_value=data_max)
        
        # Aplicar filtros
        df_filtrado = aplicar_filtros_dataframe(df, filtro_fonte, filtro_altura, data_inicio, data_fim)
        
        # Exibir estatísticas
        st.markdown("---")
        st.markdown("### 📈 Estatísticas")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total de Registros", len(df_filtrado))
        
        with col2:
            if not df_filtrado.empty and 'Velocidade do Vento (m/s)' in df_filtrado.columns:
                vel_media = df_filtrado['Velocidade do Vento (m/s)'].dropna().mean()
                st.metric("Velocidade Média do Vento", f"{vel_media:.2f} m/s" if pd.notna(vel_media) else "N/A")
        
        with col3:
            if not df_filtrado.empty and 'Temperatura (°C)' in df_filtrado.columns:
                temp_media = df_filtrado['Temperatura (°C)'].dropna().mean()
                st.metric("Temperatura Média", f"{temp_media:.1f}°C" if pd.notna(temp_media) else "N/A")
        
        with col4:
            if not df_filtrado.empty and 'Umidade (%)' in df_filtrado.columns:
                umid_media = df_filtrado['Umidade (%)'].dropna().mean()
                st.metric("Umidade Média", f"{umid_media:.1f}%" if pd.notna(umid_media) else "N/A")
        
        # Exibir tabela
        st.markdown("---")
        st.markdown("### 📋 Dados Meteorológicos")
        
        if df_filtrado.empty:
            st.warning("🔍 Nenhum dado encontrado com os filtros aplicados.")
        else:
            # Opções de exibição
            col1, col2 = st.columns([3, 1])
            with col2:
                mostrar_indices = st.checkbox("Mostrar índices", value=False)
            
            # Exibir tabela com configurações
            st.dataframe(
                df_filtrado,
                use_container_width=True,
                hide_index=not mostrar_indices,
                column_config={
                    'Data/Hora': st.column_config.TextColumn('Data/Hora', width="medium"),
                    'Fonte': st.column_config.TextColumn('Fonte', width="medium"),
                    'Altura (m)': st.column_config.NumberColumn('Altura (m)', format="%.1f"),
                    'Velocidade do Vento (m/s)': st.column_config.NumberColumn('Velocidade do Vento (m/s)', format="%.2f"),
                    'Temperatura (°C)': st.column_config.NumberColumn('Temperatura (°C)', format="%.1f"),
                    'Umidade (%)': st.column_config.NumberColumn('Umidade (%)', format="%.1f")
                }
            )
            
            # Opção de download
            if len(df_filtrado) > 0:
                csv = df_filtrado.to_csv(index=False)
                st.download_button(
                    label="📥 Baixar dados (CSV)",
                    data=csv,
                    file_name=f"dados_meteorologicos_{cidade_selecionada.split(' - ')[0]}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
    
    except Exception as e:
        st.error(f"❌ Erro ao carregar dados: {str(e)}")
        
        with st.expander("🔧 Detalhes do erro"):
            import traceback
            st.code(traceback.format_exc())

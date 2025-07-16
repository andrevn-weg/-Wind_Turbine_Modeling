"""
Página de Listagem de Localidades

Esta página permite visualizar e gerenciar todas as localidades cadastradas:
- Listar países, estados e cidades
- Visualizar localidades em mapa
- Filtrar e buscar localidades
- Editar e excluir registros
"""

import streamlit as st
import pandas as pd
import sys
from pathlib import Path
import plotly.express as px
import plotly.graph_objects as go

# Adicionar src ao path para imports
src_path = Path(__file__).parent.parent.parent / "src"
sys.path.insert(0, str(src_path))

from geographic import Pais, Regiao, Cidade
from geographic import PaisRepository, RegiaoRepository, CidadeRepository


def create_map_from_cities(cidades):
    """
    Cria um mapa interativo com as cidades fornecidas
    
    Args:
        cidades: Lista de objetos Cidade
        
    Returns:
        plotly.graph_objects.Figure: Mapa interativo
    """
    if not cidades:
        return None
    
    # Preparar dados para o mapa
    df_map = pd.DataFrame([
        {
            'cidade': cidade.nome,
            'latitude': cidade.latitude,
            'longitude': cidade.longitude,
            'populacao': cidade.populacao or 0,
            'altitude': cidade.altitude or 0,
            'id': cidade.id
        }
        for cidade in cidades
    ])
    
    # Criar mapa com plotly
    fig = px.scatter_mapbox(
        df_map,
        lat="latitude",
        lon="longitude",
        hover_name="cidade",
        hover_data={
            "populacao": ":,",
            "altitude": ":.1f",
            "latitude": ":.4f",
            "longitude": ":.4f"
        },
        size="populacao",
        size_max=20,
        zoom=6,
        height=500,
        title="Mapa de Localidades Cadastradas"
    )
    
    # Configurar o mapa
    fig.update_layout(
        mapbox_style="open-street-map",
        margin={"r": 0, "t": 50, "l": 0, "b": 0},
        showlegend=False
    )
    
    return fig


def show_statistics():
    """Exibe estatísticas resumidas do sistema"""
    st.markdown("### 📊 Estatísticas do Sistema")
    
    try:
        # Inicializar repositórios
        pais_repo = PaisRepository()
        regiao_repo = RegiaoRepository()
        cidade_repo = CidadeRepository()
        
        # Buscar dados
        paises = pais_repo.listar_todos()
        regioes = regiao_repo.listar_todos()
        cidades = cidade_repo.listar_todos()
        
        # Exibir métricas
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("🏳️ Países", len(paises))
        
        with col2:
            st.metric("🗺️ Estados/Regiões", len(regioes))
        
        with col3:
            st.metric("🏙️ Cidades", len(cidades))
        
        with col4:
            # População total (apenas cidades com dados)
            pop_total = sum(c.populacao for c in cidades if c.populacao)
            st.metric("👥 População Total", f"{pop_total:,}")
            
    except Exception as e:
        st.error(f"Erro ao carregar estatísticas: {e}")


def show_countries():
    """Exibe a lista de países"""
    st.markdown("### 🏳️ Países Cadastrados")
    
    try:
        pais_repo = PaisRepository()
        paises = pais_repo.listar_todos()
        
        if not paises:
            st.info("Nenhum país cadastrado ainda.")
            return
        
        # Criar DataFrame para exibição
        df_paises = pd.DataFrame([
            {
                'ID': pais.id,
                'Nome': pais.nome,
                'Código ISO': pais.codigo
            }
            for pais in paises
        ])
        
        # Exibir tabela
        st.dataframe(df_paises, use_container_width=True, hide_index=True)
        
        # Opções de ação
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🔄 Atualizar Lista de Países"):
                st.rerun()
        
        with col2:
            if st.button("➕ Cadastrar Novo País"):
                st.switch_page("pages/1_cadastro_localidade.py")
                
    except Exception as e:
        st.error(f"Erro ao carregar países: {e}")


def show_states():
    """Exibe a lista de estados/regiões"""
    st.markdown("### 🗺️ Estados/Regiões Cadastrados")
    
    try:
        regiao_repo = RegiaoRepository()
        pais_repo = PaisRepository()
        
        regioes = regiao_repo.listar_todos()
        paises = {p.id: p.nome for p in pais_repo.listar_todos()}
        
        if not regioes:
            st.info("Nenhum estado/região cadastrado ainda.")
            return
        
        # Criar DataFrame para exibição
        df_regioes = pd.DataFrame([
            {
                'ID': regiao.id,
                'Nome': regiao.nome,
                'País': paises.get(regiao.pais_id, 'N/A'),
                'Sigla': regiao.sigla or 'N/A'
            }
            for regiao in regioes
        ])
        
        # Filtro por país
        paises_disponiveis = ['Todos'] + [p for p in paises.values()]
        pais_selecionado = st.selectbox("Filtrar por país:", paises_disponiveis)
        
        if pais_selecionado != 'Todos':
            df_filtered = df_regioes[df_regioes['País'] == pais_selecionado]
        else:
            df_filtered = df_regioes
        
        # Exibir tabela
        st.dataframe(df_filtered, use_container_width=True, hide_index=True)
        
        # Opções de ação
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🔄 Atualizar Lista de Estados"):
                st.rerun()
        
        with col2:
            if st.button("➕ Cadastrar Novo Estado"):
                st.switch_page("pages/1_cadastro_localidade.py")
                
    except Exception as e:
        st.error(f"Erro ao carregar estados: {e}")


def show_cities():
    """Exibe a lista de cidades com mapa"""
    st.markdown("### 🏙️ Cidades Cadastradas")
    
    try:
        cidade_repo = CidadeRepository()
        regiao_repo = RegiaoRepository()
        pais_repo = PaisRepository()
        
        cidades = cidade_repo.listar_todos()
        regioes = {r.id: r.nome for r in regiao_repo.listar_todos()}
        paises = {p.id: p.nome for p in pais_repo.listar_todos()}
        
        if not cidades:
            st.info("Nenhuma cidade cadastrada ainda.")
            return
        
        # Filtros
        col1, col2 = st.columns(2)
        
        with col1:
            # Filtro por nome
            nome_filtro = st.text_input("🔍 Buscar por nome:", placeholder="Digite o nome da cidade...")
        
        with col2:
            # Filtro por estado
            regioes_disponiveis = ['Todos'] + [r for r in regioes.values()]
            regiao_selecionada = st.selectbox("Filtrar por estado:", regioes_disponiveis)
        
        # Aplicar filtros
        cidades_filtradas = cidades
        
        if nome_filtro:
            cidades_filtradas = [c for c in cidades_filtradas 
                               if nome_filtro.lower() in c.nome.lower()]
        
        if regiao_selecionada != 'Todos':
            regiao_id = next((k for k, v in regioes.items() if v == regiao_selecionada), None)
            if regiao_id:
                cidades_filtradas = [c for c in cidades_filtradas 
                                   if c.regiao_id == regiao_id]
        
        # Exibir mapa se houver cidades
        if cidades_filtradas:
            st.markdown("#### 🗺️ Mapa das Localidades")
            
            mapa = create_map_from_cities(cidades_filtradas)
            if mapa:
                st.plotly_chart(mapa, use_container_width=True)
            else:
                st.warning("Não foi possível gerar o mapa.")
        
        # Criar DataFrame para exibição
        if cidades_filtradas:
            df_cidades = pd.DataFrame([
                {
                    'ID': cidade.id,
                    'Nome': cidade.nome,
                    'Estado': regioes.get(cidade.regiao_id, 'N/A'),
                    'País': paises.get(cidade.pais_id, 'N/A'),
                    'Latitude': f"{cidade.latitude:.4f}",
                    'Longitude': f"{cidade.longitude:.4f}",
                    'População': f"{cidade.populacao:,}" if cidade.populacao else 'N/A',
                    'Altitude (m)': f"{cidade.altitude:.1f}" if cidade.altitude else 'N/A'
                }
                for cidade in cidades_filtradas
            ])
            
            st.markdown(f"#### 📋 Lista de Cidades ({len(cidades_filtradas)} encontradas)")
            st.dataframe(df_cidades, use_container_width=True, hide_index=True)
            
        else:
            st.warning("Nenhuma cidade encontrada com os filtros aplicados.")
        
        # Opções de ação
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🔄 Atualizar Lista"):
                st.rerun()
        
        with col2:
            if st.button("➕ Cadastrar Nova Cidade"):
                st.switch_page("pages/1_cadastro_localidade.py")
        
        with col3:
            if st.button("🌍 Ver Todas no Mapa"):
                # Mostrar mapa com todas as cidades
                if cidades:
                    mapa_completo = create_map_from_cities(cidades)
                    if mapa_completo:
                        st.plotly_chart(mapa_completo, use_container_width=True)
                
    except Exception as e:
        st.error(f"Erro ao carregar cidades: {e}")


def show_detailed_view():
    """Exibe visualização detalhada de uma localidade específica"""
    st.markdown("### 🔍 Visualização Detalhada")
    
    try:
        cidade_repo = CidadeRepository()
        cidades = cidade_repo.listar_todos()
        
        if not cidades:
            st.info("Nenhuma cidade cadastrada para visualização detalhada.")
            return
        
        # Seletor de cidade
        nomes_cidades = [f"{c.nome} (ID: {c.id})" for c in cidades]
        cidade_selecionada = st.selectbox("Selecione uma cidade para ver detalhes:", nomes_cidades)
        
        if cidade_selecionada:
            # Extrair ID da cidade
            cidade_id = int(cidade_selecionada.split("ID: ")[1].split(")")[0])
            cidade = next(c for c in cidades if c.id == cidade_id)
            
            # Buscar dados relacionados
            regiao_repo = RegiaoRepository()
            pais_repo = PaisRepository()
            
            regiao = regiao_repo.buscar_por_id(cidade.regiao_id) if cidade.regiao_id else None
            pais = pais_repo.buscar_por_id(cidade.pais_id) if cidade.pais_id else None
            
            # Exibir informações em colunas
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### 📍 Informações Básicas")
                st.write(f"**Nome:** {cidade.nome}")
                st.write(f"**ID:** {cidade.id}")
                st.write(f"**Estado:** {regiao.nome if regiao else 'N/A'}")
                st.write(f"**País:** {pais.nome if pais else 'N/A'}")
                
                st.markdown("#### 🌍 Coordenadas")
                st.write(f"**Latitude:** {cidade.latitude:.6f}")
                st.write(f"**Longitude:** {cidade.longitude:.6f}")
                
            with col2:
                st.markdown("#### 📊 Dados Demográficos")
                st.write(f"**População:** {cidade.populacao:,}" if cidade.populacao else "**População:** N/A")
                st.write(f"**Altitude:** {cidade.altitude:.1f} metros" if cidade.altitude else "**Altitude:** N/A")
                
                if cidade.notes:
                    st.markdown("#### 📝 Observações")
                    st.write(cidade.notes)
            
            # Mapa individual
            st.markdown("#### 🗺️ Localização no Mapa")
            mapa_individual = create_map_from_cities([cidade])
            if mapa_individual:
                st.plotly_chart(mapa_individual, use_container_width=True)
            
            # Cidades próximas
            st.markdown("#### 🏘️ Cidades Próximas")
            try:
                cidades_proximas = cidade_repo.buscar_proximas(
                    cidade.latitude, 
                    cidade.longitude, 
                    raio_km=100
                )
                # Remover a própria cidade da lista
                cidades_proximas = [c for c in cidades_proximas if c.id != cidade.id]
                
                if cidades_proximas:
                    for c in cidades_proximas[:5]:  # Mostrar até 5 cidades próximas
                        distancia = cidade.distancia_aproximada(c)
                        st.write(f"• **{c.nome}** - {distancia:.1f} km de distância")
                else:
                    st.info("Nenhuma cidade cadastrada próxima encontrada em um raio de 100 km.")
                    
            except Exception as e:
                st.warning(f"Erro ao buscar cidades próximas: {e}")
                
    except Exception as e:
        st.error(f"Erro na visualização detalhada: {e}")


def main():
    """Função principal da página"""
    
    # Título principal
    st.title("📋 Listar Localidades")
    st.markdown("Visualize e gerencie todas as localidades cadastradas no sistema")
    
    # Sidebar com opções
    st.sidebar.header("🛠️ Opções de Visualização")
    
    # Seletor de modo de visualização
    modo_visualizacao = st.sidebar.radio(
        "Escolha o que visualizar:",
        [
            "🔍 Visualização Detalhada",
            "📊 Estatísticas Gerais",
            "🏳️ Países",
            "🗺️ Estados/Regiões", 
            "🏙️ Cidades com Mapa"
            
        ]
    )
    
    # Informações no sidebar
    st.sidebar.markdown("---")
    st.sidebar.info("""
    **💡 Dicas:**
    
    • **Estatísticas:** Visão geral do sistema
    • **Países:** Lista todos os países cadastrados
    • **Estados:** Lista estados/regiões por país
    • **Cidades:** Lista com mapa interativo
    • **Detalhada:** Informações completas de uma cidade
    """)
    
    # Renderizar a visualização selecionada
    try:
        if modo_visualizacao == "📊 Estatísticas Gerais":
            show_statistics()
            
        elif modo_visualizacao == "🏳️ Países":
            show_countries()
            
        elif modo_visualizacao == "🗺️ Estados/Regiões":
            show_states()
            
        elif modo_visualizacao == "🏙️ Cidades com Mapa":
            show_cities()
            
        elif modo_visualizacao == "🔍 Visualização Detalhada":
            show_detailed_view()
            
    except Exception as e:
        st.error(f"❌ Erro ao carregar visualização: {str(e)}")
        
        with st.expander("🔧 Detalhes do erro"):
            import traceback
            st.code(traceback.format_exc())
    
    # Rodapé
    st.sidebar.markdown("---")
    st.sidebar.success("✅ Sistema de listagem ativo!")
    
    # Links rápidos
    st.sidebar.markdown("### 🔗 Links Rápidos")
    if st.sidebar.button("➕ Cadastrar Nova Localidade"):
        st.switch_page("pages/1_cadastro_localidade.py")


if __name__ == "__main__":
    main()
else:
    main()

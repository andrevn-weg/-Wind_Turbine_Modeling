"""
Subpágina para cadastro de dados meteorológicos

Esta página permite coletar e cadastrar dados meteorológicos das APIs:
- NASA POWER (alturas: 10m, 50m)
- Open-Meteo (alturas: 10m, 80m, 120m, 180m)

Inclui validação para evitar dados duplicados.
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
from meteorological.api.nasa_power import NASAPowerClient
from meteorological.api.open_meteo import OpenMeteoClient
from geographic import CidadeRepository, RegiaoRepository, PaisRepository


def verificar_dados_existentes(repo, cidade_id, fonte_id, data_inicio, data_fim, altura):
    """
    Verifica se já existem dados para os parâmetros fornecidos
    
    Returns:
        bool: True se existem dados duplicados
    """
    try:
        # Buscar dados existentes para o período usando o método correto
        dados_existentes = repo.buscar_por_periodo(
            data_inicio, data_fim, cidade_id
        )
        
        # Verificar se algum dado corresponde à fonte e altura
        for dado in dados_existentes:
            if (dado.meteorological_data_source_id == fonte_id and 
                dado.altura_captura == altura):
                return True
        
        return False
        
    except Exception:
        # Em caso de erro, assumir que não há duplicatas
        return False


def formatar_cidade_display(cidade, regiao_nome, pais_codigo):
    """
    Formatar cidade para exibição no selectbox
    """
    regiao_display = f" - {regiao_nome}" if regiao_nome else ""
    return f"{cidade.nome}{regiao_display} - {pais_codigo} - lat: {cidade.latitude:.4f} - lon: {cidade.longitude:.4f}"


def processar_coleta_dados(api_client, latitude, longitude, data_inicio, data_fim, alturas_selecionadas, fonte_id, cidade_id, repo):
    """
    Processa a coleta de dados da API e salva no banco
    """
    dados_salvos = 0
    erros = []
    
    for altura in alturas_selecionadas:
        try:
            # Verificar duplicatas antes de coletar
            if verificar_dados_existentes(repo, cidade_id, fonte_id, data_inicio, data_fim, altura):
                erros.append(f"Dados para altura {altura}m já existem no período selecionado")
                continue
            
            # Coletar dados da API
            st.info(f"🔄 Coletando dados para altura {altura}m...")
            
            dados_api = api_client.obter_dados_historicos_vento(
                latitude=latitude,
                longitude=longitude,
                data_inicio=data_inicio,
                data_fim=data_fim,
                alturas=[altura]
            )
            
            if not dados_api or 'dados' not in dados_api:
                erros.append(f"Nenhum dado retornado para altura {altura}m")
                continue
            
            # Processar e salvar cada registro
            for registro in dados_api['dados']:
                try:
                    # Converter data se necessário - agora esperamos datetime
                    if isinstance(registro['data_hora'], str):
                        data_hora_registro = datetime.fromisoformat(registro['data_hora'])
                    elif isinstance(registro['data_hora'], datetime):
                        data_hora_registro = registro['data_hora']
                    else:
                        # Fallback - se ainda for date, converter para datetime
                        data_hora_registro = datetime.combine(registro['data_hora'], datetime.min.time())
                    
                    # Usar altura do registro (pode ser diferente da altura solicitada)
                    altura_registro = registro.get('altura_captura', altura)
                    
                    # Criar objeto MeteorologicalData
                    dado_meteorologico = MeteorologicalData(
                        cidade_id=cidade_id,
                        meteorological_data_source_id=fonte_id,
                        data_hora=data_hora_registro,
                        temperatura=registro.get('temperatura'),
                        umidade=registro.get('umidade'),
                        velocidade_vento=registro['velocidade_vento'],
                        altura_captura=altura_registro,
                        created_at=datetime.now()
                    )
                    
                    # Salvar no banco usando o método correto
                    dado_id = repo.salvar(dado_meteorologico)
                    if dado_id:
                        dados_salvos += 1
                    
                except Exception as e:
                    erros.append(f"Erro ao salvar registro {registro.get('data', 'N/A')} para altura {altura}m: {str(e)}")
            
        except Exception as e:
            erros.append(f"Erro ao coletar dados para altura {altura}m: {str(e)}")
    
    return dados_salvos, erros


def render_statistics_summary(met_repo):
    """Renderiza resumo de estatísticas"""
    try:
        total_dados = len(met_repo.listar_todos())
        if total_dados > 0:
            st.markdown(f"""
            <div class="wind-info-card slide-in">
                <h4 class="wind-info-title">📊 Dados Atuais: {total_dados:,} registros meteorológicos</h4>
            </div>
            """, unsafe_allow_html=True)
    except:
        pass


def render_api_source_selection_static(fontes_api):
    """Renderiza seleção de fontes de API de forma estática para formulários"""
    st.markdown("""
    <div class='section-header-minor'>
        <h4>🌪️ Fontes de Dados e Alturas</h4>
    </div>
    """, unsafe_allow_html=True)
    
    if not fontes_api:
        st.markdown("""
        <div class='warning-box'>
            <h4>Nenhuma Fonte Disponível</h4>
            <p>Cadastre NASA_POWER ou OPEN_METEO primeiro na aba de fontes!</p>
        </div>
        """, unsafe_allow_html=True)
        return {}
    
    # Verificar quais fontes estão disponíveis
    nasa_disponivel = 'NASA_POWER' in fontes_api
    meteo_disponivel = 'OPEN_METEO' in fontes_api
    
    selecoes = {}
    
    # Criar colunas estáticas para as duas principais fontes
    col1, col2 = st.columns(2)
    
    # Coluna 1: NASA POWER
    with col1:
        if nasa_disponivel:
            fonte_nasa = fontes_api['NASA_POWER']
            
            st.markdown("""
            <div style='background: linear-gradient(135deg, #e74c3c22, #e74c3c11); 
                        padding: 15px; border-radius: 10px; margin-bottom: 10px;
                        border-left: 4px solid #e74c3c;'>
                <h4 style='color: #e74c3c; margin: 0; display: flex; align-items: center;'>
                    🛰️ NASA POWER
                </h4>
                <p style='margin: 5px 0 0 0; color: #666; font-size: 0.9em;'>Dados globais via satélite - Mais estável, processamento lento</p>
                <p style='margin: 5px 0 0 0; color: #888; font-size: 0.85em;'>
                    <strong>Alturas disponíveis:</strong> 10m, 50m
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            
            st.markdown("**Selecione as alturas de captura:**")
            
            
            alturas_nasa = []
            
            
            if st.checkbox("📏 10m", key="NASA_POWER_10m"):
                alturas_nasa.append(10)
            
            
            if st.checkbox("📏 50m", key="NASA_POWER_50m"):
                alturas_nasa.append(50)
            
            if alturas_nasa:
                selecoes['NASA_POWER'] = {
                    'fonte_obj': fonte_nasa,
                    'alturas': alturas_nasa
                }
                alturas_str = ", ".join([f"{a}m" for a in alturas_nasa])
                st.success(f"✅ NASA POWER: {len(alturas_nasa)} altura(s) - {alturas_str}")

        else:
            st.markdown("""
            <div style='background: #f8f9fa; padding: 15px; border-radius: 10px; border-left: 4px solid #6c757d;'>
                <h4 style='color: #6c757d; margin: 0;'>🛰️ NASA POWER</h4>
                <p style='margin: 5px 0 0 0; color: #999; font-size: 0.9em;'>Não disponível - cadastre a fonte primeiro</p>
            </div>
            """, unsafe_allow_html=True)
    
    # Coluna 2: Open-Meteo
    with col2:
        if meteo_disponivel:
            fonte_meteo = fontes_api['OPEN_METEO']
            
            st.markdown("""
            <div style='background: linear-gradient(135deg, #3498db22, #3498db11); 
                        padding: 15px; border-radius: 10px; margin-bottom: 10px;
                        border-left: 4px solid #3498db;'>
                <h4 style='color: #3498db; margin: 0; display: flex; align-items: center;'>
                    🌍 OPEN METEO
                </h4>
                <p style='margin: 5px 0 0 0; color: #666; font-size: 0.9em;'>Dados históricos de alta resolução - Mais rápido, com limites</p>
                <p style='margin: 5px 0 0 0; color: #888; font-size: 0.85em;'>
                    <strong>Alturas disponíveis:</strong> 10m, 80m, 120m, 180m
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            
            st.markdown("**Selecione as alturas de captura:**")
            
            # Checkboxes para alturas Open-Meteo
            col_meteo1, col_meteo2 = st.columns(2)
            col_meteo3, col_meteo4 = st.columns(2)
            alturas_meteo = []
            
            
            if st.checkbox("📏 10m", key="OPEN_METEO_10m"):
                alturas_meteo.append(10)
        
        
            if st.checkbox("📏 80m", key="OPEN_METEO_80m"):
                alturas_meteo.append(80)
        
        
            if st.checkbox("📏 120m", key="OPEN_METEO_120m"):
                alturas_meteo.append(120)
        
        
            if st.checkbox("📏 180m", key="OPEN_METEO_180m"):
                alturas_meteo.append(180)
            
            if alturas_meteo:
                selecoes['OPEN_METEO'] = {
                    'fonte_obj': fonte_meteo,
                    'alturas': alturas_meteo
                }
                alturas_str = ", ".join([f"{a}m" for a in alturas_meteo])
                st.success(f"✅ Open-Meteo: {len(alturas_meteo)} altura(s) - {alturas_str}")

        else:
            st.markdown("""
            <div style='background: #f8f9fa; padding: 15px; border-radius: 10px; border-left: 4px solid #6c757d;'>
                <h4 style='color: #6c757d; margin: 0;'>🌍 OPEN METEO</h4>
                <p style='margin: 5px 0 0 0; color: #999; font-size: 0.9em;'>Não disponível - cadastre a fonte primeiro</p>
            </div>
            """, unsafe_allow_html=True)
    
    return selecoes


def create_meteorological_data():
    """
    Interface para cadastro de dados meteorológicos
    """
    
    # Header principal
    st.markdown("""
    <div class='main-header'>
        <h3 style='color: #0066cc; display: flex; align-items: center; justify-content: center;'>
            🌪️ Coleta de Dados Meteorológicos
        </h3>
        <p style='color: #666;'>Colete dados históricos de vento das principais APIs meteorológicas.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Inicializar repositórios
    try:
        met_repo = MeteorologicalDataRepository()
        fonte_repo = MeteorologicalDataSourceRepository()
        cidade_repo = CidadeRepository()
        regiao_repo = RegiaoRepository()
        pais_repo = PaisRepository()
        
        # Criar tabelas se necessário
        met_repo.criar_tabela()
        fonte_repo.criar_tabela()
        
        # Carregar dados necessários
        fontes = fonte_repo.listar_todos()
        cidades = cidade_repo.listar_todos()
        regioes = {r.id: r.nome for r in regiao_repo.listar_todos()}
        paises = {p.id: p.codigo for p in pais_repo.listar_todos()}
        
        # Validações iniciais
        if not fontes:
            st.markdown("""
            <div class='warning-box'>
                <h4>❌ Nenhuma fonte de dados cadastrada</h4>
                <p>Cadastre uma fonte primeiro para poder coletar dados.</p>
            </div>
            """, unsafe_allow_html=True)
            if st.button("➕ Ir para Cadastro de Fontes", use_container_width=True):
                st.session_state.selected_meteorological_tab = "fonte"
                st.rerun()
            return
        
        if not cidades:
            st.markdown("""
            <div class='warning-box'>
                <h4>❌ Nenhuma cidade cadastrada</h4>
                <p>Cadastre uma cidade primeiro para definir o local de coleta.</p>
            </div>
            """, unsafe_allow_html=True)
            if st.button("🏙️ Ir para Cadastro de Cidades", use_container_width=True):
                st.switch_page("pages/1_cadastro_localidade.py")
            return
            
    except Exception as e:
        st.markdown(f"""
        <div class='warning-box'>
            <h4>Erro ao inicializar sistema</h4>
            <p>{str(e)}</p>
        </div>
        """, unsafe_allow_html=True)
        return

    # Estatísticas rápidas
    render_statistics_summary(met_repo)

    # Formulário principal
    with st.form("form_dados_meteorologicos", clear_on_submit=False, border=True):
        
        # Seção 1: Localização
        column1, column2 = st.columns([3, 1], border=True)
        
        with column1:
            st.markdown("""
            <div class='section-header-minor'>
                <h4>🏙️ Localização</h4>
            </div>
            """, unsafe_allow_html=True)
            
            # Preparar opções de cidades com informações completas
            opcoes_cidades = {}
            for cidade in cidades:
                regiao_nome = regioes.get(cidade.regiao_id)
                pais_codigo = paises.get(cidade.pais_id, "N/A")
                display_text = formatar_cidade_display(cidade, regiao_nome, pais_codigo)
                opcoes_cidades[display_text] = cidade
            
            cidade_selecionada_text = st.selectbox(
                "Cidade ***para coleta***",
                options=list(opcoes_cidades.keys()),
                help="Selecione a cidade onde serão coletados os dados meteorológicos"
            )
            
            cidade_selecionada = opcoes_cidades[cidade_selecionada_text] if cidade_selecionada_text else None
            
            if cidade_selecionada:
                st.info(f"📍 **Coordenadas:** {cidade_selecionada.latitude:.4f}, {cidade_selecionada.longitude:.4f}")
        
        with column2:
            st.markdown("""
            <div class='thermal-section'>
                <h4>Período de Coleta</h4>
            </div>
            """, unsafe_allow_html=True)
            
            col1, col2 = column2.columns(2)
            
            with col1:
                data_inicio = st.date_input(
                    "***Data Início***",
                    value=date.today() - timedelta(days=394),
                    max_value=date.today(),
                    help="Data inicial para coleta dos dados"
                )
            
            with col2:
                data_fim = st.date_input(
                    "***Data Fim***",
                    value=date.today() - timedelta(days=30),
                    max_value=date.today(),
                    help="Data final para coleta dos dados"
                )
            
            # Validação de período
            if data_inicio and data_fim:
                if data_inicio > data_fim:
                    st.error("❌ Data início deve ser anterior à data fim")
                else:
                    diferenca_dias = (data_fim - data_inicio).days + 1
                    st.success(f"📅 **Período:** {diferenca_dias} dias")
                    
                    if diferenca_dias > 365:
                        st.warning("⚠️ Período muito extenso. Considere dividir em períodos menores.")

        # Seção 2: Seleção de Fontes e Alturas
        st.markdown("---")
        
        # Filtrar fontes relacionadas às APIs
        fontes_api = {f.name: f for f in fontes if f.name in ['NASA_POWER', 'OPEN_METEO']}
        
        # Renderizar seleção de fontes (agora estática para formulários)
        selecoes = render_api_source_selection_static(fontes_api)

        # Seção 3: Botões de ação
        st.markdown("---")
        st.markdown("""
        <div style="text-align: center; margin-top: 20px;">
        </div>
        """, unsafe_allow_html=True)
        
        submitted = st.form_submit_button("🌪️ Iniciar Coleta de Dados", use_container_width=True, type="primary")

    # Processamento do formulário
    if submitted:
        # Validações
        erros = []
        
        if not cidade_selecionada:
            erros.append("Cidade é obrigatória")
        
        if not data_inicio or not data_fim or data_inicio > data_fim:
            erros.append("Período inválido - verifique as datas")
        
        if not selecoes:
            erros.append("Selecione pelo menos uma fonte e altura")
        
        if erros:
            st.markdown("""
            <div class='warning-box'>
                <h4>⚠️ Erros de Validação</h4>
            </div>
            """, unsafe_allow_html=True)
            for erro in erros:
                st.error(f"• {erro}")
            return
        
        # Mostrar resumo antes de processar
        st.markdown("""
        <div class='info-box'>
            <h4>🚀 Iniciando coleta de dados...</h4>
        </div>
        """, unsafe_allow_html=True)
        
        # Inicializar clientes das APIs
        clientes_api = {
            'NASA_POWER': NASAPowerClient(),
            'OPEN_METEO': OpenMeteoClient()
        }
        
        # Processar cada fonte selecionada
        total_dados_salvos = 0
        todos_erros = []
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for i, (nome_fonte, dados) in enumerate(selecoes.items()):
            try:
                progress = (i + 1) / len(selecoes)
                progress_bar.progress(progress)
                status_text.text(f"Processando {nome_fonte.replace('_', ' ')}...")
                
                # Obter cliente da API
                cliente = clientes_api.get(nome_fonte)
                if not cliente:
                    todos_erros.append(f"Cliente para {nome_fonte} não disponível")
                    continue
                
                # Processar coleta
                dados_salvos, erros_fonte = processar_coleta_dados(
                    api_client=cliente,
                    latitude=cidade_selecionada.latitude,
                    longitude=cidade_selecionada.longitude,
                    data_inicio=data_inicio,
                    data_fim=data_fim,
                    alturas_selecionadas=dados['alturas'],
                    fonte_id=dados['fonte_obj'].id,
                    cidade_id=cidade_selecionada.id,
                    repo=met_repo
                )
                
                total_dados_salvos += dados_salvos
                todos_erros.extend(erros_fonte)
                
            except Exception as e:
                todos_erros.append(f"Erro ao processar {nome_fonte}: {str(e)}")
        
        # Finalizar e mostrar resultados
        progress_bar.empty()
        status_text.empty()
        
        if total_dados_salvos > 0:
            st.markdown(f"""
            <div class='info-box'>
                <h4>✅ Coleta Concluída com Sucesso!</h4>
                <h5>{total_dados_salvos} registros salvos no banco de dados.</h5>
                <p>Os dados meteorológicos foram coletados e estão prontos para análise.</p>
            </div>
            """, unsafe_allow_html=True)
            st.balloons()
            
            # Estatísticas da coleta
            with st.expander("📊 Detalhes da Coleta Realizada"):
                st.write(f"**🏙️ Cidade:** {cidade_selecionada.nome}")
                st.write(f"**📅 Período:** {data_inicio} até {data_fim}")
                st.write(f"**📊 Total de registros:** {total_dados_salvos}")
                st.write(f"**🌪️ Fontes utilizadas:** {', '.join([nome.replace('_', ' ') for nome in selecoes.keys()])}")
                
                if todos_erros:
                    st.write("**⚠️ Avisos durante a coleta:**")
                    for erro in todos_erros:
                        st.write(f"  • {erro}")
        else:
            st.markdown("""
            <div class='warning-box'>
                <h4>❌ Nenhum dado foi coletado</h4>
                <p>Verifique os erros abaixo e tente novamente.</p>
            </div>
            """, unsafe_allow_html=True)
            
            if todos_erros:
                st.write("**Erros encontrados:**")
                for erro in todos_erros:
                    st.error(f"• {erro}")

    # Seção de informações e últimos registros
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="wind-info-card slide-in">
            <h4 class="wind-info-title">💡 Informações Importantes</h4>
        </div>
        """, unsafe_allow_html=True)
        
        st.info("""
        **🔍 Validação Automática:**
        • Sistema verifica dados existentes
        • Evita inserções duplicadas
        • Baseado em: cidade + período + fonte + altura
        
        **⏱️ Performance:**
        • NASA POWER: mais lento, mais estável
        • Open-Meteo: mais rápido, com limites diários
        • Períodos longos podem demorar mais
        """)
    
    with col2:
        st.markdown("""
        <div class="wind-info-card slide-in">
            <h4 class="wind-info-title">📋 Últimos Registros</h4>
        </div>
        """, unsafe_allow_html=True)
        
        try:
            # Mostrar últimos 5 registros
            ultimos_dados = met_repo.listar_todos()
            if ultimos_dados:
                ultimos_5 = sorted(ultimos_dados, key=lambda x: x.created_at or datetime.min, reverse=True)[:5]
                
                for dado in ultimos_5:
                    cidade_nome = next((c.nome for c in cidades if c.id == dado.cidade_id), "N/A")
                    fonte_nome = next((f.name for f in fontes if f.id == dado.meteorological_data_source_id), "N/A")
                    
                    st.write(f"• **{cidade_nome}** - {fonte_nome.replace('_', ' ')} - {dado.altura_captura}m - {dado.data_hora.strftime('%Y-%m-%d %H:%M')} - Velocidade: {dado.velocidade_vento} m/s")
            else:
                st.write("Nenhum dado cadastrado ainda.")
                
        except Exception as e:
            st.write(f"Erro ao carregar registros: {e}")


if __name__ == "__main__":
    create_meteorological_data()

"""
Página de Parâmetros Iniciais para Análise de Turbinas Eólicas

Esta página permite selecionar e configurar os parâmetros básicos necessários
para a análise de viabilidade eólica:
- Seleção de localidade com dados meteorológicos
- Escolha de turbina e especificações
- Altura de instalação
- Período de análise
"""

import streamlit as st
import sys
from pathlib import Path
import pandas as pd
from datetime import datetime, date, timedelta
import pytz

def safe_convert_to_date(datetime_obj):
    """
    Converte datetime para date de forma segura, lidando com timezone.
    
    Args:
        datetime_obj: Objeto datetime que pode ter timezone
        
    Returns:
        date: Objeto date sem timezone
    """
    if datetime_obj is None:
        return None
    
    # Se o datetime tem timezone, converter para local
    if hasattr(datetime_obj, 'tzinfo') and datetime_obj.tzinfo is not None:
        # Converter para timezone local ou UTC
        if datetime_obj.tzinfo != pytz.UTC:
            datetime_obj = datetime_obj.astimezone(pytz.UTC)
        # Remover timezone antes de converter para date
        datetime_obj = datetime_obj.replace(tzinfo=None)
    
    return datetime_obj.date() if hasattr(datetime_obj, 'date') else datetime_obj

# Adicionar src ao path para imports
src_path = Path(__file__).parent.parent.parent.parent / "src"
sys.path.insert(0, str(src_path))

from meteorological.meteorological_data.repository import MeteorologicalDataRepository
from geographic import CidadeRepository, RegiaoRepository, PaisRepository
from turbine_parameters.aerogenerators.repository import AerogeneratorRepository
from turbine_parameters.manufacturers.repository import ManufacturerRepository


def render_initial_parameters_tab():
    """Renderiza a aba de parâmetros iniciais."""
    
    st.markdown("""
    <div class="wind-info-card slide-in">
        <h4 class="wind-info-title">📋 Configuração dos Parâmetros Iniciais</h4>
        <p>Configure os parâmetros básicos para a análise de viabilidade eólica.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Inicializar repositórios
    try:
        met_repo = MeteorologicalDataRepository()
        cidade_repo = CidadeRepository()
        regiao_repo = RegiaoRepository()
        pais_repo = PaisRepository()
        aerogenerator_repo = AerogeneratorRepository()
        manufacturer_repo = ManufacturerRepository()
        
    except Exception as e:
        st.error(f"❌ Erro ao conectar com o banco de dados: {str(e)}")
        return
    
    # Criar colunas para organização
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 🌍 Localização")
        
        # Buscar localidades com dados meteorológicos
        try:
            cidades_com_dados = met_repo.get_unique_cities_with_data()
            if not cidades_com_dados:
                st.warning("⚠️ Nenhuma cidade com dados meteorológicos encontrada.")
                return
            
            # Criar lista de opções com formato "Cidade, Estado, País"
            opcoes_cidades = []
            cidades_dict = {}
            
            for cidade_info in cidades_com_dados:
                cidade_id = cidade_info['cidade_id']
                cidade_data = cidade_repo.find_by_id(cidade_id)
                
                if cidade_data:
                    regiao_data = regiao_repo.find_by_id(cidade_data.regiao_id)
                    pais_data = pais_repo.find_by_id(regiao_data.pais_id)
                    
                    opcao = f"{cidade_data.nome}, {regiao_data.nome}, {pais_data.nome}"
                    opcoes_cidades.append(opcao)
                    cidades_dict[opcao] = {
                        'cidade': cidade_data,
                        'regiao': regiao_data,
                        'pais': pais_data,
                        'dados_count': cidade_info['dados_count']
                    }
            
            # Selectbox para escolha da cidade
            cidade_selecionada_key = st.selectbox(
                "Selecione a localidade:",
                opcoes_cidades,
                key="cidade_select",
                help="Selecione uma cidade que possui dados meteorológicos coletados"
            )
            
            if cidade_selecionada_key:
                cidade_selecionada = cidades_dict[cidade_selecionada_key]
                
                # Exibir informações da cidade selecionada
                st.info(f"""
                **📍 Localidade Selecionada:**
                - **Cidade:** {cidade_selecionada['cidade'].nome}
                - **Estado/Região:** {cidade_selecionada['regiao'].nome}
                - **País:** {cidade_selecionada['pais'].nome}
                - **Latitude:** {cidade_selecionada['cidade'].latitude:.4f}°
                - **Longitude:** {cidade_selecionada['cidade'].longitude:.4f}°
                - **Dados Disponíveis:** {cidade_selecionada['dados_count']} registros
                """)
                
        except Exception as e:
            st.error(f"❌ Erro ao buscar cidades: {str(e)}")
            return
    
    with col2:
        st.markdown("### 📊 Período de Análise")
        
        try:
            # Buscar período disponível para a cidade selecionada
            if 'cidade_selecionada' in locals():
                periodo_info = met_repo.get_date_range_for_city(cidade_selecionada['cidade'].id)
                
                if periodo_info:
                    data_inicio_db = safe_convert_to_date(periodo_info['data_inicio'])
                    data_fim_db = safe_convert_to_date(periodo_info['data_fim'])
                    
                    st.info(f"""
                    **📅 Período Disponível:**
                    - **Início:** {data_inicio_db}
                    - **Fim:** {data_fim_db}
                    - **Total:** {(data_fim_db - data_inicio_db).days} dias
                    """)
                    
                    # Seletores de data
                    data_inicio = st.date_input(
                        "Data Início:",
                        value=data_inicio_db,
                        min_value=data_inicio_db,
                        max_value=data_fim_db,
                        key="data_inicio"
                    )
                    
                    data_fim = st.date_input(
                        "Data Fim:",
                        value=data_fim_db,
                        min_value=data_inicio_db,
                        max_value=data_fim_db,
                        key="data_fim"
                    )
                    
                    # Validar período selecionado
                    if data_inicio <= data_fim:
                        dias_analise = (data_fim - data_inicio).days + 1
                        st.success(f"✅ Período válido: {dias_analise} dias")
                    else:
                        st.error("❌ Data de início deve ser anterior à data fim")
                        
                else:
                    st.warning("⚠️ Nenhum dado meteorológico encontrado para esta cidade.")
                    
        except Exception as e:
            st.error(f"❌ Erro ao buscar período de dados: {str(e)}")
    
    st.markdown("---")
    
    # Seção de Turbina
    st.markdown("### 🌀 Especificações da Turbina")
    
    col3, col4 = st.columns(2)
    
    with col3:
        try:
            # Buscar fabricantes
            fabricantes = manufacturer_repo.find_all()
            if not fabricantes:
                st.warning("⚠️ Nenhum fabricante encontrado no banco de dados.")
                return
            
            opcoes_fabricantes = [(f.nome, f.id) for f in fabricantes]
            opcoes_fabricantes.insert(0, ("Selecione um fabricante", None))
            
            fabricante_selecionado = st.selectbox(
                "Fabricante:",
                opcoes_fabricantes,
                format_func=lambda x: x[0],
                key="fabricante_select"
            )
            
            if fabricante_selecionado[1]:
                # Buscar aerogeneradores do fabricante
                aerogeneradores = aerogenerator_repo.find_by_manufacturer_id(fabricante_selecionado[1])
                
                if aerogeneradores:
                    opcoes_turbinas = [(f"{aero.modelo} ({aero.potencia_nominal}kW)", aero) for aero in aerogeneradores]
                    
                    turbina_selecionada_tuple = st.selectbox(
                        "Modelo da Turbina:",
                        opcoes_turbinas,
                        format_func=lambda x: x[0],
                        key="turbina_select"
                    )
                    
                    if turbina_selecionada_tuple:
                        turbina_selecionada = turbina_selecionada_tuple[1]
                        
                        st.info(f"""
                        **🌀 Turbina Selecionada:**
                        - **Modelo:** {turbina_selecionada.modelo}
                        - **Potência Nominal:** {turbina_selecionada.potencia_nominal:,} kW
                        - **Diâmetro do Rotor:** {turbina_selecionada.diametro_rotor} m
                        - **Altura do Hub:** {turbina_selecionada.altura_hub} m
                        """)
                        
                else:
                    st.warning("⚠️ Nenhuma turbina encontrada para este fabricante.")
                    
        except Exception as e:
            st.error(f"❌ Erro ao buscar turbinas: {str(e)}")
    
    with col4:
        st.markdown("### ⚡ Configurações de Instalação")
        
        # Altura do hub (permitir personalização)
        if 'turbina_selecionada' in locals():
            altura_hub = st.number_input(
                "Altura do Hub (m):",
                min_value=10.0,
                max_value=200.0,
                value=float(turbina_selecionada.altura_hub),
                step=5.0,
                key="altura_hub",
                help="Altura de instalação da turbina (pode ser diferente da altura padrão)"
            )
        else:
            altura_hub = st.number_input(
                "Altura do Hub (m):",
                min_value=10.0,
                max_value=200.0,
                value=80.0,
                step=5.0,
                key="altura_hub_default"
            )
        
        # Fatores de ajuste
        st.markdown("**Fatores de Correção:**")
        fator_wake = st.slider(
            "Fator de Wake (%)",
            min_value=0,
            max_value=30,
            value=5,
            help="Perdas por efeito wake (turbulência entre turbinas)"
        )
        
        fator_disponibilidade = st.slider(
            "Disponibilidade (%)",
            min_value=80,
            max_value=100,
            value=95,
            help="Percentual de tempo que a turbina está operacional"
        )
    
    st.markdown("---")
    
    # Botão de confirmação
    col5, col6, col7 = st.columns([1, 2, 1])
    
    with col6:
        if st.button("💾 Confirmar Parâmetros", type="primary", use_container_width=True):
            try:
                # Verificar se todas as variáveis necessárias estão definidas
                if 'cidade_selecionada' not in locals() or 'turbina_selecionada' not in locals():
                    st.error("❌ Selecione cidade e turbina antes de confirmar.")
                    return
                
                if 'data_inicio' not in locals() or 'data_fim' not in locals() or 'dias_analise' not in locals():
                    st.error("❌ Configure o período de análise antes de confirmar.")
                    return
                
                # Garantir que as datas são objetos date
                if hasattr(data_inicio, 'date'):
                    data_inicio = data_inicio.date()
                if hasattr(data_fim, 'date'):
                    data_fim = data_fim.date()
                
                # Salvar parâmetros no session state
                st.session_state.analysis_state.update({
                    'cidade_selected': cidade_selecionada,
                    'turbina_selected': turbina_selecionada,
                    'altura_turbina': altura_hub,
                    'fatores_correcao': {
                        'wake': fator_wake / 100,
                        'disponibilidade': fator_disponibilidade / 100
                    },
                    'periodo_analise': {
                        'data_inicio': data_inicio,
                        'data_fim': data_fim,
                        'dias_total': dias_analise
                    }
                })
                
                st.success("✅ Parâmetros confirmados! Prossiga para a próxima aba.")
                
            except Exception as e:
                st.error(f"❌ Erro ao salvar parâmetros: {str(e)}")


if __name__ == "__main__":
    render_initial_parameters_tab()

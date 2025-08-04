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
    Converte datetime para date de forma segura, lidando com timezone e strings.
    
    Args:
        datetime_obj: Objeto datetime, string ISO ou date
        
    Returns:
        date: Objeto date sem timezone
    """
    if datetime_obj is None:
        return None
    
    # Se já é um objeto date, retornar diretamente
    if isinstance(datetime_obj, date) and not isinstance(datetime_obj, datetime):
        return datetime_obj
    
    # Se é string, converter para datetime primeiro
    if isinstance(datetime_obj, str):
        try:
            # Tentar diferentes formatos de data
            for fmt in ['%Y-%m-%d %H:%M:%S', '%Y-%m-%d', '%Y-%m-%dT%H:%M:%S', '%Y-%m-%dT%H:%M:%S.%f']:
                try:
                    datetime_obj = datetime.strptime(datetime_obj, fmt)
                    break
                except ValueError:
                    continue
            else:
                # Se nenhum formato funcionou, tentar parse ISO
                datetime_obj = datetime.fromisoformat(datetime_obj.replace('Z', '+00:00'))
        except (ValueError, AttributeError) as e:
            print(f"Erro ao converter string para datetime: {datetime_obj} - {e}")
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
                cidade_data = cidade_repo.buscar_por_id(cidade_id)
                
                if cidade_data:
                    regiao_data = regiao_repo.buscar_por_id(cidade_data.regiao_id)
                    pais_data = pais_repo.buscar_por_id(regiao_data.pais_id)
                    
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
                try:
                    cidade_nome = cidade_selecionada['cidade'].nome if hasattr(cidade_selecionada['cidade'], 'nome') else str(cidade_selecionada['cidade'])
                    regiao_nome = cidade_selecionada['regiao'].nome if hasattr(cidade_selecionada['regiao'], 'nome') else str(cidade_selecionada['regiao'])
                    pais_nome = cidade_selecionada['pais'].nome if hasattr(cidade_selecionada['pais'], 'nome') else str(cidade_selecionada['pais'])
                    latitude = cidade_selecionada['cidade'].latitude if hasattr(cidade_selecionada['cidade'], 'latitude') else 'N/A'
                    longitude = cidade_selecionada['cidade'].longitude if hasattr(cidade_selecionada['cidade'], 'longitude') else 'N/A'
                    dados_count = cidade_selecionada.get('dados_count', 'N/A')
                    
                    st.info(f"""
                    **📍 Localidade Selecionada:**
                    - **Cidade:** {cidade_nome}
                    - **Estado/Região:** {regiao_nome}
                    - **País:** {pais_nome}
                    - **Latitude:** {latitude:.4f}° {f' ({type(latitude)})' if latitude != 'N/A' else ''}
                    - **Longitude:** {longitude:.4f}° {f' ({type(longitude)})' if longitude != 'N/A' else ''}
                    - **Dados Disponíveis:** {dados_count} registros
                    """)
                except Exception as info_error:
                    st.warning(f"⚠️ Erro ao exibir informações da cidade: {str(info_error)}")
                    st.info(f"Debug: cidade_selecionada={cidade_selecionada}")
                
        except Exception as e:
            st.error(f"❌ Erro ao buscar cidades: {str(e)}")
            return
    
    with col2:
        st.markdown("### 📊 Período de Análise")
        
        try:
            # Buscar período disponível para a cidade selecionada
            if 'cidade_selecionada' in locals() and cidade_selecionada:
                # Verificar se cidade_selecionada é um dicionário e tem a estrutura correta
                cidade_id = None
                if isinstance(cidade_selecionada, dict) and 'cidade' in cidade_selecionada:
                    cidade_obj = cidade_selecionada['cidade']
                    if hasattr(cidade_obj, 'id'):
                        cidade_id = cidade_obj.id
                    elif isinstance(cidade_obj, dict) and 'id' in cidade_obj:
                        cidade_id = cidade_obj['id']
                elif isinstance(cidade_selecionada, dict) and 'id' in cidade_selecionada:
                    cidade_id = cidade_selecionada['id']
                
                if cidade_id:
                    periodo_info = met_repo.get_date_range_for_city(cidade_id)
                    
                    if periodo_info:
                        try:
                            data_inicio_db = safe_convert_to_date(periodo_info['data_inicio'])
                            data_fim_db = safe_convert_to_date(periodo_info['data_fim'])
                            
                            if data_inicio_db and data_fim_db:
                                total_dias = (data_fim_db - data_inicio_db).days
                                
                                st.info(f"""
                                **📅 Período Disponível:**
                                - **Início:** {data_inicio_db}
                                - **Fim:** {data_fim_db}
                                - **Total:** {total_dias} dias
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
                                st.warning("⚠️ Dados de período inválidos para esta cidade.")
                                st.info(f"Debug: data_inicio_db={data_inicio_db}, data_fim_db={data_fim_db}")
                                st.info(f"Debug: periodo_info={periodo_info}")
                        except Exception as date_error:
                            st.error(f"❌ Erro ao processar datas: {str(date_error)}")
                            st.info(f"Debug: periodo_info={periodo_info}")
                    else:
                        st.warning("⚠️ Nenhum dado meteorológico encontrado para esta cidade.")
                else:
                    st.warning("⚠️ Selecione uma cidade para ver o período disponível.")
                    st.info(f"Debug: cidade_selecionada={cidade_selecionada}")
                    
        except Exception as e:
            st.error(f"❌ Erro ao carregar dados meteorológicos: {str(e)}")
            import traceback
            st.code(traceback.format_exc())
    
    st.markdown("---")
    
    # Seção de Turbina
    st.markdown("### 🌀 Especificações da Turbina")
    
    col3, col4 = st.columns(2)
    
    with col3:
        try:
            # Buscar fabricantes
            fabricantes = manufacturer_repo.listar_todos()
            if not fabricantes:
                st.warning("⚠️ Nenhum fabricante encontrado no banco de dados.")
                return
            
            opcoes_fabricantes = [(f.name, f.id) for f in fabricantes]
            opcoes_fabricantes.insert(0, ("Selecione um fabricante", None))
            
            fabricante_selecionado = st.selectbox(
                "Fabricante:",
                opcoes_fabricantes,
                format_func=lambda x: x[0],
                key="fabricante_select"
            )
            
            if fabricante_selecionado[1]:
                # Buscar aerogeneradores do fabricante
                aerogeneradores = aerogenerator_repo.buscar_por_fabricante(fabricante_selecionado[1])
                
                if aerogeneradores:
                    opcoes_turbinas = [(f"{aero.model} ({aero.rated_power_kw}kW)", aero) for aero in aerogeneradores]
                    
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
                        - **Modelo:** {turbina_selecionada.model}
                        - **Potência Nominal:** {turbina_selecionada.rated_power_kw:,} kW
                        - **Diâmetro do Rotor:** {turbina_selecionada.rotor_diameter_m} m
                        - **Velocidade Cut-in:** {turbina_selecionada.cut_in_speed} m/s
                        - **Velocidade Cut-out:** {turbina_selecionada.cut_out_speed} m/s
                        """)
                        
                else:
                    st.warning("⚠️ Nenhuma turbina encontrada para este fabricante.")
                    
        except Exception as e:
            st.error(f"❌ Erro ao buscar turbinas: {str(e)}")
    
    with col4:
        st.markdown("### ⚡ Configurações de Instalação")
        
        # Altura do hub (sempre configurável, sem valor padrão de turbina)
        altura_hub = st.number_input(
            "Altura do Hub (m):",
            min_value=10.0,
            max_value=200.0,
            value=80.0,
            step=5.0,
            key="altura_hub",
            help="Altura de instalação da turbina (configurável conforme necessidade do projeto)"
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

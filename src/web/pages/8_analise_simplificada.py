"""
Página 8: Análise Simplificada de Turbinas Eólicas

Esta página oferece uma análise direta e integrada:
- Seleção de cidade e turbina do banco de dados
- Previsão de geração usando lei de potência ou logarítmica
- Análise de tempo operacional (inoperante, MPPT, nominal, cut-out)
- Dados meteorológicos reais (OpenMeteo ou NASA Power)
"""

import streamlit as st
import sys
from pathlib import Path
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import io
import base64

# Adicionar src ao path para imports
src_path = Path(__file__).parent.parent.parent / "src"
sys.path.insert(0, str(src_path))

# Imports dos repositórios
from meteorological.meteorological_data.repository import MeteorologicalDataRepository
from meteorological.meteorological_data_source.repository import MeteorologicalDataSourceRepository
from geographic import CidadeRepository, RegiaoRepository, PaisRepository
from turbine_parameters.aerogenerators.repository import AerogeneratorRepository
from turbine_parameters.manufacturers.repository import ManufacturerRepository


# Funções auxiliares para downloads
def gerar_csv_download(dataframe, nome_arquivo):
    """Gera um link de download para CSV"""
    try:
        csv = dataframe.to_csv(index=False, encoding='utf-8-sig')
        b64 = base64.b64encode(csv.encode('utf-8-sig')).decode()
        href = f'<a href="data:file/csv;base64,{b64}" download="{nome_arquivo}.csv" class="download-button">📥 Download CSV - {nome_arquivo}</a>'
        return href
    except Exception as e:
        st.error(f"Erro ao gerar CSV: {str(e)}")
        return None


def gerar_excel_download(dataframe, nome_arquivo):
    """Gera um link de download para Excel"""
    try:
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            dataframe.to_excel(writer, index=False, sheet_name='Análise')
        
        output.seek(0)
        b64 = base64.b64encode(output.read()).decode()
        href = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="{nome_arquivo}.xlsx" class="download-button">📊 Download Excel - {nome_arquivo}</a>'
        return href
    except Exception as e:
        st.error(f"Erro ao gerar Excel: {str(e)}")
        return None


def criar_secao_download(dataframe, nome_base, titulo_secao):
    """Cria uma seção com opções de download para um DataFrame"""
    if dataframe is not None and not dataframe.empty:
        with st.expander(f"📥 Downloads - {titulo_secao}"):
            col1, col2 = st.columns(2)
            
            with col1:
                csv_link = gerar_csv_download(dataframe, f"{nome_base}_csv")
                if csv_link:
                    st.markdown(csv_link, unsafe_allow_html=True)
            
            with col2:
                excel_link = gerar_excel_download(dataframe, f"{nome_base}_excel")
                if excel_link:
                    st.markdown(excel_link, unsafe_allow_html=True)
            
            st.markdown("---")
            st.caption(f"📊 Total de registros: {len(dataframe)}")
    else:
        st.warning(f"⚠️ Nenhum dado disponível para download em {titulo_secao}")


def calcular_velocidade_corrigida(velocidade_10m, altura_alvo, metodo, parametros):
    """
    Calcula velocidade do vento na altura da turbina usando lei de potência ou logarítmica.
    
    Args:
        velocidade_10m: Velocidade do vento a 10m (m/s)
        altura_alvo: Altura da turbina (m)
        metodo: 'potencia' ou 'logaritmica'
        parametros: dict com parâmetros específicos do método
    
    Returns:
        Velocidade corrigida na altura da turbina
    """
    altura_ref = 10.0  # Altura de referência dos dados meteorológicos
    
    if metodo == 'potencia':
        # Lei de Potência: v(h) = v_ref * (h/h_ref)^n
        n = parametros.get('n', 0.2)  # Expoente típico para terreno aberto
        return velocidade_10m * (altura_alvo / altura_ref) ** n
    
    elif metodo == 'logaritmica':
        # Lei Logarítmica: v(h) = v_ref * ln(h/z0) / ln(h_ref/z0)
        z0 = parametros.get('z0', 0.1)  # Rugosidade típica para pastagem
        if altura_alvo <= z0 or altura_ref <= z0:
            return velocidade_10m  # Evitar divisão por zero ou log negativo
        return velocidade_10m * np.log(altura_alvo / z0) / np.log(altura_ref / z0)
    
    return velocidade_10m


def calcular_potencia_turbina(velocidade, turbina_specs):
    """
    Calcula a potência gerada pela turbina baseada na velocidade do vento.
    Usa uma curva de potência simplificada.
    
    Args:
        velocidade: Velocidade do vento (m/s)
        turbina_specs: Especificações da turbina
    
    Returns:
        Potência em kW
    """
    # Converter todos os valores para float para evitar problemas com Decimal
    cut_in = float(turbina_specs['cut_in_speed'])
    cut_out = float(turbina_specs['cut_out_speed'])
    rated_speed = float(turbina_specs.get('rated_wind_speed', 12.0))
    rated_power = float(turbina_specs['rated_power_kw'])
    velocidade = float(velocidade)
    
    if velocidade < cut_in or velocidade > cut_out:
        return 0.0
    elif velocidade <= rated_speed:
        # Região MPPT - curva cúbica simplificada
        return rated_power * ((velocidade - cut_in) / (rated_speed - cut_in)) ** 3
    else:
        # Região nominal - potência constante
        return rated_power


def classificar_estado_operacional(velocidade, turbina_specs):
    """
    Classifica o estado operacional da turbina baseado na velocidade.
    
    Returns:
        'inoperante', 'mppt', 'nominal', ou 'cut_out'
    """
    # Converter todos os valores para float para evitar problemas com Decimal
    cut_in = float(turbina_specs['cut_in_speed'])
    cut_out = float(turbina_specs['cut_out_speed'])
    rated_speed = float(turbina_specs.get('rated_wind_speed', 12.0))
    velocidade = float(velocidade)
    
    if velocidade < cut_in:
        return 'inoperante'
    elif velocidade > cut_out:
        return 'cut_out'
    elif velocidade <= rated_speed:
        return 'mppt'
    else:
        return 'nominal'


def exibir_resultados():
    """Exibe os resultados da análise simplificada."""
    
    try:
        dados = st.session_state['analise_simplificada']
        df_resultados = dados['df_resultados']
        cidade_info = dados['cidade_info']
        turbina_info = dados['turbina_info']
        parametros = dados['parametros_analise']
        
        st.markdown("---")
        st.markdown("##  Resultados da Análise")
        
        # Informações gerais
        col1, col2, col3 = st.columns(3)
        
        try:
            with col1:
                st.info(f"""
                **🏙️ Localização**
                {cidade_info['cidade'].nome}, {cidade_info['regiao'].nome}
                Lat: {cidade_info['cidade'].latitude:.4f}°
                Lon: {cidade_info['cidade'].longitude:.4f}°
                """)
        except Exception:
            with col1:
                st.info("**🏙️ Localização**\nInformações não disponíveis")
        
        try:
            with col2:
                st.info(f"""
                **🌀 Turbina**
                {turbina_info.model}
                Potência: {turbina_info.rated_power_kw:,} kW
                Diâmetro: {turbina_info.rotor_diameter_m} m
                """)
        except Exception:
            with col2:
                st.info("**🌀 Turbina**\nInformações não disponíveis")
        
        try:
            with col3:
                st.info(f"""
                **⚙️ Configuração**
                Método: {parametros['metodo'].title()}
                Altura: {parametros['altura']} m
                Fonte: {parametros['fonte'].title()}
                """)
        except Exception:
            with col3:
                st.info("**⚙️ Configuração**\nInformações não disponíveis")
        
    except Exception as e:
        st.error(f"❌ Erro ao carregar dados da análise: {str(e)}")
        return
    
    # Estatísticas de geração
    st.markdown("""
    <div class="wind-info-card slide-in">
        <h4 class="wind-info-title">⚡ Estatísticas de Geração</h4>
    </div>
    """, unsafe_allow_html=True)
    
    try:
        # Calcular métricas
        potencia_media = df_resultados['potencia_kw'].mean()
        potencia_maxima = df_resultados['potencia_kw'].max()
        
        # Calcular energia total baseada na frequência dos dados
        num_registros = len(df_resultados)
        if num_registros > 0:
            # Assumir que dados são horários se temos aproximadamente 24 registros por dia
            registros_por_dia = num_registros / parametros['periodo']
            if registros_por_dia >= 20:  # Dados horários
                energia_total_kwh = df_resultados['potencia_kw'].sum()
            else:  # Dados menos frequentes, estimar
                energia_total_kwh = df_resultados['potencia_kw'].sum() * (24 / registros_por_dia)
        else:
            energia_total_kwh = 0
        
        # Estatísticas por estado operacional
        estados_count = df_resultados['estado_operacional'].value_counts()
        total_registros = len(df_resultados)
        
        col1, col2, col3, col4 = st.columns(4)
        
        try:
            with col1:
                st.metric(
                    "Potência Média",
                    f"{potencia_media:.1f} kW",
                    delta=f"{(potencia_media/float(turbina_info.rated_power_kw))*100:.1f}% da nominal"
                )
        except Exception:
            with col1:
                st.metric("Potência Média", f"{potencia_media:.1f} kW")
        
        try:
            with col2:
                st.metric(
                    "Energia Estimada",
                    f"{energia_total_kwh:.0f} kWh",
                    delta=f"em {parametros['periodo']} dias"
                )
        except Exception:
            with col2:
                st.metric("Energia Estimada", f"{energia_total_kwh:.0f} kWh")
        
        try:
            with col3:
                velocidade_media = df_resultados['velocidade_corrigida'].mean()
                st.metric(
                    "Velocidade Média",
                    f"{velocidade_media:.1f} m/s",
                    delta=f"na altura {parametros['altura']}m"
                )
        except Exception:
            with col3:
                st.metric("Velocidade Média", "N/A")
        
        try:
            with col4:
                fator_capacidade = (potencia_media / float(turbina_info.rated_power_kw)) * 100
                st.metric(
                    "Fator de Capacidade",
                    f"{fator_capacidade:.1f}%",
                    delta="Eficiência geral"
                )
        except Exception:
            with col4:
                st.metric("Fator de Capacidade", "N/A")
                
    except Exception as metrics_error:
        st.error(f"❌ Erro ao calcular estatísticas: {str(metrics_error)}")
        return
    
    # Tabela de tempo operacional
    st.markdown("""
    <div class="wind-info-card slide-in">
        <h4 class="wind-info-title">⏱️ Análise de Tempo Operacional</h4>
    </div>
    """, unsafe_allow_html=True)
    
    try:
        # Calcular porcentagens
        porcentagens = {}
        for estado in ['inoperante', 'mppt', 'nominal', 'cut_out']:
            count = estados_count.get(estado, 0)
            porcentagem = (count / total_registros) * 100 if total_registros > 0 else 0
            porcentagens[estado] = porcentagem
        
        # Criar DataFrame para tabela
        df_estados = pd.DataFrame([
            {
                'Estado Operacional': '🔴 Inoperante',
                'Descrição': f'v < {float(turbina_info.cut_in_speed):.1f} m/s (cut-in)',
                'Tempo (%)': f"{porcentagens['inoperante']:.1f}%",
                'Registros': estados_count.get('inoperante', 0)
            },
            {
                'Estado Operacional': '🟡 MPPT',
                'Descrição': f'{float(turbina_info.cut_in_speed):.1f} ≤ v ≤ {float(turbina_info.rated_wind_speed):.1f} m/s',
                'Tempo (%)': f"{porcentagens['mppt']:.1f}%",
                'Registros': estados_count.get('mppt', 0)
            },
            {
                'Estado Operacional': '🟢 Nominal',
                'Descrição': f'{float(turbina_info.rated_wind_speed):.1f} < v ≤ {float(turbina_info.cut_out_speed):.1f} m/s',
                'Tempo (%)': f"{porcentagens['nominal']:.1f}%",
                'Registros': estados_count.get('nominal', 0)
            },
            {
                'Estado Operacional': '🔴 Cut-out',
                'Descrição': f'v > {float(turbina_info.cut_out_speed):.1f} m/s (segurança)',
                'Tempo (%)': f"{porcentagens['cut_out']:.1f}%",
                'Registros': estados_count.get('cut_out', 0)
            }
        ])
        
        st.dataframe(df_estados, use_container_width=True, hide_index=True)
        
    except Exception as table_error:
        st.error(f"❌ Erro ao gerar tabela de estados operacionais: {str(table_error)}")
        # Tabela básica como fallback
        try:
            st.write("**Estados Operacionais (valores aproximados):**")
            for estado, count in estados_count.items():
                porcentagem = (count / total_registros) * 100 if total_registros > 0 else 0
                st.write(f"- {estado.title()}: {porcentagem:.1f}% ({count} registros)")
        except Exception:
            st.write("Dados de estados operacionais não disponíveis.")
    
    # Gráficos de análise
    st.markdown("""
    <div class="wind-info-card slide-in">
        <h4 class="wind-info-title">📈 Visualizações</h4>
    </div>
    """, unsafe_allow_html=True)
    
    try:
        # Gráfico de pizza dos estados operacionais
        try:
            fig_pie = px.pie(
                values=[porcentagens[estado] for estado in ['inoperante', 'mppt', 'nominal', 'cut_out']],
                names=['Inoperante', 'MPPT', 'Nominal', 'Cut-out'],
                title="Distribuição do Tempo Operacional",
                color_discrete_map={
                    'Inoperante': '#ff4444',
                    'MPPT': '#ffaa00', 
                    'Nominal': '#44ff44',
                    'Cut-out': '#ff0000'
                }
            )
        except Exception as pie_error:
            st.warning(f"⚠️ Erro ao gerar gráfico de pizza: {str(pie_error)}")
            fig_pie = None
        
        # Gráfico temporal de potência
        try:
            fig_temporal = px.line(
                df_resultados,
                x='datetime',
                y='potencia_kw',
                title="Potência Gerada ao Longo do Tempo",
                labels={'potencia_kw': 'Potência (kW)', 'datetime': 'Data/Hora'}
            )
            fig_temporal.add_hline(y=float(turbina_info.rated_power_kw), line_dash="dash", 
                                  annotation_text="Potência Nominal")
        except Exception as temporal_error:
            st.warning(f"⚠️ Erro ao gerar gráfico temporal: {str(temporal_error)}")
            fig_temporal = None
        
        # Histograma de velocidades
        try:
            fig_hist = px.histogram(
                df_resultados,
                x='velocidade_corrigida',
                nbins=30,
                title="Distribuição de Velocidades do Vento",
                labels={'velocidade_corrigida': 'Velocidade (m/s)', 'count': 'Frequência'}
            )
            fig_hist.add_vline(x=float(turbina_info.cut_in_speed), line_dash="dash", 
                               annotation_text="Cut-in")
            fig_hist.add_vline(x=float(turbina_info.cut_out_speed), line_dash="dash", 
                               annotation_text="Cut-out")
            fig_hist.add_vline(x=float(turbina_info.rated_wind_speed), line_dash="dash", 
                               annotation_text="Nominal")
        except Exception as hist_error:
            st.warning(f"⚠️ Erro ao gerar histograma: {str(hist_error)}")
            fig_hist = None
        
        # Exibir gráficos
        col1, col2 = st.columns(2)
        
        try:
            with col1:
                if fig_pie:
                    st.plotly_chart(fig_pie, use_container_width=True)
                else:
                    st.info("Gráfico de pizza não disponível")
        except Exception:
            with col1:
                st.info("Erro ao exibir gráfico de pizza")
        
        try:
            with col2:
                if fig_hist:
                    st.plotly_chart(fig_hist, use_container_width=True)
                else:
                    st.info("Histograma não disponível")
        except Exception:
            with col2:
                st.info("Erro ao exibir histograma")
        
        try:
            if fig_temporal:
                st.plotly_chart(fig_temporal, use_container_width=True)
            else:
                st.info("Gráfico temporal não disponível")
        except Exception:
            st.info("Erro ao exibir gráfico temporal")
            
    except Exception as viz_error:
        st.error(f"❌ Erro geral nas visualizações: {str(viz_error)}")
        st.info("Visualizações não disponíveis neste momento.")
    
    # Dados diários agregados
    st.markdown("""
    <div class="wind-info-card slide-in">
        <h4 class="wind-info-title">📅 Previsão Média Diária</h4>
    </div>
    """, unsafe_allow_html=True)
    
    try:
        # Agregar por dia
        df_diario = df_resultados.groupby('data').agg({
            'potencia_kw': ['mean', 'max', 'sum'],
            'velocidade_corrigida': 'mean',
            'estado_operacional': lambda x: (x == 'nominal').sum() / len(x) * 100
        }).round(2)
        
        # Flatten column names
        df_diario.columns = ['Potência Média (kW)', 'Potência Máxima (kW)', 
                            'Energia Diária (kWh)', 'Velocidade Média (m/s)', 
                            'Tempo Nominal (%)']
        
        # Mostrar últimos 10 dias
        st.dataframe(df_diario.tail(10), use_container_width=True)
        
        # Opções de download para dados diários
        criar_secao_download(df_diario, "dados_diarios", "Previsão Média Diária")
        
    except Exception as daily_error:
        st.warning(f"⚠️ Erro ao gerar dados diários: {str(daily_error)}")
        st.info("Dados diários não disponíveis.")
    
    # Análise por mês
    st.markdown("""
    <div class="wind-info-card slide-in">
        <h4 class="wind-info-title">📅 Análise Mensal de Geração</h4>
    </div>
    """, unsafe_allow_html=True)
    
    try:
        # Criar coluna de mês-ano
        df_resultados['mes_ano'] = pd.to_datetime(df_resultados['datetime']).dt.to_period('M')
        
        # Agregar por mês
        df_mensal = df_resultados.groupby('mes_ano').agg({
            'potencia_kw': ['mean', 'max', 'sum'],
            'velocidade_corrigida': 'mean',
            'estado_operacional': lambda x: (x.isin(['mppt', 'nominal'])).sum() / len(x) * 100
        }).round(2)
        
        # Flatten column names
        df_mensal.columns = ['Potência Média (kW)', 'Potência Máxima (kW)', 
                            'Energia Total (kWh)', 'Velocidade Média (m/s)', 
                            'Tempo Produtivo (%)']
        
        # Calcular energia média diária por mês
        df_mensal['Energia Média Diária (kWh)'] = (df_mensal['Energia Total (kWh)'] / 
                                                   df_mensal.index.to_series().apply(lambda x: x.days_in_month)).round(2)
        
        # Exibir tabela mensal
        if len(df_mensal) > 0:
            st.dataframe(df_mensal, use_container_width=True)
            
            # Gráfico de geração mensal
            col1, col2 = st.columns(2)
            
            with col1:
                try:
                    fig_mensal_energia = px.bar(
                        x=df_mensal.index.astype(str),
                        y=df_mensal['Energia Total (kWh)'],
                        title="Energia Total por Mês",
                        labels={'x': 'Mês/Ano', 'y': 'Energia Total (kWh)'},
                        color=df_mensal['Energia Total (kWh)'],
                        color_continuous_scale='Blues'
                    )
                    fig_mensal_energia.update_layout(showlegend=False, coloraxis_showscale=False)
                    st.plotly_chart(fig_mensal_energia, use_container_width=True)
                except Exception:
                    st.info("Gráfico mensal de energia não disponível")
            
            with col2:
                try:
                    fig_mensal_produtivo = px.line(
                        x=df_mensal.index.astype(str),
                        y=df_mensal['Tempo Produtivo (%)'],
                        title="Tempo Produtivo por Mês (%)",
                        labels={'x': 'Mês/Ano', 'y': 'Tempo Produtivo (%)'},
                        markers=True
                    )
                    fig_mensal_produtivo.update_traces(line_color='green', marker_color='darkgreen')
                    fig_mensal_produtivo.add_hline(y=df_mensal['Tempo Produtivo (%)'].mean(), 
                                                  line_dash="dash", annotation_text="Média")
                    st.plotly_chart(fig_mensal_produtivo, use_container_width=True)
                except Exception:
                    st.info("Gráfico mensal de produtividade não disponível")
            
            # Opções de download para dados mensais
            criar_secao_download(df_mensal, "dados_mensais", "Análise Mensal")
            
        else:
            st.info("Dados insuficientes para análise mensal.")
            
    except Exception as monthly_error:
        st.warning(f"⚠️ Erro ao gerar análise mensal: {str(monthly_error)}")
        st.info("Análise mensal não disponível.")
    
    # Análise por dia da semana
    st.markdown("""
    <div class="wind-info-card slide-in">
        <h4 class="wind-info-title">📊 Análise por Dia da Semana</h4>
    </div>
    """, unsafe_allow_html=True)
    
    try:
        # Criar coluna de dia da semana
        df_resultados['dia_semana'] = pd.to_datetime(df_resultados['datetime']).dt.day_name()
        df_resultados['dia_semana_num'] = pd.to_datetime(df_resultados['datetime']).dt.dayofweek
        
        # Traduzir nomes dos dias para português
        dias_pt = {
            'Monday': 'Segunda-feira',
            'Tuesday': 'Terça-feira', 
            'Wednesday': 'Quarta-feira',
            'Thursday': 'Quinta-feira',
            'Friday': 'Sexta-feira',
            'Saturday': 'Sábado',
            'Sunday': 'Domingo'
        }
        df_resultados['dia_semana_pt'] = df_resultados['dia_semana'].map(dias_pt)
        
        # Agregar por dia da semana
        df_semanal = df_resultados.groupby(['dia_semana_num', 'dia_semana_pt']).agg({
            'potencia_kw': ['mean', 'std'],
            'velocidade_corrigida': 'mean',
            'estado_operacional': lambda x: (x.isin(['mppt', 'nominal'])).sum() / len(x) * 100
        }).round(2)
        
        # Flatten column names
        df_semanal.columns = ['Potência Média (kW)', 'Desvio Padrão (kW)', 
                             'Velocidade Média (m/s)', 'Tempo Produtivo (%)']
        
        # Reset index para facilitar plotagem
        df_semanal = df_semanal.reset_index()
        df_semanal = df_semanal.sort_values('dia_semana_num')
        
        # Exibir tabela semanal
        st.dataframe(df_semanal[['dia_semana_pt', 'Potência Média (kW)', 'Desvio Padrão (kW)', 
                                'Velocidade Média (m/s)', 'Tempo Produtivo (%)']].rename(
                                columns={'dia_semana_pt': 'Dia da Semana'}), 
                    use_container_width=True, hide_index=True)
        
        # Gráfico de geração por dia da semana
        col1, col2 = st.columns(2)
        
        with col1:
            try:
                fig_semanal = px.bar(
                    df_semanal,
                    x='dia_semana_pt',
                    y='Potência Média (kW)',
                    title="Potência Média por Dia da Semana",
                    labels={'dia_semana_pt': 'Dia da Semana', 'Potência Média (kW)': 'Potência Média (kW)'},
                    color='Potência Média (kW)',
                    color_continuous_scale='Viridis'
                )
                fig_semanal.update_layout(showlegend=False, coloraxis_showscale=False)
                fig_semanal.update_xaxes(tickangle=45)
                st.plotly_chart(fig_semanal, use_container_width=True)
            except Exception:
                st.info("Gráfico semanal não disponível")
        
        with col2:
            try:
                fig_velocidade_semanal = px.line(
                    df_semanal,
                    x='dia_semana_pt',
                    y='Velocidade Média (m/s)',
                    title="Velocidade Média do Vento por Dia",
                    labels={'dia_semana_pt': 'Dia da Semana', 'Velocidade Média (m/s)': 'Velocidade (m/s)'},
                    markers=True
                )
                fig_velocidade_semanal.update_traces(line_color='orange', marker_color='darkorange')
                fig_velocidade_semanal.update_xaxes(tickangle=45)
                st.plotly_chart(fig_velocidade_semanal, use_container_width=True)
            except Exception:
                st.info("Gráfico de velocidade semanal não disponível")
        
        # Opções de download para dados semanais
        criar_secao_download(df_semanal[['dia_semana_pt', 'Potência Média (kW)', 'Desvio Padrão (kW)', 
                                        'Velocidade Média (m/s)', 'Tempo Produtivo (%)']].rename(
                                        columns={'dia_semana_pt': 'Dia da Semana'}), 
                            "dados_semanais", "Análise Semanal")
                
    except Exception as weekly_error:
        st.warning(f"⚠️ Erro ao gerar análise semanal: {str(weekly_error)}")
        st.info("Análise semanal não disponível.")
    
    # Análise de correlações
    st.markdown("""
    <div class="wind-info-card slide-in">
        <h4 class="wind-info-title">🔗 Correlações e Análises Avançadas</h4>
    </div>
    """, unsafe_allow_html=True)
    
    try:
        # Matriz de correlação
        correlation_data = df_resultados[['velocidade_10m', 'velocidade_corrigida', 'potencia_kw']]
        if 'temperatura' in df_resultados.columns:
            temp_data = df_resultados['temperatura'].dropna()
            if len(temp_data) > 0:
                correlation_data = df_resultados[['velocidade_10m', 'velocidade_corrigida', 'potencia_kw', 'temperatura']].dropna()
        
        if 'umidade' in df_resultados.columns:
            umid_data = df_resultados['umidade'].dropna()
            if len(umid_data) > 0 and 'temperatura' in correlation_data.columns:
                correlation_data = df_resultados[['velocidade_10m', 'velocidade_corrigida', 'potencia_kw', 'temperatura', 'umidade']].dropna()
        
        # Calcular correlações
        corr_matrix = correlation_data.corr()
        
        col1, col2 = st.columns(2)
        
        with col1:
            try:
                # Heatmap de correlação
                fig_corr = px.imshow(
                    corr_matrix,
                    title="Matriz de Correlação",
                    color_continuous_scale='RdBu',
                    aspect='auto',
                    text_auto=True
                )
                fig_corr.update_layout(
                    xaxis_title="Variáveis",
                    yaxis_title="Variáveis"
                )
                st.plotly_chart(fig_corr, use_container_width=True)
            except Exception:
                st.info("Matriz de correlação não disponível")
        
        with col2:
            try:
                # Scatter plot: Velocidade vs Potência
                fig_scatter = px.scatter(
                    df_resultados.sample(min(1000, len(df_resultados))),  # Amostra para performance
                    x='velocidade_corrigida',
                    y='potencia_kw',
                    title="Velocidade vs Potência",
                    labels={'velocidade_corrigida': 'Velocidade Corrigida (m/s)', 'potencia_kw': 'Potência (kW)'},
                    color='estado_operacional',
                    color_discrete_map={
                        'inoperante': '#ff4444',
                        'mppt': '#ffaa00',
                        'nominal': '#44ff44',
                        'cut_out': '#ff0000'
                    }
                )
                st.plotly_chart(fig_scatter, use_container_width=True)
            except Exception:
                st.info("Gráfico de dispersão não disponível")
        
        # Estatísticas avançadas
        st.write("**📈 Estatísticas Detalhadas:**")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.write("**Potência (kW):**")
            st.write(f"• Mediana: {df_resultados['potencia_kw'].median():.1f} kW")
            st.write(f"• Percentil 25: {df_resultados['potencia_kw'].quantile(0.25):.1f} kW")
            st.write(f"• Percentil 75: {df_resultados['potencia_kw'].quantile(0.75):.1f} kW")
            st.write(f"• Desvio padrão: {df_resultados['potencia_kw'].std():.1f} kW")
        
        with col2:
            st.write("**Velocidade (m/s):**")
            st.write(f"• Mediana: {df_resultados['velocidade_corrigida'].median():.1f} m/s")
            st.write(f"• Mínima: {df_resultados['velocidade_corrigida'].min():.1f} m/s")
            st.write(f"• Máxima: {df_resultados['velocidade_corrigida'].max():.1f} m/s")
            st.write(f"• Desvio padrão: {df_resultados['velocidade_corrigida'].std():.1f} m/s")
        
        with col3:
            try:
                # Calcular eficiência
                potencia_teorica_max = len(df_resultados) * float(turbina_info.rated_power_kw)
                eficiencia_real = (df_resultados['potencia_kw'].sum() / potencia_teorica_max) * 100
                
                st.write("**Eficiência:**")
                st.write(f"• Eficiência real: {eficiencia_real:.1f}%")
                st.write(f"• Horas operando: {len(df_resultados[df_resultados['potencia_kw'] > 0])}")
                st.write(f"• Horas parada: {len(df_resultados[df_resultados['potencia_kw'] == 0])}")
                
                # Calcular disponibilidade
                disponibilidade = (len(df_resultados[df_resultados['estado_operacional'] != 'cut_out']) / len(df_resultados)) * 100
                st.write(f"• Disponibilidade: {disponibilidade:.1f}%")
            except Exception:
                st.write("**Eficiência:**\nDados não disponíveis")
        
        # Preparar dados de correlação para download
        if 'correlation_data' in locals() and not correlation_data.empty:
            correlation_matrix = correlation_data.corr()
            criar_secao_download(correlation_matrix, "dados_correlacao", "Matriz de Correlação")
                
    except Exception as correlation_error:
        st.warning(f"⚠️ Erro ao gerar análise de correlações: {str(correlation_error)}")
        st.info("Análise de correlações não disponível.")
    
    # Análise horária (se houver dados suficientes)
    if len(df_resultados) > 24:
        st.markdown("""
        <div class="wind-info-card slide-in">
            <h4 class="wind-info-title">🕐 Análise Horária de Geração</h4>
        </div>
        """, unsafe_allow_html=True)
        
        try:
            # Criar coluna de hora
            df_resultados['hora'] = pd.to_datetime(df_resultados['datetime']).dt.hour
            
            # Agregar por hora
            df_horario = df_resultados.groupby('hora').agg({
                'potencia_kw': ['mean', 'std'],
                'velocidade_corrigida': 'mean'
            }).round(2)
            
            # Flatten column names
            df_horario.columns = ['Potência Média (kW)', 'Desvio Padrão (kW)', 'Velocidade Média (m/s)']
            df_horario = df_horario.reset_index()
            
            # Gráfico horário
            col1, col2 = st.columns(2)
            
            with col1:
                try:
                    fig_horario = px.line(
                        df_horario,
                        x='hora',
                        y='Potência Média (kW)',
                        title="Perfil de Geração por Hora do Dia",
                        labels={'hora': 'Hora do Dia', 'Potência Média (kW)': 'Potência Média (kW)'},
                        markers=True
                    )
                    fig_horario.update_traces(line_color='blue', marker_color='darkblue')
                    fig_horario.update_xaxes(dtick=2)  # Mostrar de 2 em 2 horas
                    st.plotly_chart(fig_horario, use_container_width=True)
                except Exception:
                    st.info("Gráfico horário não disponível")
            
            with col2:
                try:
                    fig_velocidade_horario = px.line(
                        df_horario,
                        x='hora',
                        y='Velocidade Média (m/s)',
                        title="Perfil de Velocidade por Hora do Dia",
                        labels={'hora': 'Hora do Dia', 'Velocidade Média (m/s)': 'Velocidade Média (m/s)'},
                        markers=True
                    )
                    fig_velocidade_horario.update_traces(line_color='red', marker_color='darkred')
                    fig_velocidade_horario.update_xaxes(dtick=2)
                    st.plotly_chart(fig_velocidade_horario, use_container_width=True)
                except Exception:
                    st.info("Gráfico de velocidade horário não disponível")
            
            # Opções de download para dados horários
            criar_secao_download(df_horario, "dados_horarios", "Análise Horária")
                    
        except Exception as hourly_error:
            st.warning(f"⚠️ Erro ao gerar análise horária: {str(hourly_error)}")
            st.info("Análise horária não disponível.")
    
    # Resumo de performance
    st.markdown("""
    <div class="wind-info-card slide-in">
        <h4 class="wind-info-title">📋 Resumo de Performance</h4>
    </div>
    """, unsafe_allow_html=True)
    
    try:
        col1, col2 = st.columns(2)
        
        with col1:
            try:
                st.write("**Métricas de Geração:**")
                st.write(f"• Energia total: {energia_total_kwh:.0f} kWh")
                st.write(f"• Energia média diária: {energia_total_kwh/parametros['periodo']:.1f} kWh/dia")
                st.write(f"• Fator de capacidade: {fator_capacidade:.1f}%")
                st.write(f"• Tempo produtivo: {porcentagens['mppt'] + porcentagens['nominal']:.1f}%")
            except Exception:
                st.write("**Métricas de Geração:**\nDados não disponíveis")
        
        with col2:
            try:
                st.write("**Condições de Vento:**")
                st.write(f"• Velocidade média (10m): {df_resultados['velocidade_10m'].mean():.1f} m/s")
                st.write(f"• Velocidade média ({parametros['altura']}m): {velocidade_media:.1f} m/s")
                st.write(f"• Fator de correção: {velocidade_media/df_resultados['velocidade_10m'].mean():.2f}")
                st.write(f"• Método: {parametros['metodo'].title()}")
            except Exception:
                st.write("**Condições de Vento:**\nDados não disponíveis")
                
    except Exception as summary_error:
        st.warning(f"⚠️ Erro ao gerar resumo: {str(summary_error)}")
        st.info("Resumo de performance não disponível.")
    
    # Seção de download dos dados completos
    st.markdown("""
    <div class="wind-info-card slide-in">
        <h4 class="wind-info-title">📥 Download dos Dados Completos</h4>
    </div>
    """, unsafe_allow_html=True)
    
    try:
        # Preparar dados completos para download
        dados_completos = df_resultados.copy()
        
        # Formatar datas para melhor legibilidade
        dados_completos['data_formatada'] = pd.to_datetime(dados_completos['datetime']).dt.strftime('%d/%m/%Y')
        dados_completos['hora_formatada'] = pd.to_datetime(dados_completos['datetime']).dt.strftime('%H:%M')
        
        # Reordenar colunas para melhor apresentação
        colunas_ordenadas = ['data_formatada', 'hora_formatada', 'velocidade_10m', 'velocidade_corrigida', 
                           'potencia_kw', 'estado_operacional']
        
        # Adicionar colunas adicionais se existirem
        for col in ['temperatura', 'umidade', 'pressao']:
            if col in dados_completos.columns:
                colunas_ordenadas.append(col)
        
        dados_para_download = dados_completos[colunas_ordenadas].rename(columns={
            'data_formatada': 'Data',
            'hora_formatada': 'Hora',
            'velocidade_10m': 'Velocidade 10m (m/s)',
            'velocidade_corrigida': f'Velocidade {parametros["altura"]}m (m/s)',
            'potencia_kw': 'Potência (kW)',
            'estado_operacional': 'Estado Operacional',
            'temperatura': 'Temperatura (°C)',
            'umidade': 'Umidade (%)',
            'pressao': 'Pressão (hPa)'
        })
        
        criar_secao_download(dados_para_download, "dados_completos_analise", "Dados Completos da Análise")
        
    except Exception as download_error:
        st.warning(f"⚠️ Erro ao preparar downloads: {str(download_error)}")
        st.info("Downloads não disponíveis neste momento.")


def main():
    """Função principal da página de análise simplificada."""
    
    # Configurar tema dos gráficos (se disponível)
    try:
        import plotly.io as pio
        pio.templates.default = "plotly_white"
    except Exception:
        pass  # Continuar sem tema personalizado
    
   
    
    # Header
    st.markdown("""
    <div style="text-align: center; padding: 2rem; background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%); border-radius: 10px; margin-bottom: 2rem;">
        <h1 style="color: white; margin: 0;">⚡ Análise de Geração Eólicas</h1>
        <p style="color: #e8f4fd; margin: 0.5rem 0 0 0;">Previsão direta de geração de energia com dados reais do banco</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Inicializar repositórios
    try:
        met_repo = MeteorologicalDataRepository()
        source_repo = MeteorologicalDataSourceRepository()
        cidade_repo = CidadeRepository()
        regiao_repo = RegiaoRepository()
        pais_repo = PaisRepository()
        aerogenerator_repo = AerogeneratorRepository()
        manufacturer_repo = ManufacturerRepository()
    except Exception as e:
        st.error(f"❌ Erro ao conectar com o banco de dados: {str(e)}")
        return
    
    # Sidebar com configurações
    st.sidebar.header("⚙️ Configurações da Análise")
    
    # 1. Seleção da cidade
    st.sidebar.markdown("""
    <div class="wind-info-card slide-in">
        <h4 class="wind-info-title">🌍 Localização</h4>
    </div>
    """, unsafe_allow_html=True)
    cidade_selecionada = None
    try:
        cidades_com_dados = met_repo.get_unique_cities_with_data()
        if not cidades_com_dados:
            st.sidebar.error("❌ Nenhuma cidade com dados meteorológicos encontrada.")
            st.sidebar.info("💡 Cadastre dados meteorológicos primeiro.")
            return
        
        opcoes_cidades = []
        cidades_dict = {}
        
        for cidade_info in cidades_com_dados:
            try:
                cidade_id = cidade_info['cidade_id']
                cidade_data = cidade_repo.buscar_por_id(cidade_id)
                
                if cidade_data:
                    regiao_data = regiao_repo.buscar_por_id(cidade_data.regiao_id)
                    pais_data = pais_repo.buscar_por_id(regiao_data.pais_id)
                    
                    opcao = f"{cidade_data.nome}, {regiao_data.nome}"
                    opcoes_cidades.append(opcao)
                    cidades_dict[opcao] = {
                        'cidade': cidade_data,
                        'regiao': regiao_data,
                        'pais': pais_data,
                        'dados_count': cidade_info['dados_count']
                    }
            except Exception as cidade_error:
                st.sidebar.warning(f"⚠️ Erro ao processar cidade {cidade_info.get('cidade_id', 'N/A')}: {str(cidade_error)}")
                continue
        
        if not opcoes_cidades:
            st.sidebar.error("❌ Nenhuma cidade válida encontrada.")
            return
        
        cidade_selecionada_key = st.sidebar.selectbox(
            "Cidade:",
            opcoes_cidades,
            help="Cidade com dados meteorológicos"
        )
        
        cidade_selecionada = cidades_dict.get(cidade_selecionada_key)
        
    except Exception as e:
        st.sidebar.error(f"❌ Erro ao carregar cidades: {str(e)}")
        with st.sidebar.expander("🔧 Detalhes do Erro"):
            st.code(str(e))
        return
    
    # 2. Seleção da turbina
    st.sidebar.markdown("""
    <div class="wind-info-card slide-in">
        <h4 class="wind-info-title">🌀 Turbina</h4>
    </div>
    """, unsafe_allow_html=True)
    turbina_selecionada = None
    try:
        fabricantes = manufacturer_repo.listar_todos()
        if not fabricantes:
            st.sidebar.error("❌ Nenhum fabricante encontrado no banco de dados.")
            st.sidebar.info("💡 Cadastre fabricantes e turbinas primeiro.")
            return
        
        opcoes_fabricantes = [f.name for f in fabricantes]
        fabricante_selecionado_nome = st.sidebar.selectbox("Fabricante:", opcoes_fabricantes)
        
        # Encontrar ID do fabricante
        try:
            fabricante_id = next(f.id for f in fabricantes if f.name == fabricante_selecionado_nome)
        except StopIteration:
            st.sidebar.error("❌ Fabricante selecionado não encontrado.")
            return
        
        # Buscar turbinas do fabricante
        try:
            aerogeneradores = aerogenerator_repo.buscar_por_fabricante(fabricante_id)
            if not aerogeneradores:
                st.sidebar.error("❌ Nenhuma turbina encontrada para este fabricante.")
                st.sidebar.info("💡 Cadastre turbinas para este fabricante.")
                return
            
            opcoes_turbinas = [f"{aero.model} ({aero.rated_power_kw}kW)" for aero in aerogeneradores]
            turbina_selecionada_nome = st.sidebar.selectbox("Turbina:", opcoes_turbinas)
            
            # Encontrar turbina selecionada
            try:
                turbina_index = opcoes_turbinas.index(turbina_selecionada_nome)
                turbina_selecionada = aerogeneradores[turbina_index]
            except (ValueError, IndexError):
                st.sidebar.error("❌ Turbina selecionada não encontrada.")
                return
                
        except Exception as turb_error:
            st.sidebar.error(f"❌ Erro ao carregar turbinas: {str(turb_error)}")
            return
        
    except Exception as e:
        st.sidebar.error(f"❌ Erro ao carregar dados de turbinas: {str(e)}")
        with st.sidebar.expander("🔧 Detalhes do Erro"):
            st.code(str(e))
        return
    
    # 3. Configurações de análise
    st.sidebar.markdown("""
    <div class="wind-info-card slide-in">
        <h4 class="wind-info-title">📊 Parâmetros de Análise</h4>
    </div>
    """, unsafe_allow_html=True)
    
    metodo_projecao = st.sidebar.selectbox(
        "Método de Projeção:",
        ["potencia", "logaritmica"],
        format_func=lambda x: "Lei de Potência" if x == "potencia" else "Lei Logarítmica"
    )
    
    # Parâmetros específicos do método
    if metodo_projecao == "potencia":
        terreno_tipo = st.sidebar.selectbox(
            "Tipo de Terreno:",
            ["agua", "plano", "pastagem", "arvores", "floresta", "cidade"],
            index=2,  # pastagem como padrão
            format_func=lambda x: {
                "agua": "Água/Lagos (n=0.10)",
                "plano": "Terreno Plano (n=0.16)", 
                "pastagem": "Pastagem (n=0.20)",
                "arvores": "Árvores Esparsas (n=0.22)",
                "floresta": "Floresta (n=0.28)",
                "cidade": "Área Urbana (n=0.40)"
            }[x]
        )
        
        parametros_terreno = {
            "agua": {"n": 0.10, "z0": 0.0002},
            "plano": {"n": 0.16, "z0": 0.03},
            "pastagem": {"n": 0.20, "z0": 0.10},
            "arvores": {"n": 0.22, "z0": 0.25},
            "floresta": {"n": 0.28, "z0": 1.00},
            "cidade": {"n": 0.40, "z0": 2.00}
        }
        
        parametros = parametros_terreno[terreno_tipo]
        st.sidebar.info(f"**Expoente n:** {parametros['n']}")
        
    else:  # logaritmica
        terreno_tipo = st.sidebar.selectbox(
            "Tipo de Terreno:",
            ["agua", "plano", "pastagem", "arvores", "floresta", "cidade"],
            index=2,  # pastagem como padrão
            format_func=lambda x: {
                "agua": "Água/Lagos (z0=0.0002m)",
                "plano": "Terreno Plano (z0=0.03m)",
                "pastagem": "Pastagem (z0=0.10m)",
                "arvores": "Árvores Esparsas (z0=0.25m)",
                "floresta": "Floresta (z0=1.00m)",
                "cidade": "Área Urbana (z0=2.00m)"
            }[x]
        )
        
        parametros_terreno = {
            "agua": {"n": 0.10, "z0": 0.0002},
            "plano": {"n": 0.16, "z0": 0.03},
            "pastagem": {"n": 0.20, "z0": 0.10},
            "arvores": {"n": 0.22, "z0": 0.25},
            "floresta": {"n": 0.28, "z0": 1.00},
            "cidade": {"n": 0.40, "z0": 2.00}
        }
        
        parametros = parametros_terreno[terreno_tipo]
        st.sidebar.info(f"**Rugosidade z0:** {parametros['z0']} m")
    
    altura_turbina = st.sidebar.number_input(
        "Altura da Turbina (m):",
        min_value=20.0,
        max_value=150.0,
        value=80.0,
        step=5.0
    )
    
    fonte_dados = st.sidebar.selectbox(
        "Fonte dos Dados:",
        ["nasa_power", "openmeteo"],
        format_func=lambda x: "NASA Power" if x == "nasa_power" else "OpenMeteo"
    )
    
    # Período de análise
    st.sidebar.markdown("""
    <div class="wind-info-card slide-in">
        <h4 class="wind-info-title">📅 Período</h4>
    </div>
    """, unsafe_allow_html=True)
    
    # Verificar datas disponíveis para a cidade selecionada
    try:
        if cidade_selecionada:
            cidade_id = cidade_selecionada['cidade'].id
            dados_cidade = met_repo.buscar_por_cidade(cidade_id)
            
            if dados_cidade:
                # Obter datas mínima e máxima disponíveis
                datas_disponiveis = [d.data_hora.date() for d in dados_cidade]
                data_min = min(datas_disponiveis)
                data_max = max(datas_disponiveis)
                total_dias = (data_max - data_min).days + 1
                
                st.sidebar.info(f"""
                **📊 Dados Disponíveis:**
                • De: {data_min.strftime('%d/%m/%Y')}
                • Até: {data_max.strftime('%d/%m/%Y')}
                • Total: {total_dias} dias
                • Registros: {len(dados_cidade)}
                """)
                
                # Opções de período baseadas nos dados disponíveis
                opcoes_periodo = []
                if total_dias >= 30:
                    opcoes_periodo.append(30)
                if total_dias >= 60:
                    opcoes_periodo.append(60)
                if total_dias >= 90:
                    opcoes_periodo.append(90)
                if total_dias >= 180:
                    opcoes_periodo.append(180)
                if total_dias >= 365:
                    opcoes_periodo.append(365)
                
                # Sempre incluir a opção de usar todos os dados
                opcoes_periodo.append(total_dias)
                
                periodo_dias = st.sidebar.selectbox(
                    "Período de Análise:",
                    opcoes_periodo,
                    index=min(2, len(opcoes_periodo)-1),  # Padrão: 90 dias ou menor disponível
                    format_func=lambda x: f"Últimos {x} dias" if x != total_dias else f"Todos os dados ({x} dias)"
                )
            else:
                # Fallback se não há dados
                periodo_dias = st.sidebar.selectbox(
                    "Período de Análise:",
                    [30, 60, 90, 180, 365],
                    index=2,
                    format_func=lambda x: f"Últimos {x} dias"
                )
        else:
            # Fallback se cidade não selecionada
            periodo_dias = st.sidebar.selectbox(
                "Período de Análise:",
                [30, 60, 90, 180, 365],
                index=2,
                format_func=lambda x: f"Últimos {x} dias"
            )
    except Exception as periodo_error:
        st.sidebar.warning(f"⚠️ Erro ao verificar período: {str(periodo_error)}")
        periodo_dias = st.sidebar.selectbox(
            "Período de Análise:",
            [30, 60, 90, 180, 365],
            index=2,
            format_func=lambda x: f"Últimos {x} dias"
        )
    
    # Botão de análise
    if st.sidebar.button("🚀 Executar Análise", type="primary"):
        
        # Verificar se dados necessários estão disponíveis
        if not cidade_selecionada:
            st.error("❌ Selecione uma cidade válida primeiro.")
            return
            
        if not turbina_selecionada:
            st.error("❌ Selecione uma turbina válida primeiro.")
            return
        
        with st.spinner("Executando análise simplificada..."):
            try:
                # Carregar dados meteorológicos
                try:
                    cidade_id = cidade_selecionada['cidade'].id
                    data_fim = datetime.now().date()
                    data_inicio = data_fim - timedelta(days=periodo_dias)
                    
                    # Buscar dados sem filtro de período primeiro
                    dados_met = met_repo.buscar_por_cidade(cidade_id)
                    
                    if not dados_met:
                        st.error("❌ Nenhum dado meteorológico encontrado para esta cidade.")
                        st.info("💡 Verifique se os dados meteorológicos foram coletados para esta cidade.")
                        return
                
                except Exception as met_error:
                    st.error(f"❌ Erro ao carregar dados meteorológicos: {str(met_error)}")
                    return
                
                # Buscar informações das fontes de dados
                try:
                    sources = source_repo.listar_todos()
                    source_map = {source.name.lower(): source.id for source in sources}
                    
                    # Obter todas as datas disponíveis primeiro
                    todas_datas = [d.data_hora.date() for d in dados_met]
                    data_mais_recente = max(todas_datas)
                    data_mais_antiga = min(todas_datas)
                    
                    # Calcular data de início baseada no período selecionado
                    if periodo_dias == len(dados_met) or periodo_dias >= (data_mais_recente - data_mais_antiga).days:
                        # Usar todos os dados disponíveis
                        data_inicio = data_mais_antiga
                        data_fim = data_mais_recente
                        st.info(f"📊 Usando todos os dados disponíveis: {data_inicio.strftime('%d/%m/%Y')} a {data_fim.strftime('%d/%m/%Y')}")
                    else:
                        # Usar período específico a partir da data mais recente
                        data_fim = data_mais_recente
                        data_inicio = data_fim - timedelta(days=periodo_dias-1)
                        
                        # Verificar se a data de início calculada não é anterior aos dados disponíveis
                        if data_inicio < data_mais_antiga:
                            data_inicio = data_mais_antiga
                            st.warning(f"⚠️ Período ajustado: usando dados de {data_inicio.strftime('%d/%m/%Y')} a {data_fim.strftime('%d/%m/%Y')}")
                        else:
                            st.info(f"📊 Analisando período: {data_inicio.strftime('%d/%m/%Y')} a {data_fim.strftime('%d/%m/%Y')}")
                    
                    # Filtrar por período usando as datas calculadas
                    dados_met = [d for d in dados_met if data_inicio <= d.data_hora.date() <= data_fim]
                    
                    if not dados_met:
                        st.error("❌ Nenhum dado encontrado no período especificado.")
                        return
                    
                    # Filtrar por fonte se especificado
                    fonte_id = source_map.get(fonte_dados.lower())
                    if fonte_id:
                        dados_fonte = [d for d in dados_met if d.meteorological_data_source_id == fonte_id]
                        if dados_fonte:
                            dados_met = dados_fonte
                            st.success(f"✅ Usando dados da fonte {fonte_dados.upper()}: {len(dados_met)} registros")
                        else:
                            st.warning(f"⚠️ Dados da fonte {fonte_dados} não encontrados. Usando dados disponíveis: {len(dados_met)} registros")
                    else:
                        st.info(f"ℹ️ Usando todos os dados disponíveis: {len(dados_met)} registros")
                    
                    if not dados_met:
                        st.error("❌ Nenhum dado meteorológico encontrado após filtros.")
                        return
                        
                except Exception as filter_error:
                    st.error(f"❌ Erro ao filtrar dados: {str(filter_error)}")
                    return
                
                # Preparar especificações da turbina
                try:
                    turbina_specs = {
                        'model': turbina_selecionada.model,
                        'rated_power_kw': float(turbina_selecionada.rated_power_kw),
                        'rotor_diameter_m': float(turbina_selecionada.rotor_diameter_m),
                        'cut_in_speed': float(turbina_selecionada.cut_in_speed),
                        'cut_out_speed': float(turbina_selecionada.cut_out_speed),
                        'rated_wind_speed': float(turbina_selecionada.rated_wind_speed)
                    }
                except Exception as spec_error:
                    st.error(f"❌ Erro ao processar especificações da turbina: {str(spec_error)}")
                    return
                
                # Processar dados
                resultados = []
                errors_count = 0
                for i, dado in enumerate(dados_met):
                    try:
                        # Verificar se dados essenciais estão disponíveis
                        if dado.velocidade_vento is None:
                            errors_count += 1
                            continue
                            
                        # Corrigir velocidade para altura da turbina
                        velocidade_corrigida = calcular_velocidade_corrigida(
                            float(dado.velocidade_vento),  # Converter para float
                            altura_turbina,
                            metodo_projecao,
                            parametros
                        )
                        
                        # Calcular potência
                        potencia = calcular_potencia_turbina(velocidade_corrigida, turbina_specs)
                        
                        # Classificar estado operacional
                        estado = classificar_estado_operacional(velocidade_corrigida, turbina_specs)
                        
                        resultados.append({
                            'datetime': dado.data_hora,  # Usar o atributo correto
                            'velocidade_10m': float(dado.velocidade_vento),  # Converter para float
                            'velocidade_corrigida': velocidade_corrigida,
                            'potencia_kw': potencia,
                            'estado_operacional': estado,
                            'temperatura': float(dado.temperatura) if dado.temperatura else None,
                            'umidade': float(dado.umidade) if dado.umidade else None
                        })
                        
                    except Exception as calc_error:
                        errors_count += 1
                        if errors_count <= 5:  # Mostrar apenas os primeiros 5 erros
                            st.warning(f"⚠️ Erro ao processar registro {i+1}: {str(calc_error)}")
                        continue
                
                if errors_count > 0:
                    st.info(f"ℹ️ {errors_count} registros foram ignorados devido a erros nos dados.")
                
                if not resultados:
                    st.error("❌ Nenhum resultado válido foi gerado. Verifique a qualidade dos dados.")
                    return
                
                # Converter para DataFrame
                try:
                    df_resultados = pd.DataFrame(resultados)
                    df_resultados['data'] = pd.to_datetime(df_resultados['datetime']).dt.date
                    
                    # Salvar resultados no session state
                    st.session_state['analise_simplificada'] = {
                        'df_resultados': df_resultados,
                        'cidade_info': cidade_selecionada,
                        'turbina_info': turbina_selecionada,
                        'parametros_analise': {
                            'metodo': metodo_projecao,
                            'altura': altura_turbina,
                            'fonte': fonte_dados,
                            'periodo': periodo_dias,
                            'parametros_terreno': parametros
                        }
                    }
                    
                    st.success("✅ Análise concluída!")
                    
                except Exception as df_error:
                    st.error(f"❌ Erro ao processar resultados: {str(df_error)}")
                    return
                
            except Exception as e:
                st.error(f"❌ Erro geral na análise: {str(e)}")
                with st.expander("🔧 Detalhes Técnicos do Erro"):
                    import traceback
                    st.code(traceback.format_exc())
                return
    
    # Exibir resultados se disponíveis
    if 'analise_simplificada' in st.session_state:
        try:
            exibir_resultados()
        except Exception as results_error:
            st.error(f"❌ Erro ao exibir resultados: {str(results_error)}")
            with st.expander("🔧 Detalhes do Erro"):
                import traceback
                st.code(traceback.format_exc())
            
            # Botão para limpar resultados em caso de erro
            if st.button("🗑️ Limpar Resultados"):
                if 'analise_simplificada' in st.session_state:
                    del st.session_state['analise_simplificada']
                st.rerun()


if __name__ == "__main__":
    try:
        main()
    except Exception as main_error:
        st.error(f"""
        # 🚨 Erro Crítico na Análise Simplificada
        
        A página encontrou um erro inesperado.
        
        **Erro:** {str(main_error)}
        
        **Soluções:**
        1. Recarregue a página (F5)
        2. Verifique se todos os dados necessários estão cadastrados
        3. Contate o suporte técnico se o problema persistir
        """)
        
        with st.expander("🔧 Detalhes Técnicos"):
            import traceback
            st.code(traceback.format_exc())
        
        # Botões de recuperação
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🔄 Recarregar Página", type="primary"):
                st.rerun()
        
        with col2:
            if st.button("🏠 Voltar ao Home"):
                st.switch_page("src/web/pages/0_home.py")

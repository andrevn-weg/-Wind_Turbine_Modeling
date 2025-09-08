"""
Tab de Detalhamento Avançado - Análises Meteorológicas

Contém a funcionalidade da aba "Detalhamento Avançado" com análises
estatísticas avançadas, correlações e insights detalhados por fonte e altura.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import math
from scipy import stats
from scipy.optimize import minimize
import matplotlib.pyplot as plt
import matplotlib.patches as patches


def render_advanced_details_tab(df):
    """
    Renderiza a aba de Detalhamento Avançado dos dados meteorológicos
    
    Args:
        df: DataFrame com dados meteorológicos processados
    """
    if df is None or df.empty:
        st.warning("Nenhum dado disponível para análise avançada.")
        return
    
    st.markdown("""
    <div class='section-header-minor'>
        <h4>🔬 Análise Avançada dos Dados Meteorológicos</h4>
        <p>Análises estatísticas detalhadas separadas por fonte e altura de captura.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Criar coluna combinada para fonte + altura
    df['fonte_altura'] = df['fonte'] + ' - ' + df['altura_captura'].astype(str) + 'm'
    
    # Análise de extremos por fonte/altura
    st.subheader("🎯 Análise de Valores Extremos por Fonte/Altura")
    
    extremos_data = []
    
    for fonte_altura in df['fonte_altura'].unique():
        df_subset = df[df['fonte_altura'] == fonte_altura]
        
        if not df_subset.empty:
            # Velocidade do vento
            vento_max_idx = df_subset['velocidade_vento'].idxmax()
            vento_min_idx = df_subset['velocidade_vento'].idxmin()
            
            extremos_data.append({
                'fonte_altura': fonte_altura,
                'vento_max': df_subset.loc[vento_max_idx, 'velocidade_vento'],
                'vento_max_data': df_subset.loc[vento_max_idx, 'data_hora'],
                'vento_min': df_subset.loc[vento_min_idx, 'velocidade_vento'],
                'vento_min_data': df_subset.loc[vento_min_idx, 'data_hora'],
                'total_registros': len(df_subset)
            })
            
            # Adicionar temperatura e umidade se disponível
            if 'temperatura' in df_subset.columns and df_subset['temperatura'].notna().any():
                temp_data = df_subset.dropna(subset=['temperatura'])
                if not temp_data.empty:
                    temp_max_idx = temp_data['temperatura'].idxmax()
                    temp_min_idx = temp_data['temperatura'].idxmin()
                    extremos_data[-1]['temp_max'] = temp_data.loc[temp_max_idx, 'temperatura']
                    extremos_data[-1]['temp_max_data'] = temp_data.loc[temp_max_idx, 'data_hora']
                    extremos_data[-1]['temp_min'] = temp_data.loc[temp_min_idx, 'temperatura']
                    extremos_data[-1]['temp_min_data'] = temp_data.loc[temp_min_idx, 'data_hora']
    
    if extremos_data:
        df_extremos = pd.DataFrame(extremos_data)
        st.dataframe(df_extremos, use_container_width=True)
    
    # Análise de distribuição estatística
    st.markdown("---")
    st.subheader("📊 Análise de Distribuição Estatística")
    
    # Histogramas por fonte/altura
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**🌪️ Distribuição da Velocidade do Vento**")
        
        fig_hist = px.histogram(
            df,
            x='velocidade_vento',
            color='fonte_altura',
            title="Distribuição da Velocidade do Vento por Fonte/Altura",
            labels={
                'velocidade_vento': 'Velocidade (m/s)',
                'count': 'Frequência',
                'fonte_altura': 'Fonte - Altura'
            },
            barmode='overlay',
            opacity=0.7
        )
        fig_hist.update_layout(height=400)
        st.plotly_chart(fig_hist, use_container_width=True)
    
    with col2:
        if 'temperatura' in df.columns and df['temperatura'].notna().any():
            st.markdown("**🌡️ Distribuição da Temperatura**")
            
            df_temp = df.dropna(subset=['temperatura'])
            if not df_temp.empty:
                fig_hist_temp = px.histogram(
                    df_temp,
                    x='temperatura',
                    color='fonte_altura',
                    title="Distribuição da Temperatura por Fonte/Altura",
                    labels={
                        'temperatura': 'Temperatura (°C)',
                        'count': 'Frequência',
                        'fonte_altura': 'Fonte - Altura'
                    },
                    barmode='overlay',
                    opacity=0.7
                )
                fig_hist_temp.update_layout(height=400)
                st.plotly_chart(fig_hist_temp, use_container_width=True)
        else:
            st.info("Dados de temperatura não disponíveis.")
    
    # Análise de Distribuição de Weibull
    st.markdown("---")
    st.subheader("🌀 Análise de Distribuição de Weibull")
    
    def fit_weibull_distribution(wind_speeds):
        """Ajusta uma distribuição de Weibull aos dados de velocidade do vento"""
        # Remover valores zero e negativos
        wind_speeds_clean = wind_speeds[wind_speeds > 0]
        
        if len(wind_speeds_clean) < 10:
            return None, None, None
        
        # Ajustar distribuição Weibull usando método dos momentos
        def weibull_moments_objective(params):
            c, k = params
            if c <= 0 or k <= 0:
                return 1e10
            
            try:
                mean_theoretical = c * math.gamma(1 + 1/k)
                var_theoretical = c**2 * (math.gamma(1 + 2/k) - (math.gamma(1 + 1/k))**2)
            except (ValueError, OverflowError):
                return 1e10
            
            mean_empirical = np.mean(wind_speeds_clean)
            var_empirical = np.var(wind_speeds_clean)
            
            return ((mean_theoretical - mean_empirical)**2 + (var_theoretical - var_empirical)**2)
        
        # Estimativas iniciais
        mean_ws = np.mean(wind_speeds_clean)
        std_ws = np.std(wind_speeds_clean)
        
        # Evitar divisão por zero e valores inválidos
        if std_ws == 0 or mean_ws == 0:
            return None, None, None
            
        k_init = max(0.5, min(10, (std_ws / mean_ws) ** (-1.086)))
        
        try:
            c_init = mean_ws / math.gamma(1 + 1/k_init)
        except (ValueError, OverflowError):
            c_init = mean_ws  # Fallback se gamma falhar
        
        try:
            result = minimize(weibull_moments_objective, [c_init, k_init], 
                            bounds=[(0.1, 50), (0.5, 10)], method='L-BFGS-B')
            c, k = result.x
            
            # Calcular R²
            hist, bin_edges = np.histogram(wind_speeds_clean, bins=20, density=True)
            bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2
            
            # PDF teórica de Weibull
            pdf_theoretical = (k/c) * (bin_centers/c)**(k-1) * np.exp(-(bin_centers/c)**k)
            
            # Calcular R² - garantir que ambos tenham o mesmo tamanho
            if len(hist) == len(pdf_theoretical):
                ss_res = np.sum((hist - pdf_theoretical)**2)
                ss_tot = np.sum((hist - np.mean(hist))**2)
                r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
            else:
                r_squared = 0
            
            return c, k, r_squared
        except:
            return None, None, None
    
    weibull_results = []
    
    # Gráfico de distribuições de Weibull por fonte/altura
    fig_weibull = make_subplots(
        rows=2, cols=2,
        subplot_titles=['Distribuição de Weibull por Fonte/Altura', 
                       'Parâmetros de Weibull', 
                       'Comparação Empírica vs Teórica',
                       'Função de Distribuição Acumulada'],
        specs=[[{"colspan": 2}, None],
               [{"type": "xy"}, {"type": "xy"}]]
    )
    
    colors = px.colors.qualitative.Set1
    color_idx = 0
    
    for fonte_altura in df['fonte_altura'].unique()[:5]:  # Limitar a 5 para performance
        df_subset = df[df['fonte_altura'] == fonte_altura]
        wind_speeds = df_subset['velocidade_vento'].values
        
        if len(wind_speeds) > 10:
            c, k, r_squared = fit_weibull_distribution(wind_speeds)
            
            if c is not None and k is not None:
                weibull_results.append({
                    'fonte_altura': fonte_altura,
                    'parametro_c_escala': round(c, 3),
                    'parametro_k_forma': round(k, 3),
                    'r_squared': round(r_squared, 3),
                    'velocidade_media': round(np.mean(wind_speeds), 2),
                    'total_registros': len(wind_speeds)
                })
                
                # Gerar dados teóricos de Weibull
                x_range = np.linspace(0.1, max(wind_speeds) * 1.2, 100)  # Evitar zero para log
                
                # Calcular PDF e CDF com tratamento de erro
                try:
                    weibull_pdf = (k/c) * (x_range/c)**(k-1) * np.exp(-(x_range/c)**k)
                    weibull_cdf = 1 - np.exp(-(x_range/c)**k)
                    
                    # Verificar se há valores inválidos
                    weibull_pdf = np.nan_to_num(weibull_pdf, nan=0, posinf=0, neginf=0)
                    weibull_cdf = np.nan_to_num(weibull_cdf, nan=0, posinf=1, neginf=0)
                    
                except (OverflowError, RuntimeWarning):
                    # Se houver overflow, usar valores mais conservadores
                    weibull_pdf = np.zeros_like(x_range)
                    weibull_cdf = np.zeros_like(x_range)
                
                # Adicionar curva PDF ao primeiro gráfico
                fig_weibull.add_trace(
                    go.Scatter(
                        x=x_range,
                        y=weibull_pdf,
                        mode='lines',
                        name=f'{fonte_altura} (c={c:.2f}, k={k:.2f})',
                        line=dict(color=colors[color_idx % len(colors)], width=2)
                    ),
                    row=1, col=1
                )
                
                # Adicionar histograma normalizado
                hist_data, bin_edges = np.histogram(wind_speeds, bins=20, density=True)
                bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2
                
                fig_weibull.add_trace(
                    go.Scatter(
                        x=bin_centers,
                        y=hist_data,
                        mode='markers',
                        name=f'{fonte_altura} (dados)',
                        marker=dict(color=colors[color_idx % len(colors)], opacity=0.6),
                        showlegend=False
                    ),
                    row=2, col=1
                )
                
                # Adicionar CDF
                fig_weibull.add_trace(
                    go.Scatter(
                        x=x_range,
                        y=weibull_cdf,
                        mode='lines',
                        name=f'{fonte_altura} CDF',
                        line=dict(color=colors[color_idx % len(colors)], dash='dash'),
                        showlegend=False
                    ),
                    row=2, col=2
                )
                
                color_idx += 1
    
    fig_weibull.update_xaxes(title_text="Velocidade do Vento (m/s)", row=1, col=1)
    fig_weibull.update_yaxes(title_text="Densidade de Probabilidade", row=1, col=1)
    fig_weibull.update_xaxes(title_text="Velocidade do Vento (m/s)", row=2, col=1)
    fig_weibull.update_yaxes(title_text="Densidade Empírica", row=2, col=1)
    fig_weibull.update_xaxes(title_text="Velocidade do Vento (m/s)", row=2, col=2)
    fig_weibull.update_yaxes(title_text="Probabilidade Acumulada", row=2, col=2)
    
    fig_weibull.update_layout(height=800, title_text="Análise de Distribuição de Weibull")
    st.plotly_chart(fig_weibull, use_container_width=True)
    
    if weibull_results:
        st.markdown("**📊 Parâmetros de Weibull por Fonte/Altura**")
        df_weibull = pd.DataFrame(weibull_results)
        st.dataframe(df_weibull, use_container_width=True)
        
        st.info("💡 **Parâmetros de Weibull:** c (escala) indica a velocidade característica, k (forma) indica a variabilidade. Valores de k entre 1,5-3,0 são típicos para vento.")
        
        # Versão melhorada com matplotlib para melhor visualização
        st.markdown("### 📈 Análise de Distribuição de Weibull - Versão Aprimorada")
        
        if len(weibull_results) > 0:
            # Configurar matplotlib para melhor qualidade
            plt.rcParams['figure.dpi'] = 150
            plt.rcParams['savefig.dpi'] = 150
            plt.rcParams['font.size'] = 10
            
            # Criar figura com subplots - 2x2 layout
            fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
            fig.suptitle('Análise Detalhada de Distribuição de Weibull', 
                        fontsize=16, fontweight='bold', y=0.95)
            
            # Cores distintas para cada fonte/altura
            colors_matplotlib = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
            
            # Subplot 1: PDFs Teóricas de Weibull
            ax1.set_title('Distribuições de Weibull Ajustadas (PDF)', fontweight='bold', fontsize=12)
            
            for idx, result in enumerate(weibull_results[:5]):  # Limitar a 5 para visualização
                fonte_altura = result['fonte_altura']
                c = result['parametro_c_escala']
                k = result['parametro_k_forma']
                
                # Gerar range de velocidades
                v_max = c * 3  # Aproximadamente 3 vezes o parâmetro de escala
                x_range = np.linspace(0.1, v_max, 200)
                
                # Calcular PDF de Weibull
                pdf_weibull = (k/c) * (x_range/c)**(k-1) * np.exp(-(x_range/c)**k)
                
                # Plotar curva
                line = ax1.plot(x_range, pdf_weibull, 
                               color=colors_matplotlib[idx % len(colors_matplotlib)], 
                               linewidth=2.5, 
                               label=f'{fonte_altura}\nc={c:.2f}, k={k:.2f}')
                
                # Adicionar pontos de destaque em velocidades específicas
                highlight_speeds = [c * 0.5, c, c * 1.5]  # 50%, 100% e 150% do parâmetro c
                for v_highlight in highlight_speeds:
                    if v_highlight <= v_max:
                        pdf_val = (k/c) * (v_highlight/c)**(k-1) * np.exp(-(v_highlight/c)**k)
                        ax1.plot(v_highlight, pdf_val, 'o', 
                                color=colors_matplotlib[idx % len(colors_matplotlib)], 
                                markersize=8, markeredgecolor='black', markeredgewidth=1)
                        # Adicionar valor no ponto
                        ax1.annotate(f'{pdf_val:.3f}', 
                                   (v_highlight, pdf_val), 
                                   xytext=(5, 5), textcoords='offset points',
                                   fontsize=8, 
                                   bbox=dict(boxstyle="round,pad=0.2", facecolor='white', alpha=0.8))
            
            ax1.set_xlabel('Velocidade do Vento (m/s)', fontweight='bold')
            ax1.set_ylabel('Densidade de Probabilidade', fontweight='bold')
            ax1.grid(True, alpha=0.3, linestyle='--')
            ax1.legend(loc='upper right', framealpha=0.9, fontsize=9)
            
            # Subplot 2: CDFs (Funções de Distribuição Acumulada)
            ax2.set_title('Funções de Distribuição Acumulada (CDF)', fontweight='bold', fontsize=12)
            
            for idx, result in enumerate(weibull_results[:5]):
                fonte_altura = result['fonte_altura']
                c = result['parametro_c_escala']
                k = result['parametro_k_forma']
                
                v_max = c * 3
                x_range = np.linspace(0.1, v_max, 200)
                
                # Calcular CDF de Weibull
                cdf_weibull = 1 - np.exp(-(x_range/c)**k)
                
                # Plotar curva
                ax2.plot(x_range, cdf_weibull, 
                        color=colors_matplotlib[idx % len(colors_matplotlib)], 
                        linewidth=2.5, 
                        label=f'{fonte_altura}')
                
                # Adicionar pontos de percentis importantes
                percentiles = [0.25, 0.5, 0.75, 0.9]  # 25%, 50%, 75%, 90%
                for p in percentiles:
                    # Calcular velocidade para o percentil p
                    v_percentil = c * (-np.log(1 - p))**(1/k)
                    if v_percentil <= v_max:
                        ax2.plot(v_percentil, p, 's', 
                                color=colors_matplotlib[idx % len(colors_matplotlib)], 
                                markersize=6, markeredgecolor='black', markeredgewidth=1)
                        # Adicionar valor no ponto
                        ax2.annotate(f'{v_percentil:.1f}m/s\n{p*100:.0f}%', 
                                   (v_percentil, p), 
                                   xytext=(5, -10), textcoords='offset points',
                                   fontsize=8, ha='center',
                                   bbox=dict(boxstyle="round,pad=0.2", facecolor='yellow', alpha=0.7))
            
            ax2.set_xlabel('Velocidade do Vento (m/s)', fontweight='bold')
            ax2.set_ylabel('Probabilidade Acumulada', fontweight='bold')
            ax2.grid(True, alpha=0.3, linestyle='--')
            ax2.legend(loc='lower right', framealpha=0.9, fontsize=9)
            
            # Subplot 3: Comparação Empírica vs Teórica
            ax3.set_title('Validação: Dados Empíricos vs Modelo Teórico', fontweight='bold', fontsize=12)
            
            for idx, result in enumerate(weibull_results[:3]):  # Limitar a 3 para clareza
                fonte_altura = result['fonte_altura']
                
                # Obter dados originais para esta fonte/altura
                df_subset = df[df['fonte_altura'] == fonte_altura]
                wind_speeds = df_subset['velocidade_vento'].values
                wind_speeds_clean = wind_speeds[wind_speeds > 0]
                
                if len(wind_speeds_clean) > 10:
                    # Histograma empírico
                    hist, bin_edges = np.histogram(wind_speeds_clean, bins=15, density=True)
                    bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2
                    
                    # Plotar histograma como barras
                    ax3.bar(bin_centers, hist, 
                           width=(bin_edges[1] - bin_edges[0]) * 0.8,
                           alpha=0.6, 
                           color=colors_matplotlib[idx % len(colors_matplotlib)],
                           label=f'{fonte_altura} (Empírico)',
                           edgecolor='black', linewidth=0.5)
                    
                    # Adicionar valores nas barras
                    for bc, h in zip(bin_centers, hist):
                        if h > 0.01:  # Só mostrar valores significativos
                            ax3.text(bc, h + 0.005, f'{h:.3f}', 
                                   ha='center', va='bottom', fontsize=8, fontweight='bold')
                    
                    # Curva teórica de Weibull
                    c = result['parametro_c_escala']
                    k = result['parametro_k_forma']
                    
                    x_range = np.linspace(0.1, max(wind_speeds_clean) * 1.1, 100)
                    pdf_theoretical = (k/c) * (x_range/c)**(k-1) * np.exp(-(x_range/c)**k)
                    
                    ax3.plot(x_range, pdf_theoretical, 
                            color=colors_matplotlib[idx % len(colors_matplotlib)], 
                            linewidth=3, linestyle='-',
                            label=f'{fonte_altura} (Teórico)')
            
            ax3.set_xlabel('Velocidade do Vento (m/s)', fontweight='bold')
            ax3.set_ylabel('Densidade de Probabilidade', fontweight='bold')
            ax3.grid(True, alpha=0.3, linestyle='--')
            ax3.legend(loc='upper right', framealpha=0.9, fontsize=9)
            
            # Subplot 4: Estatísticas e Parâmetros
            ax4.set_title('Parâmetros e Estatísticas de Ajuste', fontweight='bold', fontsize=12)
            
            # Criar gráfico de barras dos parâmetros
            fontes = [r['fonte_altura'] for r in weibull_results[:5]]
            c_values = [r['parametro_c_escala'] for r in weibull_results[:5]]
            k_values = [r['parametro_k_forma'] for r in weibull_results[:5]]
            r2_values = [r['r_squared'] for r in weibull_results[:5]]
            
            x_pos = np.arange(len(fontes))
            width = 0.25
            
            bars1 = ax4.bar(x_pos - width, c_values, width, label='Parâmetro c (escala)', 
                           color='skyblue', edgecolor='black', linewidth=1)
            bars2 = ax4.bar(x_pos, k_values, width, label='Parâmetro k (forma)', 
                           color='lightcoral', edgecolor='black', linewidth=1)
            bars3 = ax4.bar(x_pos + width, r2_values, width, label='R² (qualidade)', 
                           color='lightgreen', edgecolor='black', linewidth=1)
            
            # Adicionar valores nas barras
            for bars, values in [(bars1, c_values), (bars2, k_values), (bars3, r2_values)]:
                for bar, value in zip(bars, values):
                    height = bar.get_height()
                    ax4.text(bar.get_x() + bar.get_width()/2., height + 0.02,
                            f'{value:.2f}', ha='center', va='bottom', fontweight='bold', fontsize=9)
            
            ax4.set_xlabel('Fonte - Altura', fontweight='bold')
            ax4.set_ylabel('Valor do Parâmetro', fontweight='bold')
            ax4.set_xticks(x_pos)
            ax4.set_xticklabels([f.replace(' - ', '\n') for f in fontes], fontsize=9)
            ax4.legend(loc='upper left', framealpha=0.9, fontsize=9)
            ax4.grid(True, alpha=0.3, linestyle='--', axis='y')
            
            # Ajustar layout
            plt.tight_layout(rect=[0, 0.03, 1, 0.93])
            
            # Adicionar informações interpretativas
            info_text = f"""
            Análise de {len(weibull_results)} fonte(s)/altura(s) | 
            Parâmetros: c (velocidade característica), k (variabilidade) | 
            R² > 0.7 = bom ajuste
            """
            fig.text(0.02, 0.02, info_text, fontsize=10, 
                    bbox=dict(boxstyle="round,pad=0.3", facecolor='lightblue', alpha=0.8))
            
            # Mostrar no Streamlit
            st.pyplot(fig)
            plt.close()  # Limpar memória
            
            # Adicionar interpretação detalhada
            st.info("""
            📊 **Como Interpretar a Análise de Weibull:**
            
            🔹 **Primeiro painel (PDF):** Mostra a forma da distribuição - picos mais altos indicam concentração de velocidades
            🔹 **Segundo painel (CDF):** Percentis importantes - 50% = velocidade mediana, 90% = velocidades extremas
            🔹 **Terceiro painel:** Compara dados reais (barras) com modelo teórico (linha) - boa sobreposição = bom ajuste
            🔹 **Quarto painel:** Parâmetros numéricos - c ≈ velocidade média, k entre 1.5-3.0 é típico para vento
            
            💡 **Valores nos pontos:** Facilitam leitura precisa dos parâmetros e probabilidades para análise quantitativa
            """)
    
    # Projeções de Velocidade do Vento para Diferentes Alturas
    st.markdown("---")
    st.subheader("📈 Projeções para Diferentes Alturas - Lei de Potência e Lei Logarítmica")
    
    def get_terrain_description_power(n):
        """Retorna descrição do terreno baseado no expoente n"""
        descriptions = {
            0.10: "Superfície lisa, lago ou oceano",
            0.14: "Grama baixa",
            0.16: "Vegetação rasteira (até 0,3m)",
            0.20: "Arbustos, árvores ocasionais",
            0.22: "Árvores, construções ocasionais",
            0.24: "Árvores, construções ocasionais",
            0.28: "Áreas residenciais",
            0.40: "Áreas residenciais densas"
        }
        return descriptions.get(n, "Personalizado")
    
    # Seção de Configurações dos Parâmetros
    with st.expander("⚙️ Configurações dos Parâmetros", expanded=False):
        st.markdown("### 🔧 Parâmetros Configuráveis")
        
        col_config1, col_config2 = st.columns(2)
        
        with col_config1:
            st.markdown("**🌪️ Lei de Potência**")
            
            # Parâmetro n (expoente)
            n_value = st.selectbox(
                "Expoente n (tipo de terreno):",
                options=[0.10, 0.14, 0.16, 0.20, 0.22, 0.24, 0.28, 0.40],
                index=4,  # Default: 0.22
                format_func=lambda x: f"{x:.2f} - {get_terrain_description_power(x)}"
            )
            
            # Opção personalizada
            if st.checkbox("Usar valor personalizado para n"):
                n_value = st.slider("Expoente n personalizado:", 0.05, 0.50, 0.22, 0.01)
        
        with col_config2:
            st.markdown("**🌳 Lei Logarítmica**")
            
            # Parâmetro z0 (rugosidade)
            z0_options = {
                0.01: "Liso, gelo, lama",
                0.20: "Mar aberto e calmo", 
                0.50: "Mar agitado",
                3.00: "Neve",
                8.00: "Gramado",
                10.00: "Pasto acidentado",
                30.00: "Campo em declive",
                50.00: "Cultivado",
                100.00: "Poucas árvores",
                250.00: "Muitas árvores, poucos edifícios",
                500.00: "Florestas",
                1500.00: "Subúrbios",
                3000.00: "Zonas urbanas com edifícios altos"
            }
            
            z0_value = st.selectbox(
                "Rugosidade z₀ (mm):",
                options=list(z0_options.keys()),
                index=8,  # Default: 100.00 (Poucas árvores)
                format_func=lambda x: f"{x:.2f} - {z0_options[x]}"
            )
            
            # Converter para metros
            z0_meters = z0_value / 1000
            
            # Opção personalizada
            if st.checkbox("Usar valor personalizado para z₀"):
                z0_meters = st.slider("Rugosidade z₀ (m):", 0.00001, 5.0, 0.1, 0.00001, format="%.5f")
        
        # Configurações adicionais
        st.markdown("**📊 Configurações de Análise**")
        col_range1, col_range2 = st.columns(2)
        
        with col_range1:
            altura_min = st.number_input("Altura mínima (m):", min_value=1, max_value=50, value=5)
            altura_max = st.number_input("Altura máxima (m):", min_value=51, max_value=200, value=100)
        
        with col_range2:
            intervalo_altura = st.selectbox("Intervalo de altura:", [1, 2, 5, 10], index=2)
            mostrar_intersecao = st.checkbox("Destacar ponto de interseção", value=True)
    
    # Definir alturas para projeção baseado nas configurações
    target_heights = np.arange(altura_min, altura_max + 1, intervalo_altura)
    detailed_heights = np.arange(10, altura_max + 1, 10)
    
    def power_law_projection(v_ref, h_ref, h_target, alpha=None):
        """Projeção usando Lei de Potência: v = v_ref * (h/h_ref)^alpha"""
        if alpha is None:
            alpha = n_value
        return v_ref * (h_target / h_ref) ** alpha
    
    def log_law_projection(v_ref, h_ref, h_target, z0=None):
        """Projeção usando Lei Logarítmica: v = v_ref * ln(h/z0) / ln(h_ref/z0)"""
        if z0 is None:
            z0 = z0_meters
        if h_target <= z0 or h_ref <= z0:
            return np.nan
        return v_ref * np.log(h_target / z0) / np.log(h_ref / z0)
    
    # Análise Comparativa entre Fontes de Dados (OpenMeteo vs NASA_POWER)
    st.markdown("---")
    st.subheader("🌍 Impacto das Diferenças entre Fontes de Dados")
    
    # Analisar diferenças entre fontes
    fontes_disponiveis = df['fonte'].unique()
    
    if len(fontes_disponiveis) > 1:
        st.markdown("### 📊 Comparação de Velocidades Médias por Fonte")
        
        # Calcular estatísticas por fonte e altura
        fonte_stats = []
        for fonte in fontes_disponiveis:
            for altura in df['altura_captura'].unique():
                df_subset = df[(df['fonte'] == fonte) & (df['altura_captura'] == altura)]
                if len(df_subset) > 0:
                    fonte_stats.append({
                        'fonte': fonte,
                        'altura': altura,
                        'velocidade_media': df_subset['velocidade_vento'].mean(),
                        'velocidade_std': df_subset['velocidade_vento'].std(),
                        'num_registros': len(df_subset),
                        'velocidade_min': df_subset['velocidade_vento'].min(),
                        'velocidade_max': df_subset['velocidade_vento'].max()
                    })
        
        if fonte_stats:
            df_fonte_stats = pd.DataFrame(fonte_stats)
            
            # Mostrar tabela comparativa
            st.dataframe(df_fonte_stats, use_container_width=True)
            
            # Análise do impacto nas projeções
            st.markdown("### 🎯 Impacto nas Projeções - Comparação entre Fontes")
            
            # Selecionar altura de referência comum
            alturas_comuns = []
            for altura in df['altura_captura'].unique():
                tem_todas_fontes = all(
                    len(df[(df['fonte'] == fonte) & (df['altura_captura'] == altura)]) > 0 
                    for fonte in fontes_disponiveis
                )
                if tem_todas_fontes:
                    alturas_comuns.append(altura)
            
            if alturas_comuns:
                altura_ref_comum = st.selectbox(
                    "Selecionar altura de referência para comparação:",
                    options=alturas_comuns,
                    index=0
                )
                
                # Mostrar velocidades médias por fonte na altura de referência
                st.markdown(f"### 📊 Velocidades Médias na Altura de Referência ({altura_ref_comum}m)")
                
                velocidades_ref = {}
                col_metrics = st.columns(len(fontes_disponiveis))
                
                for idx, fonte in enumerate(fontes_disponiveis):
                    df_fonte = df[(df['fonte'] == fonte) & (df['altura_captura'] == altura_ref_comum)]
                    if len(df_fonte) > 0:
                        v_ref = df_fonte['velocidade_vento'].mean()
                        velocidades_ref[fonte] = v_ref
                        
                        with col_metrics[idx]:
                            st.metric(
                                label=f"🌪️ {fonte}",
                                value=f"{v_ref:.2f} m/s",
                                delta=f"±{df_fonte['velocidade_vento'].std():.2f}"
                            )
                
                # Calcular projeções para cada fonte
                projection_comparison = []
                
                # Criar gráfico unificado com cores específicas
                fig_unified = make_subplots(
                    rows=1, cols=1,
                    subplot_titles=['Comparação Completa: OpenMeteo (Verde) vs NASA_POWER (Vermelho)']
                )
                
                # Cores específicas para cada fonte
                source_colors = {
                    'OpenMeteo': "#080073",  # Azul
                    'NASA_POWER': '#d62728'  # Vermelho
                }
                
                # Gráficos de diferenças com cores diferentes
                fig_differences = make_subplots(
                    rows=2, cols=2,
                    subplot_titles=[
                        'Projeções Lei de Potência - Comparação',
                        'Projeções Lei Logarítmica - Comparação', 
                        'Diferenças Absolutas entre Fontes',
                        'Impacto Percentual das Diferenças'
                    ], print_grid=True
                )
                
                # Cores para gráficos de diferenças (evitando azul e vermelho)
                diff_colors = ['#2ca02c', '#ff7f0e', '#9467bd', '#8c564b', '#e377c2']
                
                # Processar cada fonte e adicionar aos gráficos
                fonte_data = {}
                
                for fonte in fontes_disponiveis:
                    df_fonte = df[(df['fonte'] == fonte) & (df['altura_captura'] == altura_ref_comum)]
                    
                    if len(df_fonte) > 0:
                        v_ref_fonte = df_fonte['velocidade_vento'].mean()
                        
                        # Calcular projeções para esta fonte
                        power_proj_fonte = [power_law_projection(v_ref_fonte, altura_ref_comum, h, n_value) for h in target_heights]
                        log_proj_fonte = [log_law_projection(v_ref_fonte, altura_ref_comum, h, z0_meters) for h in target_heights]
                        
                        # Armazenar dados da fonte
                        fonte_data[fonte] = {
                            'v_ref': v_ref_fonte,
                            'power_proj': power_proj_fonte,
                            'log_proj': log_proj_fonte
                        }
                        
                        # Armazenar para comparação
                        for i, h in enumerate(target_heights):
                            projection_comparison.append({
                                'fonte': fonte,
                                'altura_referencia': altura_ref_comum,
                                'altura_projecao': h,
                                'velocidade_referencia': round(v_ref_fonte, 2),
                                'lei_potencia': round(power_proj_fonte[i], 2),
                                'lei_logaritmica': round(log_proj_fonte[i], 2) if not np.isnan(log_proj_fonte[i]) else None
                            })
                        
                        # Determinar cor baseada na fonte
                        if fonte in source_colors:
                            color = source_colors[fonte]
                        else:
                            color = diff_colors[0]  # Cor padrão para outras fontes
                        
                        # Adicionar ao gráfico unificado - Lei de Potência
                        fig_unified.add_trace(
                            go.Scatter(
                                x=target_heights,
                                y=power_proj_fonte,
                                mode='lines+markers',
                                name=f'{fonte} - Lei de Potência',
                                line=dict(color=color, width=3),
                                marker=dict(size=6, symbol='circle')
                            )
                        )
                        
                        # Lei Logarítmica no mesmo gráfico
                        valid_log_fonte = [v for v in log_proj_fonte if not np.isnan(v)]
                        valid_heights_fonte = [target_heights[i] for i, v in enumerate(log_proj_fonte) if not np.isnan(v)]
                        
                        fig_unified.add_trace(
                            go.Scatter(
                                x=valid_heights_fonte,
                                y=valid_log_fonte,
                                mode='lines+markers',
                                name=f'{fonte} - Lei Logarítmica',
                                line=dict(color=color, dash='dash', width=3),
                                marker=dict(size=6, symbol='diamond')
                            )
                        )
                        
                        # Adicionar aos gráficos de comparação detalhada
                        fig_differences.add_trace(
                            go.Scatter(
                                x=target_heights,
                                y=power_proj_fonte,
                                mode='lines+markers',
                                name=f'{fonte} - Potência',
                                line=dict(color=color, width=2),
                                marker=dict(size=4),
                                showlegend=False
                            ),
                            row=1, col=1
                        )
                        
                        fig_differences.add_trace(
                            go.Scatter(
                                x=valid_heights_fonte,
                                y=valid_log_fonte,
                                mode='lines+markers',
                                name=f'{fonte} - Logarítmica',
                                line=dict(color=color, dash='dash', width=2),
                                marker=dict(size=4),
                                showlegend=False
                            ),
                            row=1, col=2
                        )
                
                # Adicionar ponto de interseção se solicitado
                if mostrar_intersecao and len(fonte_data) >= 2:
                    fontes_list = list(fonte_data.keys())
                    if len(fontes_list) >= 2:
                        fonte1, fonte2 = fontes_list[0], fontes_list[1]
                        
                        # Encontrar ponto de interseção das leis de potência
                        power1 = fonte_data[fonte1]['power_proj']
                        power2 = fonte_data[fonte2]['power_proj']
                        
                        # Encontrar altura onde as diferenças são mínimas
                        diff_power = [abs(p1 - p2) for p1, p2 in zip(power1, power2)]
                        min_diff_idx = np.argmin(diff_power)
                        intersect_height = target_heights[min_diff_idx]
                        intersect_value = (power1[min_diff_idx] + power2[min_diff_idx]) / 2
                        
                        # Adicionar ponto de interseção
                        fig_unified.add_trace(
                            go.Scatter(
                                x=[intersect_height],
                                y=[intersect_value],
                                mode='markers+text',
                                name='Ponto de Convergência',
                                marker=dict(size=15, color='yellow', symbol='star', 
                                          line=dict(width=3, color='black')),
                                text=[f'Convergência<br>h={intersect_height}m<br>v={intersect_value:.1f}m/s'],
                                textposition='top center',
                                textfont=dict(size=12, color='black')
                            )
                        )
                
                # Calcular diferenças entre fontes
                if len(fontes_disponiveis) >= 2:
                    fonte_base = fontes_disponiveis[0]
                    
                    for idx, fonte_comp in enumerate(fontes_disponiveis[1:]):
                        if fonte_base in fonte_data and fonte_comp in fonte_data:
                            power_base = fonte_data[fonte_base]['power_proj']
                            power_comp = fonte_data[fonte_comp]['power_proj']
                            log_base = fonte_data[fonte_base]['log_proj']
                            log_comp = fonte_data[fonte_comp]['log_proj']
                            
                            # Diferenças absolutas
                            diff_power = [abs(p_comp - p_base) for p_comp, p_base in zip(power_comp, power_base)]
                            diff_log = [abs(l_comp - l_base) for l_comp, l_base in zip(log_comp, log_base) if not np.isnan(l_comp) and not np.isnan(l_base)]
                            diff_heights_log = [target_heights[i] for i, (l_comp, l_base) in enumerate(zip(log_comp, log_base)) if not np.isnan(l_comp) and not np.isnan(l_base)]
                            
                            # Diferenças percentuais
                            perc_power = [abs(p_comp - p_base) / p_base * 100 if p_base > 0 else 0 for p_comp, p_base in zip(power_comp, power_base)]
                            perc_log = [abs(l_comp - l_base) / l_base * 100 if l_base > 0 else 0 for l_comp, l_base in zip(log_comp, log_base) if not np.isnan(l_comp) and not np.isnan(l_base)]
                            
                            # Usar cores diferentes para diferenças (evitando azul e vermelho)
                            diff_color = diff_colors[idx % len(diff_colors)]
                            
                            # Adicionar diferenças aos gráficos
                            fig_differences.add_trace(
                                go.Scatter(
                                    x=target_heights,
                                    y=diff_power,
                                    mode='lines+markers',
                                    name=f'Dif. Potência: {fonte_comp} vs {fonte_base}',
                                    line=dict(color=diff_color, width=2),
                                    marker=dict(size=5),
                                    showlegend=False
                                ),
                                row=2, col=1
                            )
                            
                            fig_differences.add_trace(
                                go.Scatter(
                                    x=target_heights,
                                    y=perc_power,
                                    mode='lines+markers',
                                    name=f'% Potência: {fonte_comp} vs {fonte_base}',
                                    line=dict(color=diff_color, width=2),
                                    marker=dict(size=5),
                                    showlegend=False
                                ),
                                row=2, col=2
                            )
                
                # Configurar layout do gráfico unificado
                fig_unified.update_xaxes(title_text="Altura (m)")
                fig_unified.update_yaxes(title_text="Velocidade do Vento (m/s)")
                fig_unified.update_layout(
                    height=600, 
                    title_text=f"Comparação Completa de Projeções (Ref: {altura_ref_comum}m)",
                    legend=dict(x=0.02, y=0.98),
                    hovermode='x unified'
                )
                
                # Configurar layouts dos gráficos de diferenças
                fig_differences.update_xaxes(title_text="Altura (m)", row=1, col=1)
                fig_differences.update_yaxes(title_text="Velocidade (m/s)", row=1, col=1)
                fig_differences.update_xaxes(title_text="Altura (m)", row=1, col=2)
                fig_differences.update_yaxes(title_text="Velocidade (m/s)", row=1, col=2)
                fig_differences.update_xaxes(title_text="Altura (m)", row=2, col=1)
                fig_differences.update_yaxes(title_text="Diferença Absoluta (m/s)", row=2, col=1)
                fig_differences.update_xaxes(title_text="Altura (m)", row=2, col=2)
                fig_differences.update_yaxes(title_text="Diferença Percentual (%)", row=2, col=2)
                
                fig_differences.update_layout(
                    height=800, 
                    title_text=f"Análise Detalhada de Diferenças (Ref: {altura_ref_comum}m)"
                )
                
                # Mostrar gráficos
                st.markdown("### 🔄 Gráfico Unificado de Comparação")
                st.plotly_chart(fig_unified, use_container_width=True)
                
                st.markdown("### 📊 Análise Detalhada de Diferenças")
                st.plotly_chart(fig_differences, use_container_width=True)
                
                # Versão melhorada com matplotlib para melhor visualização
                st.markdown("### 📈 Análise Detalhada de Diferenças - Versão Aprimorada")
                
                if len(fontes_disponiveis) >= 2:
                    # import matplotlib.pyplot as plt
                    # import matplotlib.patches as patches
                    
                    # Configurar matplotlib para melhor qualidade
                    plt.rcParams['figure.dpi'] = 150
                    plt.rcParams['savefig.dpi'] = 150
                    
                    # Criar figura com subplots
                    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
                    fig.suptitle(f'Análise Detalhada de Diferenças entre Fontes (Ref: {altura_ref_comum}m)', 
                                fontsize=16, fontweight='bold', y=0.95)
                    
                    # Cores específicas
                    colors_matplotlib = {
                        'OpenMeteo': '#1f77b4',  # Azul
                        'NASA_POWER': '#d62728',  # Vermelho
                        'diferenca': '#2ca02c'    # Verde para diferenças
                    }
                    
                    # Subplot 1: Projeções Lei de Potência
                    ax1.set_title('Projeções Lei de Potência - Comparação', fontweight='bold', fontsize=12)
                    
                    for fonte in fontes_disponiveis:
                        if fonte in fonte_data:
                            power_proj = fonte_data[fonte]['power_proj']
                            color = colors_matplotlib.get(fonte, '#1f77b4')
                            
                            # Plotar linha e pontos
                            line = ax1.plot(target_heights, power_proj, 
                                           marker='o', linewidth=2.5, markersize=6,
                                           label=f'{fonte}', color=color, alpha=0.8)
                            
                            # Adicionar valores nos pontos (apenas para alguns pontos para não poluir)
                            for i in range(0, len(target_heights), 4):  # A cada 4 pontos
                                ax1.annotate(f'{power_proj[i]:.1f}', 
                                           (target_heights[i], power_proj[i]),
                                           textcoords="offset points", xytext=(0,8), 
                                           ha='center', fontsize=8, color=color,
                                           weight='bold')
                    
                    ax1.set_xlabel('Altura (m)', fontweight='bold')
                    ax1.set_ylabel('Velocidade (m/s)', fontweight='bold')
                    ax1.grid(True, alpha=0.3, linestyle='--')
                    ax1.legend(loc='upper left', framealpha=0.9)
                    
                    # Subplot 2: Projeções Lei Logarítmica
                    ax2.set_title('Projeções Lei Logarítmica - Comparação', fontweight='bold', fontsize=12)
                    
                    for fonte in fontes_disponiveis:
                        if fonte in fonte_data:
                            log_proj = fonte_data[fonte]['log_proj']
                            valid_log = [v for v in log_proj if not np.isnan(v)]
                            valid_heights = [target_heights[i] for i, v in enumerate(log_proj) if not np.isnan(v)]
                            color = colors_matplotlib.get(fonte, '#1f77b4')
                            
                            if len(valid_log) > 0:
                                # Plotar linha e pontos
                                ax2.plot(valid_heights, valid_log, 
                                        marker='s', linewidth=2.5, markersize=6,
                                        label=f'{fonte}', color=color, alpha=0.8, linestyle='--')
                                
                                # Adicionar valores nos pontos
                                for i in range(0, len(valid_heights), 4):  # A cada 4 pontos
                                    ax2.annotate(f'{valid_log[i]:.1f}', 
                                               (valid_heights[i], valid_log[i]),
                                               textcoords="offset points", xytext=(0,8), 
                                               ha='center', fontsize=8, color=color,
                                               weight='bold')
                    
                    ax2.set_xlabel('Altura (m)', fontweight='bold')
                    ax2.set_ylabel('Velocidade (m/s)', fontweight='bold')
                    ax2.grid(True, alpha=0.3, linestyle='--')
                    ax2.legend(loc='upper left', framealpha=0.9)
                    
                    # Subplot 3: Diferenças Absolutas
                    if len(fontes_disponiveis) >= 2:
                        fonte_base = fontes_disponiveis[0]
                        fonte_comp = fontes_disponiveis[1]
                        
                        if fonte_base in fonte_data and fonte_comp in fonte_data:
                            power_base = fonte_data[fonte_base]['power_proj']
                            power_comp = fonte_data[fonte_comp]['power_proj']
                            log_base = fonte_data[fonte_base]['log_proj']
                            log_comp = fonte_data[fonte_comp]['log_proj']
                            
                            # Diferenças Lei de Potência
                            diff_power = [abs(p_comp - p_base) for p_comp, p_base in zip(power_comp, power_base)]
                            
                            ax3.set_title('Diferenças Absolutas entre Fontes', fontweight='bold', fontsize=12)
                            
                            # Plotar diferenças de potência
                            line1 = ax3.plot(target_heights, diff_power, 
                                           marker='o', linewidth=3, markersize=7,
                                           label=f'Lei de Potência: |{fonte_comp} - {fonte_base}|', 
                                           color='#2ca02c', alpha=0.8)
                            
                            # Adicionar valores nos pontos
                            for i in range(0, len(target_heights), 3):  # A cada 3 pontos
                                ax3.annotate(f'{diff_power[i]:.2f}', 
                                           (target_heights[i], diff_power[i]),
                                           textcoords="offset points", xytext=(0,10), 
                                           ha='center', fontsize=9, color='#2ca02c',
                                           weight='bold', bbox=dict(boxstyle="round,pad=0.2", 
                                                                  facecolor='white', alpha=0.7))
                            
                            # Diferenças Lei Logarítmica
                            diff_log = []
                            diff_heights_log = []
                            for i, (l_comp, l_base) in enumerate(zip(log_comp, log_base)):
                                if not np.isnan(l_comp) and not np.isnan(l_base):
                                    diff_log.append(abs(l_comp - l_base))
                                    diff_heights_log.append(target_heights[i])
                            
                            if len(diff_log) > 0:
                                ax3.plot(diff_heights_log, diff_log, 
                                        marker='s', linewidth=3, markersize=7,
                                        label=f'Lei Logarítmica: |{fonte_comp} - {fonte_base}|', 
                                        color='#ff7f0e', alpha=0.8, linestyle='--')
                                
                                # Adicionar valores nos pontos
                                for i in range(0, len(diff_heights_log), 3):
                                    ax3.annotate(f'{diff_log[i]:.2f}', 
                                               (diff_heights_log[i], diff_log[i]),
                                               textcoords="offset points", xytext=(0,10), 
                                               ha='center', fontsize=9, color='#ff7f0e',
                                               weight='bold', bbox=dict(boxstyle="round,pad=0.2", 
                                                                      facecolor='white', alpha=0.7))
                            
                            ax3.set_xlabel('Altura (m)', fontweight='bold')
                            ax3.set_ylabel('Diferença Absoluta (m/s)', fontweight='bold')
                            ax3.grid(True, alpha=0.3, linestyle='--')
                            ax3.legend(loc='upper left', framealpha=0.9)
                    
                    # Subplot 4: Diferenças Percentuais
                    if len(fontes_disponiveis) >= 2:
                        ax4.set_title('Impacto Percentual das Diferenças', fontweight='bold', fontsize=12)
                        
                        # Diferenças percentuais Lei de Potência
                        perc_power = [abs(p_comp - p_base) / p_base * 100 if p_base > 0 else 0 
                                     for p_comp, p_base in zip(power_comp, power_base)]
                        
                        ax4.plot(target_heights, perc_power, 
                                marker='o', linewidth=3, markersize=7,
                                label=f'Lei de Potência (%)', 
                                color='#9467bd', alpha=0.8)
                        
                        # Adicionar valores nos pontos
                        for i in range(0, len(target_heights), 4):  # A cada 4 pontos
                            ax4.annotate(f'{perc_power[i]:.1f}%', 
                                       (target_heights[i], perc_power[i]),
                                       textcoords="offset points", xytext=(0,10), 
                                       ha='center', fontsize=9, color='#9467bd',
                                       weight='bold', bbox=dict(boxstyle="round,pad=0.2", 
                                                              facecolor='white', alpha=0.7))
                        
                        # Diferenças percentuais Lei Logarítmica
                        if len(diff_log) > 0 and len(diff_heights_log) > 0:
                            perc_log = []
                            for i, (l_comp, l_base) in enumerate(zip(log_comp, log_base)):
                                if not np.isnan(l_comp) and not np.isnan(l_base) and l_base > 0:
                                    perc_log.append(abs(l_comp - l_base) / l_base * 100)
                                    
                            if len(perc_log) > 0:
                                ax4.plot(diff_heights_log[:len(perc_log)], perc_log, 
                                        marker='s', linewidth=3, markersize=7,
                                        label=f'Lei Logarítmica (%)', 
                                        color='#8c564b', alpha=0.8, linestyle='--')
                                
                                # Adicionar valores nos pontos
                                for i in range(0, len(perc_log), 4):
                                    if i < len(diff_heights_log):
                                        ax4.annotate(f'{perc_log[i]:.1f}%', 
                                                   (diff_heights_log[i], perc_log[i]),
                                                   textcoords="offset points", xytext=(0,10), 
                                                   ha='center', fontsize=9, color='#8c564b',
                                                   weight='bold', bbox=dict(boxstyle="round,pad=0.2", 
                                                                          facecolor='white', alpha=0.7))
                        
                        ax4.set_xlabel('Altura (m)', fontweight='bold')
                        ax4.set_ylabel('Diferença Percentual (%)', fontweight='bold')
                        ax4.grid(True, alpha=0.3, linestyle='--')
                        ax4.legend(loc='upper left', framealpha=0.9)
                        
                        # Adicionar linha de referência em 10%
                        ax4.axhline(y=10, color='red', linestyle=':', alpha=0.7, 
                                   label='Referência 10%')
                    
                    # Ajustar layout
                    plt.tight_layout(rect=[0, 0.03, 1, 0.93])
                    
                    # Adicionar informações dos parâmetros
                    fig.text(0.02, 0.02, f'Parâmetros: n = {n_value:.3f}, z₀ = {z0_meters:.4f} m', 
                            fontsize=10, bbox=dict(boxstyle="round,pad=0.3", facecolor='lightgray', alpha=0.8))
                    
                    # Mostrar no Streamlit
                    st.pyplot(fig)
                    plt.close()  # Limpar memória
                    
                    # Adicionar informações interpretativas
                    st.info("""
                    📊 **Como Interpretar o Gráfico:**
                    
                    🔹 **Primeiro painel:** Projeções Lei de Potência - Compare as curvas entre fontes
                    🔹 **Segundo painel:** Projeções Lei Logarítmica - Geralmente mais conservadora
                    🔹 **Terceiro painel:** Diferenças absolutas em m/s - Valores altos indicam maior discrepância
                    🔹 **Quarto painel:** Diferenças percentuais - Valores acima de 10% são significativos
                    
                    💡 **Valores nos pontos:** Mostram exatamente a magnitude das diferenças para facilitar análise numérica
                    """)
                
                # Tabela de comparação detalhada
                if projection_comparison:
                    st.markdown("### 📋 Tabela Comparativa Detalhada")
                    
                    df_proj_comp = pd.DataFrame(projection_comparison)
                    
                    # Pivotar para comparação lado a lado
                    if len(fontes_disponiveis) == 2:
                        fonte1, fonte2 = fontes_disponiveis
                        
                        df_f1 = df_proj_comp[df_proj_comp['fonte'] == fonte1]
                        df_f2 = df_proj_comp[df_proj_comp['fonte'] == fonte2]
                        
                        comparison_table = []
                        for h in target_heights[:10]:  # Limitar a 10 alturas para visualização
                            row_f1 = df_f1[df_f1['altura_projecao'] == h]
                            row_f2 = df_f2[df_f2['altura_projecao'] == h]
                            
                            if not row_f1.empty and not row_f2.empty:
                                pot_f1 = row_f1.iloc[0]['lei_potencia']
                                pot_f2 = row_f2.iloc[0]['lei_potencia']
                                log_f1 = row_f1.iloc[0]['lei_logaritmica']
                                log_f2 = row_f2.iloc[0]['lei_logaritmica']
                                
                                if log_f1 is not None and log_f2 is not None:
                                    comparison_table.append({
                                        'altura_m': h,
                                        f'{fonte1}_potencia': pot_f1,
                                        f'{fonte2}_potencia': pot_f2,
                                        'dif_potencia_abs': abs(pot_f1 - pot_f2),
                                        'dif_potencia_perc': abs(pot_f1 - pot_f2) / pot_f1 * 100 if pot_f1 > 0 else 0,
                                        f'{fonte1}_logaritmica': log_f1,
                                        f'{fonte2}_logaritmica': log_f2,
                                        'dif_log_abs': abs(log_f1 - log_f2) if log_f1 and log_f2 else None,
                                        'dif_log_perc': abs(log_f1 - log_f2) / log_f1 * 100 if log_f1 and log_f2 and log_f1 > 0 else None
                                    })
                        
                        if comparison_table:
                            df_comparison_table = pd.DataFrame(comparison_table)
                            st.dataframe(df_comparison_table, use_container_width=True)
                            
                            # Resumo estatístico das diferenças
                            st.markdown("### 📈 Resumo Estatístico das Diferenças")
                            col_stat1, col_stat2 = st.columns(2)
                            
                            with col_stat1:
                                st.markdown("**Lei de Potência:**")
                                st.metric("Diferença Média (m/s)", f"{df_comparison_table['dif_potencia_abs'].mean():.2f}")
                                st.metric("Diferença Máxima (m/s)", f"{df_comparison_table['dif_potencia_abs'].max():.2f}")
                                st.metric("Diferença Percentual Média (%)", f"{df_comparison_table['dif_potencia_perc'].mean():.1f}")
                            
                            with col_stat2:
                                if df_comparison_table['dif_log_abs'].notna().any():
                                    st.markdown("**Lei Logarítmica:**")
                                    st.metric("Diferença Média (m/s)", f"{df_comparison_table['dif_log_abs'].mean():.2f}")
                                    st.metric("Diferença Máxima (m/s)", f"{df_comparison_table['dif_log_abs'].max():.2f}")
                                    st.metric("Diferença Percentual Média (%)", f"{df_comparison_table['dif_log_perc'].mean():.1f}")
                
                # Análise de impacto
                st.markdown("### 🎯 Análise de Impacto")
                
                velocidades_ref = {}
                for fonte in fontes_disponiveis:
                    df_fonte = df[(df['fonte'] == fonte) & (df['altura_captura'] == altura_ref_comum)]
                    if len(df_fonte) > 0:
                        velocidades_ref[fonte] = df_fonte['velocidade_vento'].mean()
                
                if len(velocidades_ref) >= 2:
                    v_min = min(velocidades_ref.values())
                    v_max = max(velocidades_ref.values())
                    diff_ref = v_max - v_min
                    
                    st.info(f"""
                    📊 **Resumo do Impacto das Diferenças entre Fontes:**
                    
                    - **Diferença na velocidade de referência:** {diff_ref:.2f} m/s ({diff_ref/v_min*100:.1f}%)
                    - **Fonte com menor velocidade:** {min(velocidades_ref, key=velocidades_ref.get)} ({v_min:.2f} m/s)
                    - **Fonte com maior velocidade:** {max(velocidades_ref, key=velocidades_ref.get)} ({v_max:.2f} m/s)
                    
                    💡 **Implicações:** Esta diferença se amplifica nas projeções para alturas maiores, 
                    podendo resultar em estimativas de potencial eólico significativamente diferentes.
                    """)
            else:
                st.warning("Nenhuma altura comum encontrada entre as fontes para comparação.")
    else:
        st.info("Apenas uma fonte de dados disponível. Comparação entre fontes não é possível.")

    projection_results = []
    intersection_data = []
    
    # Selecionar dados de referência (altura mais comum ou especificada)
    height_counts = df['altura_captura'].value_counts()
    reference_heights = height_counts.head(3).index.tolist()  # Top 3 alturas mais comuns
    
    # Criar gráfico principal com análise de interseção
    fig_projections = make_subplots(
        rows=2, cols=2,
        subplot_titles=['Projeções - Lei de Potência vs Lei Logarítmica', 
                       'Análise de Interseção e Diferenças',
                       'Valores Detalhados a cada 10m',
                       'Correlação entre Alturas Coincidentes'],
        specs=[[{"type": "xy"}, {"type": "xy"}],
               [{"type": "xy"}, {"type": "xy"}]]
    )
    
    color_idx = 0
    
    for ref_height in reference_heights:
        # Filtrar dados para altura de referência
        df_ref = df[df['altura_captura'] == ref_height]
        
        if len(df_ref) > 0:
            avg_wind_speed = df_ref['velocidade_vento'].mean()
            
            # Calcular projeções com parâmetros configuráveis
            power_projections = [power_law_projection(avg_wind_speed, ref_height, h, n_value) for h in target_heights]
            log_projections = [log_law_projection(avg_wind_speed, ref_height, h, z0_meters) for h in target_heights]
            
            # Calcular projeções detalhadas para tabela
            detailed_power = [power_law_projection(avg_wind_speed, ref_height, h, n_value) for h in detailed_heights]
            detailed_log = [log_law_projection(avg_wind_speed, ref_height, h, z0_meters) for h in detailed_heights]
            
            # Encontrar ponto de interseção (como no MATLAB)
            valid_power = np.array([p for p, l in zip(power_projections, log_projections) if not np.isnan(l)])
            valid_log = np.array([l for p, l in zip(power_projections, log_projections) if not np.isnan(l)])
            valid_heights = np.array([h for h, p, l in zip(target_heights, power_projections, log_projections) if not np.isnan(l)])
            
            if len(valid_power) > 1 and len(valid_log) > 1:
                diff_curves = np.abs(valid_power - valid_log)
                idx_intersect = np.argmin(diff_curves)
                h_intersect = valid_heights[idx_intersect]
                v_intersect = valid_power[idx_intersect]
                min_diff = diff_curves[idx_intersect]
                
                intersection_data.append({
                    'altura_referencia': ref_height,
                    'velocidade_referencia': round(avg_wind_speed, 2),
                    'altura_intersecao': round(h_intersect, 1),
                    'velocidade_intersecao': round(v_intersect, 2),
                    'diferenca_minima': round(min_diff, 3),
                    'parametro_n': n_value,
                    'parametro_z0': z0_meters
                })
            
            # Armazenar resultados detalhados
            for i, h in enumerate(detailed_heights):
                if h <= altura_max:
                    power_val = power_law_projection(avg_wind_speed, ref_height, h, n_value)
                    log_val = log_law_projection(avg_wind_speed, ref_height, h, z0_meters)
                    
                    projection_results.append({
                        'altura_referencia': ref_height,
                        'altura_projecao': h,
                        'velocidade_referencia': round(avg_wind_speed, 2),
                        'lei_potencia': round(power_val, 2),
                        'lei_logaritmica': round(log_val, 2) if not np.isnan(log_val) else None,
                        'diferenca_absoluta': round(abs(power_val - log_val), 3) if not np.isnan(log_val) else None,
                        'diferenca_percentual': round(abs(power_val - log_val) / power_val * 100, 1) if not np.isnan(log_val) and power_val > 0 else None
                    })
            
            # Gráfico principal - Comparação das leis
            fig_projections.add_trace(
                go.Scatter(
                    x=target_heights,
                    y=power_projections,
                    mode='lines+markers',
                    name=f'Lei Potência - Ref: {ref_height}m',
                    line=dict(color=colors[color_idx % len(colors)], width=2),
                    marker=dict(size=4)
                ),
                row=1, col=1
            )
            
            # Adicionar lei logarítmica
            valid_log_full = [v for v in log_projections if not np.isnan(v)]
            valid_heights_full = [target_heights[i] for i, v in enumerate(log_projections) if not np.isnan(v)]
            
            fig_projections.add_trace(
                go.Scatter(
                    x=valid_heights_full,
                    y=valid_log_full,
                    mode='lines+markers',
                    name=f'Lei Logarítmica - Ref: {ref_height}m',
                    line=dict(color=colors[color_idx % len(colors)], dash='dash', width=2),
                    marker=dict(size=4)
                ),
                row=1, col=1
            )
            
            # Destacar ponto de interseção se solicitado
            if mostrar_intersecao and len(valid_power) > 1:
                fig_projections.add_trace(
                    go.Scatter(
                        x=[h_intersect],
                        y=[v_intersect],
                        mode='markers',
                        name=f'Interseção {ref_height}m ({h_intersect:.1f}m, {v_intersect:.2f}m/s)',
                        marker=dict(
                            size=12,
                            color='yellow',
                            line=dict(color='black', width=2),
                            symbol='star'
                        )
                    ),
                    row=1, col=1
                )
            
            # Gráfico de diferenças
            if len(valid_power) > 1 and len(valid_log) > 1:
                differences = np.abs(valid_power - valid_log)
                fig_projections.add_trace(
                    go.Scatter(
                        x=valid_heights,
                        y=differences,
                        mode='lines+markers',
                        name=f'Diferença Absoluta - Ref: {ref_height}m',
                        line=dict(color=colors[color_idx % len(colors)]),
                        marker=dict(size=4)
                    ),
                    row=1, col=2
                )
            
            # Gráfico detalhado a cada 10m (como no MATLAB)
            detailed_power_clean = [v for v in detailed_power if not np.isnan(v)]
            detailed_log_clean = [detailed_log[i] for i, v in enumerate(detailed_power) if not np.isnan(v)]
            detailed_heights_clean = [detailed_heights[i] for i, v in enumerate(detailed_power) if not np.isnan(v)]
            
            fig_projections.add_trace(
                go.Scatter(
                    x=detailed_heights_clean,
                    y=detailed_power_clean,
                    mode='markers+text',
                    name=f'Pontos 10m - Potência {ref_height}m',
                    marker=dict(size=8, color=colors[color_idx % len(colors)]),
                    text=[f'{v:.1f}' for v in detailed_power_clean],
                    textposition="top center",
                    textfont=dict(size=8, color=colors[color_idx % len(colors)]),
                    showlegend=False
                ),
                row=2, col=1
            )
            
            if len(detailed_log_clean) > 0:
                fig_projections.add_trace(
                    go.Scatter(
                        x=detailed_heights_clean,
                        y=detailed_log_clean,
                        mode='markers+text',
                        name=f'Pontos 10m - Log {ref_height}m',
                        marker=dict(size=8, color=colors[color_idx % len(colors)], symbol='diamond'),
                        text=[f'{v:.1f}' for v in detailed_log_clean],
                        textposition="bottom center",
                        textfont=dict(size=8, color=colors[color_idx % len(colors)]),
                        showlegend=False
                    ),
                    row=2, col=1
                )
            
            color_idx += 1
    
    # Análise de correlação para alturas coincidentes
    correlation_data = []
    unique_heights = df['altura_captura'].unique()
    
    for i, h1 in enumerate(unique_heights):
        for h2 in unique_heights[i+1:]:
            try:
                # Filtrar dados por altura
                df_h1 = df[df['altura_captura'] == h1].copy()
                df_h2 = df[df['altura_captura'] == h2].copy()
                
                # Converter para índice de data_hora
                df_h1 = df_h1.set_index('data_hora')
                df_h2 = df_h2.set_index('data_hora')
                
                # Encontrar timestamps coincidentes
                common_times = df_h1.index.intersection(df_h2.index)
                
                if len(common_times) > 10:  # Pelo menos 10 pontos coincidentes
                    # Extrair valores para os timestamps coincidentes
                    v1_common = df_h1.loc[common_times, 'velocidade_vento'].copy()
                    v2_common = df_h2.loc[common_times, 'velocidade_vento'].copy()
                    
                    # Verificar se ambas as séries têm o mesmo tamanho
                    if len(v1_common) == len(v2_common):
                        # Criar DataFrame temporário para facilitar a limpeza
                        temp_df = pd.DataFrame({
                            'v1': v1_common,
                            'v2': v2_common
                        })
                        
                        # Remover linhas com qualquer valor NaN
                        temp_df_clean = temp_df.dropna()
                        
                        if len(temp_df_clean) > 10:
                            v1_clean = temp_df_clean['v1'].values
                            v2_clean = temp_df_clean['v2'].values
                            
                            # Calcular correlação
                            correlation = np.corrcoef(v1_clean, v2_clean)[0, 1]
                            
                            correlation_data.append({
                                'altura_1': h1,
                                'altura_2': h2,
                                'correlacao': round(correlation, 3),
                                'pontos_coincidentes': len(v1_clean),
                                'ratio_teorico_potencia': round((h2/h1)**0.143, 3),
                                'ratio_empirico': round(v2_clean.mean() / v1_clean.mean(), 3)
                            })
                            
                            # Adicionar pontos de correlação ao gráfico
                            fig_projections.add_trace(
                                go.Scatter(
                                    x=v1_clean,
                                    y=v2_clean,
                                    mode='markers',
                                    name=f'{h1}m vs {h2}m',
                                    marker=dict(
                                        size=4,
                                        opacity=0.6,
                                        color=colors[(len(correlation_data)-1) % len(colors)]
                                    ),
                                    showlegend=False
                                ),
                                row=2, col=2
                            )
                            
            except (ValueError, RuntimeWarning, IndexError, KeyError) as e:
                # Log do erro para debugging (opcional) e continuar
                # print(f"Erro na correlação entre {h1}m e {h2}m: {e}")
                continue
    
    # Configurar layouts dos subplots
    fig_projections.update_xaxes(title_text="Altura (m)", row=1, col=1)
    fig_projections.update_yaxes(title_text="Velocidade do Vento (m/s)", row=1, col=1)
    fig_projections.update_xaxes(title_text="Altura (m)", row=1, col=2)
    fig_projections.update_yaxes(title_text="Diferença Absoluta (m/s)", row=1, col=2)
    fig_projections.update_xaxes(title_text="Altura (m)", row=2, col=1)
    fig_projections.update_yaxes(title_text="Velocidade do Vento (m/s)", row=2, col=1)
    fig_projections.update_xaxes(title_text="Velocidade Altura 1 (m/s)", row=2, col=2)
    fig_projections.update_yaxes(title_text="Velocidade Altura 2 (m/s)", row=2, col=2)
    
    # Adicionar informações dos parâmetros como anotação
    param_text = f"Parâmetros:<br>n = {n_value:.3f}<br>z₀ = {z0_meters:.3f} m"
    fig_projections.add_annotation(
        x=0.02, y=0.98,
        xref="paper", yref="paper",
        text=param_text,
        showarrow=False,
        font=dict(size=10),
        bgcolor="white",
        bordercolor="black",
        borderwidth=1
    )
    
    fig_projections.update_layout(height=800, title_text="Análise Comparativa: Lei de Potência vs Lei Logarítmica")
    st.plotly_chart(fig_projections, use_container_width=True)
    
    # Exibir tabelas de resultados
    col_results1, col_results2 = st.columns(2)
    
    with col_results1:
        # Tabela de interseções
        if intersection_data:
            st.markdown("**🎯 Pontos de Interseção das Curvas**")
            df_intersections = pd.DataFrame(intersection_data)
            st.dataframe(df_intersections, use_container_width=True)
            
            # Destacar informações importantes
            for idx, row in df_intersections.iterrows():
                st.info(f"📍 **Ref {row['altura_referencia']}m:** Interseção em {row['altura_intersecao']}m "
                       f"({row['velocidade_intersecao']} m/s) - Diferença: {row['diferenca_minima']} m/s")
    
    with col_results2:
        # Tabela de resultados detalhados
        if projection_results:
            st.markdown("**📊 Valores Detalhados (amostra)**")
            df_projections = pd.DataFrame(projection_results).head(15)
            st.dataframe(df_projections, use_container_width=True)
    
    # Tabela completa expansível
    if projection_results:
        with st.expander("📋 Tabela Completa de Resultados", expanded=False):
            df_complete = pd.DataFrame(projection_results)
            
            # Filtros para a tabela
            col_filter1, col_filter2 = st.columns(2)
            with col_filter1:
                selected_ref_height = st.selectbox(
                    "Filtrar por altura de referência:",
                    options=['Todas'] + df_complete['altura_referencia'].unique().tolist()
                )
            with col_filter2:
                show_only_differences = st.checkbox("Mostrar apenas diferenças > 0.5 m/s")
            
            # Aplicar filtros
            df_filtered = df_complete.copy()
            if selected_ref_height != 'Todas':
                df_filtered = df_filtered[df_filtered['altura_referencia'] == selected_ref_height]
            if show_only_differences:
                df_filtered = df_filtered[df_filtered['diferenca_absoluta'] > 0.5]
            
            st.dataframe(df_filtered, use_container_width=True)
            
            # Estatísticas resumidas
            if not df_filtered.empty:
                st.markdown("**� Estatísticas dos Resultados Filtrados**")
                stats_data = {
                    'Métrica': [
                        'Diferença Média (m/s)',
                        'Diferença Máxima (m/s)',
                        'Diferença Mínima (m/s)',
                        'Diferença Percentual Média (%)',
                        'Registros Analisados'
                    ],
                    'Valor': [
                        f"{df_filtered['diferenca_absoluta'].mean():.3f}",
                        f"{df_filtered['diferenca_absoluta'].max():.3f}",
                        f"{df_filtered['diferenca_absoluta'].min():.3f}",
                        f"{df_filtered['diferenca_percentual'].mean():.1f}",
                        f"{len(df_filtered)}"
                    ]
                }
                st.table(pd.DataFrame(stats_data))
    
    # Informações educativas
    st.markdown("---")
    with st.expander("ℹ️ Informações sobre os Métodos", expanded=False):
        st.markdown("""
        ### 🔬 **Lei de Potência**
        **Fórmula:** `v = v_ref × (h/h_ref)^n`
        
        **Parâmetro n (expoente):**
        - **0.10:** Superfície lisa, lago ou oceano
        - **0.14:** Grama baixa  
        - **0.16:** Vegetação rasteira (até 0,3m), árvores ocasionais
        - **0.20:** Arbustos, árvores ocasionais
        - **0.22-0.24:** Árvores, construções ocasionais
        - **0.28-0.40:** Áreas residenciais
        
        ### 🌳 **Lei Logarítmica**
        **Fórmula:** `v = v_ref × ln(h/z₀) / ln(h_ref/z₀)`
        
        **Parâmetro z₀ (rugosidade em mm):**
        - **0.01:** Liso, gelo, lama
        - **0.20:** Mar aberto e calmo
        - **8.00:** Gramado
        - **100.00:** Poucas árvores
        - **500.00:** Florestas
        - **1500.00:** Subúrbios
        - **3000.00:** Zonas urbanas com edifícios altos
        
        ### 📊 **Interpretação dos Resultados**
        - **Ponto de Interseção:** Altura onde ambos os métodos preveem a mesma velocidade
        - **Diferenças Baixas (< 0.5 m/s):** Ambos os métodos são equivalentes
        - **Diferenças Altas (> 1.0 m/s):** Escolha do método impacta significativamente os resultados
        """)
        
        st.info("💡 **Dica:** A Lei de Potência é mais simples e amplamente usada. A Lei Logarítmica é mais precisa para terrenos complexos com rugosidade bem definida.")
    
    # Tabela de correlações
    if correlation_data:
        st.markdown("**🔗 Correlações entre Alturas Coincidentes**")
        df_correlations = pd.DataFrame(correlation_data)
        st.dataframe(df_correlations, use_container_width=True)
        
        st.info("💡 **Interpretação:** Correlação próxima de 1 indica alta concordância entre alturas. O ratio teórico vs empírico mostra a precisão da Lei de Potência.")
    
    # Classificação do vento por fonte/altura
    st.markdown("---")
    st.subheader("🌀 Análise da Classificação do Vento por Fonte/Altura")
    
    if 'classificacao_vento' in df.columns:
        # Criar tabela cruzada
        classificacao_crosstab = pd.crosstab(
            df['classificacao_vento'], 
            df['fonte_altura'], 
            margins=True
        )
        
        st.dataframe(classificacao_crosstab, use_container_width=True)
        
        # Gráfico de barras empilhadas
        df_class_plot = df.groupby(['fonte_altura', 'classificacao_vento']).size().reset_index(name='count')
        
        fig_class = px.bar(
            df_class_plot,
            x='fonte_altura',
            y='count',
            color='classificacao_vento',
            title="Distribuição das Classificações de Vento por Fonte/Altura",
            labels={
                'count': 'Número de Registros',
                'fonte_altura': 'Fonte - Altura',
                'classificacao_vento': 'Classificação'
            }
        )
        fig_class.update_layout(
            height=500,
            xaxis_tickangle=-45
        )
        st.plotly_chart(fig_class, use_container_width=True)
    
    # Análise de correlação avançada
    st.markdown("---")
    st.subheader("🔗 Análise de Correlação Avançada")
    
    # Preparar dados para correlação
    colunas_numericas = ['velocidade_vento', 'altura_captura']
    
    if 'temperatura' in df.columns:
        colunas_numericas.append('temperatura')
    if 'umidade' in df.columns:
        colunas_numericas.append('umidade')
    
    # Adicionar variáveis temporais
    df_corr = df.copy()
    df_corr['hora'] = df_corr['data_hora'].dt.hour
    df_corr['dia_ano'] = df_corr['data_hora'].dt.dayofyear
    df_corr['mes'] = df_corr['data_hora'].dt.month
    
    colunas_numericas.extend(['hora', 'dia_ano', 'mes'])
    
    # Matriz de correlação por fonte/altura
    for fonte_altura in df['fonte_altura'].unique()[:3]:  # Limitar a 3 para performance
        st.markdown(f"**📈 Correlação para {fonte_altura}**")
        
        df_subset = df_corr[df_corr['fonte_altura'] == fonte_altura]
        
        if len(df_subset) > 1:
            correlation_matrix = df_subset[colunas_numericas].corr()
            
            fig_corr = px.imshow(
                correlation_matrix,
                text_auto=True,
                aspect="auto",
                title=f"Matriz de Correlação - {fonte_altura}",
                color_continuous_scale='RdBu_r'
            )
            fig_corr.update_layout(height=400)
            st.plotly_chart(fig_corr, use_container_width=True)
    
    # Análise temporal avançada
    st.markdown("---")
    st.subheader("⏰ Análise Temporal Avançada")
    
    # Padrões por hora do dia
    if len(df) > 24:
        df_temporal = df.copy()
        df_temporal['hora'] = df_temporal['data_hora'].dt.hour
        df_temporal['dia_semana'] = df_temporal['data_hora'].dt.day_name()
        df_temporal['mes'] = df_temporal['data_hora'].dt.month_name()
        
        # Heatmap por hora e fonte/altura
        hourly_avg = df_temporal.groupby(['hora', 'fonte_altura'])['velocidade_vento'].mean().reset_index()
        
        if not hourly_avg.empty:
            hourly_pivot = hourly_avg.pivot(index='hora', columns='fonte_altura', values='velocidade_vento')
            
            fig_hourly = px.imshow(
                hourly_pivot.T,
                title="Velocidade Média do Vento por Hora do Dia e Fonte/Altura",
                labels={
                    'x': 'Hora do Dia',
                    'y': 'Fonte - Altura',
                    'color': 'Velocidade (m/s)'
                },
                color_continuous_scale='viridis'
            )
            fig_hourly.update_layout(height=500)
            st.plotly_chart(fig_hourly, use_container_width=True)
    
    # Análise de tendências
    st.markdown("---")
    st.subheader("📈 Análise de Tendências")
    
    # Calcular tendências para cada fonte/altura
    tendencias_data = []
    
    for fonte_altura in df['fonte_altura'].unique():
        df_subset = df[df['fonte_altura'] == fonte_altura].sort_values('data_hora')
        
        if len(df_subset) > 10:  # Necessário pelo menos 10 pontos para tendência
            # Calcular tendência linear
            x = np.arange(len(df_subset))
            y = df_subset['velocidade_vento'].values
            
            # Regressão linear simples
            coeffs = np.polyfit(x, y, 1)
            tendencia = coeffs[0]  # coeficiente angular
            
            # R² para qualidade do ajuste
            y_pred = np.polyval(coeffs, x)
            r_squared = 1 - (np.sum((y - y_pred) ** 2) / np.sum((y - np.mean(y)) ** 2))
            
            tendencias_data.append({
                'fonte_altura': fonte_altura,
                'tendencia_ms_por_registro': tendencia,
                'tendencia_interpretacao': 'Crescente' if tendencia > 0 else 'Decrescente' if tendencia < 0 else 'Estável',
                'r_squared': r_squared,
                'qualidade_ajuste': 'Boa' if r_squared > 0.5 else 'Moderada' if r_squared > 0.2 else 'Baixa',
                'total_registros': len(df_subset)
            })
    
    if tendencias_data:
        df_tendencias = pd.DataFrame(tendencias_data)
        st.dataframe(df_tendencias, use_container_width=True)
        
        st.info("💡 A tendência indica se a velocidade do vento está aumentando ou diminuindo ao longo do tempo para cada fonte/altura.")
    
    # Análise de outliers
    st.markdown("---")
    st.subheader("🎯 Detecção de Outliers por Fonte/Altura")
    
    outliers_data = []
    
    for fonte_altura in df['fonte_altura'].unique():
        df_subset = df[df['fonte_altura'] == fonte_altura]
        
        if len(df_subset) > 4:  # Necessário pelo menos 5 pontos para quartis
            Q1 = df_subset['velocidade_vento'].quantile(0.25)
            Q3 = df_subset['velocidade_vento'].quantile(0.75)
            IQR = Q3 - Q1
            
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            
            outliers = df_subset[
                (df_subset['velocidade_vento'] < lower_bound) | 
                (df_subset['velocidade_vento'] > upper_bound)
            ]
            
            outliers_data.append({
                'fonte_altura': fonte_altura,
                'total_registros': len(df_subset),
                'outliers_detectados': len(outliers),
                'percentual_outliers': (len(outliers) / len(df_subset) * 100) if len(df_subset) > 0 else 0,
                'limite_inferior': lower_bound,
                'limite_superior': upper_bound,
                'outlier_maximo': outliers['velocidade_vento'].max() if len(outliers) > 0 else None,
                'outlier_minimo': outliers['velocidade_vento'].min() if len(outliers) > 0 else None
            })
    
    if outliers_data:
        df_outliers = pd.DataFrame(outliers_data)
        st.dataframe(df_outliers, use_container_width=True)
        
        st.info("📊 Outliers são valores que se desviam significativamente do padrão normal. Podem indicar eventos meteorológicos extremos ou erros de medição.")

"""
Subpágina para exclusão de dados meteorológicos

Esta página permite remover dados meteorológicos:
- Exclusão por período específico
- Exclusão completa de uma cidade
- Confirmações de segurança
- Relatório de exclusões realizadas
"""

import streamlit as st
import sys
from pathlib import Path
from datetime import datetime, date, timedelta
import pandas as pd
import traceback

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


def debug_dados_cidade(cidade_id):
    """
    Função de debug para investigar problemas nos dados
    """
    try:
        repo_dados = MeteorologicalDataRepository()
        dados_cidade = repo_dados.buscar_por_cidade(cidade_id)
        
        if not dados_cidade:
            return "Nenhum dado encontrado"
        
        debug_info = []
        debug_info.append(f"Total de registros encontrados: {len(dados_cidade)}")
        
        for i, dado in enumerate(dados_cidade[:5]):  # Apenas os primeiros 5 para debug
            debug_info.append(f"\nRegistro {i+1}:")
            debug_info.append(f"  ID: {dado.id}")
            debug_info.append(f"  Data/Hora: {dado.data_hora} (tipo: {type(dado.data_hora)})")
            debug_info.append(f"  Altura: {dado.altura_captura} (tipo: {type(dado.altura_captura)})")
            debug_info.append(f"  Fonte ID: {dado.meteorological_data_source_id}")
            
            if hasattr(dado.data_hora, 'tzinfo'):
                debug_info.append(f"  Timezone: {dado.data_hora.tzinfo}")
        
        return "\n".join(debug_info)
        
    except Exception as e:
        return f"Erro no debug: {str(e)}"


def obter_estatisticas_cidade(cidade_id):
    """
    Obtém estatísticas dos dados de uma cidade
    """
    try:
        repo_dados = MeteorologicalDataRepository()
        fonte_repo = MeteorologicalDataSourceRepository()
        
        dados_cidade = repo_dados.buscar_por_cidade(cidade_id)
        
        if not dados_cidade or len(dados_cidade) == 0:
            return None
        
        # Verificar se dados_cidade é uma lista válida
        if not isinstance(dados_cidade, list):
            st.error("Erro: Dados retornados não estão no formato esperado")
            return None
        
        # Buscar informações das fontes
        fontes = fonte_repo.listar_todos()
        fontes_map = {fonte.id: fonte.name for fonte in fontes}
        
        # Calcular estatísticas
        total_registros = len(dados_cidade)
        
        # Agrupar por fonte
        dados_por_fonte = {}
        datas_min_max = []
        alturas_unicas = set()
        
        for dado in dados_cidade:
            fonte_nome = fontes_map.get(dado.meteorological_data_source_id, "Desconhecida")
            if fonte_nome not in dados_por_fonte:
                dados_por_fonte[fonte_nome] = 0
            dados_por_fonte[fonte_nome] += 1
            
            if dado.data_hora:
                try:
                    # Normalizar datetime para evitar problemas de timezone
                    data_normalizada = dado.data_hora
                    
                    # Verificar se é datetime válido
                    if not isinstance(data_normalizada, datetime):
                        # Tentar converter se for string
                        if isinstance(data_normalizada, str):
                            data_normalizada = datetime.fromisoformat(data_normalizada.replace('T', ' ').replace('Z', ''))
                        else:
                            continue  # Pular este registro se não conseguir processar
                    
                    # Se tem timezone, converter para naive (UTC)
                    if data_normalizada.tzinfo is not None:
                        data_normalizada = data_normalizada.replace(tzinfo=None)
                    
                    datas_min_max.append(data_normalizada)
                except Exception as e_date:
                    # Log erro específico da data e continuar
                    print(f"Erro ao processar data {dado.data_hora}: {e_date}")
                    continue
            
            if dado.altura_captura:
                try:
                    altura_val = float(dado.altura_captura)
                    alturas_unicas.add(altura_val)
                except (ValueError, TypeError):
                    pass  # Ignorar alturas inválidas
        
        data_inicio = min(datas_min_max) if datas_min_max else None
        data_fim = max(datas_min_max) if datas_min_max else None
        
        return {
            'total_registros': total_registros,
            'dados_por_fonte': dados_por_fonte,
            'data_inicio': data_inicio,
            'data_fim': data_fim,
            'alturas': sorted(list(alturas_unicas))
        }
        
    except Exception as e:
        # Log mais detalhado do erro para debug
        error_details = traceback.format_exc()
        st.error(f"Erro ao obter estatísticas: {str(e)}")
        # Para debug, mostrar detalhes do erro (remover em produção)
        with st.expander("Detalhes do erro (debug)"):
            st.code(error_details)
        return None


def excluir_dados_periodo(cidade_id, data_inicio, data_fim, altura_especifica=None, fonte_especifica=None):
    """
    Exclui dados meteorológicos por período
    """
    try:
        repo_dados = MeteorologicalDataRepository()
        
        # Converter datas para datetime naive (sem timezone)
        data_inicio_dt = datetime.combine(data_inicio, datetime.min.time())
        data_fim_dt = datetime.combine(data_fim, datetime.max.time())
        
        # Buscar dados no período para confirmar
        dados_periodo = repo_dados.buscar_por_periodo(data_inicio_dt, data_fim_dt, cidade_id)
        
        # Filtrar por altura e fonte se especificado
        dados_para_excluir = []
        for dado in dados_periodo:
            incluir = True
            
            if altura_especifica and dado.altura_captura != altura_especifica:
                incluir = False
            
            if fonte_especifica and dado.meteorological_data_source_id != fonte_especifica:
                incluir = False
            
            if incluir:
                dados_para_excluir.append(dado)
        
        if not dados_para_excluir:
            return 0, "Nenhum dado encontrado no período especificado."
        
        # Excluir cada registro
        excluidos = 0
        for dado in dados_para_excluir:
            if repo_dados.excluir(dado.id):
                excluidos += 1
        
        return excluidos, f"Sucesso: {excluidos} registros excluídos."
        
    except Exception as e:
        return 0, f"Erro ao excluir dados: {str(e)}"


def excluir_todos_dados_cidade(cidade_id):
    """
    Exclui todos os dados meteorológicos de uma cidade
    """
    try:
        repo_dados = MeteorologicalDataRepository()
        
        # Buscar todos os dados da cidade
        dados_cidade = repo_dados.buscar_por_cidade(cidade_id)
        
        if not dados_cidade:
            return 0, "Nenhum dado encontrado para esta cidade."
        
        # Excluir todos os registros
        excluidos = 0
        for dado in dados_cidade:
            if repo_dados.excluir(dado.id):
                excluidos += 1
        
        return excluidos, f"Sucesso: {excluidos} registros excluídos."
        
    except Exception as e:
        return 0, f"Erro ao excluir dados: {str(e)}"


def delete_meteorological_data():
    """
    Função principal da página de exclusão de dados meteorológicos
    """
    # Cabeçalho da página
    st.markdown("""
    <div class="section-header">
        <h4>🗑️ Exclusão de Dados Meteorológicos</h4>
    </div>
    """, unsafe_allow_html=True)
    
    st.warning("⚠️ **Atenção:** Esta operação remove permanentemente os dados do banco. Use com cautela!")
    
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
        help="Selecione a cidade para gerenciar seus dados meteorológicos"
    )
    
    if not cidade_selecionada:
        return
    
    # Encontrar o ID da cidade selecionada
    cidade_id = None
    cidade_nome = ""
    for cidade_info in cidades_com_dados:
        if cidade_info[0] == cidade_selecionada:
            cidade_id = cidade_info[1]
            cidade_nome = cidade_info[2]
            break
    
    if not cidade_id:
        st.error("Erro ao identificar a cidade selecionada.")
        return
    
    # Obter estatísticas da cidade
    estatisticas = obter_estatisticas_cidade(cidade_id)
    
    if not estatisticas:
        st.warning(f"📭 Nenhum dado meteorológico encontrado para {cidade_nome}.")
        
        # Botão de debug para investigar o problema
        if st.button("🔍 Debug - Investigar dados"):
            debug_info = debug_dados_cidade(cidade_id)
            with st.expander("Informações de Debug"):
                st.text(debug_info)
        
        return
    
    # Exibir estatísticas
    st.markdown("---")
    st.markdown("### 📊 Estatísticas dos Dados")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total de Registros", estatisticas['total_registros'])
    
    with col2:
        if estatisticas['data_inicio'] and estatisticas['data_fim']:
            periodo = f"{estatisticas['data_inicio'].strftime('%d/%m/%Y')} a {estatisticas['data_fim'].strftime('%d/%m/%Y')}"
            st.metric("Período", periodo)
    
    with col3:
        alturas_str = ", ".join([f"{h}m" for h in estatisticas['alturas']]) if estatisticas['alturas'] else "N/A"
        st.metric("Alturas", alturas_str)
    
    # Distribuição por fonte
    if estatisticas['dados_por_fonte']:
        st.markdown("**Distribuição por Fonte:**")
        for fonte, quantidade in estatisticas['dados_por_fonte'].items():
            st.write(f"• {fonte}: {quantidade} registros")
    
    # Seção de exclusão
    st.markdown("---")
    st.markdown("### 🗑️ Opções de Exclusão")
    
    # Tipos de exclusão
    tipo_exclusao = st.radio(
        "Escolha o tipo de exclusão:",
        ["Exclusão por período", "Exclusão completa da cidade"],
        help="Selecione se deseja excluir dados de um período específico ou todos os dados da cidade"
    )
    
    if tipo_exclusao == "Exclusão por período":
        st.markdown("#### 📅 Exclusão por Período")
        
        col1, col2 = st.columns(2)
        
        with col1:
            data_inicio = st.date_input(
                "Data de início:",
                value=estatisticas['data_inicio'].date() if estatisticas['data_inicio'] else date.today(),
                min_value=estatisticas['data_inicio'].date() if estatisticas['data_inicio'] else None,
                max_value=estatisticas['data_fim'].date() if estatisticas['data_fim'] else None
            )
        
        with col2:
            data_fim = st.date_input(
                "Data de fim:",
                value=estatisticas['data_fim'].date() if estatisticas['data_fim'] else date.today(),
                min_value=data_inicio,
                max_value=estatisticas['data_fim'].date() if estatisticas['data_fim'] else None
            )
        
        # Filtros adicionais
        st.markdown("**Filtros Opcionais:**")
        col1, col2 = st.columns(2)
        
        with col1:
            # Filtro por altura
            opcoes_altura = ["Todas"] + [f"{h}m" for h in estatisticas['alturas']]
            altura_selecionada = st.selectbox("Altura específica:", opcoes_altura)
            altura_especifica = None
            if altura_selecionada != "Todas":
                altura_especifica = float(altura_selecionada.replace('m', ''))
        
        with col2:
            # Filtro por fonte
            try:
                fonte_repo = MeteorologicalDataSourceRepository()
                fontes = fonte_repo.listar_todos()
                opcoes_fonte = ["Todas"] + [fonte.name for fonte in fontes]
                fonte_selecionada = st.selectbox("Fonte específica:", opcoes_fonte)
                fonte_especifica = None
                if fonte_selecionada != "Todas":
                    for fonte in fontes:
                        if fonte.name == fonte_selecionada:
                            fonte_especifica = fonte.id
                            break
            except:
                fonte_especifica = None
        
        # Confirmação e execução
        if st.button("🗑️ Excluir Dados do Período", type="primary"):
            if data_inicio > data_fim:
                st.error("❌ A data de início deve ser anterior à data de fim.")
            else:
                # Confirmação adicional
                confirmacao = st.checkbox(
                    f"✅ Confirmo que desejo excluir os dados meteorológicos de {cidade_nome} "
                    f"no período de {data_inicio.strftime('%d/%m/%Y')} a {data_fim.strftime('%d/%m/%Y')}"
                )
                
                if confirmacao:
                    with st.spinner("Excluindo dados..."):
                        excluidos, mensagem = excluir_dados_periodo(
                            cidade_id, data_inicio, data_fim, altura_especifica, fonte_especifica
                        )
                    
                    if excluidos > 0:
                        st.success(mensagem)
                        st.balloons()
                        # Atualizar a página
                        st.rerun()
                    else:
                        st.warning(mensagem)
                else:
                    st.info("👆 Marque a confirmação acima para executar a exclusão.")
    
    else:  # Exclusão completa
        st.markdown("#### 🚨 Exclusão Completa da Cidade")
        
        st.error(f"⚠️ **ATENÇÃO:** Esta ação irá remover TODOS os {estatisticas['total_registros']} registros meteorológicos de {cidade_nome}!")
        
        # Confirmações múltiplas para segurança
        confirmacao1 = st.checkbox(f"✅ Entendo que todos os dados de {cidade_nome} serão perdidos permanentemente")
        confirmacao2 = st.checkbox(f"✅ Confirmo que desejo excluir TODOS os {estatisticas['total_registros']} registros")
        
        # Campo de confirmação por texto
        texto_confirmacao = st.text_input(
            label=f'Digite "{cidade_nome}" para confirmar a exclusão completa:',
            help="Digite exatamente o nome da cidade para confirmar",
            value=f'{cidade_nome}',
            icon="✍️"
        )
        
        confirmacao_texto = texto_confirmacao.strip() == cidade_nome
        
        if confirmacao1 and confirmacao2 and confirmacao_texto:
            if st.button("🚨 EXCLUIR TODOS OS DADOS", type="primary"):
                with st.spinner("Excluindo todos os dados..."):
                    excluidos, mensagem = excluir_todos_dados_cidade(cidade_id)
                
                if excluidos > 0:
                    st.success(mensagem)
                    st.balloons()
                    # Atualizar a página
                    st.rerun()
                else:
                    st.error(mensagem)
        else:
            st.info("👆 Complete todas as confirmações acima para executar a exclusão completa.")
    
    # Avisos de segurança
    st.markdown("---")
    st.info("""
    💡 **Dicas de Segurança:**
    
    • **Backup:** Considere fazer backup dos dados antes de excluir
    • **Visualização:** Use a aba 'Visualizar Dados' para conferir os dados antes de excluir
    • **Período específico:** Para manter alguns dados, use a exclusão por período
    • **Irreversível:** Dados excluídos não podem ser recuperados
    """)

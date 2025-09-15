"""
Módulo para processamento de dados meteorológicos da análise simplificada
"""

def obter_mapeamento_fontes_correto(sources):
    """
    Cria mapeamento correto das fontes de dados.
    
    O problema anterior era usar source.name.lower(), mas as opções do selectbox
    são 'nasa_power' e 'openmeteo', enquanto no banco pode estar 'NASA_POWER' e 'OPEN_METEO'
    """
    source_map = {}
    
    for source in sources:
        fonte_nome = source.name.upper()
        
        # Mapeamento correto baseado nos nomes reais do banco
        if fonte_nome in ['NASA_POWER', 'NASA POWER']:
            source_map['nasa_power'] = source.id
        elif fonte_nome in ['OPEN_METEO', 'OPENMETEO', 'OPEN METEO']:
            source_map['openmeteo'] = source.id
        # Adicionar outras fontes conforme necessário
        
        # Também adicionar o nome original em lowercase para compatibilidade
        source_map[source.name.lower()] = source.id
    
    return source_map


def filtrar_dados_por_fonte_e_periodo(dados_met, fonte_dados, source_map, data_inicio, data_fim):
    """
    Filtra dados meteorológicos por fonte e período.
    
    Args:
        dados_met: Lista de dados meteorológicos
        fonte_dados: Nome da fonte selecionada ('nasa_power', 'openmeteo', 'todos')
        source_map: Mapeamento de fontes
        data_inicio: Data de início do período
        data_fim: Data de fim do período
    
    Returns:
        dados_filtrados, mensagem_info
    """
    import streamlit as st
    
    # Filtrar por período
    dados_periodo = [d for d in dados_met if data_inicio <= d.data_hora.date() <= data_fim]
    
    if not dados_periodo:
        return [], "❌ Nenhum dado encontrado no período especificado."
    
    # Filtrar por fonte se especificado
    if fonte_dados.lower() == 'todos':
        mensagem = f"ℹ️ Usando todos os dados disponíveis: {len(dados_periodo)} registros"
        return dados_periodo, mensagem
    
    fonte_id = source_map.get(fonte_dados.lower())
    if fonte_id:
        dados_fonte = [d for d in dados_periodo if d.meteorological_data_source_id == fonte_id]
        if dados_fonte:
            mensagem = f"✅ Usando dados da fonte {fonte_dados.upper()}: {len(dados_fonte)} registros"
            return dados_fonte, mensagem
        else:
            mensagem = f"⚠️ Dados da fonte {fonte_dados} não encontrados. Usando todos os dados: {len(dados_periodo)} registros"
            return dados_periodo, mensagem
    else:
        mensagem = f"⚠️ Fonte {fonte_dados} não mapeada. Usando todos os dados: {len(dados_periodo)} registros"
        return dados_periodo, mensagem


def agrupar_dados_por_fonte_altura(dados_originais, fontes_info):
    """
    Agrupa dados por fonte E altura, criando chaves únicas para cada combinação.
    
    Exemplo de agrupamento:
    - NASA_POWER (10m)
    - NASA_POWER (50m) 
    - OPEN_METEO (10m)
    """
    # Criar mapeamento de fontes por ID
    fonte_map = {fonte.id: fonte for fonte in fontes_info}
    
    # Agrupar dados por fonte e altura (chave única para cada combinação)
    dados_por_fonte_altura = {}
    
    for dado in dados_originais:
        if dado.velocidade_vento is not None:
            fonte_id = dado.meteorological_data_source_id
            altura = float(dado.altura_captura) if dado.altura_captura else 10.0
            
            # Verificar se a fonte existe no mapeamento
            if fonte_id not in fonte_map:
                continue
            
            fonte_nome = fonte_map[fonte_id].name.replace('_', ' ').title()
            # Chave única: fonte + altura
            chave = f"{fonte_nome} ({altura:.0f}m)"
            
            if chave not in dados_por_fonte_altura:
                dados_por_fonte_altura[chave] = {
                    'fonte_id': fonte_id,
                    'fonte_nome': fonte_nome,
                    'fonte_nome_original': fonte_map[fonte_id].name,
                    'altura': altura,
                    'velocidades': [],
                    'dados': [],
                    'data_inicio': dado.data_hora,
                    'data_fim': dado.data_hora
                }
            
            dados_por_fonte_altura[chave]['velocidades'].append(float(dado.velocidade_vento))
            dados_por_fonte_altura[chave]['dados'].append(dado)
            
            # Atualizar data de início e fim
            if dado.data_hora < dados_por_fonte_altura[chave]['data_inicio']:
                dados_por_fonte_altura[chave]['data_inicio'] = dado.data_hora
            if dado.data_hora > dados_por_fonte_altura[chave]['data_fim']:
                dados_por_fonte_altura[chave]['data_fim'] = dado.data_hora
    
    return dados_por_fonte_altura


def calcular_estatisticas_por_grupo(dados_por_fonte_altura):
    """
    Calcula estatísticas para cada grupo fonte-altura.
    """
    for chave, info in dados_por_fonte_altura.items():
        velocidades = info['velocidades']
        if velocidades:
            info['media'] = sum(velocidades) / len(velocidades)
            info['mediana'] = sorted(velocidades)[len(velocidades)//2]
            info['minima'] = min(velocidades)
            info['maxima'] = max(velocidades)
            info['registros'] = len(velocidades)
    
    return dados_por_fonte_altura


def organizar_por_fonte(dados_por_fonte_altura):
    """
    Organiza dados agrupados por fonte para exibição.
    
    Returns:
        dict: {fonte_nome: [(chave, info), ...]}
    """
    fontes_organizadas = {}
    
    for chave, info in dados_por_fonte_altura.items():
        fonte_nome = info['fonte_nome']
        if fonte_nome not in fontes_organizadas:
            fontes_organizadas[fonte_nome] = []
        fontes_organizadas[fonte_nome].append((chave, info))
    
    # Ordenar alturas dentro de cada fonte
    for fonte_nome in fontes_organizadas:
        fontes_organizadas[fonte_nome].sort(key=lambda x: x[1]['altura'])
    
    return fontes_organizadas
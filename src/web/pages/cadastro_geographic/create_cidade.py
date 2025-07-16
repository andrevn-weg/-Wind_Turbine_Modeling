import streamlit as st
import sys
from pathlib import Path

# Adicionar src ao path para imports
src_path = Path(__file__).parent.parent.parent.parent / "src"
sys.path.insert(0, str(src_path))

from geographic import Pais, Regiao, Cidade, PaisRepository, RegiaoRepository, CidadeRepository


def create_cidade():
    """
    Interface para cadastro de cidades
    """
    st.subheader("🏙️ Cadastro de Cidade")
    
    # Carregar países e regiões disponíveis
    try:
        pais_repo = PaisRepository()
        regiao_repo = RegiaoRepository()
        pais_repo.criar_tabela()
        regiao_repo.criar_tabela()
        
        paises = pais_repo.listar_todos()
        
        if not paises:
            st.error("❌ Nenhum país cadastrado. Cadastre um país primeiro!")
            if st.button("➕ Ir para Cadastro de País"):
                st.session_state.selected_tab = "pais"
                st.rerun()
            return
            
    except Exception as e:
        st.error(f"Erro ao carregar dados: {str(e)}")
        return
    
    with st.form("form_cidade", clear_on_submit=False):
        st.markdown("### Dados da Cidade")
        
        # Seleção do país
        pais_opcoes = {f"{p.nome} ({p.codigo})": p for p in paises}
        pais_selecionado = st.selectbox(
            "País *",
            options=list(pais_opcoes.keys()),
            help="Selecione o país ao qual esta cidade pertence"
        )
        
        pais_obj = pais_opcoes[pais_selecionado] if pais_selecionado else None
        regiao_obj = None
        
        # Carregar regiões do país selecionado
        if pais_obj:
            try:
                regioes = regiao_repo.buscar_por_pais(pais_obj.id)
                
                if regioes:
                    regiao_opcoes = {f"{r.nome_completo()}": r for r in regioes}
                    regiao_opcoes["Não informar região"] = None
                    
                    regiao_selecionada = st.selectbox(
                        "Estado/Região",
                        options=list(regiao_opcoes.keys()),
                        help="Selecione o estado/região (opcional)"
                    )
                    
                    regiao_obj = regiao_opcoes[regiao_selecionada] if regiao_selecionada != "Não informar região" else None
                else:
                    st.info(f"ℹ️ Nenhuma região cadastrada para {pais_obj.nome}. A cidade será cadastrada sem região específica.")
                    
            except Exception as e:
                st.warning(f"Erro ao carregar regiões: {str(e)}")
        
        # Dados básicos da cidade
        col1, col2 = st.columns(2)
        
        with col1:
            nome = st.text_input(
                "Nome da Cidade *", 
                placeholder="Ex: Jaraguá do Sul, São Paulo, Miami",
                help="Nome completo da cidade"
            )
        
        with col2:
            populacao = st.number_input(
                "População",
                min_value=0,
                value=None,
                help="População estimada da cidade (opcional)"
            )
        
        # Coordenadas geográficas
        st.markdown("#### 📍 Coordenadas Geográficas")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            latitude = st.number_input(
                "Latitude *",
                min_value=-90.0,
                max_value=90.0,
                value=0.0,
                step=0.000001,
                format="%.6f",
                help="Latitude em graus decimais (-90 a 90)"
            )
        
        with col2:
            longitude = st.number_input(
                "Longitude *",
                min_value=-180.0,
                max_value=180.0,
                value=0.0,
                step=0.000001,
                format="%.6f",
                help="Longitude em graus decimais (-180 a 180)"
            )
        
        with col3:
            altitude = st.number_input(
                "Altitude (m)",
                min_value=-500.0,
                max_value=9000.0,
                value=None,
                help="Altitude média em metros (opcional)"
            )
        
        # Notas adicionais
        notes = st.text_area(
            "Notas Adicionais",
            placeholder="Informações extras sobre a cidade...",
            help="Informações complementares (opcional)"
        )
        
        # Validações visuais
        if nome and len(nome.strip()) > 0:
            st.success(f"✅ Nome válido: {nome}")
        elif nome:
            st.error("❌ Nome não pode estar vazio")
        
        if latitude != 0.0 or longitude != 0.0:
            st.success(f"✅ Coordenadas válidas: {latitude}, {longitude}")
            
            # Mostrar mapa se possível
            if st.checkbox("🗺️ Visualizar no mapa"):
                import pandas as pd
                map_data = pd.DataFrame({
                    'lat': [latitude],
                    'lon': [longitude]
                })
                st.map(map_data)
        
        st.markdown("---")
        
        # Botões
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col2:
            submitted = st.form_submit_button(
                "💾 Salvar Cidade", 
                type="primary", 
                use_container_width=True
            )
        
        if submitted and pais_obj:
            # Criar e validar cidade
            cidade = Cidade(
                nome=nome.strip(),
                regiao_id=regiao_obj.id if regiao_obj else None,
                pais_id=pais_obj.id,
                latitude=latitude,
                longitude=longitude,
                populacao=populacao if populacao and populacao > 0 else None,
                altitude=altitude if altitude is not None else None,
                notes=notes.strip() if notes.strip() else None
            )
            
            if not cidade.validar():
                st.error("❌ Dados da cidade são inválidos. Verifique os campos obrigatórios.")
                return
            
            try:
                repo = CidadeRepository()
                repo.criar_tabela()
                
                # Verificar se já existe cidade com mesmo nome na região/país
                cidades_existentes = repo.buscar_por_nome(nome)
                
                if regiao_obj:
                    cidade_existente = next((c for c in cidades_existentes 
                                          if c.regiao_id == regiao_obj.id), None)
                    local_desc = f"região {regiao_obj.nome}"
                else:
                    cidade_existente = next((c for c in cidades_existentes 
                                          if c.pais_id == pais_obj.id and c.regiao_id is None), None)
                    local_desc = f"país {pais_obj.nome} (sem região específica)"
                
                if cidade_existente:
                    st.error(f"❌ Já existe uma cidade com o nome '{nome}' na {local_desc}")
                    return
                
                # Salvar nova cidade
                cidade_id = repo.salvar(cidade)
                st.success(f"✅ Cidade '{nome}' salva com sucesso! (ID: {cidade_id})")
                
                # Mostrar detalhes
                with st.expander("📋 Detalhes da cidade salva", expanded=True):
                    detalhes = {
                        "id": cidade_id,
                        "nome": cidade.nome,
                        "pais": pais_obj.nome,
                        "coordenadas": f"{cidade.latitude}, {cidade.longitude}"
                    }
                    
                    if regiao_obj:
                        detalhes["estado_regiao"] = regiao_obj.nome_completo()
                    if cidade.populacao:
                        detalhes["populacao"] = f"{cidade.populacao:,} habitantes"
                    if cidade.altitude is not None:
                        detalhes["altitude"] = f"{cidade.altitude} metros"
                    if cidade.notes:
                        detalhes["notas"] = cidade.notes
                    
                    st.json(detalhes)
                
                st.info("💡 Recarregue a página ou use o menu lateral para cadastrar outra cidade.")
                
            except Exception as e:
                st.error(f"❌ Erro ao salvar cidade: {str(e)}")
    
    # Seção de ajuda
    with st.expander("ℹ️ Ajuda - Coordenadas Geográficas"):
        st.markdown("""
        **Como encontrar coordenadas:**
        - Use o Google Maps: clique com o botão direito no local e copie as coordenadas
        - Use sites como GPS-coordinates.net
        - Para cidades brasileiras, use o IBGE
        
        **Exemplos de coordenadas:**
        - 🌟 **Jaraguá do Sul, SC**: -26.4869, -49.0679
        - 🏙️ **São Paulo, SP**: -23.5505, -46.6333
        - 🏖️ **Rio de Janeiro, RJ**: -22.9068, -43.1729
        - 🌊 **Florianópolis, SC**: -27.5954, -48.5480
        
        **Regras:**
        - Latitude: -90 a +90 (negativa = Sul, positiva = Norte)
        - Longitude: -180 a +180 (negativa = Oeste, positiva = Leste)
        - Use ponto como separador decimal
        """)
    
    # Mostrar cidades da região/país selecionado
    if st.checkbox("📋 Ver cidades cadastradas") and pais_obj:
        try:
            repo = CidadeRepository()
            
            if regiao_obj:
                cidades = repo.buscar_por_regiao(regiao_obj.id)
                titulo = f"Cidades de {regiao_obj.nome_completo()}"
            else:
                cidades = repo.buscar_por_pais(pais_obj.id)
                titulo = f"Cidades de {pais_obj.nome}"
            
            if cidades:
                st.markdown(f"### {titulo}")
                for cidade in cidades:
                    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
                    with col1:
                        st.write(f"**{cidade.nome}**")
                    with col2:
                        st.caption(f"{cidade.latitude:.4f}")
                    with col3:
                        st.caption(f"{cidade.longitude:.4f}")
                    with col4:
                        st.caption(f"ID: {cidade.id}")
            else:
                st.info(f"Nenhuma cidade cadastrada para {regiao_obj.nome_completo() if regiao_obj else pais_obj.nome}.")
                
        except Exception as e:
            st.error(f"Erro ao carregar cidades: {str(e)}")


if __name__ == "__main__":
    # Para teste individual da página
    # st.set_page_config(page_title="Cadastro de Cidade", page_icon="🏙️")
    create_cidade()

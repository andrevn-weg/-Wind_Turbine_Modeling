import streamlit as st
import sys
from pathlib import Path
from decimal import Decimal

# Adicionar src ao path para imports
src_path = Path(__file__).parent.parent.parent.parent.parent / "src"
sys.path.insert(0, str(src_path))

from turbine_parameters import (
    Aerogenerator, AerogeneratorRepository,
    ManufacturerRepository, TurbineTypeRepository,
    GeneratorTypeRepository, ControlTypeRepository
)


def create_aerogenerator():
    """Interface para cadastro de aerogeradores"""
    st.subheader("🏭 Cadastro de Aerogerador")
    
    try:
        # Carregar dados de referência
        manufacturer_repo = ManufacturerRepository()
        turbine_type_repo = TurbineTypeRepository()
        generator_type_repo = GeneratorTypeRepository()
        control_type_repo = ControlTypeRepository()
        
        manufacturers = manufacturer_repo.listar_todos()
        turbine_types = turbine_type_repo.listar_todos()
        generator_types = generator_type_repo.listar_todos()
        control_types = control_type_repo.listar_todos()
        
        # Verificar se existem dados necessários
        if not manufacturers:
            st.error("❌ Nenhum fabricante cadastrado. Cadastre fabricantes primeiro.")
            return
        if not turbine_types:
            st.error("❌ Nenhum tipo de turbina cadastrado.")
            return
        if not generator_types:
            st.error("❌ Nenhum tipo de gerador cadastrado.")
            return
        if not control_types:
            st.error("❌ Nenhum tipo de controle cadastrado.")
            return
        
        with st.form("form_aerogenerator"):
            st.markdown("### Dados Básicos")
            
            col1, col2 = st.columns(2)
            with col1:
                model_code = st.text_input("Código do Modelo *", placeholder="Ex: V90-2.0MW")
                model = st.text_input("Nome do Modelo *", placeholder="Ex: Vestas V90 2MW")
            
            with col2:
                manufacture_year = st.number_input("Ano de Fabricação", min_value=1980, max_value=2030, value=2020)
                
                # Selectbox para fabricante
                manufacturer_options = {f"{m.name} - {m.country}": m.id for m in manufacturers}
                selected_manufacturer = st.selectbox("Fabricante *", list(manufacturer_options.keys()))
                manufacturer_id = manufacturer_options[selected_manufacturer]
            
            st.markdown("### Características de Potência")
            col1, col2, col3 = st.columns(3)
            with col1:
                rated_power_kw = st.number_input("Potência Nominal (kW) *", min_value=0.1, value=2000.0)
                rated_voltage_kv = st.number_input("Tensão Nominal (kV) *", min_value=0.1, value=0.69)
            with col2:
                apparent_power_kva = st.number_input("Potência Aparente (kVA)", min_value=0.0, value=0.0)
                power_factor = st.number_input("Fator de Potência", min_value=0.1, max_value=1.0, value=0.95)
            
            st.markdown("### Características do Vento")
            col1, col2, col3 = st.columns(3)
            with col1:
                cut_in_speed = st.number_input("Velocidade Cut-in (m/s) *", min_value=0.1, value=4.0)
            with col2:
                cut_out_speed = st.number_input("Velocidade Cut-out (m/s) *", min_value=0.1, value=25.0)
            with col3:
                rated_wind_speed = st.number_input("Velocidade Nominal (m/s)", min_value=0.0, value=12.0)
            
            st.markdown("### Características do Rotor")
            col1, col2, col3 = st.columns(3)
            with col1:
                rotor_diameter_m = st.number_input("Diâmetro do Rotor (m) *", min_value=1.0, value=90.0)
            with col2:
                blade_count = st.number_input("Número de Pás", min_value=1, max_value=10, value=3)
            with col3:
                rated_rotor_speed_rpm = st.number_input("Velocidade Nominal (RPM)", min_value=0.0, value=18.0)
            
            st.markdown("### Controle e Operação")
            col1, col2 = st.columns(2)
            with col1:
                variable_speed = st.checkbox("Velocidade Variável", value=True)
                pitch_control = st.checkbox("Controle de Pitch", value=True)
            with col2:
                pitch_min_deg = st.number_input("Ângulo Mín. Pitch (°)", value=0.0)
                pitch_max_deg = st.number_input("Ângulo Máx. Pitch (°)", value=90.0)
            
            st.markdown("### Tipos de Componentes")
            col1, col2, col3 = st.columns(3)
            with col1:
                turbine_type_options = {t.type: t.id for t in turbine_types}
                selected_turbine_type = st.selectbox("Tipo de Turbina *", list(turbine_type_options.keys()))
                turbine_type_id = turbine_type_options[selected_turbine_type]
            
            with col2:
                generator_type_options = {g.type: g.id for g in generator_types}
                selected_generator_type = st.selectbox("Tipo de Gerador *", list(generator_type_options.keys()))
                generator_type_id = generator_type_options[selected_generator_type]
            
            with col3:
                control_type_options = {c.type: c.id for c in control_types}
                selected_control_type = st.selectbox("Tipo de Controle *", list(control_type_options.keys()))
                control_type_id = control_type_options[selected_control_type]
            
            # Botão de submissão
            if st.form_submit_button("💾 Cadastrar Aerogerador", type="primary"):
                if not model_code.strip():
                    st.error("❌ Código do modelo é obrigatório!")
                    return
                if not model.strip():
                    st.error("❌ Nome do modelo é obrigatório!")
                    return
                
                try:
                    # Criar instância do aerogerador
                    aerogenerator = Aerogenerator(
                        model_code=model_code.strip(),
                        manufacturer_id=manufacturer_id,
                        model=model.strip(),
                        manufacture_year=manufacture_year,
                        rated_power_kw=Decimal(str(rated_power_kw)),
                        apparent_power_kva=Decimal(str(apparent_power_kva)) if apparent_power_kva > 0 else None,
                        power_factor=Decimal(str(power_factor)) if power_factor > 0 else None,
                        rated_voltage_kv=Decimal(str(rated_voltage_kv)),
                        cut_in_speed=Decimal(str(cut_in_speed)),
                        cut_out_speed=Decimal(str(cut_out_speed)),
                        rated_wind_speed=Decimal(str(rated_wind_speed)) if rated_wind_speed > 0 else None,
                        rotor_diameter_m=Decimal(str(rotor_diameter_m)),
                        blade_count=blade_count,
                        rated_rotor_speed_rpm=Decimal(str(rated_rotor_speed_rpm)) if rated_rotor_speed_rpm > 0 else None,
                        variable_speed=variable_speed,
                        pitch_control=pitch_control,
                        pitch_min_deg=Decimal(str(pitch_min_deg)) if pitch_min_deg != 0 else None,
                        pitch_max_deg=Decimal(str(pitch_max_deg)) if pitch_max_deg != 0 else None,
                        turbine_type_id=turbine_type_id,
                        generator_type_id=generator_type_id,
                        control_type_id=control_type_id
                    )
                    
                    # Salvar no banco
                    repo = AerogeneratorRepository()
                    repo.criar_tabela()
                    aerogenerator_id = repo.salvar(aerogenerator)
                    
                    st.success(f"✅ Aerogerador cadastrado com sucesso! ID: {aerogenerator_id}")
                    st.balloons()
                    
                    # Mostrar resumo
                    with st.expander("📋 Dados Cadastrados", expanded=True):
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("ID", aerogenerator_id)
                            st.metric("Código", aerogenerator.model_code)
                        with col2:
                            st.metric("Potência (kW)", float(aerogenerator.rated_power_kw))
                            st.metric("Diâmetro (m)", float(aerogenerator.rotor_diameter_m))
                        with col3:
                            st.metric("Fabricante", selected_manufacturer.split(" - ")[0])
                            st.metric("Tipo", selected_turbine_type)
                
                except Exception as e:
                    st.error(f"❌ Erro ao cadastrar: {str(e)}")
    
    except Exception as e:
        st.error(f"❌ Erro ao carregar dados: {str(e)}")
        
        with st.expander("🔧 Detalhes do erro"):
            import traceback
            st.code(traceback.format_exc())

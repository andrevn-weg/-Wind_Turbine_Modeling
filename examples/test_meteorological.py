#!/usr/bin/env python3
"""
Script de testes para o módulo meteorológico

Este script executa testes abrangentes para validar todas as funcionalidades
do módulo meteorológico implementado.

Autor: André Vinícius Lima do Nascimento
Data: 2025
"""

import sys
import os
from datetime import date, datetime, timedelta

# Adicionar o diretório src ao path para importações
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from meteorological import (
    MeteorologicalDataSource, MeteorologicalDataSourceRepository,
    MeteorologicalData, MeteorologicalDataRepository
)


class TestadorModuloMeteorologico:
    """Classe para testar todas as funcionalidades do módulo meteorológico"""
    
    def __init__(self):
        self.fonte_repo = MeteorologicalDataSourceRepository()
        self.dados_repo = MeteorologicalDataRepository()
        self.erros = []
        self.sucessos = 0
        
    def log_resultado(self, teste: str, sucesso: bool, detalhe: str = ""):
        """Registra o resultado de um teste"""
        if sucesso:
            self.sucessos += 1
            print(f"   ✅ {teste}")
            if detalhe:
                print(f"      {detalhe}")
        else:
            self.erros.append(f"{teste}: {detalhe}")
            print(f"   ❌ {teste}")
            if detalhe:
                print(f"      {detalhe}")
    
    def testar_entidade_fonte(self):
        """Testa a entidade MeteorologicalDataSource"""
        print("\n🧪 Testando entidade MeteorologicalDataSource...")
        
        # Teste 1: Criação e validação
        fonte = MeteorologicalDataSource(name="TEST_SOURCE", description="Teste")
        self.log_resultado(
            "Criação de fonte válida",
            fonte.validar(),
            f"Nome: {fonte.formatar_nome()}"
        )
        
        # Teste 2: Validação de nome inválido
        fonte_invalida = MeteorologicalDataSource(name="", description="Teste")
        self.log_resultado(
            "Rejeição de nome vazio",
            not fonte_invalida.validar(),
            "Nome vazio deve ser inválido"
        )
        
        # Teste 3: Formatação de nome
        fonte_formatacao = MeteorologicalDataSource(name="  test_api  ")
        nome_formatado = fonte_formatacao.formatar_nome()
        self.log_resultado(
            "Formatação de nome",
            nome_formatado == "TEST_API",
            f"'{fonte_formatacao.name}' -> '{nome_formatado}'"
        )
        
        # Teste 4: Conversão para dicionário
        fonte_dict = fonte.to_dict()
        campos_esperados = ['id', 'name', 'description']
        tem_campos = all(campo in fonte_dict for campo in campos_esperados)
        self.log_resultado(
            "Conversão para dicionário",
            tem_campos,
            f"Campos: {list(fonte_dict.keys())}"
        )
    
    def testar_entidade_dados(self):
        """Testa a entidade MeteorologicalData"""
        print("\n🧪 Testando entidade MeteorologicalData...")
        
        # Teste 1: Dados válidos
        dados = MeteorologicalData(
            meteorological_data_source_id=1,
            cidade_id=1,
            data=date.today(),
            velocidade_vento=7.5,
            temperatura=25.0,
            umidade=60.0
        )
        self.log_resultado(
            "Criação de dados válidos",
            dados.validar(),
            f"Vento: {dados.velocidade_vento}m/s"
        )
        
        # Teste 2: Dados inválidos (IDs zerados)
        dados_invalidos = MeteorologicalData(
            meteorological_data_source_id=0,
            cidade_id=0,
            data=date.today()
        )
        self.log_resultado(
            "Rejeição de IDs inválidos",
            not dados_invalidos.validar(),
            "IDs zerados devem ser inválidos"
        )
        
        # Teste 3: Classificação de vento
        dados.velocidade_vento = 8.5
        classificacao = dados.classificar_vento()
        self.log_resultado(
            "Classificação de vento",
            classificacao in ["Vento fresco", "Vento forte"],
            f"8.5 m/s = {classificacao}"
        )
        
        # Teste 4: Verificação de dados disponíveis
        tem_vento = dados.tem_dados_vento()
        tem_temp = dados.tem_dados_temperatura()
        tem_umidade = dados.tem_dados_umidade()
        self.log_resultado(
            "Verificação de dados disponíveis",
            tem_vento and tem_temp and tem_umidade,
            f"Vento: {tem_vento}, Temp: {tem_temp}, Umidade: {tem_umidade}"
        )
        
        # Teste 5: Validação de ranges
        dados_range = MeteorologicalData(
            meteorological_data_source_id=1,
            cidade_id=1,
            data=date.today(),
            velocidade_vento=-1.0,  # Inválido
            temperatura=100.0,      # Inválido
            umidade=150.0          # Inválido
        )
        self.log_resultado(
            "Rejeição de valores fora de range",
            not dados_range.validar(),
            "Valores negativos/extremos devem ser inválidos"
        )
    
    def testar_repositorio_fonte(self):
        """Testa o repositório MeteorologicalDataSourceRepository"""
        print("\n🧪 Testando repositório MeteorologicalDataSourceRepository...")
        
        # Configurar tabela
        self.fonte_repo.criar_tabela()
        
        # Teste 1: Salvar fonte
        fonte = MeteorologicalDataSource(
            name="TEST_REPO_SOURCE",
            description="Fonte para teste de repositório"
        )
        try:
            fonte_id = self.fonte_repo.salvar(fonte)
            self.log_resultado(
                "Salvamento de fonte",
                fonte_id > 0,
                f"ID gerado: {fonte_id}"
            )
        except Exception as e:
            self.log_resultado("Salvamento de fonte", False, str(e))
            return
        
        # Teste 2: Buscar por ID
        fonte_encontrada = self.fonte_repo.buscar_por_id(fonte_id)
        self.log_resultado(
            "Busca por ID",
            fonte_encontrada is not None and fonte_encontrada.name == "TEST_REPO_SOURCE",
            f"Encontrada: {fonte_encontrada.name if fonte_encontrada else 'None'}"
        )
        
        # Teste 3: Buscar por nome
        fonte_por_nome = self.fonte_repo.buscar_por_nome("TEST_REPO_SOURCE")
        self.log_resultado(
            "Busca por nome",
            fonte_por_nome is not None,
            f"Encontrada: {fonte_por_nome.name if fonte_por_nome else 'None'}"
        )
        
        # Teste 4: Atualizar fonte
        if fonte_encontrada:
            fonte_encontrada.description = "Descrição atualizada"
            sucesso_update = self.fonte_repo.atualizar(fonte_encontrada)
            self.log_resultado(
                "Atualização de fonte",
                sucesso_update,
                "Descrição foi atualizada"
            )
        
        # Teste 5: Listar todas
        todas_fontes = self.fonte_repo.listar_todos()
        self.log_resultado(
            "Listar todas as fontes",
            len(todas_fontes) > 0,
            f"Total: {len(todas_fontes)} fontes"
        )
        
        # Teste 6: Verificar duplicatas
        existe = self.fonte_repo.existe_nome("TEST_REPO_SOURCE")
        self.log_resultado(
            "Verificação de duplicatas",
            existe,
            "Fonte deve existir no banco"
        )
        
        # Teste 7: Excluir fonte
        sucesso_delete = self.fonte_repo.excluir(fonte_id)
        self.log_resultado(
            "Exclusão de fonte",
            sucesso_delete,
            f"Fonte ID {fonte_id} foi removida"
        )
    
    def testar_repositorio_dados(self):
        """Testa o repositório MeteorologicalDataRepository"""
        print("\n🧪 Testando repositório MeteorologicalDataRepository...")
        
        # Configurar tabelas
        self.dados_repo.criar_tabela()
        self.fonte_repo.criar_tabela()
        
        # Criar uma fonte de teste
        fonte = MeteorologicalDataSource(name="TEST_DATA_SOURCE", description="Para teste de dados")
        fonte_id = self.fonte_repo.salvar(fonte)
        
        # Teste 1: Salvar dados meteorológicos
        dados = MeteorologicalData(
            meteorological_data_source_id=fonte_id,
            cidade_id=1,  # Assumindo que existe cidade ID 1
            data=date.today(),
            altura_captura=20.0,
            velocidade_vento=6.5,
            temperatura=23.5,
            umidade=65.0
        )
        
        try:
            dados_id = self.dados_repo.salvar(dados)
            self.log_resultado(
                "Salvamento de dados meteorológicos",
                dados_id > 0,
                f"ID gerado: {dados_id}"
            )
        except Exception as e:
            self.log_resultado("Salvamento de dados meteorológicos", False, str(e))
            return
        
        # Teste 2: Buscar por ID
        dados_encontrados = self.dados_repo.buscar_por_id(dados_id)
        self.log_resultado(
            "Busca de dados por ID",
            dados_encontrados is not None,
            f"Velocidade: {dados_encontrados.velocidade_vento if dados_encontrados else 'None'} m/s"
        )
        
        # Teste 3: Buscar por cidade
        dados_cidade = self.dados_repo.buscar_por_cidade(1, limite=10)
        self.log_resultado(
            "Busca por cidade",
            len(dados_cidade) > 0,
            f"Encontrados: {len(dados_cidade)} registros"
        )
        
        # Teste 4: Buscar por fonte
        dados_fonte = self.dados_repo.buscar_por_fonte(fonte_id, limite=10)
        self.log_resultado(
            "Busca por fonte",
            len(dados_fonte) > 0,
            f"Encontrados: {len(dados_fonte)} registros"
        )
        
        # Teste 5: Buscar por período
        data_inicio = date.today() - timedelta(days=1)
        data_fim = date.today() + timedelta(days=1)
        dados_periodo = self.dados_repo.buscar_por_periodo(data_inicio, data_fim)
        self.log_resultado(
            "Busca por período",
            len(dados_periodo) > 0,
            f"Período: {data_inicio} a {data_fim}, encontrados: {len(dados_periodo)}"
        )
        
        # Teste 6: Consulta com detalhes da cidade
        dados_detalhados = self.dados_repo.buscar_com_detalhes_cidade(limite=5)
        tem_campos_cidade = any('cidade_nome' in dados for dados in dados_detalhados) if dados_detalhados else False
        self.log_resultado(
            "Consulta relacional com cidades",
            tem_campos_cidade,
            f"Registros com detalhes: {len(dados_detalhados)}"
        )
        
        # Teste 7: Atualizar dados
        if dados_encontrados:
            dados_encontrados.velocidade_vento = 8.0
            sucesso_update = self.dados_repo.atualizar(dados_encontrados)
            self.log_resultado(
                "Atualização de dados",
                sucesso_update,
                "Velocidade do vento atualizada para 8.0 m/s"
            )
        
        # Teste 8: Estatísticas por cidade
        stats = self.dados_repo.buscar_estatisticas_vento_por_cidade(1)
        tem_estatisticas = 'total_registros' in stats and stats['total_registros'] > 0
        self.log_resultado(
            "Cálculo de estatísticas",
            tem_estatisticas,
            f"Registros: {stats.get('total_registros', 0)}, Média: {stats.get('velocidade_media', 0):.2f} m/s"
        )
        
        # Teste 9: Exclusão de dados
        sucesso_delete = self.dados_repo.excluir(dados_id)
        self.log_resultado(
            "Exclusão de dados",
            sucesso_delete,
            f"Dados ID {dados_id} foram removidos"
        )
        
        # Limpeza: remover fonte de teste
        self.fonte_repo.excluir(fonte_id)
    
    def testar_integracao_completa(self):
        """Testa a integração completa entre os módulos"""
        print("\n🧪 Testando integração completa...")
        
        try:
            # Criar fonte
            fonte = MeteorologicalDataSource(
                name="INTEGRATION_TEST",
                description="Teste de integração completa"
            )
            fonte_id = self.fonte_repo.salvar(fonte)
            
            # Criar vários dados meteorológicos
            dados_ids = []
            for i in range(5):
                dados = MeteorologicalData(
                    meteorological_data_source_id=fonte_id,
                    cidade_id=1,
                    data=date.today() - timedelta(days=i),
                    velocidade_vento=5.0 + i,
                    temperatura=20.0 + i,
                    umidade=60.0 + i*2
                )
                dados_id = self.dados_repo.salvar(dados)
                dados_ids.append(dados_id)
            
            # Testar consultas relacionais
            dados_completos = self.dados_repo.buscar_com_detalhes_cidade(limite=10)
            dados_da_fonte = [d for d in dados_completos if d.get('fonte_nome') == 'INTEGRATION_TEST']
            
            self.log_resultado(
                "Integração fonte-dados-cidade",
                len(dados_da_fonte) == 5,
                f"Encontrados {len(dados_da_fonte)}/5 registros esperados"
            )
            
            # Testar estatísticas
            stats = self.dados_repo.buscar_estatisticas_vento_por_cidade(1)
            media_esperada = sum(range(5, 10)) / 5  # 5+6+7+8+9 / 5 = 7
            diferenca = abs(stats.get('velocidade_media', 0) - media_esperada)
            
            self.log_resultado(
                "Cálculo de estatísticas integradas",
                diferenca < 1.0,  # Margem de erro devido a outros dados
                f"Média calculada: {stats.get('velocidade_media', 0):.2f}, esperada: {media_esperada}"
            )
            
            # Limpeza
            for dados_id in dados_ids:
                self.dados_repo.excluir(dados_id)
            self.fonte_repo.excluir(fonte_id)
            
        except Exception as e:
            self.log_resultado("Integração completa", False, str(e))
    
    def executar_todos_testes(self):
        """Executa todos os testes do módulo"""
        print("🧪 === EXECUTANDO TESTES DO MÓDULO METEOROLÓGICO ===")
        
        self.testar_entidade_fonte()
        self.testar_entidade_dados()
        self.testar_repositorio_fonte()
        self.testar_repositorio_dados()
        self.testar_integracao_completa()
        
        # Relatório final
        total_testes = self.sucessos + len(self.erros)
        taxa_sucesso = (self.sucessos / total_testes * 100) if total_testes > 0 else 0
        
        print(f"\n📊 === RELATÓRIO FINAL DOS TESTES ===")
        print(f"✅ Sucessos: {self.sucessos}")
        print(f"❌ Erros: {len(self.erros)}")
        print(f"📈 Taxa de sucesso: {taxa_sucesso:.1f}%")
        
        if self.erros:
            print(f"\n❌ Erros encontrados:")
            for erro in self.erros:
                print(f"   • {erro}")
        else:
            print(f"\n🎉 Todos os testes passaram com sucesso!")
        
        return len(self.erros) == 0


def main():
    """Função principal de testes"""
    print("🧪 === TESTE COMPLETO DO MÓDULO METEOROLÓGICO ===")
    print("Sistema de Simulação de Turbinas Eólicas\n")
    
    testador = TestadorModuloMeteorologico()
    
    try:
        sucesso_geral = testador.executar_todos_testes()
        
        if sucesso_geral:
            print("\n✅ === MÓDULO METEOROLÓGICO VALIDADO ===")
            print("🎯 Todas as funcionalidades estão operacionais!")
            print("🚀 Módulo pronto para produção!")
        else:
            print("\n⚠️ === MÓDULO COM PROBLEMAS ===")
            print("🔧 Correções necessárias antes do uso em produção")
        
    except Exception as e:
        print(f"\n❌ Erro crítico durante os testes: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

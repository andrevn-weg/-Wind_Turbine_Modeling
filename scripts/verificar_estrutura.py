#!/usr/bin/env python3
"""
Script para verificar qual estrutura está sendo usada nas páginas web
e sugerir atualizações se necessário.
"""

import sys
from pathlib import Path

# Adicionar src ao path
PROJECT_ROOT = Path(__file__).parent.parent
src_path = PROJECT_ROOT / "src"
sys.path.insert(0, str(src_path))

def verificar_imports_pages():
    """Verifica os imports nas páginas web"""
    
    pages_dir = PROJECT_ROOT / "src" / "web" / "pages"
    print(f"🔍 Verificando imports em: {pages_dir}")
    
    for page_file in pages_dir.glob("*.py"):
        print(f"\n📄 Arquivo: {page_file.name}")
        
        try:
            content = page_file.read_text(encoding='utf-8')
            
            # Verificar imports problemáticos
            if "from models.wind_models.vento_api import VentoAPI" in content:
                print("   ❌ Import problemático encontrado: models.wind_models.vento_api")
                print("   📝 Sugestão: Implementar VentoAPI no módulo climate")
            
            # Verificar imports do geographic
            if any(phrase in content for phrase in ["CidadeModel", "PaisModel", "RegiaoModel"]):
                print("   ⚠️ Usando estrutura antiga: *Model classes")
                print("   📝 Sugestão: Migrar para nova estrutura separada")
            
            if "from geographic" in content:
                print("   ✅ Usando imports do módulo geographic")
            elif any(phrase in content for phrase in ["Cidade", "Pais", "Regiao"]) and "geographic" not in content:
                print("   ⚠️ Possível uso de entidades sem import adequado")
                
        except Exception as e:
            print(f"   ❌ Erro ao ler arquivo: {e}")

def sugerir_correcoes():
    """Sugere correções para os problemas encontrados"""
    
    print("\n" + "="*60)
    print("📋 RELATÓRIO DE CORREÇÕES NECESSÁRIAS")
    print("="*60)
    
    print("\n1. 🚨 PROBLEMA CRÍTICO: VentoAPI ausente")
    print("   Localização: src/web/pages/cadastro_localidade.py e listar_localidades.py")
    print("   Solução: Implementar VentoAPI em src/climate/api/vento.py")
    print("   Código sugerido:")
    print("   ```python")
    print("   from src.climate.api import VentoAPI")
    print("   # ou")
    print("   from climate.api import VentoAPI")
    print("   ```")
    
    print("\n2. ✅ CORREÇÃO IMPLEMENTADA: Separação Entity/Repository")
    print("   Status: Concluída para módulo geographic")
    print("   Nova estrutura disponível em:")
    print("   - src/geographic/{pais,regiao,cidade}/{entity,repository}.py")
    print("   - Exemplo: examples/exemplo_geographic_refatorado.py")
    
    print("\n3. 🔄 PRÓXIMAS AÇÕES RECOMENDADAS:")
    print("   a) Implementar VentoAPI (prioridade ALTA)")
    print("   b) Atualizar imports nas páginas web")
    print("   c) Migrar estrutura dos módulos climate e turbine")
    print("   d) Criar testes para nova estrutura")
    
    print("\n4. 📝 EXEMPLO DE MIGRAÇÃO DE IMPORT:")
    print("   Antes:")
    print("   ```python")
    print("   from models.wind_models.vento_api import VentoAPI  # ❌ Não existe")
    print("   ```")
    print("   Depois:")
    print("   ```python")
    print("   from climate.api import VentoAPI  # ✅ Quando implementado")
    print("   ```")

if __name__ == "__main__":
    print("🔧 Verificador de Estrutura - Módulo Geographic")
    print("="*60)
    
    verificar_imports_pages()
    sugerir_correcoes()
    
    print("\n" + "="*60)
    print("✅ Verificação concluída!")
    print("📄 Consulte o relatório completo em: docs/relatorio_situacao_atual.md")

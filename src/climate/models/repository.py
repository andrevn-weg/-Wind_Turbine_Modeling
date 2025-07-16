"""
Repositórios para dados climáticos.

Este módulo contém os repositórios responsáveis pela persistência
e recuperação de dados climáticos e eólicos.
"""

import sqlite3
import json
from datetime import datetime
from typing import List, Optional, Dict, Any
from pathlib import Path

from .entity import DadosClimaticos, DadosEolicos, LocalizacaoClimatica, SerieTemporalVento


class DadosClimaticosRepository:
    """
    Repositório para operações CRUD de dados climáticos.
    
    Gerencia a persistência de dados climáticos básicos no banco de dados SQLite.
    """
    
    def __init__(self, db_path: str = "data/wind_turbine.db"):
        """
        Inicializa o repositório.
        
        Args:
            db_path: Caminho para o banco de dados SQLite
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._criar_tabelas()
    
    def _criar_tabelas(self):
        """Cria as tabelas necessárias no banco de dados."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Tabela para dados climáticos básicos
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS dados_climaticos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    cidade TEXT NOT NULL,
                    latitude REAL NOT NULL,
                    longitude REAL NOT NULL,
                    temperatura REAL NOT NULL,
                    umidade REAL NOT NULL,
                    data TEXT NOT NULL,
                    altura_medicao INTEGER DEFAULT 10,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(latitude, longitude, data)
                )
            """)
            
            conn.commit()
    
    def criar(self, dados: DadosClimaticos) -> int:
        """
        Cria um novo registro de dados climáticos.
        
        Args:
            dados: Dados climáticos a serem salvos
        
        Returns:
            ID do registro criado
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO dados_climaticos 
                (cidade, latitude, longitude, temperatura, umidade, data, altura_medicao)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                dados.cidade,
                dados.latitude,
                dados.longitude,
                dados.temperatura,
                dados.umidade,
                dados.data.isoformat(),
                dados.altura_medicao
            ))
            
            return cursor.lastrowid
    
    def buscar_por_id(self, id: int) -> Optional[DadosClimaticos]:
        """
        Busca dados climáticos por ID.
        
        Args:
            id: ID do registro
        
        Returns:
            Dados climáticos encontrados ou None
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT cidade, latitude, longitude, temperatura, umidade, data, altura_medicao
                FROM dados_climaticos WHERE id = ?
            """, (id,))
            
            row = cursor.fetchone()
            if row:
                return DadosClimaticos(
                    cidade=row[0],
                    latitude=row[1],
                    longitude=row[2],
                    temperatura=row[3],
                    umidade=row[4],
                    data=datetime.fromisoformat(row[5]),
                    altura_medicao=row[6]
                )
            return None
    
    def buscar_por_localizacao(self, latitude: float, longitude: float,
                             tolerancia: float = 0.01) -> List[DadosClimaticos]:
        """
        Busca dados climáticos por localização.
        
        Args:
            latitude: Latitude da localização
            longitude: Longitude da localização
            tolerancia: Tolerância para busca (graus)
        
        Returns:
            Lista de dados climáticos encontrados
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT cidade, latitude, longitude, temperatura, umidade, data, altura_medicao
                FROM dados_climaticos 
                WHERE latitude BETWEEN ? AND ? 
                AND longitude BETWEEN ? AND ?
                ORDER BY data DESC
            """, (
                latitude - tolerancia,
                latitude + tolerancia,
                longitude - tolerancia,
                longitude + tolerancia
            ))
            
            return [
                DadosClimaticos(
                    cidade=row[0],
                    latitude=row[1],
                    longitude=row[2],
                    temperatura=row[3],
                    umidade=row[4],
                    data=datetime.fromisoformat(row[5]),
                    altura_medicao=row[6]
                )
                for row in cursor.fetchall()
            ]
    
    def buscar_por_periodo(self, inicio: datetime, fim: datetime) -> List[DadosClimaticos]:
        """
        Busca dados climáticos por período.
        
        Args:
            inicio: Data de início
            fim: Data de fim
        
        Returns:
            Lista de dados climáticos no período
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT cidade, latitude, longitude, temperatura, umidade, data, altura_medicao
                FROM dados_climaticos 
                WHERE data BETWEEN ? AND ?
                ORDER BY data ASC
            """, (inicio.isoformat(), fim.isoformat()))
            
            return [
                DadosClimaticos(
                    cidade=row[0],
                    latitude=row[1],
                    longitude=row[2],
                    temperatura=row[3],
                    umidade=row[4],
                    data=datetime.fromisoformat(row[5]),
                    altura_medicao=row[6]
                )
                for row in cursor.fetchall()
            ]
    
    def listar_todos(self, limite: int = 1000) -> List[DadosClimaticos]:
        """
        Lista todos os dados climáticos.
        
        Args:
            limite: Número máximo de registros
        
        Returns:
            Lista de dados climáticos
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT cidade, latitude, longitude, temperatura, umidade, data, altura_medicao
                FROM dados_climaticos 
                ORDER BY data DESC
                LIMIT ?
            """, (limite,))
            
            return [
                DadosClimaticos(
                    cidade=row[0],
                    latitude=row[1],
                    longitude=row[2],
                    temperatura=row[3],
                    umidade=row[4],
                    data=datetime.fromisoformat(row[5]),
                    altura_medicao=row[6]
                )
                for row in cursor.fetchall()
            ]
    
    def deletar_por_id(self, id: int) -> bool:
        """
        Deleta dados climáticos por ID.
        
        Args:
            id: ID do registro
        
        Returns:
            True se deletado com sucesso
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("DELETE FROM dados_climaticos WHERE id = ?", (id,))
            return cursor.rowcount > 0
    
    def contar_total_registros(self) -> int:
        """
        Conta o total de registros de dados climáticos.
        
        Returns:
            Número total de registros
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM dados_climaticos")
            result = cursor.fetchone()
            
            return result[0] if result else 0
    
    def obter_dados_recentes(self, limite: int = 100) -> List[DadosClimaticos]:
        """
        Obtém os dados mais recentes.
        
        Args:
            limite: Número máximo de registros a retornar
        
        Returns:
            Lista dos dados mais recentes
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, cidade, latitude, longitude, temperatura, umidade, 
                       data, altura_medicao, created_at
                FROM dados_climaticos 
                ORDER BY data DESC, created_at DESC
                LIMIT ?
            """, (limite,))
            
            resultados = []
            for row in cursor.fetchall():
                dados = DadosClimaticos(
                    id=row[0],
                    cidade=row[1],
                    latitude=row[2],
                    longitude=row[3],
                    temperatura=row[4],
                    umidade=row[5],
                    data=datetime.fromisoformat(row[6]),
                    altura_medicao=row[7]
                )
                resultados.append(dados)
            
            return resultados
    
    def obter_periodo_dados(self) -> Optional[tuple]:
        """
        Obtém o período (data inicial e final) dos dados armazenados.
        
        Returns:
            Tupla (data_inicio, data_fim) ou None se não houver dados
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT MIN(data), MAX(data) FROM dados_climaticos
            """)
            
            result = cursor.fetchone()
            
            if result and result[0] and result[1]:
                return (
                    datetime.fromisoformat(result[0]),
                    datetime.fromisoformat(result[1])
                )
            
            return None
    
    def obter_por_periodo_e_localizacao(self, inicio: datetime, fim: datetime, 
                                       localizacao_id: int) -> List[DadosClimaticos]:
        """
        Busca dados por período e localização.
        
        Args:
            inicio: Data/hora de início
            fim: Data/hora de fim
            localizacao_id: ID da localização
        
        Returns:
            Lista de dados climáticos encontrados
        """
        # Para compatibilidade, assumindo que temos latitude/longitude na localização
        # Este método precisará ser refinado quando integrarmos completamente com LocalizacaoClimatica
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, cidade, latitude, longitude, temperatura, umidade, 
                       data, altura_medicao, created_at
                FROM dados_climaticos 
                WHERE data BETWEEN ? AND ?
                ORDER BY data
            """, (inicio.isoformat(), fim.isoformat()))
            
            resultados = []
            for row in cursor.fetchall():
                dados = DadosClimaticos(
                    id=row[0],
                    cidade=row[1],
                    latitude=row[2],
                    longitude=row[3],
                    temperatura=row[4],
                    umidade=row[5],
                    data=datetime.fromisoformat(row[6]),
                    altura_medicao=row[7]
                )
                resultados.append(dados)
            
            return resultados
    
    def obter_por_periodo(self, inicio: datetime, fim: datetime) -> List[DadosClimaticos]:
        """
        Busca dados por período.
        
        Args:
            inicio: Data/hora de início
            fim: Data/hora de fim
        
        Returns:
            Lista de dados climáticos encontrados
        """
        return self.buscar_por_periodo(inicio, fim)
    
    def obter_por_localizacao(self, localizacao_id: int) -> List[DadosClimaticos]:
        """
        Busca dados por ID de localização.
        
        Args:
            localizacao_id: ID da localização
        
        Returns:
            Lista de dados climáticos encontrados
        """
        # Para compatibilidade, vamos buscar por todas as localizações
        # Este método precisará ser refinado quando integrarmos completamente
        return self.listar_todos(limite=10000)


class DadosEolicosRepository:
    """
    Repositório para operações CRUD de dados eólicos.
    
    Gerencia a persistência de dados eólicos específicos no banco de dados SQLite.
    """
    
    def __init__(self, db_path: str = "data/wind_turbine.db"):
        """
        Inicializa o repositório.
        
        Args:
            db_path: Caminho para o banco de dados SQLite
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._criar_tabelas()
    
    def _criar_tabelas(self):
        """Cria as tabelas necessárias no banco de dados."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Tabela para dados eólicos
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS dados_eolicos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    cidade TEXT NOT NULL,
                    latitude REAL NOT NULL,
                    longitude REAL NOT NULL,
                    temperatura REAL NOT NULL,
                    umidade REAL NOT NULL,
                    velocidade_vento REAL NOT NULL,
                    direcao_vento REAL,
                    velocidade_vento_max REAL,
                    rajada_vento REAL,
                    data TEXT NOT NULL,
                    altura_medicao INTEGER DEFAULT 10,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(latitude, longitude, data)
                )
            """)
            
            conn.commit()
    
    def criar(self, dados: DadosEolicos) -> int:
        """
        Cria um novo registro de dados eólicos.
        
        Args:
            dados: Dados eólicos a serem salvos
        
        Returns:
            ID do registro criado
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO dados_eolicos 
                (cidade, latitude, longitude, temperatura, umidade, velocidade_vento,
                 direcao_vento, velocidade_vento_max, rajada_vento, data, altura_medicao)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                dados.cidade,
                dados.latitude,
                dados.longitude,
                dados.temperatura,
                dados.umidade,
                dados.velocidade_vento,
                dados.direcao_vento,
                dados.velocidade_vento_max,
                dados.rajada_vento,
                dados.data.isoformat(),
                dados.altura_medicao
            ))
            
            return cursor.lastrowid
    
    def criar_multiplos(self, dados_lista: List[DadosEolicos]) -> List[int]:
        """
        Cria múltiplos registros de dados eólicos.
        
        Args:
            dados_lista: Lista de dados eólicos
        
        Returns:
            Lista de IDs dos registros criados
        """
        ids = []
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            for dados in dados_lista:
                cursor.execute("""
                    INSERT OR REPLACE INTO dados_eolicos 
                    (cidade, latitude, longitude, temperatura, umidade, velocidade_vento,
                     direcao_vento, velocidade_vento_max, rajada_vento, data, altura_medicao)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    dados.cidade,
                    dados.latitude,
                    dados.longitude,
                    dados.temperatura,
                    dados.umidade,
                    dados.velocidade_vento,
                    dados.direcao_vento,
                    dados.velocidade_vento_max,
                    dados.rajada_vento,
                    dados.data.isoformat(),
                    dados.altura_medicao
                ))
                ids.append(cursor.lastrowid)
            
            conn.commit()
        
        return ids
    
    def buscar_por_localizacao_periodo(self, latitude: float, longitude: float,
                                     inicio: datetime, fim: datetime,
                                     tolerancia: float = 0.01) -> List[DadosEolicos]:
        """
        Busca dados eólicos por localização e período.
        
        Args:
            latitude: Latitude da localização
            longitude: Longitude da localização
            inicio: Data de início
            fim: Data de fim
            tolerancia: Tolerância para busca (graus)
        
        Returns:
            Lista de dados eólicos encontrados
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT cidade, latitude, longitude, temperatura, umidade, velocidade_vento,
                       direcao_vento, velocidade_vento_max, rajada_vento, data, altura_medicao
                FROM dados_eolicos 
                WHERE latitude BETWEEN ? AND ? 
                AND longitude BETWEEN ? AND ?
                AND data BETWEEN ? AND ?
                ORDER BY data ASC
            """, (
                latitude - tolerancia,
                latitude + tolerancia,
                longitude - tolerancia,
                longitude + tolerancia,
                inicio.isoformat(),
                fim.isoformat()
            ))
            
            return [
                DadosEolicos(
                    cidade=row[0],
                    latitude=row[1],
                    longitude=row[2],
                    temperatura=row[3],
                    umidade=row[4],
                    velocidade_vento=row[5],
                    direcao_vento=row[6],
                    velocidade_vento_max=row[7],
                    rajada_vento=row[8],
                    data=datetime.fromisoformat(row[9]),
                    altura_medicao=row[10]
                )
                for row in cursor.fetchall()
            ]
    
    def calcular_estatisticas_localizacao(self, latitude: float, longitude: float,
                                        tolerancia: float = 0.01) -> Dict[str, float]:
        """
        Calcula estatísticas de vento para uma localização.
        
        Args:
            latitude: Latitude da localização
            longitude: Longitude da localização
            tolerancia: Tolerância para busca (graus)
        
        Returns:
            Dicionário com estatísticas
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    AVG(velocidade_vento) as media_vento,
                    MIN(velocidade_vento) as min_vento,
                    MAX(velocidade_vento) as max_vento,
                    COUNT(*) as total_registros,
                    AVG(temperatura) as media_temperatura,
                    AVG(umidade) as media_umidade
                FROM dados_eolicos 
                WHERE latitude BETWEEN ? AND ? 
                AND longitude BETWEEN ? AND ?
            """, (
                latitude - tolerancia,
                latitude + tolerancia,
                longitude - tolerancia,
                longitude + tolerancia
            ))
            
            row = cursor.fetchone()
            if row and row[0] is not None:
                return {
                    'media_vento': row[0],
                    'min_vento': row[1],
                    'max_vento': row[2],
                    'total_registros': row[3],
                    'media_temperatura': row[4],
                    'media_umidade': row[5]
                }
            return {}
    
    def buscar_dias_viaveis_turbina(self, latitude: float, longitude: float,
                                   velocidade_cut_in: float = 2.5,
                                   velocidade_cut_out: float = 25.0,
                                   tolerancia: float = 0.01) -> int:
        """
        Conta dias viáveis para operação de turbina eólica.
        
        Args:
            latitude: Latitude da localização
            longitude: Longitude da localização
            velocidade_cut_in: Velocidade mínima de operação
            velocidade_cut_out: Velocidade máxima de operação
            tolerancia: Tolerância para busca (graus)
        
        Returns:
            Número de dias viáveis
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT COUNT(*) 
                FROM dados_eolicos 
                WHERE latitude BETWEEN ? AND ? 
                AND longitude BETWEEN ? AND ?
                AND velocidade_vento BETWEEN ? AND ?
            """, (
                latitude - tolerancia,
                latitude + tolerancia,
                longitude - tolerancia,
                longitude + tolerancia,
                velocidade_cut_in,
                velocidade_cut_out
            ))
            
            result = cursor.fetchone()
            return result[0] if result else 0


class LocalizacaoClimaticaRepository:
    """
    Repositório para operações CRUD de localizações climáticas.
    
    Gerencia a persistência de localizações com metadados climáticos.
    """
    
    def __init__(self, db_path: str = "data/wind_turbine.db"):
        """
        Inicializa o repositório.
        
        Args:
            db_path: Caminho para o banco de dados SQLite
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._criar_tabelas()
    
    def _criar_tabelas(self):
        """Cria as tabelas necessárias no banco de dados."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS localizacoes_climaticas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome TEXT NOT NULL,
                    latitude REAL NOT NULL,
                    longitude REAL NOT NULL,
                    altitude REAL,
                    tipo_terreno TEXT,
                    rugosidade REAL,
                    fuso_horario TEXT DEFAULT 'America/Sao_Paulo',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(latitude, longitude)
                )
            """)
            
            conn.commit()
    
    def criar(self, localizacao: LocalizacaoClimatica) -> int:
        """
        Cria uma nova localização climática.
        
        Args:
            localizacao: Localização a ser salva
        
        Returns:
            ID do registro criado
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO localizacoes_climaticas 
                (nome, latitude, longitude, altitude, tipo_terreno, rugosidade, fuso_horario)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                localizacao.nome,
                localizacao.latitude,
                localizacao.longitude,
                localizacao.altitude,
                localizacao.tipo_terreno,
                localizacao.rugosidade,
                localizacao.fuso_horario
            ))
            
            return cursor.lastrowid
    
    def buscar_por_nome(self, nome: str) -> Optional[LocalizacaoClimatica]:
        """
        Busca localização por nome.
        
        Args:
            nome: Nome da localização
        
        Returns:
            Localização encontrada ou None
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT nome, latitude, longitude, altitude, tipo_terreno, rugosidade, fuso_horario
                FROM localizacoes_climaticas 
                WHERE nome = ?
            """, (nome,))
            
            row = cursor.fetchone()
            if row:
                return LocalizacaoClimatica(
                    nome=row[0],
                    latitude=row[1],
                    longitude=row[2],
                    altitude=row[3],
                    tipo_terreno=row[4],
                    rugosidade=row[5],
                    fuso_horario=row[6]
                )
            return None
    
    def listar_todas(self) -> List[LocalizacaoClimatica]:
        """
        Lista todas as localizações climáticas.
        
        Returns:
            Lista de localizações
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT nome, latitude, longitude, altitude, tipo_terreno, rugosidade, fuso_horario
                FROM localizacoes_climaticas 
                ORDER BY nome
            """)
            
            return [
                LocalizacaoClimatica(
                    nome=row[0],
                    latitude=row[1],
                    longitude=row[2],
                    altitude=row[3],
                    tipo_terreno=row[4],
                    rugosidade=row[5],
                    fuso_horario=row[6]
                )
                for row in cursor.fetchall()
            ]
    
    def remover(self, id: int) -> bool:
        """
        Remove uma localização por ID.
        
        Args:
            id: ID da localização a ser removida
        
        Returns:
            True se removido com sucesso, False caso contrário
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("DELETE FROM localizacoes_climaticas WHERE id = ?", (id,))
            
            return cursor.rowcount > 0

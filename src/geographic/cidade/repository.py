import sqlite3
from typing import Optional, List
from math import cos, radians

from .entity import Cidade


class CidadeRepository:
    """
    Classe responsável pela persistência e recuperação de dados de Cidade no banco de dados.
    Implementa o padrão Repository para operações CRUD.
    
    Esta classe é responsável apenas pela camada de dados, sem lógica de negócio.
    """
    
    def __init__(self, db_path: str = "data/wind_turbine.db"):
        """
        Inicializa o repositório com conexão ao banco de dados.
        
        Args:
            db_path: Caminho para o arquivo do banco de dados SQLite
        """
        self.db_path = db_path
        self.conn = None
        self.cursor = None
    
    def _conectar(self) -> None:
        """Estabelece conexão com o banco de dados"""
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
    
    def _desconectar(self) -> None:
        """Fecha a conexão com o banco de dados"""
        if self.conn:
            self.conn.close()
            self.conn = None
            self.cursor = None
    
    def criar_tabela(self) -> None:
        """Cria a tabela de cidades se não existir"""
        try:
            self._conectar()
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS cidades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                regiao_id INTEGER,
                pais_id INTEGER,
                latitude REAL NOT NULL,
                longitude REAL NOT NULL,
                populacao INTEGER,
                altitude REAL,
                notes TEXT,
                FOREIGN KEY (regiao_id) REFERENCES regioes (id),
                FOREIGN KEY (pais_id) REFERENCES paises (id)
            )
            ''')
            self.conn.commit()
        finally:
            self._desconectar()
    
    def salvar(self, cidade: Cidade) -> int:
        """
        Salva uma nova cidade no banco de dados.
        
        Args:
            cidade: Instância de Cidade a ser salva
            
        Returns:
            int: ID da cidade inserida
            
        Raises:
            ValueError: Se a cidade não passa na validação
        """
        if not cidade.validar():
            raise ValueError("Dados da cidade são inválidos")
            
        try:
            self._conectar()
            self.cursor.execute('''
            INSERT INTO cidades (nome, regiao_id, pais_id, latitude, longitude, populacao, altitude, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                cidade.nome, cidade.regiao_id, cidade.pais_id, 
                cidade.latitude, cidade.longitude, cidade.populacao, 
                cidade.altitude, cidade.notes
            ))
            self.conn.commit()
            cidade_id = self.cursor.lastrowid
            cidade.id = cidade_id  # Atualiza o ID da instância
            return cidade_id
        finally:
            self._desconectar()
    
    def buscar_por_id(self, cidade_id: int) -> Optional[Cidade]:
        """
        Busca uma cidade pelo seu ID.
        
        Args:
            cidade_id: ID da cidade a ser buscada
            
        Returns:
            Optional[Cidade]: Instância de Cidade se encontrada, None caso contrário
        """
        try:
            self._conectar()
            self.cursor.execute('SELECT * FROM cidades WHERE id = ?', (cidade_id,))
            resultado = self.cursor.fetchone()
            
            if resultado:
                return self._row_to_entity(resultado)
            return None
        finally:
            self._desconectar()
    
    def buscar_por_nome(self, nome: str) -> List[Cidade]:
        """
        Busca cidades cujo nome contenha o termo informado.
        
        Args:
            nome: Termo a ser buscado nos nomes das cidades
            
        Returns:
            List[Cidade]: Lista de cidades encontradas
        """
        try:
            self._conectar()
            self.cursor.execute('SELECT * FROM cidades WHERE nome LIKE ? ORDER BY nome', (f'%{nome}%',))
            resultados = self.cursor.fetchall()
            
            return [self._row_to_entity(resultado) for resultado in resultados]
        finally:
            self._desconectar()
    
    def listar_todos(self) -> List[Cidade]:
        """
        Lista todas as cidades cadastradas.
        
        Returns:
            List[Cidade]: Lista com todas as cidades
        """
        try:
            self._conectar()
            self.cursor.execute('SELECT * FROM cidades ORDER BY nome')
            resultados = self.cursor.fetchall()
            
            return [self._row_to_entity(resultado) for resultado in resultados]
        finally:
            self._desconectar()
    
    def atualizar(self, cidade: Cidade) -> bool:
        """
        Atualiza os dados de uma cidade existente.
        
        Args:
            cidade: Instância de Cidade com os dados atualizados
            
        Returns:
            bool: True se a atualização foi bem-sucedida, False caso contrário
            
        Raises:
            ValueError: Se a cidade não tem ID ou não passa na validação
        """
        if not cidade.id:
            raise ValueError("Cidade deve ter um ID para ser atualizada")
        if not cidade.validar():
            raise ValueError("Dados da cidade são inválidos")
            
        try:
            self._conectar()
            self.cursor.execute('''
            UPDATE cidades
            SET nome = ?, regiao_id = ?, pais_id = ?, latitude = ?, longitude = ?, 
                populacao = ?, altitude = ?, notes = ?
            WHERE id = ?
            ''', (
                cidade.nome, cidade.regiao_id, cidade.pais_id, 
                cidade.latitude, cidade.longitude, cidade.populacao, 
                cidade.altitude, cidade.notes, cidade.id
            ))
            self.conn.commit()
            
            return self.cursor.rowcount > 0
        finally:
            self._desconectar()
    
    def excluir(self, cidade_id: int) -> bool:
        """
        Remove uma cidade do banco de dados.
        
        Args:
            cidade_id: ID da cidade a ser removida
            
        Returns:
            bool: True se a exclusão foi bem-sucedida, False caso contrário
        """
        try:
            self._conectar()
            self.cursor.execute('DELETE FROM cidades WHERE id = ?', (cidade_id,))
            self.conn.commit()
            
            return self.cursor.rowcount > 0
        finally:
            self._desconectar()
    
    def buscar_proximas(self, latitude: float, longitude: float, raio_km: float = 50.0) -> List[Cidade]:
        """
        Busca cidades próximas a um ponto geográfico.
        Usa uma aproximação simples para distância geográfica.
        
        Args:
            latitude: Latitude do ponto central
            longitude: Longitude do ponto central
            raio_km: Raio de busca em quilômetros
            
        Returns:
            List[Cidade]: Lista de cidades encontradas dentro do raio
        """
        # Aproximação simples: 1 grau de latitude ≈ 111 km
        lat_range = raio_km / 111.0
        lon_range = raio_km / (111.0 * abs(cos(radians(latitude))) if latitude != 0 else 111.0)
        
        try:
            self._conectar()
            self.cursor.execute('''
            SELECT * FROM cidades 
            WHERE latitude BETWEEN ? AND ?
            AND longitude BETWEEN ? AND ?
            ORDER BY nome
            ''', (
                latitude - lat_range, latitude + lat_range,
                longitude - lon_range, longitude + lon_range
            ))
            resultados = self.cursor.fetchall()
            
            return [self._row_to_entity(resultado) for resultado in resultados]
        finally:
            self._desconectar()
    
    def buscar_por_regiao(self, regiao_id: int) -> List[Cidade]:
        """
        Busca todas as cidades de uma região específica.
        
        Args:
            regiao_id: ID da região
            
        Returns:
            List[Cidade]: Lista de cidades da região
        """
        try:
            self._conectar()
            self.cursor.execute('SELECT * FROM cidades WHERE regiao_id = ? ORDER BY nome', (regiao_id,))
            resultados = self.cursor.fetchall()
            
            return [self._row_to_entity(resultado) for resultado in resultados]
        finally:
            self._desconectar()
    
    def buscar_por_pais(self, pais_id: int) -> List[Cidade]:
        """
        Busca todas as cidades de um país específico.
        
        Args:
            pais_id: ID do país
            
        Returns:
            List[Cidade]: Lista de cidades do país
        """
        try:
            self._conectar()
            self.cursor.execute('SELECT * FROM cidades WHERE pais_id = ? ORDER BY nome', (pais_id,))
            resultados = self.cursor.fetchall()
            
            return [self._row_to_entity(resultado) for resultado in resultados]
        finally:
            self._desconectar()
    
    def _row_to_entity(self, row: tuple) -> Cidade:
        """
        Converte uma linha do banco de dados em uma entidade Cidade.
        
        Args:
            row: Tupla com os dados da linha do banco
            
        Returns:
            Cidade: Instância da entidade Cidade
        """
        return Cidade(
            id=row[0],
            nome=row[1],
            regiao_id=row[2],
            pais_id=row[3],
            latitude=row[4],
            longitude=row[5],
            populacao=row[6],
            altitude=row[7],
            notes=row[8]
        )

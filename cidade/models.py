import sqlite3
from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from datetime import datetime
from math import cos, radians




@dataclass
class Cidade:
    """
    Modelo de dados para representar uma cidade/localidade com suas coordenadas geográficas.
    
    Attributes:
        id (Optional[int]): Identificador único da cidade no banco de dados
        nome (str): Nome da cidade/localidade
        regiao_id (Optional[int]): Referência à região/estado (chave estrangeira)
        pais_id (Optional[int]): Referência direta ao país (chave estrangeira)
        latitude (float): Latitude geográfica
        longitude (float): Longitude geográfica
        populacao (Optional[int]): População estimada da cidade
        altitude (Optional[float]): Altitude média em metros
        notes (Optional[str]): Notas adicionais sobre a cidade/localidade
    """
    id: Optional[int] = None
    nome: str = ""
    regiao_id: Optional[int] = None
    pais_id: Optional[int] = None
    latitude: float = 0.0
    longitude: float = 0.0
    populacao: Optional[int] = None
    altitude: Optional[float] = None
    notes: Optional[str] = None
    
    def __repr__(self) -> str:
        return f"Cidade(id={self.id}, nome={self.nome}, lat={self.latitude}, long={self.longitude})"
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte a instância em um dicionário"""
        return {
            "id": self.id,
            "nome": self.nome,
            "regiao_id": self.regiao_id,
            "pais_id": self.pais_id,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "populacao": self.populacao,
            "altitude": self.altitude,
            "notes": self.notes
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Cidade':
        """Cria uma instância de Cidade a partir de um dicionário"""
        return cls(
            id=data.get("id"),
            nome=data.get("nome", ""),
            regiao_id=data.get("regiao_id"),
            pais_id=data.get("pais_id"),
            latitude=data.get("latitude", 0.0),
            longitude=data.get("longitude", 0.0),
            populacao=data.get("populacao"),
            altitude=data.get("altitude"),
            notes=data.get("notes")
        )


class CidadeModel:
    """
    Classe responsável pela manipulação dos dados de Cidade no banco de dados.
    Implementa operações CRUD (Create, Read, Update, Delete).
    """
    
    def __init__(self, db_path: str = "wind_turbine.db"):
        """
        Inicializa o modelo com conexão ao banco de dados.
        
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
    
    def adicionar(self, cidade: Cidade) -> int:
        """
        Adiciona uma nova cidade ao banco de dados.
        
        Args:
            cidade: Instância de Cidade a ser adicionada
            
        Returns:
            int: ID da cidade inserida
        """
        try:
            self._conectar()
            self.cursor.execute('''
            INSERT INTO cidades (nome, regiao_id, pais_id, latitude, longitude, populacao, altitude, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (cidade.nome, cidade.regiao_id, cidade.pais_id, cidade.latitude, cidade.longitude, cidade.populacao, cidade.altitude, cidade.notes))
            self.conn.commit()
            # Retorna o ID da cidade inserida
            cidade_id = self.cursor.lastrowid
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
                return Cidade(
                    id=resultado[0],
                    nome=resultado[1],
                    regiao_id=resultado[2],
                    pais_id=resultado[3],
                    latitude=resultado[4],
                    longitude=resultado[5],
                    populacao=resultado[6],
                    altitude=resultado[7],
                    notes=resultado[8]
                )
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
            self.cursor.execute('SELECT * FROM cidades WHERE nome LIKE ?', (f'%{nome}%',))
            resultados = self.cursor.fetchall()
            
            cidades = []
            for resultado in resultados:
                cidade = Cidade(
                    id=resultado[0],
                    nome=resultado[1],
                    regiao_id=resultado[2],
                    pais_id=resultado[3],
                    latitude=resultado[4],
                    longitude=resultado[5],
                    populacao=resultado[6],
                    altitude=resultado[7],
                    notes=resultado[8]
                )
                cidades.append(cidade)
            
            return cidades
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
            
            cidades = []
            for resultado in resultados:
                cidade = Cidade(
                    id=resultado[0],
                    nome=resultado[1],
                    regiao_id=resultado[2],
                    pais_id=resultado[3],
                    latitude=resultado[4],
                    longitude=resultado[5],
                    populacao=resultado[6],
                    altitude=resultado[7],
                    notes=resultado[8]
                )
                cidades.append(cidade)
            
            return cidades
        finally:
            self._desconectar()
    
    def atualizar(self, cidade: Cidade) -> bool:
        """
        Atualiza os dados de uma cidade existente.
        
        Args:
            cidade: Instância de Cidade com os dados atualizados
            
        Returns:
            bool: True se a atualização foi bem-sucedida, False caso contrário
        """
        if not cidade.id:
            return False
            
        try:
            self._conectar()
            self.cursor.execute('''
            UPDATE cidades
            SET nome = ?, regiao_id = ?, pais_id = ?, latitude = ?, longitude = ?, populacao = ?, altitude = ?, notes = ?
            WHERE id = ?
            ''', (cidade.nome, cidade.regiao_id, cidade.pais_id, cidade.latitude, cidade.longitude, cidade.populacao, cidade.altitude, cidade.notes, cidade.id))
            self.conn.commit()
            
            # Verifica se alguma linha foi afetada
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
            
            # Verifica se alguma linha foi afetada
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
        # A aproximação de longitude varia com a latitude
        lat_range = raio_km / 111.0
        lon_range = raio_km / (111.0 * abs(cos(radians(latitude))) if latitude != 0 else 111.0)
        
        try:
            self._conectar()
            self.cursor.execute('''
            SELECT * FROM cidades 
            WHERE latitude BETWEEN ? AND ?
            AND longitude BETWEEN ? AND ?
            ''', (
                latitude - lat_range, latitude + lat_range,
                longitude - lon_range, longitude + lon_range
            ))
            resultados = self.cursor.fetchall()
            
            cidades = []
            for resultado in resultados:
                cidade = Cidade(
                    id=resultado[0],
                    nome=resultado[1],
                    regiao_id=resultado[2],
                    pais_id=resultado[3],
                    latitude=resultado[4],
                    longitude=resultado[5],
                    populacao=resultado[6],
                    altitude=resultado[7],
                    notes=resultado[8]
                )
                cidades.append(cidade)
            
            return cidades
        finally:
            self._desconectar()
import sqlite3
from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from datetime import datetime
from math import cos, radians

@dataclass
class Regiao:
    """
    Modelo simplificado para representar regiões/estados.
    
    Attributes:
        id (Optional[int]): Identificador único da região
        nome (str): Nome da região ou estado
        pais_id (Optional[int]): Referência ao país (chave estrangeira)
        sigla (Optional[str]): Sigla ou abreviação da região (ex: "SC", "SP")
    """
    id: Optional[int] = None
    nome: str = ""
    pais_id: Optional[int] = None
    sigla: Optional[str] = None
    
    def __repr__(self) -> str:
        return f"Regiao(id={self.id}, nome={self.nome}, sigla={self.sigla})"
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte a instância em um dicionário"""
        return {
            "id": self.id,
            "nome": self.nome,
            "pais_id": self.pais_id,
            "sigla": self.sigla
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Regiao':
        """Cria uma instância de Região a partir de um dicionário"""
        return cls(
            id=data.get("id"),
            nome=data.get("nome", ""),
            pais_id=data.get("pais_id"),
            sigla=data.get("sigla")
        )


class RegiaoModel:
    """
    Classe responsável pela manipulação dos dados de Região no banco de dados.
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
        """Cria a tabela de regiões se não existir"""
        try:
            self._conectar()
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS regioes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                pais_id INTEGER,
                sigla TEXT,
                FOREIGN KEY (pais_id) REFERENCES paises (id)
            )
            ''')
            self.conn.commit()
        finally:
            self._desconectar()
    
    def adicionar(self, regiao: Regiao) -> int:
        """
        Adiciona uma nova região ao banco de dados.
        
        Args:
            regiao: Instância de Regiao a ser adicionada
            
        Returns:
            int: ID da região inserida
        """
        try:
            self._conectar()
            self.cursor.execute('''
            INSERT INTO regioes (nome, pais_id, sigla)
            VALUES (?, ?, ?)
            ''', (regiao.nome, regiao.pais_id, regiao.sigla))
            self.conn.commit()
            # Retorna o ID da região inserida
            regiao_id = self.cursor.lastrowid
            return regiao_id
        finally:
            self._desconectar()
    
    def buscar_por_id(self, regiao_id: int) -> Optional[Regiao]:
        """
        Busca uma região pelo seu ID.
        
        Args:
            regiao_id: ID da região a ser buscada
            
        Returns:
            Optional[Regiao]: Instância de Regiao se encontrada, None caso contrário
        """
        try:
            self._conectar()
            self.cursor.execute('SELECT * FROM regioes WHERE id = ?', (regiao_id,))
            resultado = self.cursor.fetchone()
            
            if resultado:
                return Regiao(
                    id=resultado[0],
                    nome=resultado[1],
                    pais_id=resultado[2],
                    sigla=resultado[3]
                )
            return None
        finally:
            self._desconectar()
    
    def buscar_por_nome(self, nome: str) -> List[Regiao]:
        """
        Busca regiões cujo nome contenha o termo informado.
        
        Args:
            nome: Termo a ser buscado nos nomes das regiões
            
        Returns:
            List[Regiao]: Lista de regiões encontradas
        """
        try:
            self._conectar()
            self.cursor.execute('SELECT * FROM regioes WHERE nome LIKE ?', (f'%{nome}%',))
            resultados = self.cursor.fetchall()
            
            regioes = []
            for resultado in resultados:
                regiao = Regiao(
                    id=resultado[0],
                    nome=resultado[1],
                    pais_id=resultado[2],
                    sigla=resultado[3]
                )
                regioes.append(regiao)
            
            return regioes
        finally:
            self._desconectar()
    
    def buscar_por_pais(self, pais_id: int) -> List[Regiao]:
        """
        Busca regiões pelo ID do país.
        
        Args:
            pais_id: ID do país a ser filtrado
            
        Returns:
            List[Regiao]: Lista de regiões encontradas para o país
        """
        try:
            self._conectar()
            self.cursor.execute('SELECT * FROM regioes WHERE pais_id = ? ORDER BY nome', (pais_id,))
            resultados = self.cursor.fetchall()
            
            regioes = []
            for resultado in resultados:
                regiao = Regiao(
                    id=resultado[0],
                    nome=resultado[1],
                    pais_id=resultado[2],
                    sigla=resultado[3]
                )
                regioes.append(regiao)
            
            return regioes
        finally:
            self._desconectar()
    
    def buscar_por_sigla(self, sigla: str) -> Optional[Regiao]:
        """
        Busca uma região pela sua sigla.
        
        Args:
            sigla: Sigla da região
            
        Returns:
            Optional[Regiao]: Instância de Regiao se encontrada, None caso contrário
        """
        try:
            self._conectar()
            self.cursor.execute('SELECT * FROM regioes WHERE sigla = ?', (sigla,))
            resultado = self.cursor.fetchone()
            
            if resultado:
                return Regiao(
                    id=resultado[0],
                    nome=resultado[1],
                    pais_id=resultado[2],
                    sigla=resultado[3]
                )
            return None
        finally:
            self._desconectar()
    
    def listar_todos(self) -> List[Regiao]:
        """
        Lista todas as regiões cadastradas.
        
        Returns:
            List[Regiao]: Lista com todas as regiões
        """
        try:
            self._conectar()
            self.cursor.execute('SELECT * FROM regioes ORDER BY nome')
            resultados = self.cursor.fetchall()
            
            regioes = []
            for resultado in resultados:
                regiao = Regiao(
                    id=resultado[0],
                    nome=resultado[1],
                    pais_id=resultado[2],
                    sigla=resultado[3]
                )
                regioes.append(regiao)
            
            return regioes
        finally:
            self._desconectar()
    
    def atualizar(self, regiao: Regiao) -> bool:
        """
        Atualiza os dados de uma região existente.
        
        Args:
            regiao: Instância de Regiao com os dados atualizados
            
        Returns:
            bool: True se a atualização foi bem-sucedida, False caso contrário
        """
        if not regiao.id:
            return False
            
        try:
            self._conectar()
            self.cursor.execute('''
            UPDATE regioes
            SET nome = ?, pais_id = ?, sigla = ?
            WHERE id = ?
            ''', (regiao.nome, regiao.pais_id, regiao.sigla, regiao.id))
            self.conn.commit()
            
            # Verifica se alguma linha foi afetada
            return self.cursor.rowcount > 0
        finally:
            self._desconectar()
    
    def excluir(self, regiao_id: int) -> bool:
        """
        Remove uma região do banco de dados.
        
        Args:
            regiao_id: ID da região a ser removida
            
        Returns:
            bool: True se a exclusão foi bem-sucedida, False caso contrário
        """
        try:
            self._conectar()
            self.cursor.execute('DELETE FROM regioes WHERE id = ?', (regiao_id,))
            self.conn.commit()
            
            # Verifica se alguma linha foi afetada
            return self.cursor.rowcount > 0
        finally:
            self._desconectar()


import sqlite3
from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from datetime import datetime
from math import cos, radians

@dataclass
class Pais:
    """
    Modelo simplificado para representar países.
    
    Attributes:
        id (Optional[int]): Identificador único do país
        nome (str): Nome do país
        codigo (str): Código ISO do país (ex: "BR", "US")
    """
    id: Optional[int] = None
    nome: str = ""
    codigo: str = ""
    
    def __repr__(self) -> str:
        return f"Pais(id={self.id}, nome={self.nome}, codigo={self.codigo})"
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte a instância em um dicionário"""
        return {
            "id": self.id,
            "nome": self.nome,
            "codigo": self.codigo
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Pais':
        """Cria uma instância de País a partir de um dicionário"""
        return cls(
            id=data.get("id"),
            nome=data.get("nome", ""),
            codigo=data.get("codigo", "")
        )


class PaisModel:
    """
    Classe responsável pela manipulação dos dados de País no banco de dados.
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
        """Cria a tabela de países se não existir"""
        try:
            self._conectar()
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS paises (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                codigo TEXT NOT NULL UNIQUE
            )
            ''')
            self.conn.commit()
        finally:
            self._desconectar()
    
    def adicionar(self, pais: Pais) -> int:
        """
        Adiciona um novo país ao banco de dados.
        
        Args:
            pais: Instância de Pais a ser adicionada
            
        Returns:
            int: ID do país inserido
        """
        try:
            self._conectar()
            self.cursor.execute('''
            INSERT INTO paises (nome, codigo)
            VALUES (?, ?)
            ''', (pais.nome, pais.codigo))
            self.conn.commit()
            # Retorna o ID do país inserido
            pais_id = self.cursor.lastrowid
            return pais_id
        finally:
            self._desconectar()
    
    def buscar_por_id(self, pais_id: int) -> Optional[Pais]:
        """
        Busca um país pelo seu ID.
        
        Args:
            pais_id: ID do país a ser buscado
            
        Returns:
            Optional[Pais]: Instância de Pais se encontrado, None caso contrário
        """
        try:
            self._conectar()
            self.cursor.execute('SELECT * FROM paises WHERE id = ?', (pais_id,))
            resultado = self.cursor.fetchone()
            
            if resultado:
                return Pais(
                    id=resultado[0],
                    nome=resultado[1],
                    codigo=resultado[2]
                )
            return None
        finally:
            self._desconectar()
    
    def buscar_por_nome(self, nome: str) -> List[Pais]:
        """
        Busca países cujo nome contenha o termo informado.
        
        Args:
            nome: Termo a ser buscado nos nomes dos países
            
        Returns:
            List[Pais]: Lista de países encontrados
        """
        try:
            self._conectar()
            self.cursor.execute('SELECT * FROM paises WHERE nome LIKE ?', (f'%{nome}%',))
            resultados = self.cursor.fetchall()
            
            paises = []
            for resultado in resultados:
                pais = Pais(
                    id=resultado[0],
                    nome=resultado[1],
                    codigo=resultado[2]
                )
                paises.append(pais)
            
            return paises
        finally:
            self._desconectar()
    
    def buscar_por_codigo(self, codigo: str) -> Optional[Pais]:
        """
        Busca um país pelo seu código ISO.
        
        Args:
            codigo: Código ISO do país
            
        Returns:
            Optional[Pais]: Instância de Pais se encontrado, None caso contrário
        """
        try:
            self._conectar()
            self.cursor.execute('SELECT * FROM paises WHERE codigo = ?', (codigo,))
            resultado = self.cursor.fetchone()
            
            if resultado:
                return Pais(
                    id=resultado[0],
                    nome=resultado[1],
                    codigo=resultado[2]
                )
            return None
        finally:
            self._desconectar()
    
    def listar_todos(self) -> List[Pais]:
        """
        Lista todos os países cadastrados.
        
        Returns:
            List[Pais]: Lista com todos os países
        """
        try:
            self._conectar()
            self.cursor.execute('SELECT * FROM paises ORDER BY nome')
            resultados = self.cursor.fetchall()
            
            paises = []
            for resultado in resultados:
                pais = Pais(
                    id=resultado[0],
                    nome=resultado[1],
                    codigo=resultado[2]
                )
                paises.append(pais)
            
            return paises
        finally:
            self._desconectar()
    
    def atualizar(self, pais: Pais) -> bool:
        """
        Atualiza os dados de um país existente.
        
        Args:
            pais: Instância de Pais com os dados atualizados
            
        Returns:
            bool: True se a atualização foi bem-sucedida, False caso contrário
        """
        if not pais.id:
            return False
            
        try:
            self._conectar()
            self.cursor.execute('''
            UPDATE paises
            SET nome = ?, codigo = ?
            WHERE id = ?
            ''', (pais.nome, pais.codigo, pais.id))
            self.conn.commit()
            
            # Verifica se alguma linha foi afetada
            return self.cursor.rowcount > 0
        finally:
            self._desconectar()
    
    def excluir(self, pais_id: int) -> bool:
        """
        Remove um país do banco de dados.
        
        Args:
            pais_id: ID do país a ser removido
            
        Returns:
            bool: True se a exclusão foi bem-sucedida, False caso contrário
        """
        try:
            self._conectar()
            self.cursor.execute('DELETE FROM paises WHERE id = ?', (pais_id,))
            self.conn.commit()
            
            # Verifica se alguma linha foi afetada
            return self.cursor.rowcount > 0
        finally:
            self._desconectar()
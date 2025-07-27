import sqlite3
from typing import Optional, List
from datetime import datetime

from .entity import Manufacturer


class ManufacturerRepository:
    """
    Classe responsável pela persistência e recuperação de dados de Fabricantes no banco de dados.
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
        """Cria a tabela de fabricantes se não existir"""
        try:
            self._conectar()
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS manufacturers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR NOT NULL UNIQUE,
                country VARCHAR,
                official_website VARCHAR,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            ''')
            self.conn.commit()
        finally:
            self._desconectar()
    
    def salvar(self, manufacturer: Manufacturer) -> int:
        """
        Salva um fabricante no banco de dados.
        
        Args:
            manufacturer: Instância do fabricante a ser salvo
            
        Returns:
            int: ID do fabricante salvo
            
        Raises:
            ValueError: Se já existir um fabricante com o mesmo nome
        """
        try:
            self._conectar()
            
            # Verificar se já existe um fabricante com o mesmo nome
            self.cursor.execute('SELECT COUNT(*) FROM manufacturers WHERE name = ?', (manufacturer.name,))
            if self.cursor.fetchone()[0] > 0:
                raise ValueError(f"Já existe um fabricante com o nome '{manufacturer.name}'")
            
            # Definir timestamps
            agora = datetime.now()
            if not manufacturer.created_at:
                manufacturer.created_at = agora
            manufacturer.updated_at = agora
            
            self.cursor.execute('''
                INSERT INTO manufacturers (name, country, official_website, created_at, updated_at) 
                VALUES (?, ?, ?, ?, ?)
            ''', (manufacturer.name, manufacturer.country, manufacturer.official_website,
                  manufacturer.created_at, manufacturer.updated_at))
            
            self.conn.commit()
            manufacturer_id = self.cursor.lastrowid
            manufacturer.id = manufacturer_id  # Atualiza o ID da instância
            return manufacturer_id
        finally:
            self._desconectar()
    
    def buscar_por_id(self, manufacturer_id: int) -> Optional[Manufacturer]:
        """
        Busca um fabricante pelo ID.
        
        Args:
            manufacturer_id: ID do fabricante
            
        Returns:
            Optional[Manufacturer]: Fabricante encontrado ou None
        """
        try:
            self._conectar()
            self.cursor.execute('SELECT * FROM manufacturers WHERE id = ?', (manufacturer_id,))
            resultado = self.cursor.fetchone()
            
            if resultado:
                return self._row_to_entity(resultado)
            return None
        finally:
            self._desconectar()
    
    def buscar_por_nome(self, name: str) -> Optional[Manufacturer]:
        """
        Busca um fabricante pelo nome.
        
        Args:
            name: Nome do fabricante
            
        Returns:
            Optional[Manufacturer]: Fabricante encontrado ou None
        """
        try:
            self._conectar()
            self.cursor.execute('SELECT * FROM manufacturers WHERE name = ?', (name,))
            resultado = self.cursor.fetchone()
            
            if resultado:
                return self._row_to_entity(resultado)
            return None
        finally:
            self._desconectar()
    
    def buscar_por_termo(self, termo: str) -> List[Manufacturer]:
        """
        Busca fabricantes que contenham o termo no nome.
        
        Args:
            termo: Termo a ser buscado no nome
            
        Returns:
            List[Manufacturer]: Lista de fabricantes encontrados
        """
        try:
            self._conectar()
            self.cursor.execute(
                'SELECT * FROM manufacturers WHERE name LIKE ? ORDER BY name',
                (f'%{termo}%',)
            )
            resultados = self.cursor.fetchall()
            
            return [self._row_to_entity(resultado) for resultado in resultados]
        finally:
            self._desconectar()
    
    def buscar_por_pais(self, country: str) -> List[Manufacturer]:
        """
        Busca fabricantes de um país específico.
        
        Args:
            country: País dos fabricantes
            
        Returns:
            List[Manufacturer]: Lista de fabricantes do país
        """
        try:
            self._conectar()
            self.cursor.execute(
                'SELECT * FROM manufacturers WHERE country = ? ORDER BY name',
                (country,)
            )
            resultados = self.cursor.fetchall()
            
            return [self._row_to_entity(resultado) for resultado in resultados]
        finally:
            self._desconectar()
    
    def listar_todos(self) -> List[Manufacturer]:
        """
        Lista todos os fabricantes ordenados por nome.
        
        Returns:
            List[Manufacturer]: Lista de todos os fabricantes
        """
        try:
            self._conectar()
            self.cursor.execute('SELECT * FROM manufacturers ORDER BY name')
            resultados = self.cursor.fetchall()
            
            return [self._row_to_entity(resultado) for resultado in resultados]
        finally:
            self._desconectar()
    
    def atualizar(self, manufacturer: Manufacturer) -> bool:
        """
        Atualiza um fabricante existente.
        
        Args:
            manufacturer: Fabricante com dados atualizados
            
        Returns:
            bool: True se atualizou com sucesso, False caso contrário
            
        Raises:
            ValueError: Se já existir outro fabricante com o mesmo nome
        """
        try:
            self._conectar()
            
            # Verificar se já existe outro fabricante com o mesmo nome
            self.cursor.execute(
                'SELECT COUNT(*) FROM manufacturers WHERE name = ? AND id != ?',
                (manufacturer.name, manufacturer.id)
            )
            if self.cursor.fetchone()[0] > 0:
                raise ValueError(f"Já existe outro fabricante com o nome '{manufacturer.name}'")
            
            # Atualizar timestamp
            manufacturer.updated_at = datetime.now()
            
            self.cursor.execute('''
            UPDATE manufacturers 
            SET name = ?, country = ?, official_website = ?, updated_at = ?
            WHERE id = ?
            ''', (manufacturer.name, manufacturer.country, manufacturer.official_website,
                  manufacturer.updated_at, manufacturer.id))
            
            self.conn.commit()
            
            return self.cursor.rowcount > 0
        finally:
            self._desconectar()
    
    def excluir(self, manufacturer_id: int) -> bool:
        """
        Exclui um fabricante pelo ID.
        
        Args:
            manufacturer_id: ID do fabricante a ser excluído
            
        Returns:
            bool: True se excluiu com sucesso, False caso contrário
        """
        try:
            self._conectar()
            self.cursor.execute('DELETE FROM manufacturers WHERE id = ?', (manufacturer_id,))
            self.conn.commit()
            
            return self.cursor.rowcount > 0
        finally:
            self._desconectar()
    
    def existe_nome(self, name: str, excluir_id: Optional[int] = None) -> bool:
        """
        Verifica se já existe um fabricante com o nome especificado.
        
        Args:
            name: Nome do fabricante
            excluir_id: ID a ser excluído da verificação (para updates)
            
        Returns:
            bool: True se existe, False caso contrário
        """
        try:
            self._conectar()
            if excluir_id:
                self.cursor.execute(
                    'SELECT COUNT(*) FROM manufacturers WHERE name = ? AND id != ?',
                    (name, excluir_id)
                )
            else:
                self.cursor.execute('SELECT COUNT(*) FROM manufacturers WHERE name = ?', (name,))
            
            count = self.cursor.fetchone()[0]
            return count > 0
        finally:
            self._desconectar()
    
    def contar_total(self) -> int:
        """
        Conta o total de fabricantes cadastrados.
        
        Returns:
            int: Número total de fabricantes
        """
        try:
            self._conectar()
            self.cursor.execute('SELECT COUNT(*) FROM manufacturers')
            return self.cursor.fetchone()[0]
        finally:
            self._desconectar()
    
    def listar_paises(self) -> List[str]:
        """
        Lista todos os países únicos dos fabricantes.
        
        Returns:
            List[str]: Lista de países únicos
        """
        try:
            self._conectar()
            self.cursor.execute('''
            SELECT DISTINCT country 
            FROM manufacturers 
            WHERE country IS NOT NULL AND country != ''
            ORDER BY country
            ''')
            resultados = self.cursor.fetchall()
            
            return [resultado[0] for resultado in resultados]
        finally:
            self._desconectar()
    
    def _row_to_entity(self, row: tuple) -> Manufacturer:
        """
        Converte uma linha do banco de dados em uma entidade Manufacturer.
        
        Args:
            row: Tupla com os dados da linha do banco
            
        Returns:
            Manufacturer: Instância da entidade Manufacturer
        """
        # Converter strings de datetime se necessário
        created_at_obj = None
        if row[4]:  # campo created_at
            if isinstance(row[4], str):
                try:
                    created_at_obj = datetime.fromisoformat(row[4])
                except ValueError:
                    try:
                        created_at_obj = datetime.strptime(row[4], '%Y-%m-%d %H:%M:%S')
                    except ValueError:
                        created_at_obj = datetime.strptime(row[4], '%Y-%m-%d')
            else:
                created_at_obj = row[4]
        
        updated_at_obj = None
        if row[5]:  # campo updated_at
            if isinstance(row[5], str):
                try:
                    updated_at_obj = datetime.fromisoformat(row[5])
                except ValueError:
                    try:
                        updated_at_obj = datetime.strptime(row[5], '%Y-%m-%d %H:%M:%S')
                    except ValueError:
                        updated_at_obj = datetime.strptime(row[5], '%Y-%m-%d')
            else:
                updated_at_obj = row[5]
        
        return Manufacturer(
            id=row[0],
            name=row[1],
            country=row[2],
            official_website=row[3],
            created_at=created_at_obj,
            updated_at=updated_at_obj
        )

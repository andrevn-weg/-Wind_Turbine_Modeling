import sqlite3
from typing import Optional, List

from .entity import MeteorologicalDataSource


class MeteorologicalDataSourceRepository:
    """
    Classe responsável pela persistência e recuperação de dados de Fonte de Dados Meteorológicos no banco de dados.
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
        """Cria a tabela de fontes de dados meteorológicos se não existir"""
        try:
            self._conectar()
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS meteorological_data_source (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                description TEXT
            )
            ''')
            self.conn.commit()
        finally:
            self._desconectar()
    
    def salvar(self, fonte: MeteorologicalDataSource) -> int:
        """
        Salva uma nova fonte de dados meteorológicos no banco de dados.
        
        Args:
            fonte: Instância de MeteorologicalDataSource a ser salva
            
        Returns:
            int: ID da fonte inserida
            
        Raises:
            ValueError: Se a fonte não passa na validação
        """
        if not fonte.validar():
            raise ValueError("Dados da fonte de dados meteorológicos são inválidos")
            
        try:
            self._conectar()
            self.cursor.execute('''
            INSERT INTO meteorological_data_source (name, description)
            VALUES (?, ?)
            ''', (fonte.formatar_nome(), fonte.description))
            self.conn.commit()
            fonte_id = self.cursor.lastrowid
            fonte.id = fonte_id  # Atualiza o ID da instância
            return fonte_id
        finally:
            self._desconectar()
    
    def buscar_por_id(self, fonte_id: int) -> Optional[MeteorologicalDataSource]:
        """
        Busca uma fonte de dados meteorológicos pelo seu ID.
        
        Args:
            fonte_id: ID da fonte a ser buscada
            
        Returns:
            Optional[MeteorologicalDataSource]: Instância de MeteorologicalDataSource se encontrada, None caso contrário
        """
        try:
            self._conectar()
            self.cursor.execute('SELECT * FROM meteorological_data_source WHERE id = ?', (fonte_id,))
            resultado = self.cursor.fetchone()
            
            if resultado:
                return self._row_to_entity(resultado)
            return None
        finally:
            self._desconectar()
    
    def buscar_por_nome(self, name: str) -> Optional[MeteorologicalDataSource]:
        """
        Busca uma fonte de dados meteorológicos pelo nome.
        
        Args:
            name: Nome da fonte a ser buscada
            
        Returns:
            Optional[MeteorologicalDataSource]: Instância de MeteorologicalDataSource se encontrada, None caso contrário
        """
        try:
            self._conectar()
            self.cursor.execute('SELECT * FROM meteorological_data_source WHERE name = ?', (name.upper(),))
            resultado = self.cursor.fetchone()
            
            if resultado:
                return self._row_to_entity(resultado)
            return None
        finally:
            self._desconectar()
    
    def buscar_por_termo(self, termo: str) -> List[MeteorologicalDataSource]:
        """
        Busca fontes de dados meteorológicos cujo nome ou descrição contenha o termo informado.
        
        Args:
            termo: Termo a ser buscado nos nomes e descrições das fontes
            
        Returns:
            List[MeteorologicalDataSource]: Lista de fontes encontradas
        """
        try:
            self._conectar()
            self.cursor.execute('''
            SELECT * FROM meteorological_data_source 
            WHERE name LIKE ? OR description LIKE ? 
            ORDER BY name
            ''', (f'%{termo}%', f'%{termo}%'))
            resultados = self.cursor.fetchall()
            
            return [self._row_to_entity(resultado) for resultado in resultados]
        finally:
            self._desconectar()
    
    def listar_todos(self) -> List[MeteorologicalDataSource]:
        """
        Lista todas as fontes de dados meteorológicos cadastradas.
        
        Returns:
            List[MeteorologicalDataSource]: Lista com todas as fontes
        """
        try:
            self._conectar()
            self.cursor.execute('SELECT * FROM meteorological_data_source ORDER BY name')
            resultados = self.cursor.fetchall()
            
            return [self._row_to_entity(resultado) for resultado in resultados]
        finally:
            self._desconectar()
    
    def atualizar(self, fonte: MeteorologicalDataSource) -> bool:
        """
        Atualiza os dados de uma fonte de dados meteorológicos existente.
        
        Args:
            fonte: Instância de MeteorologicalDataSource com os dados atualizados
            
        Returns:
            bool: True se a atualização foi bem-sucedida, False caso contrário
            
        Raises:
            ValueError: Se a fonte não tem ID ou não passa na validação
        """
        if not fonte.id:
            raise ValueError("Fonte de dados deve ter um ID para ser atualizada")
        if not fonte.validar():
            raise ValueError("Dados da fonte de dados meteorológicos são inválidos")
            
        try:
            self._conectar()
            self.cursor.execute('''
            UPDATE meteorological_data_source
            SET name = ?, description = ?
            WHERE id = ?
            ''', (fonte.formatar_nome(), fonte.description, fonte.id))
            self.conn.commit()
            
            return self.cursor.rowcount > 0
        finally:
            self._desconectar()
    
    def excluir(self, fonte_id: int) -> bool:
        """
        Remove uma fonte de dados meteorológicos do banco de dados.
        
        Args:
            fonte_id: ID da fonte a ser removida
            
        Returns:
            bool: True se a exclusão foi bem-sucedida, False caso contrário
        """
        try:
            self._conectar()
            self.cursor.execute('DELETE FROM meteorological_data_source WHERE id = ?', (fonte_id,))
            self.conn.commit()
            
            return self.cursor.rowcount > 0
        finally:
            self._desconectar()
    
    def existe_nome(self, name: str, excluir_id: Optional[int] = None) -> bool:
        """
        Verifica se já existe uma fonte com o nome informado.
        
        Args:
            name: Nome a ser verificado
            excluir_id: ID da fonte a ser excluída da verificação (para updates)
            
        Returns:
            bool: True se o nome já existe, False caso contrário
        """
        try:
            self._conectar()
            if excluir_id:
                self.cursor.execute('''
                SELECT COUNT(*) FROM meteorological_data_source 
                WHERE name = ? AND id != ?
                ''', (name.upper(), excluir_id))
            else:
                self.cursor.execute('''
                SELECT COUNT(*) FROM meteorological_data_source 
                WHERE name = ?
                ''', (name.upper(),))
            
            resultado = self.cursor.fetchone()
            return resultado[0] > 0
        finally:
            self._desconectar()
    
    def _row_to_entity(self, row: tuple) -> MeteorologicalDataSource:
        """
        Converte uma linha do banco de dados em uma entidade MeteorologicalDataSource.
        
        Args:
            row: Tupla com os dados da linha do banco
            
        Returns:
            MeteorologicalDataSource: Instância da entidade MeteorologicalDataSource
        """
        return MeteorologicalDataSource(
            id=row[0],
            name=row[1],
            description=row[2]
        )

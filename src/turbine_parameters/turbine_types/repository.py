import sqlite3
from typing import Optional, List

from .entity import TurbineType


class TurbineTypeRepository:
    """
    Classe responsável pela persistência e recuperação de dados de Tipos de Turbina no banco de dados.
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
        """Cria a tabela de tipos de turbina se não existir"""
        try:
            self._conectar()
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS turbine_types (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                type VARCHAR NOT NULL UNIQUE,
                description TEXT
            )
            ''')
            self.conn.commit()
        finally:
            self._desconectar()
    
    def salvar(self, turbine_type: TurbineType) -> int:
        """
        Salva um tipo de turbina no banco de dados.
        
        Args:
            turbine_type: Instância do tipo de turbina a ser salvo
            
        Returns:
            int: ID do tipo de turbina salvo
            
        Raises:
            ValueError: Se já existir um tipo de turbina com o mesmo nome
        """
        try:
            self._conectar()
            
            # Verificar se já existe um tipo de turbina com o mesmo nome
            if self.existe_tipo(turbine_type.type):
                raise ValueError(f"Já existe um tipo de turbina '{turbine_type.type}'")
            
            self.cursor.execute('''
            INSERT INTO turbine_types (type, description)
            VALUES (?, ?)
            ''', (turbine_type.type, turbine_type.description))
            
            self.conn.commit()
            type_id = self.cursor.lastrowid
            turbine_type.id = type_id  # Atualiza o ID da instância
            return type_id
        finally:
            self._desconectar()
    
    def buscar_por_id(self, type_id: int) -> Optional[TurbineType]:
        """
        Busca um tipo de turbina pelo ID.
        
        Args:
            type_id: ID do tipo de turbina
            
        Returns:
            Optional[TurbineType]: Tipo de turbina encontrado ou None
        """
        try:
            self._conectar()
            self.cursor.execute('SELECT * FROM turbine_types WHERE id = ?', (type_id,))
            resultado = self.cursor.fetchone()
            
            if resultado:
                return self._row_to_entity(resultado)
            return None
        finally:
            self._desconectar()
    
    def buscar_por_tipo(self, type_name: str) -> Optional[TurbineType]:
        """
        Busca um tipo de turbina pelo nome do tipo.
        
        Args:
            type_name: Nome do tipo de turbina
            
        Returns:
            Optional[TurbineType]: Tipo de turbina encontrado ou None
        """
        try:
            self._conectar()
            self.cursor.execute('SELECT * FROM turbine_types WHERE type = ?', (type_name,))
            resultado = self.cursor.fetchone()
            
            if resultado:
                return self._row_to_entity(resultado)
            return None
        finally:
            self._desconectar()
    
    def buscar_por_termo(self, termo: str) -> List[TurbineType]:
        """
        Busca tipos de turbina que contenham o termo no nome ou descrição.
        
        Args:
            termo: Termo a ser buscado
            
        Returns:
            List[TurbineType]: Lista de tipos de turbina encontrados
        """
        try:
            self._conectar()
            self.cursor.execute('''
            SELECT * FROM turbine_types 
            WHERE type LIKE ? OR description LIKE ?
            ORDER BY type
            ''', (f'%{termo}%', f'%{termo}%'))
            resultados = self.cursor.fetchall()
            
            return [self._row_to_entity(resultado) for resultado in resultados]
        finally:
            self._desconectar()
    
    def listar_todos(self) -> List[TurbineType]:
        """
        Lista todos os tipos de turbina ordenados por tipo.
        
        Returns:
            List[TurbineType]: Lista de todos os tipos de turbina
        """
        try:
            self._conectar()
            self.cursor.execute('SELECT * FROM turbine_types ORDER BY type')
            resultados = self.cursor.fetchall()
            
            return [self._row_to_entity(resultado) for resultado in resultados]
        finally:
            self._desconectar()
    
    def atualizar(self, turbine_type: TurbineType) -> bool:
        """
        Atualiza um tipo de turbina existente.
        
        Args:
            turbine_type: Tipo de turbina com dados atualizados
            
        Returns:
            bool: True se atualizou com sucesso, False caso contrário
            
        Raises:
            ValueError: Se já existir outro tipo de turbina com o mesmo nome
        """
        try:
            self._conectar()
            
            # Verificar se já existe outro tipo de turbina com o mesmo nome
            if self.existe_tipo(turbine_type.type, excluir_id=turbine_type.id):
                raise ValueError(f"Já existe outro tipo de turbina '{turbine_type.type}'")
            
            self.cursor.execute('''
            UPDATE turbine_types 
            SET type = ?, description = ?
            WHERE id = ?
            ''', (turbine_type.type, turbine_type.description, turbine_type.id))
            
            self.conn.commit()
            
            return self.cursor.rowcount > 0
        finally:
            self._desconectar()
    
    def excluir(self, type_id: int) -> bool:
        """
        Exclui um tipo de turbina pelo ID.
        
        Args:
            type_id: ID do tipo de turbina a ser excluído
            
        Returns:
            bool: True se excluiu com sucesso, False caso contrário
        """
        try:
            self._conectar()
            self.cursor.execute('DELETE FROM turbine_types WHERE id = ?', (type_id,))
            self.conn.commit()
            
            return self.cursor.rowcount > 0
        finally:
            self._desconectar()
    
    def existe_tipo(self, type_name: str, excluir_id: Optional[int] = None) -> bool:
        """
        Verifica se já existe um tipo de turbina com o nome especificado.
        
        Args:
            type_name: Nome do tipo de turbina
            excluir_id: ID a ser excluído da verificação (para updates)
            
        Returns:
            bool: True se existe, False caso contrário
        """
        try:
            self._conectar()
            if excluir_id:
                self.cursor.execute(
                    'SELECT COUNT(*) FROM turbine_types WHERE type = ? AND id != ?',
                    (type_name, excluir_id)
                )
            else:
                self.cursor.execute('SELECT COUNT(*) FROM turbine_types WHERE type = ?', (type_name,))
            
            count = self.cursor.fetchone()[0]
            return count > 0
        finally:
            self._desconectar()
    
    def contar_total(self) -> int:
        """
        Conta o total de tipos de turbina cadastrados.
        
        Returns:
            int: Número total de tipos de turbina
        """
        try:
            self._conectar()
            self.cursor.execute('SELECT COUNT(*) FROM turbine_types')
            return self.cursor.fetchone()[0]
        finally:
            self._desconectar()
    
    def inicializar_tipos_padrao(self) -> None:
        """
        Inicializa os tipos padrão de turbina se não existirem.
        """
        tipos_padrao = [
            TurbineType(
                type="Horizontal",
                description="Turbinas de eixo horizontal - tipo mais comum, com rotor paralelo ao solo"
            ),
            TurbineType(
                type="Vertical",
                description="Turbinas de eixo vertical - rotor perpendicular ao solo, captam vento de qualquer direção"
            )
        ]
        
        for tipo in tipos_padrao:
            try:
                if not self.existe_tipo(tipo.type):
                    self.salvar(tipo)
            except ValueError:
                # Tipo já existe, continuar
                continue
    
    def _row_to_entity(self, row: tuple) -> TurbineType:
        """
        Converte uma linha do banco de dados em uma entidade TurbineType.
        
        Args:
            row: Tupla com os dados da linha do banco
            
        Returns:
            TurbineType: Instância da entidade TurbineType
        """
        return TurbineType(
            id=row[0],
            type=row[1],
            description=row[2]
        )

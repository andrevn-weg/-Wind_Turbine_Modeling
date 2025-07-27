import sqlite3
from typing import Optional, List

from .entity import ControlType


class ControlTypeRepository:
    """
    Classe responsável pela persistência e recuperação de dados de Tipos de Controle no banco de dados.
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
        """Cria a tabela de tipos de controle se não existir"""
        try:
            self._conectar()
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS control_types (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                type VARCHAR NOT NULL UNIQUE,
                description TEXT
            )
            ''')
            self.conn.commit()
        finally:
            self._desconectar()
    
    def salvar(self, control_type: ControlType) -> int:
        """
        Salva um tipo de controle no banco de dados.
        
        Args:
            control_type: Instância do tipo de controle a ser salvo
            
        Returns:
            int: ID do tipo de controle salvo
            
        Raises:
            ValueError: Se já existir um tipo de controle com o mesmo nome
        """
        try:
            self._conectar()
            
            # Verificar se já existe um tipo de controle com o mesmo nome
            if self.existe_tipo(control_type.type):
                raise ValueError(f"Já existe um tipo de controle '{control_type.type}'")
            
            self.cursor.execute('''
            INSERT INTO control_types (type, description)
            VALUES (?, ?)
            ''', (control_type.type, control_type.description))
            
            self.conn.commit()
            type_id = self.cursor.lastrowid
            control_type.id = type_id  # Atualiza o ID da instância
            return type_id
        finally:
            self._desconectar()
    
    def buscar_por_id(self, type_id: int) -> Optional[ControlType]:
        """
        Busca um tipo de controle pelo ID.
        
        Args:
            type_id: ID do tipo de controle
            
        Returns:
            Optional[ControlType]: Tipo de controle encontrado ou None
        """
        try:
            self._conectar()
            self.cursor.execute('SELECT * FROM control_types WHERE id = ?', (type_id,))
            resultado = self.cursor.fetchone()
            
            if resultado:
                return self._row_to_entity(resultado)
            return None
        finally:
            self._desconectar()
    
    def buscar_por_tipo(self, type_name: str) -> Optional[ControlType]:
        """
        Busca um tipo de controle pelo nome do tipo.
        
        Args:
            type_name: Nome do tipo de controle
            
        Returns:
            Optional[ControlType]: Tipo de controle encontrado ou None
        """
        try:
            self._conectar()
            self.cursor.execute('SELECT * FROM control_types WHERE type = ?', (type_name,))
            resultado = self.cursor.fetchone()
            
            if resultado:
                return self._row_to_entity(resultado)
            return None
        finally:
            self._desconectar()
    
    def buscar_por_termo(self, termo: str) -> List[ControlType]:
        """
        Busca tipos de controle que contenham o termo no nome ou descrição.
        
        Args:
            termo: Termo a ser buscado
            
        Returns:
            List[ControlType]: Lista de tipos de controle encontrados
        """
        try:
            self._conectar()
            self.cursor.execute('''
            SELECT * FROM control_types 
            WHERE type LIKE ? OR description LIKE ?
            ORDER BY type
            ''', (f'%{termo}%', f'%{termo}%'))
            resultados = self.cursor.fetchall()
            
            return [self._row_to_entity(resultado) for resultado in resultados]
        finally:
            self._desconectar()
    
    def listar_todos(self) -> List[ControlType]:
        """
        Lista todos os tipos de controle ordenados por tipo.
        
        Returns:
            List[ControlType]: Lista de todos os tipos de controle
        """
        try:
            self._conectar()
            self.cursor.execute('SELECT * FROM control_types ORDER BY type')
            resultados = self.cursor.fetchall()
            
            return [self._row_to_entity(resultado) for resultado in resultados]
        finally:
            self._desconectar()
    
    def listar_que_requerem_pitch(self) -> List[ControlType]:
        """
        Lista tipos de controle que requerem atuadores de pitch.
        
        Returns:
            List[ControlType]: Lista de tipos de controle com pitch
        """
        try:
            self._conectar()
            self.cursor.execute('''
            SELECT * FROM control_types 
            WHERE type IN ('Pitch', 'Active Stall')
            ORDER BY type
            ''')
            resultados = self.cursor.fetchall()
            
            return [self._row_to_entity(resultado) for resultado in resultados]
        finally:
            self._desconectar()
    
    def listar_controles_passivos(self) -> List[ControlType]:
        """
        Lista tipos de controle passivos.
        
        Returns:
            List[ControlType]: Lista de tipos de controle passivos
        """
        try:
            self._conectar()
            self.cursor.execute('''
            SELECT * FROM control_types 
            WHERE type = 'Stall'
            ORDER BY type
            ''')
            resultados = self.cursor.fetchall()
            
            return [self._row_to_entity(resultado) for resultado in resultados]
        finally:
            self._desconectar()
    
    def atualizar(self, control_type: ControlType) -> bool:
        """
        Atualiza um tipo de controle existente.
        
        Args:
            control_type: Tipo de controle com dados atualizados
            
        Returns:
            bool: True se atualizou com sucesso, False caso contrário
            
        Raises:
            ValueError: Se já existir outro tipo de controle com o mesmo nome
        """
        try:
            self._conectar()
            
            # Verificar se já existe outro tipo de controle com o mesmo nome
            if self.existe_tipo(control_type.type, excluir_id=control_type.id):
                raise ValueError(f"Já existe outro tipo de controle '{control_type.type}'")
            
            self.cursor.execute('''
            UPDATE control_types 
            SET type = ?, description = ?
            WHERE id = ?
            ''', (control_type.type, control_type.description, control_type.id))
            
            self.conn.commit()
            
            return self.cursor.rowcount > 0
        finally:
            self._desconectar()
    
    def excluir(self, type_id: int) -> bool:
        """
        Exclui um tipo de controle pelo ID.
        
        Args:
            type_id: ID do tipo de controle a ser excluído
            
        Returns:
            bool: True se excluiu com sucesso, False caso contrário
        """
        try:
            self._conectar()
            self.cursor.execute('DELETE FROM control_types WHERE id = ?', (type_id,))
            self.conn.commit()
            
            return self.cursor.rowcount > 0
        finally:
            self._desconectar()
    
    def existe_tipo(self, type_name: str, excluir_id: Optional[int] = None) -> bool:
        """
        Verifica se já existe um tipo de controle com o nome especificado.
        
        Args:
            type_name: Nome do tipo de controle
            excluir_id: ID a ser excluído da verificação (para updates)
            
        Returns:
            bool: True se existe, False caso contrário
        """
        try:
            self._conectar()
            if excluir_id:
                self.cursor.execute(
                    'SELECT COUNT(*) FROM control_types WHERE type = ? AND id != ?',
                    (type_name, excluir_id)
                )
            else:
                self.cursor.execute('SELECT COUNT(*) FROM control_types WHERE type = ?', (type_name,))
            
            count = self.cursor.fetchone()[0]
            return count > 0
        finally:
            self._desconectar()
    
    def contar_total(self) -> int:
        """
        Conta o total de tipos de controle cadastrados.
        
        Returns:
            int: Número total de tipos de controle
        """
        try:
            self._conectar()
            self.cursor.execute('SELECT COUNT(*) FROM control_types')
            return self.cursor.fetchone()[0]
        finally:
            self._desconectar()
    
    def inicializar_tipos_padrao(self) -> None:
        """
        Inicializa os tipos padrão de controle se não existirem.
        """
        tipos_padrao = [
            ControlType(
                type="Pitch",
                description="Controle ativo através do ângulo das pás - maior eficiência e controle preciso"
            ),
            ControlType(
                type="Stall",
                description="Controle passivo através do stall aerodinâmico - design mais simples e robusto"
            ),
            ControlType(
                type="Active Stall",
                description="Controle ativo do stall através do ângulo das pás - combina eficiências do pitch e stall"
            )
        ]
        
        for tipo in tipos_padrao:
            try:
                if not self.existe_tipo(tipo.type):
                    self.salvar(tipo)
            except ValueError:
                # Tipo já existe, continuar
                continue
    
    def _row_to_entity(self, row: tuple) -> ControlType:
        """
        Converte uma linha do banco de dados em uma entidade ControlType.
        
        Args:
            row: Tupla com os dados da linha do banco
            
        Returns:
            ControlType: Instância da entidade ControlType
        """
        return ControlType(
            id=row[0],
            type=row[1],
            description=row[2]
        )

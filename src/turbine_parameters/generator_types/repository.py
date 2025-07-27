import sqlite3
from typing import Optional, List

from .entity import GeneratorType


class GeneratorTypeRepository:
    """
    Classe responsável pela persistência e recuperação de dados de Tipos de Gerador no banco de dados.
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
        """Cria a tabela de tipos de gerador se não existir"""
        try:
            self._conectar()
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS generator_types (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                type VARCHAR NOT NULL UNIQUE,
                description TEXT
            )
            ''')
            self.conn.commit()
        finally:
            self._desconectar()
    
    def salvar(self, generator_type: GeneratorType) -> int:
        """
        Salva um tipo de gerador no banco de dados.
        
        Args:
            generator_type: Instância do tipo de gerador a ser salvo
            
        Returns:
            int: ID do tipo de gerador salvo
            
        Raises:
            ValueError: Se já existir um tipo de gerador com o mesmo nome
        """
        try:
            self._conectar()
            
            # Verificar se já existe um tipo de gerador com o mesmo nome
            if self.existe_tipo(generator_type.type):
                raise ValueError(f"Já existe um tipo de gerador '{generator_type.type}'")
            
            self.cursor.execute('''
            INSERT INTO generator_types (type, description)
            VALUES (?, ?)
            ''', (generator_type.type, generator_type.description))
            
            self.conn.commit()
            type_id = self.cursor.lastrowid
            generator_type.id = type_id  # Atualiza o ID da instância
            return type_id
        finally:
            self._desconectar()
    
    def buscar_por_id(self, type_id: int) -> Optional[GeneratorType]:
        """
        Busca um tipo de gerador pelo ID.
        
        Args:
            type_id: ID do tipo de gerador
            
        Returns:
            Optional[GeneratorType]: Tipo de gerador encontrado ou None
        """
        try:
            self._conectar()
            self.cursor.execute('SELECT * FROM generator_types WHERE id = ?', (type_id,))
            resultado = self.cursor.fetchone()
            
            if resultado:
                return self._row_to_entity(resultado)
            return None
        finally:
            self._desconectar()
    
    def buscar_por_tipo(self, type_name: str) -> Optional[GeneratorType]:
        """
        Busca um tipo de gerador pelo nome do tipo.
        
        Args:
            type_name: Nome do tipo de gerador
            
        Returns:
            Optional[GeneratorType]: Tipo de gerador encontrado ou None
        """
        try:
            self._conectar()
            self.cursor.execute('SELECT * FROM generator_types WHERE type = ?', (type_name,))
            resultado = self.cursor.fetchone()
            
            if resultado:
                return self._row_to_entity(resultado)
            return None
        finally:
            self._desconectar()
    
    def buscar_por_termo(self, termo: str) -> List[GeneratorType]:
        """
        Busca tipos de gerador que contenham o termo no nome ou descrição.
        
        Args:
            termo: Termo a ser buscado
            
        Returns:
            List[GeneratorType]: Lista de tipos de gerador encontrados
        """
        try:
            self._conectar()
            self.cursor.execute('''
            SELECT * FROM generator_types 
            WHERE type LIKE ? OR description LIKE ?
            ORDER BY type
            ''', (f'%{termo}%', f'%{termo}%'))
            resultados = self.cursor.fetchall()
            
            return [self._row_to_entity(resultado) for resultado in resultados]
        finally:
            self._desconectar()
    
    def listar_todos(self) -> List[GeneratorType]:
        """
        Lista todos os tipos de gerador ordenados por tipo.
        
        Returns:
            List[GeneratorType]: Lista de todos os tipos de gerador
        """
        try:
            self._conectar()
            self.cursor.execute('SELECT * FROM generator_types ORDER BY type')
            resultados = self.cursor.fetchall()
            
            return [self._row_to_entity(resultado) for resultado in resultados]
        finally:
            self._desconectar()
    
    def atualizar(self, generator_type: GeneratorType) -> bool:
        """
        Atualiza um tipo de gerador existente.
        
        Args:
            generator_type: Tipo de gerador com dados atualizados
            
        Returns:
            bool: True se atualizou com sucesso, False caso contrário
            
        Raises:
            ValueError: Se já existir outro tipo de gerador com o mesmo nome
        """
        try:
            self._conectar()
            
            # Verificar se já existe outro tipo de gerador com o mesmo nome
            if self.existe_tipo(generator_type.type, excluir_id=generator_type.id):
                raise ValueError(f"Já existe outro tipo de gerador '{generator_type.type}'")
            
            self.cursor.execute('''
            UPDATE generator_types 
            SET type = ?, description = ?
            WHERE id = ?
            ''', (generator_type.type, generator_type.description, generator_type.id))
            
            self.conn.commit()
            
            return self.cursor.rowcount > 0
        finally:
            self._desconectar()
    
    def excluir(self, type_id: int) -> bool:
        """
        Exclui um tipo de gerador pelo ID.
        
        Args:
            type_id: ID do tipo de gerador a ser excluído
            
        Returns:
            bool: True se excluiu com sucesso, False caso contrário
        """
        try:
            self._conectar()
            self.cursor.execute('DELETE FROM generator_types WHERE id = ?', (type_id,))
            self.conn.commit()
            
            return self.cursor.rowcount > 0
        finally:
            self._desconectar()
    
    def existe_tipo(self, type_name: str, excluir_id: Optional[int] = None) -> bool:
        """
        Verifica se já existe um tipo de gerador com o nome especificado.
        
        Args:
            type_name: Nome do tipo de gerador
            excluir_id: ID a ser excluído da verificação (para updates)
            
        Returns:
            bool: True se existe, False caso contrário
        """
        try:
            self._conectar()
            if excluir_id:
                self.cursor.execute(
                    'SELECT COUNT(*) FROM generator_types WHERE type = ? AND id != ?',
                    (type_name, excluir_id)
                )
            else:
                self.cursor.execute('SELECT COUNT(*) FROM generator_types WHERE type = ?', (type_name,))
            
            count = self.cursor.fetchone()[0]
            return count > 0
        finally:
            self._desconectar()
    
    def contar_total(self) -> int:
        """
        Conta o total de tipos de gerador cadastrados.
        
        Returns:
            int: Número total de tipos de gerador
        """
        try:
            self._conectar()
            self.cursor.execute('SELECT COUNT(*) FROM generator_types')
            return self.cursor.fetchone()[0]
        finally:
            self._desconectar()
    
    def inicializar_tipos_padrao(self) -> None:
        """
        Inicializa os tipos padrão de gerador se não existirem.
        """
        tipos_padrao = [
            GeneratorType(
                type="Synchronous",
                description="Gerador síncrono - velocidade constante, conectado diretamente à rede"
            ),
            GeneratorType(
                type="Asynchronous",
                description="Gerador assíncrono (indução) - velocidade variável, mais simples e robusto"
            ),
            GeneratorType(
                type="PMSG",
                description="Permanent Magnet Synchronous Generator - alta eficiência, sem escovas"
            ),
            GeneratorType(
                type="DFIG",
                description="Doubly Fed Induction Generator - controle independente de potência ativa e reativa"
            )
        ]
        
        for tipo in tipos_padrao:
            try:
                if not self.existe_tipo(tipo.type):
                    self.salvar(tipo)
            except ValueError:
                # Tipo já existe, continuar
                continue
    
    def _row_to_entity(self, row: tuple) -> GeneratorType:
        """
        Converte uma linha do banco de dados em uma entidade GeneratorType.
        
        Args:
            row: Tupla com os dados da linha do banco
            
        Returns:
            GeneratorType: Instância da entidade GeneratorType
        """
        return GeneratorType(
            id=row[0],
            type=row[1],
            description=row[2]
        )

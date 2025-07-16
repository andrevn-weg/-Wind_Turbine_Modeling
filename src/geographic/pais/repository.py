import sqlite3
from typing import Optional, List

from .entity import Pais


class PaisRepository:
    """
    Classe responsável pela persistência e recuperação de dados de País no banco de dados.
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
    
    def salvar(self, pais: Pais) -> int:
        """
        Salva um novo país no banco de dados.
        
        Args:
            pais: Instância de País a ser salva
            
        Returns:
            int: ID do país inserido
            
        Raises:
            ValueError: Se o país não passa na validação
        """
        if not pais.validar():
            raise ValueError("Dados do país são inválidos")
            
        try:
            self._conectar()
            self.cursor.execute('''
            INSERT INTO paises (nome, codigo)
            VALUES (?, ?)
            ''', (pais.nome, pais.formatar_codigo()))
            self.conn.commit()
            pais_id = self.cursor.lastrowid
            pais.id = pais_id  # Atualiza o ID da instância
            return pais_id
        finally:
            self._desconectar()
    
    def buscar_por_id(self, pais_id: int) -> Optional[Pais]:
        """
        Busca um país pelo seu ID.
        
        Args:
            pais_id: ID do país a ser buscado
            
        Returns:
            Optional[Pais]: Instância de País se encontrada, None caso contrário
        """
        try:
            self._conectar()
            self.cursor.execute('SELECT * FROM paises WHERE id = ?', (pais_id,))
            resultado = self.cursor.fetchone()
            
            if resultado:
                return self._row_to_entity(resultado)
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
            self.cursor.execute('SELECT * FROM paises WHERE nome LIKE ? ORDER BY nome', (f'%{nome}%',))
            resultados = self.cursor.fetchall()
            
            return [self._row_to_entity(resultado) for resultado in resultados]
        finally:
            self._desconectar()
    
    def buscar_por_codigo(self, codigo: str) -> Optional[Pais]:
        """
        Busca um país pelo seu código ISO.
        
        Args:
            codigo: Código ISO do país (ex: "BR", "US")
            
        Returns:
            Optional[Pais]: Instância de País se encontrada, None caso contrário
        """
        try:
            self._conectar()
            self.cursor.execute('SELECT * FROM paises WHERE codigo = ?', (codigo.upper(),))
            resultado = self.cursor.fetchone()
            
            if resultado:
                return self._row_to_entity(resultado)
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
            
            return [self._row_to_entity(resultado) for resultado in resultados]
        finally:
            self._desconectar()
    
    def atualizar(self, pais: Pais) -> bool:
        """
        Atualiza os dados de um país existente.
        
        Args:
            pais: Instância de País com os dados atualizados
            
        Returns:
            bool: True se a atualização foi bem-sucedida, False caso contrário
            
        Raises:
            ValueError: Se o país não tem ID ou não passa na validação
        """
        if not pais.id:
            raise ValueError("País deve ter um ID para ser atualizado")
        if not pais.validar():
            raise ValueError("Dados do país são inválidos")
            
        try:
            self._conectar()
            self.cursor.execute('''
            UPDATE paises
            SET nome = ?, codigo = ?
            WHERE id = ?
            ''', (pais.nome, pais.formatar_codigo(), pais.id))
            self.conn.commit()
            
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
            
            return self.cursor.rowcount > 0
        finally:
            self._desconectar()
    
    def existe_codigo(self, codigo: str, excluir_id: Optional[int] = None) -> bool:
        """
        Verifica se já existe um país com o código informado.
        
        Args:
            codigo: Código ISO a ser verificado
            excluir_id: ID do país a ser excluído da verificação (para updates)
            
        Returns:
            bool: True se o código já existe, False caso contrário
        """
        try:
            self._conectar()
            if excluir_id:
                self.cursor.execute('SELECT COUNT(*) FROM paises WHERE codigo = ? AND id != ?', 
                                  (codigo.upper(), excluir_id))
            else:
                self.cursor.execute('SELECT COUNT(*) FROM paises WHERE codigo = ?', (codigo.upper(),))
            
            resultado = self.cursor.fetchone()
            return resultado[0] > 0
        finally:
            self._desconectar()
    
    def _row_to_entity(self, row: tuple) -> Pais:
        """
        Converte uma linha do banco de dados em uma entidade País.
        
        Args:
            row: Tupla com os dados da linha do banco
            
        Returns:
            Pais: Instância da entidade País
        """
        return Pais(
            id=row[0],
            nome=row[1],
            codigo=row[2]
        )

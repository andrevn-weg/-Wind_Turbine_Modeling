import sqlite3
from typing import Optional, List

from .entity import Regiao


class RegiaoRepository:
    """
    Classe responsável pela persistência e recuperação de dados de Região no banco de dados.
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
    
    def salvar(self, regiao: Regiao) -> int:
        """
        Salva uma nova região no banco de dados.
        
        Args:
            regiao: Instância de Região a ser salva
            
        Returns:
            int: ID da região inserida
            
        Raises:
            ValueError: Se a região não passa na validação
        """
        if not regiao.validar():
            raise ValueError("Dados da região são inválidos")
            
        try:
            self._conectar()
            self.cursor.execute('''
            INSERT INTO regioes (nome, pais_id, sigla)
            VALUES (?, ?, ?)
            ''', (regiao.nome, regiao.pais_id, regiao.formatar_sigla() if regiao.sigla else None))
            self.conn.commit()
            regiao_id = self.cursor.lastrowid
            regiao.id = regiao_id  # Atualiza o ID da instância
            return regiao_id
        finally:
            self._desconectar()
    
    def buscar_por_id(self, regiao_id: int) -> Optional[Regiao]:
        """
        Busca uma região pelo seu ID.
        
        Args:
            regiao_id: ID da região a ser buscada
            
        Returns:
            Optional[Regiao]: Instância de Região se encontrada, None caso contrário
        """
        try:
            self._conectar()
            self.cursor.execute('SELECT * FROM regioes WHERE id = ?', (regiao_id,))
            resultado = self.cursor.fetchone()
            
            if resultado:
                return self._row_to_entity(resultado)
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
            self.cursor.execute('SELECT * FROM regioes WHERE nome LIKE ? ORDER BY nome', (f'%{nome}%',))
            resultados = self.cursor.fetchall()
            
            return [self._row_to_entity(resultado) for resultado in resultados]
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
            
            return [self._row_to_entity(resultado) for resultado in resultados]
        finally:
            self._desconectar()
    
    def buscar_por_sigla(self, sigla: str) -> List[Regiao]:
        """
        Busca regiões pela sigla.
        
        Args:
            sigla: Sigla da região
            
        Returns:
            List[Regiao]: Lista de regiões encontradas com a sigla
        """
        try:
            self._conectar()
            self.cursor.execute('SELECT * FROM regioes WHERE sigla = ? ORDER BY nome', (sigla.upper(),))
            resultados = self.cursor.fetchall()
            
            return [self._row_to_entity(resultado) for resultado in resultados]
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
            
            return [self._row_to_entity(resultado) for resultado in resultados]
        finally:
            self._desconectar()
    
    def atualizar(self, regiao: Regiao) -> bool:
        """
        Atualiza os dados de uma região existente.
        
        Args:
            regiao: Instância de Região com os dados atualizados
            
        Returns:
            bool: True se a atualização foi bem-sucedida, False caso contrário
            
        Raises:
            ValueError: Se a região não tem ID ou não passa na validação
        """
        if not regiao.id:
            raise ValueError("Região deve ter um ID para ser atualizada")
        if not regiao.validar():
            raise ValueError("Dados da região são inválidos")
            
        try:
            self._conectar()
            self.cursor.execute('''
            UPDATE regioes
            SET nome = ?, pais_id = ?, sigla = ?
            WHERE id = ?
            ''', (regiao.nome, regiao.pais_id, regiao.formatar_sigla() if regiao.sigla else None, regiao.id))
            self.conn.commit()
            
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
            
            return self.cursor.rowcount > 0
        finally:
            self._desconectar()
    
    def existe_sigla_no_pais(self, sigla: str, pais_id: int, excluir_id: Optional[int] = None) -> bool:
        """
        Verifica se já existe uma região com a sigla informada no país.
        
        Args:
            sigla: Sigla a ser verificada
            pais_id: ID do país
            excluir_id: ID da região a ser excluída da verificação (para updates)
            
        Returns:
            bool: True se a sigla já existe no país, False caso contrário
        """
        try:
            self._conectar()
            if excluir_id:
                self.cursor.execute('''
                SELECT COUNT(*) FROM regioes 
                WHERE sigla = ? AND pais_id = ? AND id != ?
                ''', (sigla.upper(), pais_id, excluir_id))
            else:
                self.cursor.execute('''
                SELECT COUNT(*) FROM regioes 
                WHERE sigla = ? AND pais_id = ?
                ''', (sigla.upper(), pais_id))
            
            resultado = self.cursor.fetchone()
            return resultado[0] > 0
        finally:
            self._desconectar()
    
    def _row_to_entity(self, row: tuple) -> Regiao:
        """
        Converte uma linha do banco de dados em uma entidade Região.
        
        Args:
            row: Tupla com os dados da linha do banco
            
        Returns:
            Regiao: Instância da entidade Região
        """
        return Regiao(
            id=row[0],
            nome=row[1],
            pais_id=row[2],
            sigla=row[3]
        )

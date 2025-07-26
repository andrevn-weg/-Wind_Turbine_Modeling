import sqlite3
from typing import Optional, List, Tuple, Dict
from datetime import datetime, date

from .entity import MeteorologicalData


class MeteorologicalDataRepository:
    """
    Classe responsável pela persistência e recuperação de dados meteorológicos no banco de dados.
    Implementa o padrão Repository para operações CRUD com consultas relacionais avançadas.
    
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
        """Cria a tabela de dados meteorológicos se não existir"""
        try:
            self._conectar()
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS meteorological_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                meteorological_data_source_id INTEGER NOT NULL,
                cidade_id INTEGER NOT NULL,
                data_hora TIMESTAMP NOT NULL,
                altura_captura REAL,
                velocidade_vento REAL,
                temperatura REAL,
                umidade REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (meteorological_data_source_id) REFERENCES meteorological_data_source (id),
                FOREIGN KEY (cidade_id) REFERENCES cidades (id)
            )
            ''')
            self.conn.commit()
        finally:
            self._desconectar()
    
    def salvar(self, dados: MeteorologicalData) -> int:
        """
        Salva novos dados meteorológicos no banco de dados.
        
        Args:
            dados: Instância de MeteorologicalData a ser salva
            
        Returns:
            int: ID dos dados inseridos
            
        Raises:
            ValueError: Se os dados não passam na validação
        """
        if not dados.validar():
            raise ValueError("Dados meteorológicos são inválidos")
        
        # Se created_at não foi definido, usar o timestamp atual
        if not dados.created_at:
            dados.created_at = datetime.now()
            
        try:
            self._conectar()
            self.cursor.execute('''
            INSERT INTO meteorological_data 
            (meteorological_data_source_id, cidade_id, data_hora, altura_captura, 
             velocidade_vento, temperatura, umidade, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (dados.meteorological_data_source_id, dados.cidade_id, dados.data_hora,
                  dados.altura_captura, dados.velocidade_vento, dados.temperatura,
                  dados.umidade, dados.created_at))
            self.conn.commit()
            dados_id = self.cursor.lastrowid
            dados.id = dados_id  # Atualiza o ID da instância
            return dados_id
        finally:
            self._desconectar()
    
    def buscar_por_id(self, dados_id: int) -> Optional[MeteorologicalData]:
        """
        Busca dados meteorológicos pelo seu ID.
        
        Args:
            dados_id: ID dos dados a serem buscados
            
        Returns:
            Optional[MeteorologicalData]: Instância se encontrada, None caso contrário
        """
        try:
            self._conectar()
            self.cursor.execute('SELECT * FROM meteorological_data WHERE id = ?', (dados_id,))
            resultado = self.cursor.fetchone()
            
            if resultado:
                return self._row_to_entity(resultado)
            return None
        finally:
            self._desconectar()
    
    def buscar_por_cidade(self, cidade_id: int, limite: Optional[int] = None) -> List[MeteorologicalData]:
        """
        Busca dados meteorológicos por cidade.
        
        Args:
            cidade_id: ID da cidade
            limite: Número máximo de registros a retornar
            
        Returns:
            List[MeteorologicalData]: Lista de dados meteorológicos
        """
        try:
            self._conectar()
            query = 'SELECT * FROM meteorological_data WHERE cidade_id = ? ORDER BY data_hora DESC'
            params = [cidade_id]
            
            if limite:
                query += ' LIMIT ?'
                params.append(limite)
            
            self.cursor.execute(query, params)
            resultados = self.cursor.fetchall()
            
            return [self._row_to_entity(resultado) for resultado in resultados]
        finally:
            self._desconectar()
    
    def buscar_por_fonte(self, fonte_id: int, limite: Optional[int] = None) -> List[MeteorologicalData]:
        """
        Busca dados meteorológicos por fonte de dados.
        
        Args:
            fonte_id: ID da fonte de dados
            limite: Número máximo de registros a retornar
            
        Returns:
            List[MeteorologicalData]: Lista de dados meteorológicos
        """
        try:
            self._conectar()
            query = 'SELECT * FROM meteorological_data WHERE meteorological_data_source_id = ? ORDER BY data_hora DESC'
            params = [fonte_id]
            
            if limite:
                query += ' LIMIT ?'
                params.append(limite)
            
            self.cursor.execute(query, params)
            resultados = self.cursor.fetchall()
            
            return [self._row_to_entity(resultado) for resultado in resultados]
        finally:
            self._desconectar()
    
    def buscar_por_periodo(self, data_inicio: datetime, data_fim: datetime, 
                          cidade_id: Optional[int] = None) -> List[MeteorologicalData]:
        """
        Busca dados meteorológicos por período.
        
        Args:
            data_inicio: Data/hora inicial do período
            data_fim: Data/hora final do período
            cidade_id: ID da cidade (opcional)
            
        Returns:
            List[MeteorologicalData]: Lista de dados meteorológicos no período
        """
        try:
            self._conectar()
            query = 'SELECT * FROM meteorological_data WHERE data_hora BETWEEN ? AND ?'
            params = [data_inicio, data_fim]
            
            if cidade_id:
                query += ' AND cidade_id = ?'
                params.append(cidade_id)
            
            query += ' ORDER BY data_hora DESC'
            
            self.cursor.execute(query, params)
            resultados = self.cursor.fetchall()
            
            return [self._row_to_entity(resultado) for resultado in resultados]
        finally:
            self._desconectar()
    
    def buscar_com_detalhes_cidade(self, limite: Optional[int] = None) -> List[Dict]:
        """
        Busca dados meteorológicos com informações detalhadas da cidade.
        Consulta relacional que junta dados meteorológicos com dados geográficos.
        
        Args:
            limite: Número máximo de registros a retornar
            
        Returns:
            List[Dict]: Lista de dicionários com dados meteorológicos e da cidade
        """
        try:
            self._conectar()
            query = '''
            SELECT 
                md.id, md.data, md.altura_captura, md.velocidade_vento, 
                md.temperatura, md.umidade, md.created_at,
                c.nome as cidade_nome, c.latitude, c.longitude, c.altitude,
                r.nome as regiao_nome, r.sigla as regiao_sigla,
                p.nome as pais_nome, p.codigo as pais_codigo,
                mds.name as fonte_nome, mds.description as fonte_descricao
            FROM meteorological_data md
            JOIN cidades c ON md.cidade_id = c.id
            LEFT JOIN regioes r ON c.regiao_id = r.id
            LEFT JOIN paises p ON c.pais_id = p.id
            JOIN meteorological_data_source mds ON md.meteorological_data_source_id = mds.id
            ORDER BY md.data DESC
            '''
            
            if limite:
                query += f' LIMIT {limite}'
            
            self.cursor.execute(query)
            resultados = self.cursor.fetchall()
            
            colunas = [desc[0] for desc in self.cursor.description]
            return [dict(zip(colunas, resultado)) for resultado in resultados]
        finally:
            self._desconectar()
    
    def buscar_estatisticas_vento_por_cidade(self, cidade_id: int) -> Dict:
        """
        Busca estatísticas de vento para uma cidade específica.
        
        Args:
            cidade_id: ID da cidade
            
        Returns:
            Dict: Estatísticas de vento (média, máximo, mínimo, contagem)
        """
        try:
            self._conectar()
            query = '''
            SELECT 
                COUNT(*) as total_registros,
                AVG(velocidade_vento) as velocidade_media,
                MIN(velocidade_vento) as velocidade_minima,
                MAX(velocidade_vento) as velocidade_maxima,
                AVG(temperatura) as temperatura_media,
                MIN(temperatura) as temperatura_minima,
                MAX(temperatura) as temperatura_maxima
            FROM meteorological_data 
            WHERE cidade_id = ? AND velocidade_vento IS NOT NULL
            '''
            
            self.cursor.execute(query, (cidade_id,))
            resultado = self.cursor.fetchone()
            
            if resultado:
                colunas = [desc[0] for desc in self.cursor.description]
                return dict(zip(colunas, resultado))
            
            return {}
        finally:
            self._desconectar()
    
    def buscar_dados_recentes_por_regiao(self, regiao_id: int, dias: int = 30) -> List[Dict]:
        """
        Busca dados meteorológicos recentes de uma região específica.
        
        Args:
            regiao_id: ID da região
            dias: Número de dias para buscar dados recentes (padrão: 30)
            
        Returns:
            List[Dict]: Lista de dados meteorológicos com informações da cidade
        """
        try:
            self._conectar()
            query = '''
            SELECT 
                md.id, md.data, md.velocidade_vento, md.temperatura, md.umidade,
                c.nome as cidade_nome, c.latitude, c.longitude,
                mds.name as fonte_nome
            FROM meteorological_data md
            JOIN cidades c ON md.cidade_id = c.id
            JOIN meteorological_data_source mds ON md.meteorological_data_source_id = mds.id
            WHERE c.regiao_id = ? 
            AND md.data_hora >= datetime('now', '-{} days')
            ORDER BY md.data DESC, c.nome
            '''.format(dias)
            
            self.cursor.execute(query, (regiao_id,))
            resultados = self.cursor.fetchall()
            
            colunas = [desc[0] for desc in self.cursor.description]
            return [dict(zip(colunas, resultado)) for resultado in resultados]
        finally:
            self._desconectar()
    
    def atualizar(self, dados: MeteorologicalData) -> bool:
        """
        Atualiza dados meteorológicos existentes.
        
        Args:
            dados: Instância de MeteorologicalData com os dados atualizados
            
        Returns:
            bool: True se a atualização foi bem-sucedida, False caso contrário
            
        Raises:
            ValueError: Se os dados não têm ID ou não passam na validação
        """
        if not dados.id:
            raise ValueError("Dados meteorológicos devem ter um ID para serem atualizados")
        if not dados.validar():
            raise ValueError("Dados meteorológicos são inválidos")
            
        try:
            self._conectar()
            self.cursor.execute('''
            UPDATE meteorological_data
            SET meteorological_data_source_id = ?, cidade_id = ?, data_hora = ?,
                altura_captura = ?, velocidade_vento = ?, temperatura = ?, umidade = ?
            WHERE id = ?
            ''', (dados.meteorological_data_source_id, dados.cidade_id, dados.data_hora,
                  dados.altura_captura, dados.velocidade_vento, dados.temperatura,
                  dados.umidade, dados.id))
            self.conn.commit()
            
            return self.cursor.rowcount > 0
        finally:
            self._desconectar()
    
    def excluir(self, dados_id: int) -> bool:
        """
        Remove dados meteorológicos do banco de dados.
        
        Args:
            dados_id: ID dos dados a serem removidos
            
        Returns:
            bool: True se a exclusão foi bem-sucedida, False caso contrário
        """
        try:
            self._conectar()
            self.cursor.execute('DELETE FROM meteorological_data WHERE id = ?', (dados_id,))
            self.conn.commit()
            
            return self.cursor.rowcount > 0
        finally:
            self._desconectar()
    
    def excluir_por_cidade_e_periodo(self, cidade_id: int, data_inicio: datetime, data_fim: datetime) -> int:
        """
        Remove dados meteorológicos por cidade e período.
        
        Args:
            cidade_id: ID da cidade
            data_inicio: Data inicial do período
            data_fim: Data final do período
            
        Returns:
            int: Número de registros removidos
        """
        try:
            self._conectar()
            self.cursor.execute('''
            DELETE FROM meteorological_data 
            WHERE cidade_id = ? AND data_hora BETWEEN ? AND ?
            ''', (cidade_id, data_inicio, data_fim))
            self.conn.commit()
            
            return self.cursor.rowcount
        finally:
            self._desconectar()
    
    def buscar_cidades_com_dados(self) -> List[int]:
        """
        Busca todas as cidades que possuem dados meteorológicos.
        
        Returns:
            List[int]: Lista de IDs das cidades que têm dados meteorológicos
        """
        try:
            self._conectar()
            self.cursor.execute('SELECT DISTINCT cidade_id FROM meteorological_data ORDER BY cidade_id')
            resultados = self.cursor.fetchall()
            
            return [resultado[0] for resultado in resultados]
        finally:
            self._desconectar()
    
    def listar_todos(self, limite: Optional[int] = None) -> List[MeteorologicalData]:
        """
        Lista todos os dados meteorológicos cadastrados.
        
        Args:
            limite: Número máximo de registros a retornar
            
        Returns:
            List[MeteorologicalData]: Lista com todos os dados
        """
        try:
            self._conectar()
            query = 'SELECT * FROM meteorological_data ORDER BY data_hora DESC'
            
            if limite:
                query += f' LIMIT {limite}'
            
            self.cursor.execute(query)
            resultados = self.cursor.fetchall()
            
            return [self._row_to_entity(resultado) for resultado in resultados]
        finally:
            self._desconectar()
    
    def _row_to_entity(self, row: tuple) -> MeteorologicalData:
        """
        Converte uma linha do banco de dados em uma entidade MeteorologicalData.
        
        Args:
            row: Tupla com os dados da linha do banco
            
        Returns:
            MeteorologicalData: Instância da entidade MeteorologicalData
        """
        # Converter strings de data/timestamp se necessário
        data_hora_obj = None
        if row[3]:  # campo data_hora
            if isinstance(row[3], str):
                # Tentar diferentes formatos de timestamp
                try:
                    data_hora_obj = datetime.fromisoformat(row[3])
                except ValueError:
                    try:
                        data_hora_obj = datetime.strptime(row[3], '%Y-%m-%d %H:%M:%S')
                    except ValueError:
                        # Fallback para formato de data apenas
                        data_hora_obj = datetime.strptime(row[3], '%Y-%m-%d')
            else:
                data_hora_obj = row[3]
        
        created_at_obj = None
        if row[8]:  # campo created_at
            if isinstance(row[8], str):
                created_at_obj = datetime.fromisoformat(row[8])
            else:
                created_at_obj = row[8]
        
        return MeteorologicalData(
            id=row[0],
            meteorological_data_source_id=row[1],
            cidade_id=row[2],
            data_hora=data_hora_obj,
            altura_captura=row[4],
            velocidade_vento=row[5],
            temperatura=row[6],
            umidade=row[7],
            created_at=created_at_obj
        )

import sqlite3
from typing import Optional, List, Dict, Tuple
from datetime import datetime
from decimal import Decimal

from .entity import Aerogenerator


class AerogeneratorRepository:
    """
    Classe responsável pela persistência e recuperação de dados de Aerogeradores no banco de dados.
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
        """
        Cria a tabela de aerogeradores se não existir.
        Note: As tabelas de referência (manufacturers, turbine_types, etc.) devem existir.
        """
        try:
            self._conectar()
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS aerogenerators (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                model_code VARCHAR NOT NULL UNIQUE,
                manufacturer_id INTEGER NOT NULL,
                model VARCHAR NOT NULL,
                manufacture_year INTEGER,
                
                -- Power and Voltage Characteristics
                rated_power_kw DECIMAL NOT NULL,
                apparent_power_kva DECIMAL,
                power_factor DECIMAL,
                rated_voltage_kv DECIMAL NOT NULL,
                
                -- Wind Speed Characteristics
                cut_in_speed DECIMAL NOT NULL,
                cut_out_speed DECIMAL NOT NULL,
                rated_wind_speed DECIMAL,
                
                -- Rotor Characteristics
                rotor_diameter_m DECIMAL NOT NULL,
                blade_count INTEGER NOT NULL DEFAULT 3,
                rated_rotor_speed_rpm DECIMAL,
                
                -- Control and Operation
                variable_speed BOOLEAN NOT NULL DEFAULT 1,
                pitch_control BOOLEAN NOT NULL DEFAULT 1,
                pitch_min_deg DECIMAL,
                pitch_max_deg DECIMAL,
                
                -- Relationships
                turbine_type_id INTEGER NOT NULL,
                generator_type_id INTEGER NOT NULL,
                control_type_id INTEGER NOT NULL,
                
                -- Metadata
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_by VARCHAR DEFAULT 'andrevn',
                
                FOREIGN KEY (manufacturer_id) REFERENCES manufacturers (id),
                FOREIGN KEY (turbine_type_id) REFERENCES turbine_types (id),
                FOREIGN KEY (generator_type_id) REFERENCES generator_types (id),
                FOREIGN KEY (control_type_id) REFERENCES control_types (id)
            )
            ''')
            self.conn.commit()
        finally:
            self._desconectar()
    
    def salvar(self, aerogenerator: Aerogenerator) -> int:
        """
        Salva um aerogerador no banco de dados.
        
        Args:
            aerogenerator: Instância do aerogerador a ser salvo
            
        Returns:
            int: ID do aerogerador salvo
            
        Raises:
            ValueError: Se já existir um aerogerador com o mesmo código de modelo
        """
        try:
            self._conectar()
            
            # Verificar se já existe um aerogerador com o mesmo código de modelo
            self.cursor.execute('SELECT COUNT(*) FROM aerogenerators WHERE model_code = ?', (aerogenerator.model_code,))
            if self.cursor.fetchone()[0] > 0:
                raise ValueError(f"Já existe um aerogerador com o código '{aerogenerator.model_code}'")
            
            # Definir timestamps
            agora = datetime.now()
            if not aerogenerator.created_at:
                aerogenerator.created_at = agora
            aerogenerator.updated_at = agora
            if not aerogenerator.created_by:
                aerogenerator.created_by = 'andrevn'
            
            self.cursor.execute('''
            INSERT INTO aerogenerators (
                model_code, manufacturer_id, model, manufacture_year,
                rated_power_kw, apparent_power_kva, power_factor, rated_voltage_kv,
                cut_in_speed, cut_out_speed, rated_wind_speed,
                rotor_diameter_m, blade_count, rated_rotor_speed_rpm,
                variable_speed, pitch_control, pitch_min_deg, pitch_max_deg,
                turbine_type_id, generator_type_id, control_type_id,
                created_at, updated_at, created_by
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                aerogenerator.model_code, aerogenerator.manufacturer_id, aerogenerator.model,
                aerogenerator.manufacture_year, float(aerogenerator.rated_power_kw),
                float(aerogenerator.apparent_power_kva) if aerogenerator.apparent_power_kva else None,
                float(aerogenerator.power_factor) if aerogenerator.power_factor else None,
                float(aerogenerator.rated_voltage_kv), float(aerogenerator.cut_in_speed),
                float(aerogenerator.cut_out_speed),
                float(aerogenerator.rated_wind_speed) if aerogenerator.rated_wind_speed else None,
                float(aerogenerator.rotor_diameter_m), aerogenerator.blade_count,
                float(aerogenerator.rated_rotor_speed_rpm) if aerogenerator.rated_rotor_speed_rpm else None,
                aerogenerator.variable_speed, aerogenerator.pitch_control,
                float(aerogenerator.pitch_min_deg) if aerogenerator.pitch_min_deg else None,
                float(aerogenerator.pitch_max_deg) if aerogenerator.pitch_max_deg else None,
                aerogenerator.turbine_type_id, aerogenerator.generator_type_id,
                aerogenerator.control_type_id, aerogenerator.created_at,
                aerogenerator.updated_at, aerogenerator.created_by
            ))
            
            self.conn.commit()
            aerogenerator_id = self.cursor.lastrowid
            aerogenerator.id = aerogenerator_id  # Atualiza o ID da instância
            return aerogenerator_id
        finally:
            self._desconectar()
    
    def buscar_por_id(self, aerogenerator_id: int) -> Optional[Aerogenerator]:
        """
        Busca um aerogerador pelo ID.
        
        Args:
            aerogenerator_id: ID do aerogerador
            
        Returns:
            Optional[Aerogenerator]: Aerogerador encontrado ou None
        """
        try:
            self._conectar()
            self.cursor.execute('SELECT * FROM aerogenerators WHERE id = ?', (aerogenerator_id,))
            resultado = self.cursor.fetchone()
            
            if resultado:
                return self._row_to_entity(resultado)
            return None
        finally:
            self._desconectar()
    
    def buscar_por_model_code(self, model_code: str) -> Optional[Aerogenerator]:
        """
        Busca um aerogerador pelo código do modelo.
        
        Args:
            model_code: Código do modelo
            
        Returns:
            Optional[Aerogenerator]: Aerogerador encontrado ou None
        """
        try:
            self._conectar()
            self.cursor.execute('SELECT * FROM aerogenerators WHERE model_code = ?', (model_code,))
            resultado = self.cursor.fetchone()
            
            if resultado:
                return self._row_to_entity(resultado)
            return None
        finally:
            self._desconectar()
    
    def buscar_por_fabricante(self, manufacturer_id: int) -> List[Aerogenerator]:
        """
        Busca aerogeradores de um fabricante específico.
        
        Args:
            manufacturer_id: ID do fabricante
            
        Returns:
            List[Aerogenerator]: Lista de aerogeradores do fabricante
        """
        try:
            self._conectar()
            self.cursor.execute('''
            SELECT * FROM aerogenerators 
            WHERE manufacturer_id = ? 
            ORDER BY model
            ''', (manufacturer_id,))
            resultados = self.cursor.fetchall()
            
            return [self._row_to_entity(resultado) for resultado in resultados]
        finally:
            self._desconectar()
    
    def buscar_por_faixa_potencia(self, potencia_min: Decimal, potencia_max: Decimal) -> List[Aerogenerator]:
        """
        Busca aerogeradores por faixa de potência.
        
        Args:
            potencia_min: Potência mínima em kW
            potencia_max: Potência máxima em kW
            
        Returns:
            List[Aerogenerator]: Lista de aerogeradores na faixa de potência
        """
        try:
            self._conectar()
            self.cursor.execute('''
            SELECT * FROM aerogenerators 
            WHERE rated_power_kw BETWEEN ? AND ?
            ORDER BY rated_power_kw
            ''', (float(potencia_min), float(potencia_max)))
            resultados = self.cursor.fetchall()
            
            return [self._row_to_entity(resultado) for resultado in resultados]
        finally:
            self._desconectar()
    
    def buscar_por_diametro_rotor(self, diametro_min: Decimal, diametro_max: Decimal) -> List[Aerogenerator]:
        """
        Busca aerogeradores por faixa de diâmetro do rotor.
        
        Args:
            diametro_min: Diâmetro mínimo em metros
            diametro_max: Diâmetro máximo em metros
            
        Returns:
            List[Aerogenerator]: Lista de aerogeradores na faixa de diâmetro
        """
        try:
            self._conectar()
            self.cursor.execute('''
            SELECT * FROM aerogenerators 
            WHERE rotor_diameter_m BETWEEN ? AND ?
            ORDER BY rotor_diameter_m
            ''', (float(diametro_min), float(diametro_max)))
            resultados = self.cursor.fetchall()
            
            return [self._row_to_entity(resultado) for resultado in resultados]
        finally:
            self._desconectar()
    
    def buscar_com_detalhes_completos(self, limite: Optional[int] = None) -> List[Dict]:
        """
        Busca aerogeradores com detalhes completos incluindo informações dos relacionamentos.
        
        Args:
            limite: Limite de resultados
            
        Returns:
            List[Dict]: Lista de dicionários com informações completas
        """
        try:
            self._conectar()
            query = '''
            SELECT 
                a.*,
                m.name as manufacturer_name,
                m.country as manufacturer_country,
                tt.type as turbine_type,
                gt.type as generator_type,
                ct.type as control_type
            FROM aerogenerators a
            LEFT JOIN manufacturers m ON a.manufacturer_id = m.id
            LEFT JOIN turbine_types tt ON a.turbine_type_id = tt.id
            LEFT JOIN generator_types gt ON a.generator_type_id = gt.id
            LEFT JOIN control_types ct ON a.control_type_id = ct.id
            ORDER BY a.model
            '''
            
            if limite:
                query += f' LIMIT {limite}'
            
            self.cursor.execute(query)
            resultados = self.cursor.fetchall()
            
            colunas = [desc[0] for desc in self.cursor.description]
            return [dict(zip(colunas, resultado)) for resultado in resultados]
        finally:
            self._desconectar()
    
    def buscar_estatisticas_por_fabricante(self) -> List[Dict]:
        """
        Busca estatísticas de aerogeradores agrupadas por fabricante.
        
        Returns:
            List[Dict]: Lista com estatísticas por fabricante
        """
        try:
            self._conectar()
            self.cursor.execute('''
            SELECT 
                m.name as manufacturer_name,
                COUNT(a.id) as total_models,
                AVG(a.rated_power_kw) as avg_power_kw,
                MIN(a.rated_power_kw) as min_power_kw,
                MAX(a.rated_power_kw) as max_power_kw,
                AVG(a.rotor_diameter_m) as avg_diameter_m,
                MIN(a.rotor_diameter_m) as min_diameter_m,
                MAX(a.rotor_diameter_m) as max_diameter_m
            FROM aerogenerators a
            JOIN manufacturers m ON a.manufacturer_id = m.id
            GROUP BY m.id, m.name
            ORDER BY total_models DESC
            ''')
            resultados = self.cursor.fetchall()
            
            colunas = [desc[0] for desc in self.cursor.description]
            return [dict(zip(colunas, resultado)) for resultado in resultados]
        finally:
            self._desconectar()
    
    def listar_todos(self) -> List[Aerogenerator]:
        """
        Lista todos os aerogeradores ordenados por modelo.
        
        Returns:
            List[Aerogenerator]: Lista de todos os aerogeradores
        """
        try:
            self._conectar()
            self.cursor.execute('SELECT * FROM aerogenerators ORDER BY model')
            resultados = self.cursor.fetchall()
            
            return [self._row_to_entity(resultado) for resultado in resultados]
        finally:
            self._desconectar()
    
    def atualizar(self, aerogenerator: Aerogenerator) -> bool:
        """
        Atualiza um aerogerador existente.
        
        Args:
            aerogenerator: Aerogerador com dados atualizados
            
        Returns:
            bool: True se atualizou com sucesso, False caso contrário
            
        Raises:
            ValueError: Se já existir outro aerogerador com o mesmo código de modelo
        """
        try:
            self._conectar()
            
            # Verificar se já existe outro aerogerador com o mesmo código de modelo
            self.cursor.execute(
                'SELECT COUNT(*) FROM aerogenerators WHERE model_code = ? AND id != ?',
                (aerogenerator.model_code, aerogenerator.id)
            )
            if self.cursor.fetchone()[0] > 0:
                raise ValueError(f"Já existe outro aerogerador com o código '{aerogenerator.model_code}'")
            
            # Atualizar timestamp
            aerogenerator.updated_at = datetime.now()
            
            self.cursor.execute('''
            UPDATE aerogenerators SET
                model_code = ?, manufacturer_id = ?, model = ?, manufacture_year = ?,
                rated_power_kw = ?, apparent_power_kva = ?, power_factor = ?, rated_voltage_kv = ?,
                cut_in_speed = ?, cut_out_speed = ?, rated_wind_speed = ?,
                rotor_diameter_m = ?, blade_count = ?, rated_rotor_speed_rpm = ?,
                variable_speed = ?, pitch_control = ?, pitch_min_deg = ?, pitch_max_deg = ?,
                turbine_type_id = ?, generator_type_id = ?, control_type_id = ?,
                updated_at = ?
            WHERE id = ?
            ''', (
                aerogenerator.model_code, aerogenerator.manufacturer_id, aerogenerator.model,
                aerogenerator.manufacture_year, float(aerogenerator.rated_power_kw),
                float(aerogenerator.apparent_power_kva) if aerogenerator.apparent_power_kva else None,
                float(aerogenerator.power_factor) if aerogenerator.power_factor else None,
                float(aerogenerator.rated_voltage_kv), float(aerogenerator.cut_in_speed),
                float(aerogenerator.cut_out_speed),
                float(aerogenerator.rated_wind_speed) if aerogenerator.rated_wind_speed else None,
                float(aerogenerator.rotor_diameter_m), aerogenerator.blade_count,
                float(aerogenerator.rated_rotor_speed_rpm) if aerogenerator.rated_rotor_speed_rpm else None,
                aerogenerator.variable_speed, aerogenerator.pitch_control,
                float(aerogenerator.pitch_min_deg) if aerogenerator.pitch_min_deg else None,
                float(aerogenerator.pitch_max_deg) if aerogenerator.pitch_max_deg else None,
                aerogenerator.turbine_type_id, aerogenerator.generator_type_id,
                aerogenerator.control_type_id, aerogenerator.updated_at, aerogenerator.id
            ))
            
            self.conn.commit()
            
            return self.cursor.rowcount > 0
        finally:
            self._desconectar()
    
    def excluir(self, aerogenerator_id: int) -> bool:
        """
        Exclui um aerogerador pelo ID.
        
        Args:
            aerogenerator_id: ID do aerogerador a ser excluído
            
        Returns:
            bool: True se excluiu com sucesso, False caso contrário
        """
        try:
            self._conectar()
            self.cursor.execute('DELETE FROM aerogenerators WHERE id = ?', (aerogenerator_id,))
            self.conn.commit()
            
            return self.cursor.rowcount > 0
        finally:
            self._desconectar()
    
    def existe_model_code(self, model_code: str, excluir_id: Optional[int] = None) -> bool:
        """
        Verifica se já existe um aerogerador com o código de modelo especificado.
        
        Args:
            model_code: Código do modelo
            excluir_id: ID a ser excluído da verificação (para updates)
            
        Returns:
            bool: True se existe, False caso contrário
        """
        try:
            self._conectar()
            if excluir_id:
                self.cursor.execute(
                    'SELECT COUNT(*) FROM aerogenerators WHERE model_code = ? AND id != ?',
                    (model_code, excluir_id)
                )
            else:
                self.cursor.execute('SELECT COUNT(*) FROM aerogenerators WHERE model_code = ?', (model_code,))
            
            count = self.cursor.fetchone()[0]
            return count > 0
        finally:
            self._desconectar()
    
    def contar_total(self) -> int:
        """
        Conta o total de aerogeradores cadastrados.
        
        Returns:
            int: Número total de aerogeradores
        """
        try:
            self._conectar()
            self.cursor.execute('SELECT COUNT(*) FROM aerogenerators')
            return self.cursor.fetchone()[0]
        finally:
            self._desconectar()
    
    def _row_to_entity(self, row: tuple) -> Aerogenerator:
        """
        Converte uma linha do banco de dados em uma entidade Aerogenerator.
        
        Args:
            row: Tupla com os dados da linha do banco
            
        Returns:
            Aerogenerator: Instância da entidade Aerogenerator
        """
        # Converter valores para Decimal quando necessário
        def to_decimal(value):
            return Decimal(str(value)) if value is not None else None
        
        # Converter strings de datetime se necessário
        created_at_obj = None
        if row[22]:  # campo created_at
            if isinstance(row[22], str):
                try:
                    created_at_obj = datetime.fromisoformat(row[22])
                except ValueError:
                    try:
                        created_at_obj = datetime.strptime(row[22], '%Y-%m-%d %H:%M:%S')
                    except ValueError:
                        created_at_obj = datetime.strptime(row[22], '%Y-%m-%d')
            else:
                created_at_obj = row[22]
        
        updated_at_obj = None
        if row[23]:  # campo updated_at
            if isinstance(row[23], str):
                try:
                    updated_at_obj = datetime.fromisoformat(row[23])
                except ValueError:
                    try:
                        updated_at_obj = datetime.strptime(row[23], '%Y-%m-%d %H:%M:%S')
                    except ValueError:
                        updated_at_obj = datetime.strptime(row[23], '%Y-%m-%d')
            else:
                updated_at_obj = row[23]
        
        return Aerogenerator(
            id=row[0],
            model_code=row[1],
            manufacturer_id=row[2],
            model=row[3],
            manufacture_year=row[4],
            rated_power_kw=to_decimal(row[5]),
            apparent_power_kva=to_decimal(row[6]),
            power_factor=to_decimal(row[7]),
            rated_voltage_kv=to_decimal(row[8]),
            cut_in_speed=to_decimal(row[9]),
            cut_out_speed=to_decimal(row[10]),
            rated_wind_speed=to_decimal(row[11]),
            rotor_diameter_m=to_decimal(row[12]),
            blade_count=row[13],
            rated_rotor_speed_rpm=to_decimal(row[14]),
            variable_speed=bool(row[15]),
            pitch_control=bool(row[16]),
            pitch_min_deg=to_decimal(row[17]),
            pitch_max_deg=to_decimal(row[18]),
            turbine_type_id=row[19],
            generator_type_id=row[20],
            control_type_id=row[21],
            created_at=created_at_obj,
            updated_at=updated_at_obj,
            created_by=row[24] if len(row) > 24 else None
        )

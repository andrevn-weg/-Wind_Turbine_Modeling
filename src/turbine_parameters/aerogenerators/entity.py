from dataclasses import dataclass
from typing import Optional, Dict, Any
from datetime import datetime
from decimal import Decimal


@dataclass
class Aerogenerator:
    """
    Entidade de domínio para representar um aerogerador completo.
    
    Esta classe representa apenas o objeto de negócio, sem responsabilidades de persistência.
    
    Attributes:
        id (Optional[int]): Identificador único do aerogerador no banco de dados
        model_code (str): Código único do modelo
        manufacturer_id (int): Referência ao fabricante (chave estrangeira)
        model (str): Nome/modelo do aerogerador
        manufacture_year (Optional[int]): Ano de fabricação
        
        # Características de Potência e Tensão
        rated_power_kw (Decimal): Potência nominal (kW)
        apparent_power_kva (Optional[Decimal]): Potência Aparente S (kVA)
        power_factor (Optional[Decimal]): Fator de Potência
        rated_voltage_kv (Decimal): Tensão nominal (kV)
        
        # Características de Velocidade do Vento
        cut_in_speed (Decimal): Velocidade cut-in (m/s)
        cut_out_speed (Decimal): Velocidade cut-out (m/s)
        rated_wind_speed (Optional[Decimal]): Velocidade nominal do vento (m/s)
        
        # Características do Rotor
        rotor_diameter_m (Decimal): Diâmetro do rotor (m)
        blade_count (int): Número de pás
        rated_rotor_speed_rpm (Optional[Decimal]): Velocidade nominal (RPM)
        
        # Controle e Operação
        variable_speed (bool): Se possui velocidade variável
        pitch_control (bool): Se possui controle de pitch
        pitch_min_deg (Optional[Decimal]): Ângulo mínimo de pitch
        pitch_max_deg (Optional[Decimal]): Ângulo máximo de pitch
        
        # Relacionamentos
        turbine_type_id (int): Referência ao tipo de turbina (chave estrangeira)
        generator_type_id (int): Referência ao tipo de gerador (chave estrangeira)
        control_type_id (int): Referência ao tipo de controle (chave estrangeira)
        
        # Metadados
        created_at (Optional[datetime]): Data de criação do registro
        updated_at (Optional[datetime]): Data da última atualização do registro
        created_by (Optional[str]): Usuário que criou o registro
    """
    id: Optional[int] = None
    model_code: str = ""
    manufacturer_id: int = 0
    model: str = ""
    manufacture_year: Optional[int] = None
    
    # Características de Potência e Tensão
    rated_power_kw: Decimal = Decimal('0')
    apparent_power_kva: Optional[Decimal] = None
    power_factor: Optional[Decimal] = None
    rated_voltage_kv: Decimal = Decimal('0')
    
    # Características de Velocidade do Vento
    cut_in_speed: Decimal = Decimal('0')
    cut_out_speed: Decimal = Decimal('0')
    rated_wind_speed: Optional[Decimal] = None
    
    # Características do Rotor
    rotor_diameter_m: Decimal = Decimal('0')
    blade_count: int = 3
    rated_rotor_speed_rpm: Optional[Decimal] = None
    
    # Controle e Operação
    variable_speed: bool = True
    pitch_control: bool = True
    pitch_min_deg: Optional[Decimal] = None
    pitch_max_deg: Optional[Decimal] = None
    
    # Relacionamentos
    turbine_type_id: int = 0
    generator_type_id: int = 0
    control_type_id: int = 0
    
    # Metadados
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    created_by: Optional[str] = None

    def __post_init__(self):
        """Validações após a inicialização do objeto"""
        self._validar()
    
    def _validar(self) -> None:
        """
        Valida os dados da entidade Aerogenerator.
        
        Raises:
            ValueError: Se algum campo obrigatório estiver vazio ou inválido
        """
        # Validações de campos obrigatórios
        if not self.model_code or not self.model_code.strip():
            raise ValueError("Código do modelo é obrigatório")
        
        if not self.model or not self.model.strip():
            raise ValueError("Nome do modelo é obrigatório")
        
        if self.manufacturer_id <= 0:
            raise ValueError("ID do fabricante é obrigatório e deve ser positivo")
        
        if self.turbine_type_id <= 0:
            raise ValueError("ID do tipo de turbina é obrigatório e deve ser positivo")
        
        if self.generator_type_id <= 0:
            raise ValueError("ID do tipo de gerador é obrigatório e deve ser positivo")
        
        if self.control_type_id <= 0:
            raise ValueError("ID do tipo de controle é obrigatório e deve ser positivo")
        
        # Validações de tamanho de campos
        if len(self.model_code.strip()) > 100:
            raise ValueError("Código do modelo não pode exceder 100 caracteres")
        
        if len(self.model.strip()) > 255:
            raise ValueError("Nome do modelo não pode exceder 255 caracteres")
        
        # Validações de valores numéricos
        if self.rated_power_kw <= 0:
            raise ValueError("Potência nominal deve ser maior que zero")
        
        if self.rated_voltage_kv <= 0:
            raise ValueError("Tensão nominal deve ser maior que zero")
        
        if self.cut_in_speed <= 0:
            raise ValueError("Velocidade cut-in deve ser maior que zero")
        
        if self.cut_out_speed <= 0:
            raise ValueError("Velocidade cut-out deve ser maior que zero")
        
        if self.cut_in_speed >= self.cut_out_speed:
            raise ValueError("Velocidade cut-in deve ser menor que cut-out")
        
        if self.rotor_diameter_m <= 0:
            raise ValueError("Diâmetro do rotor deve ser maior que zero")
        
        if self.blade_count <= 0:
            raise ValueError("Número de pás deve ser maior que zero")
        
        # Validações opcionais
        if self.manufacture_year and (self.manufacture_year < 1980 or self.manufacture_year > 2050):
            raise ValueError("Ano de fabricação deve estar entre 1980 e 2050")
        
        if self.apparent_power_kva and self.apparent_power_kva <= 0:
            raise ValueError("Potência aparente deve ser maior que zero")
        
        if self.power_factor and (self.power_factor <= 0 or self.power_factor > 1):
            raise ValueError("Fator de potência deve estar entre 0 e 1")
        
        if self.rated_wind_speed and self.rated_wind_speed <= 0:
            raise ValueError("Velocidade nominal do vento deve ser maior que zero")
        
        if self.rated_rotor_speed_rpm and self.rated_rotor_speed_rpm <= 0:
            raise ValueError("Velocidade nominal do rotor deve ser maior que zero")
        
        if self.pitch_min_deg is not None and (self.pitch_min_deg < -90 or self.pitch_min_deg > 90):
            raise ValueError("Ângulo mínimo de pitch deve estar entre -90 e 90 graus")
        
        if self.pitch_max_deg is not None and (self.pitch_max_deg < -90 or self.pitch_max_deg > 90):
            raise ValueError("Ângulo máximo de pitch deve estar entre -90 e 90 graus")
        
        if (self.pitch_min_deg is not None and self.pitch_max_deg is not None and 
            self.pitch_min_deg >= self.pitch_max_deg):
            raise ValueError("Ângulo mínimo de pitch deve ser menor que o máximo")
        
        # Normalizar campos
        self.model_code = self.model_code.strip()
        self.model = self.model.strip()
        if self.created_by:
            self.created_by = self.created_by.strip()
    
    def get_swept_area(self) -> Decimal:
        """
        Calcula a área varrida pelo rotor em m².
        
        Returns:
            Decimal: Área varrida em metros quadrados
        """
        import math
        radius = self.rotor_diameter_m / 2
        return Decimal(str(math.pi)) * radius * radius
    
    def get_tip_speed_ratio(self, wind_speed: Decimal) -> Optional[Decimal]:
        """
        Calcula a razão de velocidade da ponta (TSR) para uma velocidade de vento.
        
        Args:
            wind_speed: Velocidade do vento em m/s
            
        Returns:
            Optional[Decimal]: TSR ou None se não houver velocidade nominal do rotor
        """
        if not self.rated_rotor_speed_rpm or wind_speed <= 0:
            return None
        
        # Converter RPM para rad/s
        omega = (self.rated_rotor_speed_rpm * Decimal('2') * Decimal(str(3.14159))) / Decimal('60')
        # Calcular velocidade da ponta
        tip_speed = omega * (self.rotor_diameter_m / 2)
        return tip_speed / wind_speed
    
    def get_power_density(self) -> Decimal:
        """
        Calcula a densidade de potência (kW/m²).
        
        Returns:
            Decimal: Densidade de potência em kW por metro quadrado
        """
        return self.rated_power_kw / self.get_swept_area()
    
    def is_in_operational_range(self, wind_speed: Decimal) -> bool:
        """
        Verifica se uma velocidade de vento está na faixa operacional.
        
        Args:
            wind_speed: Velocidade do vento em m/s
            
        Returns:
            bool: True se estiver na faixa operacional
        """
        return self.cut_in_speed <= wind_speed <= self.cut_out_speed
    
    def has_pitch_control_capability(self) -> bool:
        """
        Verifica se o aerogerador tem capacidade de controle de pitch.
        
        Returns:
            bool: True se tem controle de pitch
        """
        return self.pitch_control and (self.pitch_min_deg is not None or self.pitch_max_deg is not None)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Converte a entidade para um dicionário.
        
        Returns:
            Dict[str, Any]: Representação da entidade em formato de dicionário
        """
        return {
            'id': self.id,
            'model_code': self.model_code,
            'manufacturer_id': self.manufacturer_id,
            'model': self.model,
            'manufacture_year': self.manufacture_year,
            'rated_power_kw': float(self.rated_power_kw),
            'apparent_power_kva': float(self.apparent_power_kva) if self.apparent_power_kva else None,
            'power_factor': float(self.power_factor) if self.power_factor else None,
            'rated_voltage_kv': float(self.rated_voltage_kv),
            'cut_in_speed': float(self.cut_in_speed),
            'cut_out_speed': float(self.cut_out_speed),
            'rated_wind_speed': float(self.rated_wind_speed) if self.rated_wind_speed else None,
            'rotor_diameter_m': float(self.rotor_diameter_m),
            'blade_count': self.blade_count,
            'rated_rotor_speed_rpm': float(self.rated_rotor_speed_rpm) if self.rated_rotor_speed_rpm else None,
            'variable_speed': self.variable_speed,
            'pitch_control': self.pitch_control,
            'pitch_min_deg': float(self.pitch_min_deg) if self.pitch_min_deg else None,
            'pitch_max_deg': float(self.pitch_max_deg) if self.pitch_max_deg else None,
            'turbine_type_id': self.turbine_type_id,
            'generator_type_id': self.generator_type_id,
            'control_type_id': self.control_type_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'created_by': self.created_by
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Aerogenerator':
        """
        Cria uma instância da entidade a partir de um dicionário.
        
        Args:
            data: Dicionário com os dados da entidade
            
        Returns:
            Aerogenerator: Nova instância da entidade
        """
        # Converter valores para Decimal quando necessário
        def to_decimal(value):
            return Decimal(str(value)) if value is not None else None
        
        # Converter strings de datetime se necessário
        created_at = None
        if data.get('created_at'):
            if isinstance(data['created_at'], str):
                created_at = datetime.fromisoformat(data['created_at'])
            else:
                created_at = data['created_at']
        
        updated_at = None
        if data.get('updated_at'):
            if isinstance(data['updated_at'], str):
                updated_at = datetime.fromisoformat(data['updated_at'])
            else:
                updated_at = data['updated_at']
        
        return cls(
            id=data.get('id'),
            model_code=data.get('model_code', ''),
            manufacturer_id=data.get('manufacturer_id', 0),
            model=data.get('model', ''),
            manufacture_year=data.get('manufacture_year'),
            rated_power_kw=to_decimal(data.get('rated_power_kw', 0)),
            apparent_power_kva=to_decimal(data.get('apparent_power_kva')),
            power_factor=to_decimal(data.get('power_factor')),
            rated_voltage_kv=to_decimal(data.get('rated_voltage_kv', 0)),
            cut_in_speed=to_decimal(data.get('cut_in_speed', 0)),
            cut_out_speed=to_decimal(data.get('cut_out_speed', 0)),
            rated_wind_speed=to_decimal(data.get('rated_wind_speed')),
            rotor_diameter_m=to_decimal(data.get('rotor_diameter_m', 0)),
            blade_count=data.get('blade_count', 3),
            rated_rotor_speed_rpm=to_decimal(data.get('rated_rotor_speed_rpm')),
            variable_speed=data.get('variable_speed', True),
            pitch_control=data.get('pitch_control', True),
            pitch_min_deg=to_decimal(data.get('pitch_min_deg')),
            pitch_max_deg=to_decimal(data.get('pitch_max_deg')),
            turbine_type_id=data.get('turbine_type_id', 0),
            generator_type_id=data.get('generator_type_id', 0),
            control_type_id=data.get('control_type_id', 0),
            created_at=created_at,
            updated_at=updated_at,
            created_by=data.get('created_by')
        )
    
    def __str__(self) -> str:
        """Representação textual da entidade"""
        return f"Aerogenerator(id={self.id}, model_code='{self.model_code}', model='{self.model}')"
    
    def __repr__(self) -> str:
        """Representação detalhada da entidade"""
        return (f"Aerogenerator(id={self.id}, model_code='{self.model_code}', "
                f"model='{self.model}', rated_power_kw={self.rated_power_kw})")

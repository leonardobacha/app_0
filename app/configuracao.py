from pydantic import Field #BaseSettings, 
from pydantic_settings import BaseSettings
import logging
from logging.handlers import RotatingFileHandler
from seguranca import gerar_api_key_hash
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

# Configuração avançada do Logger
logger = logging.getLogger(__name__)

# Definindo o nível do logger
logger.setLevel(logging.INFO)  # Pode ser DEBUG, INFO, WARNING, ERROR, CRITICAL

# Formatando a saída do log
formatter = logging.Formatter(
    "%(asctime)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
)

# Console Handler para exibir os logs no console
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)

# File Handler para salvar os logs em um arquivo com rotação
file_handler = RotatingFileHandler(
    "logs/api_logs.log", maxBytes=10 * 1024 * 1024, backupCount=3
)  # Max 10MB por arquivo, mantendo até 3 backups
file_handler.setFormatter(formatter)

# Adicionando handlers ao logger
logger.addHandler(console_handler)
logger.addHandler(file_handler)

# Exemplo de log
logger.info("Logger configurado com sucesso!")


class Configuracoes(BaseSettings):
    CONEXAO: str = Field(..., env="CONEXAO")
    CHAVE_SECRETA: str = Field(..., env="CHAVE_SECRETA")
    ALGORITMO: str = Field(..., env="ALGORITMO")
    TEMPO_DE_EXPIRACAO_TOKEN_DE_ACESSO: int = Field(
        ..., env="TEMPO_DE_EXPIRACAO_TOKEN_DE_ACESSO"
    )
    CHAVE_API: str = Field(..., env="CHAVE_API")


configuracoes = Configuracoes()

API_KEY_HASH = gerar_api_key_hash(configuracoes.CHAVE_API)

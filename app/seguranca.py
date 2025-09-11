from passlib.context import CryptContext

contexto_senha = CryptContext(schemes=["bcrypt"], deprecated="auto")


def gerar_senha_hash(senha: str) -> str:
    """
    Gera o hash da senha de usuário.
    """
    return contexto_senha.hash(senha)


def verificar_senha(senha_digitada: str, senha_hash: str) -> bool:
    """
    Verifica se a senha fornecida corresponde ao hash da senha armazenada.
    """
    return contexto_senha.verify(senha_digitada, senha_hash)


def gerar_api_key_hash(api_key: str) -> str:
    """
    Gera o hash da chave API.
    """
    return contexto_senha.hash(api_key)


def verificar_api_key(api_key_digitada: str, api_key_hash: str) -> bool:
    """
    Verifica se a chave API fornecida corresponde ao hash da chave armazenada.
    """
    return contexto_senha.verify(api_key_digitada, api_key_hash)

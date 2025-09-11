from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
import models
import autenticacao
from database import get_db
from configuracao import logger

oauth2_esquema = OAuth2PasswordBearer(tokenUrl="/autenticacao/login")


def obter_usuario_atual(
    token: str = Depends(oauth2_esquema), db: Session = Depends(get_db)
):
    # Verificar o token
    dados_token = autenticacao.verificar_token(token)

    if not dados_token:
        logger.error("Token inválido fornecido")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido"
        )

    # Buscar o usuário no banco de dados
    usuario = (
        db.query(models.Usuario)
        .filter(models.Usuario.email == dados_token["sub"])
        .first()
    )

    if not usuario:
        logger.error(f"Usuário com email {dados_token['sub']} não encontrado")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuário não encontrado"
        )

    # Caso o usuário seja encontrado, retornamos ele
    logger.info(f"Usuário {usuario.nome} autenticado com sucesso")
    return usuario

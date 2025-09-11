from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
import repositorio
import schemas
from sqlalchemy.orm import Session
from database import get_db
import autenticacao
from configuracao import logger

router = APIRouter(prefix="/autenticacao", tags=["Autenticação"])


# ------------------ Rota de Login e Geração de Token ------------------


@router.post("/login", response_model=schemas.Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    """
    Realiza a autenticação do usuário e gera um token JWT válido.
    """
    try:
        # Verifica as credenciais fornecidas
        usuario = repositorio.autenticar_usuario(
            db, form_data.username, form_data.password
        )

        if not usuario:
            # Logando falha de autenticação
            logger.warning(
                f"Tentativa de login falhou para o usuário: {form_data.username}"
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciais inválidas"
            )

        # Gerando o token de acesso
        token_acesso = autenticacao.criar_token_acesso(dados={"sub": usuario.email})

        # Logando o sucesso de login
        logger.info(f"Usuário autenticado com sucesso: {usuario.email}")

        # Retorna o token gerado
        return schemas.Token(access_token=token_acesso, token_type="bearer")

    except Exception as e:
        # Logando erro inesperado
        logger.error(f"Erro ao processar login: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro no servidor"
        )

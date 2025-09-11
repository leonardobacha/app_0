import traceback
from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
import schemas, repositorio
from database import get_db
from sqlalchemy.orm import Session
from oath2 import obter_usuario_atual
import models
from configuracao import logger
from typing import List
from configuracao import limiter

router = APIRouter(prefix="/usuarios", tags=["Usuários"])

# ------------------ Rota de Criação de Usuário ------------------


@router.post(
    "/", response_model=schemas.UsuarioResposta, status_code=status.HTTP_201_CREATED
)
def criar_usuario(
    usuario: schemas.UsuarioCriacao, db: Session = Depends(get_db)
):
    try:
        novo_usuario = repositorio.criar_usuario(db, usuario)
        logger.info(
            f"Usuário criado com sucesso: {novo_usuario.nome} (ID: {novo_usuario.id})"
        )
        return novo_usuario
    except Exception as e:
        traceback.print_exc()
        logger.error(f"Erro ao criar usuário: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


# ------------------ Rota para Obter os Dados do Usuário Atual ------------------
@router.get("/meus_dados", response_model=schemas.UsuarioRespostaComLinks)
@limiter.limit("10/minute")  # Aplica o rate limit
def meus_dados(
    request: Request, usuario_atual: models.Usuario = Depends(obter_usuario_atual)
):  # <-- Adiciona request
    logger.info(
        f"Usuário acessou seus dados: {usuario_atual.nome} (ID: {usuario_atual.id})"
    )
    return schemas.UsuarioRespostaComLinks(
        id=usuario_atual.id,
        nome=usuario_atual.nome,
        email=usuario_atual.email,
        links=[
            {"rel": "self", "href": "/usuarios/meus_dados", "method": "GET"},
            {
                "rel": "pedidos",
                "href": f"/usuarios/{usuario_atual.id}/pedidos",
                "method": "GET",
            },
        ],
    )


# ------------------ Rota de Atualização Completa de Usuário ------------------


@router.put("/{usuario_id}", response_model=schemas.UsuarioResposta)
def atualizar_usuario(
    usuario_id: int,
    usuario: schemas.UsuarioAtualizacao,
    db: Session = Depends(get_db),
):
    try:
        usuario_atualizado = repositorio.atualizar_usuario(db, usuario_id, usuario)
        logger.info(
            f"Usuário atualizado com sucesso: {usuario_atualizado.nome} (ID: {usuario_atualizado.id})"
        )
        return usuario_atualizado
    except Exception as e:
        traceback.print_exc()
        logger.error(f"Erro ao atualizar usuário {usuario_id}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


# ------------------ Rota de Atualização Parcial de Usuário (PATCH) ------------------


@router.patch("/{usuario_id}", response_model=schemas.UsuarioResposta)
def atualizar_usuario_parcial(
    usuario_id: int,
    usuario: schemas.UsuarioAtualizacao,
    db: Session = Depends(get_db),
):
    try:
        usuario_atualizado = repositorio.atualizar_usuario(db, usuario_id, usuario)
        logger.info(
            f"Usuário atualizado parcialmente: {usuario_atualizado.nome} (ID: {usuario_atualizado.id})"
        )
        return usuario_atualizado
    except Exception as e:
        traceback.print_exc()
        logger.error(f"Erro ao atualizar parcialmente o usuário {usuario_id}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


# ------------------ Rota para Deletar um Usuário ------------------


@router.delete("/{usuario_id}", status_code=status.HTTP_204_NO_CONTENT)
def deletar_usuario(
    usuario_id: int,
    db: Session = Depends(get_db),
):
    try:
        if repositorio.deletar_usuario(db, usuario_id):
            logger.info(f"Usuário deletado com sucesso: ID {usuario_id}")
            return {"msg": "Usuário deletado com sucesso."}
    except Exception as e:
        traceback.print_exc()
        logger.error(f"Erro ao deletar usuário {usuario_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Erro ao deletar o usuário"
        )


# ------------------ Rota para Listar pedidos do Usuário ------------------


# @router.get(
#     "/{usuario_id}/pedidos",
#     response_model=List[schemas.PedidoRespostaComLinks],
#     status_code=status.HTTP_200_OK,
# )
# def listar_pedidos_usuario(
#     usuario_id: int,
#     db: Session = Depends(get_db),
#     limit: int = Query(10, le=100),
#     offset: int = Query(0, ge=0),
# ):
#     try:
#         pedidos = repositorio.listar_pedidos_usuario(db, usuario_id, limit, offset)
#         total_pedidos = repositorio.contar_pedidos_usuario(db, usuario_id)

#         next_offset = offset + limit if offset + limit < total_pedidos else None
#         prev_offset = offset - limit if offset > 0 else None

#         links_paginacao = []
#         if prev_offset is not None:
#             links_paginacao.append(
#                 {
#                     "rel": "previous",
#                     "href": f"/pedidos?offset={prev_offset}&limit={limit}",
#                 }
#             )
#         if next_offset is not None:
#             links_paginacao.append(
#                 {"rel": "next", "href": f"/pedidos?offset={next_offset}&limit={limit}"}
#             )

#         return [
#             schemas.PedidoRespostaComLinks(
#                 id=pedido.id,
#                 preco_total=pedido.preco_total,
#                 links=[
#                     {"rel": "self", "href": f"/pedidos/{pedido.id}"},
#                     {"rel": "usuario", "href": f"/usuarios/{usuario_id}"},
#                     *links_paginacao,
#                 ],
#             )
#             for pedido in pedidos
#         ]
#     except Exception as e:
#         traceback.print_exc()
#         logger.error(f"Erro ao listar pedidos: {str(e)}")
#         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

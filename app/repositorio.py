from sqlalchemy.orm import Session
import models, seguranca
from typing import List
from pydantic import BaseModel, EmailStr

# ------------------ CRUD Usuário ------------------


def criar_usuario(db: Session, usuario: BaseModel):
    senha_hash = seguranca.gerar_senha_hash(usuario.senha)
    novo_usuario = models.Usuario(
        nome=usuario.nome, email=usuario.email, senha_hash=senha_hash
    )
    db.add(novo_usuario)
    db.commit()
    db.refresh(novo_usuario)
    return novo_usuario


def obter_usuario_por_id(db: Session, usuario_id: int):
    return db.query(models.Usuario).filter(models.Usuario.id == usuario_id).first()


def obter_usuario_por_email(db: Session, email: str):
    return db.query(models.Usuario).filter(models.Usuario.email == email).first()


def atualizar_usuario(db: Session, usuario_id: int, usuario_dados: BaseModel):
    usuario = obter_usuario_por_id(db, usuario_id)
    if not usuario:
        return None
    for chave, valor in usuario_dados.dict(exclude_unset=True).items():
        setattr(usuario, chave, valor)
    db.commit()
    db.refresh(usuario)
    return usuario


def deletar_usuario(db: Session, usuario_id: int):
    usuario = obter_usuario_por_id(db, usuario_id)
    if not usuario:
        return False
    db.delete(usuario)
    db.commit()
    return True


def autenticar_usuario(db: Session, email: str, senha: str):
    usuario = db.query(models.Usuario).filter(models.Usuario.email == email).first()
    if usuario and seguranca.verificar_senha(senha, usuario.senha_hash):
        return usuario
    return None


def obter_usuarios(db: Session) -> List[models.Usuario]:
    return db.query(models.Usuario).all()


# # ------------------ CRUD Produto ------------------


# def criar_produto(db: Session, produto: BaseModel):
#     novo_produto = models.Produto(**produto.dict())
#     db.add(novo_produto)
#     db.commit()
#     db.refresh(novo_produto)
#     return novo_produto


# def obter_produto_por_id(db: Session, produto_id: int):
#     return db.query(models.Produto).filter(models.Produto.id == produto_id).first()


# def listar_produtos(db: Session):
#     return db.query(models.Produto).all()


# def atualizar_produto(db: Session, produto_id: int, produto_dados: BaseModel):
#     produto = obter_produto_por_id(db, produto_id)
#     if not produto:
#         return None
#     for chave, valor in produto_dados.dict(exclude_unset=True).items():
#         setattr(produto, chave, valor)
#     db.commit()
#     db.refresh(produto)
#     return produto


# def deletar_produto(db: Session, produto_id: int):
#     produto = obter_produto_por_id(db, produto_id)
#     if not produto:
#         return False
#     db.delete(produto)
#     db.commit()
#     return True


# # ------------------ CRUD Pedido ------------------


# def criar_pedido(db: Session, usuario_id: int, pedido: BaseModel):
#     novo_pedido = models.Pedido(usuario_id=usuario_id)
#     db.add(novo_pedido)
#     db.commit()
#     db.refresh(novo_pedido)

#     pedido_produto_entries = []
#     for produto_id in pedido.produtos:
#         produto = db.query(models.Produto).filter_by(id=produto_id).first()
#         if not produto or produto.estoque <= 0:
#             continue  # Ignora produtos sem estoque

#         produto.estoque -= 1  # Debita do estoque
#         db.add(produto)

#         pedido_produto_entries.append(
#             models.PedidoProduto(
#                 pedido_id=novo_pedido.id, produto_id=produto.id, preco=produto.preco
#             )
#         )

#     db.add_all(pedido_produto_entries)
#     db.commit()
#     db.refresh(novo_pedido)
#     return novo_pedido


# def obter_pedido_por_id(db: Session, pedido_id: int):
#     return db.query(models.Pedido).filter(models.Pedido.id == pedido_id).first()


# def listar_pedidos_usuario(db: Session, usuario_id: int, limit: int, offset: int):
#     return (
#         db.query(models.Pedido)
#         .filter(models.Pedido.usuario_id == usuario_id)
#         .offset(offset)
#         .limit(limit)
#         .all()
#     )


# def contar_pedidos_usuario(db: Session, usuario_id: int):
#     return (
#         db.query(models.Pedido).filter(models.Pedido.usuario_id == usuario_id).count()
#     )


# def deletar_pedido(db: Session, pedido_id: int):
#     pedido = obter_pedido_por_id(db, pedido_id)
#     if not pedido:
#         return False
#     db.query(models.PedidoProduto).filter_by(pedido_id=pedido.id).delete()
#     db.delete(pedido)
#     db.commit()
#     return True

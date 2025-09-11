from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Union
from schemas import Parametro
from models import Parametro as ModelParametro
from database import get_db

parametros_router = APIRouter()

@parametros_router.get("/parametros", response_model=List[Parametro])
def read_parametros(db: Session = Depends(get_db)):
    """
    Retorna uma lista de todos os parametros cadastrados.

    """
    parametros = db.query(ModelParametro).all()
    return [Parametro.from_orm(parametro) for parametro in parametros]

@parametros_router.get("/parametros/{parametro_id}", response_model=Parametro)
def read_parametro(parametro_id: int, db: Session = Depends(get_db)):
    """
    Retorna os detalhes de um parametro específico com base no ID fornecido.

    Args:
        parametro_id: O ID do parametro.

    Raises:
        HTTPException: Se o parametro não for encontrado.
    """
    db_parametro = db.query(ModelParametro).filter(ModelParametro.id == parametro_id).first()
    if db_parametro is None:
        raise HTTPException(status_code=404, detail="Parametro não encontrado")
    return Parametro.from_orm(db_parametro)

@parametros_router.post("/parametros", response_model=Parametro)
def create_parametro(parametro: Parametro, db: Session = Depends(get_db)):
    """
    Cria um novo parametro com os dados fornecidos.

    Args:
        parametro: Dados do parametro a ser criado.

    Returns:
        Parametro: parametro criado.
    """ 
    db_parametro = ModelParametro(**parametro.dict(exclude={"id"})) 
    db.add(db_parametro)
    db.commit()
    db.refresh(db_parametro)
    return Parametro.from_orm(db_parametro)

@parametros_router.put("/parametros/{parametro_id}", response_model=Parametro)
def update_parametro(parametro_id: int, parametro: Parametro, db: Session = Depends(get_db)):
    """
    Atualiza os dados de um parametro existente.

    Args:
        parametro_id: O ID do parametro a ser atualizado.
        parametro: Os novos dados do parametro.

    Raises:
        HTTPException: 404 - Parametro não encontrado.

    Returns:
        Parametro: O parametro atualizado.
    """
    db_parametro = db.query(ModelParametro).filter(ModelParametro.id == parametro_id).first()
    if db_parametro is None:
        raise HTTPException(status_code=404, detail="Parametro não encontrado")

    for key, value in parametro.dict(exclude_unset=True).items():
        setattr(db_parametro, key, value)

    db.commit()
    db.refresh(db_parametro)
    return Parametro.from_orm(db_parametro)

@parametros_router.delete("/parametros/{parametro_id}", response_model=Parametro)
def delete_parametro(parametro_id: int, db: Session = Depends(get_db)):
    """
    Exclui um parametro.

    Args:
        parametro_id: O ID do parametro a ser excluído.

    Raises:
        HTTPException: 404 - Parametro não encontrado.

    Returns:
        Parametro: O parametro excluído.
    """
    db_parametro = db.query(ModelParametro).filter(ModelParametro.id == parametro_id).first()
    if db_parametro is None:
        raise HTTPException(status_code=404, detail="Parametro não encontrado")

    parametro_deletado = Parametro.from_orm(db_parametro)

    db.delete(db_parametro)
    db.commit()
    return parametro_deletado

@parametros_router.get("/parametros/nome/{nome_parametro}", response_model=Union[Parametro, List[Parametro]]) 
def read_parametro_por_nome(nome_parametro: str, db: Session = Depends(get_db)):
    """
    Busca parametros pelo nome (parcial ou completo).
    
    Args:
        nome_parametro: O nome (ou parte do nome) do parametro a ser buscado.
    
    Raises:
        HTTPException: 404 - Nenhum parametro encontrado com esse nome.
        
    Returns:
        Union[Parametro, List[Parametro]]: Um único objeto `Parametro` se houver apenas uma correspondência, 
        ou uma lista de `Parametro` se houver várias correspondências.
    """
    db_parametros = db.query(ModelParametro).filter(ModelParametro.nome.ilike(f"%{nome_parametro}%")).all() # ilike para case-insensitive

    if not db_parametros:
        raise HTTPException(status_code=404, detail="Nenhum parametro encontrado com esse nome")

    if len(db_parametros) == 1:  # Retorna um único Parametro se houver apenas uma correspondência
        return Parametro.from_orm(db_parametros[0])

    return [Parametro.from_orm(parametro) for parametro in db_parametros]

@parametros_router.get("/parametros/email/{email_parametro}", response_model=Parametro)
def read_parametro_por_email(email_parametro: str, db: Session = Depends(get_db)):
    """
    Busca um parametro pelo email.

    Args:
        email_parametro: O email do parametro a ser buscado.
        
    Raises:
         HTTPException: 404 - Nenhum parametro encontrado com esse email.

    Returns:
        Parametro: O parametro encontrado.
    """
    db_parametro = db.query(ModelParametro).filter(ModelParametro.email == email_parametro).first()

    if db_parametro is None:
        raise HTTPException(status_code=404, detail="Nenhum parametro encontrado com esse email")
    
    return Parametro.from_orm(db_parametro)
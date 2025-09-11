from fastapi import APIRouter, Depends, HTTPException,  status, Security
from sqlalchemy.orm import Session
from fastapi.security import APIKeyHeader
from typing import List, Union
from schemas import Rio, Parametro, Coleta
from models import Rio as ModelRio
from models import Parametro as ModelParametro
from models import ColetaParametro as ModelColetaParametro
from models import Coleta as ModelColeta
from database import get_db
from sqlalchemy import func
import traceback
import seguranca
from configuracao import logger, configuracoes, API_KEY_HASH


rios_router = APIRouter()

@rios_router.get("/rios", response_model=List[Rio])
def read_rios(db: Session = Depends(get_db)):
    rios = db.query(ModelRio).all()
    return [Rio.from_orm(rio) for rio in rios]

@rios_router.post("/rios", response_model=Rio)
def create_rio(
    rio: Rio, 
    db: Session = Depends(get_db),
    api_key_header: str = Security(APIKeyHeader(name="X-API-Key")),
):

    if not seguranca.verificar_api_key(api_key_header, API_KEY_HASH):
        logger.warning(
            f"Falha na autenticação: API Key inválida ou ausente. Chave recebida: {api_key_header}"
        )
        # Caso a chave da API seja inválida, levantamos uma HTTPException com status 401
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key inválida ou não fornecida. Por favor, forneça uma chave válida.",
        )
    
    try:
        db_rio = ModelRio(**rio.dict(exclude={"id"}))
        db.add(db_rio)
        db.commit()
        db.refresh(db_rio)
        return Rio.from_orm(db_rio)
    
    except Exception as e:
        traceback.print_exc()
        # Logando o erro
        logger.error(f"Erro ao criar produto: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@rios_router.put("/rios/{codigo_rio}", response_model=Rio)
def update_rio(codigo_rio: str, rio: Rio, db: Session = Depends(get_db)):
    db_rio = db.query(ModelRio).filter(ModelRio.codigo == codigo_rio).first()
    if db_rio is None:
        raise HTTPException(status_code=404, detail="Rio não encontrado")

    for key, value in rio.dict(exclude_unset=True, exclude={"id"}).items():
        setattr(db_rio, key, value)

    db.commit()
    db.refresh(db_rio)
    return Rio.from_orm(db_rio)

@rios_router.get("/rios/{codigo_rio}", response_model=Rio)
def read_rio_por_codigo(codigo_rio: str, db: Session = Depends(get_db)):
    db_rio = db.query(ModelRio).filter(ModelRio.codigo == codigo_rio).first()
    if db_rio is None:
        raise HTTPException(status_code=404, detail="Nenhum rio encontrado com esse código")
    return Rio.from_orm(db_rio)

@rios_router.get("/rios/nome/{rio_nome}", response_model=Union[Rio, List[Rio]]) 
def read_parametro_por_nome(rio_nome: str, db: Session = Depends(get_db)):
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
    db_parametros = db.query(ModelRio).filter(ModelRio.nome.ilike(f"%{rio_nome}%")).all() # ilike para case-insensitive

    if not db_parametros:
        raise HTTPException(status_code=404, detail="Nenhum parametro encontrado com esse nome")

    if len(db_parametros) == 1:  # Retorna um único Parametro se houver apenas uma correspondência
        return Rio.from_orm(db_parametros[0])

    return [Rio.from_orm(parametro) for parametro in db_parametros]


@rios_router.get("/rio/{rio_nome}/coletas/{parametro_nome}/resumo")
def get_resumo_estatistico(rio_nome: str, parametro_nome: str, db: Session = Depends(get_db)):
    # Buscando o rio
    rio = db.query(ModelRio).filter(ModelRio.nome == rio_nome).first()
    if not rio:
        raise HTTPException(status_code=404, detail="Rio não encontrado")
    
    parametro = db.query(ModelParametro).filter(ModelParametro.nome == parametro_nome).first()
    if not parametro:
        raise HTTPException(status_code=404, detail="Parametro não encontrado")
    
    # Buscando as coletas do rio e o parâmetro desejado
    # parametro_resumo = db.query(
    #     func.avg(ModelColetaParametro.valor).label("media"),
    #     func.max(ModelColetaParametro.valor).label("maximo"),
    #     func.min(ModelColetaParametro.valor).label("minimo")
    # ).join(ModelColetaParametro).join(ModelColeta).filter(        #).join(ModelColeta).filter(
    #     ModelColeta.rio_id == rio.id,  #    ModelColeta.rio_id == rio.id,
    #     ModelColetaParametro.parametro_id == parametro.id   #ModelColetaParametro.parametro_id == parametro.id
    # ).first()

    parametro_resumo = db.query(
        func.avg(ModelColetaParametro.valor).label("media"),
        func.max(ModelColetaParametro.valor).label("maximo"),
        func.min(ModelColetaParametro.valor).label("minimo")
    ).select_from(ModelColetaParametro).join(
        ModelColeta, ModelColeta.id == ModelColetaParametro.coleta_id
    ).join(
        ModelRio, ModelRio.id == ModelColeta.rio_id
    ).join(
        ModelParametro, ModelParametro.id == ModelColetaParametro.parametro_id
    ).filter(
        ModelRio.id == rio.id, 
        ModelParametro.id == parametro.id
    ).first()


    if parametro_resumo is None:
        raise HTTPException(status_code=404, detail="Parâmetro não encontrado para esse rio")

    # Retornando o resumo estatístico
    return {
        "id": rio.id,
        "nome": parametro_nome,
        "média": parametro_resumo.media,
        "máximo": parametro_resumo.maximo,
        "mínimo": parametro_resumo.minimo
    }

@rios_router.get("/rio/{rio_nome}/coletas/{parametro_nome}/grafico")
def get_grafico(rio_nome: str, parametro_nome: str, db: Session = Depends(get_db)):
    # Buscando o rio
    rio = db.query(ModelRio).filter(ModelRio.nome == rio_nome).first()
    if not rio:
        raise HTTPException(status_code=404, detail="Rio não encontrado")
    
    parametro = db.query(ModelParametro).filter(ModelParametro.nome == parametro_nome).first()
    if not parametro:
        raise HTTPException(status_code=404, detail="Parametro não encontrado")
    # Buscando os valores de coleta do rio e o parâmetro desejado
    # parametros = db.query(
    #     ModelParametro.nome,
    #     ModelColetaParametro.valor,
    #     ModelColeta.datas
    # ).join(ModelColeta).filter(
    #     ModelColeta.rio_id == rio.id, #MESMA COISA ACIMA
    #     ModelColetaParametro.parametro_id == parametro.id
    # ).all()

    parametros = db.query(
        ModelParametro.nome,
        ModelColetaParametro.valor,
        ModelColeta.datas
    ).select_from(ModelColetaParametro
    ).join(
        ModelColeta, ModelColeta.id == ModelColetaParametro.coleta_id
    ).join(
        ModelRio, ModelRio.id == ModelColeta.rio_id
    ).join(
        ModelParametro, ModelParametro.id == ModelColetaParametro.parametro_id
    ).filter(
        ModelRio.id == rio.id, 
        ModelParametro.id == parametro.id
    ).all()


    if not parametros:
        raise HTTPException(status_code=404, detail="Parâmetro não encontrado para esse rio")

    # Preparando os dados para o gráfico
    dados_grafico = [{"data": parametro.datas, "valor": parametro.valor} for parametro in parametros]

    return {
        "id": rio.id,
        "nome": parametro_nome,
        "dados": dados_grafico
    }

# Não buscar um rio pelo ID nem deletar em nenhuma hipótese

# @rios_router.get("/rios/{rio_id}", response_model=Rio)
# def read_rio(rio_id: int, db: Session = Depends(get_db)):
#     db_rio = db.query(ModelRio).filter(ModelRio.id == rio_id).first()
#     if db_rio is None:
#         raise HTTPException(status_code=404, detail="Rio não encontrado")
#     return Rio.from_orm(db_rio)


# @rios_router.delete("/rios/{rio_id}", response_model=Rio)
# def delete_rio(rio_id: int, db: Session = Depends(get_db)):
#     db_rio = db.query(ModelRio).filter(ModelRio.id == rio_id).first()
#     if db_rio is None:
#         raise HTTPException(status_code=404, detail="Rio não encontrado")

#     rio_deletado = Rio.from_orm(db_rio)

#     db.delete(db_rio)
#     db.commit()
#     return rio_deletado
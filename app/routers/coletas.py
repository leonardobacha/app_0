from fastapi import APIRouter, Depends, HTTPException, status, Security
from sqlalchemy.orm import Session
from fastapi.security import APIKeyHeader
from typing import List, Dict, Union
from schemas import Coleta
from models import Coleta as ModelColeta, Parametro as ModelParametro, Rio as ModelRio # Importe os modelos
from database import get_db
import seguranca
from configuracao import logger, configuracoes, API_KEY_HASH
import traceback

coletas_router = APIRouter()

@coletas_router.post("/coletas", response_model=Coleta, status_code=status.HTTP_201_CREATED)
def create_coleta(
    coleta: Coleta, 
    db: Session = Depends(get_db),
    api_key_header: str = Security(APIKeyHeader(name="X-API-Key"))):
    
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


        db_parametro = db.query(ModelParametro).filter(ModelParametro.id == coleta.parametro_id).first()
        db_rio = db.query(ModelRio).filter(ModelRio.id == coleta.rio_id).first()

        if db_parametro is None or db_rio is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Parametro ou Rio não encontrado")

        db_coleta = ModelColeta(**coleta.dict())
        db.add(db_coleta)
        db.commit()
        db.refresh(db_coleta)
        return Coleta.from_orm(db_coleta)

    except Exception as e:
        traceback.print_exc()
        # Logando o erro
        logger.error(f"Erro ao criar produto: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

# @coletas_router.get("/coletas", response_model=List[Coleta])
# def read_all_coletas(db: Session = Depends(get_db)):
#     coletas = db.query(ModelColeta).all()
#     return [Coleta.from_orm(c) for c in coletas]


@coletas_router.get("/coletas", response_model=List[Coleta])
def read_all_coletas(db: Session = Depends(get_db)):
    coletas = db.query(ModelColeta).all()

    # Garante que os dados relacionados sejam carregados
    for c in coletas:
        _ = c.coletas_parametros

    return coletas

@coletas_router.get("/coletas/parametro/{nome_parametro}", response_model=Dict[str, Union[str, List[str]]])
def read_coletas_por_nome_parametro(nome_parametro: str, db: Session = Depends(get_db)):
    db_parametro = db.query(ModelParametro).filter(ModelParametro.nome.ilike(f"%{nome_parametro}%")).first()

    if not db_parametro:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Parametro não encontrado")

    rios_coletados = []
    for coleta in db_parametro.coletas_parametros:
        rio = coleta.rio  
        if rio:  
            rios_coletados.append(rio.nome)

    if not rios_coletados:
        raise HTTPException(status_code=404, detail=f"O parametro '{nome_parametro}' não possui matrículas cadastradas.")

    return {"parametro": db_parametro.nome, "rios": rios_coletados}

@coletas_router.get("/coletas/rio/{codigo_rio}", response_model=Dict[str, Union[str, List[str]]])
def read_parametros_coletados_por_codigo_rio(codigo_rio: str, db: Session = Depends(get_db)):
    """Retorna o nome do rio e uma lista com os nomes dos parametros coletados."""
    db_rio = db.query(ModelRio).filter(ModelRio.codigo == codigo_rio).first()

    if not db_rio:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rio não encontrado")

    # parametros_coletados = []
    # for coleta in db_rio.coletas:  # Itera pelas matrículas do rio
    #     parametro = coleta.coletas_parametros  # Acessa o parametro diretamente pelo relacionamento
    #     if parametro:  # Verifica se o parametro existe (pode ter sido excluído)
    #         parametros_coletados.append(parametro.nome) #parametro.nome

    parametros_coletados = []

    for coleta in db_rio.coletas:
        for parametro in coleta.coletas_parametros:
            if parametro:
                parametros_coletados.append(parametro.parametro.nome)

    parametros_coletados = list(set(parametros_coletados))


    if not parametros_coletados:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Nenhum parametro coletado no rio '{db_rio.nome}'.")

    return {"rio": db_rio.nome, "parametros": parametros_coletados}

##ESSE CODIGO PRESTA ABAIXO ##########


@coletas_router.get("/coletas/rio/{codigo_rio}/parametro/{nome_parametro}", response_model=Dict[str, Union[str, List[Dict[str, Union[str, float]]]]])
def read_valores_parametro_rio(
    codigo_rio: str,
    nome_parametro: str,
    db: Session = Depends(get_db)
):
    """Retorna os valores de um parâmetro coletado ao longo do tempo para um rio."""
    db_rio = db.query(ModelRio).filter(ModelRio.codigo == codigo_rio).first()
    if not db_rio:
        raise HTTPException(status_code=404, detail="Rio não encontrado.")

    # Buscar o parâmetro
    db_parametro = db.query(ModelParametro).filter(ModelParametro.nome == nome_parametro).first()
    if not db_parametro:
        raise HTTPException(status_code=404, detail="Parâmetro não encontrado.")

    valores = []
    for coleta in db_rio.coletas:
        for pc in coleta.coletas_parametros:  # relacionamento coleta.parametros_coleta
            if pc.parametro_id == db_parametro.id:
                valores.append({
                    "data": coleta.datas.isoformat(),
                    "local": coleta.locali,
                    "valor": pc.valor,
                    "latitude": coleta.latitude,     # NOVO
                    "longitude": coleta.longitude 
                })

    if not valores:
        raise HTTPException(status_code=404, detail="Nenhum valor encontrado para esse parâmetro no rio.")

    return {
        "rio": db_rio.nome,
        "parametro": db_parametro.nome,
        "valores": sorted(valores, key=lambda x: x["data"])
    }

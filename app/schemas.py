from pydantic import BaseModel, EmailStr
from typing import List,Optional
from datetime import date

class ColetaParametro(BaseModel):
    parametro_id: int
    valor: float

    class Config:
        from_attributes = True
        orm_mode = True


class Coleta(BaseModel):
    codigo: str  #ADDICIONEI
    locali:str
    # parametro_id: int
    rio_id: int
    datas: date
    latitude: float  # NOVO
    longitude: float
    coletas_parametros: List[ColetaParametro]  # <-- Correção aqui

    #parametros: List[int] #ADICIONEI ISSO, SERÁ QUE É ISSO?

    class Config:
        from_attributes = True
        orm_mode = True

Coletas = List[Coleta]

class Parametro(BaseModel):
    nome: str
    #valor: float
    categoria: str

    class Config:
        from_attributes = True

Parametros = List[Parametro]

class Rio(BaseModel):
    nome: str
    codigo: str
    descricao: str

    class Config:
        from_attributes = True
        

Rios = List[Rio]


# ------------------ Usuário ------------------


class UsuarioBase(BaseModel):
    nome: str
    email: EmailStr

    class Config:
        orm_mode = True  # Permite que o modelo seja convertido para o formato ORM


class UsuarioCriacao(UsuarioBase):
    senha: str  # Campo para senha na criação do usuário


class UsuarioAtualizacao(BaseModel):
    nome: Optional[str]  # Pode ser atualizado ou deixado em branco
    email: Optional[EmailStr]  # Pode ser atualizado ou deixado em branco
    senha: Optional[str]  # Pode ser atualizado ou deixado em branco

    class Config:
        orm_mode = True


class UsuarioResposta(UsuarioBase):
    id: int  # ID do usuário que será retornado após criação ou consulta

    class Config:
        orm_mode = True


class UsuarioRespostaComLinks(UsuarioBase):
    id: int
    links: List[dict]

    class Config:
        orm_mode = True


# ------------------ Resposta de Autenticação ------------------


class Token(BaseModel):
    access_token: str
    token_type: str

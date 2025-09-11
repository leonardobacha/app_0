from sqlalchemy import Column, Integer, String, Text, ForeignKey, Float, Table, Date
from sqlalchemy.orm import relationship
from database import Base

class Usuario(Base):
    __tablename__ = "tb_usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    senha_hash = Column(String)

    #pedidos = relationship("Rio", back_populates="rio")



class Coleta(Base):
    __tablename__ = "coletas"

    id = Column(Integer, primary_key=True, index=True)
    codigo = Column(String, index=True)  # ADDICIONEI
    locali = Column(String, index=True)
    #parametro_id = Column(Integer, ForeignKey("parametros.id"))
    rio_id = Column(Integer, ForeignKey("rios.id"))
    datas = Column(Date, index=True)
    latitude = Column(Float)    # NOVO
    longitude = Column(Float) 
    rio = relationship("Rio", back_populates="coletas")
    coletas_parametros = relationship("ColetaParametro", back_populates="coletas")

class Parametro(Base):
    __tablename__ = "parametros"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    #valor = Column(Float, nullable=False)
    categoria = Column(String, nullable=False)

   # coletas = relationship("Coleta", back_populates="parametro")
    coletas_parametros = relationship("ColetaParametro", back_populates="parametro")

class ColetaParametro(Base):
    __tablename__ = "coletas_parametros"        #coletasparametros

    id = Column(Integer, primary_key=True, index=True)
    parametro_id = Column(Integer, ForeignKey("parametros.id"))
    coleta_id = Column(Integer, ForeignKey("coletas.id"))
    valor = Column(Float, nullable=False)

    coletas = relationship("Coleta", back_populates="coletas_parametros")
    parametro = relationship("Parametro", back_populates="coletas_parametros")


class Rio(Base):
    __tablename__ = "rios"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    codigo = Column(String, nullable=False, unique=True) 
    descricao = Column(Text)  

    coletas = relationship("Coleta", back_populates="rio")
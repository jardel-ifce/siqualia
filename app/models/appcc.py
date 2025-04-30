# app/models/appcc.py

from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.db.database import Base

# Tabela de Produtos
class Produto(Base):
    __tablename__ = "produtos"

    id_produto = Column(Integer, primary_key=True, index=True)
    nome_produto = Column(Text, nullable=False)
    descricao_produto = Column(Text)

    etapas = relationship("Etapa", back_populates="produto")

# Tabela de Etapas
class Etapa(Base):
    __tablename__ = "etapas"

    id_etapa = Column(Integer, primary_key=True, index=True)
    id_produto = Column(Integer, ForeignKey("produtos.id_produto"), nullable=False)
    nome_etapa = Column(Text, nullable=False)
    descricao_etapa = Column(Text)

    produto = relationship("Produto", back_populates="etapas")
    perigos = relationship("Perigo", back_populates="etapa")

# Tabela de Tipos de Perigo
class TipoPerigo(Base):
    __tablename__ = "tipo_perigo"

    id_tipo_perigo = Column(Integer, primary_key=True, index=True)
    codigo_perigo = Column(String(5), nullable=False)
    nome_tipo_perigo = Column(Text, nullable=False)

    perigos = relationship("Perigo", back_populates="tipo_perigo")

# Tabela de Perigos
class Perigo(Base):
    __tablename__ = "perigos"

    id_perigo = Column(Integer, primary_key=True, index=True)
    id_etapa = Column(Integer, ForeignKey("etapas.id_etapa"), nullable=False)
    id_tipo_perigo = Column(Integer, ForeignKey("tipo_perigo.id_tipo_perigo"), nullable=False)
    descricao_perigo = Column(Text, nullable=False)

    etapa = relationship("Etapa", back_populates="perigos")
    tipo_perigo = relationship("TipoPerigo", back_populates="perigos")
    justificativas = relationship("Justificativa", back_populates="perigo")
    medidas_controle = relationship("MedidaControle", back_populates="perigo")

# Tabela de Justificativas
class Justificativa(Base):
    __tablename__ = "justificativas"

    id_justificativa = Column(Integer, primary_key=True, index=True)
    id_perigo = Column(Integer, ForeignKey("perigos.id_perigo"), nullable=False)
    texto_justificativa = Column(Text, nullable=False)

    perigo = relationship("Perigo", back_populates="justificativas")

# Tabela de Medidas de Controle
class MedidaControle(Base):
    __tablename__ = "medidas_controle"

    id_medida = Column(Integer, primary_key=True, index=True)
    id_perigo = Column(Integer, ForeignKey("perigos.id_perigo"), nullable=False)
    texto_medida = Column(Text, nullable=False)

    perigo = relationship("Perigo", back_populates="medidas_controle")

# Formulário G
class FormularioG(Base):
    __tablename__ = "formulario_g"

    id_formulario_g = Column(Integer, primary_key=True, index=True)
    id_produto = Column(Integer, ForeignKey("produtos.id_produto"), nullable=False)
    id_etapa = Column(Integer, ForeignKey("etapas.id_etapa"), nullable=False)
    id_perigo = Column(Integer, ForeignKey("perigos.id_perigo"), nullable=False)
    id_tipo_perigo = Column(Integer, ForeignKey("tipo_perigo.id_tipo_perigo"), nullable=False)
    justificativa = Column(Text, nullable=False)
    probabilidade = Column(Text, nullable=False)
    severidade = Column(Text, nullable=False)
    risco = Column(Text, nullable=False)
    medida_preventiva = Column(Text, nullable=False)
    perigo_significativo = Column(Text)

# Formulário H
class FormularioH(Base):
    __tablename__ = "formulario_h"

    id_formulario_h = Column(Integer, primary_key=True, index=True)
    id_formulario_g = Column(Integer, ForeignKey("formulario_g.id_formulario_g"), nullable=False)
    controlado_por_prerequisito = Column(Text)
    q1_medidas_preventivas = Column(Text)
    q2_reducao_perigo = Column(Text)
    q3_aumento_perigo = Column(Text)
    q4_eliminacao_posterior = Column(Text)
    pcc = Column(Text)
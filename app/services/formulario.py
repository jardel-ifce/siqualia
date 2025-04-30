from sqlalchemy.orm import Session
from app.models.appcc import Produto, Etapa, TipoPerigo, Perigo, Justificativa, MedidaControle


def verificar_ou_criar_ids(
        db: Session,
        produto_nome: str,
        etapa_nome: str,
        tipo_perigo_nome: str,
        perigo_nome: str,
        justificativa_texto: str,
        medida_texto: str
):
    # Produto (já selecionado)
    produto = db.query(Produto).filter(Produto.nome_produto == produto_nome).first()
    if not produto:
        raise ValueError("Produto não encontrado no banco.")

    # Etapa
    etapa = db.query(Etapa).filter(
        Etapa.nome_etapa == etapa_nome,
        Etapa.id_produto == produto.id_produto
    ).first()
    etapa_existente = True
    if not etapa:
        etapa = Etapa(nome_etapa=etapa_nome, id_produto=produto.id_produto)
        db.add(etapa)
        db.commit()
        db.refresh(etapa)
        etapa_existente = False

    # Mapeamento de tipo pelo código}
    # Dinâmica pela tabela (atualizar depois)
    mapa_tipo_codigo = {
        "Biológico": "B",
        "Químico": "Q",
        "Físico": "F",
        "Alergênico": "A",
        "Radiológico": "R",
        "Qualidade": "QUAL"
    }

    codigo = mapa_tipo_codigo.get(tipo_perigo_nome.strip().capitalize(), tipo_perigo_nome[:3].upper())

    tipo = db.query(TipoPerigo).filter(TipoPerigo.codigo_perigo == codigo).first()
    tipo_existente = True
    if not tipo:
        tipo = TipoPerigo(
            nome_tipo_perigo=tipo_perigo_nome.strip().capitalize(),
            codigo_perigo=codigo
        )
        db.add(tipo)
        db.commit()
        db.refresh(tipo)
        tipo_existente = False

    # Perigo
    perigo = db.query(Perigo).filter(
        Perigo.descricao_perigo == perigo_nome,
        Perigo.id_etapa == etapa.id_etapa
    ).first()
    perigo_existente = True
    if not perigo:
        perigo = Perigo(
            descricao_perigo=perigo_nome,
            id_etapa=etapa.id_etapa,
            id_tipo_perigo=tipo.id_tipo_perigo
        )
        db.add(perigo)
        db.commit()
        db.refresh(perigo)
        perigo_existente = False

    # Justificativa
    justificativa = db.query(Justificativa).filter(
        Justificativa.id_perigo == perigo.id_perigo,
        Justificativa.texto_justificativa == justificativa_texto
    ).first()
    justificativa_existente = True
    if not justificativa:
        justificativa = Justificativa(
            id_perigo=perigo.id_perigo,
            texto_justificativa=justificativa_texto
        )
        db.add(justificativa)
        db.commit()
        db.refresh(justificativa)
        justificativa_existente = False

    # Medida
    medida = db.query(MedidaControle).filter(
        MedidaControle.id_perigo == perigo.id_perigo,
        MedidaControle.texto_medida == medida_texto
    ).first()
    medida_existente = True
    if not medida:
        medida = MedidaControle(
            id_perigo=perigo.id_perigo,
            texto_medida=medida_texto
        )
        db.add(medida)
        db.commit()
        db.refresh(medida)
        medida_existente = False

    return {
        "produto": {"id": produto.id_produto, "existente": True},
        "etapa": {"id": etapa.id_etapa, "existente": etapa_existente},
        "tipo_perigo": {"id": tipo.id_tipo_perigo, "existente": tipo_existente},
        "perigo": {"id": perigo.id_perigo, "existente": perigo_existente},
        "justificativa": {"id": justificativa.id_justificativa, "existente": justificativa_existente},
        "medida": {"id": medida.id_medida, "existente": medida_existente}
    }

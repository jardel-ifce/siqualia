import json
from pathlib import Path

def inicializar_formulario_h_em_arquivo(produto: str):
    pasta = Path("formulario_g/salvar")
    arquivos = list(pasta.glob(f"formulario_g_{produto}_*.json"))

    for arquivo in arquivos:
        with open(arquivo, "r", encoding="utf-8") as f:
            dados = json.load(f)

        if "formulario_h" in dados:
            print(f"[PULADO] Já contém formulário H: {arquivo.name}")
            continue

        perigos_significativos = [
            item for item in dados.get("formulario_g", [])
            if str(item.get("perigo_significativo", "")).strip().lower() == "sim"
        ]

        dados["formulario_h"] = [
            {
                "questao_1": None,
                "questao_2": None,
                "questao_3": None,
                "questao_4": None,
                "resultado": None
            }
            for _ in perigos_significativos
        ]

        with open(arquivo, "w", encoding="utf-8") as f:
            json.dump(dados, f, indent=2, ensure_ascii=False)

        print(f"[ATUALIZADO] Formulário H adicionado: {arquivo.name}")

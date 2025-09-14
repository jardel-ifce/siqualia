# ml/scripts/envase_rotulagem/predicao_mel.py
import pandas as pd, joblib, json, os, argparse

CLASSES = ['DESPREZÍVEL','BAIXA','MÉDIA','ALTA']

def listar_modelos_por_algoritmo(models_dir):
    modelos_por_algoritmo = {}
    if not os.path.exists(models_dir): return {}
    arquivos = [f for f in os.listdir(models_dir) if f.endswith(".pkl") and f.startswith("classificador_mel_")]
    for arq in arquivos:
        path = os.path.join(models_dir, arq)
        try:
            mdl = joblib.load(path)
            algoritmo = type(mdl).__name__
            ts = arq.replace("classificador_mel_","").replace(".pkl","")
            scaler = os.path.join(models_dir, f"scaler_mel_{ts}.pkl")
            cfg = os.path.join(models_dir, f"config_classificador_{ts}.json")
            if os.path.exists(scaler) and os.path.exists(cfg):
                with open(cfg, "r") as f: conf = json.load(f)
                nome_alg = {
                    "RandomForestClassifier":"Random Forest",
                    "SVC":"SVM",
                    "GradientBoostingClassifier":"Gradient Boosting",
                    "LogisticRegression":"Regressão Logística",
                    "GaussianNB":"Naive Bayes"
                }.get(algoritmo, algoritmo)
                modelos_por_algoritmo.setdefault(nome_alg, []).append({
                    "timestamp": ts, "modelo_path": path, "scaler_path": scaler,
                    "config_path": cfg, "config": conf, "algoritmo_original": algoritmo
                })
        except Exception:
            continue
    return modelos_por_algoritmo

def carregar_modelo_direto(info):
    modelo = joblib.load(info["modelo_path"])
    scaler = joblib.load(info["scaler_path"])
    return modelo, scaler

def criar_amostra_manual():
    # mesma interface anterior (20 atributos)
    attrs = {
        "tipo_embalagem":(0,1),"estado_embalagem":(0,1),"tampa_correta":(0,1),"vedacao_adequada":(0,1),
        "higienizacao_previa":(0,1),"uso_epi":(0,1,2),"local_envase":(0,1),"manipulador_higiene":(0,1),
        "aspecto_visual":(0,1,2),"umidade_mel":(0,1),"temperatura_envase":(0,1),"cristalizacao":(0,1,2),
        "rotulo_presente":(0,1),"informacoes_completas":(0,1),"data_validade_legivel":(0,1),
        "lote_identificado":(0,1),"registro_lote":(0,1),"treinamento_equipe":(0,1),
        "historico_reclamacoes":(0,1,2),"tempo_exposicao_ar":("num",5,60)
    }
    row = {}
    for col, dom in attrs.items():
        if dom[0] == "num":
            v = float(input(f"{col} ({dom[1]}..{dom[2]}): ").strip())
            row[col] = v
        else:
            v = int(input(f"{col} {dom}: ").strip())
            row[col] = v
    return pd.DataFrame([row])

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--perigo", choices=["bio","fis","qui"], required=True)
    args = ap.parse_args()

    script_dir = os.path.dirname(os.path.abspath(__file__))
    ml_dir = os.path.join(script_dir, "..", "..")
    models_dir = os.path.join(ml_dir, "models", "envase_rotulagem", args.perigo)

    modelos_por_alg = listar_modelos_por_algoritmo(models_dir)
    if not modelos_por_alg:
        print("Nenhum modelo encontrado. Treine antes com classificador_mel.py --perigo ...")
        return

    algs = list(modelos_por_alg.keys())
    for i, a in enumerate(algs):
        mais_recente = max(modelos_por_alg[a], key=lambda x: x["timestamp"])["timestamp"]
        print(f"{i+1}) {a} ({len(modelos_por_alg[a])}) - mais recente: {mais_recente}")
    idx = int(input("Escolha algoritmo: ").strip())-1
    algoritmo_escolhido = algs[idx]
    info = max(modelos_por_alg[algoritmo_escolhido], key=lambda x: x["timestamp"])

    modelo, scaler = carregar_modelo_direto(info)
    print("\nModelo carregado.")

    while True:
        amostra = criar_amostra_manual()
        amostra_s = scaler.transform(amostra)
        y = modelo.predict(amostra_s)[0]
        proba = modelo.predict_proba(amostra_s)[0]
        print("\nResultado:")
        for i, c in enumerate(CLASSES):
            mark = ">>" if i==y else "  "
            print(f"{mark} {c}: {proba[i]:.1%}")
        if input("\nOutra? (s/N): ").strip().lower() not in ("s","sim","y","yes"):
            break

if __name__ == "__main__":
    main()

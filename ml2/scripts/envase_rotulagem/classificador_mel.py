import pandas as pd
import joblib, os, sys, argparse, warnings, json
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.svm import SVC
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import GaussianNB
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
warnings.filterwarnings('ignore')

CLASSES = ['DESPREZÍVEL','BAIXA','MÉDIA','ALTA']

# ===== Subsets por perigo (núcleo mínimo) =====
FEATURE_SUBSETS = {
    "bio": [
        "umidade_mel","higienizacao_previa","manipulador_higiene","uso_epi",
        "local_envase","temperatura_envase","tempo_exposicao_ar","aspecto_visual"
    ],
    "fis": [
        "estado_embalagem","tampa_correta","vedacao_adequada","tipo_embalagem",
        "aspecto_visual","manipulador_higiene","local_envase"
    ],
    "qui": [
        "informacoes_completas","rotulo_presente","data_validade_legivel",
        "lote_identificado","vedacao_adequada","tipo_embalagem",
        "higienizacao_previa","registro_lote"
    ],
}

def carregar_dataset(perigo):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    ml_dir = os.path.join(script_dir, "..", "..")
    caminho = os.path.join(ml_dir, "dataset", "mel", "envase_rotulagem", perigo, "dataset_envase_rotulagem.csv")
    nome = f"Envase e Rotulagem ({perigo.upper()})"

    if not os.path.exists(caminho):
        vg = os.path.join(ml_dir, "view_generators")
        if vg not in sys.path: sys.path.insert(0, vg)
        from dataset_generator import gerar_dataset_por_tipo_perigo
        caminho, _ = gerar_dataset_por_tipo_perigo(perigo, 1500)

    df = pd.read_csv(caminho)
    if 'probabilidade' not in df.columns:
        raise RuntimeError("Coluna 'probabilidade' não encontrada no dataset")
    return df, nome

def escolher_algoritmo():
    algoritmos = {
        '1': ('Random Forest', RandomForestClassifier(n_estimators=200, max_depth=12, min_samples_split=5, random_state=42, n_jobs=-1)),
        '2': ('Gradient Boosting', GradientBoostingClassifier(n_estimators=200, max_depth=6, learning_rate=0.06, random_state=42)),
        '3': ('SVM', SVC(C=1.0, kernel='linear', random_state=42, probability=True)),
        '4': ('Regressão Logística', LogisticRegression(max_iter=1000, random_state=42, multi_class='ovr')),
        '5': ('Naive Bayes', GaussianNB()),
    }
    print("Algoritmos:\n1) RF  2) GB  3) SVM  4) LogReg  5) NB")
    escolha = input("Escolha (1-5): ").strip()
    return algoritmos.get(escolha, algoritmos['1'])

def salvar_resultados(y_test, y_pred, accuracy, nome_dataset, perigo, timestamp):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    ml_dir = os.path.join(script_dir, "..", "..")
    pasta_results = os.path.join(ml_dir, "results", "envase_rotulagem", perigo)
    os.makedirs(pasta_results, exist_ok=True)
    caminho = os.path.join(pasta_results, f"resultados_{perigo}_{timestamp}.txt")

    with open(caminho, "w", encoding="utf-8") as f:
        f.write(f"RESULTADOS - {nome_dataset}\n")
        f.write("="*60 + "\n\n")
        f.write(f"Acurácia: {accuracy:.1%}\n\n")
        f.write("MÉTRICAS POR CLASSE:\n")
        f.write(classification_report(y_test, y_pred, target_names=CLASSES))
        cm = confusion_matrix(y_test, y_pred)
        f.write("\nMATRIZ DE CONFUSÃO:\n"); f.write(str(cm)+"\n")
    print(f"Resultados salvos: {caminho}")
    return caminho, pasta_results

def salvar_modelo(modelo, scaler, nome_dataset, perigo, timestamp, features_usadas):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    ml_dir = os.path.join(script_dir, "..", "..")
    pasta_modelo = os.path.join(ml_dir, "models", "envase_rotulagem", perigo)
    os.makedirs(pasta_modelo, exist_ok=True)

    modelo_path = os.path.join(pasta_modelo, f"classificador_mel_{timestamp}.pkl")
    scaler_path = os.path.join(pasta_modelo, f"scaler_mel_{timestamp}.pkl")
    joblib.dump(modelo, modelo_path)
    joblib.dump(scaler, scaler_path)

    config = {
        "dataset_usado": nome_dataset,
        "timestamp": timestamp,
        "classes": CLASSES,
        "modelo_path": modelo_path,
        "scaler_path": scaler_path,
        "etapa": "envase_rotulagem",
        "tipo_perigo": perigo,
        "features_usadas": features_usadas,  # <<< salva a ordem das colunas
    }
    with open(os.path.join(pasta_modelo, f"config_classificador_{timestamp}.json"), "w") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    print(f"Modelo salvo em {pasta_modelo}")
    return modelo_path, scaler_path

def main():
    import pandas as pd
    from datetime import datetime

    parser = argparse.ArgumentParser()
    parser.add_argument("--perigo", choices=["bio","fis","qui"], required=True)
    args = parser.parse_args()

    df, nome_dataset = carregar_dataset(args.perigo)

    features = FEATURE_SUBSETS[args.perigo]           # <<< usa subset por perigo
    X = df[features].copy()
    y = df['probabilidade'].copy()

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2,
        random_state=42, stratify=y
    )

    scaler = StandardScaler()
    X_train_s = scaler.fit_transform(X_train)
    X_test_s  = scaler.transform(X_test)

    modelo_nome, modelo = escolher_algoritmo()
    print(f"\nTreinando {modelo_nome} para {args.perigo.upper()} (features={len(features)})...")
    modelo.fit(X_train_s, y_train)

    cv = cross_val_score(modelo, X_train_s, y_train, cv=5)
    print(f"CV média: {cv.mean():.3f} (+/- {cv.std()*2:.3f})")

    y_pred = modelo.predict(X_test_s)
    acc = accuracy_score(y_test, y_pred)
    print(f"Acurácia teste: {acc:.3f}")
    print(classification_report(y_test, y_pred, target_names=CLASSES))
    print(confusion_matrix(y_test, y_pred))

    # Permutation Importance (usa os nomes em 'features')
    timestamp = pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")
    resultados_path, pasta_results = salvar_resultados(y_test, y_pred, acc, nome_dataset, args.perigo, timestamp)

    vg_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "view_generators")
    if vg_dir not in sys.path: sys.path.insert(0, vg_dir)
    from graphic_results import compute_and_plot_permutation_importance

    pi_prefix = f"permutation_importance_{args.perigo}_{timestamp}"
    pi_info = compute_and_plot_permutation_importance(
        modelo=modelo,
        X_test_scaled=X_test_s,
        y_test=y_test.values,
        feature_names=features,
        out_dir=pasta_results,
        prefix=pi_prefix,
        n_repeats=10,
        random_state=42,
        scoring="accuracy",
        top_n=10
    )
    print(f"Permutation Importance salvo:")
    print(f" - CSV: {pi_info['csv_path']}")
    print(f" - PNG: {pi_info['png_path']}")

    salvar_modelo(modelo, scaler, nome_dataset, args.perigo, timestamp, features_usadas=features)
    print("\nConcluído.")

if __name__ == "__main__":
    main()

# ml/view_generators/graphic_results.py
import os
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from sklearn.inspection import permutation_importance

def ensure_dir(path: str):
    Path(path).mkdir(parents=True, exist_ok=True)

def compute_and_plot_permutation_importance(
    modelo,
    X_test_scaled: np.ndarray,
    y_test: np.ndarray,
    feature_names: list,
    out_dir: str,
    prefix: str = "permutation_importance",
    n_repeats: int = 10,
    random_state: int = 42,
    scoring: str = "accuracy",
    top_n: int = 10
):
    """
    Calcula a Permutation Importance (scoring por acurácia) e salva:
      - CSV: importâncias de todas as features
      - PNG: gráfico de barras (Top-N)
    """
    ensure_dir(out_dir)
    result = permutation_importance(
        modelo,
        X_test_scaled,
        y_test,
        n_repeats=n_repeats,
        random_state=random_state,
        scoring=scoring
    )

    importances_mean = result.importances_mean
    importances_std = result.importances_std

    df_imp = pd.DataFrame({
        "feature": feature_names,
        "importance_mean": importances_mean,
        "importance_std": importances_std
    }).sort_values("importance_mean", ascending=False)

    # Salvar CSV completo
    csv_path = os.path.join(out_dir, f"{prefix}.csv")
    df_imp.to_csv(csv_path, index=False, encoding="utf-8")

    # Plot Top-N
    top = df_imp.head(top_n).iloc[::-1]  # invertido p/ barra horizontal crescente
    plt.figure(figsize=(10, 6))
    plt.barh(top["feature"], top["importance_mean"], xerr=top["importance_std"])
    plt.xlabel("Permutation Importance (mean decrease in accuracy)")
    plt.ylabel("Atributo")
    plt.title("Top-{} Fatores mais relevantes (Permutation Importance)".format(top_n))
    plt.tight_layout()

    png_path = os.path.join(out_dir, f"{prefix}.png")
    plt.savefig(png_path, dpi=150)
    plt.close()

    # Retorno útil para logs ou testes automatizados
    return {
        "csv_path": csv_path,
        "png_path": png_path,
        "top_features": top[["feature", "importance_mean", "importance_std"]].iloc[::-1].to_dict(orient="records")  # volta à ordem desc
    }

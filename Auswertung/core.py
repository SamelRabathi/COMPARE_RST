import json
from pathlib import Path
from typing import Any, Dict, List

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from .config import load_config
from rst_functions import (
    discretize,
    indiscernibility,
    dependency,
    quick_reduct,
    induce_rules,
    compute_coverage,
)


# ---------------------------------------------------------------------------
# Helper: ensure NumPy objects become JSON-serializable
# ---------------------------------------------------------------------------
def _sanitize_for_json(obj: Any):
    import numpy as _np

    if isinstance(obj, (_np.integer,)):
        return int(obj)
    if isinstance(obj, (_np.floating,)):
        return float(obj)
    if isinstance(obj, (_np.bool_,)):
        return bool(obj)

    if isinstance(obj, _np.ndarray):
        return [_sanitize_for_json(x) for x in obj.tolist()]

    if isinstance(obj, dict):
        return {str(k): _sanitize_for_json(v) for k, v in obj.items()}

    if isinstance(obj, (list, tuple, set)):
        return [_sanitize_for_json(x) for x in obj]

    return obj


# ---------------------------------------------------------------------------
# Generic Run Dispatcher
# ---------------------------------------------------------------------------
def run(config_name: str) -> None:
    cfg = load_config(config_name)
    print(cfg)
    mode = cfg.get("mode", "student_two_datasets")

    if mode == "student_two_datasets":
        _run_student_two_datasets(cfg)
    elif mode == "single_dataset":
        _run_single_dataset(cfg)
    else:
        raise ValueError(f"Unbekannter mode='{mode}'")


# ---------------------------------------------------------------------------
# Student-Pipeline — 2 datasets (biased / unbiased)
# ---------------------------------------------------------------------------
def _run_student_two_datasets(cfg: Dict[str, Any]) -> None:
    out_cfg = cfg["output"]
    out_dir = Path(out_cfg["dir"])
    out_dir.mkdir(parents=True, exist_ok=True)
    prefix = out_cfg.get("prefix", "")

    biased_df = pd.read_csv(cfg["data"]["biased_csv"])
    unbiased_df = pd.read_csv(cfg["data"]["unbiased_csv"])

    decision_attr = cfg["decision_attribute"]
    bins = cfg.get("bins", 4)
    cutoffs = cfg.get("cutoffs", {})

    # Discretization
    biased = biased_df.drop(columns=[decision_attr])
    unbiased = unbiased_df.drop(columns=[decision_attr])

    biased_disc = discretize(biased, bins=bins, cutoffs=cutoffs)
    unbiased_disc = discretize(unbiased, bins=bins, cutoffs=cutoffs)

    biased_disc[decision_attr] = biased_df[decision_attr]
    unbiased_disc[decision_attr] = unbiased_df[decision_attr]

    # Optional Pass creation
    pass_grades = [pg for pg in cfg.get("pass_grades", []) if pg != ""]
    create_pass = cfg.get("create_pass", True)

    if create_pass and pass_grades:
        pass_grades_set = set(pass_grades)
        biased_disc["Pass"] = biased_df[decision_attr].isin(pass_grades_set).astype(int)
        unbiased_disc["Pass"] = unbiased_df[decision_attr].isin(pass_grades_set).astype(int)
    else:
        if "Pass" in biased_disc.columns:
            biased_disc.drop(columns=["Pass"], inplace=True, errors="ignore")
        if "Pass" in unbiased_disc.columns:
            unbiased_disc.drop(columns=["Pass"], inplace=True, errors="ignore")

    # Condition attributes
    exclude_attrs = cfg.get("exclude_attrs", [])
    cond_attrs_biased, cond_attrs_unbiased = [], []

    for col in biased_disc.columns:
        if col == decision_attr:
            continue
        if col.endswith("_disc") or biased_disc[col].dtype == "object" or str(biased_disc[col].dtype).startswith("category"):
            cond_attrs_biased.append(col)

    for col in unbiased_disc.columns:
        if col == decision_attr:
            continue
        if col.endswith("_disc") or unbiased_disc[col].dtype == "object" or str(unbiased_disc[col].dtype).startswith("category"):
            cond_attrs_unbiased.append(col)

    for col in exclude_attrs:
        cond_attrs_biased = [c for c in cond_attrs_biased if c != col]
        cond_attrs_unbiased = [c for c in cond_attrs_unbiased if c != col]

    ops = cfg.get("operations", {})
    results = {"biased": {}, "unbiased": {}}

    # ----------------- Grade-Reduct -------------------
    if ops.get("reduct_grade", False):
        results["biased"]["reduct_grade"], _ = quick_reduct(biased_disc, cond_attrs_biased, decision_attr)
        results["unbiased"]["reduct_grade"], _ = quick_reduct(unbiased_disc, cond_attrs_unbiased, decision_attr)

    # ----------------- Pass-Reduct --------------------
    if pass_grades and ops.get("reduct_pass", False):
        results["biased"]["reduct_pass"], _ = quick_reduct(biased_disc, cond_attrs_biased, "Pass")
        results["unbiased"]["reduct_pass"], _ = quick_reduct(unbiased_disc, cond_attrs_unbiased, "Pass")

    # ----------------- Grade-Rules --------------------
    if ops.get("rules_grade", False):
        results["biased"]["rules_grade"] = induce_rules(biased_disc, results["biased"].get("reduct_grade"), decision_attr)
        results["unbiased"]["rules_grade"] = induce_rules(unbiased_disc, results["unbiased"].get("reduct_grade"), decision_attr)

    # ----------------- Pass-Rules ---------------------
    if pass_grades and ops.get("rules_pass", False):
        results["biased"]["rules_pass"] = induce_rules(biased_disc, results["biased"].get("reduct_pass"), "Pass")
        results["unbiased"]["rules_pass"] = induce_rules(unbiased_disc, results["unbiased"].get("reduct_pass"), "Pass")

    # ----------------- Coverage -----------------------
    if ops.get("coverage_grade", False):
        results["biased"]["coverage_grade"] = compute_coverage(biased_disc, results["biased"]["reduct_grade"], decision_attr, results["biased"]["rules_grade"])
        results["unbiased"]["coverage_grade"] = compute_coverage(unbiased_disc, results["unbiased"]["reduct_grade"], decision_attr, results["unbiased"]["rules_grade"])

    if pass_grades and ops.get("coverage_pass", False):
        results["biased"]["coverage_pass"] = compute_coverage(biased_disc, results["biased"]["reduct_pass"], "Pass", results["biased"]["rules_pass"])
        results["unbiased"]["coverage_pass"] = compute_coverage(unbiased_disc, results["unbiased"]["reduct_pass"], "Pass", results["unbiased"]["rules_pass"])

    # ----------------- Save results -------------------
    # Redukte
    if out_cfg.get("save_reducts", True):
        out = {
            "biased": {
                "grade": results["biased"].get("reduct_grade"),
                "pass": results["biased"].get("reduct_pass"),
            },
            "unbiased": {
                "grade": results["unbiased"].get("reduct_grade"),
                "pass": results["unbiased"].get("reduct_pass"),
            },
        }
        with (out_dir / f"{prefix}reducts.json").open("w", encoding="utf-8") as f:
            json.dump(_sanitize_for_json(out), f, ensure_ascii=False, indent=2)

    # Regeln
    if out_cfg.get("save_rules", True):
        out = {
            "biased": {
                "grade": results["biased"].get("rules_grade"),
                "pass": results["biased"].get("rules_pass"),
            },
            "unbiased": {
                "grade": results["unbiased"].get("rules_grade"),
                "pass": results["unbiased"].get("rules_pass"),
            },
        }
        with (out_dir / f"{prefix}rules.json").open("w", encoding="utf-8") as f:
            json.dump(_sanitize_for_json(out), f, ensure_ascii=False, indent=2)

    # Coverage
    if out_cfg.get("save_coverage", True):
        out = {
            "biased": results["biased"],
            "unbiased": results["unbiased"],
        }
        with (out_dir / f"{prefix}coverage.json").open("w", encoding="utf-8") as f:
            json.dump(_sanitize_for_json(out), f, ensure_ascii=False, indent=2)

    # PDF Coverage Plot 
    if ops.get("plots", False) and out_cfg.get("save_plots", True):
        # Plot Grade-Coverage falls vorhanden
        if "coverage_grade" in results["biased"] and "coverage_grade" in results["unbiased"]:
            vals = [
                results["biased"]["coverage_grade"] * 100,
                results["unbiased"]["coverage_grade"] * 100
            ]
            labels = ["Biased (Grade)", "Unbiased (Grade)"]
    
            plt.figure()
            x = np.arange(len(labels))
            plt.bar(x, vals)
            plt.xticks(x, labels, rotation=10)
            plt.ylabel("Coverage [%]")
            plt.title("Coverage für Decision-Attribut (Grade)")
    
            for i, v in enumerate(vals):
                plt.text(i, v + 1, f"{v:.1f}%", ha="center")
    
            plt.ylim(0, 100)
            plt.tight_layout()
            plt.savefig(out_dir / f"{prefix}coverage_grade.pdf")
            plt.close()
    
        # Plot Pass-Coverage falls vorhanden
        if "coverage_pass" in results["biased"] and "coverage_pass" in results["unbiased"]:
            vals = [
                results["biased"]["coverage_pass"] * 100,
                results["unbiased"]["coverage_pass"] * 100
            ]
            labels = ["Biased (Pass)", "Unbiased (Pass)"]
    
            plt.figure()
            x = np.arange(len(labels))
            plt.bar(x, vals)
            plt.xticks(x, labels, rotation=10)
            plt.ylabel("Coverage [%]")
            plt.title("Coverage für Pass-Attribut")
    
            for i, v in enumerate(vals):
                plt.text(i, v + 1, f"{v:.1f}%", ha="center")
    
            plt.ylim(0, 100)
            plt.tight_layout()
            plt.savefig(out_dir / f"{prefix}coverage_pass.pdf")
            plt.close()


# ---------------------------------------------------------------------------
# Generic Single-Dataset Pipeline
# ---------------------------------------------------------------------------
def _run_single_dataset(cfg: Dict[str, Any]) -> None:
    out_cfg = cfg["output"]
    out_dir = Path(out_cfg["dir"])
    out_dir.mkdir(parents=True, exist_ok=True)
    prefix = out_cfg.get("prefix", "")
    
    # Load data
    data_cfg = cfg["data"]
    file_type = data_cfg.get("file_type", "csv")
    df = pd.read_csv(data_cfg["file"]) if file_type == "csv" else pd.read_parquet(data_cfg["file"])

    decision_attr = cfg["decision_attribute"]
    bins = cfg.get("bins", 4)
    cutoffs = cfg.get("cutoffs", {})

    # Categorical handling
    for col in data_cfg.get("categorical_definite", []):
        if col in df.columns:
            df[col] = df[col].astype("category")
    for col in data_cfg.get("categorical_optional", []):
        if col in df.columns:
            df[col] = df[col].astype("category")

    # Discretization
    X = df.drop(columns=[decision_attr])
    df_disc = discretize(X, bins=bins, cutoffs=cutoffs)
    df_disc[decision_attr] = df[decision_attr]

    # Optional Pass creation
    pass_grades = [pg for pg in cfg.get("pass_grades", []) if pg != ""]
    create_pass = cfg.get("create_pass", True)

    if create_pass and pass_grades:
        pass_set = set(pass_grades)
        df_disc["Pass"] = df[decision_attr].isin(pass_set).astype(int)

    # Condition attributes
    cond_attrs = []
    for col in df_disc.columns:
        if col == decision_attr: continue
        if col.endswith("_disc") or df_disc[col].dtype == "object" or str(df_disc[col].dtype).startswith("category"):
            cond_attrs.append(col)
    for col in cfg.get("exclude_attrs", []):
        cond_attrs = [c for c in cond_attrs if c != col]

    ops = cfg.get("operations", {})
    results = {}

    # Redukt Decision
    if ops.get("reduct", False):
        results["reduct"], _ = quick_reduct(df_disc, cond_attrs, decision_attr)

    # Rules Decision
    if ops.get("rules", False):
        results["rules"] = induce_rules(df_disc, results["reduct"], decision_attr)

    # Coverage Decision
    if ops.get("coverage", False):
        results["coverage"] = compute_coverage(df_disc, results["reduct"], decision_attr, results["rules"])

    # Pass Redukt/Rules/Coverage (optional)
    if pass_grades:
        if ops.get("reduct_pass", False):
            results["reduct_pass"], _ = quick_reduct(df_disc, cond_attrs, "Pass")
        if ops.get("rules_pass", False):
            results["rules_pass"] = induce_rules(df_disc, results["reduct_pass"], "Pass")
        if ops.get("coverage_pass", False):
            results["coverage_pass"] = compute_coverage(df_disc, results["reduct_pass"], "Pass", results["rules_pass"])

    # Save output
    if out_cfg.get("save_reducts", True):
        with (out_dir / f"{prefix}reduct.json").open("w", encoding="utf-8") as f:
            json.dump(_sanitize_for_json(results), f, ensure_ascii=False, indent=2)

    # PDF-Coverage Plot (Single Dataset)
    if ops.get("plots", False) and out_cfg.get("save_plots", True):
        # Decision Coverage
        if "coverage" in results:
            val = results["coverage"] * 100
            plt.figure()
            plt.bar([0], [val])
            plt.xticks([0], [decision_attr], rotation=10)
            plt.ylabel("Coverage [%]")
            plt.title(f"Coverage für Decision-Attribut ({decision_attr})")
            plt.text(0, val + 1, f"{val:.1f}%", ha="center")
            plt.ylim(0, 100)
            plt.tight_layout()
            plt.savefig(out_dir / f"{prefix}coverage_decision.pdf")
            plt.close()
    
        # Pass Coverage falls aktiviert
        if "coverage_pass" in results:
            val = results["coverage_pass"] * 100
            plt.figure()
            plt.bar([0], [val])
            plt.xticks([0], ["Pass"], rotation=10)
            plt.ylabel("Coverage [%]")
            plt.title("Coverage für generiertes Pass-Label")
            plt.text(0, val + 1, f"{val:.1f}%", ha="center")
            plt.ylim(0, 100)
            plt.tight_layout()
            plt.savefig(out_dir / f"{prefix}coverage_pass.pdf")
            plt.close()


    print("\n=== Ergebnisse ===")
    if "reduct" in results:
        print(f"\nRedukt:\n{results['reduct']}")
    if "rules" in results:
        print(f"\nRegeln: {len(results['rules'])}")
    if "coverage" in results:
        print(f"Coverage: {results['coverage']}")

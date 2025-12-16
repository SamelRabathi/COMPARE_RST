from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any, Dict


# Ein gemeinsamer Default für ALLE Konfigurationen
DEFAULT_CONFIG: Dict[str, Any] = {
    # - "student_two_datasets": biased/unbiased-Studentendaten
    # - "single_dataset": ein einzelner Datensatz (Crimes, Heart Failure, ...) anzunehmen, dass dies mehr genutzt wird.
    "mode": "student_two_datasets",

    # Daten zum Studenten-Setup (werden in single_dataset-Mode einfach ignoriert)
    "data": {
        "biased_csv": "./Student_Performance_Behavior_Dataset/Students_Grading_Dataset_Biased.csv",
        "unbiased_csv": "./Student_Performance_Behavior_Dataset/Students_Performance_Dataset.csv",

        # Generische Angaben für single_dataset
        "file": "./data.csv",
        "file_type": "csv",
        "categorical_definite": [],
        "categorical_optional": []
    },

    # Generisches Entscheidungsattribut (bei Studenten = "Grade", bei anderen Datensätzen etwas anderes, z.B. "Weapon Used Cd" oder "HeartDisease").
    "decision_attribute": "Grade",

    # Diskretisierung (Werden standardmäßig mit 4 bins und cutoffs = {} belegt)
    "bins": 4,
    "cutoffs": {},

    # Generisches Pass-Handling:
    # - wenn pass_grades leer ist -> kein Pass-Attribut
    # - wenn pass_grades gefüllt -> Pass-Attribut wird angelegt
    "create_pass": True,
    "pass_grades": [],  # z.B. ["A", "B", "C", "D"] für Studenten

    # Spalten, die nicht als Konditionsattribute dienen sollen
    "exclude_attrs": [],

    # Ein gemeinsamer Operations-Block:
    # - die *_grade-Keys werden nur im Studenten-Setup benutzt
    # - die *ohne grade / mit pass-Keys sind generisch & werden
    #   sowohl im Studenten- als auch im Single-Dataset-Setup
    #   verwendet, wenn sinnvoll.
    "operations": {
        # Studenten-spezifische "Grade"-Auswertung (zwei Datensätze)
        "reduct_grade": True,
        "rules_grade": True,
        "coverage_grade": True,

        # Pass-Auswertung (generisch: Studenten UND andere Datensätze möglich)
        "reduct_pass": False,
        "rules_pass": False,
        "coverage_pass": False,
        "indiscernibility_pass": False,

        # Single-Dataset generische Auswertung mit decision_attribute
        "reduct": True,
        "rules": True,
        "indiscernibility": False,
        "coverage": True,

        # Plots allgemein
        "plots": True
    },

    "output": {
        "dir": "./auswertung_results",
        "prefix": "",
        "save_intermediate_disc": False,
        "save_reducts": True,
        "save_rules": True,
        "save_indiscernibility": False,
        "save_coverage": True,
        "save_plots": True,
        "overwrite": True,
    },
}


def _deep_update(base: Dict[str, Any], updates: Dict[str, Any]) -> Dict[str, Any]:
    """Rekursives dict-update: Werte aus `updates` überschreiben `base`."""
    result = deepcopy(base)
    for k, v in updates.items():
        if isinstance(v, dict) and isinstance(result.get(k), dict):
            result[k] = _deep_update(result[k], v)
        else:
            result[k] = v
    return result


def load_config(config_name: str) -> Dict[str, Any]:
    """
    Lädt eine Konfiguration.

    Regeln:
    - Wenn `config_name` ein existierender Pfad ist, wird diese Datei verwendet.
    - Sonst wird nach `configs/{config_name}.json` relativ zum Paket gesucht.
    """
    cfg_path = Path(config_name)
    if not cfg_path.is_file():
        pkg_root = Path(__file__).resolve().parent
        cfg_dir = pkg_root / "configs"
        candidate = cfg_dir / f"{config_name}.json"
        if candidate.is_file():
            cfg_path = candidate
        else:
            raise FileNotFoundError(
                f"Keine Konfigurationsdatei gefunden unter '{config_name}' "
                f"oder '{candidate}'."
            )

    with cfg_path.open("r", encoding="utf-8") as f:
        user_cfg = json.load(f)

    return _deep_update(DEFAULT_CONFIG, user_cfg)

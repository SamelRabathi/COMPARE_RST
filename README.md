# COMPARE_RST

# Rough Set Analyse Toolkit (RST) für COMPARE

## 1. Projektbeschreibung
Dieses Projekt analysiert Datensätze mithilfe der **Rough-Set-Theorie (Pawlak)**.
Es dient zum **Berechnen von Redukten, Regeln, Coverage** und optional zur
**Visualisierung als PDF-Plots**.

Das System ist vollständig **konfigurationsbasiert** — neue Datensätze werden
über JSON-Dateien beschrieben, ohne dass Code angepasst werden muss.

Einsatz im Rahmen von:
*Masterarbeit [Erweiterung und Optimierung von Äquivalenzrelationen für Rough Set basierte Klassifikationsverfahren] als Bestandteil des Projektes "COMPARE"*  

---

## 2. Features
✔ Studenten-Pipeline: biased vs. unbiased Vergleich  
✔ Einzel-Datensatz-Analyse (Crimes, Heart Failure, beliebige Daten)  
✔ Generisches Pass-Label (aktivierbar/abschaltbar über `pass_grades`)  
✔ Diskretisierung mit automatisch oder benutzerdefiniertem Cutoff  
✔ Export von **Redukten**, **Regeln**, **Coverage**, **PDF-Plots**  
✔ Einheitliche JSON-Struktur für *alle* Datensätze  

---

## 3. Installation


```bash```
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install "numpy<2" pandas matplotlib

---

## 4. Projektstruktur


Projekt/
│── Auswertung/
│   ├── core.py          # Pipeline Logik (Students + Single-Dataset)
│   ├── config.py        # JSON Loader + Defaults
│   ├── configs/         # Beispiel-Konfigurationen
│   │   ├── students_behavior.json
│   │   ├── crimes.json
│   │   └── heart_failure.json
│── rst_functions.py     # Quick Reduct, Rules, Coverage...
│── README.md            # Dieses Dokument
│── Daten/               # Datensätze (Beispiele)

---

## 5. Nutzung


python -m Auswertung <config_name>

#### Beispiele:

'''
python -m Auswertung students_behavior
python -m Auswertung crimes
python -m Auswertung heart_failure
'''

---


## 6. JSON-Konfiguration

ALLE Configs haben dieselbe Struktur
→ mode, data, decision_attribute, create_pass, operations, output


{
  "mode": "student_two_datasets | single_dataset",

  "data": {
    "biased_csv": "...",
    "unbiased_csv": "...",
    "file": "...",
    "file_type": "csv | parquet",
    "categorical_definite": [],
    "categorical_optional": []
  },

  "decision_attribute": "grade / target / class",
  "bins": 4,
  "cutoffs": {},

  "create_pass": true,
  "pass_grades": [],

  "exclude_attrs": [],

  "operations": {
    "reduct": true,
    "rules": true,
    "coverage": true,
    "plots": true,
    "reduct_pass": false,
    "rules_pass": false,
    "coverage_pass": false
  },

  "output": {
    "dir": "./results",
    "save_reducts": true,
    "save_rules": true,
    "save_plots": true
  }
}

---


## 7. Beispiele:

##### Studenten-Vergleich
```
python -m Auswertung students_behavior
```
erstellt:
```
results_students/
 ├ reducts.json
 ├ rules.json
 ├ coverage.json
 ├ coverage_grade.pdf
 ├ coverage_pass.pdf
```

---


## 8. Output-Interpretation

| Datei           | Inhalt                         |
| --------------- | ------------------------------ |
| `reduct.json`   | minimale Merkmalsmenge         |
| `rules.json`    | induzierte Entscheidungsregeln |
| `coverage.json` | Abdeckung (%) der Regeln       |
| `.pdf`-Plots    | Coverage-Visualisierung        |

---

## 9. Hinweise

pass_grades = [] → Pass-Label deaktiviert

Größere Datensätze → Coverage dauert länger

PDF-Plots nur wenn aktiviert:
operations.plots = true && output.save_plots = true

---


## 10. Weiterentwicklungsideen

Batch-Runs über mehrere Configs

GUI/Web-Dashboard

Auto-Report-Generator (PDF)

Vergleich von Diskretisierungsmethoden

Regel-Ranking + Feature-Scoring

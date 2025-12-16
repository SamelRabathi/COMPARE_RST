# COMPARE_RST  
# Rough Set Analyse Toolkit (RST) für COMPARE

## 1. Projektbeschreibung
Dieses Projekt analysiert Datensätze mithilfe der **Rough-Set-Theorie (Pawlak)**.
Es dient zur **Berechnung von Redukten, Entscheidungsregeln, Coverage-Werten**
und unterstützt zusätzlich deren **Visualisierung über PDF-Plots**.

Das System ist vollständig **konfigurationsbasiert** – neue Datensätze werden
ausschließlich über JSON-Dateien eingebunden.  
Codeanpassungen sind nicht notwendig.

> Einsatz im Rahmen der Masterarbeit  
> **„Erweiterung und Optimierung von Äquivalenzrelationen für Rough Set basierte Klassifikationsverfahren“**  
> im Projekt **COMPARE**

---

## 2. Features

```
✔ Bei Kaggel-Daten auf Reduzierung der Redukte und anderen Erkenntnissen der RST untersuchen: 
    * Studenten-Pipeline: Vergleich **biased vs. unbiased**  
    * generische **Single-Dataset Analyse** (Crimes, Heart Failure, beliebige Daten)  
✔ **Pass-Label Support** über `pass_grades` aktivierbar/deaktivierbar  
✔ automatische oder manuelle **Diskretisierung**  
✔ exportiert **Redukte**, **Regeln**, **Coverage**, **Plots als PDF**  
✔ **einheitliche JSON-Struktur** für alle Datensätze  
```

---

## 3. Installation

```bash:```
```
$ python3 -m venv .venv
$ source .venv/bin/activate        # Linux/macOS - Für Windows: .venv\Scripts\Activate.ps1
$ pip install --upgrade pip
$ pip install --upgrade -r requirements.txt
```

---

## 4. Projektstruktur

```text
Projekt/
│── Auswertung/
│   ├── core.py          # Pipeline Logik (Studenten & Single-Dataset)
│   ├── config.py        # JSON-Lader + Default Parameter
│   ├── configs/         # Beispiel-Konfigurationen
│   │   ├── students_behavior.json
│   │   ├── crimes.json
│   │   └── heart_failure.json
│── rst_functions.py     # Algorithmen (Reduct, Rules, Coverage, ...)
│── README.md            # Dieses Dokument
│── Daten/               # Datensätze (außer die werden sow´fort von einer externen Quelle geladen)
```

---

## 5. Nutzung

```python -m Auswertung <config_name>```

#### Beispiele:

```text
* python -m Auswertung students_behavior
* python -m Auswertung crimes
* python -m Auswertung heart_failure
```

---

## 6. JSON-Konfiguration

Alle Configs besitzen dasselbe Schema:
    → mode, data, decision_attribute, create_pass, operations, output...

```text
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
```

---

## 7. Beispiele:

##### Studenten-Vergleich
```python -m Auswertung students_behavior```

Erstellt im Ordner ```./results/``` den Ordner ```results_students/``` mit folgendem Aufbau:

```text
results_students/
├── reducts.json          # Redukte
├── rules.json            # Ableitungsregeln
├── coverage.json         # Abdeckung wie viel Prozent durch Regeln bestimmt werden kann
├── coverage_grade.pdf    # Prozente zu Noten
├── coverage_pass.pdf     # Prozente zu Bestehen
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

* pass_grades = [] → Pass-Label deaktiviert

* Größere Datensätze → Coverage dauert länger*

* PDF-Plots nur wenn aktiviert:
    * operations.plots = true && output.save_plots = true

---

## 10.  Weiterentwicklungsideen

Batch-Runs über mehrere Configs

GUI/Web-Dashboard

Auto-Report-Generator (PDF)

Vergleich von Diskretisierungsmethoden

Regel-Ranking + Feature-Scoring

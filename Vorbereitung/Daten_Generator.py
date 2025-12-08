# Importe
import csv
import multiprocessing
import random

import pandas as pd


# Dateien laden
prof_liste = "CSVs/dozents.csv"
df_prof = pd.read_csv(prof_liste)
num_prof = len(df_prof)
print(f"Anzahl an Dozenten (profs): {num_prof}.")

lv_liste = "CSVs/lehrveranstaltungen.csv"
df_lv = pd.read_csv(lv_liste)
num_lv = len(df_lv)
print(f"Anzahl an Lehrveranstaltungen (LVs): {num_lv}.")

kategorien_liste = "CSVs/Bewertungskategorien.csv"
df_kategorien = pd.read_csv(kategorien_liste)
num_kategorien = len(df_kategorien)
print(f"Anzahl an Kategorien: {num_kategorien}.\n")


# Funktionen
def csv_generator(num_stud:int=10000, num_min_eval:int=2, num_max_eval:int=5, prof_path:str = 'simulated_prof_data.csv', lv_path:str = 'simulated_lv_data.csv') -> None:
    """
    Hier wird eine CSV generiert, wo zufälige Antworten von Studenten eingetragen werden. Dies soll dazu dienen, damit vor Durchführung der Befragungen/Evaluation zumindest die Funktionen erstellt werden kann. 
    Input:
        num_stud: int = Representiert die Anzahl an Studenten, die am Fragebogen teilgenommen haben.
        num_min_eval: int = Beschreibt die Mindestanzahl an Bewertungen, die ein Student schreibt. (untere Schranke im Sinne von "[")
        num_max_eval: int = Beschreibt die maximale Anzahl an Bewertungen, die ein Student schreibt. (obere Schranke im Sinne von "]")
        prof_path: str = Der Ablagepfad für die Werte der Professoren.
        lv_path: str = Der Ablagepfad für die Werte der Lehrveranstalltungen.
    """
    # Zahlenbereich für Dozenten von 0 bis Dozenten-Anzahl / für LV von 0 bis LV-Anzahl
    prof_bereich = list(range(0, num_prof))
    lv_bereich = list(range(0, num_lv))
    
    with open(prof_path, mode='w', newline='') as file, open(lv_path, mode='w', newline='') as file2:
        prof_file = csv.writer(file)
        lv_file = csv.writer(file2)
        
        # Schreibe die Spaltennamen
        prof_file.writerow(["studentId", "kriteriumId", "lesserComparableId", "greaterComparableId"])
        lv_file.writerow(["studentId", "kriteriumId", "lesserComparableId", "greaterComparableId"])

        for student in range(num_stud):
            # Jeder Student:In nimmt eine zufällige Anzahl an Bewertungen standardmäßig zwischen 2 und 5 vor. (Ist per Uebergabe aenderbar)
            anzahl_bewertungen = random.randint(num_min_eval, num_max_eval)

            # Die Profs und LVs werden über die Kategorien hinweg verglichen.
            # Annahme: Dozenten, die eine Vorlesung halten, halten ueblicherweise auch eineUebung. 
            for kategorie in range(0, num_kategorien):
                
                # Zufällige Auswahl von Profs und zufällige Reihenfolge
                ausgewaehlte_profs = random.sample(prof_bereich, anzahl_bewertungen)
                random.shuffle(ausgewaehlte_profs)

                for prof in range(len(ausgewaehlte_profs)-1):
                    prof_file.writerow([student+1, kategorie, ausgewaehlte_profs[prof], ausgewaehlte_profs[prof + 1]])

                # Zufällige Auswahl von LVs und zufällige Reihenfolge
                ausgewaehlte_lvs = random.sample(lv_bereich, anzahl_bewertungen)
                random.shuffle(ausgewaehlte_lvs)

                for lv in range(len(ausgewaehlte_lvs)-1):
                    lv_file.writerow([student+1, kategorie, ausgewaehlte_lvs[lv], ausgewaehlte_lvs[lv + 1]])
                
                # Ausgabe der zufälligen Listen
                #print(ausgewaehlte_profs)
                #print(ausgewaehlte_lvs)

    df = pd.read_csv(prof_path)
    num_rows = len(df)
    print("Anzahl an generierten Dozenten-Daten:", num_rows)
    print(df)

    df = pd.read_csv(lv_path)
    num_rows = len(df)
    print("Anzahl an generierten LV-Daten:", num_rows)
    print(df)

unterordner = "CSVs/data_generated/splitted/"
csv_generator(num_stud=20000, num_min_eval=3, num_max_eval=7, prof_path=f"{unterordner}simulierte_Dozenten_Ergebnisse.csv", lv_path=f"{unterordner}simulierte_LV_Ergebnisse.csv")

"""
    1. Modul- und Bibliothek-Importe
"""
import random

import multiprocessing as mp
import numpy as np
import pandas as pd



"""
    2. Globale Konstanten (falls vorhanden)
"""

""" Notwendige Dateien global laden """
# Für die Anzahl an LV.
LV_liste = "CSVs/lehrveranstaltungen.csv"
df_LV = pd.read_csv(LV_liste)
num_LV = len(df_LV)
    
# Für die Anzahl an LP.
LP_liste = "CSVs/dozents.csv"
df_LP = pd.read_csv(LP_liste)
num_LP = len(df_LP)

# Für die Anzahl an Bewertungskriterien, damit dies auch nach Anpassung bzw. Erweiterung sic mit aendert.
kategorien_liste = "CSVs/Bewertungskategorien.csv"
df_kategorien = pd.read_csv(kategorien_liste)
num_kategorien = len(df_kategorien)

# Ergebnisse der Umfragen zu den Lehrveranstalltungen. (derzeitig simuliert)
pfad_simulierte_LV_Ergebnisse = "CSVs/data_generated/splitted/simulierte_LV_Ergebnisse.csv"
df_LV = pd.read_csv(pfad_simulierte_LV_Ergebnisse)
num_rows_LV = len(df_LV)

# Ergebnisse der Umfragen zu den Lehrpersonen/Dozenten. (derzeitig simuliert)
pfad_simulierte_LP_Ergebnisse = "CSVs/data_generated/splitted/simulierte_Dozenten_Ergebnisse.csv"
df_LP = pd.read_csv(pfad_simulierte_LP_Ergebnisse)
num_rows_LP = len(df_LP)

LV_Grupierung = 0
LP_Grupierung = 0



"""
    3. Hilfsfunktionen (Utility Functions)
"""
def gruppieren(df:pd.DataFrame, Kategorien:pd.DataFrame, df_name:str="Kein Name vergeben!!!") -> dict:
    """
    
    """
    
    if 'kriteriumId' in df.columns:
        print(f"Gruppierung erfolgreich durchgeführt nach: {df_name}\n")
        return {k: v for k, v in df.groupby('kriteriumId')}
    
    print("Spalte 'kriteriumId' nicht gefunden. Keine Gruppierung durchgeführt.")
    return {}


def matrix_erstellen(df:pd.DataFrame, matrix_laenge:int=10) -> np.array:
    """
    
    """
    
    matrix = np.zeros((matrix_laenge, matrix_laenge))
    for index, row in df.iterrows():
        value_lower = row['lesserComparableId']
        value_greater = row['greaterComparableId']
        
        matrix[value_lower, value_greater] += 1
    
    return matrix


def Vorlage()->None:

    
    return None


def export_der_Gruppierung(Gruppierung:pd.DataFrame, Bewertungsbezug:str="", Kategorie:str="", Kategorie_Lauf:int=0, Matrix_groesse:int=10) -> str:
    """
    
    """
    print(f"{Kategorie_Lauf}. Kategorie: {Bewertungsbezug} - {Kategorie}")
    #print(f"{Gruppierung}\n\n")
    
    matrix=matrix_erstellen(Gruppierung, Matrix_groesse)
    
    # Matrix als CSV speichern
    # np.savetxt(f"Ergebnisse/{Bewertungsbezug}_{Kategorie}.csv", matrix, delimiter=',', fmt='%d')
    np.savetxt(f"CSVs/data_generated/{Bewertungsbezug}_{Kategorie}.csv", matrix, delimiter=',', fmt='%d')
    return f"{Bewertungsbezug}_{Kategorie}.csv gespeichert."


def export_pro_kategorie(kategorie):
    """
    Führt die beiden export_der_Gruppierung-Aufrufe für eine Kategorie aus.
    """
    export_der_Gruppierung(
        Gruppierung=LV_Grupierung[kategorie],
        Bewertungsbezug="LV",
        Kategorie=df_kategorien.loc[kategorie]['Kriterium'],
        Kategorie_Lauf=kategorie+1,
        Matrix_groesse=num_LV
    )
    
    export_der_Gruppierung(
        Gruppierung=LP_Grupierung[kategorie],
        Bewertungsbezug="LP",
        Kategorie=df_kategorien.loc[kategorie]['Kriterium'],
        Kategorie_Lauf=kategorie+1,
        Matrix_groesse=num_LP
    )



"""
    4. Hauptfunktionen (Main Functions)
"""
def main():
    
    """ Notwendige Dateien laden """
    print(f"Anzahl an Kategorien: {num_kategorien}.\n")
    
    print("Anzahl an Daten:", num_rows_LV)
    print(df_LV)
    
    print("Anzahl an Daten:", num_rows_LP)
    print(df_LP)
    
    print("Anzahl an LP:", num_LP)
    print("Anzahl an LV:", num_LV)

    # Unterteilung der DataFrames in den einzelnen Kategorien
    global LV_Grupierung
    global LP_Grupierung
    LV_Grupierung = gruppieren(df=df_LV, Kategorien=df_kategorien, df_name="Lehrveranstalltungen")
    LP_Grupierung = gruppieren(df=df_LP, Kategorien=df_kategorien, df_name="Dozenten")
    
    # Anzahl der verfügbaren CPU-Kerne
    num_kerne = mp.cpu_count()
    
    # Erstelle einen Pool von Prozessen
    with mp.Pool(processes=num_kerne) as pool:
        pool.map(export_pro_kategorie, range(num_kategorien))



"""
    5. Skript-Startpunkt
"""
if __name__ == "__main__":
    main()

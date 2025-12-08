"""
Hier geht es um die Erstellung von CSV Datei in denen die Bewertungskategorien für Dozenten und Kategorien erstellt und unter CSVs abgelegt werden.

AKTUELL: Dozenten und Lehrveranstalltung haben die selben Kategrorien bzw. sind die in meinen Augen vermischt.
=> Beispiele:
    Praxisbezug:
        Betrifft sowohl Dozent als auch Vorlesung, denn so Praxisfern die Vorlesung sein mag, liegt die Herleitung zur Praxis in den Händen des Dozenten.
    Selbsteinschätzung:
        Sollte nur für den Dozent bestimmt sein.
    Technikqualität/Videoqualität:
        Je nach auslegung der Frage.
"""

# Importe
import pandas as pd
import os

# Das sind die Bewertungskategorien für Dozenten und Lehrveranstaltung
Bewertungskategorien = {
    'Nummer': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11],
    'Buchstabe': ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'K', 'L'],
    'Kriterium': ['Technikqualität', 'Praxisbezug', 'Materialqualität', 'Methoden', 'Gesamteindruck', 'Selbsteinschätzung', 'LEA Gestaltung', 'Beteiligungsmöglichkeit', 'Verständlichkeit', 'Atmosphäre', 'Videoqualität']
}

Bewertungskategorien_df = pd.DataFrame(Bewertungskategorien)

# Display the DataFrame
print(Bewertungskategorien_df)

# Export the DataFrame to a CSV file
try:
    current_path = os.path.dirname(os.path.abspath(__file__)) if '__file__' in locals() else os.getcwd()
    csv_file_path = os.path.join(current_path, r"CSVs/Bewertungskategorien.csv")

except:
    csv_file_path = r"/home/samel/01. Projekte/01. Master/Projekt/CSVs/Bewertungskategorien.csv"

try:
    Bewertungskategorien_df.to_csv(csv_file_path, index=False)
    print(f"DataFrame has been exported as '{csv_file_path}'.")
    
except:
    print(f"Folgenden Pfad scheint es nich nicht zu geben: '{csv_file_path}'.")

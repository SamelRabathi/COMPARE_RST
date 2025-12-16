import csv
import random
import multiprocessing

# Konfigurierbare Parameter
file_path = r"/home/samel/01. Projekte/01. Master/Projekt/output.csv"
num_stud = 100  # Anzahl der Studenten
num_min_eval = 2  # Mindestanzahl Bewertungen pro Student
num_max_eval = 5  # Maximalanzahl Bewertungen pro Student
num_kategorien = 3  # Anzahl der Kategorien
prof_bereich = ['ProfA', 'ProfB', 'ProfC', 'ProfD']
lv_bereich = ['LVA', 'LVB', 'LVC', 'LVD']

# Funktion für die Bewertung eines einzelnen Studenten
def process_student(student):
    rows = []
    anzahl_bewertungen = random.randint(num_min_eval, num_max_eval)
    
    for kategorie in range(num_kategorien):
        # Zufällige Auswahl und Reihenfolge der Profs
        ausgewaehlte_profs = random.sample(prof_bereich, anzahl_bewertungen)
        random.shuffle(ausgewaehlte_profs)
        
        for prof in range(len(ausgewaehlte_profs) - 1):
            rows.append([student + 1, kategorie, ausgewaehlte_profs[prof], ausgewaehlte_profs[prof + 1]])
        
        # Zufällige Auswahl und Reihenfolge der LVs
        ausgewaehlte_lvs = random.sample(lv_bereich, anzahl_bewertungen)
        random.shuffle(ausgewaehlte_lvs)
        
        for lv in range(len(ausgewaehlte_lvs) - 1):
            rows.append([student + 1, kategorie, ausgewaehlte_lvs[lv], ausgewaehlte_lvs[lv + 1]])
    
    return rows

# Hauptfunktion für die parallele Verarbeitung
def main():
    with open(file_path, mode='w', newline='') as file:
        writer = csv.writer(file)
        
        # Schreibe die Spaltennamen
        writer.writerow(["studentId", "kriteriumId", "lesserComparableId", "greaterComparableId"])
        
        # Starte parallele Verarbeitung
        with multiprocessing.Pool(processes=multiprocessing.cpu_count()) as pool:
            results = pool.map(process_student, range(num_stud))
        
        # Schreibe die Ergebnisse in die Datei
        for rows in results:
            writer.writerows(rows)

main()

# --------------------------------------------------------------------------------------------------------
import numpy as np

def is_reflexive(matrix):
    """Prüft, ob die Matrix reflexiv ist."""
    return all(matrix[i][i] == 1 for i in range(len(matrix)))

def is_symmetric(matrix):
    """Prüft, ob die Matrix symmetrisch ist."""
    return all(matrix[i][j] == matrix[j][i] for i in range(len(matrix)) for j in range(len(matrix)))

def is_transitive(matrix):
    """Prüft, ob die Matrix transitiv ist."""
    size = len(matrix)
    for i in range(size):
        for j in range(size):
            for k in range(size):
                if matrix[i][j] and matrix[j][k] and not matrix[i][k]:
                    return False
    return True

def check_equivalence_relation(matrix):
    """Prüft, ob eine gegebene m*m Matrix eine Äquivalenzrelation darstellt."""
    if is_reflexive(matrix) and is_symmetric(matrix) and is_transitive(matrix):
        return True
    return False

# Beispiel
matrix = np.array([
    [1, 1, 0],
    [1, 1, 0],
    [0, 0, 1]
])

if check_equivalence_relation(matrix):
    print("Die gegebene Matrix stellt eine Äquivalenzrelation dar.")
else:
    print("Die gegebene Matrix stellt keine Äquivalenzrelation dar.")
# --------------------------------------------------------------------------------------------------------



import itertools
import numpy as np

def is_reflexive(matrix):
    """Prüft, ob die Matrix reflexiv ist."""
    return all(matrix[i][i] == 1 for i in range(len(matrix)))

def is_symmetric(matrix):
    """Prüft, ob die Matrix symmetrisch ist."""
    return all(matrix[i][j] == matrix[j][i] for i in range(len(matrix)) for j in range(len(matrix)))

def is_transitive(matrix):
    """Prüft, ob die Matrix transitiv ist."""
    size = len(matrix)
    for i in range(size):
        for j in range(size):
            for k in range(size):
                if matrix[i][j] and matrix[j][k] and not matrix[i][k]:
                    return False
    return True

def find_equivalence_relations(m):
    """Finde alle äquivalenten Relationen für eine m*m Matrix."""
    size = m * m
    equivalence_matrices = []
    
    for binary in itertools.product([0, 1], repeat=size):
        matrix = np.array(binary).reshape((m, m))
        if is_reflexive(matrix) and is_symmetric(matrix) and is_transitive(matrix):
            equivalence_matrices.append(matrix)
    
    return equivalence_matrices

# Beispiel
m = 3
equivalence_relations = find_equivalence_relations(m)
print(f"Anzahl äquivalenter Relationen für eine {m}x{m}-Matrix: {len(equivalence_relations)}")
for idx, matrix in enumerate(equivalence_relations):
    print(f"Matrix {idx+1}:")
    print(matrix)

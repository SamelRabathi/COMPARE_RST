import pandas as pd
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt

# Datei laden
df = pd.read_csv('Ergebnisse/LP_Verständlichkeit.csv', index_col=0)

# Überprüfen, ob die Matrix quadratisch ist
if df.shape[0] != df.shape[1]:
    raise ValueError("Die Matrix ist nicht quadratisch. Bitte stellen Sie sicher, dass m x m gegeben ist.")

# Sicherstellen, dass Index und Spalten identisch sind
df = df.loc[df.index.intersection(df.columns), df.columns.intersection(df.index)]

# Äquivalenzrelation prüfen: Reflexivität, Symmetrie und Transitivität

def ist_reflexiv(matrix):
    for i in range(len(matrix)):
        if matrix.iloc[i, i] != 0:
            return False
    return True

def ist_symmetrisch(matrix):
    return (matrix.sort_index(axis=0).sort_index(axis=1) == matrix.T.sort_index(axis=0).sort_index(axis=1)).all().all()

def ist_transitiv(matrix):
    m = len(matrix)
    for i in range(m):
        for j in range(m):
            for k in range(m):
                if matrix.iloc[i, j] and matrix.iloc[j, k] and not matrix.iloc[i, k]:
                    return False
    return True

def finde_aequivalente_teilrelationen(matrix):
    teilrelationen = []
    for i in range(len(matrix)):
        for j in range(i+1, len(matrix)):
            teilmatrix = matrix.iloc[i:j+1, i:j+1]
            if ist_reflexiv(teilmatrix) and ist_symmetrisch(teilmatrix) and ist_transitiv(teilmatrix):
                teilrelationen.append((i, j, teilmatrix))
    return teilrelationen

def zeichne_teilrelation(matrix, title):
    G = nx.Graph()
    labels = list(matrix.index)
    for i, row in enumerate(matrix.index):
        for j, col in enumerate(matrix.columns):
            if matrix.iloc[i, j] > 0:
                G.add_edge(labels[i], labels[j])
    
    plt.figure(figsize=(8, 6))
    nx.draw(G, with_labels=True, node_color='lightblue', node_size=2000, font_size=10, font_color='black', font_weight='bold')
    plt.title(title)
    plt.show()

# Hauptlogik
print("Reflexiv:", ist_reflexiv(df))
print("Symmetrisch:", ist_symmetrisch(df))
print("Transitiv:", ist_transitiv(df))

teilrelationen = finde_aequivalente_teilrelationen(df)
print(f"Gefundene äquivalente Teilrelationen: {len(teilrelationen)}")

# Ausgabe der Teilrelationen
for idx, (start, end, teilrelation) in enumerate(teilrelationen):
    print(f"Teilrelation {idx+1} (Zeilen/Spalten {start}-{end}):")
    print(teilrelation)
    zeichne_teilrelation(teilrelation, f"Teilrelation {idx+1}")

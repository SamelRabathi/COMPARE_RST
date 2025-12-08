import pandas as pd
import numpy as np

def discretize(df:pd.DataFrame, bins:int=4, cutoffs:dict={}) -> pd.DataFrame:
    """
    Numerische Werte werden in diskrete Kategorien überführt:
        - Binarität in Form von Zahlen sind schon Diskret (0/1 → keine Diskretisierung)
        - optionale user-defined Cutoffs (z.B. medizinisch)
        - geringe Range → equal-width diskretisierung
        - ansonsten fallback: qcut
    
    Parameter:
        df: pd.DataFrame = Zu diskreditierende Pandas DataFrame
        bins: int = Anzahl der Diskretisierungsintervalle - Quantils-binning (für fallback)
        cutoffs: dict = dictornary mit {col: [cut1, cut2, ...]} für feste Intervalle
    
    Rückgabe:
        df: DataFrame mit *_disc Spalten
        Original:          New column:
            "Total_Score"  →   "Total_Score_disc"
            "Age"          →   "Age_disc"
        
    Beispiel:
        Werte 0 – 100 werden bei bins=4 zu:
        0 → niedrigstes Quartil (0 - 24)
        1 → zweites Quartil (25 - 49)
        2 → drittes Quartil (50 - 74)
        3 → höchstes Quartil (75 - 100)
    """
    df = df.copy()
    
    for col in df.columns:
        s = df[col]

        # 1) user-definierte Cutoffs für kontinuierliche Variablen
        if col in cutoffs:
            bins_list = [-np.inf] + cutoffs[col] + [np.inf]
            df[col + "_disc"] = pd.cut(s, bins_list, labels=False)
            continue

        # 2) numerische Spalten
        if s.dtype in ["float64", "int64"]:
            # binär (0/1) -> schon diskret
            if s.nunique() == 2:
                df[col + "_disc"] = s
                continue

            # kleiner Wertebereich
            if s.max() - s.min() < 10 and s.nunique() > 3:
                df[col + "_disc"] = pd.cut(s, bins=3, labels=False)
                continue

            # fallback: qcut
            df[col + "_disc"] = pd.qcut(
                s.rank(method="first"),
                q=bins,
                labels=False,
                duplicates="drop"
            )
            continue

        # 3) kategoriale Spalten (object)
        if s.dtype == "object":
            #df[col + "_disc"] = s.astype("category").cat.codes
            continue

    return df


def indiscernibility(df: pd.DataFrame, attrs: list[str]) -> list[list[int]]:
    """
    Bildet Äquivalenzklassen der Indiscernibility Relation 'IND(P)' wieder.
    Input:
        • df: ein DataFrame (diskretisiert)
        • attrs: Liste von Attributen, nach denen Objekte verglichen werden
    Output:
        • list: Eine Liste von Listen, wo jede innere Liste eine Äquivalenzklasse [x]P ist.

    Beispiel:
        Input:
            • attrs = ["Age_disc", "StudyTime_disc"]
            df: ...
            Objekt 1: (2, 0)
            Objekt 2: (2, 0)
            Objekt 3: (1, 3)
                ...
        Output:

        [
          [0, 4, 10],     # diese drei Objekte sind ununterscheidbar
          [1, 2],         # diese beiden ebenfalls - ist auch im beispielhaften Input zu sehen.
          [3],            # einzelnes Objekt
          ...
        ]
    """
    if not attrs:
        # jede Zeile ist eigene Klasse
        return [[i] for i in df.index]

    g = df.groupby(attrs, sort=False, observed=True)

    # g.indices: dict {group_key: array(indices)}
    return [list(idx_arr) for idx_arr in g.indices.values()]


def dependency(df: pd.DataFrame, attrs, decision, eps=1e-12) -> float:
    """
    • Berechnet POS_C(D)
    • Zählt, wie viele Objekte eindeutig klassifiziert werden können
    • Dividiert durch Anzahl aller Objekte
    
    Vektoriserte (ohne Python-Schleifen über Zeilen)
    
    Input:
        • df: Information System (diskret)
        • attrs: Konditionsattribute C
        • decision: Entscheidungsattribut D
    Output:
        • Ein float zwischen 0 und 1

    Für die Attribute C:
        • indiscernibility(C) liefert Äquivalenzklassen
            -> Jede Klasse wird geprüft:
                wenn alle Objekte dieselbe Entscheidung haben → Klasse gehört zur positiven Region


    Ein float zwischen 0 und 1:
        • γ = 1 → perfekte Klassifikation
        • γ = 0 → keine Klassifikation möglich
        • 0 < γ < 1 → teils eindeutig, teils unsicher
    """
    if not attrs:
        return 0.0

    # groups: alle Äquivalenzklassen nach attrs
    g = df.groupby(attrs, sort=False, observed=True)

    # wie viele verschiedene Decisions pro Klasse?
    nunique_dec = g[decision].nunique()   # Index = Gruppenschlüssel

    # Klassengrößen
    sizes = g.size()

    # nur Klassen mit genau einer Decision zählen zur positiven Region
    pos = sizes[nunique_dec == 1].sum()

    return float(pos) / float(len(df)) if len(df) > 0 else 0.0



def analyze_dependency_structure(df, attrs, decision):
    """
    Hilfsfunktion:
      - berechnet γ(C) für alle Attribute in attrs
      - berechnet γ({a}) für jedes Einzelattribut a
    Rückgabe:
      gamma_star: float
      singles: dict {attribut: gamma({a})}
    """
    gamma_star = dependency(df, attrs, decision)
    singles = {a: dependency(df, [a], decision) for a in attrs}
    return gamma_star, singles



def quick_reduct_old(df, attrs, decision, eps=1e-12, verbose=True):
    """
    Wählt automatisch zwischen:
      - quick_reduct_monotone   (wenn mind. ein Einzelattribut γ>0 hat)
      - quick_reduct_interaction (wenn alle Einzelattribute γ=0, aber γ(C)>0)

    Logik:
      - γ(C) = dependency(df, attrs, decision)
      - singles[a] = dependency(df, [a], decision)
      - wenn max(singles) > 0: monotone Variante
      - sonst: interaktionssensitive Variante
    """
    gamma_star, singles = analyze_dependency_structure(df, attrs, decision)
    max_single = max(singles.values()) if singles else 0.0

    if verbose:
        print(f"γ(C) mit allen Attributen: {gamma_star:.6f}")
        print("Einzel-γ-Werte:")
        for a, g in singles.items():
            print(f"  {a}: γ = {g:.6f}")

    if gamma_star <= eps:
        if verbose:
            print("\nHinweis: γ(C) ≈ 0 → keine deterministische Struktur, kein sinnvolles Redukt.")
        return [], {"gamma_star": gamma_star, "singles": singles, "mode": "none"}

    # Fall 1: mindestens ein Attribut hat γ({a}) > 0 -> monotone QuickReduct sinnvoll
    if max_single > eps:
        if verbose:
            print("\nMindestens ein Attribut hat γ({a}) > 0 → benutze quick_reduct_monotone.")
        R = quick_reduct_monotone(df, attrs, decision, eps=eps)
        mode = "monotone"
    else:
        # Fall 2: alle γ({a}) == 0, aber γ(C) > 0 -> reine Interaktionen
        if verbose:
            print("\nAlle γ({a}) = 0, aber γ(C) > 0 → benutze quick_reduct_interaction.")
        R = quick_reduct_interaction(df, attrs, decision, eps=eps)
        mode = "interaction"

    return R, {"gamma_star": gamma_star, "singles": singles, "mode": mode}

def quick_reduct(df, attrs, decision, eps=1e-12, verbose=True, mode: str = "auto"):
    """
    Wählt je nach mode zwischen:
      - 'auto'         : automatische Entscheidung zwischen monotone / interaction (aktuelles Verhalten)
      - 'monotone'     : erzwingt quick_reduct_monotone
      - 'interaction'  : erzwingt quick_reduct_interaction

    Parameter:
        df       : diskretes Information System
        attrs    : Liste der Konditionsattribute
        decision : Entscheidungsattribut
        eps      : Toleranz für numerische Vergleiche
        verbose  : wenn True, werden Statusmeldungen gedruckt
        mode     : 'auto', 'monotone' oder 'interaction'
    Rückgabe:
        (R, info)
        R    : Liste der gewählten Attribute
        info : dict mit Meta-Infos (gamma_star, singles, mode)
    """
    # 1) Basis-Analyse (immer gleich)
    gamma_star, singles = analyze_dependency_structure(df, attrs, decision)
    max_single = max(singles.values()) if singles else 0.0

    if verbose:
        print(f"γ(C) mit allen Attributen: {gamma_star:.6f}")
        print("Einzel-γ-Werte:")
        for a, g in singles.items():
            print(f"  {a}: γ = {g:.6f}")

    # Falls überhaupt keine Abhängigkeit vorhanden ist → direkt abbrechen
    if gamma_star <= eps:
        if verbose:
            print("\nHinweis: γ(C) ≈ 0 → keine deterministische Struktur, kein sinnvolles Redukt.")
        return [], {"gamma_star": gamma_star, "singles": singles, "mode": "none"}

    # 2) Modus normalisieren / validieren
    mode = (mode or "auto").lower()
    if mode not in {"auto", "monotone", "interaction"}:
        raise ValueError(f"Ungültiger mode='{mode}'. Erlaubt sind: 'auto', 'monotone', 'interaction'.")

    # 3) Modus-spezifische Entscheidung
    if mode == "monotone":
        if verbose:
            print("\nErzwinge monotone QuickReduct-Variante (quick_reduct_monotone).")
        R = quick_reduct_monotone(df, attrs, decision, eps=eps)
        chosen_mode = "monotone"

    elif mode == "interaction":
        if verbose:
            print("\nErzwinge interaktionssensitive Variante (quick_reduct_interaction).")
        R = quick_reduct_interaction(df, attrs, decision, eps=eps)
        chosen_mode = "interaction"

    else:  # mode == "auto"  → dein bisheriges Verhalten
        if max_single > eps:
            if verbose:
                print("\nMindestens ein Attribut hat γ({a}) > 0 → benutze quick_reduct_monotone.")
            R = quick_reduct_monotone(df, attrs, decision, eps=eps)
            chosen_mode = "monotone"
        else:
            if verbose:
                print("\nAlle γ({a}) = 0, aber γ(C) > 0 → benutze quick_reduct_interaction.")
            R = quick_reduct_interaction(df, attrs, decision, eps=eps)
            chosen_mode = "interaction"

    return R, {"gamma_star": gamma_star, "singles": singles, "mode": chosen_mode}




def quick_reduct_monotone(df:pd.DataFrame, attrs, decision, eps=1e-12) -> list():
    """
    Was wird gemacht:
        • greedy Auswahl von Attributen
        • Maximiert schrittweise den Dependency Degree γ
        • Endet:
            • Kein Attribut γ verbessern kann. Oder
            • γ voll ist.
    Ursprung: Pawlak (1982) – Grunddefinition Reduct und Shenoi & Yao (1994), Jensen (1998) – QuickReduct-Algorithmus
    
    Input:
        • df: Diskretes IS
        • attrs: Alle konditionalen Attribute
        • decision: Die Zielvariable
    Output:
        • list: Eine Liste von Attributen z.B ['Age_disc'], welches das (hoffentlich:)) minimale notwendige Attributset ist.
    """
    R = []
    gamma_star = dependency(df, attrs, decision)
    gamma_R = 0.0

    while gamma_R < gamma_star - eps:
        best_attr = None
        best_gamma = gamma_R

        for a in attrs:
            if a in R:
                continue
            g = dependency(df, R + [a], decision)
            if g > best_gamma + eps:
                best_gamma = g
                best_attr = a

        if best_attr is None:
            break

        R.append(best_attr)
        gamma_R = best_gamma

    return R



def quick_reduct_interaction(df, attrs, decision, eps=1e-12):
    """
    QuickReduct-Variante, die auch interaktionelle Strukturen erfassen kann:
      - Startet mit R = ∅
      - Wählt in jeder Iteration das Attribut, das γ(R ∪ {a}) maximal macht
      - Erlaubt, dass der erste Schritt γ(R) = 0 lässt
      - Stoppt, wenn γ(R) ≈ γ(C) ist oder alle Attribute drin sind

    Geeignet für: Systeme mit starken Interaktionen.
    """
    R = []
    gamma_star = dependency(df, attrs, decision)
    gamma_R = 0.0

    # Wenn selbst mit allen Attributen keine Abhängigkeit vorliegt, gibt es nichts zu reduzieren
    if gamma_star <= 0 + eps:
        return []

    # Solange wir nicht die gleiche Abhängigkeit wie mit allen Attributen erreicht haben:
    while gamma_R < gamma_star - eps and len(R) < len(attrs):
        best_attr = None
        best_gamma = gamma_R

        for a in attrs:
            if a in R:
                continue

            g = dependency(df, R + [a], decision)

            # wichtig:
            # - erster Kandidat wird immer angenommen (best_attr is None)
            # - danach immer der mit der größten γ-Verbesserung
            if best_attr is None or g > best_gamma + eps:
                best_attr = a
                best_gamma = g

        if best_attr is None:
            # sollte bei gamma_star > 0 selten passieren
            break

        R.append(best_attr)
        gamma_R = best_gamma
        # optional: Debug-Ausgabe
        # print(f"hinzugefügt: {best_attr}, γ(R) = {gamma_R:.4f} (γ* = {gamma_star:.4f})")

    return R


def induce_rules(df: pd.DataFrame, reduct, decision, verbose=False):
    rules = []
    ind = indiscernibility(df, reduct)
    if verbose:
        print("Anzahl an Klassen:", len(ind))
        # print(ind)
        print()
    for block in ind:
        decs = df.loc[block, decision].unique()
        if len(decs) == 1:
            rules.append({
                "premise": {a: df.loc[block[0], a] for a in reduct},
                "decision": decs[0],
                "support": len(block),
            })
    return rules


def compute_coverage(df: pd.DataFrame, reduct: list[str], decision: str, rules: list[dict]) -> float:
    """
    Berechnet den Anteil der Objekte im df, die von mindestens einer
    deterministischen Regel abgedeckt werden.

    df       : diskretisiertes DataFrame
    reduct   : Attributliste, auf der die Regeln basieren
    decision : Name der Entscheidungsvariable (z.B. "Pass")
    rules    : Liste von Regel-Dictionaries aus induce_rules()
    """
    if len(df) == 0 or not rules:
        return 0.0

    covered = np.zeros(len(df), dtype=bool)

    for rule in rules:
        premise = rule["premise"]
        mask = np.ones(len(df), dtype=bool)
        for attr, val in premise.items():
            mask &= (df[attr] == val)
        # Alle Objekte, die diese Prämisse erfüllen, gelten als abgedeckt
        covered |= mask

    coverage = covered.sum() / len(df)
    return float(coverage)


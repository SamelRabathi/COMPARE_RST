
from typing import Dict, Tuple, Set, List, Any
import re
import math
import pandas as pd
from collections import defaultdict, Counter, deque

def parse_dfa(text: str) -> Dict[str, Any]:
    parts = [p.strip() for p in text.split(";") if p.strip()]
    transitions = {}
    states: Set[str] = set()
    alphabet: Set[str] = set()
    start = None
    finals: Set[str] = set()

    state_line_pattern = re.compile(r"^([A-Za-z0-9_]+)\s*:\s*(.+)$")
    trans_token_pattern = re.compile(r"\s*([^\s,:]+)\s*-->\s*([^\s,;]+)\s*")

    for p in parts:
        if p.startswith("in:"):
            start = p.split("in:", 1)[1].strip()
        elif p.startswith("fi:"):
            finals = set([s.strip() for s in p.split("fi:", 1)[1].split(",") if s.strip()])
        else:
            m = state_line_pattern.match(p)
            if m:
                state = m.group(1).strip()
                states.add(state)
                trans_list = m.group(2).split(",")
                for tok in trans_list:
                    tok = tok.strip()
                    if not tok:
                        continue
                    m2 = trans_token_pattern.match(tok)
                    if m2:
                        sym = m2.group(1).strip()
                        tgt = m2.group(2).strip()
                        transitions[(state, sym)] = tgt
                        states.add(tgt)
                        alphabet.add(sym)

    if start and states:
        q = deque([start])
        visited = set([start])
        while q:
            u = q.popleft()
            for (s, sym), t in transitions.items():
                if s == u and t not in visited:
                    visited.add(t)
                    q.append(t)
        reachable_states = visited
    else:
        reachable_states = set()

    return {
        "states": states,
        "alphabet": alphabet,
        "start": start,
        "finals": finals,
        "transitions": transitions,
        "reachable_states": reachable_states
    }

def dfa_features(dfa: Dict[str, Any]) -> Dict[str, Any]:
    states = dfa["states"]
    alphabet = dfa["alphabet"]
    trans = dfa["transitions"]
    finals = dfa["finals"]
    start = dfa["start"]
    reachable = dfa["reachable_states"]

    n_states = len(states)
    alphabet_size = len(alphabet)
    n_transitions = len(trans)
    n_self_loops = sum(1 for (s, a), t in trans.items() if s == t)
    final_ratio = (len(finals) / n_states) if n_states else 0.0

    out_counts = Counter()
    for (s, a), t in trans.items():
        out_counts[s] += 1
    avg_out_degree = (sum(out_counts.values()) / n_states) if n_states else 0.0

    is_complete = True
    if n_states and alphabet_size:
        for s in states:
            for a in alphabet:
                if (s, a) not in trans:
                    is_complete = False
                    break
            if not is_complete:
                break

    n_reachable = len(reachable) if start else 0
    unreachable = n_states - n_reachable if n_states else 0

    sink_states = 0
    for s in states:
        if alphabet_size == 0:
            continue
        all_self = True
        for a in alphabet:
            if (s, a) not in trans or trans[(s, a)] != s:
                all_self = False
                break
        if all_self:
            sink_states += 1

    return {
        "n_states": n_states,
        "alphabet_size": alphabet_size,
        "n_transitions": n_transitions,
        "n_self_loops": n_self_loops,
        "final_ratio": final_ratio,
        "avg_out_degree": avg_out_degree,
        "is_complete": int(is_complete),
        "n_reachable": n_reachable,
        "n_unreachable": unreachable,
        "n_sink_states": sink_states,
    }

def parse_pair_to_features(input_text: str, output_text: str) -> Dict[str, Any]:
    dfa_in = parse_dfa(input_text)
    dfa_out = parse_dfa(output_text)
    feat = dfa_features(dfa_in)
    feat["minimized_n_states"] = len(dfa_out["states"])
    feat["reduction_ratio"] = (
        (feat["minimized_n_states"] / feat["n_states"]) if feat["n_states"] else math.nan
    )
    return feat

def discretize_dataframe(df: pd.DataFrame, numeric_cols: List[str], bins: int = 3, strategy: str = "quantile") -> pd.DataFrame:
    df = df.copy()
    for col in numeric_cols:
        if strategy == "quantile":
            if df[col].nunique(dropna=True) <= 1:
                df[col + "_disc"] = 0
            else:
                df[col + "_disc"] = pd.qcut(df[col].rank(method="first"), q=bins, labels=False, duplicates="drop")
        else:
            if df[col].nunique(dropna=True) <= 1:
                df[col + "_disc"] = 0
            else:
                df[col + "_disc"] = pd.cut(df[col], bins=bins, labels=False, duplicates="drop")
    return df

def indiscernibility_partition(df: pd.DataFrame, attrs: List[str]) -> List[List[int]]:
    groups = defaultdict(list)
    for i, row in df[attrs].iterrows():
        key = tuple(row.tolist())
        groups[key].append(i)
    return list(groups.values())

def dependency_degree(df: pd.DataFrame, cond_attrs: List[str], decision_attr: str) -> float:
    if not cond_attrs:
        return 0.0
    U = set(df.index.tolist())
    part_C = indiscernibility_partition(df, cond_attrs)
    consistent_size = 0
    for block in part_C:
        dec_vals = set(df.loc[block, decision_attr].tolist())
        if len(dec_vals) == 1:
            consistent_size += len(block)
    return consistent_size / len(U) if len(U) else 0.0

def quick_reduct(df: pd.DataFrame, all_attrs: list, decision_attr: str) -> list:
    R = []
    gamma_R = 0.0
    gamma_star = dependency_degree(df, all_attrs, decision_attr)

    while gamma_R < gamma_star - 1e-12:  # solange wir die volle Abhängigkeit noch nicht erreicht haben
        best_attr = None
        best_gamma = gamma_R

        for a in all_attrs:
            if a in R:
                continue
            g = dependency_degree(df, R + [a], decision_attr)
            if g > best_gamma + 1e-12:
                best_gamma = g
                best_attr = a

        if best_attr is None:
            # keine Verbesserung mehr möglich
            break

        R.append(best_attr)
        gamma_R = best_gamma

    return R

def induce_rules(df: pd.DataFrame, reduct_attrs: List[str], decision_attr: str):
    rules = []
    blocks = indiscernibility_partition(df, reduct_attrs)
    for block in blocks:
        dec_vals = set(df.loc[block, decision_attr].tolist())
        if len(dec_vals) == 1:
            i = block[0]
            premise = {a: df.at[i, a] for a in reduct_attrs}
            decision = list(dec_vals)[0]
            support = len(block)
            rules.append({"premise": premise, "decision": decision, "support": support})
    return rules

import pandas as pd
import re

# === 1. Charger le fichier brut ===
df = pd.read_csv(
    "Compte-rendu 01.01.2026-21.01.2026.csv",
    sep=";",
    encoding="latin-1"
)

df["obs_clean"] = df["Observation"].fillna("").str.lower()

# === 2. Dictionnaire des opérations et mots associés ===
operations = {
    "remplacement_fusible": [
        "fusible", "fus", "pf", "porte fusible", "fusible hs", "fusible grillé",
        "2a", "4a", "6a"
    ],
    "remplacement_ampoule": [
        "ampoule", "lampe", "amp", "70w", "150w", "lampe hs", "ampoule grillée"
    ],
    "remplacement_driver": [
        "driver", "ballast", "alim led"
    ],
    "remplacement_boite_derivation": [
        "boite", "boîte", "derivation", "dérivation", "boitier classe 2"
    ],
    "remplacement_driver_et_connexions": [
        "driver", "connexion", "connecteur", "domino"
    ],
    "pose_lanterne_provisoire": [
        "lanterne", "provisoire", "pose lanterne", "depose", "dépose"
    ],
    "separation_phases_cablage": [
        "phase", "ep", "câblage", "cablage", "cable", "alimentation",
        "separation", "séparer"
    ],
    "plateau_led_hs": [
        "plateau", "led", "hs", "module led"
    ],
    "reenclenchement_disjoncteur": [
        "disjoncteur", "dj", "réarmement", "réenclenchement", "rearm", "re enclenche"
    ],
    "reprise_raccordement": [
        "raccordement", "reprise", "recablage", "recâblage"
    ],
    "refection_connexions": [
        "connexion", "connecteur", "refection", "refaire connexion"
    ]
}

# === 3. Fonction de détection multi-opérations ===
def detect_operations(text):
    result = {}
    for op, keywords in operations.items():
        found = any(re.search(r"\b" + re.escape(k) + r"\b", text) for k in keywords)
        result[op] = "oui" if found else "non"
    return result

# === 4. Appliquer la détection ===
multi = df["obs_clean"].apply(detect_operations)
multi_df = pd.DataFrame(list(multi))
df = pd.concat([df, multi_df], axis=1)

# === 5. Générer un résumé basé sur les opérations détectées ===
def generate_summary(row):
    ops = [op.replace("_", " ") for op in operations.keys() if row[op] == "oui"]
    if not ops:
        return "aucune opération détectée"
    return ", ".join(ops)

df["resume_ia"] = df.apply(generate_summary, axis=1)

# === 6. Export final ===
df.to_csv("Compte-rendu_enrichi.csv", sep=";", index=False)

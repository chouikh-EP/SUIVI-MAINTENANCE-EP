import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# 1) Charger le fichier brut
df = pd.read_csv(
    "Compte-rendu 01.01.2026-21.01.2026.csv",
    sep=";",
    encoding="latin1"
)

# 2) Préparer la colonne Observation
# - on remplace les valeurs vides par ""
# - on passe tout en minuscules pour la détection
df["Observation"] = df["Observation"].fillna("").astype(str).str.lower()

# 3) Dictionnaire de mots-clés -> type d’intervention
# Tu peux enrichir cette liste au fur et à mesure
operation_keywords = {
    "remplacement": "Remplacement",
    "fusible": "Remplacement fusible",
    "lampe": "Remplacement lampe",
    "ampoule": "Remplacement lampe",
    "pose": "Pose",
    "compteur": "Pose compteur",
    "separation": "Séparation",
    "plateau": "Plateau LED",
    "led": "Plateau LED",
    "reenclenchement": "Réenclenchement",
    "réenclenchement": "Réenclenchement",
    "disjoncteur": "Réenclenchement disjoncteur",
    "reprise": "Reprise alimentation",
    "refection": "Réfection",
    "réfection": "Réfection",
    "cable": "Réfection câblage",
    "câble": "Réfection câblage",
}

# 4) Fonction de détection des opérations dans une observation
def detect_operations(text):
    ops = []
    for key, label in operation_keywords.items():
        if key in text:
            ops.append(label)
    # Si aucune opération détectée, on renvoie None
    return ops if ops else None

# 5) Appliquer la détection à chaque ligne
df["operations_detectees"] = df["Observation"].apply(detect_operations)

# 6) Exploser pour avoir une ligne par opération détectée
df_ops = df.explode("operations_detectees")

# 7) Garder uniquement les lignes où une opération a été trouvée
df_ops = df_ops[df_ops["operations_detectees"].notna()]

# Si aucune opération détectée, on évite de planter et on génère un dashboard vide mais propre
if df_ops.empty:
    # Créer un dashboard vide avec un message
    fig = go.Figure()
    fig.add_annotation(
        text="Aucune intervention détectée dans les observations.",
        showarrow=False,
        font=dict(size=16)
    )
    fig.update_layout(
        title="Dashboard des interventions détectées dans les observations",
        height=400
    )
    fig.write_html("index.html", include_plotlyjs="cdn", full_html=True)
else:
    # 8) Compter les opérations
    operation_counts = df_ops["operations_detectees"].value_counts()

    # 9) Création du dashboard (barres + camembert)
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=(
            "Nombre d'interventions par type",
            "Répartition des interventions"
        ),
        specs=[[{"type": "bar"}, {"type": "domain"}]]
    )

    # Graphique en barres
    fig.add_trace(
        go.Bar(
            x=operation_counts.index,
            y=operation_counts.values,
            marker=dict(color="steelblue")
        ),
        row=1, col=1
    )

    # Camembert
    fig.add_trace(
        go.Pie(
            labels=operation_counts.index,
            values=operation_counts.values,
            hole=0.4
        ),
        row=1, col=2
    )

    fig.update_layout(
        title="Dashboard des interventions détectées dans les observations",
        height=600,
        showlegend=False
    )

    fig.update_xaxes(tickangle=-45, row=1, col=1)

    # 10) Export HTML pour GitHub Pages
    fig.write_html("index.html", include_plotlyjs="cdn", full_html=True)

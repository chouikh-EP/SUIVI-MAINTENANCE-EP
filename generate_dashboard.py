import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Charger le fichier brut
df = pd.read_csv(
    "Compte-rendu 01.01.2026-21.01.2026.csv",
    sep=";",
    encoding="latin1"
)

# Nettoyage de la colonne Observation
df["Observation"] = df["Observation"].fillna("").astype(str).str.lower()

# 🔵 DICTIONNAIRE EXACT PROPOSÉ (sans rien ajouter)
operation_keywords = {
    "remplacement": "Remplacement",
    "fusible": "Remplacement fusible",
    "lampe": "Remplacement lampe",
    "ampoule": "Remplacement lampe",
    "driver": "Remplacement driver",
    "pose": "Pose",
    "lanterne": "Pose lanterne provisoire",
    "provisoire": "Pose lanterne provisoire",
    "separation": "Séparation",
    "phases": "Séparation phases",
    "plateau": "Plateau LED HS",
    "led": "Plateau LED HS",
    "reenclenchement": "Réenclenchement disjoncteur",
    "réenclenchement": "Réenclenchement disjoncteur",
    "disjoncteur": "Réenclenchement disjoncteur",
    "refection": "Réfection connexions",
    "réfection": "Réfection connexions",
    "connexion": "Réfection connexions",
    "cable": "Reprise câblage",
    "câble": "Reprise câblage",
}

# Détection des opérations dans une observation
def detect_operations(text):
    ops = []
    for key, label in operation_keywords.items():
        if key in text:
            ops.append(label)
    return ops if ops else None

# Appliquer la détection
df["operations_detectees"] = df["Observation"].apply(detect_operations)

# Exploser pour avoir une ligne par opération
df_ops = df.explode("operations_detectees")

# Garder uniquement les lignes où une opération a été trouvée
df_ops = df_ops[df_ops["operations_detectees"].notna()]

# Si aucune opération détectée → dashboard vide mais propre
if df_ops.empty:
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
else:
    # Compter les opérations
    operation_counts = df_ops["operations_detectees"].value_counts()

    # Dashboard
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=(
            "Nombre d'interventions par type",
            "Répartition des interventions"
        ),
        specs=[[{"type": "bar"}, {"type": "domain"}]]
    )

    # Barres
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

# Export HTML
fig.write_html("index.html", include_plotlyjs="cdn", full_html=True)

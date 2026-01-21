import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Charger les données
df = pd.read_csv("donnees.csv", sep=";")

# Colonnes d'opérations
operation_cols = [col for col in df.columns if col.startswith((
    "remplacement_", "pose_", "separation_", "plateau_", 
    "reenclenchement_", "reprise_", "refection_"
))]

# Volume par opération
operation_counts = df[operation_cols].apply(lambda col: (col == "oui").sum()).sort_values(ascending=False)

# Dashboard
fig_dashboard = make_subplots(
    rows=1, cols=2,
    subplot_titles=(
        "Nombre d'interventions par opération",
        "Répartition des opérations"
    ),
    specs=[
        [{"type": "bar"}, {"type": "domain"}]
    ]
)

# Barres
fig_dashboard.add_trace(
    go.Bar(
        x=operation_counts.index,
        y=operation_counts.values,
        marker=dict(color="steelblue")
    ),
    row=1, col=1
)

# Camembert
fig_dashboard.add_trace(
    go.Pie(
        labels=operation_counts.index,
        values=operation_counts.values,
        hole=0.4
    ),
    row=1, col=2
)

fig_dashboard.update_layout(
    title="Dashboard des opérations d'intervention",
    height=600,
    showlegend=False
)

fig_dashboard.update_xaxes(tickangle=-45, row=1, col=1)

# Export HTML
fig_dashboard.write_html("index.html", include_plotlyjs="cdn", full_html=True)

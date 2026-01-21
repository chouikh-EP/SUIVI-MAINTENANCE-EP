import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
from plotly.io import to_html

# === 1. Charger les données brutes ===
# Adapte le nom du fichier si besoin
df = pd.read_csv(
    "Compte-rendu 01.01.2026-21.01.2026.csv",
    sep=";",
    encoding="latin-1"
)

# === 2. Normaliser les colonnes utilisées ===
# Colonnes existantes :
# - "Date Intervention"
# - "Activité"
# - "Type d'ouvrage"
# - "resume_ia" (ou autre colonne contenant la réparation détectée)

# Renommer pour simplifier
df = df.rename(columns={
    "Date Intervention": "date_intervention",
    # si ta colonne s'appelle autrement, change "resume_ia" ici :
    "resume_ia": "reparation"
})

# Nettoyage basique
df["date_intervention"] = pd.to_datetime(df["date_intervention"], errors="coerce")
df = df.dropna(subset=["date_intervention"])

df["reparation"] = df["reparation"].fillna("aucune opération détectée")
df["Activité"] = df["Activité"].fillna("Non renseigné")
df["Type d'ouvrage"] = df["Type d'ouvrage"].fillna("Non renseigné")

# Colonnes dérivées
df["annee"] = df["date_intervention"].dt.year
df["mois"] = df["date_intervention"].dt.to_period("M").astype(str)

# === 3. KPI principaux ===
total_interventions = len(df)
total_reparations = (df["reparation"] != "aucune opération détectée").sum()
top_reparation = (
    df[df["reparation"] != "aucune opération détectée"]["reparation"]
    .value_counts()
    .idxmax()
    if total_reparations > 0 else "Aucune"
)
top_activite = df["Activité"].value_counts().idxmax()
top_type_ouvrage = df["Type d'ouvrage"].value_counts().idxmax()

# === 4. Graphique 1 : Histogramme mensuel des interventions ===
interventions_par_mois = df.groupby("mois").size().reset_index(name="nb")
fig_mois = px.bar(
    interventions_par_mois,
    x="mois",
    y="nb",
    title="Nombre d'interventions par mois",
    labels={"mois": "Mois", "nb": "Nombre d'interventions"},
)
fig_mois.update_layout(margin=dict(l=40, r=40, t=60, b=40))

# === 5. Graphique 2 : Top réparations ===
df_rep = df[df["reparation"] != "aucune opération détectée"]
reparations_counts = df_rep["reparation"].value_counts().reset_index()
reparations_counts.columns = ["reparation", "nb"]

fig_top_rep = px.bar(
    reparations_counts.head(10),
    x="nb",
    y="reparation",
    orientation="h",
    title="Top 10 des réparations les plus fréquentes",
    labels={"nb": "Nombre d'interventions", "reparation": "Réparation"},
)
fig_top_rep.update_layout(margin=dict(l=120, r=40, t=60, b=40))

# === 6. Graphique 3 : Répartition par activité ===
activite_counts = df["Activité"].value_counts().reset_index()
activite_counts.columns = ["Activité", "nb"]

fig_activite = px.pie(
    activite_counts,
    names="Activité",
    values="nb",
    title="Répartition des interventions par activité",
    hole=0.4,
)

# === 7. Graphique 4 : Répartition par type d’ouvrage ===
type_counts = df["Type d'ouvrage"].value_counts().reset_index()
type_counts.columns = ["Type d'ouvrage", "nb"]

fig_type_ouvrage = px.pie(
    type_counts,
    names="Type d'ouvrage",
    values="nb",
    title="Répartition des interventions par type d’ouvrage",
    hole=0.4,
)

# === 8. Graphique 5 : Heatmap Mois × Réparation ===
if not df_rep.empty:
    heat_data = df_rep.groupby(["mois", "reparation"]).size().reset_index(name="nb")
    fig_heat = px.density_heatmap(
        heat_data,
        x="mois",
        y="reparation",
        z="nb",
        color_continuous_scale="Blues",
        title="Carte thermique des réparations par mois",
    )
    fig_heat.update_layout(margin=dict(l=120, r=40, t=60, b=40))
else:
    fig_heat = go.Figure()
    fig_heat.add_annotation(
        text="Aucune réparation détectée pour la heatmap.",
        showarrow=False,
        font=dict(size=16)
    )

# === 9. Graphique 6 : Évolution des réparations dans le temps ===
if not df_rep.empty:
    evol_data = df_rep.groupby(["date_intervention", "reparation"]).size().reset_index(name="nb")
    fig_evol = px.line(
        evol_data,
        x="date_intervention",
        y="nb",
        color="reparation",
        title="Évolution des réparations dans le temps",
        labels={"date_intervention": "Date", "nb": "Nombre d'interventions"},
    )
    fig_evol.update_layout(margin=dict(l=40, r=40, t=60, b=40))
else:
    fig_evol = go.Figure()
    fig_evol.add_annotation(
        text="Aucune réparation détectée pour l'évolution temporelle.",
        showarrow=False,
        font=dict(size=16)
    )

# === 10. Graphique 7 : Activité × Type d’ouvrage ===
cross_data = df.groupby(["Activité", "Type d'ouvrage"]).size().reset_index(name="nb")
fig_cross = px.bar(
    cross_data,
    x="Activité",
    y="nb",
    color="Type d'ouvrage",
    barmode="stack",
    title="Répartition des interventions par activité et type d’ouvrage",
    labels={"nb": "Nombre d'interventions"},
)
fig_cross.update_layout(margin=dict(l=40, r=40, t=60, b=40))

# === 11. Construction de la page HTML complète ===

html_kpi = f"""
<div style="display:flex; gap:20px; margin-bottom:30px;">
  <div style="flex:1; padding:15px; border-radius:8px; background:#1f77b4; color:white;">
    <h3>Total interventions</h3>
    <p style="font-size:24px; font-weight:bold;">{total_interventions}</p>
  </div>
  <div style="flex:1; padding:15px; border-radius:8px; background:#ff7f0e; color:white;">
    <h3>Total réparations détectées</h3>
    <p style="font-size:24px; font-weight:bold;">{total_reparations}</p>
  </div>
  <div style="flex:1; padding:15px; border-radius:8px; background:#2ca02c; color:white;">
    <h3>Réparation la plus fréquente</h3>
    <p style="font-size:18px; font-weight:bold;">{top_reparation}</p>
  </div>
  <div style="flex:1; padding:15px; border-radius:8px; background:#9467bd; color:white;">
    <h3>Activité dominante</h3>
    <p style="font-size:18px; font-weight:bold;">{top_activite}</p>
  </div>
</div>
"""

html_page = f"""
<html>
<head>
  <meta charset="utf-8">
  <title>Dashboard Maintenance EP</title>
</head>
<body style="font-family:Arial, sans-serif; margin:40px;">
  <h1>Dashboard Maintenance Éclairage Public</h1>
  <p>Tableau de bord basé sur les réparations détectées, les dates d'intervention, l'activité et le type d’ouvrage.</p>
  {html_kpi}
  <h2>Volume d'interventions</h2>
  {to_html(fig_mois, include_plotlyjs='cdn', full_html=False)}
  <h2>Réparations les plus fréquentes</h2>
  {to_html(fig_top_rep, include_plotlyjs=False, full_html=False)}
  <h2>Répartition par activité</h2>
  {to_html(fig_activite, include_plotlyjs=False, full_html=False)}
  <h2>Répartition par type d’ouvrage</h2>
  {to_html(fig_type_ouvrage, include_plotlyjs=False, full_html=False)}
  <h2>Carte thermique des réparations par mois</h2>
  {to_html(fig_heat, include_plotlyjs=False, full_html=False)}
  <h2>Évolution des réparations dans le temps</h2>
  {to_html(fig_evol, include_plotlyjs=False, full_html=False)}
  <h2>Activité × Type d’ouvrage</h2>
  {to_html(fig_cross, include_plotlyjs=False, full_html=False)}
</body>
</html>
"""

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html_page)

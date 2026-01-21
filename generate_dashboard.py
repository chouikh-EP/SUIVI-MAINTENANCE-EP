import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.io import to_html

# === 1. Charger le fichier enrichi ===
df = pd.read_csv(
    "Compte-rendu_enrichi.csv",
    sep=";",
    encoding="latin-1"
)

# === 2. Normalisation ===
df["date_intervention"] = pd.to_datetime(df["Date Intervention"], dayfirst=True)
df["reparation"] = df["resume_ia"].fillna("aucune opération détectée")
df["Activité"] = df["Activité"].fillna("Non renseigné")
df["Type d'ouvrage"] = df["Type d'ouvrage"].fillna("Non renseigné")

df["annee"] = df["date_intervention"].dt.year
df["mois"] = df["date_intervention"].dt.to_period("M").astype(str)

# === 3. KPI ===
total_interventions = len(df)
total_reparations = (df["reparation"] != "aucune opération détectée").sum()
top_reparation = df[df["reparation"] != "aucune opération détectée"]["reparation"].value_counts().idxmax()
top_activite = df["Activité"].value_counts().idxmax()
top_type_ouvrage = df["Type d'ouvrage"].value_counts().idxmax()

# === 4. Graphiques ===

# Histogramme mensuel
interventions_par_mois = df.groupby("mois").size().reset_index(name="nb")
fig_mois = px.bar(interventions_par_mois, x="mois", y="nb", title="Interventions par mois")

# Top réparations
df_rep = df[df["reparation"] != "aucune opération détectée"]
reparations_counts = df_rep["reparation"].value_counts().reset_index()
reparations_counts.columns = ["reparation", "nb"]
fig_top_rep = px.bar(reparations_counts.head(10), x="nb", y="reparation", orientation="h", title="Top réparations")

# Activité
activite_counts = df["Activité"].value_counts().reset_index()
activite_counts.columns = ["Activité", "nb"]
fig_activite = px.pie(activite_counts, names="Activité", values="nb", title="Répartition par activité", hole=0.4)

# Type d’ouvrage
type_counts = df["Type d'ouvrage"].value_counts().reset_index()
type_counts.columns = ["Type d'ouvrage", "nb"]
fig_type_ouvrage = px.pie(type_counts, names="Type d'ouvrage", values="nb", title="Répartition par type d’ouvrage", hole=0.4)

# Heatmap
heat_data = df_rep.groupby(["mois", "reparation"]).size().reset_index(name="nb")
fig_heat = px.density_heatmap(heat_data, x="mois", y="reparation", z="nb", title="Heatmap réparations")

# Évolution temporelle
evol_data = df_rep.groupby(["date_intervention", "reparation"]).size().reset_index(name="nb")
fig_evol = px.line(evol_data, x="date_intervention", y="nb", color="reparation", title="Évolution des réparations")

# Activité × Type d’ouvrage
cross_data = df.groupby(["Activité", "Type d'ouvrage"]).size().reset_index(name="nb")
fig_cross = px.bar(cross_data, x="Activité", y="nb", color="Type d'ouvrage", barmode="stack", title="Activité × Type d’ouvrage")

# === 5. Construction HTML ===
html_page = f"""
<html>
<head>
  <meta charset="utf-8">
  <title>Dashboard Maintenance EP</title>
</head>
<body style="font-family:Arial; margin:40px;">
  <h1>Dashboard Maintenance Éclairage Public</h1>

  <h2>KPI</h2>
  <ul>
    <li>Total interventions : {total_interventions}</li>
    <li>Total réparations détectées : {total_reparations}</li>
    <li>Réparation la plus fréquente : {top_reparation}</li>
    <li>Activité dominante : {top_activite}</li>
    <li>Type d’ouvrage dominant : {top_type_ouvrage}</li>
  </ul>

  <h2>Interventions par mois</h2>
  {to_html(fig_mois, include_plotlyjs='cdn', full_html=False)}

  <h2>Top réparations</h2>
  {to_html(fig_top_rep, include_plotlyjs=False, full_html=False)}

  <h2>Répartition par activité</h2>
  {to_html(fig_activite, include_plotlyjs=False, full_html=False)}

  <h2>Répartition par type d’ouvrage</h2>
  {to_html(fig_type_ouvrage, include_plotlyjs=False, full_html=False)}

  <h2>Heatmap réparations</h2>
  {to_html(fig_heat, include_plotlyjs=False, full_html=False)}

  <h2>Évolution des réparations</h2>
  {to_html(fig_evol, include_plotlyjs=False, full_html=False)}

  <h2>Activité × Type d’ouvrage</h2>
  {to_html(fig_cross, include_plotlyjs=False, full_html=False)}
</body>
</html>
"""

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html_page)

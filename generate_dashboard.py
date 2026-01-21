import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.io import to_html
import json

# === 1. Charger le fichier enrichi (UTF-8 propre) ===
df = pd.read_csv(
    "Compte-rendu_enrichi.csv",
    sep=";",
    encoding="utf-8"
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

top_reparation = (
    df[df["reparation"] != "aucune opération détectée"]["reparation"]
    .value_counts()
    .idxmax()
    if total_reparations > 0 else "Aucune"
)

top_activite = df["Activité"].value_counts().idxmax()
top_type_ouvrage = df["Type d'ouvrage"].value_counts().idxmax()

# === 4. Graphiques ===

# Histogramme mensuel
interventions_par_mois = df.groupby("mois").size().reset_index(name="nb")
fig_mois = px.bar(
    interventions_par_mois,
    x="mois",
    y="nb",
    title="Interventions par mois"
)

# Top réparations
df_rep = df[df["reparation"] != "aucune opération détectée"]
if not df_rep.empty:
    reparations_counts = df_rep["reparation"].value_counts().reset_index()
    reparations_counts.columns = ["reparation", "nb"]
    fig_top_rep = px.bar(
        reparations_counts.head(10),
        x="nb",
        y="reparation",
        orientation="h",
        title="Top réparations"
    )
else:
    fig_top_rep = go.Figure()
    fig_top_rep.add_annotation(text="Aucune réparation détectée", showarrow=False)

# Activité
activite_counts = df["Activité"].value_counts().reset_index()
activite_counts.columns = ["Activité", "nb"]
fig_activite = px.pie(
    activite_counts,
    names="Activité",
    values="nb",
    title="Répartition par activité",
    hole=0.4
)

# Type d’ouvrage
type_counts = df["Type d'ouvrage"].value_counts().reset_index()
type_counts.columns = ["Type d'ouvrage", "nb"]
fig_type_ouvrage = px.pie(
    type_counts,
    names="Type d'ouvrage",
    values="nb",
    title="Répartition par type d’ouvrage",
    hole=0.4
)

# Heatmap
if not df_rep.empty:
    heat_data = df_rep.groupby(["mois", "reparation"]).size().reset_index(name="nb")
    fig_heat = px.density_heatmap(
        heat_data,
        x="mois",
        y="reparation",
        z="nb",
        title="Heatmap réparations"
    )
else:
    fig_heat = go.Figure()
    fig_heat.add_annotation(text="Aucune réparation détectée", showarrow=False)

# Évolution temporelle
if not df_rep.empty:
    evol_data = df_rep.groupby(["date_intervention", "reparation"]).size().reset_index(name="nb")
    fig_evol = px.line(
        evol_data,
        x="date_intervention",
        y="nb",
        color="reparation",
        title="Évolution des réparations"
    )
else:
    fig_evol = go.Figure()
    fig_evol.add_annotation(text="Aucune réparation détectée", showarrow=False)

# Activité × Type d’ouvrage
cross_data = df.groupby(["Activité", "Type d'ouvrage"]).size().reset_index(name="nb")
fig_cross = px.bar(
    cross_data,
    x="Activité",
    y="nb",
    color="Type d'ouvrage",
    barmode="stack",
    title="Activité × Type d’ouvrage"
)

# === 5. Construction HTML (thème moderne + sidebar + filtres visuels) ===

html_page = f"""
<html>
<head>
  <meta charset="utf-8">
  <title>Dashboard Maintenance EP</title>
  <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>

  <style>
    :root {{
      --bg-color: #0d1117;
      --text-color: #e6edf3;
      --card-bg: #161b22;
      --border-color: #30363d;
      --accent: #58a6ff;
    }}
    body.light {{
      --bg-color: #f5f5f5;
      --text-color: #111827;
      --card-bg: #ffffff;
      --border-color: #d1d5db;
      --accent: #2563eb;
    }}
    body {{
      background: var(--bg-color);
      color: var(--text-color);
      font-family: "Segoe UI", Arial, sans-serif;
      margin: 0;
      display: flex;
    }}
    .sidebar {{
      width: 260px;
      background: #111827;
      color: #e5e7eb;
      padding: 20px;
      height: 100vh;
      box-sizing: border-box;
      position: fixed;
      left: 0;
      top: 0;
      border-right: 1px solid #1f2933;
    }}
    .sidebar h2 {{
      margin-top: 0;
      color: #60a5fa;
    }}
    .sidebar button {{
      width: 100%;
      padding: 10px;
      margin-top: 10px;
      border-radius: 6px;
      border: none;
      cursor: pointer;
      background: #1f2937;
      color: #e5e7eb;
    }}
    .sidebar button:hover {{
      background: #374151;
    }}
    .content {{
      margin-left: 260px;
      padding: 30px;
      box-sizing: border-box;
      width: calc(100% - 260px);
    }}
    h1, h2 {{
      color: var(--accent);
    }}
    .card {{
      background: var(--card-bg);
      padding: 20px;
      border-radius: 10px;
      margin-bottom: 20px;
      border: 1px solid var(--border-color);
    }}
    .kpi {{
      display: flex;
      gap: 20px;
      flex-wrap: wrap;
    }}
    .kpi-item {{
      flex: 1;
      min-width: 180px;
      background: var(--card-bg);
      padding: 15px;
      border-radius: 8px;
      border: 1px solid var(--border-color);
    }}
    .filters {{
      display: flex;
      gap: 20px;
      flex-wrap: wrap;
      margin-bottom: 20px;
    }}
    .filters select {{
      padding: 6px 8px;
      border-radius: 6px;
      border: 1px solid var(--border-color);
      background: var(--card-bg);
      color: var(--text-color);
    }}
  </style>
</head>

<body class="dark">

  <div class="sidebar">
    <h2>Maintenance EP</h2>
    <button id="theme-toggle">Basculer clair / sombre</button>
    <hr style="margin:20px 0; border-color:#374151;">
    <p><strong>Sections :</strong></p>
    <ul style="list-style:none; padding-left:0;">
      <li><a href="#kpi" style="color:#e5e7eb; text-decoration:none;">KPI</a></li>
      <li><a href="#volume" style="color:#e5e7eb; text-decoration:none;">Volume</a></li>
      <li><a href="#top" style="color:#e5e7eb; text-decoration:none;">Top réparations</a></li>
      <li><a href="#repartition" style="color:#e5e7eb; text-decoration:none;">Répartitions</a></li>
      <li><a href="#heat" style="color:#e5e7eb; text-decoration:none;">Heatmap</a></li>
      <li><a href="#evol" style="color:#e5e7eb; text-decoration:none;">Évolution</a></li>
      <li><a href="#cross" style="color:#e5e7eb; text-decoration:none;">Activité × Ouvrage</a></li>
    </ul>
  </div>

  <div class="content">

    <h1>Dashboard Maintenance Éclairage Public</h1>

    <div id="kpi" class="card">
      <h2>Indicateurs clés</h2>
      <div class="kpi">
        <div class="kpi-item"><h3>Total interventions</h3><p>{total_interventions}</p></div>
        <div class="kpi-item"><h3>Total réparations</h3><p>{total_reparations}</p></div>
        <div class="kpi-item"><h3>Réparation dominante</h3><p>{top_reparation}</p></div>
        <div class="kpi-item"><h3>Activité dominante</h3><p>{top_activite}</p></div>
      </div>
    </div>

    <div class="card">
      <h2>Filtres (visuels uniquement)</h2>
      <div class="filters">
        <select><option>Toutes années</option></select>
        <select><option>Toutes activités</option></select>
        <select><option>Tous ouvrages</option></select>
        <select><option>Toutes réparations</option></select>
      </div>
    </div>

    <div id="volume" class="card">
      <h2>Interventions par mois</h2>
      {to_html(fig_mois, include_plotlyjs=False, full_html=False)}
    </div>

    <div id="top" class="card">
      <h2>Top réparations</h2>
      {to_html(fig_top_rep, include_plotlyjs=False, full_html=False)}
    </div>

    <div id="repartition" class="card">
      <h2>Répartition par activité</h2>
      {to_html(fig_activite, include_plotlyjs=False, full_html=False)}
      <h2>Répartition par type d’ouvrage</h2>
      {to_html(fig_type_ouvrage, include_plotlyjs=False, full_html=False)}
    </div>

    <div id="heat" class="card">
      <h2>Heatmap réparations</h2>
      {to_html(fig_heat, include_plotlyjs=False, full_html=False)}
    </div>

    <div id="evol" class="card">
      <h2>Évolution des réparations</h2>
      {to_html(fig_evol, include_plotlyjs=False, full_html=False)}
    </div>

    <div id="cross" class="card">
      <h2>Activité × Type d’ouvrage</h2>
      {to_html(fig_cross, include_plotlyjs=False, full_html=False)}
    </div>

  </div>

  <script>
    document.getElementById('theme-toggle').addEventListener('click', () => {{
      document.body.classList.toggle('light');
    }});
  </script>

</body>
</html>
"""

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html_page)

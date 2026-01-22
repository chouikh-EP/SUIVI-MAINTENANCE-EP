# 📊 Dashboard Automatisé — Suivi Maintenance Éclairage Public

Ce projet fournit un tableau de bord complet et automatisé pour analyser les interventions de maintenance en Éclairage Public (EP).  
Il transforme un simple fichier CSV brut en un dashboard interactif, moderne et mis à jour automatiquement via GitHub Actions.

---

## 🚀 Fonctionnalités principales

### 🔧 1. Détection automatique des réparations
Le script `detect_operations.py` analyse la colonne **Observation** et identifie automatiquement les opérations réalisées grâce à un dictionnaire métier (fusible, LED, driver, câblage, etc.).

Il génère :
- des colonnes oui/non pour chaque type d’intervention
- une colonne synthétique `resume_ia`
- un fichier enrichi : **Compte-rendu_enrichi.csv**

---

### 📈 2. Dashboard interactif moderne
Le script `generate_dashboard.py` produit un tableau de bord complet basé sur :

- `Date Intervention`
- `Activité`
- `Type d'ouvrage`
- `resume_ia`

Le dashboard inclut :
- KPI (indicateurs clés)
- Histogramme mensuel
- Top réparations
- Répartition par activité
- Répartition par type d’ouvrage
- Heatmap Mois × Réparation
- Évolution temporelle
- Analyse croisée Activité × Type d’ouvrage
- **Filtres interactifs (année, activité, type d’ouvrage)**

Le résultat final est un fichier **index.html** publié automatiquement sur GitHub Pages.

---

## 🔄 Pipeline GitHub Actions

Le workflow `.github/workflows/build.yml` exécute automatiquement :

1. `detect_operations.py`  
2. `generate_dashboard.py`  
3. Publication sur la branche `gh-pages`

Chaque mise à jour du CSV brut déclenche automatiquement la mise à jour du dashboard.

---

## 📁 Structure du projet

```
/
├── detect_operations.py
├── generate_dashboard.py
├── Compte-rendu 01.01.2026-21.01.2026.csv
├── Compte-rendu_enrichi.csv (généré automatiquement)
├── index.html (généré automatiquement)
└── .github/workflows/build.yml
```

---

## 🔧 Mise à jour des données

Pour mettre à jour le dashboard :

1. Remplacer le fichier CSV brut
2. Commit + push
3. GitHub Actions régénère tout automatiquement
4. Le site GitHub Pages se met à jour

Aucune modification du code n’est nécessaire.

---

## 🌐 Accès au dashboard

Le tableau de bord est disponible à l’adresse :

```
https://github.com/chouikh-EP/SUIVI-MAINTENANCE-EP.git
```

---

## 🧩 Améliorations possibles

- Ajout de filtres avancés
- Analyse multi-annuelle
- Détection automatique des anomalies
- Intégration cartographique (si coordonnées disponibles)

---

## 👤 M.CHOUIKH

Projet développé pour optimiser le suivi de la maintenance EP, automatiser l’analyse des interventions et fournir un outil d’aide à la décision moderne et fiable.

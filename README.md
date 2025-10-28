## 💳 Gestionnaire d’Abonnements

Application **Streamlit** permettant de **gérer, visualiser et analyser ses abonnements** (Netflix, Spotify, etc.) avec **sauvegarde locale en JSON**.
---

## 🎯 Objectif du projet
Beaucoup d’utilisateurs oublient leurs abonnements, ce qui provoque des paiements inutiles.
Cette application a pour objectif de centraliser, suivre et visualiser tous les abonnements récurrents de manière claire et interactive.

---

## 🚀 Fonctionnalités principales

- **Ajout, affichage et suppression** d’abonnements.
- **Tableau de bord interactif** avec indicateurs clés :
  - Nombre d’abonnements actifs / résiliés.
  - Coût mensuel et annuel total.
  - Renouvellements à venir (7 jours).
- **Visualisations graphiques** avec Plotly :
  - Répartition des abonnements par catégorie.
  - Top 3 des abonnements les plus coûteux.
- **Filtres dynamiques** (nom, catégorie, statut).
- **Sauvegarde locale automatique** dans `data/subscriptions.json`.
- **Thème sombre moderne** et responsive.

---

## 🧰 Technologies utilisées

| Composant         | Description |
|-------------------|-------------|
| **Python**        | Langage principal |
| **Streamlit**     | Interface web interactive |
| **Pandas**        | Gestion et analyse de données |
| **Plotly Express**| Graphiques dynamiques |
| **Dateutil**      | Gestion des fréquences et intervalles |
| **JSON**          | Stockage local des abonnements |

---

## 🗂️ Structure du projet

gestionnaire-abonnements/

├── app.py                    # Script principal

├── requirements.txt           # Liste des dépendances

├── README.md                  # Documentation du projet

└── data/
    └── subscriptions.json     # Fichier de stockage local (auto-généré)

---

## 💡 Notes techniques

Les fréquences d’abonnement disponibles :

Mensuel, Trimestriel, Annuel.

Les paiements, catégories et services sont pré-remplis mais personnalisables.

Les données sont stockées localement (pas de base de données requise).

Compatible avec Windows, macOS et Linux.

---

## 🚀 Installation et exécution

1️⃣ Cloner le projet :

git clone https://github.com/guedri-oussama/gestionnaire_abonnements.git

2️⃣ Installer les librairies nécessaires :

pip install -r requirements.txt

3️⃣ Lancer l’application :

streamlit run app.py

4️⃣ Ouvrir ton navigateur sur http://localhost:8501

---

## 🧠 Auteurs

👤 Oussama GUEDRI
👤 Bernard DRUI
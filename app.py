# ============================================================
# 💳 GESTIONNAIRE D’ABONNEMENTS — GUEDRI Oussama & DRUI Bernard
# ============================================================
# Application Streamlit permettant de gérer, visualiser et analyser
# ses abonnements (Netflix, Spotify, etc.)
# avec sauvegarde locale en JSON.
# ------------------------------------------------------------

# ------------------------------------------------------------
# 📦 IMPORTS DES LIBRAIRIES
# ------------------------------------------------------------
import os, json                            # Pour gérer le stockage local (fichier JSON)
from datetime import datetime, date        # Pour manipuler les dates
from dateutil.relativedelta import relativedelta  # Pour les fréquences (mensuel, annuel…)
import pandas as pd                        # Pour le traitement de données
import streamlit as st                     # Pour l’interface utilisateur
import plotly.express as px                # Pour les graphiques interactifs


# ------------------------------------------------------------
# ⚙️ CONFIGURATION DE BASE
# ------------------------------------------------------------
st.set_page_config(
    page_title="Gestion Abonnements",      # Titre de l’application
    page_icon="💳",                        # Icône de l’onglet navigateur
    layout="wide"                          # Mise en page large
)

DATA_FILE = "data/subscriptions.json"      # Fichier JSON de stockage local

# --- Définition des fréquences d’abonnement ---
FREQUENCES = {
    "Mensuel":      {"libellé": "Mois",       "facteur": 1.0,  "delta": relativedelta(months=1)},
    "Trimestriel":  {"libellé": "Trimestre",  "facteur": 1/3,  "delta": relativedelta(months=3)},
    "Annuel":       {"libellé": "Annuel",     "facteur": 1/12, "delta": relativedelta(years=1)},
}

# --- Listes de référence pour les formulaires ---
SERVICES_POPULAIRES = [
    "Netflix","Amazon Prime","Disney+","Spotify","YouTube Premium","Canal+","Apple TV+",
    "Paramount+","Deezer","Molotov","Microsoft 365","Google One","Dropbox","iCloud",
    "Adobe Creative Cloud","PlayStation Plus","Xbox Game Pass","Le Monde","Coursera","Strava"
]
CATEGORIES = ["Divertissement","Productivité","Cloud","Presse","Jeux","Éducation","Sport","Musique","Vidéo"]
MOYENS_PAIEMENT = ["Carte bancaire","PayPal","Prélèvement automatique","Apple Pay","Google Pay","Virement"]


# ------------------------------------------------------------
# 🎨 STYLE GLOBAL (THEME SOMBRE)
# ------------------------------------------------------------
def apply_dark_theme():
    """Applique un thème sombre personnalisé à l’application Streamlit."""
    st.markdown("""
    <style>
      .stApp { background:#121826; color:#E4ECFA; font-family:Inter,system-ui,Segoe UI,Arial,sans-serif; }
      h1,h2,h3,h4 { color:#5FB3F0 !important; }
      .stMetric { background:#1E2738; padding:14px; border-radius:12px; }
      hr { border:1px solid #2C3E50; margin:16px 0; opacity:.55; }
      .small { color:#9FB5D1; font-size:.92rem; }
      .stButton>button { border:none; border-radius:9px; font-weight:700; padding:.45rem .9rem; }
      .btn-red { background:#E74C3C !important; color:#fff !important; }
      .btn-blue { background:#3B82F6 !important; color:#fff !important; }
      .btn-red:hover, .btn-blue:hover { filter:brightness(1.06); }
      .row-compact { padding:.35rem 0 .25rem 0; }
    </style>
    """, unsafe_allow_html=True)

apply_dark_theme()  # On applique le style dès le démarrage


# ------------------------------------------------------------
# 💾 GESTION DU STOCKAGE LOCAL (FICHIER JSON)
# ------------------------------------------------------------
def ensure_store():
    """Crée le dossier de stockage et le fichier JSON s’ils n’existent pas."""
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump([], f, ensure_ascii=False, indent=2)

def load_json():
    """Charge la liste des abonnements depuis le fichier JSON."""
    ensure_store()
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_json(items):
    """Enregistre la liste des abonnements dans le fichier JSON."""
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)


# ------------------------------------------------------------
# 📆 FONCTIONS DE CALCUL
# ------------------------------------------------------------
def next_renewal_from(start_str, freq_key):
    """Retourne la prochaine date de renouvellement selon la fréquence choisie."""
    try:
        d = datetime.strptime(start_str, "%Y-%m-%d").date()
    except Exception:
        return None
    delta = FREQUENCES.get(freq_key, FREQUENCES["Mensuel"])["delta"]
    today = date.today()
    while d <= today:
        d += delta
    return d.strftime("%Y-%m-%d")

def to_dataframe(items):
    """Convertit la liste JSON en DataFrame Pandas avec calculs financiers."""
    if not items:
        return pd.DataFrame()

    df = pd.DataFrame(items)

    # Colonnes manquantes → valeurs par défaut
    if "status" not in df.columns:
        df["status"] = "active"
    if "next_renewal" not in df.columns:
        df["next_renewal"] = df.apply(
            lambda r: next_renewal_from(str(r.get("start_date", date.today())), r.get("frequency", "Mensuel")),
            axis=1
        )

    # Nettoyage des données
    df["category"] = df["category"].fillna("Non catégorisé")
    df["cost"] = pd.to_numeric(df["cost"], errors="coerce").fillna(0.0)

    # Calcul du coût mensuel / annuel
    df["monthly_cost"] = df.apply(
        lambda r: round(r["cost"] * FREQUENCES.get(r.get("frequency", "Mensuel"), FREQUENCES["Mensuel"])["facteur"], 2),
        axis=1
    )
    df["annual_cost"] = (df["monthly_cost"] * 12).round(2)

    # Conversion des colonnes de dates
    if "start_date" in df.columns:
        df["start_date"] = pd.to_datetime(df["start_date"], errors="coerce").dt.date
    if "next_renewal" in df.columns:
        df["next_renewal"] = pd.to_datetime(df["next_renewal"], errors="coerce").dt.date

    return df


# ------------------------------------------------------------
# 📦 CHARGEMENT INITIAL
# ------------------------------------------------------------
subscriptions = load_json()
df = to_dataframe(subscriptions)


# ------------------------------------------------------------
# 🧭 NAVIGATION PRINCIPALE
# ------------------------------------------------------------
st.title("💳 Gestionnaire d’abonnements")
tab1, tab2, tab3 = st.tabs(["📊 Tableau de bord", "📋 Mes abonnements", "➕ Ajouter"])


# ============================================================
# 🟦 1️⃣ ONGLET : TABLEAU DE BORD
# ============================================================
with tab1:
    st.header("📊 Tableau de bord")

    # Palette de couleurs par catégorie
    PALETTE_CATEGORIES = {
        "Divertissement": "#5DADE2",
        "Productivité": "#9B8AFB",
        "Musique": "#7DCEA0",
        "Cloud": "#F1948A",
        "Sécurité": "#F7DC6F",
        "Éducation": "#A3E4D7",
        "Presse": "#D7BDE2",
        "Sport": "#F5B7B1",
        "Autre": "#BFC9CA"
    }

    if df.empty:
        st.info("👋 Aucun abonnement disponible. Commencez par ajouter votre premier abonnement.")
    else:
        now = pd.Timestamp.today()
        df_active = df[df["status"] == "active"]
        df_resilie = df[df["status"] == "cancelled"]

        renew_soon = df_active[
            (pd.to_datetime(df_active["next_renewal"]) <= now + pd.Timedelta(days=7))
        ]

        # ------------------------------------------------------------
        # 📈 INDICATEURS PRINCIPAUX (KPI)
        # ------------------------------------------------------------
        st.markdown("### 📈 Indicateurs principaux")

        st.markdown("""
        <style>
        .kpi-container {
            display: flex;
            flex-wrap: wrap;
            justify-content: space-between;
            align-items: stretch;
            gap: 20px;
            margin-top: 10px;
            margin-bottom: 25px;
        }
        .kpi-card {
            background-color: #1E2738;
            color: #E4ECFA;
            flex: 1;
            min-width: 220px;
            border-radius: 12px;
            padding: 20px;
            text-align: center;
            box-shadow: 0 0 8px rgba(0,0,0,0.3);
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }
        .kpi-card:hover {
            transform: translateY(-4px);
            box-shadow: 0 0 12px rgba(0,0,0,0.5);
        }
        .kpi-title {
            font-size: 1.1rem;
            color: #9FB5D1;
            margin-bottom: 8px;
        }
        .kpi-value {
            font-size: 2.3rem;
            font-weight: 700;
            margin: 5px 0;
        }
        .kpi-sub {
            color: #E74C3C;
            font-weight: 600;
            margin-top: 4px;
        }
        @media (max-width: 900px) {
            .kpi-container { flex-direction: column; align-items: center; }
            .kpi-card { width: 90%; }
        }
        </style>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="kpi-container">
          <div class="kpi-card">
            <div class="kpi-title">🟢 Abonnements actifs</div>
            <div class="kpi-value">{len(df_active)}</div>
            <div class="kpi-sub">⬇ {len(df_resilie)} résilié(s)</div>
          </div>
          <div class="kpi-card">
            <div class="kpi-title">💶 Total mensuel</div>
            <div class="kpi-value">{df_active['monthly_cost'].sum():.2f} €</div>
          </div>
          <div class="kpi-card">
            <div class="kpi-title">📅 Total annuel estimé</div>
            <div class="kpi-value">{df_active['annual_cost'].sum():.2f} €</div>
          </div>
          <div class="kpi-card">
            <div class="kpi-title">⚠️ À renouveler (7 jours)</div>
            <div class="kpi-value">{len(renew_soon)}</div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        st.divider()

        # ------------------------------------------------------------
        # 🔔 TABLEAU DES RENOUVELLEMENTS À VENIR
        # ------------------------------------------------------------
        st.markdown("### 🔔 Renouvellements à venir (7 prochains jours)")
        if not renew_soon.empty:
            renew_display = renew_soon[["name", "category", "monthly_cost", "next_renewal"]].copy()
            renew_display.columns = ["Service", "Catégorie", "Mensuel (€)", "Renouvellement"]
            renew_display["Mensuel (€)"] = renew_display["Mensuel (€)"].round(2)
            renew_display = renew_display.reset_index(drop=True)

            st.dataframe(
                renew_display.style.format({"Mensuel (€)": "{:.2f}"}).set_table_styles([
                    {'selector': 'th', 'props': [('background-color', '#1E2738'), ('color', '#E4ECFA'),
                                                 ('text-align', 'left'), ('font-weight', '600')]},
                    {'selector': 'td', 'props': [('background-color', '#0E1117'), ('color', '#E4ECFA'),
                                                 ('text-align', 'left'), ('padding', '6px 10px')]},
                    {'selector': 'tr:nth-child(even)', 'props': [('background-color', '#121826')]},
                    {'selector': 'tr:hover', 'props': [('background-color', '#1B2330')]}
                ]),
                use_container_width=True,
                hide_index=True
            )
        else:
            st.success("✅ Aucun renouvellement prévu dans les 7 prochains jours.")

        st.divider()

        # ------------------------------------------------------------
        # 🧭 GRAPHIQUES DE RÉPARTITION — alignés côte à côte
        # ------------------------------------------------------------
        st.markdown("### 🧭 Vue d’ensemble des abonnements")

        col1, col2 = st.columns(2, gap="large")

        # === Graphe 1 : Répartition par catégorie ===
        with col1:
            st.markdown("<h4 style='text-align:center; color:white;'>Répartition par catégorie</h4>", unsafe_allow_html=True)
            pie_data = df_active.groupby("category")["monthly_cost"].sum().reset_index()

            fig_pie = px.pie(
                pie_data,
                names="category",
                values="monthly_cost",
                color="category",
                color_discrete_map=PALETTE_CATEGORIES,
                hole=0.45
            )
            fig_pie.update_traces(
                textposition="inside",
                textinfo="percent+label",
                hovertemplate="<b>%{label}</b><br>%{value:.2f} € (%{percent})<extra></extra>"
            )
            fig_pie.update_layout(
                showlegend=True,
                legend_title_text="Catégorie",
                legend=dict(font=dict(color="white")),
                paper_bgcolor="#0E1117",
                plot_bgcolor="#0E1117",
                font=dict(color="white", size=13),
                margin=dict(t=20, b=20, l=20, r=20),
                height=420
            )
            st.plotly_chart(fig_pie, use_container_width=True)

        # === Graphe 2 : Top 3 abonnements les plus chers ===
        with col2:
            st.markdown("<h4 style='text-align:center; color:white;'>Top 3 des abonnements les plus chers</h4>", unsafe_allow_html=True)
            top3 = (
                df_active.sort_values("monthly_cost", ascending=False)
                .head(3)[["name", "category", "monthly_cost"]]
            )

            fig_top3 = px.bar(
                top3,
                x="monthly_cost",
                y="name",
                orientation="h",
                text="monthly_cost",
                color="category",
                color_discrete_map=PALETTE_CATEGORIES,
                labels={"name": "Abonnement", "monthly_cost": "Coût mensuel (€)", "category": "Catégorie"}
            )
            fig_top3.update_traces(
                texttemplate="%{text:.2f} €",
                textposition="outside",
                hovertemplate="<b>%{y}</b><br>%{x:.2f} €<extra></extra>"
            )
            fig_top3.update_layout(
                height=420,
                showlegend=True,
                legend_title_text="Catégorie",
                legend=dict(font=dict(color="white")),
                xaxis_title="Coût mensuel (€)",
                yaxis_title=None,
                paper_bgcolor="#0E1117",
                plot_bgcolor="#0E1117",
                font=dict(color="white", size=13),
                margin=dict(t=20, b=20, l=40, r=20)
            )
            st.plotly_chart(fig_top3, use_container_width=True)

        st.divider()

        # ------------------------------------------------------------
        # 📋 ANALYSE PAR CATÉGORIE
        # ------------------------------------------------------------
        st.markdown("### 📋 Analyse par catégorie")
        cat_summary = (
            df_active.groupby("category")
            .agg({"name": "count", "monthly_cost": "sum", "annual_cost": "sum"})
            .reset_index()
        )
        cat_summary.columns = ["Catégorie", "Nombre", "Mensuel (€)", "Annuel (€)"]
        cat_summary["Mensuel (€)"] = cat_summary["Mensuel (€)"].round(2)
        cat_summary["Annuel (€)"] = cat_summary["Annuel (€)"].round(2)

        st.dataframe(
            cat_summary.style.format({
                "Mensuel (€)": "{:.2f}",
                "Annuel (€)": "{:.2f}"
            }).set_table_styles([
                {'selector': 'th', 'props': [('background-color', '#1E2738'), ('color', '#E4ECFA'),
                                             ('text-align', 'left'), ('font-weight', '600')]},
                {'selector': 'td', 'props': [('background-color', '#0E1117'), ('color', '#E4ECFA'),
                                             ('text-align', 'left'), ('padding', '6px 10px')]},
                {'selector': 'tr:nth-child(even)', 'props': [('background-color', '#121826')]},
                {'selector': 'tr:hover', 'props': [('background-color', '#1B2330')]}
            ]),
            use_container_width=True,
            hide_index=True
        )


# ============================================================
# 🟦 2️⃣ ONGLET : MES ABONNEMENTS
# ============================================================
# → Liste filtrable et actions sur les abonnements
with tab2:
    st.header("📋 Mes abonnements")

    if df.empty:
        st.info("Aucun abonnement pour l’instant.")
    else:
        # --- Filtres interactifs ---
        colf1, colf2, colf3 = st.columns([2, 1, 1])
        with colf1:
            q = st.text_input("🔎 Rechercher (nom ou catégorie)", "")
        with colf2:
            fstatus = st.selectbox("Statut", ["Tous", "Actifs", "Résiliés"])
        with colf3:
            fcat = st.selectbox("Catégorie", ["Toutes"] + sorted(df["category"].unique().tolist()))

        # Application des filtres
        dff = df.copy()
        if q:
            dff = dff[dff["name"].str.contains(q, case=False, na=False) |
                      dff["category"].str.contains(q, case=False, na=False)]
        if fstatus == "Actifs":
            dff = dff[dff["status"] == "active"]
        elif fstatus == "Résiliés":
            dff = dff[dff["status"] == "cancelled"]
        if fcat != "Toutes":
            dff = dff[dff["category"] == fcat]

        # Affichage du total filtré
        total_m = dff["monthly_cost"].sum()
        st.markdown(f"**{len(dff)} abonnement(s) trouvé(s) — Total mensuel : {total_m:.2f} €**")

        # --- Liste des abonnements filtrés ---
        if dff.empty:
            st.info("Aucun résultat.")
        else:
            for _, r in dff.sort_values("name").iterrows():
                with st.container():
                    c1, c2, c3 = st.columns([3, 1.2, 0.8])
                    icon = "🟢" if r["status"] == "active" else "🔴"

                    # Infos principales
                    c1.markdown(f"**{icon} {r['name']}**")
                    c1.markdown(
                        f"<span class='small'>🏷️ {r['category']} &nbsp;|&nbsp; 💳 {r.get('payment_method','—')}</span>",
                        unsafe_allow_html=True
                    )

                    # Coût selon la fréquence
                    freq_label = FREQUENCES.get(r["frequency"], FREQUENCES["Mensuel"])["libellé"]
                    c2.markdown(f"**{r['cost']:.2f} € / {freq_label}**")

                    # --- Actions (Résilier / Supprimer) ---
                    if r["status"] == "active":
                        if c3.button("🚫 Résilier", key=f"cancel_{r.get('id', r['name'])}", use_container_width=True):
                            for s in subscriptions:
                                sid = s.get("id", s.get("name"))
                                if sid == r.get("id", r["name"]):
                                    s["status"] = "cancelled"
                                    break
                            save_json(subscriptions)
                            st.rerun()
                        st.markdown(
                            "<style>div[data-testid='stButton'] button {background:#E74C3C; color:white;}</style>",
                            unsafe_allow_html=True
                        )
                    else:
                        if c3.button("🗑️ Supprimer", key=f"del_{r.get('id', r['name'])}", use_container_width=True):
                            key = r.get("id", r["name"])
                            subscriptions[:] = [s for s in subscriptions if s.get("id", s.get("name")) != key]
                            save_json(subscriptions)
                            st.rerun()
                        st.markdown(
                            "<style>div[data-testid='stButton'] button {background:#3B82F6; color:white;}</style>",
                            unsafe_allow_html=True
                        )

                # Ligne de séparation
                st.markdown("<div class='row-compact'><hr></div>", unsafe_allow_html=True)


# ============================================================
# 🟦 3️⃣ ONGLET : AJOUT D'UN ABONNEMENT
# ============================================================
with tab3:
    st.header("➕ Ajouter un nouvel abonnement")

    with st.form("add_sub", clear_on_submit=True):
        # --- Section 1 : Informations générales ---
        st.markdown("### 🧾 Informations générales")
        col1, col2 = st.columns(2)

        # Nom du service
        with col1:
            st.markdown("**Nom du service**")
            st.write("Sélectionnez un service")
            service_choice = st.selectbox("", sorted(SERVICES_POPULAIRES))
            name_custom = st.text_input("Ou saisissez un nom personnalisé", placeholder="Ex : Mon service perso")
            name = name_custom.strip() if name_custom else service_choice

        # Catégorie
        with col2:
            st.markdown("**Catégorie**")
            st.write("Sélectionnez une catégorie")
            category_choice = st.selectbox("", sorted(CATEGORIES))
            category_custom = st.text_input("Ou saisissez une catégorie personnalisée", placeholder="Ex : Streaming, Fitness…")
            category = category_custom.strip() if category_custom else category_choice

        # --- Section 2 : Informations financières ---
        st.markdown("### 💰 Informations financières")
        col3, col4, col5 = st.columns(3)
        with col3:
            cost = st.number_input("Coût (€)", min_value=0.0, step=0.01, format="%.2f")
        with col4:
            frequency = st.selectbox("Fréquence", list(FREQUENCES.keys()))
        with col5:
            start_date = st.date_input("Date de début", value=date.today())

        # --- Section 3 : Mode de paiement ---
        st.markdown("### 💳 Mode de paiement")
        st.write("Sélectionnez un mode de paiement")
        payment_choice = st.selectbox("", sorted(MOYENS_PAIEMENT))
        payment_custom = st.text_input("Ou saisissez un mode de paiement personnalisé", placeholder="Ex : Carte cadeau…")
        payment_method = payment_custom.strip() if payment_custom else payment_choice

        # --- Notes et enregistrement ---
        notes = st.text_area("Notes (optionnel)", placeholder="Ajoutez des informations complémentaires…")
        submit = st.form_submit_button("✅ Enregistrer", use_container_width=True)

        if submit:
            # Validation des champs obligatoires
            if not name or not category or cost <= 0:
                st.error("❌ Merci de remplir tous les champs obligatoires.")
            else:
                subs = load_json()
                new_id = max([s.get("id", 0) for s in subs] + [0]) + 1
                start_str = start_date.strftime("%Y-%m-%d")
                next_ren = next_renewal_from(start_str, frequency)
                new = {
                    "id": new_id,
                    "name": name,
                    "category": category,
                    "cost": float(cost),
                    "frequency": frequency,
                    "start_date": start_str,
                    "next_renewal": next_ren,
                    "payment_method": payment_method,
                    "notes": notes,
                    "status": "active",
                    "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                subs.append(new)
                save_json(subs)
                st.success(f"✅ Abonnement « {name} » ajouté avec succès.")
                st.rerun()


# ============================================================
# 🧾 PIED DE PAGE
# ============================================================
st.markdown(
    """
    <hr style="border: 1px solid #2C3E50; margin-top: 2rem; margin-bottom: 1rem; opacity: 0.6;">
    <div style='text-align: center; color: #AAB7C4; padding: 10px 0; font-size: 0.9rem;'>
        💰 <b>Gestionnaire d'Abonnements</b> | Réalisé par 
        <b>Oussama GUEDRI</b> & <b>Bernard DRUI</b>
    </div>
    """,
    unsafe_allow_html=True)


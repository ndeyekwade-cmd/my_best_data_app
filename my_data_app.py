import streamlit as st
import pandas as pd
from PIL import Image
import requests
from io import BytesIO

# Configuration de la page
st.set_page_config(
    page_title="Annonces Chiens - Coinafrique",
    page_icon="🐕",
    layout="wide"
)

# Titre principal
st.title("🐕 Annonces de Chiens - Coinafrique Sénégal")
st.markdown("---")

# Charger les données (assumant que df_chiens existe déjà)
# Si vous avez sauvegardé en CSV: df_chiens = pd.read_csv('chiens_coinafrique.csv')

# Afficher les statistiques
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total d'annonces", len(df_chiens))
with col2:
    if 'price' in df_chiens.columns:
        # Nettoyer les prix pour calculer la moyenne
        df_temp = df_chiens.copy()
        df_temp['price_clean'] = df_temp['price'].str.replace('CFA', '').str.replace(' ', '').str.replace(',', '')
        prices_numeric = pd.to_numeric(df_temp['price_clean'], errors='coerce')
        avg_price = prices_numeric.mean()
        st.metric("Prix moyen", f"{avg_price:,.0f} CFA" if not pd.isna(avg_price) else "N/A")
with col3:
    if 'address' in df_chiens.columns:
        unique_locations = df_chiens['address'].nunique()
        st.metric("Localisations", unique_locations)

st.markdown("---")

# Sidebar pour les filtres
st.sidebar.header("🔍 Filtres")

# Filtre par localisation
if 'address' in df_chiens.columns:
    locations = ['Toutes'] + sorted(df_chiens['address'].dropna().unique().tolist())
    selected_location = st.sidebar.selectbox("Localisation", locations)
else:
    selected_location = 'Toutes'

# Filtre par prix
if 'price' in df_chiens.columns:
    st.sidebar.subheader("Prix")
    df_temp = df_chiens.copy()
    df_temp['price_clean'] = df_temp['price'].str.replace('CFA', '').str.replace(' ', '').str.replace(',', '')
    df_temp['price_numeric'] = pd.to_numeric(df_temp['price_clean'], errors='coerce')
    
    min_price = int(df_temp['price_numeric'].min()) if not df_temp['price_numeric'].isna().all() else 0
    max_price = int(df_temp['price_numeric'].max()) if not df_temp['price_numeric'].isna().all() else 1000000
    
    price_range = st.sidebar.slider(
        "Fourchette de prix (CFA)",
        min_value=min_price,
        max_value=max_price,
        value=(min_price, max_price)
    )

# Recherche par mot-clé
search_term = st.sidebar.text_input("🔎 Rechercher dans les annonces", "")

# Appliquer les filtres
df_filtered = df_chiens.copy()

if selected_location != 'Toutes':
    df_filtered = df_filtered[df_filtered['address'] == selected_location]

if 'price' in df_chiens.columns:
    df_filtered['price_clean'] = df_filtered['price'].str.replace('CFA', '').str.replace(' ', '').str.replace(',', '')
    df_filtered['price_numeric'] = pd.to_numeric(df_filtered['price_clean'], errors='coerce')
    df_filtered = df_filtered[
        (df_filtered['price_numeric'] >= price_range[0]) & 
        (df_filtered['price_numeric'] <= price_range[1])
    ]

if search_term:
    df_filtered = df_filtered[df_filtered['name'].str.contains(search_term, case=False, na=False)]

st.sidebar.markdown(f"**{len(df_filtered)}** annonces trouvées")

# Affichage des annonces
st.subheader(f"📋 Annonces ({len(df_filtered)} résultats)")

# Option d'affichage
view_type = st.radio("Type d'affichage", ["Grille", "Liste"], horizontal=True)

if view_type == "Grille":
    # Affichage en grille (3 colonnes)
    cols_per_row = 3
    for i in range(0, len(df_filtered), cols_per_row):
        cols = st.columns(cols_per_row)
        for j in range(cols_per_row):
            if i + j < len(df_filtered):
                row = df_filtered.iloc[i + j]
                with cols[j]:
                    with st.container():
                        st.markdown(f"**{row['name']}**")
                        
                        # Afficher l'image
                        if pd.notna(row['image_link']) and row['image_link']:
                            try:
                                st.image(row['image_link'], use_container_width=True)
                            except:
                                st.info("Image non disponible")
                        
                        st.markdown(f"💰 **{row['price']}**")
                        st.markdown(f"📍 {row['address']}")
                        st.markdown("---")
else:
    # Affichage en liste
    for idx, row in df_filtered.iterrows():
        with st.expander(f"{row['name']} - {row['price']}"):
            col1, col2 = st.columns([1, 2])
            with col1:
                if pd.notna(row['image_link']) and row['image_link']:
                    try:
                        st.image(row['image_link'], use_container_width=True)
                    except:
                        st.info("Image non disponible")
            with col2:
                st.markdown(f"**Nom:** {row['name']}")
                st.markdown(f"**Prix:** {row['price']}")
                st.markdown(f"**Localisation:** {row['address']}")

# Section téléchargement
st.markdown("---")
st.subheader("📥 Télécharger les données")

# Bouton de téléchargement CSV
csv = df_filtered.to_csv(index=False).encode('utf-8')
st.download_button(
    label="Télécharger en CSV",
    data=csv,
    file_name='chiens_coinafrique_filtered.csv',
    mime='text/csv',
)

# Footer
st.markdown("---")
st.caption("Données scrapées depuis Coinafrique.com - Senegal")

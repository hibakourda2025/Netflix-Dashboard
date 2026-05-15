#!/usr/bin/env python
# coding: utf-8

# In[17]:


import pandas as pd
df = pd.read_csv("NetFlix.csv")


# In[18]:


#df.shape (7787 lignes, 12 colonnes)


# In[19]:


#df.dtypes les types des colonnes


# In[20]:


df['date_added'] = pd.to_datetime(df['date_added']) # Convertir la date en format convenable
df['year_added']  = df['date_added'].dt.year
df['month_added'] = df['date_added'].dt.month


# In[21]:


df.isnull().sum()


# In[22]:

df['director'] = df['director'].fillna('Unknown')
df['cast'] = df['cast'].fillna('Unknown')
df['rating'] = df['rating'].fillna(df['rating'].mode().item())
df=df.dropna()
#df.shape (7271 lignes, 13 colonnes)


# In[23]:

#les variables
min_year = int(df['release_year'].dropna().min())
max_year = int(df['release_year'].dropna().max())

countries = df['country'].str.split(',') # Séparer les pays (car plusieurs dans une même cellule)
all_countries = countries.explode().str.strip() #pour eviter les espaces avant les virgules
top_countries = all_countries.value_counts().head(50).index.tolist()

df['genres_list'] = df['genres'].str.split(', ')  # Separer les genres (car plusieurs dans une même cellule)
all_genres = sorted(df['genres_list'].explode().unique())
all_ratings = sorted(df['rating'].explode().unique())
df['duration_min'] = df.loc[df['type'] == 'Movie', 'duration']
df['nb_saisons']   = df.loc[df['type'] == 'TV Show', 'duration']



# In[24]:

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# page config
st.set_page_config(page_title="Netflix Dashboard",page_icon="🎬")

# theme css (Cascading Style Sheets)
st.markdown("""<style> @import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Inter:wght@300;400;500;600&display=swap');
/* Global */html, body, [class*="css"] {background-color: #0D0D0D;color: #E5E5E5;font-family: 'Inter', sans-serif;}
.stApp { background-color: #0D0D0D; }

/* Sidebar */
[data-testid="stSidebar"] {background: #141414;border-right: 1px solid #222;}
[data-testid="stSidebar"] .stMarkdown h1,[data-testid="stSidebar"] .stMarkdown h2,
[data-testid="stSidebar"] .stMarkdown h3 {color: #E50914;font-family: 'Bebas Neue', cursive;letter-spacing: 2px;}

/* Headers */
h1 { font-family: 'Bebas Neue', cursive !important; letter-spacing: 3px; color: #FFFFFF !important; }
h2, h3 { font-family: 'Bebas Neue', cursive !important; letter-spacing: 2px; color: #E50914 !important; }

/* Metric cards */
[data-testid="metric-container"] {background: #1A1A1A;border: 1px solid #2A2A2A;border-left: 3px solid #E50914;border-radius: 6px;padding: 12px 16px;}
[data-testid="metric-container"] label { color: #999 !important; font-size: 0.75rem !important; letter-spacing: 1px; text-transform: uppercase; }
[data-testid="metric-container"] [data-testid="stMetricValue"] { color: #FFFFFF !important; font-size: 1.8rem !important; font-weight: 600; }
[data-testid="metric-container"] [data-testid="stMetricDelta"] { color: #E50914 !important; }

/* Selectbox & Slider */
.stSelectbox > div > div, .stMultiSelect > div > div {background: #1A1A1A !important;border: 1px solid #333 !important;
color: #E5E5E5 !important;border-radius: 6px;}
.stSlider [data-baseweb="slider"] { color: #E50914; }

/* Divider */
hr { border-color: #222 !important; margin: 1.5rem 0; }

/* Tabs */
.stTabs [data-baseweb="tab-list"] { background: #141414; border-bottom: 2px solid #E50914; }
.stTabs [data-baseweb="tab"] { color: #999; font-family: 'Inter', sans-serif; font-weight: 500; }
.stTabs [aria-selected="true"] { color: #E50914 !important; border-bottom: 2px solid #E50914; }

/* Plot backgrounds */
.js-plotly-plot { border-radius: 8px; }

/* Section label */
.section-label {font-family: 'Bebas Neue', cursive; font-size: 0.85rem; letter-spacing: 3px; color: #E50914; text-transform: uppercase; margin-bottom: 4px;}
.page-title {font-family: 'Bebas Neue', cursive; font-size: 2.8rem; letter-spacing: 4px; color: #FFFFFF; line-height: 1; margin-bottom: 0;}
.page-subtitle {font-size: 0.9rem; color: #888; margin-top: 4px; margin-bottom: 24px;}
.kpi-strip {background: linear-gradient(135deg, #1A0000 0%, #1A1A1A 100%); border: 1px solid #2A0000; border-radius: 8px; padding: 16px; margin-bottom: 20px;}
</style>""", unsafe_allow_html=True)

# plotly template
PLOTLY_LAYOUT = dict(plot_bgcolor='#141414', paper_bgcolor='#141414', font=dict(color='#E5E5E5', family='Inter'),
    title_font=dict(color='#FFFFFF', family='Inter', size=14),
    colorway=['#E50914', '#B20710', '#F5F5F1', '#831010', '#FF6B6B','#C8102E', '#FF4444', '#666666', '#999999', '#CCCCCC'],
    xaxis=dict(gridcolor='#222', zerolinecolor='#333', tickfont=dict(color='#999')),
    yaxis=dict(gridcolor='#222', zerolinecolor='#333', tickfont=dict(color='#999')),
    legend=dict(bgcolor='#1A1A1A', bordercolor='#333', borderwidth=1),margin=dict(t=50, b=40, l=40, r=20),
)


# sidebar
with st.sidebar:
    st.markdown("## 🎬 NETFLIX ANALYTICS")
    st.markdown("---")

    # Navigation
    st.markdown('<div class="section-label">Navigation</div>', unsafe_allow_html=True)
    page = st.radio("", ["🏠 Vue Générale", "📊 Catalogue & Évolution", "🌍 Géographie & Diversité", "🎭 Genres & Ratings"], label_visibility="collapsed")

    st.markdown("---")
    st.markdown('<div class="section-label">Filtres Globaux</div>', unsafe_allow_html=True)

    # Filtre Type
    type_filter = st.multiselect("Type de contenu", options=["Movie", "TV Show"], default=["Movie", "TV Show"])

    # Filtre Année
    year_range = st.slider("Années de sortie", min_value=min_year, max_value=max_year, value=(2000, max_year))

    # Filtre Pays (top 50)
    country_filter = st.multiselect("Pays (top 50)", options=top_countries, default=[])

    # Filtre Genre
    genre_filter = st.multiselect("Genre", options=all_genres, default=[])

    # Filtre Rating
    rating_filter = st.multiselect("Rating",options=all_ratings,default=[])

    st.markdown("---")
    st.markdown('<p style="color:#555;font-size:0.75rem;text-align:center;">DS2 · Projet Data Science<br>Netflix Open Data Analysis</p>', unsafe_allow_html=True)

# application des filtres
dff = df.copy()
if type_filter:
    dff = dff[dff['type'].isin(type_filter)]
dff = dff[dff['release_year'].between(year_range[0], year_range[1])]
if country_filter:
    dff = dff[dff['country'].isin(country_filter)]
if genre_filter:
    dff = dff[dff['genres_list'].apply(lambda g: any(x in g for x in genre_filter))]
if rating_filter:
    dff = dff[dff['rating'].apply(lambda g: any(x in g for x in rating_filter))]


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 1 — VUE GÉNÉRALE
# ═══════════════════════════════════════════════════════════════════════════════
if page == "🏠 Vue Générale":
    st.markdown('<div class="page-title">TABLEAU DE BORD</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Analyse du catalogue Netflix — Vue d\'ensemble</div>', unsafe_allow_html=True)

    # KPIs
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Titres", f"{len(dff):,}")
    with col2:
        n_movies = len(dff[dff['type'] == 'Movie'])
        st.metric("Films", f"{n_movies:,}")
    with col3:
        n_series = len(dff[dff['type'] == 'TV Show'])
        st.metric("Séries", f"{n_series:,}")
    
    col4, col5, col6, col7 = st.columns(4)
    with col4:
        all_countriess = dff['country'].str.split(',').explode().str.strip()
        n_countries = all_countriess.nunique()
        st.metric("Pays représentés", f"{n_countries}")
    with col5:
        n_genres = dff['genres_list'].explode().nunique()
        st.metric("Genres uniques", f"{n_genres}")
    with col6:
        all_directors = dff['director'].str.split(',').explode().str.strip()
        n_directors = all_directors.nunique()
        st.metric("Nb Réalisateurs", f"{n_directors}")
    with col7:
        all_actors = dff['cast'].str.split(',').explode().str.strip()
        n_actors = all_actors.nunique()
        st.metric("Nb acteurs", f"{n_actors}")

    st.markdown("---")

    col_a, col_b = st.columns([1, 2])

    with col_a:
        # Donut Films vs Séries
        type_counts = dff['type'].value_counts()
        fig_donut = go.Figure(go.Pie(labels=type_counts.index, values=type_counts.values, hole=0.6, marker=dict(colors=['#E50914', '#444444'], 
        line=dict(color='#0D0D0D', width=2)),textfont=dict(color='#E5E5E5', size=13),))
        fig_donut.update_layout(**PLOTLY_LAYOUT, title="Films vs Séries", showlegend=True, annotations=[dict(
        text=f"{len(dff):,}<br><span style='font-size:10px'>titres</span>", x=0.5, y=0.5, font_size=18, showarrow=False, font_color='#FFF')])
        fig_donut.update_layout(legend=dict(orientation="h", y=-0.1, x=0.2))
        st.plotly_chart(fig_donut, use_container_width=True)
        movie_pct = type_counts.get('Movie', 0) / len(dff) * 100 if len(dff) > 0 else 0
        series_pct = type_counts.get('TV Show', 0) / len(dff) * 100 if len(dff) > 0 else 0
        ratio_diff = movie_pct - series_pct
        if ratio_diff > 50:
            st.write(f"Le catalogue est fortement dominé par les films ({movie_pct:.0f}%) par rapport aux séries ({series_pct:.0f}%), avec un écart de {ratio_diff:.0f}%. Cette concentration élevée suggère une offre peu diversifiée.")
        elif ratio_diff > 20:
            st.write(f"Les films ({movie_pct:.0f}%) sont majoritaires face aux séries ({series_pct:.0f}%), avec une différence de {ratio_diff:.0f}%. L'offre manque de diversité, favorisant nettement le format cinématographique.")
        else:
            st.write(f"L'équilibre entre films ({movie_pct:.0f}%) et séries ({series_pct:.0f}%) est relativement équilibré avec un écart de {ratio_diff:.0f}%, reflétant une offre diversifiée et variée.")

    with col_b:
        # Évolution des ajouts par année
        evolution = dff.groupby(['year_added', 'type']).size().reset_index(name='count')
        evolution = evolution.dropna(subset=['year_added'])
        fig_evo = px.area(evolution, x='year_added', y='count', color='type', color_discrete_map={'Movie': '#E50914', 'TV Show': '#555555'},
            labels={'year_added': 'Année', 'count': 'Titres ajoutés', 'type': 'Type'})
        fig_evo.update_layout(**PLOTLY_LAYOUT, title="Évolution des ajouts au catalogue")
        fig_evo.update_traces(line_width=2)
        st.plotly_chart(fig_evo, use_container_width=True)
        year_totals = evolution.groupby('year_added')['count'].sum()
        if len(year_totals) > 0:
            peak_year = int(year_totals.idxmax())
            peak_count = int(year_totals.max())
            peak_movies = int(evolution[(evolution['year_added'] == peak_year) & (evolution['type'] == 'Movie')]['count'].sum())
            peak_series = int(evolution[(evolution['year_added'] == peak_year) & (evolution['type'] == 'TV Show')]['count'].sum())
            avg_count = int(year_totals.mean())
            peak_ratio = (peak_count / avg_count) if avg_count > 0 else 0
            if peak_series == 0:
                st.write(f"En {peak_year}, Netflix a atteint un pic majeur avec {peak_count:,} ajouts ({peak_movies:,} films, {peak_series:,} série), soit {peak_ratio:.1f}x la moyenne de {avg_count:,}. Cette croissance exceptionnelle était quasi exclusivement centrée sur les films.")
            else:
                movie_pct_peak = (peak_movies / peak_count * 100) if peak_count > 0 else 0
                series_pct_peak = (peak_series / peak_count * 100) if peak_count > 0 else 0
                st.write(f"En {peak_year}, Netflix a atteint un pic majeur avec {peak_count:,} ajouts ({peak_movies:,} films [{movie_pct_peak:.0f}%], {peak_series:,} séries [{series_pct_peak:.0f}%]), soit {peak_ratio:.1f}x la moyenne annuelle de {avg_count:,}. Cette explosion était portée principalement par les {['films', 'séries'][1 if series_pct_peak > movie_pct_peak else 0]}.")

    st.markdown("---")


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 2 — CATALOGUE & ÉVOLUTION
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "📊 Catalogue & Évolution":
    st.markdown('<div class="page-title">CATALOGUE & ÉVOLUTION</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Axe 1 — Structure et croissance du catalogue Netflix</div>', unsafe_allow_html=True)

    # KPIs Axe 1
    col1, col2, col3, col4 = st.columns(4)
    movies = dff[dff['type'] == 'Movie']
    series = dff[dff['type'] == 'TV Show']
    with col1:
        avg_dur = movies['duration_min'].mean()
        st.metric("Durée Moy. Film", f"{avg_dur:.0f} min")
    with col2:
        avg_sai = series['nb_saisons'].mean()
        st.metric("Saisons Moy. Série", f"{avg_sai:.1f}")
    with col3:
        peak_year = dff.groupby('year_added').size().idxmax() if len(dff) > 0 else 0
        st.metric("Année de Pic", f"{int(peak_year)}")
    with col4:
        ratio = len(movies) / len(series) if len(series) > 0 else 0
        st.metric("Ratio Films/Séries", f"{ratio:.1f}x")

    st.markdown("---")

    # Évolution mensuelle/annuelle
    col_a, col_b = st.columns(2)

    with col_a:
        yearly = dff.groupby(['year_added', 'type']).size().reset_index(name='count').dropna(subset=['year_added'])
        fig_bar = px.bar(yearly, x='year_added', y='count', color='type', color_discrete_map={'Movie': '#E50914', 'TV Show': '#555555'},
            barmode='stack', labels={'year_added': 'Année', 'count': 'Titres ajoutés', 'type': 'Type'})
        fig_bar.update_layout(**PLOTLY_LAYOUT, title="Ajouts Annuels au Catalogue")
        st.plotly_chart(fig_bar, use_container_width=True)
        yearly_totals = yearly.groupby('year_added')['count'].sum()
        if len(yearly_totals) > 0:
            peak_year = int(yearly_totals.idxmax())
            peak_count = int(yearly_totals.max())
            st.write(f"Le catalogue gagne en moyenne {int(yearly_totals.mean()):,} titres par année, avec un maximum à environ {peak_count:,} ajouts en {peak_year}.")

    with col_b:
        # Saisonnalité mensuelle
        monthly = dff.groupby('month_added').size().reset_index(name='count').dropna(subset=['month_added'])
        month_names = {1:'Jan',2:'Fév',3:'Mar',4:'Avr',5:'Mai',6:'Jun',7:'Jul',8:'Aoû',9:'Sep',10:'Oct',11:'Nov',12:'Déc'}
        monthly['month_name'] = monthly['month_added'].map(month_names)
        fig_month = go.Figure(go.Bar(x=monthly['month_name'], y=monthly['count'], marker=dict(color=monthly['count'], colorscale=[[0,'#3A0000'],[1,'#E50914']], showscale=False),
            text=monthly['count'], textposition='outside', textfont=dict(color='#E5E5E5')))
        fig_month.update_layout(**PLOTLY_LAYOUT, title="Saisonnalité des Ajouts (par mois)")
        st.plotly_chart(fig_month, use_container_width=True)
        if len(monthly) > 0:
            top_month = monthly.loc[monthly['count'].idxmax()]
            total_monthly = monthly['count'].sum()
            st.write(f"Le mois le plus actif est {top_month['month_name']} avec environ {int(top_month['count']):,} ajouts, soit près de {top_month['count'] / total_monthly * 100:.0f}% des ajouts mensuels.")

    st.markdown("---")

    col_c, col_d = st.columns(2)

    with col_c:
        # Distribution durée films
        if len(movies) > 0:
            fig_dur = go.Figure(go.Histogram(x=movies['duration_min'].dropna(),nbinsx=40,marker=dict(color='#E50914', opacity=0.8, line=dict(color='#0D0D0D', width=0.5)),))
            fig_dur.add_vline(x=movies['duration_min'].mean(), line_dash="dash",line_color="#FFF", annotation_text=f"Moy: {movies['duration_min'].mean():.0f} min",annotation_font_color="#FFF")
            fig_dur.update_layout(**PLOTLY_LAYOUT, title="Distribution Durée des Films (min)", xaxis_title="Minutes", yaxis_title="Nombre de films")
            st.plotly_chart(fig_dur, use_container_width=True)
            mean_dur = movies['duration_min'].mean()
            st.write(f"La durée moyenne des films est d'environ {mean_dur:.0f} minutes, avec une forte concentration autour du format standard de 80 à 120 minutes.")

    with col_d:
        # Distribution saisons séries
        if len(series) > 0:
            sai_counts = series['nb_saisons'].dropna().value_counts().sort_index()
            fig_sai = go.Figure(go.Bar(x=sai_counts.index.astype(int), y=sai_counts.values, marker=dict(color='#555', line=dict(color='#E50914', width=1)),
                text=sai_counts.values, textposition='outside', textfont=dict(color='#E5E5E5')))
            fig_sai.update_layout(**PLOTLY_LAYOUT, title="Nombre de Saisons par Série", xaxis_title="Saisons", yaxis_title="Nombre de séries")
            st.plotly_chart(fig_sai, use_container_width=True)
            if len(sai_counts) > 0:
                top_season = int(sai_counts.idxmax())
                top_season_count = int(sai_counts.max())
                st.write(f"Le format le plus courant est {top_season} saison(s), avec environ {top_season_count:,} séries de cette longueur.")

    # Croissance cumulée
    cumul = dff.groupby('year_added').size().reset_index(name='count').dropna(subset=['year_added'])
    cumul = cumul.sort_values('year_added')
    cumul['cumul'] = cumul['count'].cumsum()
    fig_cumul = go.Figure()
    fig_cumul.add_trace(go.Scatter(x=cumul['year_added'], y=cumul['cumul'], mode='lines+markers', line=dict(color='#E50914', width=3),
        marker=dict(color='#E50914', size=6), fill='tozeroy', fillcolor='rgba(229,9,20,0.1)', name='Titres cumulés'))
    fig_cumul.update_layout(**PLOTLY_LAYOUT, title="Croissance Cumulée du Catalogue", xaxis_title="Année", yaxis_title="Total titres")
    st.plotly_chart(fig_cumul, use_container_width=True)
    if not cumul.empty:
        total_titles = int(cumul['cumul'].iloc[-1])
        st.write(f"À la fin de la période, le catalogue atteint environ {total_titles:,} titres cumulés, montrant une progression constante.")


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 3 — GÉOGRAPHIE & DIVERSITÉ
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "🌍 Géographie & Diversité":
    st.markdown('<div class="page-title">GÉOGRAPHIE & DIVERSITÉ</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Axe 2 — Distribution mondiale de la production Netflix</div>', unsafe_allow_html=True)

    # KPIs
    col1, col2, col3 = st.columns(3)
    us_pct = len(dff[dff['country'] == 'United States']) / len(dff) * 100 if len(dff) > 0 else 0
    intl_pct = 100 - us_pct
    top_country = dff['country'].str.split(',').explode().str.strip().value_counts().idxmax() if len(dff) > 0 else "N/A"
    with col1:
        nb_countries=dff['country'].str.split(',').explode().str.strip().nunique()
        st.metric("Pays représentés", nb_countries)
    with col2:
        st.metric("Part US", f"{us_pct:.1f}%")
    with col3:
        st.metric("Part Internationale", f"{intl_pct:.1f}%")

    st.markdown("---")

    # Carte choroplèthe
    country_count = dff['country'].str.split(',').explode().str.strip().value_counts().reset_index()
    country_count.columns = ['country', 'count']

    fig_map = px.choropleth(country_count, locations='country', locationmode='country names', color='count',
    color_continuous_scale=[[0, '#1A0000'], [0.3, '#6B0000'], [0.7, '#B20710'], [1, '#E50914']], labels={'count': 'Nombre de titres'})
    fig_map.update_layout(**PLOTLY_LAYOUT,title="Répartition Mondiale de la Production Netflix",
        geo=dict(showframe=False, showcoastlines=True, coastlinecolor='#333', bgcolor='#141414', landcolor='#1A1A1A',
            oceancolor='#0D0D0D', showocean=True, lakecolor='#0D0D0D', projection_type='natural earth'),
        coloraxis_colorbar=dict(bgcolor='#141414',tickfont=dict(color='#E5E5E5'),title=dict(font=dict(color='#E5E5E5'))),height=420)
    st.plotly_chart(fig_map, use_container_width=True)
    st.write(f"La carte montre une production très concentrée : environ {us_pct:.1f}% des titres proviennent des États-Unis, tandis que le reste est réparti dans le monde.")

    st.markdown("---")

    col_a, col_b = st.columns(2)

    with col_a:
        # Top 15 pays
        top15 = dff['country'].str.split(',').explode().str.strip().value_counts().head(15)
        fig_top = go.Figure(go.Bar(x=top15.values[::-1], y=top15.index[::-1], orientation='h',
            marker=dict(color=list(range(15)), colorscale=[[0, '#2A0000'], [1, '#E50914']], showscale=False),
            text=top15.values[::-1], textposition='outside', textfont=dict(color='#E5E5E5', size=11)))
        fig_top.update_layout(**PLOTLY_LAYOUT, title="Top 15 Pays Producteurs", xaxis_title="Nombre de titres", height=460)
        st.plotly_chart(fig_top, use_container_width=True)
        if len(top15) > 0:
            top_country = top15.index[0]
            top_count = int(top15.iloc[0])
            st.write(f"Le pays en tête est {top_country} avec environ {top_count:,} titres, soit nettement plus que les autres pays du top 15.")

    with col_b:
        # US vs International par type
        dff_geo = dff.copy()
        dff_geo['origin'] = dff_geo['country'].apply(lambda x: 'États-Unis' if x == 'United States' else ('Inconnu' if x == 'Unknown' else 'International'))
        origin_type = dff_geo.groupby(['origin', 'type']).size().reset_index(name='count')
        fig_orig = px.bar(origin_type[origin_type['origin'] != 'Inconnu'], x='origin', y='count', color='type',
            color_discrete_map={'Movie': '#E50914', 'TV Show': '#555555'}, barmode='group', labels={'origin': 'Origine', 'count': 'Titres', 'type': 'Type'})
        fig_orig.update_layout(**PLOTLY_LAYOUT, title="US vs International par Type", height=460)
        st.plotly_chart(fig_orig, use_container_width=True)
        us_count = int(origin_type[origin_type['origin'] == 'États-Unis']['count'].sum())
        intl_count = int(origin_type[origin_type['origin'] == 'International']['count'].sum())
        st.write(f"Le contenu américain représente environ {us_count:,} titres contre {intl_count:,} titres internationaux, montrant une forte dominance US mais une présence internationale notable.")

    # Évolution de l'internationalisation
    intl_evo = dff.copy()
    intl_evo['origin'] = intl_evo['country'].apply(lambda x: 'États-Unis' if x == 'United States' else ('Inconnu' if x == 'Unknown' else 'International'))
    intl_evo = intl_evo[intl_evo['origin'] != 'Inconnu']
    intl_year = intl_evo.groupby(['year_added', 'origin']).size().reset_index(name='count').dropna(subset=['year_added'])
    fig_intl = px.area(intl_year, x='year_added', y='count', color='origin', color_discrete_map={'États-Unis': '#E50914', 'International': '#555555'},
        labels={'year_added': 'Année', 'count': 'Titres ajoutés', 'origin': 'Origine'})
    fig_intl.update_layout(**PLOTLY_LAYOUT, title="Évolution : Contenu US vs International dans le temps")
    st.plotly_chart(fig_intl, use_container_width=True)
    if not intl_year.empty:
        latest_year = int(intl_year['year_added'].max())
        latest_total = int(intl_year[intl_year['year_added'] == latest_year]['count'].sum())
        st.write(f"En {latest_year}, le total des ajouts US et internationaux est d'environ {latest_total:,} titres, donnant une bonne idée de la tendance la plus récente.")


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 4 — GENRES & AUDIENCE
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "🎭 Genres & Ratings":
    st.markdown('<div class="page-title">GENRES & RATINGS</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Axe 3 — Diversité des genres et ciblage du public</div>', unsafe_allow_html=True)

    # KPIs
    col1, col2, col3, col4 = st.columns(4)
    genres_exploded = dff['genres_list'].explode()
    top_genre = genres_exploded.value_counts().idxmax() if len(dff) > 0 else "N/A"
    adult_pct = len(dff[dff['rating'].isin(['TV-MA','R','NC-17','NR','UR'])]) / len(dff) * 100 if len(dff) > 0 else 0
    kids_pct = len(dff[dff['rating'].isin(['TV-Y','TV-Y7','TV-Y7-FV','TV-G','PG','G'])]) / len(dff) * 100 if len(dff) > 0 else 0
    with col1:
        st.metric("Genres uniques", genres_exploded.nunique())
    with col2:
        st.metric("Genre Dominant", top_genre)
    with col3:
        st.metric("Contenu Adultes", f"{adult_pct:.1f}%")
    with col4:
        st.metric("Contenu Enfants", f"{kids_pct:.1f}%")

    st.markdown("---")

    col_a, col_b = st.columns(2)

    with col_a:
        # Top genres
        top_genres = genres_exploded.value_counts().head(15)
        fig_genres = go.Figure(go.Bar(x=top_genres.values[::-1],y=top_genres.index[::-1],orientation='h',
            marker=dict(color=list(range(15)), colorscale=[[0, '#2A0000'], [1, '#E50914']], showscale=False),
            text=top_genres.values[::-1],textposition='outside',textfont=dict(color='#E5E5E5', size=10)))
        fig_genres.update_layout(**PLOTLY_LAYOUT, title="Top 15 Genres les Plus Représentés", xaxis_title="Nombre de titres", height=460)
        st.plotly_chart(fig_genres, use_container_width=True)
        if len(top_genres) > 0:
            top_genre_name = top_genres.index[0]
            top_genre_count = int(top_genres.iloc[0])
            st.write(f"Le genre le plus présent est {top_genre_name} avec environ {top_genre_count:,} titres, ce qui montre l'importance de ce style dans le catalogue.")

    with col_b:
        # rating pie
        aud_counts = dff['rating'].value_counts()
        fig_aud = go.Figure(go.Pie(labels=aud_counts.index, values=aud_counts.values, hole=0.5, marker=dict(colors=['#E50914', '#B20710', '#555', '#888'], 
            line=dict(color='#0D0D0D', width=2)), textfont=dict(color='#E5E5E5', size=12),))
        fig_aud.update_layout(**PLOTLY_LAYOUT, title="Répartition par Rating", height=460)
        st.plotly_chart(fig_aud, use_container_width=True)
        if len(aud_counts) > 0:
            top_rating = aud_counts.idxmax()
            top_rating_count = int(aud_counts.max())
            st.write(f"Le rating le plus fréquent est {top_rating} avec environ {top_rating_count:,} titres, montrant l'orientation du catalogue vers ce groupe d'âge.")

    st.markdown("---")

    col_c, = st.columns(1)

    with col_c:
        # Heatmap Genre × rating
        dff_h = dff.explode('genres_list')
        top_g_heat = dff_h['genres_list'].value_counts().head(10).index
        heat_data = dff_h[dff_h['genres_list'].isin(top_g_heat)]
        heat_pivot = heat_data.groupby(['genres_list', 'rating']).size().unstack(fill_value=0)

        fig_heat = go.Figure(go.Heatmap(z=heat_pivot.values, x=heat_pivot.columns.tolist(), y=heat_pivot.index.tolist(),
            colorscale=[[0, '#141414'], [0.3, '#6B0000'], [0.7, '#B20710'], [1, '#E50914']], text=heat_pivot.values,
            texttemplate="%{text}", textfont=dict(color='#E5E5E5', size=10),))
        fig_heat.update_layout(**PLOTLY_LAYOUT, title="Heatmap Genre × Rating", xaxis_title="Rating", yaxis_title="Genre")
        st.plotly_chart(fig_heat, use_container_width=True)
        max_cell = heat_pivot.values.max() if heat_pivot.size > 0 else 0
        min_cell = heat_pivot.values.min() if heat_pivot.size > 0 else 0
        avg_cell = heat_pivot.values.mean() if heat_pivot.size > 0 else 0
        dominant_genre = heat_pivot.sum(axis=1).idxmax() if not heat_pivot.empty else "inconnu"
        dominant_rating = heat_pivot.sum(axis=0).idxmax() if not heat_pivot.empty else "inconnu"
        st.write(f"La heatmap révèle que le genre '{dominant_genre}' et le rating '{dominant_rating}' sont les plus représentés dans le catalogue. Les cellules varient de {int(min_cell)} à {int(max_cell)} titres, avec une moyenne de {avg_cell:.0f}, montrant des disparités fortes dans le croisement genre-audience.")

    # Évolution genres dans le temps
    dff_evo = dff.explode('genres_list')
    top5_genres = dff_evo['genres_list'].value_counts().head(6).index
    genre_evo = dff_evo[dff_evo['genres_list'].isin(top5_genres)]
    genre_year = genre_evo.groupby(['year_added', 'genres_list']).size().reset_index(name='count')
    genre_year = genre_year.dropna(subset=['year_added'])

    fig_gevo = px.line(genre_year, x='year_added', y='count', color='genres_list', labels={'year_added': 'Année', 'count': 'Titres ajoutés', 'genres_list': 'Genre'})
    fig_gevo.update_traces(line_width=2)
    fig_gevo.update_layout(**PLOTLY_LAYOUT, title="Évolution des Top 6 Genres dans le Temps")
    st.plotly_chart(fig_gevo, use_container_width=True)
    if not genre_year.empty:
        peak_year = int(genre_year.groupby('year_added')['count'].sum().idxmax())
        peak_count = int(genre_year.groupby('year_added')['count'].sum().max())
        st.write(f"Le pic d'activité des top 6 genres est atteint en {peak_year} avec environ {peak_count:,} titres ajoutés cette année-là, ce qui met en évidence le moment fort de leur évolution.")


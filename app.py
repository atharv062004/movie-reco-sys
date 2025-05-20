import streamlit as st
import pickle
import pandas as pd
import requests
import os

# --------------------
# Google Custom Search Setup
# --------------------
API_KEY = "AIzaSyDLSPnHMmcf347oDGuFKwwv52A3Vv1HY84"
CX = "b0d2c7b8e1a7d4c2b"

# --------------------
# Load or initialize poster cache
# --------------------
if os.path.exists("posters_cache.pkl"):
    with open("posters_cache.pkl", "rb") as f:
        poster_cache = pickle.load(f)
else:
    poster_cache = {}

# --------------------
# Fetch poster and update cache
# --------------------
def fetch_poster(movie_title):
    if movie_title in poster_cache:
        return poster_cache[movie_title]

    try:
        url = f"https://www.googleapis.com/customsearch/v1?q={movie_title} movie poster&cx={CX}&key={API_KEY}&searchType=image"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        if 'items' in data:
            poster_url = data['items'][0]['link']
            poster_cache[movie_title] = poster_url
            # Save updated cache
            with open("posters_cache.pkl", "wb") as f:
                pickle.dump(poster_cache, f)
            return poster_url
    except Exception as e:
        print(f"Error: {e}")

    # Fallback placeholder
    fallback = "https://via.placeholder.com/500x750?text=Poster+Unavailable"
    poster_cache[movie_title] = fallback
    with open("posters_cache.pkl", "wb") as f:
        pickle.dump(poster_cache, f)
    return fallback

# --------------------
# Recommend function
# --------------------
def recommend(movie):
    movie_index = movies[movies['title'] == movie].index[0]
    distances = similarity[movie_index]
    movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

    recommended_movies = []
    recommended_posters = []

    for i in movies_list:
        title = movies.iloc[i[0]].title
        recommended_movies.append(title)
        recommended_posters.append(fetch_poster(title))

    return recommended_movies, recommended_posters

# --------------------
# Load data
# --------------------
movies_dict = pickle.load(open("movie_dict.pkl", "rb"))
movies = pd.DataFrame(movies_dict)
similarity = pickle.load(open("similarity.pkl", "rb"))

# --------------------
# UI Styling
# --------------------
st.markdown("""
    <style>
        .stApp {
            background-color: #121212;
            color: #ffffff;
        }
        .title {
            font-size: 48px;
            font-weight: bold;
            text-align: center;
            color: #00BFFF;
            margin-bottom: 30px;
        }
        .movie-title {
            font-size: 16px;
            color: #FFD700;
            text-align: center;
            margin-top: 10px;
        }
        img {
            border-radius: 10px;
            border: 2px solid #444;
            box-shadow: 0 0 10px rgba(0,0,0,0.6);
        }
        div.stButton > button:first-child {
            background-color: #1E90FF;
            color: white;
            border-radius: 10px;
            padding: 10px 24px;
            font-size: 16px;
            font-weight: bold;
        }
        div.stButton > button:first-child:hover {
            background-color: #00BFFF;
            color: black;
        }
    </style>
""", unsafe_allow_html=True)

# --------------------
# Streamlit UI
# --------------------
st.markdown('<div class="title">🎬 Movie Recommender System</div>', unsafe_allow_html=True)

selected_movie_name = st.selectbox(
    '🎥 Select a movie you like',
    movies['title'].values
)

if st.button('🔍 Recommend'):
    names, posters = recommend(selected_movie_name)

    cols = st.columns(5)
    for i, col in enumerate(cols):
        with col:
            st.image(posters[i], use_container_width=True)
            st.markdown(f"<div class='movie-title'>{names[i]}</div>", unsafe_allow_html=True)

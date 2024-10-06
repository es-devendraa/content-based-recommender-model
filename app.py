import os
import gdown
from flask import Flask, render_template, request
import pickle
import pandas as pd
# Function to fetch movie details (poster, etc.) from TMDb using movie title
import requests

def download_similarity_model():
    file_path = 'similarity.pkl'
    if not os.path.exists(file_path):
        print("Downloading similarity model from Google Drive...")
        url = 'https://drive.google.com/uc?id=1y8ufm0Ut0V3s3yVN4ORSMk0HgsVtRm2b'  # Replace with your file ID
        gdown.download(url, file_path, quiet=False)
    else:
        print("Similarity model already exists locally.")

# Call the download function
download_similarity_model()

app = Flask(__name__)

# Load the pickled data
movies_dict = pickle.load(open('movie_dict.pkl', 'rb'))
movies = pd.DataFrame(movies_dict)
similarity = pickle.load(open('similarity.pkl', 'rb'))



# Your OMDb API Key
OMDB_API_KEY = 'c1247a5a'

# Function to fetch movie poster from OMDb using movie title
def fetch_movie_poster(movie_title):
    url = f"http://www.omdbapi.com/?t={movie_title}&apikey={OMDB_API_KEY}"
    
    response = requests.get(url)
    
    try:
        data = response.json()
        # Print the data for debugging purposes
        # print("OMDb API Response:", data)
        
        # Check if the response contains a poster URL
        if 'Poster' in data and data['Poster'] != "N/A":
            poster_url = data['Poster']
            return poster_url
        else:
            # Handle case when poster is not found
            print(f"No poster found for the movie: {movie_title}")
            return None
    except Exception as e:
        # Print the exception for debugging purposes
        print(f"Error fetching data from OMDb API: {e}")
        return None


# Recommendation function
def recommend(movie):
    movie_index = movies[movies['title'] == movie].index[0]
    distances = similarity[movie_index]
    movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:7]
    
    recommended_movies = []
    recommended_posters = []

    for i in movies_list:
        movie_title = movies.iloc[i[0]].title
        recommended_movies.append(movie_title)
        poster_url = fetch_movie_poster(movie_title)
        recommended_posters.append(poster_url)
    
    return recommended_movies, recommended_posters

# Home route
@app.route('/')
def home():
    movie_list = movies['title'].values
    return render_template('index.html', movie_list=movie_list)

# Recommendation route
# Recommendation route
@app.route('/recommend', methods=['POST'])
def recommend_movies():
    selected_movie = request.form.get('movie')
    recommendations, posters = recommend(selected_movie)
    
    # Pass zip to the template so it can be used in Jinja2
    return render_template('index.html', 
                           movie_list=movies['title'].values, 
                           recommendations=recommendations, 
                           posters=posters, 
                           selected_movie=selected_movie, 
                           zip=zip)


if __name__ == '__main__':
    app.run(debug=True)

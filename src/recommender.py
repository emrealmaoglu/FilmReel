"""
Film önerilerini yöneten sınıf.
"""
import pandas as pd
import numpy as np
from typing import List, Dict, Any, Tuple
import logging
import requests
from googletrans import Translator
import os
from dotenv import load_dotenv
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.metrics.pairwise import linear_kernel, cosine_similarity
from surprise import Reader, Dataset, SVD
import ast

# Ortam değişkenlerini yükle
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MovieRecommender:
    def __init__(self, movies_path: str, credits_path: str, ratings_path: str = None):
        """
        Film önerici sınıfını başlat.
        
        Parametreler
        -----------
        movies_path : str
            Film CSV dosyasının yolu
        credits_path : str
            Kredi CSV dosyasının yolu
        ratings_path : str, optional
            İşbirlikçi filtreleme için puanlama CSV dosyasının yolu
        """
        self.movies_df = None
        self.credits_df = None
        self.ratings_df = None
        self.cosine_sim = None
        self.cosine_sim2 = None
        self.indices = None
        self.svd_model = None
        
        try:
            self._load_data(movies_path, credits_path, ratings_path)
            self._preprocess_data()
            self._build_similarity_matrices()
        except Exception as e:
            logger.error(f"Film önerici başlatma hatası: {str(e)}")
            raise

    def _load_data(self, movies_path: str, credits_path: str, ratings_path: str = None):
        """Load and merge the movie datasets."""
        self.movies_df = pd.read_csv(movies_path)
        self.credits_df = pd.read_csv(credits_path)
        self.credits_df.columns = ['id', 'title', 'cast', 'crew']
        self.movies_df = self.movies_df.merge(self.credits_df, on='id')
        
        if ratings_path:
            self.ratings_df = pd.read_csv(ratings_path)

    def _preprocess_data(self):
        """Preprocess the movie data for recommendation generation."""
        # Calculate weighted rating
        C = self.movies_df['vote_average'].mean()
        m = self.movies_df['vote_count'].quantile(0.9)
        
        def weighted_rating(x, m=m, C=C):
            v = x['vote_count']
            R = x['vote_average']
            return (v/(v+m) * R) + (m/(m+v) * C)
        
        self.movies_df['score'] = self.movies_df.apply(weighted_rating, axis=1)
        
        # Process features
        features = ['cast', 'crew', 'keywords', 'genres']
        for feature in features:
            self.movies_df[feature] = self.movies_df[feature].apply(ast.literal_eval)
        
        # Extract director
        def get_director(x):
            for i in x:
                if i['job'] == 'Director':
                    return i['name']
            return np.nan
        
        self.movies_df['director'] = self.movies_df['crew'].apply(get_director)
        
        # Process cast, keywords, and genres
        def get_list(x):
            if isinstance(x, list):
                names = [i['name'] for i in x]
                return names[:3] if len(names) > 3 else names
            return []
        
        for feature in ['cast', 'keywords', 'genres']:
            self.movies_df[feature] = self.movies_df[feature].apply(get_list)
        
        # Clean data
        def clean_data(x):
            if isinstance(x, list):
                return [str.lower(i.replace(" ", "")) for i in x]
            elif isinstance(x, str):
                return str.lower(x.replace(" ", ""))
            return ''
        
        for feature in ['cast', 'keywords', 'director', 'genres']:
            self.movies_df[feature] = self.movies_df[feature].apply(clean_data)
        
        # Create soup for content-based filtering
        def create_soup(x):
            return ' '.join(x['keywords']) + ' ' + ' '.join(x['cast']) + ' ' + x['director'] + ' ' + ' '.join(x['genres'])
        
        self.movies_df['soup'] = self.movies_df.apply(create_soup, axis=1)
        
        # Reset index
        self.movies_df = self.movies_df.reset_index()
        self.indices = pd.Series(self.movies_df.index, index=self.movies_df['title'])

    def _build_similarity_matrices(self):
        """Build similarity matrices for both overview and metadata-based recommendations."""
        # TF-IDF based similarity
        tfidf = TfidfVectorizer(stop_words='english')
        tfidf_matrix = tfidf.fit_transform(self.movies_df['overview'].fillna(''))
        self.cosine_sim = linear_kernel(tfidf_matrix, tfidf_matrix)
        
        # CountVectorizer based similarity
        count = CountVectorizer(stop_words='english')
        count_matrix = count.fit_transform(self.movies_df['soup'])
        self.cosine_sim2 = cosine_similarity(count_matrix, count_matrix)

    def get_recommendations(self, title: str, n_recommendations: int = 10, 
                          use_metadata: bool = True) -> List[str]:
        """
        Get movie recommendations based on a given movie title.
        
        Args:
            title (str): Title of the movie to get recommendations for
            n_recommendations (int): Number of recommendations to return
            use_metadata (bool): Whether to use metadata-based similarity (True) or overview-based (False)
        
        Returns:
            List[str]: List of recommended movie titles
        """
        try:
            idx = self.indices[title]
            sim_scores = list(enumerate(self.cosine_sim2[idx] if use_metadata else self.cosine_sim[idx]))
            sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
            sim_scores = sim_scores[1:n_recommendations+1]
            movie_indices = [i[0] for i in sim_scores]
            return self.movies_df['title'].iloc[movie_indices].tolist()
        except KeyError:
            logger.error(f"Movie '{title}' not found in the dataset")
            return []

    def train_collaborative_filtering(self):
        """Train the SVD model for collaborative filtering."""
        if self.ratings_df is None:
            logger.warning("No ratings data provided for collaborative filtering")
            return
        
        reader = Reader()
        data = Dataset.load_from_df(self.ratings_df[['userId', 'movieId', 'rating']], reader)
        trainset = data.build_full_trainset()
        self.svd_model = SVD()
        self.svd_model.fit(trainset)

    def get_collaborative_recommendations(self, user_id: int, n_recommendations: int = 10) -> List[Dict]:
        """
        Get personalized recommendations using collaborative filtering.
        
        Args:
            user_id (int): ID of the user to get recommendations for
            n_recommendations (int): Number of recommendations to return
        
        Returns:
            List[Dict]: List of recommended movies with predicted ratings
        """
        if self.svd_model is None:
            logger.error("SVD model not trained. Call train_collaborative_filtering() first.")
            return []
        
        # Get all movies the user hasn't rated
        user_ratings = self.ratings_df[self.ratings_df['userId'] == user_id]
        all_movies = set(self.ratings_df['movieId'].unique())
        rated_movies = set(user_ratings['movieId'])
        unrated_movies = all_movies - rated_movies
        
        # Predict ratings for unrated movies
        predictions = []
        for movie_id in unrated_movies:
            pred = self.svd_model.predict(user_id, movie_id)
            predictions.append({
                'movieId': movie_id,
                'predicted_rating': pred.est
            })
        
        # Sort by predicted rating and return top N
        predictions.sort(key=lambda x: x['predicted_rating'], reverse=True)
        return predictions[:n_recommendations]

    def get_hybrid_recommendations(self, title: str, user_id: int = None, 
                                 n_recommendations: int = 10) -> List[Dict]:
        """
        Get hybrid recommendations combining content-based and collaborative filtering.
        
        Args:
            title (str): Title of the movie to get recommendations for
            user_id (int, optional): ID of the user for personalized recommendations
            n_recommendations (int): Number of recommendations to return
        
        Returns:
            List[Dict]: List of recommended movies with scores
        """
        # Get content-based recommendations
        content_recs = self.get_recommendations(title, n_recommendations)
        
        if user_id is not None and self.svd_model is not None:
            # Get collaborative filtering recommendations
            collab_recs = self.get_collaborative_recommendations(user_id, n_recommendations)
            
            # Combine and rank recommendations
            combined_recs = []
            for movie in content_recs:
                movie_id = self.movies_df[self.movies_df['title'] == movie]['id'].iloc[0]
                pred = self.svd_model.predict(user_id, movie_id)
                combined_recs.append({
                    'title': movie,
                    'score': pred.est
                })
            
            # Sort by combined score
            combined_recs.sort(key=lambda x: x['score'], reverse=True)
            return combined_recs[:n_recommendations]
        
        return [{'title': movie, 'score': None} for movie in content_recs]

class Recommender:
    """
    Film önerilerini gerçekleştiren sınıf.
    
    Özellikler
    ----------
    logger : logging.Logger
        Loglama için logger nesnesi
    tmdb_token : str
        TMDB API anahtarı
    translator : Translator
        Google Translate API nesnesi
    """
    
    def __init__(self):
        """
        Recommender sınıfının başlatıcı metodu.
        """
        self.logger = logging.getLogger(__name__)
        self.tmdb_token = os.getenv('TMDB_API_KEY')
        if not self.tmdb_token:
            raise ValueError("TMDB_API_KEY ortam değişkeni bulunamadı")
        
        self.translator = Translator()
        
    def calculate_weighted_rating(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        IMDB formülüne göre ağırlıklı puan hesaplar.
        
        Parameters
        ----------
        df : pd.DataFrame
            Film verilerini içeren DataFrame
            
        Returns
        -------
        pd.DataFrame
            Ağırlıklı puanlar eklenmiş DataFrame
        """
        try:
            # Ortalama oy değerini hesapla
            C = df['vote_average'].mean()
            
            # Minimum oy sayısını hesapla (90. yüzdelik dilim)
            m = df['vote_count'].quantile(0.9)
            
            # Minimum oy sayısına sahip filmleri filtrele
            q_movies = df.copy().loc[df['vote_count'] >= m]
            
            # Ağırlıklı puan hesapla
            def weighted_rating(x, m=m, C=C):
                v = x['vote_count']
                R = x['vote_average']
                return (v/(v+m) * R) + (m/(m+v) * C)
            
            q_movies['score'] = q_movies.apply(weighted_rating, axis=1)
            
            # Puanlara göre sırala
            q_movies = q_movies.sort_values('score', ascending=False)
            
            self.logger.info("Ağırlıklı puanlar başarıyla hesaplandı.")
            return q_movies
            
        except Exception as e:
            self.logger.error(f"Ağırlıklı puan hesaplama hatası: {str(e)}")
            raise
        
    def get_content_based_recommendations(
        self,
        movie_title: str,
        movies_df: pd.DataFrame,
        similarity_matrix: np.ndarray,
        top_n: int = 5
    ) -> List[Dict[str, Any]]:
        """
        İçerik tabanlı film önerileri oluşturur.
        
        Parameters
        ----------
        movie_title : str
            Önerilerin oluşturulacağı film başlığı
        movies_df : pd.DataFrame
            Film verilerini içeren DataFrame
        similarity_matrix : np.ndarray
            Benzerlik matrisi
        top_n : int, optional
            Önerilecek film sayısı, by default 5
            
        Returns
        -------
        List[Dict[str, Any]]
            Önerilen filmlerin bilgilerini içeren liste
        """
        try:
            # Film indeksini bul
            idx = movies_df[movies_df['title'] == movie_title].index[0]
            
            # Benzerlik skorlarını hesapla
            sim_scores = list(enumerate(similarity_matrix[idx]))
            sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
            sim_scores = sim_scores[1:top_n+1]
            
            # Önerilen filmlerin indekslerini al
            movie_indices = [i[0] for i in sim_scores]
            
            # Önerilen filmlerin bilgilerini topla
            recommendations = []
            for idx in movie_indices:
                movie = movies_df.iloc[idx]
                poster, overview = self.fetch_movie_details(movie['movie_id'])
                recommendations.append({
                    'movie_id': movie['movie_id'],
                    'title': movie['title'],
                    'poster': poster,
                    'overview': overview,
                    'score': movie.get('score', None),
                    'vote_average': movie['vote_average'],
                    'vote_count': movie['vote_count']
                })
                
            self.logger.info(f"{movie_title} için {top_n} film önerisi oluşturuldu.")
            return recommendations
            
        except Exception as e:
            self.logger.error(f"İçerik tabanlı öneri oluşturma hatası: {str(e)}")
            raise
            
    def get_hybrid_recommendations(
        self,
        movie_title: str,
        movies_df: pd.DataFrame,
        similarity_matrix: np.ndarray,
        top_n: int = 5
    ) -> List[Dict[str, Any]]:
        """
        İçerik tabanlı ve popülerlik bazlı hibrit öneriler oluşturur.
        
        Parameters
        ----------
        movie_title : str
            Önerilerin oluşturulacağı film başlığı
        movies_df : pd.DataFrame
            Film verilerini içeren DataFrame
        similarity_matrix : np.ndarray
            Benzerlik matrisi
        top_n : int, optional
            Önerilecek film sayısı, by default 5
            
        Returns
        -------
        List[Dict[str, Any]]
            Önerilen filmlerin bilgilerini içeren liste
        """
        try:
            # İçerik tabanlı önerileri al
            content_recs = self.get_content_based_recommendations(
                movie_title, movies_df, similarity_matrix, top_n=top_n*2
            )
            
            # Ağırlıklı puanları hesapla
            scored_movies = self.calculate_weighted_rating(movies_df)
            
            # Önerileri birleştir ve sırala
            recommendations = []
            for rec in content_recs:
                movie_score = scored_movies[scored_movies['movie_id'] == rec['movie_id']]['score'].values
                if len(movie_score) > 0:
                    rec['weighted_score'] = movie_score[0]
                else:
                    rec['weighted_score'] = 0
                recommendations.append(rec)
                
            # Ağırlıklı puana göre sırala
            recommendations.sort(key=lambda x: x['weighted_score'], reverse=True)
                
            self.logger.info(f"{movie_title} için {top_n} hibrit öneri oluşturuldu.")
            return recommendations[:top_n]
            
        except Exception as e:
            self.logger.error(f"Hibrit öneri oluşturma hatası: {str(e)}")
            raise
            
    def fetch_movie_details(self, movie_id: int) -> Tuple[str, str]:
        """
        TMDB API'sinden film detaylarını çeker.
        
        Parameters
        ----------
        movie_id : int
            Film ID'si
            
        Returns
        -------
        Tuple[str, str]
            Film posteri URL'si ve özeti
        """
        try:
            headers = {
                "accept": "application/json",
                "Authorization": f"Bearer {self.tmdb_token}"
            }
            
            url = f"https://api.themoviedb.org/3/movie/{movie_id}?language=en-US"
            response = requests.get(url, headers=headers)
            data = response.json()
            
            # Poster URL'sini oluştur
            if 'poster_path' in data and data['poster_path']:
                poster_path = data['poster_path']
                poster_url = f"https://image.tmdb.org/t/p/w500/{poster_path}"
            else:
                poster_url = "https://via.placeholder.com/500x750?text=No+Poster+Available"
                
            # Özeti al ve çevir
            overview = data.get('overview', 'No overview available.')
            translated_overview = self.translate_text(overview)
            
            return poster_url, translated_overview
            
        except Exception as e:
            self.logger.error(f"Film detayları çekme hatası: {str(e)}")
            return "https://via.placeholder.com/500x750?text=Error", "Film detayları alınamadı."
            
    def translate_text(self, text: str, target_language: str = 'tr') -> str:
        """
        Metni hedef dile çevirir.
        
        Parameters
        ----------
        text : str
            Çevrilecek metin
        target_language : str, optional
            Hedef dil kodu, by default 'tr'
            
        Returns
        -------
        str
            Çevrilmiş metin
        """
        try:
            translation = self.translator.translate(text, dest=target_language)
            return translation.text
        except Exception as e:
            self.logger.error(f"Metin çevirme hatası: {str(e)}")
            return text 
"""
Özellik mühendisliği ve benzerlik hesaplamalarını yöneten sınıf.
"""
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from typing import Tuple, List, Dict, Any
import logging

class FeatureEngineer:
    """
    Özellik mühendisliği ve benzerlik hesaplamalarını gerçekleştiren sınıf.
    
    Attributes
    ----------
    logger : logging.Logger
        Loglama için logger nesnesi
    """
    
    def __init__(self):
        """
        FeatureEngineer sınıfının başlatıcı metodu.
        """
        self.logger = logging.getLogger(__name__)
        
    def calculate_weighted_rating(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Ağırlıklı film puanlarını hesaplar.
        
        Parameters
        ----------
        df : pd.DataFrame
            İşlenecek DataFrame
            
        Returns
        -------
        pd.DataFrame
            Ağırlıklı puanlar eklenmiş DataFrame
        """
        try:
            C = df['vote_average'].mean()
            m = df['vote_count'].quantile(0.9)
            
            def weighted_rating(x, m=m, C=C):
                v = x['vote_count']
                R = x['vote_average']
                return (v/(v+m) * R) + (m/(m+v) * C)
                
            df['score'] = df.apply(weighted_rating, axis=1)
            df = df.sort_values('score', ascending=False)
            
            self.logger.info("Ağırlıklı puanlar başarıyla hesaplandı.")
            return df
            
        except Exception as e:
            self.logger.error(f"Ağırlıklı puan hesaplama hatası: {str(e)}")
            raise
            
    def create_soup_feature(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Film özelliklerini birleştirerek 'soup' özelliği oluşturur.
        
        Parameters
        ----------
        df : pd.DataFrame
            İşlenecek DataFrame
            
        Returns
        -------
        pd.DataFrame
            'soup' özelliği eklenmiş DataFrame
        """
        try:
            def create_soup(x):
                director = x['director'] if pd.notna(x['director']) else ''
                return ' '.join(x['keywords']) + ' ' + ' '.join(x['cast']) + ' ' + director + ' ' + ' '.join(x['genres'])
                
            df['soup'] = df.apply(create_soup, axis=1)
            
            self.logger.info("'Soup' özelliği başarıyla oluşturuldu.")
            return df
            
        except Exception as e:
            self.logger.error(f"'Soup' özelliği oluşturma hatası: {str(e)}")
            raise
            
    def calculate_tfidf_similarity(self, df: pd.DataFrame) -> np.ndarray:
        """
        TF-IDF tabanlı benzerlik matrisini hesaplar.
        
        Parameters
        ----------
        df : pd.DataFrame
            İşlenecek DataFrame
            
        Returns
        -------
        np.ndarray
            TF-IDF benzerlik matrisi
        """
        try:
            tfidf = TfidfVectorizer(stop_words='english')
            tfidf_matrix = tfidf.fit_transform(df['overview'])
            cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)
            
            self.logger.info("TF-IDF benzerlik matrisi başarıyla hesaplandı.")
            return cosine_sim
            
        except Exception as e:
            self.logger.error(f"TF-IDF benzerlik hesaplama hatası: {str(e)}")
            raise
            
    def calculate_content_similarity(self, df: pd.DataFrame) -> np.ndarray:
        """
        İçerik tabanlı benzerlik matrisini hesaplar.
        
        Parameters
        ----------
        df : pd.DataFrame
            İşlenecek DataFrame
            
        Returns
        -------
        np.ndarray
            İçerik benzerlik matrisi
        """
        try:
            count = CountVectorizer(stop_words='english')
            count_matrix = count.fit_transform(df['soup'])
            cosine_sim = cosine_similarity(count_matrix, count_matrix)
            
            self.logger.info("İçerik benzerlik matrisi başarıyla hesaplandı.")
            return cosine_sim
            
        except Exception as e:
            self.logger.error(f"İçerik benzerlik hesaplama hatası: {str(e)}")
            raise
            
    def create_user_preference_features(self, user_df: pd.DataFrame, movie_df: pd.DataFrame) -> pd.DataFrame:
        """
        Kullanıcı tercihlerine dayalı özellikler oluşturur.
        
        Parameters
        ----------
        user_df : pd.DataFrame
            Kullanıcı verilerini içeren DataFrame
        movie_df : pd.DataFrame
            Film verilerini içeren DataFrame
            
        Returns
        -------
        pd.DataFrame
            Kullanıcı tercihlerine dayalı özellikler eklenmiş DataFrame
        """
        try:
            # Kullanıcıların izlediği filmlerin türlerini topla
            user_genres = {}
            for _, row in user_df.iterrows():
                watched_movies = eval(row['watched_movies'])
                for movie_id in watched_movies:
                    movie = movie_df[movie_df['movie_id'] == movie_id]
                    if not movie.empty:
                        genres = eval(movie['genres'].iloc[0])
                        for genre in genres:
                            if genre['name'] in user_genres:
                                user_genres[genre['name']] += 1
                            else:
                                user_genres[genre['name']] = 1
                                
            # Kullanıcı tercihlerini normalize et
            total = sum(user_genres.values())
            if total > 0:
                user_genres = {k: v/total for k, v in user_genres.items()}
                
            # Kullanıcı tercihlerini DataFrame'e ekle
            user_df['genre_preferences'] = user_df.apply(
                lambda x: user_genres if x['user_id'] in user_genres else {},
                axis=1
            )
            
            self.logger.info("Kullanıcı tercih özellikleri başarıyla oluşturuldu.")
            return user_df
            
        except Exception as e:
            self.logger.error(f"Kullanıcı tercih özellikleri oluşturma hatası: {str(e)}")
            raise 
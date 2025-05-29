"""
Kullanıcı profil yönetimini gerçekleştiren sınıf.
"""
import pandas as pd
import json
from typing import List, Dict, Any
import logging
from pathlib import Path

class UserProfileManager:
    """
    Kullanıcı profil yönetimini gerçekleştiren sınıf.
    
    Attributes
    ----------
    data_dir : Path
        Veri dosyalarının bulunduğu dizin
    logger : logging.Logger
        Loglama için logger nesnesi
    """
    
    def __init__(self, data_dir: str = "data"):
        """
        UserProfileManager sınıfının başlatıcı metodu.
        
        Parameters
        ----------
        data_dir : str, optional
            Veri dosyalarının bulunduğu dizin, by default "data"
        """
        self.data_dir = Path(data_dir)
        self.logger = logging.getLogger(__name__)
        self.user_data_path = self.data_dir / "user_profiles.csv"
        
    def create_user_profile(self, user_id: str) -> None:
        """
        Yeni bir kullanıcı profili oluşturur.
        
        Parameters
        ----------
        user_id : str
            Kullanıcı ID'si
        """
        try:
            # Kullanıcı verilerini yükle veya oluştur
            if self.user_data_path.exists():
                user_df = pd.read_csv(self.user_data_path)
            else:
                user_df = pd.DataFrame(columns=['user_id', 'watched_movies', 'preferences'])
                
            # Kullanıcı zaten varsa hata ver
            if user_id in user_df['user_id'].values:
                raise ValueError(f"Kullanıcı {user_id} zaten mevcut.")
                
            # Yeni kullanıcı profili oluştur
            new_user = pd.DataFrame({
                'user_id': [user_id],
                'watched_movies': ['[]'],
                'preferences': ['{}']
            })
            
            # Kullanıcıyı DataFrame'e ekle
            user_df = pd.concat([user_df, new_user], ignore_index=True)
            
            # Verileri kaydet
            user_df.to_csv(self.user_data_path, index=False)
            
            self.logger.info(f"Kullanıcı {user_id} için yeni profil oluşturuldu.")
            
        except Exception as e:
            self.logger.error(f"Kullanıcı profili oluşturma hatası: {str(e)}")
            raise
            
    def add_watched_movie(self, user_id: str, movie_id: int) -> None:
        """
        Kullanıcının izlediği filmler listesine yeni bir film ekler.
        
        Parameters
        ----------
        user_id : str
            Kullanıcı ID'si
        movie_id : int
            Film ID'si
        """
        try:
            # Kullanıcı verilerini yükle
            user_df = pd.read_csv(self.user_data_path)
            
            # Kullanıcıyı bul
            user_idx = user_df[user_df['user_id'] == user_id].index[0]
            
            # İzlenen filmleri al
            watched_movies = eval(user_df.loc[user_idx, 'watched_movies'])
            
            # Film zaten izlenmişse hata ver
            if movie_id in watched_movies:
                raise ValueError(f"Film {movie_id} zaten izlenmiş.")
                
            # Yeni filmi ekle
            watched_movies.append(movie_id)
            
            # Güncellenmiş listeyi kaydet
            user_df.loc[user_idx, 'watched_movies'] = str(watched_movies)
            user_df.to_csv(self.user_data_path, index=False)
            
            self.logger.info(f"Kullanıcı {user_id} için film {movie_id} izlenenler listesine eklendi.")
            
        except Exception as e:
            self.logger.error(f"İzlenen film ekleme hatası: {str(e)}")
            raise
            
    def update_preferences(self, user_id: str, preferences: Dict[str, float]) -> None:
        """
        Kullanıcı tercihlerini günceller.
        
        Parameters
        ----------
        user_id : str
            Kullanıcı ID'si
        preferences : Dict[str, float]
            Güncellenecek tercihler
        """
        try:
            # Kullanıcı verilerini yükle
            user_df = pd.read_csv(self.user_data_path)
            
            # Kullanıcıyı bul
            user_idx = user_df[user_df['user_id'] == user_id].index[0]
            
            # Mevcut tercihleri al
            current_preferences = eval(user_df.loc[user_idx, 'preferences'])
            
            # Tercihleri güncelle
            current_preferences.update(preferences)
            
            # Güncellenmiş tercihleri kaydet
            user_df.loc[user_idx, 'preferences'] = str(current_preferences)
            user_df.to_csv(self.user_data_path, index=False)
            
            self.logger.info(f"Kullanıcı {user_id} için tercihler güncellendi.")
            
        except Exception as e:
            self.logger.error(f"Tercih güncelleme hatası: {str(e)}")
            raise
            
    def get_user_profile(self, user_id: str) -> Dict[str, Any]:
        """
        Kullanıcı profilini getirir.
        
        Parameters
        ----------
        user_id : str
            Kullanıcı ID'si
            
        Returns
        -------
        Dict[str, Any]
            Kullanıcı profil bilgileri
        """
        try:
            # Kullanıcı verilerini yükle
            user_df = pd.read_csv(self.user_data_path)
            
            # Kullanıcıyı bul
            user = user_df[user_df['user_id'] == user_id].iloc[0]
            
            # Profil bilgilerini döndür
            return {
                'user_id': user['user_id'],
                'watched_movies': eval(user['watched_movies']),
                'preferences': eval(user['preferences'])
            }
            
        except Exception as e:
            self.logger.error(f"Kullanıcı profili getirme hatası: {str(e)}")
            raise
            
    def get_all_users(self) -> List[str]:
        """
        Tüm kullanıcı ID'lerini getirir.
        
        Returns
        -------
        List[str]
            Kullanıcı ID'lerinin listesi
        """
        try:
            # Kullanıcı verilerini yükle
            user_df = pd.read_csv(self.user_data_path)
            
            # Kullanıcı ID'lerini döndür
            return user_df['user_id'].tolist()
            
        except Exception as e:
            self.logger.error(f"Kullanıcı listesi getirme hatası: {str(e)}")
            raise 
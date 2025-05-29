"""
Veri yükleme ve başlangıç veri işleme işlemlerini yöneten sınıf.
"""
import pandas as pd
from pathlib import Path
from typing import Tuple, Dict, Any
import logging
import os

class DataLoader:
    """
    Film verilerini yükleyen ve başlangıç işlemlerini gerçekleştiren sınıf.
    
    Attributes
    ----------
    data_dir : Path
        Veri dosyalarının bulunduğu dizin
    logger : logging.Logger
        Loglama için logger nesnesi
    """
    
    def __init__(self, data_dir: str = None):
        """
        DataLoader sınıfının başlatıcı metodu.
        
        Parameters
        ----------
        data_dir : str, optional
            Veri dosyalarının bulunduğu dizin, by default None
        """
        if data_dir is None:
            # Proje kök dizinini bul
            current_dir = Path(__file__).resolve().parent
            project_root = current_dir.parent
            self.data_dir = project_root / "data"
        else:
            self.data_dir = Path(data_dir)
        self.logger = logging.getLogger(__name__)
        
    def load_movie_data(self) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Film ve kredi verilerini yükler.
        
        Returns
        -------
        Tuple[pd.DataFrame, pd.DataFrame]
            Film ve kredi verilerini içeren DataFrame'ler
            
        Raises
        ------
        FileNotFoundError
            Veri dosyaları bulunamadığında
        """
        try:
            movies_path = self.data_dir / "tmdb_5000_movies.csv"
            credits_path = self.data_dir / "tmdb_5000_credits.csv"
            
            if not movies_path.exists():
                raise FileNotFoundError(f"Film veri dosyası bulunamadı: {movies_path}")
            if not credits_path.exists():
                raise FileNotFoundError(f"Kredi veri dosyası bulunamadı: {credits_path}")
                
            movies_df = pd.read_csv(movies_path, low_memory=False)
            credits_df = pd.read_csv(credits_path)
            
            self.logger.info("Veri setleri başarıyla yüklendi.")
            return movies_df, credits_df
            
        except Exception as e:
            self.logger.error(f"Veri yükleme hatası: {str(e)}")
            raise
            
    def merge_datasets(self, movies_df: pd.DataFrame, credits_df: pd.DataFrame) -> pd.DataFrame:
        """
        Film ve kredi verilerini birleştirir.
        
        Parameters
        ----------
        movies_df : pd.DataFrame
            Film verilerini içeren DataFrame
        credits_df : pd.DataFrame
            Kredi verilerini içeren DataFrame
            
        Returns
        -------
        pd.DataFrame
            Birleştirilmiş veri seti
            
        Raises
        ------
        Exception
            Veri birleştirme işlemi başarısız olduğunda
        """
        try:
            # Kredi verilerinin sütunlarını yeniden adlandır
            credits_df.columns = ['movie_id', 'title', 'cast', 'crew']
            
            # Film verilerindeki id sütununu movie_id olarak yeniden adlandır
            movies_df.rename(columns={'id': 'movie_id'}, inplace=True)
            
            # Veri setlerini birleştir
            merged_df = movies_df.merge(credits_df, on='movie_id')
            
            # title_y sütununu title olarak yeniden adlandır
            merged_df.rename(columns={'title_y': 'title'}, inplace=True)
            
            self.logger.info("Veri setleri başarıyla birleştirildi.")
            return merged_df
            
        except Exception as e:
            self.logger.error(f"Veri birleştirme hatası: {str(e)}")
            raise
            
    def load_user_data(self) -> pd.DataFrame:
        """
        Kullanıcı verilerini yükler.
        
        Returns
        -------
        pd.DataFrame
            Kullanıcı verilerini içeren DataFrame
        """
        try:
            user_data_path = self.data_dir / "user_profiles.csv"
            if user_data_path.exists():
                user_df = pd.read_csv(user_data_path)
                self.logger.info("Kullanıcı verileri başarıyla yüklendi.")
                return user_df
            else:
                # Kullanıcı verileri yoksa boş bir DataFrame oluştur
                user_df = pd.DataFrame(columns=['user_id', 'watched_movies', 'preferences'])
                self.logger.info("Yeni kullanıcı veri seti oluşturuldu.")
                return user_df
                
        except Exception as e:
            self.logger.error(f"Kullanıcı verisi yükleme hatası: {str(e)}")
            raise 
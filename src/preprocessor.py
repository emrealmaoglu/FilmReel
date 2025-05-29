"""
Veri ön işleme işlemlerini yöneten sınıf.
"""
import pandas as pd
import numpy as np
from typing import List, Dict, Any
import logging
import ast

class Preprocessor:
    """
    Veri ön işleme işlemlerini gerçekleştiren sınıf.
    
    Attributes
    ----------
    logger : logging.Logger
        Loglama için logger nesnesi
    """
    
    def __init__(self):
        """
        Preprocessor sınıfının başlatıcı metodu.
        """
        self.logger = logging.getLogger(__name__)
        
    def preprocess_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Veri setini ön işler.
        
        Parameters
        ----------
        df : pd.DataFrame
            İşlenecek veri seti
            
        Returns
        -------
        pd.DataFrame
            Ön işlenmiş veri seti
            
        Raises
        ------
        Exception
            Veri ön işleme işlemi başarısız olduğunda
        """
        try:
            # Eksik değerleri temizle
            df = self.clean_missing_values(df)
            
            # JSON sütunlarını ayrıştır
            df = self.parse_json_columns(df, ['cast', 'crew', 'keywords', 'genres'])
            
            # Yönetmen bilgisini çıkar
            df = self.extract_director(df)
            
            # Önemli öğeleri çıkar
            df = self.extract_top_items(df, ['cast', 'keywords', 'genres'])
            
            # Metin verilerini temizle
            df = self.clean_text_data(df, ['cast', 'keywords', 'genres'])
            
            self.logger.info("Veri ön işleme başarıyla tamamlandı.")
            return df
            
        except Exception as e:
            self.logger.error(f"Veri ön işleme hatası: {str(e)}")
            raise
        
    def clean_missing_values(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Eksik değerleri temizler.
        
        Parameters
        ----------
        df : pd.DataFrame
            İşlenecek veri seti
            
        Returns
        -------
        pd.DataFrame
            Eksik değerleri temizlenmiş veri seti
            
        Raises
        ------
        Exception
            Eksik değer temizleme işlemi başarısız olduğunda
        """
        try:
            # Eksik değerleri doldur
            df['overview'] = df['overview'].fillna('')
            df['tagline'] = df['tagline'].fillna('')
            df['runtime'] = df['runtime'].fillna(df['runtime'].mean())
            df['budget'] = df['budget'].fillna(0)
            df['revenue'] = df['revenue'].fillna(0)
            
            self.logger.info("Eksik değerler başarıyla temizlendi.")
            return df
            
        except Exception as e:
            self.logger.error(f"Eksik değer temizleme hatası: {str(e)}")
            raise
            
    def parse_json_columns(self, df: pd.DataFrame, columns: List[str]) -> pd.DataFrame:
        """
        JSON formatındaki sütunları ayrıştırır.
        
        Parameters
        ----------
        df : pd.DataFrame
            İşlenecek veri seti
        columns : List[str]
            Ayrıştırılacak sütunlar
            
        Returns
        -------
        pd.DataFrame
            JSON sütunları ayrıştırılmış veri seti
            
        Raises
        ------
        Exception
            JSON ayrıştırma işlemi başarısız olduğunda
        """
        try:
            for column in columns:
                if column in df.columns:
                    df[column] = df[column].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else x)
                
            self.logger.info("JSON sütunları başarıyla ayrıştırıldı.")
            return df
            
        except Exception as e:
            self.logger.error(f"JSON ayrıştırma hatası: {str(e)}")
            raise
            
    def extract_director(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Yönetmen bilgisini çıkarır.
        
        Parameters
        ----------
        df : pd.DataFrame
            İşlenecek veri seti
            
        Returns
        -------
        pd.DataFrame
            Yönetmen bilgisi eklenmiş veri seti
            
        Raises
        ------
        Exception
            Yönetmen bilgisi çıkarma işlemi başarısız olduğunda
        """
        try:
            def get_director(x):
                for i in x:
                    if i['job'] == 'Director':
                        return i['name']
                return np.nan
                
            df['director'] = df['crew'].apply(get_director)
            
            self.logger.info("Yönetmen bilgileri başarıyla çıkarıldı.")
            return df
            
        except Exception as e:
            self.logger.error(f"Yönetmen bilgisi çıkarma hatası: {str(e)}")
            raise
            
    def extract_top_items(self, df: pd.DataFrame, columns: List[str], n: int = 3) -> pd.DataFrame:
        """
        Belirtilen sütunlardan en önemli öğeleri çıkarır.
        
        Parameters
        ----------
        df : pd.DataFrame
            İşlenecek veri seti
        columns : List[str]
            İşlenecek sütunlar
        n : int, optional
            Çıkarılacak öğe sayısı, by default 3
            
        Returns
        -------
        pd.DataFrame
            Önemli öğeleri çıkarılmış veri seti
            
        Raises
        ------
        Exception
            Önemli öğe çıkarma işlemi başarısız olduğunda
        """
        try:
            for column in columns:
                if column in df.columns:
                    df[column] = df[column].apply(lambda x: x[:n] if isinstance(x, list) else x)
                
            self.logger.info("Önemli öğeler başarıyla çıkarıldı.")
            return df
            
        except Exception as e:
            self.logger.error(f"Önemli öğe çıkarma hatası: {str(e)}")
            raise
            
    def clean_text_data(self, df: pd.DataFrame, columns: List[str]) -> pd.DataFrame:
        """
        Metin verilerini temizler.
        
        Parameters
        ----------
        df : pd.DataFrame
            İşlenecek veri seti
        columns : List[str]
            Temizlenecek sütunlar
            
        Returns
        -------
        pd.DataFrame
            Metin verileri temizlenmiş veri seti
            
        Raises
        ------
        Exception
            Metin temizleme işlemi başarısız olduğunda
        """
        try:
            def clean_text(x):
                if isinstance(x, list):
                    return [str.lower(str(i).replace(" ", "")) for i in x]
                elif isinstance(x, dict):
                    return str.lower(str(x.get('name', '')).replace(" ", ""))
                elif isinstance(x, str):
                    return str.lower(x.replace(" ", ""))
                else:
                    return ''
            
            for column in columns:
                if column in df.columns:
                    df[column] = df[column].apply(clean_text)
            
            self.logger.info("Metin verileri başarıyla temizlendi.")
            return df
            
        except Exception as e:
            self.logger.error(f"Metin temizleme hatası: {str(e)}")
            raise 
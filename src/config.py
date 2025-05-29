"""
Ortam değişkenleri ve gizli bilgileri yönetmek için yapılandırma modülü.
"""
import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv
from pydantic import BaseSettings, Field

# .env dosyasından ortam değişkenlerini yükle
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

class Settings(BaseSettings):
    """Doğrulama ile uygulama ayarları."""
    
    # API Yapılandırması
    TMDB_API_KEY: str = Field(..., description="TMDB API anahtarı")
    TMDB_API_BASE_URL: str = Field(
        default="https://api.themoviedb.org/3",
        description="TMDB API temel URL'si"
    )
    
    # Uygulama Yapılandırması
    DEBUG: bool = Field(default=False, description="Hata ayıklama modu")
    LOG_LEVEL: str = Field(default="INFO", description="Günlük kayıt seviyesi")
    
    # Veri Yolları
    MOVIES_DATA_PATH: Path = Field(
        default=Path("data/movies.csv"),
        description="Film veri seti yolu"
    )
    CREDITS_DATA_PATH: Path = Field(
        default=Path("data/credits.csv"),
        description="Kredi veri seti yolu"
    )
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True

def get_settings() -> Settings:
    """Doğrulama ile uygulama ayarlarını al."""
    try:
        return Settings()
    except Exception as e:
        raise ValueError(f"Ayarlar yüklenemedi: {str(e)}")

# Global ayarlar örneği oluştur
settings = get_settings()

def validate_api_key(api_key: Optional[str] = None) -> str:
    """
    API anahtarını doğrula.
    
    Parametreler
    -----------
    api_key : Optional[str]
        Doğrulanacak API anahtarı. None ise, ayarlardan alınır.
        
    Dönüşler
    -------
    str
        Doğrulanmış API anahtarı
        
    Hatalar
    ------
    ValueError
        API anahtarı geçersiz veya eksikse
    """
    key = api_key or settings.TMDB_API_KEY
    if not key or len(key) < 10:  # Temel doğrulama
        raise ValueError("Geçersiz veya eksik API anahtarı")
    return key 
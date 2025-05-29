"""
Hız sınırlama ve hata yönetimi ile TMDB API için güvenli istemci.
"""
import time
import logging
from typing import Dict, Any, Optional
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .config import settings, validate_api_key

logger = logging.getLogger(__name__)

class TMDBClient:
    """Hız sınırlama ve hata yönetimi ile TMDB API istemcisi."""
    
    def __init__(self):
        """TMDB API istemcisini başlat."""
        self.api_key = validate_api_key()
        self.base_url = settings.TMDB_API_BASE_URL
        self.session = self._create_session()
        
    def _create_session(self) -> requests.Session:
        """
        Yeniden deneme mantığı ile bir requests oturumu oluştur.
        
        Dönüşler
        -------
        requests.Session
            Yapılandırılmış oturum nesnesi
        """
        session = requests.Session()
        
        # Yeniden deneme stratejisini yapılandır
        retry_strategy = Retry(
            total=3,  # yeniden deneme sayısı
            backoff_factor=1,  # yeniden denemeler arasında 1, 2, 4 saniye bekle
            status_forcelist=[429, 500, 502, 503, 504]  # yeniden denenecek HTTP durum kodları
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        return session
    
    def _make_request(
        self,
        endpoint: str,
        method: str = "GET",
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Hız sınırlama ve hata yönetimi ile API isteği yap.
        
        Parametreler
        -----------
        endpoint : str
            API endpoint'i
        method : str, optional
            HTTP metodu, varsayılan "GET"
        params : Optional[Dict[str, Any]], optional
            Sorgu parametreleri, varsayılan None
        data : Optional[Dict[str, Any]], optional
            İstek gövdesi verisi, varsayılan None
            
        Dönüşler
        -------
        Dict[str, Any]
            API yanıt verisi
            
        Hatalar
        ------
        requests.exceptions.RequestException
            İstek başarısız olursa
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        # API anahtarını parametrelere ekle
        params = params or {}
        params["api_key"] = self.api_key
        
        try:
            response = self.session.request(
                method=method,
                url=url,
                params=params,
                json=data,
                timeout=10  # 10 saniyelik zaman aşımı
            )
            response.raise_for_status()
            
            # Hız sınırlama - API limitlerine uy
            if "X-RateLimit-Remaining" in response.headers:
                remaining = int(response.headers["X-RateLimit-Remaining"])
                if remaining < 10:  # Kalan istek sayısı 10'dan azsa
                    reset_time = int(response.headers.get("X-RateLimit-Reset", 60))
                    logger.warning(f"Hız limiti neredeyse aşıldı. {reset_time} saniye bekleniyor.")
                    time.sleep(reset_time)
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"API isteği başarısız oldu: {str(e)}")
            raise
    
    def get_movie_details(self, movie_id: int) -> Dict[str, Any]:
        """
        TMDB API'den film detaylarını al.
        
        Parametreler
        -----------
        movie_id : int
            TMDB film ID'si
            
        Dönüşler
        -------
        Dict[str, Any]
            Film detayları
        """
        return self._make_request(f"movie/{movie_id}")
    
    def search_movies(self, query: str) -> Dict[str, Any]:
        """
        TMDB API'de film ara.
        
        Parametreler
        -----------
        query : str
            Arama sorgusu
            
        Dönüşler
        -------
        Dict[str, Any]
            Arama sonuçları
        """
        return self._make_request("search/movie", params={"query": query}) 
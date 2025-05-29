"""
Film öneri sistemi için Streamlit uygulaması.
"""
import streamlit as st
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import sys
import os
import logging
from typing import Tuple

# Proje kök dizinini Python yoluna ekle
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.data_loader import DataLoader
from src.preprocessor import Preprocessor
from src.recommender import Recommender

# Loglama ayarları
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_data() -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Veri setlerini yükler.
    
    Returns
    -------
    Tuple[pd.DataFrame, pd.DataFrame]
        Film ve kredi veri setleri
        
    Raises
    ------
    Exception
        Veri yükleme işlemi başarısız olduğunda
    """
    try:
        data_loader = DataLoader()
        movies_df, credits_df = data_loader.load_movie_data()
        logger.info("Veri setleri başarıyla yüklendi.")
        return movies_df, credits_df
        
    except Exception as e:
        logger.error(f"Veri yükleme hatası: {str(e)}")
        raise

def preprocess_data(movies_df: pd.DataFrame, credits_df: pd.DataFrame) -> pd.DataFrame:
    """
    Veri setlerini ön işler.
    
    Parameters
    ----------
    movies_df : pd.DataFrame
        Film veri seti
    credits_df : pd.DataFrame
        Kredi veri seti
        
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
        data_loader = DataLoader()
        merged_df = data_loader.merge_datasets(movies_df, credits_df)
        
        preprocessor = Preprocessor()
        processed_df = preprocessor.preprocess_data(merged_df)
        
        logger.info("Veri setleri başarıyla ön işlendi.")
        return processed_df
        
    except Exception as e:
        logger.error(f"Veri ön işleme hatası: {str(e)}")
        raise

def main():
    """
    Ana uygulama fonksiyonu.
    """
    st.set_page_config(
        page_title="FilmReel - Film Öneri Sistemi",
        page_icon="🎬",
        layout="wide"
    )

    # Ana başlık ve açıklama
    st.title("🎬 FilmReel")
    st.markdown("""
        ### Kişiselleştirilmiş Film Önerileri
        
        Beğendiğiniz bir filmi seçin, size benzer 5 film önerelim. Film önerilerimiz, 
        seçtiğiniz filmin içeriğine, türüne ve temasına göre özenle seçilir.
        """)
    
    try:
        # Veri setlerini yükle
        movies_df, credits_df = load_data()
        
        # Veri setlerini ön işle
        processed_df = preprocess_data(movies_df, credits_df)
        
        # TF-IDF vektörlerini oluştur
        tfidf = TfidfVectorizer(stop_words='english')
        tfidf_matrix = tfidf.fit_transform(processed_df['overview'].fillna(''))
        similarity_matrix = cosine_similarity(tfidf_matrix, tfidf_matrix)
        
        # Öneri sistemini başlat
        recommender = Recommender()

        # Film seçimi
        st.markdown("### 🎯 Film Seçimi")
        movie_list = processed_df['title'].tolist()
        selected_movie = st.selectbox(
            "Beğendiğiniz bir filmi seçin:",
            movie_list,
            index=movie_list.index("The Dark Knight") if "The Dark Knight" in movie_list else 0,
            help="Size benzer filmler önerebilmemiz için beğendiğiniz bir filmi seçin."
        )

        if selected_movie:
            with st.spinner("Film önerileri hazırlanıyor..."):
                recommendations = recommender.get_content_based_recommendations(
                    selected_movie,
                    processed_df,
                    similarity_matrix,
                    top_n=5
                )
                
                # Önerileri göster
                st.markdown(f"### 🎬 '{selected_movie}' için Öneriler")
                st.markdown("Seçtiğiniz filme benzer 5 film önerisi:")
                
                # 5 sütunlu grid oluştur
                cols = st.columns(5)
                
                for i, rec in enumerate(recommendations):
                    with cols[i % 5]:
                        # Film posteri
                        if 'poster' in rec and rec['poster']:
                            st.image(rec['poster'], use_column_width=True)
                        
                        # Film başlığı
                        st.markdown(f"#### {rec['title']}")
                        
                        # Film puanı
                        if 'vote_average' in rec:
                            st.markdown(f"⭐ {rec['vote_average']:.1f}/10")
                        
                        # Film özeti
                        if 'overview' in rec and rec['overview']:
                            with st.expander("📝 Film Özeti"):
                                st.markdown(rec['overview'])
                
    except Exception as e:
        st.error(f"Bir hata oluştu: {str(e)}")
        logger.error(f"Uygulama hatası: {str(e)}")

if __name__ == "__main__":
    main() 
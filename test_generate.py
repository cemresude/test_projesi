import streamlit as st
import google.generativeai as genai
import json
import os
from dotenv import load_dotenv

# 1. API Anahtarını Ayarla
# .env dosyasından anahtarı çeker (Güvenli yöntem)

# VEYA anahtarı direkt buraya yapıştırabilirsiniz (Sadece test için):
# api_key = "AIzaSyD......" 



# 2. Sayfa Ayarları
st.set_page_config(page_title="Otomatik Test Üretici", layout="wide")
st.title("🤖 NLP ile Gereksinimlerden Test Senaryosu Çıkarma")
st.markdown("Yazılım Kalite Güvencesi ve Testi Projesi")

# 3. Kenar Çubuğu (Sidebar) - Dosya Yükleme
with st.sidebar:
    api_key = st.text_input("Google API Anahtarınızı Girin:", type="password")
    st.header("Veri Girişi")
    uploaded_file = st.file_uploader("Gereksinim dosyasını (.txt) yükleyin", type=["txt"])
    
    # Model Seçimi (Opsiyonel)
    model_type = st.selectbox("Model Seçin", [
        "models/gemini-2.5-flash",
        "models/gemini-2.5-pro",
        "models/gemini-2.0-flash-exp",
        "models/gemini-2.0-flash",
        "models/gemini-2.0-flash-001",
        "models/gemini-2.0-flash-exp-image-generation",
        "models/gemini-2.0-flash-lite-001",
        "models/gemini-2.0-flash-lite",
        "models/gemini-2.0-flash-lite-preview-02-05",
        "models/gemini-2.0-flash-lite-preview",
        "models/gemini-exp-1206",
        "models/gemini-2.5-flash-preview-tts",
        "models/gemini-2.5-pro-preview-tts",
        "models/gemma-3-1b-it",
        "models/gemma-3-4b-it",
        "models/gemma-3-12b-it",
        "models/gemma-3-27b-it",
        "models/gemma-3n-e4b-it",
        "models/gemma-3n-e2b-it",
        "models/gemini-flash-latest",
        "models/gemini-flash-lite-latest",
        "models/gemini-pro-latest",
        "models/gemini-2.5-flash-lite",
        "models/gemini-2.5-flash-image-preview",
        "models/gemini-2.5-flash-image",
        "models/gemini-2.5-flash-preview-09-2025",
        "models/gemini-2.5-flash-lite-preview-09-2025",
        "models/gemini-3-pro-preview",
        "models/gemini-3-flash-preview",
        "models/gemini-3-pro-image-preview",
        "models/nano-banana-pro-preview",
        "models/gemini-robotics-er-1.5-preview",
        "models/gemini-2.5-computer-use-preview-10-2025",
        "models/deep-research-pro-preview-12-2025",
    ])

# 4. Ana Uygulama Mantığı
if not api_key:
    st.error("Lütfen API anahtarınızı tanımlayın!")
    st.stop()
else:
    print(f"Anahtar bulundu: {api_key[:5]}... (gerisi gizli)")
    
    try:
        genai.configure(api_key=api_key)
        print("Erişilebilen Modeller Listeleniyor...")
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                print(f"- {m.name}")
    except Exception as e:
        print(f"Bağlantı Hatası: {e}")

genai.configure(api_key=api_key)
if uploaded_file is not None:
    # Dosyayı okuma işlemi (Bytes'tan String'e çevirme)
    stringio = uploaded_file.getvalue().decode("utf-8")
    
    st.subheader("📄 Yüklenen Gereksinim Dokümanı")
    st.text_area("Doküman İçeriği", stringio, height=200)
    
    if st.button("🚀 Test Senaryolarını Otomatik Oluştur"):
        with st.spinner("Yapay zeka gereksinimleri analiz ediyor..."):
            try:
                # 5. Gemini'ye Gönderilecek Prompt
                prompt = f"""
                Sen uzman bir Yazılım Test Mühendisisin.
                Aşağıdaki gereksinim metnini analiz et.
                Tüm olası sınır değerleri, hatalı girişleri ve mutlu yol (happy path) senaryolarını düşün.
                
                Gereksinim Metni:
                "{stringio}"
                
                Çıktıyı SADECE aşağıdaki JSON formatında ver, başka bir açıklama yapma:
                [
                  {{"id": "TC001", "baslik": "...", "on_kosul": "...", "adimlar": "...", "beklenen_sonuc": "..."}},
                  {{"id": "TC002", "baslik": "...", "on_kosul": "...", "adimlar": "...", "beklenen_sonuc": "..."}}
                ]
                """
                
                # Modeli çağırma
                model = genai.GenerativeModel(model_type)
                response = model.generate_content(prompt)
                
                # Gelen yanıtı JSON'a çevirip tablo yapma
                try:
                    # Bazen model json markdown (```json ... ```) ekler, onu temizleyelim
                    cleaned_text = response.text.replace("```json", "").replace("```", "").strip()
                    data = json.loads(cleaned_text)
                    
                    st.success(f"Toplam {len(data)} adet test senaryosu oluşturuldu!")
                    st.table(data) # Tablo olarak göster
                    
                    # İndirme Butonu (Hocaya sunmak için JSON indirilebilir)
                    st.download_button(
                        label="📥 Testleri JSON Olarak İndir",
                        data=json.dumps(data, indent=4, ensure_ascii=False),
                        file_name="test_senaryolari.json",
                        mime="application/json"
                    )
                    
                except json.JSONDecodeError:
                    st.warning("Model çıktısı tam JSON formatında gelmedi, ham metin gösteriliyor:")
                    st.write(response.text)
                    
            except Exception as e:
                st.error(f"Bir hata oluştu: {e}")

else:
    st.info("Lütfen sol menüden bir .txt dosyası yükleyin.")
import streamlit as st
import pandas as pd

# -- 1) Session State kontrolü
if 'history' not in st.session_state:
    st.session_state['history'] = []

st.title("İki Aşamalı Satış - Kâr Marjı Hesaplama")

st.write("""
Bu uygulamada **C₀** (ilk alış maliyeti) ve **S₂** (nihai satış fiyatı) varsayılan olarak girilir.
Grup marjı (M) otomatik hesaplanır.  
Ürün ismi (opsiyonel) yazıp hesaplama yaparsanız, 
aşağıdaki hesaplama geçmişinde ürünleriniz ismiyle listelenir.
""")

# -- Girdi: Ürün İsmi
product_name = st.text_input("Ürün İsmi (opsiyonel)", "")

# -- Girdi: C0 ve S2
c0_input = st.text_input("Alış Maliyeti (C0)", value="20")
s2_input = st.text_input("Nihai Satış Fiyatı (S2)", value="90")

# Virgül -> Nokta dönüştür
c0_input = c0_input.replace(',', '.')
s2_input = s2_input.replace(',', '.')

# Validasyon
try:
    c0 = float(c0_input)
    s2 = float(s2_input)
except ValueError:
    st.error("C0 ve S2 değerlerini geçerli bir sayı olarak giriniz.")
    st.stop()

if s2 <= 0:
    st.error("S2 (nihai satış fiyatı) 0'dan büyük olmalı.")
    st.stop()

# Toplam (Grup) Marj (M) = 1 - (C0 / S2)
M = 1 - (c0 / s2)

st.markdown(f"**Toplam (Grup) Marjı (M):** {M*100:.2f}%")

# Radio ile kullanıcıya senaryo seçtiriyoruz
secenek = st.radio(
    "Hangi değeri girmek istiyorsunuz?",
    ("M2 (İkinci Satış Kâr Marjı)", "S1 (Ara Satış Fiyatı)")
)

if secenek == "M2 (İkinci Satış Kâr Marjı)":
    m2_input = st.text_input("İkinci Satış Kâr Marjı (M2) [örn: 30 => %30]", value="30")
    m2_input = m2_input.replace(',', '.').replace('%', '')
    
    if st.button("Hesapla (M2 Üzerinden)"):
        try:
            m2_val = float(m2_input)
            # 30 girilmişse 0.30'a dönüştür
            if m2_val > 1:
                m2_val /= 100.0
            
            s1 = s2 * (1 - m2_val)
            if s1 <= 0:
                st.error("Hesaplanan S1 <= 0! Girdileri kontrol edin.")
            else:
                m1 = 1 - (c0 / s1)
                
                # -- Değerleri istenen formatta hazırlayalım (2 ondalık, % işareti vb.)
                row = {
                    "Ürün": product_name if product_name else "",
                    "C0": f"{c0:.2f}",
                    "S1": f"{s1:.2f}",
                    "M1(%)": f"{m1*100:.2f}%",
                    "S2": f"{s2:.2f}",
                    "M2(%)": f"{m2_val*100:.2f}%",
                    "M(Grup %)": f"{M*100:.2f}%"
                }
                # -- Session state'e ekleyelim
                st.session_state['history'].append(row)

        except ValueError:
            st.error("Lütfen M2 değerini geçerli bir sayı olarak giriniz.")

else:
    # secenek == "S1 (Ara Satış Fiyatı)"
    s1_input = st.text_input("Ara Satış Fiyatı (S1)", value="60")
    s1_input = s1_input.replace(',', '.')

    if st.button("Hesapla (S1 Üzerinden)"):
        try:
            s1_val = float(s1_input)
            if s1_val <= 0:
                st.error("S1 0'dan büyük olmalı.")
            else:
                m1 = 1 - (c0 / s1_val)
                m2 = 1 - (s1_val / s2)
                
                row = {
                    "Ürün": product_name if product_name else "",
                    "C0": f"{c0:.2f}",
                    "S1": f"{s1_val:.2f}",
                    "M1(%)": f"{m1*100:.2f}%",
                    "S2": f"{s2:.2f}",
                    "M2(%)": f"{m2*100:.2f}%",
                    "M(Grup %)": f"{M*100:.2f}%"
                }
                st.session_state['history'].append(row)
        except ValueError:
            st.error("Lütfen S1 değerini geçerli bir sayı olarak giriniz.")

# -- Geçmişi gösterme
st.subheader("Hesaplama Geçmişi")
if len(st.session_state['history']) > 0:
    # DataFrame'e çevirip tablo olarak gösterelim
    df_history = pd.DataFrame(st.session_state['history'])
    st.table(df_history)
else:
    st.write("Henüz hesaplama yapılmadı.")

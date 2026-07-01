import streamlit as st
import datetime
import random

# --- ŞİFRE VE GİRİŞ EKRANI ---
def check_password():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    if not st.session_state.logged_in:
        st.markdown("<h1 style='text-align: center;'>Arşive Giriş</h1>", unsafe_allow_html=True)
        pwd = st.text_input("Şifre:", type="password")
        # Şifreyi buradan değiştirebilirsin
        if pwd == "16agustos": 
            st.session_state.logged_in = True
            st.rerun()
        elif pwd != "":
            st.error("Yanlış şifre.")
        st.stop()

check_password()

# --- SİTE İÇERİĞİ (Giriş Başarılıysa Burası Çalışır) ---

st.title("💜 Bizim Arşivimiz")

# --- SAYAÇ (16 Ağustos 2025'ten itibaren) ---
start_date = datetime.date(2025, 8, 16)
today = datetime.date.today()
delta = today - start_date

st.info(f"**Birlikte Geçen Zaman:** {delta.days} gün oldu. (Başlangıç: 16 Ağustos 2025)")

st.divider()

# --- TO-DO LIST ---
st.subheader("📝 Günlük Görevler")
st.write("Aşağıdaki görevleri tamamladıkça işaretle. (Not: Sayfa yenilendiğinde veya ertesi gün sıfırlanır)")

# Görevler
tasks = ["Türkçe Deneme", "Tarih/Matematik Deneme", "Alan", "Eğitim", "Coğrafya Tekrar"]

# Görevlerin durumunu session_state içinde tutalım
for task in tasks:
    if task not in st.session_state:
        st.session_state[task] = False
    
    st.session_state[task] = st.checkbox(task, value=st.session_state[task])

st.divider()

# --- ARŞİV (Video ve Slaytlar) ---
st.subheader("📼 Anılar ve Arşiv")
st.write("Aşağıdaki içerikleri izleyebilirsin:")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### Slaytlar")
    # Slaytlar için Google Drive veya benzeri bir platformdan alınan embed linkleri konulmalı
    st.components.v1.iframe("https://docs.google.com/presentation/d/e/...senin_linkin.../embed", height=300)
    st.write("Slayt 1")

with col2:
    st.markdown("### Videolar")
    # Videolar için YouTube liste dışı linkleri kullanılmalı
    st.video("https://www.youtube.com/watch?v=ornek_video_linki")
    st.write("Video 1")

st.divider()

# --- RASTGELE NOT KUTUSU ---
st.subheader("💌 Sana Bir Notum Var")

# 25-30 notunu bu listeye ekleyeceksin
notlar = [
    "Bugün çok güzelsin, her zamanki gibi.",
    "Çalışmalarında başarılar, o denemeler fullenecek!",
    "Ne zaman yorulsan, 16 Ağustos'u ve sonrasını hatırla.",
    "Birlikte daha çok anı biriktireceğiz.",
    "Coğrafya tekrarını unutma, haritalara iyi bak."
    # ... Diğer notlarını buraya virgülle ayırarak ekle
]

if st.button("Bir Not Oku"):
    secilen_not = random.choice(notlar)
    st.success(secilen_not)
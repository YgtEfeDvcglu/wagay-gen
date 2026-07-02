import json
import datetime

import streamlit as st
import streamlit.components.v1 as components
import gspread
from google.oauth2.service_account import Credentials

# ======================================================================
# AYARLAR — Burayı kendine göre düzenle
# ======================================================================

# Günlük görevler (sırayı değiştirirsen Google Sheet'teki satır sırası da
# otomatik olarak buna göre yeniden kurulur, sorun olmaz)
TASKS = ["Türkçe Deneme", "Tarih/Matematik Deneme", "Alan", "Eğitim", "Coğrafya Tekrar"]

# Google Slides linkleri — her biri "Web'de Yayınla" (Publish to web) ile
# alınan embed linki olmalı. Birden fazla slayt eklemek için listeye yeni
# satır ekle.
SLIDE_LINKS = [
    "https://docs.google.com/presentation/d/e/...senin_linkin_1.../embed",
    "https://docs.google.com/presentation/d/e/...senin_linkin_2.../embed",
]

# YouTube "Liste Dışı" (Unlisted) video linkleri. İstediğin kadar ekleyebilirsin.
VIDEO_LINKS = [
    "https://www.youtube.com/watch?v=ornek_video_linki",
]

# Not kartları — 25-30'a tamamla. Her biri virgülle ayrılmış bir metin.
# Bunlar tamamen senin yazacağın, kişisel notların; burada sadece örnek
# olarak orijinal 5 not duruyor.
NOTES = [
    "Bugün çok güzelsin, her zamanki gibi.",
    "Çalışmalarında başarılar, o denemeler fullenecek!",
    "Ne zaman yorulsan, 16 Ağustos'u ve sonrasını hatırla.",
    "Birlikte daha çok anı biriktireceğiz.",
    "Coğrafya tekrarını unutma, haritalara iyi bak.",
    # ... diğer notlarını buraya, aynı formatta, virgülle ayırarak ekle
]

START_DATE = datetime.date(2025, 8, 16)

# ======================================================================
# SAYFA AYARLARI
# ======================================================================

st.set_page_config(page_title="Bizim Arşivimiz", page_icon="💜", layout="wide")

# ======================================================================
# ÖZEL CSS — lila / gece arşivi teması
#   Not: buradaki renk kodlarını değiştirirsen, render_note_sidebar()
#   içindeki HTML_TEMPLATE'teki renkleri de aynı tut — o parça ayrı bir
#   iframe olduğu için bu CSS'i miras almıyor.
# ======================================================================

GLOBAL_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@500;600;700&family=Manrope:wght@400;500;600;700&family=Space+Mono:wght@400;700&display=swap');

:root {
    --ink: #1C1225;
    --plum: #3B1F52;
    --plum-light: #4E2A6B;
    --lilac: #C9A6E0;
    --lilac-soft: #E8D9F5;
    --paper-red: #B23A48;
}

.stApp {
    background: radial-gradient(circle at 18% -8%, var(--plum-light) 0%, var(--ink) 55%);
    color: var(--lilac-soft);
    font-family: 'Manrope', sans-serif;
}

.main .block-container {
    max-width: 880px;
    padding-top: 2.5rem;
    padding-bottom: 4rem;
}

header[data-testid="stHeader"] { background: transparent; }
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, var(--ink), var(--plum));
    border-right: 1px solid rgba(201,166,224,0.15);
}

/* ---- özel içerik blokları ---- */
.arsiv-eyebrow {
    font-family: 'Space Mono', monospace;
    font-size: 11px;
    letter-spacing: 3px;
    text-transform: uppercase;
    color: var(--paper-red);
    margin-bottom: 10px;
}

.arsiv-card {
    background: linear-gradient(155deg, rgba(78,42,107,0.55), rgba(28,18,37,0.9));
    border: 1px solid rgba(201,166,224,0.22);
    border-radius: 18px;
    padding: 30px 34px;
    margin-bottom: 26px;
    box-shadow: 0 24px 48px -28px rgba(0,0,0,0.7);
}

.arsiv-h1 {
    font-family: 'Cormorant Garamond', serif;
    font-weight: 700;
    font-size: 44px;
    color: var(--lilac-soft);
    margin: 4px 0 2px 0;
}

.arsiv-tagline {
    font-family: 'Manrope', sans-serif;
    font-size: 14px;
    color: rgba(232,217,245,0.6);
    margin-bottom: 30px;
}

.arsiv-h3 {
    font-family: 'Cormorant Garamond', serif;
    font-weight: 600;
    font-size: 26px;
    color: var(--lilac-soft);
    margin: 0 0 14px 0;
}

.arsiv-subtitle {
    font-family: 'Space Mono', monospace;
    font-size: 11px;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: var(--lilac);
    margin: 4px 0 10px 0;
}

.arsiv-caption {
    font-size: 13px;
    color: rgba(232,217,245,0.55);
    margin: 4px 0 6px 0;
}

.counter-number {
    font-family: 'Space Mono', monospace;
    font-size: 64px;
    font-weight: 700;
    line-height: 1;
    background: linear-gradient(120deg, var(--lilac-soft), var(--lilac) 60%, var(--paper-red));
    -webkit-background-clip: text;
    background-clip: text;
    color: transparent;
}

.counter-label {
    font-size: 14px;
    color: rgba(232,217,245,0.7);
    margin-top: 6px;
}

.anniversary-banner {
    display: inline-block;
    font-family: 'Manrope', sans-serif;
    font-size: 13px;
    font-weight: 600;
    color: var(--ink);
    background: var(--lilac);
    padding: 6px 14px;
    border-radius: 999px;
    margin-bottom: 14px;
}

/* ---- widget'lar ---- */
.stButton > button {
    background: linear-gradient(135deg, var(--plum-light), var(--ink));
    border: 1px solid rgba(201,166,224,0.4);
    color: var(--lilac-soft);
    border-radius: 999px;
    padding: 8px 22px;
    font-family: 'Manrope', sans-serif;
    font-weight: 600;
    letter-spacing: 0.3px;
    transition: all 0.2s ease;
}
.stButton > button:hover {
    border-color: var(--lilac);
    color: var(--ink);
    background: var(--lilac);
}

input[type="password"], input[type="text"] {
    background: rgba(255,255,255,0.05) !important;
    color: var(--lilac-soft) !important;
    border: 1px solid rgba(201,166,224,0.3) !important;
    border-radius: 10px !important;
}

[data-testid="stCheckbox"] label p { color: var(--lilac-soft); font-size: 15px; }
input[type="checkbox"] { accent-color: var(--lilac); }

[data-testid="stProgress"] > div > div { background: linear-gradient(90deg, var(--lilac), var(--paper-red)); }

hr { border-color: rgba(201,166,224,0.15); }
</style>
"""

st.markdown(GLOBAL_CSS, unsafe_allow_html=True)


# ======================================================================
# ŞİFRE KONTROLÜ
# ======================================================================

def check_password() -> None:
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    if st.session_state.logged_in:
        return

    try:
        correct_password = st.secrets["password"]
    except Exception:
        st.error(
            "⚠️ Şifre henüz tanımlanmamış. `.streamlit/secrets.toml` içine "
            '`password = "..."` satırını eklemen gerekiyor (bkz. KURULUM.md).'
        )
        st.stop()

    _, mid, _ = st.columns([1, 1.1, 1])
    with mid:
        st.markdown("<div class='arsiv-eyebrow' style='text-align:center;'>ÖZEL ARŞİV</div>", unsafe_allow_html=True)
        st.markdown("<h1 class='arsiv-h1' style='text-align:center; font-size:32px;'>Bu kapı sadece ikimize açılıyor</h1>", unsafe_allow_html=True)
        pwd = st.text_input("Şifre", type="password", label_visibility="collapsed", placeholder="Şifre")
        if pwd and pwd == correct_password:
            st.session_state.logged_in = True
            st.rerun()
        elif pwd:
            st.error("Yanlış şifre, tekrar dene.")

    st.stop()


check_password()

# ======================================================================
# GOOGLE SHEETS — to-do listesinin iki cihazdan da senkron kalması için
# ======================================================================

@st.cache_resource(show_spinner=False)
def get_gsheet():
    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    creds = Credentials.from_service_account_info(dict(st.secrets["gcp_service_account"]), scopes=scopes)
    client = gspread.authorize(creds)
    return client.open_by_key(st.secrets["sheet_id"]).sheet1


def ensure_sheet_initialized(sheet) -> None:
    values = sheet.get_all_values()
    header_ok = len(values) > 0 and values[0][:2] == ["task", "checked"]
    if not header_ok:
        sheet.clear()
        header = ["task", "checked", "", "last_reset"]
        data_rows = [[t, "FALSE"] for t in TASKS]
        sheet.update(range_name="A1", values=[header] + data_rows)
        sheet.update(range_name="D2", values=[[""]])


def load_todo_state(sheet) -> dict:
    """Sheet'ten bugünün görev durumlarını okur; tarih değiştiyse otomatik sıfırlar."""
    ensure_sheet_initialized(sheet)
    values = sheet.get_all_values()
    today_str = datetime.date.today().isoformat()
    last_reset = values[1][3] if len(values) > 1 and len(values[1]) > 3 else ""

    if last_reset != today_str:
        for idx in range(len(TASKS)):
            sheet.update_cell(idx + 2, 2, "FALSE")
        sheet.update_cell(2, 4, today_str)
        return {t: False for t in TASKS}

    state = {}
    for idx, task in enumerate(TASKS):
        row = values[idx + 1] if len(values) > idx + 1 else []
        state[task] = (row[1].strip().upper() == "TRUE") if len(row) > 1 else False
    return state


def update_task(sheet, task: str, value: bool) -> None:
    row_index = TASKS.index(task) + 2  # +1 başlık, +1 de 1-indexli olduğu için
    sheet.update_cell(row_index, 2, "TRUE" if value else "FALSE")


try:
    _sheet = get_gsheet()
    SHEETS_READY = True
except Exception:
    _sheet = None
    SHEETS_READY = False


# ======================================================================
# BÖLÜMLER
# ======================================================================

def render_header() -> None:
    st.markdown("<div class='arsiv-eyebrow'>💜 ÖZEL ARŞİV</div>", unsafe_allow_html=True)
    st.markdown("<h1 class='arsiv-h1'>Bizim Arşivimiz</h1>", unsafe_allow_html=True)
    st.markdown("<div class='arsiv-tagline'>Gün, görev, kayıt ve not — hepsi burada.</div>", unsafe_allow_html=True)


def render_counter() -> None:
    today = datetime.date.today()
    delta_days = (today - START_DATE).days
    months_passed = (today.year - START_DATE.year) * 12 + (today.month - START_DATE.month)
    if today.day < START_DATE.day:
        months_passed -= 1
    is_anniversary_day = today.day == START_DATE.day

    st.markdown("<div class='arsiv-card'>", unsafe_allow_html=True)
    st.markdown("<div class='arsiv-eyebrow'>ARŞİV NO. 01 — SAYAÇ</div>", unsafe_allow_html=True)
    if is_anniversary_day and months_passed > 0:
        st.markdown(
            f"<div class='anniversary-banner'>🎉 Bugün {months_passed}. ay dönümümüz!</div>",
            unsafe_allow_html=True,
        )
    st.markdown(f"<div class='counter-number'>{delta_days}</div>", unsafe_allow_html=True)
    st.markdown(
        f"<div class='counter-label'>gün — 16 Ağustos 2025'ten beri · {months_passed} aydır birlikteyiz</div>",
        unsafe_allow_html=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)


def render_todo() -> None:
    st.markdown("<div class='arsiv-card'>", unsafe_allow_html=True)
    st.markdown("<div class='arsiv-eyebrow'>ARŞİV NO. 02 — GÜNLÜK GÖREVLER</div>", unsafe_allow_html=True)
    st.markdown("<h3 class='arsiv-h3'>Bugünün listesi</h3>", unsafe_allow_html=True)

    if not SHEETS_READY:
        st.warning(
            "Google Sheets bağlantısı henüz kurulmadı, bu yüzden görevler şu an "
            "sadece bu oturumda görünür ve senkron çalışmaz. Kurulum için KURULUM.md dosyasına bak."
        )
        for task in TASKS:
            st.checkbox(task, key=f"local_{task}")
        st.markdown("</div>", unsafe_allow_html=True)
        return

    state = load_todo_state(_sheet)
    done = sum(state.values())

    col_a, col_b = st.columns([5, 1])
    with col_a:
        st.progress(done / len(TASKS) if TASKS else 0, text=f"{done}/{len(TASKS)} tamamlandı")
    with col_b:
        if st.button("🔄", help="Diğer cihazdan gelen güncellemeleri çek"):
            st.rerun()

    for task in TASKS:
        current = state[task]
        # Anahtarı mevcut değere bağlıyoruz ki farklı cihazdan gelen bir
        # değişiklik ya da gece yarısı sıfırlanma, tarayıcıdaki eski
        # widget durumu yüzünden görmezden gelinmesin.
        widget_key = f"chk_{task}_{current}"
        new_val = st.checkbox(task, value=current, key=widget_key)
        if new_val != current:
            update_task(_sheet, task, new_val)
            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)


def render_archive() -> None:
    st.markdown("<div class='arsiv-card'>", unsafe_allow_html=True)
    st.markdown("<div class='arsiv-eyebrow'>ARŞİV NO. 03 — KAYITLAR</div>", unsafe_allow_html=True)
    st.markdown("<h3 class='arsiv-h3'>Anılar</h3>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("<div class='arsiv-subtitle'>Slaytlar</div>", unsafe_allow_html=True)
        for i, link in enumerate(SLIDE_LINKS, 1):
            st.markdown(f"<div class='arsiv-caption'>Slayt {i}</div>", unsafe_allow_html=True)
            components.iframe(link, height=260)
    with col2:
        st.markdown("<div class='arsiv-subtitle'>Videolar</div>", unsafe_allow_html=True)
        for i, link in enumerate(VIDEO_LINKS, 1):
            st.markdown(f"<div class='arsiv-caption'>Video {i}</div>", unsafe_allow_html=True)
            st.video(link)

    st.markdown("</div>", unsafe_allow_html=True)


# ---- kırmızı not kağıtları: bağımsız bir HTML/CSS/JS bileşeni ----
# Bunu ayrı bir bileşen olarak yazmamızın nedeni: Streamlit her tıklamada
# sunucu tarafında tüm sayfayı yeniden çalıştırıp yeniden çizer, bu da
# animasyonu her seferinde "kesip" baştan başlatır. Bu bileşen kendi
# iframe'i içinde, Streamlit'ten bağımsız, saf JS ile çalışıyor — bu yüzden
# animasyon pürüzsüz oluyor ve sayfanın geri kalanı hiç yeniden çizilmiyor.
NOTE_WIDGET_TEMPLATE = """
<div id="not-widget">
<style>
  #not-widget { font-family: 'Manrope', sans-serif; }
  #not-buton {
    width: 100%;
    background: linear-gradient(135deg, #4E2A6B, #1C1225);
    border: 1px solid rgba(201,166,224,0.4);
    color: #E8D9F5;
    border-radius: 999px;
    padding: 10px 18px;
    font-family: 'Manrope', sans-serif;
    font-weight: 600;
    font-size: 14px;
    cursor: pointer;
    transition: all .2s ease;
  }
  #not-buton:hover { background: #C9A6E0; color: #1C1225; border-color: #C9A6E0; }

  #kagit-alani {
    position: relative;
    margin-top: 18px;
    height: 340px;
    overflow-y: auto;
    overflow-x: hidden;
  }
  #kagit-alani:empty::before {
    content: "Henüz bir not okumadın. Butona bas.";
    display: block;
    color: rgba(232,217,245,0.35);
    font-size: 13px;
    padding-top: 24px;
    text-align: center;
  }

  .kagit-konum {
    position: absolute;
    left: 50%;
    width: 150px;
    margin-left: -75px;
  }
  .kagit {
    background: linear-gradient(160deg, #c9505c, #8e2836);
    color: #fdeceb;
    font-size: 12.5px;
    line-height: 1.45;
    padding: 16px 14px 14px 14px;
    border-radius: 3px;
    box-shadow: 0 12px 22px -10px rgba(0,0,0,0.65);
    position: relative;
    opacity: 0;
    transform: translateY(-22px) scale(0.9);
  }
  .kagit.goster {
    animation: dropIn .45s cubic-bezier(.2,.8,.3,1.05) forwards;
  }
  .kagit::before {
    content: '';
    position: absolute;
    top: -6px;
    left: 50%;
    transform: translateX(-50%);
    width: 11px;
    height: 11px;
    border-radius: 50%;
    background: #C9A6E0;
    box-shadow: 0 2px 4px rgba(0,0,0,0.4);
  }
  @keyframes dropIn { to { opacity: 1; transform: translateY(0) scale(1); } }

  #temizle-link {
    display: inline-block;
    margin-top: 8px;
    font-size: 11px;
    color: rgba(232,217,245,0.4);
    text-decoration: none;
    cursor: pointer;
  }
  #temizle-link:hover { color: #C9A6E0; }
</style>

<button id="not-buton">💌 Bir Not Oku</button>
<div id="kagit-alani"></div>
<a id="temizle-link" href="#">kağıtları topla</a>

<script>
  const notlar = __NOTLAR_JSON__;

  function karistir(dizi) {
    for (let i = dizi.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [dizi[i], dizi[j]] = [dizi[j], dizi[i]];
    }
    return dizi;
  }

  let havuz = karistir(notlar.slice());
  let sayac = 0;
  const alan = document.getElementById('kagit-alani');

  document.getElementById('not-buton').addEventListener('click', function () {
    if (havuz.length === 0) havuz = karistir(notlar.slice());
    const metin = havuz.pop();
    sayac += 1;

    const konum = document.createElement('div');
    konum.className = 'kagit-konum';
    const aci = (Math.random() * 22 - 11).toFixed(1);
    const dx = (Math.random() * 36 - 18).toFixed(0);
    konum.style.transform = 'translateX(' + dx + 'px) rotate(' + aci + 'deg)';
    konum.style.top = ((sayac - 1) * 14) + 'px';
    konum.style.zIndex = String(sayac);

    const kagit = document.createElement('div');
    kagit.className = 'kagit';
    kagit.textContent = metin;
    konum.appendChild(kagit);
    alan.appendChild(konum);

    requestAnimationFrame(function () {
      requestAnimationFrame(function () { kagit.classList.add('goster'); });
    });
    konum.scrollIntoView({ behavior: 'smooth', block: 'end' });
  });

  document.getElementById('temizle-link').addEventListener('click', function (e) {
    e.preventDefault();
    alan.innerHTML = '';
    sayac = 0;
  });
</script>
</div>
"""


def render_note_sidebar() -> None:
    with st.sidebar:
        st.markdown("<div class='arsiv-eyebrow'>ARŞİV NO. 04 — NOTLAR</div>", unsafe_allow_html=True)
        st.markdown("<h3 class='arsiv-h3' style='font-size:22px;'>Sana bir notum var</h3>", unsafe_allow_html=True)
        html = NOTE_WIDGET_TEMPLATE.replace("__NOTLAR_JSON__", json.dumps(NOTES, ensure_ascii=False))
        components.html(html, height=430, scrolling=False)


# ======================================================================
# ANA AKIŞ
# ======================================================================

render_header()
render_counter()
render_todo()
render_archive()
render_note_sidebar()

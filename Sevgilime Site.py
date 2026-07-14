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
TASKS = ["Türkçe Deneme", "Mat Deneme", "Alan", "Mevzuat", "Tekrarlar"]

# Google Slides linkleri — her biri "Web'de Yayınla" (Publish to web) ile
# alınan embed linki olmalı. Birden fazla slayt eklemek için listeye yeni
# satır ekle.
SLIDE_LINKS = [
    {"baslik": "Senin için hazırladığım ilk slayt", "link": "https://docs.google.com/presentation/d/e/2PACX-1vTEN1GL1WX38hiL706djqrsamUVQ0T56sgnZsKH2vDAyUKhNWV0SagDGp0TGjM9W7gi3KNzv2yH2exo/pubembed?start=true&loop=true&delayms=60000"},
    {"baslik": "Araşmak için özel çabam", "link": "https://docs.google.com/presentation/d/e/2PACX-1vShudHZcWUT119wbSyybEZxjaXW4eW6qi6JPHVvSyaX-zPd_DpljXIUO9JbaKM_rDqGD540Ln0dUwk9/pubembed?start=true&loop=true&delayms=60000"},
    {"baslik": "Doğum gününe özel", "link": "https://docs.google.com/presentation/d/e/2PACX-1vTnYFp7yi0g2ixOiMSSSFXIBoqkTvCyX45Uk_IfBZwP9DSyeDKJrnPqSoZVEMAjuiC4Nyi32XPt0Msm/pubembed?start=true&loop=true&delayms=60000"},
]

# YouTube "Liste Dışı" (Unlisted) video linkleri. İstediğin kadar ekleyebilirsin.
VIDEO_LINKS = [
    {"baslik": "Senle İlk Ortak Anımız", "link": "https://www.youtube.com/watch?v=R80w7Ye5Qz0"},
    {"baslik": "Sana Attığım İlk Video, hediyelerini açmıştım sevinçle", "link": "https://www.youtube.com/watch?v=NmjYdA1Wn-w"},
    {"baslik": "Doğum günün için geçmiştim kamera karşısına", "link": "https://www.youtube.com/watch?v=r7fq_oeVL_I"},
    {"baslik": "Bebeğim canı sıkılmıştı çareyi onla iletişimde bulduk", "link": "https://www.youtube.com/watch?v=HtP57OEh4VE"},
    {"baslik": "Sana olan sevgim dağlara taşlara ve alnıma yazılacak kadar yüce", "link": "https://www.youtube.com/watch?v=EPEGP6KZwK8"},
    {"baslik": "Sevgilime biraz desteğim gerekmişti", "link": "https://www.youtube.com/watch?v=5uyyKv4uxg4"},
    {"baslik": "Bi tanemin bana aldığı muhteşem hediyeyi açmıştım mutlulukla", "link": "https://www.youtube.com/watch?v=TNPneyS7D3o"},
]

# Not kartları — 25-30'a tamamla. Her biri virgülle ayrılmış bir metin.
# Bunlar tamamen senin yazacağın, kişisel notların; burada sadece örnek
# olarak orijinal 5 not duruyor.
NOTES = [
    "Dün de bugün de tüm geleceğimde de benim her şeyimsin",
    "İlk kez göktaşı yağmurunu kayda aldığımdaki heyecanımla seviyorum seni",
    "Ben her an, her saniye seninleyim; en büyük destekçin en büyük inanç kaynağınım",
    "Dünyanın dört bir yanını görmeyi özel kılan şey senin varlığın",
    "Sen benim her anımda şans meleğim, mutluluk kaynağımsın",
    "Yanında olmak bu hayatta isteyebileceğim en yüce şey, senin yanın benim mutluluğum her daim",
    "Senden önce ne kadar umutsuzsam senden sonra bi o kadar (u)mutluyum",
    "Kendime şanssız demeyi senle bıraktım, sana sahip olmak dünyadaki her şanstan öte",
    "Dün olmasa da bugün olamıyorsa da o iş her neyse yarın olacağına yine en çok ben inanrım",
    "Her anımda ve her anımda olmanı istiyorum, ne yaşanır bilmem yeter ki senle yaşansın",
    "Güzelliğinle, zekanla ve kalbinle hayatımın her köşesinde iyi ki sensin benimle",
    "İleride her şey olabilirim yeter ki senle olayım bebeğim",
    "En kötü günde yanındayım çünkü en iyi gününde yanında olmak istiyorum",
    
    # ... diğer notlarını buraya, aynı formatta, virgülle ayırarak ekle
]
MUSIC_LINKS = [
    "https://open.spotify.com/embed/track/3iByXxPXdGsuvlYGCHJ0ED",
    "https://www.youtube.com/embed/SxCZL9C3C1Y?si=v7OEHQ8PmsGD_BWk",
    "https://www.youtube.com/embed/wmCgjLPvueY",
    "https://open.spotify.com/embed/track/0MR22mypm79sVh5ejaTO6x",
    "https://open.spotify.com/embed/track/5rRAOgZOAqHwUMwVAXkUYU",
    "https://open.spotify.com/embed/track/1oDCK7PW72XEZ1pE5rh87A",
    "https://open.spotify.com/embed/track/73hX9ImSkUt2qMnB2BcAZo",
    "https://open.spotify.com/embed/track/4tC96bxgSFkA9tvPI0kCMb",
    "https://open.spotify.com/embed/track/6dknibX4oGFTxWoodrv9wu",
    "https://open.spotify.com/embed/track/1ko2lVN0vKGUl9zrU0qSlT",
    "https://open.spotify.com/embed/track/29Xdknl9fhRsV0oOYyQOKy",
    "https://www.youtube.com/embed/hgRtcsMvLT4",
    "https://open.spotify.com/embed/track/2mrSLrErsXbkcoIzGrD82E",
    "https://open.spotify.com/embed/track/39q7xibBdRboeMKUbZEB6g",
    "https://open.spotify.com/embed/track/5YEBDtfU1CkrYUCJtjRmaa",
    "https://open.spotify.com/embed/track/5arCoiBvRy9G6IMKLUVyzf",
    "https://open.spotify.com/embed/track/41UTnVa6DvcVPUYoXWA97h",
    "https://open.spotify.com/embed/track/1YSPIHUt1JiN9H1GcgH8Ce",
    "https://open.spotify.com/embed/track/48i055G1OT5KxGGftwFxWy",
    "https://open.spotify.com/embed/track/3Xls4cNOwy01dtrNXb1inG",
    "https://open.spotify.com/embed/track/62AuGbAkt8Ox2IrFFb8GKV",
    "https://open.spotify.com/embed/track/1s9tRQg4Mscu53c17qar36",
    "https://open.spotify.com/embed/track/7yzbimr8WVyAtBX3Eg6UL9",
    "https://open.spotify.com/embed/track/6DJ1zVJeXzpfGjFtELxnNw",
    "https://open.spotify.com/embed/track/6NmdCdQGOBVxVLIIJdPw3z",
    "https://open.spotify.com/embed/track/1S2AvHZ9OFDX5EW30mTVKg",
    "https://open.spotify.com/embed/track/2bCQHF9gdG5BNDVuEIEnNk",
    "https://open.spotify.com/embed/track/1qCQTy0fTXerET4x8VHyr9",
    "https://open.spotify.com/embed/track/63T7DJ1AFDD6Bn8VzG6JE8",
    "https://open.spotify.com/embed/track/2RaA6kIcvomt77qlIgGhCT",
    "https://open.spotify.com/embed/track/62oNfnQqObaqARM0DTibAL",
    "https://open.spotify.com/embed/track/3MrRksHupTVEQ7YbA0FsZK",
    "https://open.spotify.com/embed/track/2aibwv5hGXSgw7Yru8IYTO",
    "https://open.spotify.com/embed/track/7LfpUSGgCmK1YlNUDuhYet",
    "https://open.spotify.com/embed/track/7lQWRAjyhTpCWFC0jmclT4",
    "https://open.spotify.com/embed/track/5CGpPUcUahMuLzkNK9ZgPP",
    "https://open.spotify.com/embed/track/1ENLIbxO4Uma773neTHxbp",
    "https://open.spotify.com/embed/track/0uvx2NCmezldX5aPjnKe3g",
    "https://open.spotify.com/embed/track/29FQEJUtBAnxWEkux39d7I",
    "https://open.spotify.com/embed/track/4VqGRYxeWXLGtZLOywd1uB",
    "https://open.spotify.com/embed/track/5xdySZ8v0lEOKblcwXWT3M",
    "https://open.spotify.com/embed/track/2QTzQw5R2C5rL6S9B1zrO7",
    "https://open.spotify.com/embed/track/5bCp9MMG1Qo4QB2OHoSRpN",
    "https://open.spotify.com/embed/track/4UDmDIqJIbrW0hMBQMFOsM",
    "https://open.spotify.com/embed/track/0z1o5L7HJx562xZSATcIpY",
    "https://open.spotify.com/embed/track/5haXbSJqjjM0TCJ5XkfEaC",
    "https://open.spotify.com/embed/track/0IfQ4tp3J7VqTfJbtzPLOq",
    "https://open.spotify.com/embed/track/561F1zqRwGPCTMRsLsXVtL",
    "https://open.spotify.com/embed/track/4mn2kNTqiGLwaUR8JdhJ1l",
    "https://open.spotify.com/embed/track/0oUBuOO4g9P4lREqfqR5nq",
    "https://open.spotify.com/embed/track/2h7c8sfEWiKhDCWlt2KekF",
    "https://open.spotify.com/embed/track/7FXj7Qg3YorUxdrzvrcY25",
    "https://open.spotify.com/embed/track/2e2frIpnZUcPl4vXaxLbCk",
    "https://open.spotify.com/embed/track/5HwAaXDLVDgVcoGIjDRANK",
    "https://open.spotify.com/embed/track/5dUMh0ugelpKfoFp3qChuK",
    "https://open.spotify.com/embed/track/4WOruM7TiQSETsWYy8bDSX",
    "https://open.spotify.com/embed/track/30FURVTCpbKyykjSEQzGkH",
    "https://open.spotify.com/embed/track/12hNVeWLSUXzOySe86H2KI",
    "https://open.spotify.com/embed/track/5MxNLUsfh7uzROypsoO5qe",
    "https://open.spotify.com/embed/track/4C2BEVMCOoTRYLQdxumczm",
    "https://open.spotify.com/embed/track/1LQ2xfAGdiZQBOTzjQwRlh",
    "https://open.spotify.com/embed/track/0x4GSz5C4XZDkNhFswGboC",
    "https://open.spotify.com/embed/track/4s6LhHAV5SEsOV0lC2tjvJ",
    "https://open.spotify.com/embed/track/3spdoTYpuCpmq19tuD0bOe",
    "https://open.spotify.com/embed/track/6b37xrsNCWYIUphFBazqD6",
    "https://open.spotify.com/embed/track/1FWtprHStw6VvFqFXDmLT9",
    "https://open.spotify.com/embed/track/3wMJQ5qeN02ljNn3lRMVka",
    "https://open.spotify.com/embed/track/1hkzQo4E2cxGHZEd706zje",
    "https://open.spotify.com/embed/track/4FmCUATNIarCQh72JYdvnm",
    "https://open.spotify.com/embed/track/3jiaYurK7YVA9hPMIgHwSH",
    "https://open.spotify.com/embed/track/7gmZSC6kk7TGscGMZ86sb4",
    "https://open.spotify.com/embed/track/6tR3guUSh0V3sz5IcZsUrw",
    "https://open.spotify.com/embed/track/0fmNiN85g1XF1NemAGY7G2",
    "https://open.spotify.com/embed/track/1hQFF33xi8ruavZNyovtUN",
    "https://open.spotify.com/embed/track/4BcAcEbp6j6luowfAliUfW",
    "https://open.spotify.com/embed/track/5W9w0b1Nn20jFnPBdQ5LVH",
    "https://open.spotify.com/embed/track/35oDERZK91SJtzPqfSPDil",
    "https://open.spotify.com/embed/track/0ISVTNluQbDYEHVUsstVcb",
    "https://open.spotify.com/embed/track/2pCLg7o60iAnNEbYDW9Lhy",
    "https://open.spotify.com/embed/track/75L9HQapNnbNUEUGwviKON",
    "https://open.spotify.com/embed/track/3P8AIM1rwNA1x5zfAFw8lI",
    "https://www.youtube.com/embed/sezYlHYxs-Q",
    "https://open.spotify.com/embed/track/5kbX6QlSDGgprK3jVuxGt7",
    "https://open.spotify.com/embed/track/74VR3AkGPhbYXnxcOYa16x",
    "https://open.spotify.com/embed/track/4H065d2WS05Pig3f5u0ARg",
    "https://open.spotify.com/embed/track/33KPNILfz7Wv8Nd4etVazJ",
    "https://open.spotify.com/embed/track/7xiw42KTmCcqfZNCZqUcnF",
    "https://open.spotify.com/embed/track/7shYNyB5sVWtKfnnnHdB5P",
    "https://open.spotify.com/embed/track/0cgcD73SD4nFdTK2oKofzW",
    "https://open.spotify.com/embed/track/2S7RApTsKT0CtYojYq2cKz",
    "https://open.spotify.com/embed/track/0ShJKWx4I64bNYogXBoV82",
    "https://open.spotify.com/embed/track/3UPrUZ9mJWEPjXzgF7GS8f",
    "https://open.spotify.com/embed/track/0OGpY82sToZSrrDgk4Iuic",
    "https://open.spotify.com/embed/track/4FGYzQqH2i1E3OtuMydnzY",
    "https://open.spotify.com/embed/track/5dIFM4dkwEjMnFppbHTsEA",
    "https://open.spotify.com/embed/track/4pXQgxhWKlII677i9DBDRL",
    "https://open.spotify.com/embed/track/20k2aZQl6hH0EfGMDxXGey",
    "https://open.spotify.com/embed/track/7rWgGyRK7RAqAAXy4bLft9",
    "https://open.spotify.com/embed/track/2xZfPZxInlDXDKc6NDts8Z",
    "https://open.spotify.com/embed/track/2FEWcWHnDmGD6WSqpW4VYu",
    "https://open.spotify.com/embed/track/6GMbt2Q4g7Qh46Ko7e3rbA",
]     
START_DATE = datetime.date(2025, 8, 16)

TR_TZ = datetime.timezone(datetime.timedelta(hours=3))


def turkiye_bugunu() -> datetime.date:
    """Streamlit Cloud sunucuları UTC saatiyle çalışıyor; gün değişimini
    (gece yarısı) bu yüzden Türkiye saatine göre hesaplıyoruz."""
    return datetime.datetime.now(TR_TZ).date()

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

.st-key-counter_card,
.st-key-todo_card,
.st-key-archive_card,
.st-key-music_card, 
.st-key-movie_card {
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

.counter-row {
    display: flex;
    align-items: baseline;
    gap: 10px;
}

.counter-number {
    font-family: 'Space Mono', monospace;
    font-size: 58px;
    font-weight: 700;
    line-height: 1;
    background: linear-gradient(120deg, var(--lilac-soft), var(--lilac) 60%, var(--paper-red));
    -webkit-background-clip: text;
    background-clip: text;
    color: transparent;
}

.counter-unit {
    font-family: 'Manrope', sans-serif;
    font-size: 18px;
    font-weight: 600;
    color: var(--lilac-soft);
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
        # API'nin matris uyuşmazlığından hata vermemesi için satır uzunluklarını boşluklarla 4'e tamamlıyoruz
        data_rows = [[t, "FALSE", "", ""] for t in TASKS]
        sheet.update([header] + data_rows, "A1")
        sheet.update([[""]], "D2")


def load_todo_state(sheet) -> dict:
    """Sheet'ten bugünün görev durumlarını okur; tarih değiştiyse otomatik sıfırlar."""
    ensure_sheet_initialized(sheet)
    values = sheet.get_all_values()
    today_str = turkiye_bugunu().isoformat()
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
except Exception as e:
    _sheet = None
    SHEETS_READY = False
    _sheets_error = str(e)


# ======================================================================
# BÖLÜMLER
# ======================================================================

def render_header() -> None:
    st.markdown("<div class='arsiv-eyebrow'>💜 ÖZEL ARŞİV</div>", unsafe_allow_html=True)
    st.markdown("<h1 class='arsiv-h1'>Bizim Arşivimiz</h1>", unsafe_allow_html=True)
    st.markdown("<div class='arsiv-tagline'>Gün, görev, kayıt ve not — hepsi burada.</div>", unsafe_allow_html=True)


def render_counter() -> None:
    today = turkiye_bugunu()
    delta_days = (today - START_DATE).days
    months_passed = (today.year - START_DATE.year) * 12 + (today.month - START_DATE.month)
    if today.day < START_DATE.day:
        months_passed -= 1
    is_anniversary_day = today.day == START_DATE.day

    with st.container(key="counter_card"):
        if is_anniversary_day and months_passed > 0:
            st.markdown(
                f"<div class='anniversary-banner'>🎉 Bugün {months_passed}. ay dönümümüz!</div>",
                unsafe_allow_html=True,
            )
        st.markdown(
            f"<div class='counter-row'><span class='counter-number'>{delta_days}</span>"
            f"<span class='counter-unit'>gün</span></div>"
            f"{months_passed} aydır birlikteyiz</div>",
            unsafe_allow_html=True,
        )

def render_music_box() -> None:
    if not MUSIC_LINKS:
        return
    import random
    # Her gün için o güne özel sabit bir rastgelelik (seed) oluşturuyoruz.
    # Böylece şarkı gün boyu değişmez ama her gün listeden tamamen rastgele seçilir.
    rng = random.Random(turkiye_bugunu().toordinal())
    gunun_sarkisi = rng.choice(MUSIC_LINKS)
    
    with st.container(key="music_card"):
        st.markdown("<div class='arsiv-eyebrow'>GÜNÜN FREKANSI</div>", unsafe_allow_html=True)
        # Spotify'ın varsayılan embed yüksekliği 152, Apple Music'in 175'tir.
        components.iframe(gunun_sarkisi, height=152 if "spotify" in gunun_sarkisi else 175)
# --- DEĞİŞECEK / EKLENECEK KISIM BAŞLANGICI ---
@st.cache_data(ttl=86400)
def get_movie_of_the_day(date_str):
    import csv, random, re
    import urllib.request
    try:
        # 1. Excel'in bozduğu noktalı virgül ve görünmez BOM (utf-8-sig) sorunlarını otomatik çözer
        with open("watchlist.csv", "r", encoding="utf-8-sig") as f:
            ilk_satir = f.readline()
            ayirici = ";" if ";" in ilk_satir else ","
            f.seek(0)
            reader = csv.DictReader(f, delimiter=ayirici)
            # Boş satırları atlayarak filmleri listeye çeker
            movies = [row for row in reader if row.get("Name")]
        
        if not movies:
            return "Hata: Liste okunamadı (Sütunlar bozuk)", "", "", "https://s.ltrbxd.com/static/img/empty-poster-250.8461d43a.png"

        rng = random.Random(datetime.date.today().toordinal())
        gunun_filmi = rng.choice(movies)
        
        ad = gunun_filmi.get("Name", "Bilinmeyen Film")
        link = gunun_filmi.get("Letterboxd URI", "")
        yil = gunun_filmi.get("Year", "")
        
        # 2. Harici kütüphane gerektirmeyen (built-in) urllib ile afişi çekiyoruz
        afis = "https://s.ltrbxd.com/static/img/empty-poster-250.8461d43a.png"
        if link:
            req = urllib.request.Request(link, headers={"User-Agent": "Mozilla/5.0"})
            try:
                with urllib.request.urlopen(req) as response:
                    html = response.read().decode('utf-8')
                    match = re.search(r'"image":"(https://a\.ltrbxd\.com/resized/.*?.jpg.*?)"', html)
                    if match: afis = match.group(1)
            except:
                pass # Siteden afiş çekilemezse varsayılan gri görselle devam eder
        
        return ad, yil, link, afis
    except Exception as e:
        # 3. Kod patlarsa saklanmasın, hatayı ekrana bassın ki sorunu görelim
        return f"Sistem Hatası: {str(e)}", "", "", "https://s.ltrbxd.com/static/img/empty-poster-250.8461d43a.png"


def render_movie_box() -> None:
    ad, yil, link, afis = get_movie_of_the_day(datetime.date.today().isoformat())
    if not ad: return
    
    with st.container(key="movie_card"):
        st.markdown("<div class='arsiv-eyebrow'>GÜNÜN FİLMİ</div>", unsafe_allow_html=True)
        html = f"""
        <div style="display: flex; gap: 15px; align-items: center; background: rgba(255,255,255,0.05); padding: 10px; border-radius: 12px; border: 1px solid rgba(201,166,224,0.2);">
            <img src="{afis}" style="width: 75px; border-radius: 6px; box-shadow: 0 4px 8px rgba(0,0,0,0.3);">
            <div>
                <div style="color: #E8D9F5; font-weight: bold; font-size: 16px; font-family: 'Manrope', sans-serif;">{ad} <span style="font-size: 12px; color: rgba(232,217,245,0.6);">({yil})</span></div>
                <a href="{link}" target="_blank" style="display: inline-block; margin-top: 8px; color: #1C1225; background: #C9A6E0; padding: 5px 12px; border-radius: 999px; text-decoration: none; font-size: 12px; font-weight: bold; font-family: 'Manrope', sans-serif; transition: opacity 0.2s;">Letterboxd'da İncele</a>
            </div>
        </div>
        """
        st.markdown(html, unsafe_allow_html=True)
# --- DEĞİŞECEK / EKLENECEK KISIM BİTİŞİ ---
# ---- çalışma zamanlayıcısı: kronometre + geri sayım ----
# Not kağıtları gibi bu da ayrı bir HTML/JS bileşeni. Saniyede bir
# güncellenmesi gerekiyor; bunu Streamlit'in sunucu taraflı rerun'larıyla
# yapsaydık hem görüntü titrer hem de (Google Sheets bağlıyken) saniyede
# bir gereksiz API isteği atardık. Bu yüzden tamamen tarayıcıda, kendi
# başına çalışıyor.
TIMER_WIDGET_HTML = """
<div id="zaman-widget">
<style>
  #zaman-widget { font-family: 'Manrope', sans-serif; color: #E8D9F5; }
  .zaman-modlar { display: flex; gap: 8px; margin-bottom: 14px; }
  .zaman-mod-buton {
    flex: 1;
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(201,166,224,0.3);
    color: rgba(232,217,245,0.6);
    border-radius: 999px;
    padding: 7px 10px;
    font-family: 'Manrope', sans-serif;
    font-size: 12px;
    font-weight: 600;
    cursor: pointer;
    transition: all .2s ease;
  }
  .zaman-mod-buton.aktif { background: #C9A6E0; color: #1C1225; border-color: #C9A6E0; }
  .zaman-mod-buton:disabled { cursor: not-allowed; opacity: 0.5; }

  .zaman-sure-girisi {
    display: none;
    align-items: center;
    gap: 8px;
    margin-bottom: 10px;
    font-size: 12px;
    color: rgba(232,217,245,0.6);
  }
  .zaman-sure-girisi input {
    width: 56px;
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(201,166,224,0.3);
    border-radius: 8px;
    color: #E8D9F5;
    padding: 4px 8px;
    font-family: 'Space Mono', monospace;
    font-size: 13px;
  }

  .zaman-gosterge {
    font-family: 'Space Mono', monospace;
    font-size: 42px;
    font-weight: 700;
    text-align: center;
    padding: 6px 0 16px 0;
    letter-spacing: 1px;
    color: #E8D9F5;
  }
  .zaman-gosterge.bitti { color: #B23A48; animation: zamanVurgu 0.6s ease 3; }
  @keyframes zamanVurgu { 50% { transform: scale(1.08); } }

  .zaman-kontroller { display: flex; gap: 8px; }
  .zaman-buton {
    flex: 1;
    background: linear-gradient(135deg, #4E2A6B, #1C1225);
    border: 1px solid rgba(201,166,224,0.4);
    color: #E8D9F5;
    border-radius: 999px;
    padding: 9px 14px;
    font-family: 'Manrope', sans-serif;
    font-weight: 600;
    font-size: 13px;
    cursor: pointer;
    transition: all .2s ease;
  }
  .zaman-buton:hover { background: #C9A6E0; color: #1C1225; border-color: #C9A6E0; }
</style>

<div class="zaman-modlar">
  <button class="zaman-mod-buton aktif" id="mod-kronometre">⏱ Kronometre</button>
  <button class="zaman-mod-buton" id="mod-geri-sayim">⏳ Geri Sayım</button>
</div>

<div class="zaman-sure-girisi" id="sure-girisi-alani">
  <span>Süre (dakika):</span>
  <input type="number" id="sure-input" value="25" min="1" max="180">
</div>

<div class="zaman-gosterge" id="zaman-gosterge">00:00</div>

<div class="zaman-kontroller">
  <button class="zaman-buton" id="zaman-baslat">Başlat</button>
  <button class="zaman-buton" id="zaman-sifirla">Sıfırla</button>
</div>

<script>
  let mod = 'up';
  let saniye = 0;
  let hedefSaniye = 25 * 60;
  let calisiyor = false;
  let zamanlayici = null;

  const gosterge = document.getElementById('zaman-gosterge');
  const baslatBtn = document.getElementById('zaman-baslat');
  const sifirlaBtn = document.getElementById('zaman-sifirla');
  const modKronometre = document.getElementById('mod-kronometre');
  const modGeriSayim = document.getElementById('mod-geri-sayim');
  const sureGirisiAlani = document.getElementById('sure-girisi-alani');
  const sureInput = document.getElementById('sure-input');

  function formatla(sn) {
    const s = Math.max(0, sn);
    const dk = Math.floor(s / 60);
    const saniyeK = s % 60;
    return String(dk).padStart(2, '0') + ':' + String(saniyeK).padStart(2, '0');
  }

  function goster() {
    gosterge.textContent = mod === 'up' ? formatla(saniye) : formatla(hedefSaniye - saniye);
  }

  function beepCal() {
    try {
      const ctx = new (window.AudioContext || window.webkitAudioContext)();
      const osc = ctx.createOscillator();
      const kazanc = ctx.createGain();
      osc.connect(kazanc);
      kazanc.connect(ctx.destination);
      osc.frequency.value = 720;
      kazanc.gain.setValueAtTime(0.15, ctx.currentTime);
      osc.start();
      osc.stop(ctx.currentTime + 0.35);
    } catch (e) { /* sessiz geç */ }
  }

  function tikla() {
    saniye += 1;
    if (mod === 'down' && saniye >= hedefSaniye) {
      saniye = hedefSaniye;
      durdur();
      gosterge.classList.add('bitti');
      beepCal();
    }
    goster();
  }

  function baslatDurdur() {
    if (calisiyor) {
      durdur();
    } else {
      calisiyor = true;
      baslatBtn.textContent = 'Duraklat';
      modKronometre.disabled = true;
      modGeriSayim.disabled = true;
      zamanlayici = setInterval(tikla, 1000);
    }
  }

  function durdur() {
    calisiyor = false;
    baslatBtn.textContent = 'Başlat';
    clearInterval(zamanlayici);
  }

  function sifirla() {
    durdur();
    saniye = 0;
    gosterge.classList.remove('bitti');
    modKronometre.disabled = false;
    modGeriSayim.disabled = false;
    goster();
  }

  modKronometre.addEventListener('click', function () {
    if (calisiyor) return;
    mod = 'up';
    modKronometre.classList.add('aktif');
    modGeriSayim.classList.remove('aktif');
    sureGirisiAlani.style.display = 'none';
    sifirla();
  });

  modGeriSayim.addEventListener('click', function () {
    if (calisiyor) return;
    mod = 'down';
    modGeriSayim.classList.add('aktif');
    modKronometre.classList.remove('aktif');
    sureGirisiAlani.style.display = 'flex';
    sifirla();
  });

  sureInput.addEventListener('change', function () {
    const dk = Math.max(1, Math.min(180, parseInt(sureInput.value) || 25));
    sureInput.value = dk;
    hedefSaniye = dk * 60;
    if (!calisiyor) { saniye = 0; goster(); }
  });

  baslatBtn.addEventListener('click', baslatDurdur);
  sifirlaBtn.addEventListener('click', sifirla);

  goster();
</script>
</div>
"""
def render_shared_timer():
    if not SHEETS_READY:
        st.warning("Ortak kronometre için Google Sheets bağlantısı gerekiyor.")
        return

    ws = get_shared_timer_sheet()
    records = ws.get_all_values()
    
    # Veritabanındaki son durumu okuyoruz
    durum = records[1][0] if len(records) > 1 and len(records[1]) > 0 else "DURDU"
    baslangic_str = records[1][1] if len(records) > 1 and len(records[1]) > 1 else "0"

    col_btn1, col_btn2 = st.columns(2)
    if durum == "DURDU":
        if col_btn1.button("▶ Ortak Başlat", use_container_width=True):
            now_str = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=3))).isoformat()
            ws.update([["CALISIYOR", now_str]], "A2")
            st.rerun()
    else:
        if col_btn1.button("⏸ Herkes İçin Durdur", use_container_width=True):
            ws.update([["DURDU", "0"]], "A2")
            st.rerun()

    if col_btn2.button("🔄 Eşitle", use_container_width=True, help="Diğer cihazdan başlatıldıysa süreyi çeker"):
        st.rerun()

    # Eğer çalışıyorsa, aradaki zaman farkını bulup sadece sayaç kısmını HTML ile akıcı gösteriyoruz
    if durum == "CALISIYOR" and baslangic_str != "0":
        baslangic = datetime.datetime.fromisoformat(baslangic_str)
        now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=3)))
        diff_seconds = int((now - baslangic).total_seconds())
        if diff_seconds < 0: diff_seconds = 0
        
        mini_html = f"""
        <div style="font-family: 'Space Mono', monospace; font-size: 48px; font-weight: 700; text-align: center; color: #E8D9F5; padding: 15px 0;">
            <span id="shared-time"></span>
        </div>
        <script>
            let saniye = {diff_seconds};
            function formatla(sn) {{
                const dk = Math.floor(sn / 60);
                const saniyeK = sn % 60;
                return String(dk).padStart(2, '0') + ':' + String(saniyeK).padStart(2, '0');
            }}
            document.getElementById('shared-time').textContent = formatla(saniye);
            setInterval(() => {{
                saniye++;
                document.getElementById('shared-time').textContent = formatla(saniye);
            }}, 1000);
        </script>
        """
        components.html(mini_html, height=120)
    else:
        st.markdown("<div style=\"font-family: 'Space Mono', monospace; font-size: 48px; font-weight: 700; text-align: center; color: #E8D9F5; padding: 15px 0;\">00:00</div>", unsafe_allow_html=True)

def render_todo() -> None:
    with st.container(key="todo_card"):
        st.markdown("<h3 class='arsiv-h3'>Bugünün listesi</h3>", unsafe_allow_html=True)

        if not SHEETS_READY:
            st.warning(
                "Google Sheets bağlantısı henüz kurulmadı, bu yüzden görevler şu an "
                "sadece bu oturumda görünür ve senkron çalışmaz. Kurulum için KURULUM.md dosyasına bak."
            )
            st.code(_sheets_error, language="text")
            for task in TASKS:
                st.checkbox(task, key=f"local_{task}")
        else:
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

        st.markdown(
            "<div class='arsiv-subtitle' style='margin-top:22px;'>Çalışma Zamanlayıcısı</div>",
            unsafe_allow_html=True,
        )
        mod = st.radio("Zamanlayıcı Modu", ["Kişisel (Kronometre / Geri Sayım)", "Ortak Kronometre"], horizontal=True, label_visibility="collapsed")
        if mod == "Kişisel (Kronometre / Geri Sayım)":
            components.html(TIMER_WIDGET_HTML, height=215, scrolling=False)
        else:
            render_shared_timer()


def render_archive() -> None:
    with st.container(key="archive_card"):
        st.markdown("<h3 class='arsiv-h3'>Anılar</h3>", unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("<div class='arsiv-subtitle'>Slaytlar</div>", unsafe_allow_html=True)
            for slayt in SLIDE_LINKS:
                st.markdown(f"<div class='arsiv-caption'>{slayt['baslik']}</div>", unsafe_allow_html=True)
                components.iframe(slayt["link"], height=260)
        with col2:
            st.markdown("<div class='arsiv-subtitle'>Videolar</div>", unsafe_allow_html=True)
            for video in VIDEO_LINKS:
                st.markdown(f"<div class='arsiv-caption'>{video['baslik']}</div>", unsafe_allow_html=True)
                st.video(video["link"])


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
def get_messages_sheet():
    if not SHEETS_READY: return None
    worksheets = _sheet.spreadsheet.worksheets()
    for ws in worksheets:
        if ws.title == "Mesajlar":
            return ws
    # Sayfa yoksa arka planda kendi oluşturur
    ws = _sheet.spreadsheet.add_worksheet("Mesajlar", 100, 3)
    ws.update([["Tarih", "Mesaj", "Okundu_mu"]], "A1")
    return ws

@st.dialog("Sürpriz Mesaj Yaz")
def mesaj_yaz_modal(msg_sheet):
    st.markdown("Ona görünmesini istediğin notu buraya bırak. Sen gönderdikten sonraki ilk girişinde ekranının ortasında belirecek.", unsafe_allow_html=True)
    yeni_mesaj = st.text_area("Mesaj", label_visibility="collapsed", placeholder="İçinden geçenleri yaz...")
    if st.button("Gönder", use_container_width=True):
        if yeni_mesaj.strip():
            # Türkiye saatini baz alarak kaydeder
            tarih = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=3))).isoformat()
            msg_sheet.append_row([tarih, yeni_mesaj.strip(), "FALSE"])
            # Gönderen kişinin ekranında bildirim çıkmaması için o anlık oturum damgası basıyoruz
            st.session_state.just_sent = True
            st.rerun()

@st.dialog("Sana Bir Mesaj Var! 💌")
def mesaj_oku_modal(msg_sheet, mesaj_metni, row_index):
    st.markdown(f"<div style='font-size:18px; text-align:center; padding: 20px 0; color: #E8D9F5; font-family: \"Manrope\", sans-serif;'>{mesaj_metni}</div>", unsafe_allow_html=True)
    if st.button("Okudum, kalbime sakladım", use_container_width=True):
        # Okunduğu an veritabanında TRUE olur ve kalıcı olarak imha edilmiş gibi görünmez olur
        msg_sheet.update_cell(row_index, 3, "TRUE")
        st.rerun()
def get_shared_timer_sheet():
    if not SHEETS_READY: return None
    for ws in _sheet.spreadsheet.worksheets():
        if ws.title == "OrtakKronometre":
            return ws
    # Sayfa yoksa arka planda oluşturur: A1(Durum), B1(Baslangic_Tarihi)
    ws = _sheet.spreadsheet.add_worksheet("OrtakKronometre", 10, 2)
    ws.update([["Durum", "Baslangic_Tarihi"], ["DURDU", "0"]], "A1")
    return ws
def render_note_sidebar() -> None:
    with st.sidebar:
        st.markdown("<h3 class='arsiv-h3' style='font-size:22px;'>Sana bir notum var</h3>", unsafe_allow_html=True)
        html = NOTE_WIDGET_TEMPLATE.replace("__NOTLAR_JSON__", json.dumps(NOTES, ensure_ascii=False))
        components.html(html, height=430, scrolling=False)

        st.markdown("<hr style='margin: 30px 0 20px 0;'>", unsafe_allow_html=True)
        
        if "just_sent" not in st.session_state:
            st.session_state.just_sent = False

        if SHEETS_READY:
            msg_sheet = get_messages_sheet()
            records = msg_sheet.get_all_values()
            
            unread_msg = None
            unread_row = -1
            # Arka plandaki verileri tarar ve okunmamış (FALSE) ilk mesajı bulur
            for i, row in enumerate(records):
                if i == 0: continue
                if len(row) >= 3 and row[2] == "FALSE":
                    unread_msg = row[1]
                    unread_row = i + 1
                    break

            if unread_msg and not st.session_state.just_sent:
                st.markdown("<div class='arsiv-eyebrow' style='color:#C9A6E0; text-align:center;'>SÜRPRİZ!</div>", unsafe_allow_html=True)
                if st.button("💌 Sürpriz Mesajı Oku", use_container_width=True):
                    mesaj_oku_modal(msg_sheet, unread_msg, unread_row)
            else:
                if st.button("📝 Yeni Sürpriz Mesaj Yaz", use_container_width=True):
                    mesaj_yaz_modal(msg_sheet)

# ======================================================================
# ANA AKIŞ
# ======================================================================

render_header()

col_sayac, col_liste = st.columns([1, 1.25])
with col_sayac:
    render_counter()
    render_music_box()
    render_movie_box()
with col_liste:
    render_todo()

render_archive()
render_note_sidebar()

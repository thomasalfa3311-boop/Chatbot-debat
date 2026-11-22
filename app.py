import streamlit as st
import anthropic

st.set_page_config(page_title="AI Debat", page_icon="🎤")
st.title("🎤 AI Debat")

client = anthropic.Anthropic(api_key=st.secrets["ANTHROPIC_API_KEY"])
MODEL = "claude-sonnet-5-5"

# ---------- Sidebar: pengaturan debat ----------
with st.sidebar:
    st.header("Pengaturan Debat")
    topik = st.text_input("Topik debat", "Sekolah sebaiknya melarang HP")
    posisi_ai = st.radio("AI berada di pihak", ["Pro (setuju)", "Kontra (tidak setuju)"])
    level = st.select_slider("Tingkat kesulitan", ["Santai", "Sedang", "Sengit"], value="Sedang")
    if st.button("Mulai ulang debat"):
        st.session_state.pop("messages", None)
        st.rerun()

SYSTEM_PROMPT = f"""Kamu adalah lawan debat yang cerdas, sopan, dan tajam.
Topik debat: "{topik}".
Kamu berada di pihak: {posisi_ai}. Pertahankan posisi ini sepanjang debat.
Tingkat kesulitan: {level}.

Aturan:
- Gunakan bahasa Indonesia yang jelas dan mudah dipahami.
- Serang argumen lawan, bukan orangnya.
- Beri alasan dan contoh konkret. Jangan mengarang data atau statistik.
- Jawab singkat (maksimal 3 paragraf pendek), akhiri dengan satu pertanyaan atau tantangan balik.
- Kalau lawan membuat argumen yang benar-benar kuat, akui dengan jujur lalu lanjutkan sanggahanmu.
"""

# ---------- Riwayat chat ----------
if "messages" not in st.session_state:
    st.session_state.messages = []

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

if not st.session_state.messages:
    st.info(f"Topik: **{topik}**. AI di pihak **{posisi_ai}**. Kirim argumen pertamamu!")

# ---------- Input pengguna ----------
if prompt := st.chat_input("Tulis argumenmu..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            with client.messages.stream(
                model=MODEL,
                max_tokens=800,
                system=SYSTEM_PROMPT,
                messages=st.session_state.messages,
            ) as stream:
                jawaban = st.write_stream(stream.text_stream)
        except Exception as e:
            jawaban = f"Maaf, terjadi error: {e}"
            st.error(jawaban)

    st.session_state.messages.append({"role": "assistant", "content": jawaban})

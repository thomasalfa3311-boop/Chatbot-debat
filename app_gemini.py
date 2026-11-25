import streamlit as st
from google import genai
from google.genai import types

st.set_page_config(page_title="AI Debat", page_icon="🎤")
st.title("🎤 AI Debat")

client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
MODEL = "gemini-3.8-flash"

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


def ke_format_gemini(messages):
    """Ubah riwayat chat ke format Gemini (peran 'assistant' jadi 'model')."""
    hasil = []
    for m in messages:
        peran = "user" if m["role"] == "user" else "model"
        hasil.append(types.Content(role=peran, parts=[types.Part(text=m["content"])]))
    return hasil


def aliran_teks(messages):
    for chunk in client.models.generate_content_stream(
        model=MODEL,
        contents=ke_format_gemini(messages),
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            max_output_tokens=800,
        ),
    ):
        if chunk.text:
            yield chunk.text


# ---------- Input pengguna ----------
if prompt := st.chat_input("Tulis argumenmu..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            jawaban = st.write_stream(aliran_teks(st.session_state.messages))
        except Exception as e:
            jawaban = f"Maaf, terjadi error: {e}"
            st.error(jawaban)

    st.session_state.messages.append({"role": "assistant", "content": jawaban})

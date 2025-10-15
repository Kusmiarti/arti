import streamlit as st
import google.generativeai as genai
import os

# ==============================================================================
# KONFIGURASI APLIKASI STREAMLIT
# ==============================================================================

st.set_page_config(
    page_title="Chatbot Gemini Streamlit",
    page_icon="🤖"
)

st.title("🤖 Chatbot Gemini dengan Streamlit")
st.caption("Aplikasi Chatbot sederhana menggunakan Google Gemini API dan Streamlit.")

# ==============================================================================
# PENGATURAN API KEY DAN MODEL (PENTING!)
# ==============================================================================

# Ganti ini dengan API KEY GEMINI ANDA!
# Catatan: Di aplikasi Streamlit, lebih aman menggunakan st.secrets atau variabel lingkungan
# daripada menempatkan key langsung di kode.
# Untuk demo, kita gunakan variabel yang bisa diganti.
# JANGAN BAGIKAN KODE INI DENGAN API KEY DI DALAMNYA KE PUBLIK.
# Sebaiknya gunakan st.secrets["GEMINI_API_KEY"]
API_KEY = "AIzaSyBteyzW2lqx9HkiwDSTSgln6acWaXP9g-U" # <--- GANTI BAGIAN INI!

# Nama model Gemini yang akan digunakan.
MODEL_NAME = 'gemini-1.5-flash'

# ==============================================================================
# KONTEKS AWAL CHATBOT
# ==============================================================================

# Definisikan peran chatbot Anda di sini (Instruksi Sistem)
INITIAL_CHATBOT_CONTEXT = [
    {
        "role": "user",
        "parts": ["Kamu adalah ahli bahasa jawa. Berikan contoh kata dan kalimat yang sesuai unggah-ungguh basa jawa beserta artinya dalam bahasa indonesia. Jawaban singkat dan faktual. Tolak pertanyaan non-sejarah."]
    },
    {
        "role": "model",
        "parts": ["Baik! saya akan berikan kata dan kalimat yang sesuai dengan unggah-ungguh basa jawa beserta artinya dalam bahasa indonesia. Apa yang ingin kamu ketahui tentang basa Jawa?"]
    }
]

# ==============================================================================
# FUNGSI INISIALISASI
# ==============================================================================

# Fungsi untuk menginisialisasi atau mendapatkan sesi chat
@st.cache_resource
def get_chat_session():
    """Menginisialisasi konfigurasi Gemini dan sesi chat."""
    
    # 1. Cek API Key
    if API_KEY == "AIzaSyBteyzW2lqx9HkiwDSTSgln6acWaXP9g-U" or not API_KEY:
        st.error("⚠️ **Peringatan**: API Key Gemini belum diatur. Harap ganti `AIzaSyBteyzW2lqx9HkiwDSTSgln6acWaXP9g-U` dengan API Key Anda yang valid.")
        st.stop()
    
    # 2. Konfigurasi API
    try:
        genai.configure(api_key=API_KEY)
        # st.success("Gemini API Key berhasil dikonfigurasi.")
    except Exception as e:
        st.error(f"❌ **Kesalahan saat mengkonfigurasi API Key**: {e}")
        st.stop()

    # 3. Inisialisasi Model
    try:
        model = genai.GenerativeModel(
            MODEL_NAME,
            generation_config=genai.types.GenerationConfig(
                temperature=0.4,
                max_output_tokens=500
            )
        )
        # st.success(f"Model '{MODEL_NAME}' berhasil diinisialisasi.")
    except Exception as e:
        st.error(f"❌ **Kesalahan saat inisialisasi model** '{MODEL_NAME}': {e}. Pastikan nama model benar dan tersedia.")
        st.stop()

    # 4. Memulai Sesi Chat dengan Konteks Awal
    chat_session = model.start_chat(history=INITIAL_CHATBOT_CONTEXT)
    return chat_session

# Dapatkan sesi chat (hanya dijalankan sekali berkat st.cache_resource)
chat = get_chat_session()

# ==============================================================================
# LOGIKA APLIKASI STREAMLIT
# ==============================================================================

# Inisialisasi riwayat chat di Streamlit's session_state
# Riwayat akan dimulai dari INITIAL_CHATBOT_CONTEXT (role: user, role: model)
if "messages" not in st.session_state:
    st.session_state.messages = []
    
    # Tambahkan INITIAL_CHATBOT_CONTEXT ke riwayat untuk ditampilkan
    # Kita hanya perlu menampilkan balasan model sebagai pesan pertama
    if INITIAL_CHATBOT_CONTEXT:
         # Cek apakah INITIAL_CHATBOT_CONTEXT memiliki pesan balasan model
        model_reply = INITIAL_CHATBOT_CONTEXT[-1]
        if model_reply['role'] == 'model':
            st.session_state.messages.append(model_reply)


# Tampilkan pesan riwayat
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        # Asumsi 'parts' adalah list dengan string tunggal sebagai isi pesan
        st.markdown(message["parts"][0]) 

# Ambil input pengguna
if prompt := st.chat_input("Tanyakan sesuatu tentang basa Jawa..."):
    
    # 1. Tampilkan pesan pengguna di UI
    st.chat_message("user").markdown(prompt)
    
    # 2. Tambahkan pesan pengguna ke riwayat state
    st.session_state.messages.append({"role": "user", "parts": [prompt]})

    # 3. Kirim pesan ke Gemini
    with st.chat_message("model"):
        with st.spinner("Sedang memproses..."):
            try:
                # Kirim input pengguna. Input langsung diambil dari variabel 'prompt'.
                response = chat.send_message(prompt, request_options={"timeout": 60})
                
                # Cek respons
                if response and response.text:
                    st.markdown(response.text)
                    
                    # 4. Tambahkan balasan model ke riwayat state
                    st.session_state.messages.append({"role": "model", "parts": [response.text]})
                else:
                    error_message = "Maaf, saya tidak bisa memberikan balasan. Respons API kosong atau tidak valid."
                    st.error(error_message)
                    st.session_state.messages.append({"role": "model", "parts": [error_message]})

            except Exception as e:
                error_message = f"Maaf, terjadi kesalahan saat berkomunikasi dengan Gemini: \n\nDetail: {e}"
                st.error(error_message)
                st.session_state.messages.append({"role": "model", "parts": [error_message]})

# ==============================================================================
# TOMBOL RESET CHAT
# ==============================================================================

if st.button("Mulai Chat Baru (Reset)"):
    # Clear riwayat state
    st.session_state.messages = []
    
    # Reset sesi chat dengan konteks awal
    st.cache_resource.clear()
    global chat # Memastikan variabel global chat diperbarui
    chat

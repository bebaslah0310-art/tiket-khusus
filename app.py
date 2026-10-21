import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import io
import os
import urllib.request

# Mengatur tampilan halaman
st.set_page_config(page_title="Cetak Tiket A4 Otomatis", layout="wide")

st.title("🎟️ Generator Tiket Khusus A4 (Otomatis)")

# --- AREA UTAMA (MEMBAGI JADI 2 KOLOM) ---
col1, col2 = st.columns([1, 1.5])

with col1:
    st.subheader("📝 1. Edit Data Tiket")
    tanggal = st.text_input("Tanggal Kunjungan", "21 Oktober 2026")
    nama_grup = st.text_input("Nama Grup / Sekolah", "TK Taruna Bakti")
    
    st.info("💡 Sistem otomatis meletakkan teks rata tengah pada area garis tanda di gambar, dengan huruf tebal.")

# --- PROSES PEMBUATAN TIKET & KANVAS A4 ---
# Menggunakan file gambar dengan garis penanda
template_path = "Tiket Khusus Kaumpandak Waterpark (1).png"

try:
    # 1. Load gambar master
    img_master = Image.open(template_path).convert("RGB")
    draw = ImageDraw.Draw(img_master)
    W, H = img_master.size

    # --- SOLUSI FONT TEBAL OTOMATIS ---
    # Mengunduh font Roboto Bold agar tulisan tebal dan jelas
    font_url = "https://github.com/googlefonts/roboto/raw/main/src/hinted/Roboto-Bold.ttf"
    font_path = "Roboto-Bold.ttf"
    
    if not os.path.exists(font_path):
        with st.spinner("Mengunduh font tebal..."):
            urllib.request.urlretrieve(font_url, font_path)
            
    # Ukuran font disesuaikan dengan proporsi garis penanda
    ukuran_font_tanggal = int(H * 0.045)  
    ukuran_font_grup = int(H * 0.08)     

    font_tanggal = ImageFont.truetype(font_path, ukuran_font_tanggal)
    font_grup = ImageFont.truetype(font_path, ukuran_font_grup)

    # --- FUNGSI UNTUK MENULIS TEKS RATA TENGAH (CENTER ALIGNMENT) ---
    def draw_text_centered(draw, text, font, x_center, y_center, color):
        try:
            # Pillow versi baru
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
        except AttributeError:
            # Pillow versi lama
            text_width, text_height = draw.textsize(text, font=font)
        
        # Kalkulasi agar koordinat persis berada di tengah teks
        x = x_center - (text_width / 2)
        y = y_center - (text_height / 2) - int(H * 0.01) # Sedikit penyesuaian visual vertikal
        
        draw.text((x, y), text, font=font, fill=color)

    # --- KOORDINAT BERDASARKAN GARIS TANDA DI GAMBAR ---
    # Titik tengah untuk Tanggal (berada di garis abu-abu kanan atas)
    titik_tengah_x_tanggal = int(W * 0.81)
    titik_tengah_y_tanggal = int(H * 0.165)
    
    # Titik tengah untuk Nama Grup (berada di garis abu-abu bawah tengah)
    titik_tengah_x_grup = int(W * 0.5)
    titik_tengah_y_grup = int(H * 0.885)

    # Terapkan fungsi rata tengah
    draw_text_centered(draw, tanggal, font_tanggal, titik_tengah_x_tanggal, titik_tengah_y_tanggal, "#003366")
    draw_text_centered(draw, nama_grup, font_grup, titik_tengah_x_grup, titik_tengah_y_grup, "#003366")

    # --- MENYUSUN KE KERTAS A4 ---
    # Ukuran standar A4 pada resolusi tinggi (300 DPI)
    a4_width, a4_height = 2480, 3508
    kanvas_a4 = Image.new('RGB', (a4_width, a4_height), 'white')

    # Ukuran tiket disesuaikan agar muat 10 buah (16:9 ratio) dengan jarak potong
    ticket_w, ticket_h = 1120, 630
    tiket_resized = img_master.resize((ticket_w, ticket_h), Image.LANCZOS)

    margin_kiri = 100
    margin_atas = 100
    jarak_potong = 40

    # Menyusun 2 kolom dan 5 baris
    for baris in range(5):
        for kolom in range(2):
            x = margin_kiri + kolom * (ticket_w + jarak_potong)
            y = margin_atas + baris * (ticket_h + jarak_potong)
            kanvas_a4.paste(tiket_resized, (x, y))

    # --- TAMPILKAN PREVIEW & TOMBOL DOWNLOAD ---
    with col2:
        st.subheader("📄 2. Live Preview Kertas A4")
        st.image(kanvas_a4, caption="Preview Kertas A4 (Isi 10 Tiket, siap digunting)", use_column_width=True)

        buf_pdf = io.BytesIO()
        kanvas_a4.save(buf_pdf, format="PDF", resolution=300.0)
        byte_pdf = buf_pdf.getvalue()
        
        st.download_button(
            label="⬇️ Download File PDF (Siap Print)",
            data=byte_pdf,
            file_name=f"Cetak_Tiket_{nama_grup.replace(' ', '_')}.pdf",
            mime="application/pdf",
            use_container_width=True
        )

except FileNotFoundError:
    st.error(f"❌ Error: File gambar '{template_path}' tidak ditemukan. Pastikan nama file gambar di dalam folder sama persis.")

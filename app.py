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
    tanggal = st.text_input("Tanggal Kunjungan", "21 NOVEMBER 2026")
    nama_grup = st.text_input("Nama Grup / Sekolah", "TEST DULU SEBELUM NYOBA CETAK KARENA NAMA INI SANGAT PANJANG")
    
    st.info("💡 Sistem Auto-Scaling kini lebih ketat. Font dijamin tidak akan keluar dari lengkungan area putih.")

# --- PROSES PEMBUATAN TIKET & KANVAS A4 ---
template_path = "Tiket Khusus Kaumpandak Waterpark (1).png"

try:
    # Load gambar master
    img_master = Image.open(template_path).convert("RGB")
    draw = ImageDraw.Draw(img_master)
    W, H = img_master.size

    # Mengunduh font Roboto Bold
    font_url = "https://github.com/googlefonts/roboto/raw/main/src/hinted/Roboto-Bold.ttf"
    font_path = "Roboto-Bold.ttf"
    
    if not os.path.exists(font_path):
        with st.spinner("Mengunduh font tebal..."):
            urllib.request.urlretrieve(font_url, font_path)

    # --- FUNGSI AUTO-SCALING FONT (YANG DISEMPURNAKAN) ---
    def get_optimal_font(text, font_path, max_font_size, max_width, draw):
        """Mengecilkan ukuran font secara otomatis jika teks lebih lebar dari max_width"""
        current_size = max_font_size
        font = ImageFont.truetype(font_path, current_size)
        
        while current_size > 10: # Batas minimal ukuran font agar tidak terlalu tak terlihat
            try:
                bbox = draw.textbbox((0, 0), text, font=font)
                text_width = bbox[2] - bbox[0]
            except AttributeError:
                text_width, _ = draw.textsize(text, font=font)
                
            # Jika lebar teks sudah lebih kecil dari batas toleransi (max_width), berhenti mengecilkan
            if text_width <= max_width:
                break
            
            # Jika belum, kurangi ukuran font secara bertahap
            current_size -= 2
            font = ImageFont.truetype(font_path, current_size)
            
        return font

    # --- PENGATURAN AREA MAKSIMAL YANG LEBIH KETAT (PERBAIKAN) ---
    # Toleransi lebar diperkecil agar aman dari lengkungan pinggir kotak putih
    max_width_tanggal = int(W * 0.18) # Hanya mentoleransi maksimal 18% dari lebar gambar total
    max_width_grup = int(W * 0.42)    # Hanya mentoleransi maksimal 42% dari lebar gambar total (area aman garis abu-abu)

    # Tentukan font optimal
    font_tanggal = get_optimal_font(tanggal, font_path, max_font_size=int(H * 0.045), max_width=max_width_tanggal, draw=draw)
    font_grup = get_optimal_font(nama_grup, font_path, max_font_size=int(H * 0.08), max_width=max_width_grup, draw=draw)

    # --- FUNGSI UNTUK MENULIS TEKS RATA TENGAH ---
    def draw_text_centered(draw, text, font, x_center, y_center, color):
        try:
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
        except AttributeError:
            text_width, text_height = draw.textsize(text, font=font)
        
        x = x_center - (text_width / 2)
        y = y_center - (text_height / 2) - int(H * 0.01)
        draw.text((x, y), text, font=font, fill=color)

    # --- KOORDINAT BERDASARKAN GARIS TANDA DI GAMBAR ---
    titik_tengah_x_tanggal = int(W * 0.81)
    titik_tengah_y_tanggal = int(H * 0.165)
    
    titik_tengah_x_grup = int(W * 0.5)
    titik_tengah_y_grup = int(H * 0.885)

    # Terapkan teks ke gambar
    draw_text_centered(draw, tanggal, font_tanggal, titik_tengah_x_tanggal, titik_tengah_y_tanggal, "#003366")
    draw_text_centered(draw, nama_grup, font_grup, titik_tengah_x_grup, titik_tengah_y_grup, "#003366")

    # --- MENYUSUN KE KERTAS A4 ---
    a4_width, a4_height = 2480, 3508
    kanvas_a4 = Image.new('RGB', (a4_width, a4_height), 'white')

    ticket_w, ticket_h = 1120, 630
    tiket_resized = img_master.resize((ticket_w, ticket_h), Image.LANCZOS)

    margin_kiri = 100
    margin_atas = 100
    jarak_potong = 40

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

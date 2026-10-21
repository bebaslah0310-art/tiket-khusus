import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import io

# Mengatur tampilan halaman menjadi lebar
st.set_page_config(page_title="Cetak Tiket A4 Otomatis", layout="wide")

st.title("🎟️ Generator Tiket Khusus A4 (Otomatis)")
st.write("Masukkan Tanggal dan Nama Grup. Sistem akan otomatis mengatur ukuran, posisi tengah, dan menyusunnya menjadi 10 tiket dalam 1 kertas A4 siap cetak.")

# --- AREA UTAMA (MEMBAGI JADI 2 KOLOM) ---
col1, col2 = st.columns([1, 1.5])

with col1:
    st.subheader("📝 1. Edit Data Tiket")
    tanggal = st.text_input("Tanggal Kunjungan", "25 Oktober 2026")
    nama_grup = st.text_input("Nama Grup / Sekolah", "TK Taruna Bakti")
    
    st.info("💡 Ketik data di atas, dan pratinjau kertas A4 di sebelah kanan akan langsung diperbarui.")

# --- PROSES PEMBUATAN TIKET & KANVAS A4 ---
template_path = "Tiket Khusus Kaumpandak Waterpark 2.jpg"

try:
    # 1. Load gambar master
    img_master = Image.open(template_path).convert("RGB")
    draw = ImageDraw.Draw(img_master)
    W, H = img_master.size

    # --- PENGATURAN OTOMATIS (POSISI & UKURAN FONT) ---
    # Posisi tengah berdasarkan area ceklis di gambar
    titik_tengah_x_tanggal = int(W * 0.815) # Area putih atas kanan
    titik_tengah_y_tanggal = int(H * 0.135)
    
    titik_tengah_x_grup = int(W * 0.5)      # Area putih bawah tengah
    titik_tengah_y_grup = int(H * 0.885)

    # Ukuran font otomatis menyesuaikan resolusi gambar asli
    ukuran_font_tanggal = int(H * 0.045)
    ukuran_font_grup = int(H * 0.08)

    # Load font (Gunakan Arial jika ada, jika tidak pakai default)
    try:
        font_tanggal = ImageFont.truetype("arial.ttf", ukuran_font_tanggal)
        font_grup = ImageFont.truetype("arial.ttf", ukuran_font_grup)
    except IOError:
        font_tanggal = ImageFont.load_default()
        font_grup = ImageFont.load_default()

    # --- FUNGSI UNTUK MENULIS TEKS RATA TENGAH ---
    def draw_text_centered(draw, text, font, x_center, y_center, color):
        try:
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
        except AttributeError:
            text_width, text_height = draw.textsize(text, font=font)
        
        # Kalkulasi agar titik x dan y berada persis di tengah teks
        x = x_center - (text_width / 2)
        y = y_center - (text_height / 2)
        draw.text((x, y), text, font=font, fill=color)

    # Tulis Tanggal dan Nama Grup secara otomatis
    draw_text_centered(draw, tanggal, font_tanggal, titik_tengah_x_tanggal, titik_tengah_y_tanggal, "black")
    draw_text_centered(draw, nama_grup, font_grup, titik_tengah_x_grup, titik_tengah_y_grup, "#003366")

    # --- MENYUSUN KE KERTAS A4 ---
    # Ukuran standar A4 pada 300 DPI
    a4_width, a4_height = 2480, 3508
    kanvas_a4 = Image.new('RGB', (a4_width, a4_height), 'white')

    # Ukuran ideal tiket agar muat 10 buah di A4 dengan sisa ruang potong
    ticket_w, ticket_h = 1120, 630
    tiket_resized = img_master.resize((ticket_w, ticket_h), Image.LANCZOS)

    # Pengaturan Jarak & Margin
    margin_kiri = 100
    margin_atas = 100
    jarak_potong = 40

    # Looping paste 10 tiket (2 kolom x 5 baris)
    for baris in range(5):
        for kolom in range(2):
            x = margin_kiri + kolom * (ticket_w + jarak_potong)
            y = margin_atas + baris * (ticket_h + jarak_potong)
            kanvas_a4.paste(tiket_resized, (x, y))

    # --- TAMPILKAN PREVIEW & TOMBOL DOWNLOAD ---
    with col2:
        st.subheader("📄 2. Live Preview Kertas A4")
        st.image(kanvas_a4, caption="Preview Kertas A4 (Isi 10 Tiket, siap digunting)", use_column_width=True)

        # Siapkan file PDF
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
    st.error(f"❌ Error: File gambar '{template_path}' tidak ditemukan. Pastikan file gambar telah diupload dengan nama yang sesuai.")

import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import io

st.set_page_config(page_title="Cetak Tiket A4", layout="centered")

st.title("🎟️ Generator Tiket A4 (Isi 10)")
st.write("Aplikasi ini akan mencetak 10 tiket ke dalam 1 lembar kertas A4 siap cetak.")

# Input Data
tanggal = st.text_input("Tanggal Kunjungan (Contoh: 25 Oktober 2026)", "")
nama_grup = st.text_input("Nama Grup / Sekolah (Contoh: TK Taruna Bakti)", "")

# Konfigurasi Posisi Teks untuk 1 Tiket
st.sidebar.header("Pengaturan Posisi Teks")
pos_x_tanggal = st.sidebar.slider("Posisi X (Kiri-Kanan) Tanggal", 0, 2000, 1420)
pos_y_tanggal = st.sidebar.slider("Posisi Y (Atas-Bawah) Tanggal", 0, 1000, 120)
pos_y_grup = st.sidebar.slider("Posisi Y (Atas-Bawah) Nama Grup", 0, 1500, 920)
ukuran_font = st.sidebar.slider("Ukuran Font Nama Grup", 20, 150, 70)

if st.button("Buat & Susun di Kertas A4"):
    try:
        # 1. Buat satu tiket (Master)
        template_path = "Tiket Khusus Kaumpandak Waterpark (1).png"
        img = Image.open(template_path).convert("RGB")
        draw = ImageDraw.Draw(img)

        try:
            font_tanggal = ImageFont.truetype("arial.ttf", 45)
            font_grup = ImageFont.truetype("arial.ttf", ukuran_font)
        except IOError:
            font_tanggal = ImageFont.load_default()
            font_grup = ImageFont.load_default()

        # Tulis Tanggal
        draw.text((pos_x_tanggal, pos_y_tanggal), tanggal, font=font_tanggal, fill="black")

        # Tulis Nama Grup (Rata Tengah)
        try:
            text_bbox = draw.textbbox((0, 0), nama_grup, font=font_grup)
            text_width = text_bbox[2] - text_bbox[0]
        except AttributeError:
            text_width, text_height = draw.textsize(nama_grup, font=font_grup)
            
        pos_x_grup = (img.width - text_width) / 2
        draw.text((pos_x_grup, pos_y_grup), nama_grup, font=font_grup, fill="#003366")

        # 2. Susun 10 Tiket ke Kanvas A4
        # Ukuran A4 pada 300 DPI adalah 2480 x 3508 piksel
        a4_width, a4_height = 2480, 3508
        kanvas_a4 = Image.new('RGB', (a4_width, a4_height), 'white')

        # Ukuran tiap tiket (disesuaikan agar proporsional dan muat 10 buah)
        # Menjaga rasio 16:9
        ticket_w = 1120
        ticket_h = 630
        tiket_resized = img.resize((ticket_w, ticket_h), Image.LANCZOS)

        # Pengaturan Layout (Margin Narrow & Jarak Potong)
        margin_kiri_kanan = 100
        margin_atas_bawah = 100
        jarak_x = 40  # Ruang potong vertikal
        jarak_y = 40  # Ruang potong horizontal

        # Proses tempel (Paste) ke kanvas 2 kolom x 5 baris
        for baris in range(5):
            for kolom in range(2):
                x = margin_kiri_kanan + kolom * (ticket_w + jarak_x)
                y = margin_atas_bawah + baris * (ticket_h + jarak_y)
                kanvas_a4.paste(tiket_resized, (x, y))

        st.image(kanvas_a4, caption="Preview Kertas A4 (Isi 10 Tiket)", use_column_width=True)

        # 3. Simpan sebagai PDF (Sangat disarankan untuk akurasi ukuran cetak)
        buf_pdf = io.BytesIO()
        kanvas_a4.save(buf_pdf, format="PDF", resolution=300.0)
        byte_pdf = buf_pdf.getvalue()

        st.success("File A4 berhasil disusun!")
        st.download_button(
            label="📄 Download File Siap Cetak (Format PDF)",
            data=byte_pdf,
            file_name=f"Cetak_A4_{nama_grup.replace(' ', '_')}.pdf",
            mime="application/pdf"
        )

    except FileNotFoundError:
        st.error(f"❌ Error: File gambar '{template_path}' tidak ditemukan.")

import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import io

# Mengatur tampilan halaman menjadi lebih lebar untuk menampung preview berdampingan
st.set_page_config(page_title="Editor & Cetak Tiket A4", layout="wide")

st.title("🎟️ Editor Tiket Khusus & Generator A4")
st.write("Edit teks dan sesuaikan posisi pada panel sebelah kiri. Preview tiket satuan akan muncul di sebelah kanan.")

# --- SIDEBAR UNTUK PENGATURAN POSISI ---
st.sidebar.header("🛠️ Pengaturan Posisi & Ukuran")
st.sidebar.write("Geser untuk memindahkan teks di area putih.")
pos_x_tanggal = st.sidebar.slider("Posisi X (Kiri-Kanan) Tanggal", 0, 2000, 1420)
pos_y_tanggal = st.sidebar.slider("Posisi Y (Atas-Bawah) Tanggal", 0, 1000, 120)

st.sidebar.markdown("---")
pos_y_grup = st.sidebar.slider("Posisi Y (Atas-Bawah) Nama Grup", 0, 1500, 920)
ukuran_font = st.sidebar.slider("Ukuran Font Nama Grup", 20, 150, 70)

# --- AREA UTAMA (MEMBAGI JADI 2 KOLOM) ---
col1, col2 = st.columns([1, 1.2])

with col1:
    st.subheader("1. Masukkan Data Tiket")
    tanggal = st.text_input("Tanggal Kunjungan", "25 Oktober 2026")
    nama_grup = st.text_input("Nama Grup / Sekolah", "TK Taruna Bakti")
    
    st.info("💡 Ketik data di atas, dan lihat perubahannya secara real-time pada gambar di sebelah kanan.")

# --- PROSES PEMBUATAN PREVIEW TIKET SATUAN ---
template_path = "Tiket Khusus Kaumpandak Waterpark (1).png"
try:
    # Load gambar
    img_master = Image.open(template_path).convert("RGB")
    draw = ImageDraw.Draw(img_master)

    # Load font
    try:
        font_tanggal = ImageFont.truetype("arial.ttf", 45)
        font_grup = ImageFont.truetype("arial.ttf", ukuran_font)
    except IOError:
        font_tanggal = ImageFont.load_default()
        font_grup = ImageFont.load_default()

    # Terapkan Teks ke Gambar Master
    # 1. Tanggal
    draw.text((pos_x_tanggal, pos_y_tanggal), tanggal, font=font_tanggal, fill="black")

    # 2. Nama Grup (Otomatis Rata Tengah)
    try:
        text_bbox = draw.textbbox((0, 0), nama_grup, font=font_grup)
        text_width = text_bbox[2] - text_bbox[0]
    except AttributeError:
        text_width, text_height = draw.textsize(nama_grup, font=font_grup)
        
    pos_x_grup = (img_master.width - text_width) / 2
    draw.text((pos_x_grup, pos_y_grup), nama_grup, font=font_grup, fill="#003366")

    with col2:
        st.subheader("2. Live Preview Tiket")
        # Menampilkan gambar yang sudah ditambahkan teks secara real-time
        st.image(img_master, caption="Pratinjau Tiket Anda", use_column_width=True)

    st.markdown("---")
    st.subheader("3. Proses Cetak ke Kertas A4")
    
    # --- TOMBOL GENERATE A4 ---
    if st.button("✨ Susun 10 Tiket ke Kertas A4 & Siapkan File Cetak"):
        with st.spinner("Sedang menyusun tiket ke format A4..."):
            # Ukuran A4 pada 300 DPI adalah 2480 x 3508 piksel
            a4_width, a4_height = 2480, 3508
            kanvas_a4 = Image.new('RGB', (a4_width, a4_height), 'white')

            # Resize tiket master (Rasio proporsional)
            ticket_w = 1120
            ticket_h = 630
            tiket_resized = img_master.resize((ticket_w, ticket_h), Image.LANCZOS)

            # Pengaturan Jarak & Margin
            margin_kiri_kanan = 100
            margin_atas_bawah = 100
            jarak_x = 40  # Jarak potong gunting vertikal
            jarak_y = 40  # Jarak potong gunting horizontal

            # Looping untuk menempelkan 10 tiket (2 kolom x 5 baris)
            for baris in range(5):
                for kolom in range(2):
                    x = margin_kiri_kanan + kolom * (ticket_w + jarak_x)
                    y = margin_atas_bawah + baris * (ticket_h + jarak_y)
                    kanvas_a4.paste(tiket_resized, (x, y))

            # Simpan hasil ke dalam memory sebagai PDF
            buf_pdf = io.BytesIO()
            kanvas_a4.save(buf_pdf, format="PDF", resolution=300.0)
            byte_pdf = buf_pdf.getvalue()

            st.success("✅ File A4 berhasil disusun! Silakan klik tombol di bawah untuk mengunduh.")
            
            # Tombol Download PDF
            st.download_button(
                label="📄 Download File PDF (Siap Print)",
                data=byte_pdf,
                file_name=f"Cetak_A4_10Tiket_{nama_grup.replace(' ', '_')}.pdf",
                mime="application/pdf"
            )
            
            # Menampilkan preview lembar A4 secara keseluruhan di bawah tombol download
            st.image(kanvas_a4, caption="Preview Hasil Akhir Kertas A4 (Ruang putih di antara tiket adalah area gunting)", use_column_width=True)

except FileNotFoundError:
    st.error("❌ Error: File gambar template tidak ditemukan. Pastikan file 'Tiket Khusus Kaumpandak Waterpark (1).png' berada di folder yang sama.")

import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import io
import os

st.set_page_config(page_title="Cetak Tiket A4 Otomatis", layout="wide")

st.title("🎟️ Generator Tiket Khusus A4 (Otomatis)")

col1, col2 = st.columns([1, 1.5])

with col1:
    st.subheader("🖼️ 1. Pilih Template")
    jenis_template = st.radio(
        "Sesuaikan dengan panjang nama grup/sekolah:",
        ["Template Nama Panjang (Gambar 1)", "Template Nama Pendek (Gambar 2)"]
    )

    st.subheader("📝 2. Edit Data Tiket")
    with st.form("form_edit_tiket"):
        tanggal = st.text_input("Tanggal Kunjungan", "21 NOVEMBER 2026")
        nama_grup = st.text_input("Nama Grup / Sekolah", "TEST DULU SEBELUM NYOBA CETAK")
        
        tombol_cek = st.form_submit_button("✅ Cek / Tampilkan")
    
    st.info("💡 Klik Cek / Tampilkan Lalu Download File PDF Nya.")

if "Panjang" in jenis_template:
    template_path = "Tiket Ceria Kaumpandak Waterpark.png"
    batas_lebar_grup_persen = 0.80 
    y_grup_persen = 0.875           
else:
    template_path = "Tiket Khusus Kaumpandak Waterpark (1).png"
    batas_lebar_grup_persen = 0.40 
    y_grup_persen = 0.875           

try:
    img_master = Image.open(template_path).convert("RGB")
    draw = ImageDraw.Draw(img_master)
    W, H = img_master.size

    # --- PENGATURAN FONT CALIBRI BOLD ---
    font_path = "calibrib.ttf"
    
    if not os.path.exists(font_path):
        st.warning("⚠️ Peringatan: File font 'calibrib.ttf' tidak ditemukan di folder. Silakan upload file tersebut agar font Calibri Bold bisa diterapkan.")

    def get_optimal_font(text, font_path, max_font_size, max_width, draw):
        current_size = max_font_size
        try:
            font = ImageFont.truetype(font_path, current_size)
            
            while current_size > 10: 
                try:
                    bbox = draw.textbbox((0, 0), text, font=font)
                    text_width = bbox[2] - bbox[0]
                except AttributeError:
                    text_width, _ = draw.textsize(text, font=font)
                    
                if text_width <= max_width:
                    break
                
                current_size -= 2
                font = ImageFont.truetype(font_path, current_size)
                
            return font
        except OSError:
            return ImageFont.load_default()

    max_width_tanggal = int(W * 0.18) 
    max_width_grup = int(W * batas_lebar_grup_persen)    

    font_tanggal = get_optimal_font(tanggal, font_path, max_font_size=int(H * 0.045), max_width=max_width_tanggal, draw=draw)
    font_grup = get_optimal_font(nama_grup, font_path, max_font_size=int(H * 0.08), max_width=max_width_grup, draw=draw)

    def draw_text_centered(draw, text, font, x_center, y_center, color):
        try:
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            offset_x = bbox[0] 
            offset_y = bbox[1]
        except AttributeError:
            text_width, text_height = draw.textsize(text, font=font)
            offset_x, offset_y = 0, 0
        
        x = x_center - (text_width / 2) - offset_x
        y = y_center - (text_height / 2) - offset_y
        draw.text((x, y), text, font=font, fill=color)

    titik_tengah_x_tanggal = int(W * 0.81)
    titik_tengah_y_tanggal = int(H * 0.175)
    
    titik_tengah_x_grup = int(W * 0.51) 
    titik_tengah_y_grup = int(H * y_grup_persen) 

    draw_text_centered(draw, tanggal, font_tanggal, titik_tengah_x_tanggal, titik_tengah_y_tanggal, "#003366")
    draw_text_centered(draw, nama_grup, font_grup, titik_tengah_x_grup, titik_tengah_y_grup, "#003366")

    # --- PENYESUAIAN MARGIN 0.5 & CENTER ON PAGE ---
    a4_width, a4_height = 2480, 3508
    kanvas_a4 = Image.new('RGB', (a4_width, a4_height), 'white')

    ticket_w, ticket_h = 1160, 652 
    tiket_resized = img_master.resize((ticket_w, ticket_h), Image.LANCZOS)

    jarak_potong = 40

    total_lebar_grid = (ticket_w * 2) + jarak_potong
    total_tinggi_grid = (ticket_h * 5) + (jarak_potong * 4)

    margin_kiri = (a4_width - total_lebar_grid) // 2
    margin_atas = (a4_height - total_tinggi_grid) // 2

    for baris in range(5):
        for kolom in range(2):
            x = margin_kiri + kolom * (ticket_w + jarak_potong)
            y = margin_atas + baris * (ticket_h + jarak_potong)
            kanvas_a4.paste(tiket_resized, (x, y))

    with col2:
        st.subheader("📄 3. Live Preview Kertas A4")
        # PERBAIKAN: Mengganti use_column_width menjadi use_container_width
        st.image(kanvas_a4, caption="Preview Kertas A4 (Isi 10 Tiket, siap digunting)", use_container_width=True)

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
    st.error(f"❌ Error: File gambar '{template_path}' tidak ditemukan. Pastikan nama file tersebut ada di folder yang sama.")

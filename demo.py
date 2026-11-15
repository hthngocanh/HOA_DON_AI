import json
import streamlit as st
from PIL import Image
import pytesseract
from src.improved import extract_improved

st.set_page_config(
    page_title="Trích xuất thông tin hóa đơn - SROIE",
    page_icon="🧾",
    layout="wide"
)

st.title("🧾 Hệ thống Trích xuất Thông tin Hóa đơn Bán lẻ")
st.caption("Đồ án: Chủ đề 05 – Dataset ICDAR2019-SROIE | OCR: Tesseract | Trích xuất: Improved Rule-based")

uploaded_file = st.file_uploader(
    "Tải lên ảnh hóa đơn (JPG, JPEG, PNG)",
    type=["jpg", "jpeg", "png"]
)

if uploaded_file is not None:
    image = Image.open(uploaded_file)

    col1, col2 = st.columns([1, 1.2])

    with col1:
        st.subheader("1. Ảnh hóa đơn gốc")
        st.image(image, use_container_width=True)

    with col2:
        st.subheader("2. Kết quả nhận diện & Trích xuất")
        with st.spinner("Đang tiền xử lý ảnh và chạy Tesseract OCR..."):
            # Tiền xử lý giống hệt Notebook 02: Grayscale + Resize 2x
            gray_img = image.convert("L")
            w, h = gray_img.size
            resized_img = gray_img.resize((w * 2, h * 2), Image.Resampling.LANCZOS)

            # Chạy Tesseract OCR
            ocr_text = pytesseract.image_to_string(resized_img)

            # Trích xuất 4 trường thông tin từ module Improved
            extracted_data = extract_improved(ocr_text)

            # Đảm bảo đủ 4 trường và giá trị rỗng thành None (null trong JSON)
            final_json = {
                "company": extracted_data.get("company") or None,
                "date": extracted_data.get("date") or None,
                "address": extracted_data.get("address") or None,
                "total": extracted_data.get("total") or None,
            }

        st.markdown("**Kết quả trích xuất (JSON):**")
        st.json(final_json)

        json_str = json.dumps(final_json, ensure_ascii=False, indent=2)
        file_stem = uploaded_file.name.rsplit(".", 1)[0]
        st.download_button(
            label="📥 Tải kết quả JSON",
            data=json_str,
            file_name=f"{file_stem}_result.json",
            mime="application/json"
        )

        with st.expander("Xem văn bản OCR thô (Tesseract output)", expanded=False):
            st.text(ocr_text if ocr_text.strip() else "(Không nhận diện được văn bản)")
else:
    st.info("👆 Vui lòng tải lên một ảnh hóa đơn để bắt đầu trích xuất thông tin.")
import json
from pathlib import Path
from PIL import Image
import pytesseract
import streamlit as st
import pandas as pd

from src.baseline import extract_fields as extract_baseline
from src.improved import extract_improved

st.set_page_config(
    page_title="Hệ thống trích xuất thông tin hóa đơn bán lẻ",
    layout="wide"
)

# Giao diện đơn giản, tối giản, không icon/emoji
st.markdown("""
<style>
    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
        max-width: 1200px;
    }
    .field-card {
        border: 1px solid #E2E8F0;
        border-radius: 6px;
        padding: 10px 14px;
        margin-bottom: 10px;
        background-color: #F8FAFC;
    }
    .field-label {
        font-size: 0.75rem;
        font-weight: 600;
        color: #475569;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .field-value {
        font-size: 0.95rem;
        font-weight: 600;
        color: #0F172A;
        margin-top: 4px;
        word-break: break-word;
    }
    .field-value.empty {
        color: #94A3B8;
        font-weight: 400;
        font-style: italic;
    }
</style>
""", unsafe_allow_html=True)

st.title("Trích xuất thông tin từ ảnh hóa đơn bán lẻ")
st.caption("Đề tài: Tự động nhận diện và trích xuất thông tin (KIE) trên bộ dữ liệu ICDAR 2019 SROIE")

# Khởi tạo trạng thái trong session_state
if "use_sample" not in st.session_state:
    st.session_state["use_sample"] = False
if "results" not in st.session_state:
    st.session_state["results"] = None

SAMPLE_PATH = Path("data/ICDAR2019-SROIE/assets/ex.jpg")

# ==============================================================================
# KHU VỰC ĐIỀU KHIỂN ĐẦU VÀO
# ==============================================================================
ctrl_col1, ctrl_col2, ctrl_col3 = st.columns([1.5, 1, 1.2], gap="medium")

with ctrl_col1:
    uploaded_file = st.file_uploader(
        "Tải ảnh hóa đơn từ máy tính:",
        type=["jpg", "jpeg", "png"],
        help="Hỗ trợ các định dạng JPG, JPEG, PNG."
    )
    if uploaded_file is not None:
        st.session_state["use_sample"] = False

with ctrl_col2:
    st.write("Ảnh mẫu có sẵn:")
    if SAMPLE_PATH.exists():
        if st.button("Sử dụng ảnh mẫu", use_container_width=True):
            st.session_state["use_sample"] = True
    else:
        st.caption("Không tìm thấy tệp ảnh mẫu ex.jpg.")

with ctrl_col3:
    method = st.radio(
        "Chọn phương pháp:",
        options=["Improved", "Baseline", "So sánh"],
        horizontal=True,
        help="Improved: Mô hình cải tiến 8 cờ. Baseline: Mô hình cơ sở. So sánh: Đối chiếu kết quả giữa hai mô hình."
    )

# Xác định ảnh được chọn
active_image = None
active_filename = ""

if uploaded_file is not None and not st.session_state["use_sample"]:
    try:
        active_image = Image.open(uploaded_file)
        active_filename = uploaded_file.name
    except Exception:
        st.error("Tệp tải lên không phải là ảnh hợp lệ hoặc đã bị lỗi.")
elif st.session_state["use_sample"]:
    if SAMPLE_PATH.exists():
        try:
            active_image = Image.open(SAMPLE_PATH)
            active_filename = "ex.jpg"
        except Exception:
            st.error("Không thể mở tệp ảnh mẫu.")
    else:
        st.error("Tệp ảnh mẫu ex.jpg không tồn tại.")

# Nút thực hiện trích xuất
st.markdown("<div style='margin-top: 8px;'></div>", unsafe_allow_html=True)
if st.button("Thực hiện trích xuất", type="primary", use_container_width=True):
    if active_image is None:
        st.warning("Vui lòng tải ảnh lên hoặc chọn ảnh mẫu trước khi thực hiện trích xuất.")
    else:
        with st.spinner("Đang xử lý ảnh và trích xuất thông tin..."):
            try:
                # Tiền xử lý theo chuẩn thực nghiệm: Chuyển xám + Phóng to 2x (Lanczos)
                gray_img = active_image.convert("L")
                w, h = gray_img.size
                resized_img = gray_img.resize((w * 2, h * 2), Image.Resampling.LANCZOS)

                # Nhận dạng văn bản qua Tesseract OCR
                ocr_text = pytesseract.image_to_string(resized_img, lang="eng", config="--oem 3 --psm 6")

                # Trích xuất dữ liệu qua 2 mô hình
                res_baseline = extract_baseline(ocr_text)
                res_improved = extract_improved(ocr_text)

                def clean_dict(d):
                    return {
                        "company": d.get("company") or None,
                        "date": d.get("date") or None,
                        "address": d.get("address") or None,
                        "total": d.get("total") or None,
                    }

                st.session_state["results"] = {
                    "baseline": clean_dict(res_baseline),
                    "improved": clean_dict(res_improved),
                    "filename": active_filename,
                    "ocr_text": ocr_text
                }
            except Exception as e:
                st.error(f"Đã xảy ra lỗi trong quá trình xử lý ảnh hoặc nhận dạng OCR: {e}")

st.markdown("---")

# ==============================================================================
# KHU VỰC HIỂN THỊ ẢNH ĐẦU VÀO VÀ KẾT QUẢ
# ==============================================================================
col_img, col_res = st.columns([1, 1.2], gap="large")

with col_img:
    st.subheader("Ảnh hóa đơn đầu vào")
    if active_image is not None:
        st.image(active_image, caption=f"Tệp đang xử lý: {active_filename}", use_container_width=True)
    else:
        st.info("Chưa có ảnh nào được chọn. Vui lòng tải ảnh lên hoặc nhấn 'Sử dụng ảnh mẫu'.")

with col_res:
    st.subheader("Kết quả trích xuất")
    results = st.session_state.get("results")

    if results is None:
        st.info("Chọn phương pháp và nhấn 'Thực hiện trích xuất' để xem kết quả.")
    else:
        if not results.get("ocr_text", "").strip():
            st.warning("Không nhận diện được nội dung văn bản từ ảnh. Vui lòng kiểm tra độ nét và góc chụp của hóa đơn.")

        def render_field(label, value):
            has_val = value is not None and str(value).strip() != ""
            val_text = str(value) if has_val else "(Không tìm thấy)"
            val_class = "field-value" if has_val else "field-value empty"
            st.markdown(f"""
            <div class="field-card">
                <div class="field-label">{label}</div>
                <div class="{val_class}">{val_text}</div>
            </div>
            """, unsafe_allow_html=True)

        json_output = None

        if method == "Improved":
            st.caption("Phương pháp: Mô hình cải tiến (Improved - 8 cờ)")
            data = results["improved"]
            render_field("Company (Tên công ty / Cửa hàng)", data["company"])
            render_field("Date (Ngày lập hóa đơn)", data["date"])
            render_field("Address (Địa chỉ)", data["address"])
            render_field("Total (Tổng tiền)", data["total"])
            json_output = data

        elif method == "Baseline":
            st.caption("Phương pháp: Mô hình cơ sở (Baseline)")
            data = results["baseline"]
            render_field("Company (Tên công ty / Cửa hàng)", data["company"])
            render_field("Date (Ngày lập hóa đơn)", data["date"])
            render_field("Address (Địa chỉ)", data["address"])
            render_field("Total (Tổng tiền)", data["total"])
            json_output = data

        elif method == "So sánh":
            st.caption("Phương pháp: So sánh song song (Baseline vs Improved)")
            comp_data = {
                "Trường thông tin": [
                    "Company (Tên công ty / Cửa hàng)",
                    "Date (Ngày lập hóa đơn)",
                    "Address (Địa chỉ)",
                    "Total (Tổng tiền)"
                ],
                "Baseline": [
                    results["baseline"]["company"] or "(Không tìm thấy)",
                    results["baseline"]["date"] or "(Không tìm thấy)",
                    results["baseline"]["address"] or "(Không tìm thấy)",
                    results["baseline"]["total"] or "(Không tìm thấy)"
                ],
                "Improved": [
                    results["improved"]["company"] or "(Không tìm thấy)",
                    results["improved"]["date"] or "(Không tìm thấy)",
                    results["improved"]["address"] or "(Không tìm thấy)",
                    results["improved"]["total"] or "(Không tìm thấy)"
                ]
            }
            st.dataframe(pd.DataFrame(comp_data), use_container_width=True, hide_index=True)
            json_output = {
                "baseline": results["baseline"],
                "improved": results["improved"]
            }

        # Xem và tải kết quả JSON
        if json_output is not None:
            st.markdown("<div style='margin-top: 14px;'></div>", unsafe_allow_html=True)
            with st.expander("Xem dữ liệu JSON chi tiết", expanded=False):
                st.json(json_output)

            stem = results["filename"].rsplit(".", 1)[0] if results["filename"] else "invoice"
            json_str = json.dumps(json_output, ensure_ascii=False, indent=2)
            st.download_button(
                label="Tải kết quả JSON",
                data=json_str,
                file_name=f"{stem}_{method.lower()}.json",
                mime="application/json",
                use_container_width=True
            )

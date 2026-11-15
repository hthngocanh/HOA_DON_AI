# Bàn giao người 4 -> người 5
Cấu hình đóng băng (chọn trên train): `outputs/improved/frozen_config.json`. Không chỉnh sau khi xem Validation/Test.
Kết quả: `improved_train.csv`, `improved_validation.csv`, `validation_and_train_comparison.csv`, `f1_company_address.csv`, `improvement_explanations.csv`, `ablation_tung_co.csv`.
## Cách dùng (người 5)
```python
from src.improved import ocr_frozen, extract_improved, norm_date, norm_total, norm_text, exact
text = ocr_frozen(pil_image)             # (nếu cần OCR từ ảnh) dùng đúng bước tiền xử lý đã đóng băng
pred = extract_improved(text)            # dict company/date/address/total (giá trị GỐC; không tìm thấy = None)
ok = exact(pred["total"], gold_total, "total")   # so khớp sau chuẩn hóa
```
Cấu hình đọc từ `outputs/improved/frozen_config.json`. Chạy trên Test đúng một lần, không chỉnh luật sau đó.
Nguồn OCR: original (gray+resize2x). Ghi chú: nếu mục 5 còn tắt (RUN_PREPROC=False) thì chưa thử tiền xử lý ảnh.

## Kết luận (Validation, n=125)
Cải tiến tốt hơn baseline trên Validation: Macro EM 0.468 -> 0.554 (+0.086); sửa đúng 43, làm hỏng 0 lượt trường/ảnh.

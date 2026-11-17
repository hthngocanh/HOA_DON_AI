# HỆ THỐNG TRÍCH XUẤT THÔNG TIN TỪ ẢNH HÓA ĐƠN BÁN LẺ (ICDAR2019-SROIE)
### TÀI LIỆU HƯỚNG DẪN TÁI LẬP NGHIÊN CỨU (REPRODUCIBILITY GUIDE)

Môn học: Nhập môn Trí tuệ Nhân tạo  
Chủ đề 05: Trích xuất thông tin tự động từ ảnh hóa đơn bán lẻ (Key Information Extraction - KIE)  
Bộ dữ liệu chuẩn: ICDAR 2019 - SROIE (Scanned Receipts OCR and Information Extraction)  
Nhóm thực hiện: Nhóm 02  

---

## MỤC LỤC
1. [Giới thiệu đề tài và mục tiêu](#1-giới-thiệu-đề-tài-và-mục-tiêu)
2. [Nguồn dataset, cách tải và cấu trúc dữ liệu](#2-nguồn-dataset-cách-tải-và-cấu-trúc-dữ-liệu)
3. [Công nghệ, thư viện và phiên bản thực tế](#3-công-nghệ-thư-viện-và-phiên-bản-thực-tế)
4. [Cấu trúc thư mục và vai trò các file](#4-cấu-trúc-thư-mục-và-vai-trò-các-file)
5. [Hướng dẫn cài đặt môi trường](#5-hướng-dẫn-cài-đặt-môi-trường)
6. [Quy trình tái lập nghiên cứu theo thứ tự thực thi](#6-quy-trình-tái-lập-nghiên-cứu-theo-thứ-tự-thực-thi)
7. [Phương pháp đánh giá và kết quả thực nghiệm](#7-phương-pháp-đánh-giá-và-kết-quả-thực-nghiệm)
8. [Hướng dẫn khởi chạy Giao diện Demo](#8-hướng-dẫn-khởi-chạy-giao-diện-demo)
9. [Các lỗi thường gặp và cách khắc phục](#9-các-lỗi-thường-gặp-và-cách-khắc-phục)
10. [Tài liệu tham khảo](#10-tài-liệu-tham-khảo)

---

## 1. Giới thiệu đề tài và mục tiêu

Dự án tập trung giải quyết bài toán bóc tách dữ liệu có cấu trúc từ tài liệu ảnh (Key Information Extraction - KIE) trên hóa đơn bán lẻ tiếng Anh tại Malaysia, sử dụng bộ dữ liệu chuẩn ICDAR 2019 SROIE.

### Mục tiêu nghiên cứu:
1. Xây dựng đường ống xử lý hai giai đoạn: Tiền xử lý ảnh kết hợp nhận dạng quang học Tesseract OCR, sau đó trích xuất thông tin bằng hệ thống luật heuristic (Rule-based).
2. Trích xuất chính xác 4 trường thực thể mục tiêu:
   - `company`: Tên doanh nghiệp/cửa hàng phát hành hóa đơn.
   - `date`: Ngày lập hóa đơn.
   - `address`: Địa chỉ cơ sở bán hàng.
   - `total`: Tổng số tiền thanh toán cuối cùng.
3. Xây dựng giải pháp cơ sở (Baseline) sử dụng biểu thức chính quy (Regex) và phân tích vị trí dòng văn bản.
4. Phát triển giải pháp cải tiến (Improved) thông qua phương pháp thực nghiệm triệt tiêu từng cờ (Ablation Study) trên tập Train (501 hóa đơn), đóng băng cấu hình quy tắc và kiểm chứng trên tập Validation (125 hóa đơn).
5. Đánh giá kiểm thử khách quan, độc lập trên 361 hóa đơn tập Test chuẩn SROIE theo nguyên tắc không rò rỉ dữ liệu (No Data Leakage).
6. Triển khai ứng dụng Web tương tác (Demo Dashboard) phục vụ nghiệm thu và thử nghiệm thực tế.

---

## 2. Nguồn dataset, cách tải và cấu trúc dữ liệu

### 2.1. Nguồn dữ liệu
- Bộ dữ liệu gốc: Cuộc thi ICDAR 2019 Robust Reading Challenge on Scanned Receipts OCR and Information Extraction (SROIE), tổ chức tại hội thảo ICDAR 2019.
- Bản phân phối sử dụng: Bản chuẩn hóa mở rộng do jsdnrs phát hành trên Hugging Face (`jsdnrs/ICDAR2019-SROIE`), cấp phép theo Creative Commons Attribution 4.0 International (CC-BY-4.0). Phiên bản này đã tích hợp sẵn định dạng Apache Parquet và bổ sung 14 nhãn bị khuyết trong tập Test gốc của Task 3.

### 2.2. Vị trí dữ liệu trong dự án và cách tải
Toàn bộ dữ liệu của đề tài được đặt trong thư mục `data/ICDAR2019-SROIE/data/`:
- `train-00000-of-00001.parquet`: Chứa 626 hóa đơn gốc cho huấn luyện và kiểm chứng (kích thước khoảng 318.6 MB).
- `test-00000-of-00001.parquet`: Chứa 361 hóa đơn kiểm thử độc lập (kích thước khoảng 191.0 MB).
- Tổng số mẫu toàn bộ tập dữ liệu: 987 hóa đơn.

Nếu cần tải lại dữ liệu từ nguồn Hugging Face:
- Phương pháp 1 (Python `datasets`):
  ```python
  from datasets import load_dataset
  dataset = load_dataset("jsdnrs/ICDAR2019-SROIE", split="all")
  ```
- Phương pháp 2 (Tải thủ công): Truy cập đường dẫn `https://huggingface.co/datasets/jsdnrs/ICDAR2019-SROIE` và tải 2 tệp `.parquet` về đặt vào đúng thư mục `data/ICDAR2019-SROIE/data/`.

### 2.3. Cấu trúc trường dữ liệu trong Parquet
Mỗi bản ghi hóa đơn trong tệp Parquet bao gồm các trường:
- `image`: Dữ liệu ảnh hóa đơn ở định dạng PIL Image/Binary PNG/JPEG.
- `key`: Chuỗi định danh duy nhất của hóa đơn (ví dụ: `X51005200931`).
- `image_size`: Kích thước ảnh gốc (`width`, `height`).
- `words`: Mảng danh sách các từ văn bản nhận diện được.
- `bboxes`: Mảng danh sách tọa độ bounding box tương ứng `[x1, y1, x2, y2]`.
- `entities`: Cấu trúc nhãn chuẩn (Ground Truth) gồm 4 trường chuỗi:
  - `company`: Tên cửa hàng hoặc doanh nghiệp (ví dụ: `BOOK TA .K (TAMAN DAYA) SDN BHD`).
  - `date`: Ngày phát hành hóa đơn (ví dụ: `25/12/2018`).
  - `address`: Địa chỉ nơi bán hàng (ví dụ: `NO.53 55,57 & 59, JALAN SAGU 18...`).
  - `total`: Số tiền thanh toán (ví dụ: `9.00`).

---

## 3. Công nghệ, thư viện và phiên bản thực tế

Hệ thống được xây dựng và xác thực trên môi trường Python 3.11. Các thư viện và phiên bản cụ thể quy định tại `requirements.txt` và `Dockerfile`:

| Tên công nghệ / Thư viện | Phiên bản thực tế | Vai trò trong hệ thống |
| :--- | :--- | :--- |
| Python | 3.11.x | Ngôn ngữ thực thi chính |
| Tesseract OCR | 5.x | Engine nhận dạng ký tự quang học nguồn mở |
| pytesseract | 0.3.13 | Thư viện wrapper giao tiếp với Tesseract OCR |
| opencv-python-headless | 4.11.0.86 | Tiền xử lý ảnh, biến đổi không gian màu, nội suy ảnh |
| Pillow (PIL) | 11.1.0 | Thao tác mở, giải nén và chuyển đổi đối tượng ảnh |
| numpy | 2.2.3 | Xử lý mảng ma trận số, tính toán tọa độ và bộ sinh số ngẫu nhiên |
| pandas | 2.2.3 | Xử lý bảng dữ liệu, nhãn Ground Truth, tính chỉ số thống kê |
| pyarrow | 14.0.0+ | Đọc định dạng tệp nén Apache Parquet |
| matplotlib | 3.10.1 | Trực quan hóa dữ liệu và biểu đồ phân tích lỗi |
| jupyterlab | 4.3.5 | Môi trường tương tác thực nghiệm khoa học |
| streamlit | >=1.40.0 | Khung phát triển ứng dụng giao diện web demo tương tác |
| Docker & Docker Compose | 24.x+ | Đóng gói môi trường đồng nhất và chạy đa dịch vụ |

---

## 4. Cấu trúc thư mục và vai trò các file

```text
HOA_DON_AI/
├── 01_khao_sat.ipynb          # Notebook 01: Khảo sát dữ liệu, phân chia Train/Val/Test (Seed 42)
├── 02_ocr.ipynb               # Notebook 02: Nghiên cứu tiền xử lý ảnh và chạy OCR cho tập Train/Val
├── 03_baseline.ipynb          # Notebook 03: Triển khai Baseline, đánh giá tập Val và phân loại lỗi
├── 04_cai_tien.ipynb          # Notebook 04: Ablation study 11 cờ, chọn 8 cờ và đóng băng cấu hình
├── 05_danh_gia_test.ipynb     # Notebook 05: Đánh giá độc lập mô hình Baseline và Improved trên Test
├── demo.py                    # Ứng dụng web Streamlit demo tương tác người dùng
├── splits.csv                 # Tệp chỉ mục phân chia 987 mẫu: Train (501), Val (125), Test (361)
├── requirements.txt           # Danh sách các gói phụ thuộc Python
├── Dockerfile                 # Dockerfile cài sẵn Debian, Tesseract 5 và Python 3.11
├── compose.yaml               # Thiết lập Docker Compose cho JupyterLab (8888) và Demo (8501)
├── src/                       # Thư mục mã nguồn logic tái sử dụng
│   ├── __init__.py            # Khởi tạo package Python
│   ├── baseline.py            # Thuật toán trích xuất Baseline cơ sở
│   ├── improved.py            # Thuật toán trích xuất Improved (commit 733916b)
│   └── utils.py               # Các hàm tiện ích bổ trợ
├── data/                      # Thư mục dữ liệu
│   └── ICDAR2019-SROIE/
│       ├── assets/ex.jpg      # Ảnh hóa đơn mẫu phục vụ thử nghiệm giao diện
│       └── data/
│           ├── train-00000-of-00001.parquet  # Dữ liệu Train/Val gốc (626 hóa đơn)
│           └── test-00000-of-00001.parquet   # Dữ liệu Test gốc (361 hóa đơn)
└── outputs/                   # Thư mục chứa kết quả sinh ra trong quá trình thực nghiệm
    ├── ground_truth/          # Nhãn chuẩn CSV theo từng tập (train, validation, test)
    ├── ocr/                   # Dữ liệu văn bản OCR (train_validation_ocr.csv, test_ocr.csv)
    ├── baseline/              # Kết quả dự đoán và đánh giá của mô hình Baseline
    ├── improved/              # Cấu hình đóng băng frozen_config.json và kết quả tập cải tiến
    └── test/                  # Kết quả kiểm thử và báo cáo đối chiếu trên 361 mẫu Test
```

---

## 5. Hướng dẫn cài đặt môi trường

### Cách 1: Sử dụng Docker Compose (Khuyến nghị cho tính tái lập cao nhất)
Yêu cầu: Máy đã cài đặt Docker và Docker Compose.

1. Di chuyển vào thư mục dự án:
   ```bash
   cd HOA_DON_AI
   ```
2. Khởi động môi trường container:
   ```bash
   docker compose up --build
   ```
3. Truy cập các dịch vụ:
   - JupyterLab: Mở trình duyệt tại `http://localhost:8888` (không yêu cầu mật khẩu token).
   - Demo Streamlit: Mở trình duyệt tại `http://localhost:8501`.

### Cách 2: Cài đặt trên máy cục bộ (Local Environment)

1. Cài đặt Tesseract OCR Engine trên hệ điều hành:
   - Ubuntu / Debian Linux:
     ```bash
     sudo apt-get update
     sudo apt-get install -y tesseract-ocr tesseract-ocr-eng
     ```
   - macOS (Homebrew):
     ```bash
     brew install tesseract
     ```
   - Windows: Tải và cài đặt bản Tesseract 5 từ UB-Mannheim, sau đó thêm đường dẫn `C:\Program Files\Tesseract-OCR` vào biến môi trường `PATH`.

2. Thiết lập môi trường ảo Python 3.11:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate    # Trên Windows: .venv\Scripts\activate
   pip install --upgrade pip
   pip install -r requirements.txt
   pip install pyarrow
   ```

3. Kiểm tra môi trường:
   ```bash
   tesseract --version
   python3 -c "import pytesseract, cv2, PIL, pandas, pyarrow, streamlit; print('Cài đặt thành công!')"
   ```

---

## 6. Quy trình tái lập nghiên cứu theo thứ tự thực thi

Quy trình nghiên cứu gồm 5 bước tuần tự tương ứng với 5 Notebook. Mỗi bước có đầu vào và đầu ra xác định, đảm bảo không rò rỉ thông tin từ tập Test vào quá trình phát triển luật:

```
01_khao_sat.ipynb -> 02_ocr.ipynb -> 03_baseline.ipynb -> 04_cai_tien.ipynb -> 05_danh_gia_test.ipynb
```

### Bảng tóm tắt luồng thực nghiệm:

| Bước | Tệp thực thi | Đầu vào | Công việc chính | Đầu ra được tạo |
| :--- | :--- | :--- | :--- | :--- |
| 1 | `01_khao_sat.ipynb` | `data/ICDAR2019-SROIE/data/*.parquet` | Khảo sát phân bố 4 trường. Phân chia 626 ảnh Train thành Train (501 ảnh, 80%) và Validation (125 ảnh, 20%) với `RANDOM_SEED = 42`. Giữ nguyên 361 ảnh Test. | `splits.csv`<br>`outputs/ground_truth/train_ground_truth.csv`<br>`outputs/ground_truth/validation_ground_truth.csv` |
| 2 | `02_ocr.ipynb` | `train-00000-of-00001.parquet`<br>`splits.csv` | Khảo sát các kỹ thuật tiền xử lý ảnh (Resize 2x Cubic + Grayscale). Chạy nhận dạng Tesseract OCR hàng loạt cho 626 ảnh Train và Validation. | `outputs/ocr/train_validation_ocr.csv` |
| 3 | `03_baseline.ipynb` | `train_validation_ocr.csv`<br>`validation_ground_truth.csv`<br>`src/baseline.py` | Áp dụng quy tắc cơ sở (Regex, vị trí dòng) để bóc tách 4 trường trên 125 ảnh Validation. Đo chỉ số Exact Match và phân loại nguyên nhân lỗi. | `outputs/baseline/baseline_validation.csv` |
| 4 | `04_cai_tien.ipynb` | `train_validation_ocr.csv`<br>`train_ground_truth.csv`<br>`src/improved.py` | Thực nghiệm triệt tiêu (Ablation Study) 11 cờ trên 501 ảnh Train. Chọn các cờ có mức tăng EM >= 0.5% (`MIN_GAIN = 0.005`). Đóng băng cấu hình vào JSON và kiểm chứng trên Validation. | `outputs/improved/frozen_config.json`<br>`outputs/improved/improved_train.csv`<br>`outputs/improved/improved_validation.csv`<br>`outputs/improved/validation_and_train_comparison.csv` |
| 5 | `05_danh_gia_test.ipynb` | `test-00000-of-00001.parquet`<br>`splits.csv`<br>`frozen_config.json`<br>`src/baseline.py`<br>`src/improved.py` | Chạy OCR cho 361 ảnh Test. Áp dụng song song Baseline và Improved (8 cờ đã đóng băng), tuyệt đối không sửa luật. Tính toán Exact Match, Token F1, phân tích lỗi. | `outputs/ground_truth/test_ground_truth.csv`<br>`outputs/ocr/test_ocr.csv`<br>`outputs/test/baseline_test.csv`<br>`outputs/test/improved_test.csv`<br>`outputs/test/test_comparison.csv` |

### Chi tiết các bước thực hiện:

#### Bước 1: Khảo sát và phân chia tập dữ liệu (`01_khao_sat.ipynb`)
- Mở và chạy toàn bộ các ô trong `01_khao_sat.ipynb`.
- Sử dụng `np.random.default_rng(42)` để xáo trộn ngẫu nhiên tập 626 mẫu Train gốc.
- Tạo phân vùng: 501 mẫu Train (80.03%), 125 mẫu Validation (19.97%), và 361 mẫu Test (100%).
- Xuất danh sách chỉ mục vào `splits.csv` và các tệp nhãn chuẩn Ground Truth vào `outputs/ground_truth/`.

#### Bước 2: Tiền xử lý ảnh và trích xuất OCR (`02_ocr.ipynb`)
- Mở và chạy toàn bộ các ô trong `02_ocr.ipynb`.
- Quy chuẩn tiền xử lý:
  - Chuyển xám: `cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)`
  - Phóng to 2 lần nội suy Cubic: `cv2.resize(gray, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)`
  - Cấu hình Tesseract: `lang="eng", config="--oem 3 --psm 6"`
- Lưu kết quả nhận dạng thô của 626 hóa đơn vào `outputs/ocr/train_validation_ocr.csv`.

#### Bước 3: Đánh giá mô hình cơ sở Baseline (`03_baseline.ipynb`)
- Mở và chạy `03_baseline.ipynb`.
- Logic trích xuất Baseline (`src/baseline.py`):
  - `company`: Dòng đầu tiên trong số 5 dòng đầu có ít nhất 3 chữ cái.
  - `date`: Biểu thức chính quy đầu tiên khớp với định dạng ngày tháng (`DD/MM/YYYY`, `YYYY-MM-DD`, `DD Mon YYYY`), ưu tiên dòng có từ khóa `DATE`.
  - `total`: Quét các từ khóa `GRAND TOTAL`, `TOTAL AMOUNT`, `TOTAL`... và trích xuất số tiền cuối dòng.
  - `address`: Gom tối đa 8 dòng phía sau Company nếu dòng đó chứa từ khóa địa danh (`JALAN`, `TAMAN`, `SELANGOR`...) hoặc mã bưu chính 5 chữ số.
- Đánh giá trên 125 mẫu Validation để xác định điểm mốc cơ sở.

#### Bước 4: Nghiên cứu cải tiến và đóng băng cấu hình (`04_cai_tien.ipynb`)
- Mở và chạy `04_cai_tien.ipynb`.
- Thực hiện Ablation Study đánh giá 11 cờ độc lập trên tập Train (501 ảnh):
  - 8 cờ thỏa mãn điều kiện `gain >= 0.005` (0.5%):
    - `company_v2`: Cơ chế chấm điểm từ khóa pháp nhân và ghép dòng ngắt (`SDN BHD`, `ENTERPRISE`...).
    - `clean_date`: Nắn chỉnh lỗi ký tự quang học trong ngày (`O/0`, `l/1`...).
    - `date_v2`: Kiểm tra tính hợp lệ của ngày, bỏ qua ngày hết hạn.
    - `clean_amount`: Nắn chỉnh lỗi đọc chữ số trong trường số tiền.
    - `total_kw`: Mở rộng từ khóa tổng tiền và hỗ trợ cụm `TOTAL INCL GST`.
    - `total_pos`: Cơ chế dự phòng lấy số tiền lớn nhất ở phần đáy hóa đơn khi mất từ khóa.
    - `addr_v2`: Mở rộng bộ từ khóa nhận diện địa chỉ và cắt bỏ phần `TEL/FAX` thừa.
    - `addr_merge`: Ghép các khối dòng liên tiếp nhau thay vì lấy rải rác.
  - 3 cờ bị loại vì không đạt ngưỡng tăng điểm: `clean_text`, `total_nospace`, `total_gstcut`.
- Lưu cấu hình 8 cờ được chọn vào `outputs/improved/frozen_config.json`. Sau bước này, cấu hình được khóa cố định.

#### Bước 5: Đánh giá kiểm thử độc lập trên tập Test (`05_danh_gia_test.ipynb`)
- Lưu ý: Không thay đổi nội dung file `05_danh_gia_test.ipynb`.
- Notebook thực hiện đọc 361 ảnh từ `test-00000-of-00001.parquet`, chạy OCR theo quy chuẩn đã đóng băng, áp dụng `src/baseline.py` và `src/improved.py` (với `frozen_config.json`) để đối chiếu kết quả cuối cùng.

---

## 7. Phương pháp đánh giá và kết quả thực nghiệm

### 7.1. Định nghĩa các chỉ số đánh giá
1. Chuẩn hóa trước khi so khớp:
   - Text (`company`, `address`): Chuyển chữ thường, xóa toàn bộ dấu câu, thu gọn nhiều khoảng trắng thành một khoảng trắng đơn.
   - Date: Chuyển đổi mọi định dạng ngày về chuẩn ISO `YYYY-MM-DD`.
   - Total: Loại bỏ ký hiệu tiền tệ (`RM`, `$`), xóa dấu phẩy ngăn cách hàng nghìn, quy về số thực làm tròn 2 chữ số thập phân (`xx.xx`).
2. Exact Match (EM): Trả về 1 nếu giá trị dự đoán trùng khớp tuyệt đối 100% với nhãn chuẩn Ground Truth sau khi đã chuẩn hóa; ngược lại tính 0 điểm.
3. Macro EM: Điểm trung bình cộng EM của cả 4 trường:
   $$\text{Macro EM} = \frac{\text{EM}_{\text{company}} + \text{EM}_{\text{date}} + \text{EM}_{\text{address}} + \text{EM}_{\text{total}}}{4}$$
4. Token-level Precision, Recall, F1: Đánh giá độ phủ và mức độ trùng khớp từng phần trên hai trường chuỗi dài là `company` và `address`.
5. All-Invoice Accuracy: Tỷ lệ phần trăm số hóa đơn mà cả 4 trường đều đạt Exact Match đồng thời trên cùng một tờ hóa đơn.

### 7.2. Kết quả trên tập Validation (125 hóa đơn - Đối chứng tinh chỉnh)

| Trường thông tin | Baseline EM (%) | Improved EM (%) | Chênh lệch EM |
| :--- | :---: | :---: | :---: |
| Company | 24.80% | 36.00% | +11.20% |
| Date | 75.20% | 80.80% | +5.60% |
| Address | 30.40% | 35.20% | +4.80% |
| Total | 56.80% | 69.60% | +12.80% |
| Macro EM (Trung bình) | 46.80% | 55.40% | +8.60% |

Ghi chú: Trên tập Validation, mô hình Improved sửa đúng thêm 43 lượt trường/ảnh mà không làm hỏng bất kỳ trường nào đang đúng ở mô hình Baseline.

### 7.3. Kết quả trên tập Test độc lập (361 hóa đơn - Kiểm thử cuối cùng)

| Chỉ số / Trường thông tin | Baseline | Improved | Chênh lệch |
| :--- | :---: | :---: | :---: |
| Company Exact Match | 17.17% (62/361) | 30.75% (111/361) | +13.58% |
| Company Token F1 | 47.81% | 67.09% | +19.28% |
| Date Exact Match | 67.31% (243/361) | 68.98% (249/361) | +1.67% |
| Address Exact Match | 14.13% (51/361) | 5.54% (20/361) | -8.59% |
| Address Token F1 | 73.70% | 75.98% | +2.28% |
| Total Exact Match | 56.23% (203/361) | 65.37% (236/361) | +9.14% |
| All-Invoice Accuracy | 3.32% (12/361) | 1.11% (4/361) | -2.22% |
| Tổng số lỗi trích xuất | 885 lỗi | 828 lỗi | Giảm 57 lỗi |

### 7.4. Phân tích kết quả thực nghiệm
- Trường Company: Đạt bước tiến rõ rệt nhất, EM tăng từ 17.17% lên 30.75% (+13.58%), Token F1 tăng +19.28%. Quy tắc chấm điểm heuristic và nối cụm từ pháp nhân bị ngắt dòng hoạt động ổn định trên dữ liệu mới.
- Trường Total: EM tăng từ 56.23% lên 65.37% (+9.14%), bắt đúng thêm 33 hóa đơn nhờ sự kết hợp giữa mở rộng từ khóa và cơ chế dự phòng vị trí đáy hóa đơn.
- Trường Address: EM giảm từ 14.13% xuống 5.54% (-8.59%), nhưng Token F1 lại tăng từ 73.70% lên 75.98% (+2.28%).
  - Bản chất: Thuật toán `addr_merge` gom cụm các khối dòng liên tiếp giúp bao phủ trọn vẹn thông tin địa chỉ thực tế. Tuy nhiên, do địa chỉ dài (trên 40 ký tự), chỉ cần OCR nhận diện sai một ký tự số nhà, tên đường hoặc dấu phân cách thì tiêu chuẩn Exact Match sẽ đánh giá là 0 điểm. Việc Token F1 tăng chứng minh lượng thông tin có ích trích xuất thực tế tăng lên.

---

## 8. Hướng dẫn khởi chạy Giao diện Demo

Ứng dụng Demo được xây dựng tại `demo.py`, cho phép tương tác trực quan qua trình duyệt:

```bash
# Khởi chạy ứng dụng Streamlit
streamlit run demo.py
```
Sau khi chạy lệnh, truy cập trình duyệt tại: `http://localhost:8501`.

### Các chức năng trên giao diện:
1. Tải ảnh hóa đơn: Kéo thả tệp ảnh bất kỳ định dạng JPG, JPEG hoặc PNG.
2. Thử nghiệm nhanh với ảnh mẫu: Nút bấm chọn sẵn ảnh mẫu SROIE (`data/ICDAR2019-SROIE/assets/ex.jpg`).
3. Lựa chọn phương pháp:
   - Improved (Mặc định): Sử dụng thuật toán cải tiến 8 cờ đóng băng.
   - Baseline: Sử dụng thuật toán cơ sở.
   - So sánh song song: Hiển thị bảng đối chiếu kết quả của cả hai mô hình.
4. Hiển thị kết quả: Thẻ thông tin 4 trường dữ liệu, hiển thị toàn bộ văn bản OCR thô và nút tải kết quả trích xuất dạng file JSON.

---

## 9. Các lỗi thường gặp và cách khắc phục

1. Thiếu file `outputs/improved/frozen_config.json`:
   - Hiện tượng: Báo lỗi không tìm thấy file cấu hình khi chạy `demo.py`.
   - Nguyên nhân: Thư mục `outputs/` nằm trong `.gitignore` nên không được lưu trữ trên Git remote.
   - Khắc phục: Chạy lại ô đóng băng cấu hình trong `04_cai_tien.ipynb`, hoặc tạo tệp `outputs/improved/frozen_config.json` với nội dung 8 cờ đã chốt:
     ```json
     {
       "cfg": {
         "clean_text": false, "clean_date": true, "date_v2": true, "clean_amount": true,
         "total_kw": true, "total_nospace": false, "total_gstcut": false, "total_pos": true,
         "company_v2": true, "addr_v2": true, "addr_merge": true
       }
     }
     ```

2. Lỗi đường dẫn `/app` khi chạy ngoài Docker:
   - Hiện tượng: Báo lỗi `FileNotFoundError: [Errno 2] No such file or directory: '/app'`.
   - Nguyên nhân: Đường dẫn tuyệt đối trong một số script cũ gán cứng theo môi trường Docker.
   - Khắc phục: Sử dụng `Path.cwd()` để tự động nhận diện thư mục gốc của dự án.

3. Lỗi thiếu thư viện `pyarrow` khi đọc Parquet:
   - Hiện tượng: Báo lỗi `ImportError: Unable to find a usable engine; tried using: 'pyarrow', 'fastparquet'`.
   - Khắc phục: Cài đặt bổ sung thư viện: `pip install pyarrow`.

---

## 10. Tài liệu tham khảo

1. ICDAR 2019 SROIE Competition:  
   Huang, Z., Chen, K., He, J., Bai, X., Karatzas, D., Lu, S., & Jawahar, C. V. (2019). *ICDAR2019 Competition on Scanned Receipt OCR and Information Extraction*. In 2019 International Conference on Document Analysis and Recognition (ICDAR), pp. 1516-1520.  
   DOI: [10.1109/icdar.2019.00244](https://doi.org/10.1109/icdar.2019.00244) | arXiv: [2103.10213](https://arxiv.org/abs/2103.10213) | Web: [https://rrc.cvc.uab.es/?ch=13](https://rrc.cvc.uab.es/?ch=13)

2. Dataset ICDAR2019-SROIE (Hugging Face Datasets):  
   jsdnrs. *ICDAR2019's Scanned Receipts OCR and Information Extraction (SROIE)*.  
   Hugging Face: [https://huggingface.co/datasets/jsdnrs/ICDAR2019-SROIE](https://huggingface.co/datasets/jsdnrs/ICDAR2019-SROIE) | GitHub: [https://github.com/jsdnrs/ICDAR2019-SROIE](https://github.com/jsdnrs/ICDAR2019-SROIE)

3. Tesseract OCR Engine:  
   Smith, R. (2007). *An Overview of the Tesseract OCR Engine*. In Ninth International Conference on Document Analysis and Recognition (ICDAR 2007).  
   Mã nguồn Tesseract: [https://github.com/tesseract-ocr/tesseract](https://github.com/tesseract-ocr/tesseract) | UB-Mannheim Windows binary: [https://github.com/UB-Mannheim/tesseract/wiki](https://github.com/UB-Mannheim/tesseract/wiki)

4. Thư viện Python chính thức:  
   - pytesseract: [https://pypi.org/project/pytesseract/](https://pypi.org/project/pytesseract/)  
   - OpenCV: [https://opencv.org/](https://opencv.org/)  
   - Streamlit: [https://streamlit.io/](https://streamlit.io/)  
   - Pillow (PIL): [https://python-pillow.org/](https://python-pillow.org/)

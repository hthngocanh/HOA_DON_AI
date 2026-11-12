import re

MONTHS = r"(?:JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC)[A-Z]*"

# Ba kiểu ngày: 25/12/2018, 2018-03-23, 25 Mar 2018
DATE_PATTERNS = [
    r"\b\d{1,2}\s*[/\-.]\s*\d{1,2}\s*[/\-.]\s*\d{2,4}\b",
    r"\b\d{4}\s*[/\-.]\s*\d{1,2}\s*[/\-.]\s*\d{1,2}\b",
    r"\b\d{1,2}[\s\-]*" + MONTHS + r"[\s\-,]*\d{2,4}\b",
]
DATE_RE = re.compile("|".join(f"(?:{p})" for p in DATE_PATTERNS), re.IGNORECASE)

# Số tiền có 2 chữ số thập phân (chấp nhận dấu phẩy do OCR đọc sai)
AMOUNT_RE = re.compile(r"\d[\d,]*[.,]\s?\d{2}\b")

# Thứ tự ưu tiên từ khóa tổng tiền
TOTAL_KEYS = ["GRAND TOTAL", "TOTAL ROUNDED", "ROUNDED TOTAL", "NET TOTAL",
              "TOTAL AMOUNT", "AMOUNT DUE", "AMOUNT PAYABLE", "TOTAL"]
# Bỏ các dòng không phải tổng tiền cuối
TOTAL_EXCLUDE = re.compile(
    r"SUB|EXCL|QTY|QUANTITY|SAVING|DISCOUNT|POINT|TOTAL\s*GST|TAX", re.IGNORECASE)

ADDR_KW = re.compile(
    r"\b(JALAN|JLN|TAMAN|TMN|LOT|NO|BANDAR|KAWASAN|SELANGOR|JOHOR|KUALA LUMPUR|KL|"
    r"PETALING|SHAH ALAM|KLANG|CHERAS|PAHANG|PENANG|WILAYAH)\b", re.IGNORECASE)
POSTCODE = re.compile(r"\b\d{5}\b")
ADDR_STOP = re.compile(
    r"\b(TEL|FAX|GST|INVOICE|RECEIPT|DATE|CASH|BILL|TAX|DOC|CASHIER)\b", re.IGNORECASE)


def _get_lines(ocr_text):
    if not isinstance(ocr_text, str):
        return []
    return [ln.strip() for ln in ocr_text.split("\n") if ln.strip()]


def _find_company(lines):
    """Luật: dòng đầu tiên trong 5 dòng đầu có ít nhất 3 chữ cái."""
    for i, ln in enumerate(lines[:5]):
        if sum(c.isalpha() for c in ln) >= 3:
            return ln, i
    return None, -1


def _find_date(lines):
    """Luật: tìm ngày đầu tiên; ưu tiên dòng có chữ DATE."""
    for ln in lines:
        if "DATE" in ln.upper():
            m = DATE_RE.search(ln)
            if m:
                return m.group(0).strip()
    m = DATE_RE.search("\n".join(lines))
    return m.group(0).strip() if m else None


def _find_total(lines):
    """Luật: duyệt từ khóa theo thứ tự ưu tiên, lấy số cuối dòng (hoặc dòng kế)."""
    for key in TOTAL_KEYS:
        for i, ln in enumerate(lines):
            up = ln.upper()
            if key in up and not TOTAL_EXCLUDE.search(up):
                amounts = AMOUNT_RE.findall(ln)
                if not amounts and i + 1 < len(lines):
                    amounts = AMOUNT_RE.findall(lines[i + 1])
                if amounts:
                    return amounts[-1].replace(" ", "")
    return None


def _find_address(lines, company_idx):
    """Luật: sau dòng company (tối đa 8 dòng), gom dòng có từ khóa địa chỉ hoặc mã bưu chính,
    dừng khi gặp TEL/GST/INVOICE..."""
    if company_idx < 0:
        return None
    parts = []
    for ln in lines[company_idx + 1: company_idx + 9]:
        if ADDR_STOP.search(ln):
            break
        if ADDR_KW.search(ln) or POSTCODE.search(ln):
            parts.append(ln)
    return " ".join(parts) if parts else None


def extract_fields(ocr_text):
    """Baseline: OCR text -> 4 trường. Không tìm thấy thì trả None."""
    lines = _get_lines(ocr_text)
    company, cidx = _find_company(lines)
    return {
        "company": company,
        "date": _find_date(lines),
        "address": _find_address(lines, cidx),
        "total": _find_total(lines),
    }
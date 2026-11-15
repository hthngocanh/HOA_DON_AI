<<<<<<< HEAD
"""improved.py - phuong phap cai tien (Nguoi 4). Tu dong sinh tu 04_cai_tien.ipynb."""
import re
from datetime import date as _date

FIELDS = ["company", "date", "address", "total"]

DEFAULT_CFG = dict(
    clean_text=False,     # lam sach dong OCR: bo ky tu rac dau dong, \x0c, dong chi co ky hieu
    clean_date=False,     # sua nham O/0, l/1, S/5... trong chuoi ngay (truoc khi tim ngay)
    date_v2=False,        # kiem tra ngay hop le, nhieu dinh dang, uu tien dong DATE, bo ngay het han
    clean_amount=False,   # sua nham ky tu so trong so tien (truoc khi tim total)
    total_kw=False,       # tu khoa total mo rong + khong loai nham 'TOTAL INCL GST'
    total_nospace=False,  # so khop tu khoa sau khi bo khoang trang (NetTotal, GRANDTOTAL)
    total_gstcut=False,   # bo phan GST/TAX SUMMARY khi tim total
    total_pos=False,      # khong co tu khoa -> so lon nhat o phan duoi hoa don
    company_v2=False,     # cham diem cac dong dau de chon ten cong ty (+ ghep SDN BHD tach dong)
    addr_v2=False,        # dia chi: dau hieu dia chi rong hon, cat phan TEL/FAX cuoi dong
    addr_merge=False,     # dia chi: lay KHOI dong lien tiep (cho phep hong 1 dong) thay vi gom roi rac
)

# ================================================================ BASELINE (sao chep tu src/baseline.py cua nguoi 3)
=======
import re
import unicodedata

>>>>>>> 1e8c6cb (htna)
MONTHS = r"(?:JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC)[A-Z]*"
DATE_PATTERNS = [
    r"\b\d{1,2}\s*[/\-.]\s*\d{1,2}\s*[/\-.]\s*\d{2,4}\b",
    r"\b\d{4}\s*[/\-.]\s*\d{1,2}\s*[/\-.]\s*\d{1,2}\b",
    r"\b\d{1,2}[\s\-]*" + MONTHS + r"[\s\-,]*\d{2,4}\b",
]
DATE_RE = re.compile("|".join(f"(?:{p})" for p in DATE_PATTERNS), re.IGNORECASE)
AMOUNT_RE = re.compile(r"\d[\d,]*[.,]\s?\d{2}\b")
<<<<<<< HEAD
TOTAL_KEYS = ["GRAND TOTAL", "TOTAL ROUNDED", "ROUNDED TOTAL", "NET TOTAL",
              "TOTAL AMOUNT", "AMOUNT DUE", "AMOUNT PAYABLE", "TOTAL"]
TOTAL_EXCLUDE = re.compile(r"SUB|EXCL|QTY|QUANTITY|SAVING|DISCOUNT|POINT|TOTAL\s*GST|TAX", re.IGNORECASE)
ADDR_KW = re.compile(
    r"\b(JALAN|JLN|TAMAN|TMN|LOT|NO|BANDAR|KAWASAN|SELANGOR|JOHOR|KUALA LUMPUR|KL|"
    r"PETALING|SHAH ALAM|KLANG|CHERAS|PAHANG|PENANG|WILAYAH)\b", re.IGNORECASE)
POSTCODE = re.compile(r"\b\d{5}\b")
ADDR_STOP = re.compile(r"\b(TEL|FAX|GST|INVOICE|RECEIPT|DATE|CASH|BILL|TAX|DOC|CASHIER)\b", re.IGNORECASE)


def _get_lines(ocr_text):
    if not isinstance(ocr_text, str):
        return []
    return [ln.strip() for ln in ocr_text.split("\n") if ln.strip()]


def _b_company(lines):
    for i, ln in enumerate(lines[:5]):
        if sum(c.isalpha() for c in ln) >= 3:
            return ln, i
    return None, -1


def _b_date(lines):
    for ln in lines:
        if "DATE" in ln.upper():
            m = DATE_RE.search(ln)
            if m:
                return m.group(0).strip()
    m = DATE_RE.search("\n".join(lines))
    return m.group(0).strip() if m else None


def _b_address(lines, company_idx):
    if company_idx < 0:
        return None
    parts = []
    for ln in lines[company_idx + 1: company_idx + 9]:
        if ADDR_STOP.search(ln):
            break
        if ADDR_KW.search(ln) or POSTCODE.search(ln):
            parts.append(ln)
    return " ".join(parts) if parts else None


# ================================================================ lam sach
_CONF = str.maketrans("OoIl|SsBZ", "001115582")
_TOKEN = re.compile(r"[0-9A-Za-z|./,\-]{4,}")
_ALLOWED = set("0123456789OoIl|SsBZ./,-")


def _digit_fix(line):
    """Trong token co >= 2 chu so va chi gom ky tu de nham, doi O->0, l->1, S->5..."""
    def fn(m):
        t = m.group(0)
        if sum(c.isdigit() for c in t) >= 2 and all(c in _ALLOWED for c in t):
            return t.translate(_CONF)
        return t
    return _TOKEN.sub(fn, line)


def _clean_lines(lines):
    out = []
    for l in lines:
        l = l.replace("\x0c", " ")
        l = re.sub(r"^[^A-Za-z0-9(]+", "", l)
        l = re.sub(r"\s+", " ", l).strip()
        if sum(c.isalnum() for c in l) >= 2:
            out.append(l)
    return out


# ================================================================ date
_MONTHS = {m: i + 1 for i, m in enumerate("JAN FEB MAR APR MAY JUN JUL AUG SEP OCT NOV DEC".split())}
_MON = "|".join(_MONTHS)
_P_NUM = re.compile(r"(?<!\d)(\d{1,2})\s*[/\-.]\s*(\d{1,2})\s*[/\-.]\s*(\d{4}|\d{2})(?!\d)")
_P_ISO = re.compile(r"(?<!\d)(\d{4})\s*[/\-.]\s*(\d{1,2})\s*[/\-.]\s*(\d{1,2})(?!\d)")
_P_TXT = re.compile(r"(?<!\d)(\d{1,2})\s*[\- ]?\s*(" + _MON + r")[A-Z]*\.?[\s,\-]*(\d{4}|\d{2})(?!\d)")
_P_TXT2 = re.compile(r"(" + _MON + r")[A-Z]*\.?\s*(\d{1,2})(?:ST|ND|RD|TH)?[\s,\-]+(\d{4})(?!\d)")


def _mk(y, m, d):
    y, m, d = int(y), int(m), int(d)
    if y < 100:
        y += 2000
    if not 2000 <= y <= 2030:
        return None
    try:
        return _date(y, m, d).isoformat()
    except ValueError:
        return None


def _find_dates_line(u):
    """-> list[(vi_tri, iso, chuoi_goc)] chi gom ngay HOP LE."""
    out = []
    for m in _P_ISO.finditer(u):
        iso = _mk(*m.groups())
        if iso:
            out.append((m.start(), iso, m.group(0)))
    for m in _P_NUM.finditer(u):
        a, b, c = m.groups()
        a_, b_ = int(a), int(b)
        if b_ > 12 and a_ <= 12:
            a_, b_ = b_, a_
        iso = _mk(c, b_, a_)
        if iso:
            out.append((m.start(), iso, m.group(0)))
    for m in _P_TXT.finditer(u):
        d, mon, y = m.groups()
        iso = _mk(y, _MONTHS[mon], d)
        if iso:
            out.append((m.start(), iso, m.group(0)))
    for m in _P_TXT2.finditer(u):
        mon, d, y = m.groups()
        iso = _mk(y, _MONTHS[mon], d)
        if iso:
            out.append((m.start(), iso, m.group(0)))
    return sorted(out)


def _v2_date(lines):
    best = None
    for i, l in enumerate(lines):
        u = l.upper()
        for pos, iso, raw in _find_dates_line(u):
            score = 2 if "DATE" in u else 0
            if re.search(r"EXP|DUE|VALID|BEST BEFORE", u):
                score -= 2
            key = (score, -i, -pos)
            if best is None or key > best[0]:
                best = (key, raw)
    return best[1].strip() if best else None


def extract_date(lines, cfg):
    if cfg["clean_date"]:
        lines = [_digit_fix(l) for l in lines]
    if cfg["date_v2"]:
        d = _v2_date(lines)
        if d:
            return d
    return _b_date(lines)


# ================================================================ total
_TOTAL_KEYS_V2 = ["GRAND TOTAL", "TOTAL ROUNDED", "ROUNDED TOTAL", "NET TOTAL", "NETT TOTAL", "TOTAL AMOUNT",
                  "AMOUNT DUE", "TOTAL DUE", "AMOUNT PAYABLE", "TOTAL PAYABLE", "TOTAL INCL", "TOTAL SALES", "TOTAL"]
_TOTAL_EXCLUDE_V2 = re.compile(r"SUB|EXCL|QTY|QUANTITY|SAVING|DISCOUNT|POINT|CHANGE|TENDER|TOTAL\s*(?:GST|TAX)|"
                               r"(?:GST|TAX)\s*TOTAL", re.IGNORECASE)
_GST_HEAD = re.compile(r"(?:GST|TAX)\s*(?:SUMMARY|ANALYSIS)", re.IGNORECASE)


def _amount_value(a):
    s = a.replace(" ", "")
    if re.search(r",\d{2}$", s):
        s = s[:-3] + "." + s[-2:]
    return float(s.replace(",", ""))


def extract_total(lines, cfg):
    if cfg["clean_amount"]:
        lines = [_digit_fix(l) for l in lines]
    if cfg["total_gstcut"]:
        for i, l in enumerate(lines):
            if _GST_HEAD.search(l):
                lines = lines[:i]
                break
    keys = _TOTAL_KEYS_V2 if cfg["total_kw"] else TOTAL_KEYS
    excl = _TOTAL_EXCLUDE_V2 if cfg["total_kw"] else TOTAL_EXCLUDE
    ns = cfg["total_nospace"]
    for key in keys:
        k = key.replace(" ", "") if ns else key
        for i, ln in enumerate(lines):
            up = ln.upper().replace(" ", "") if ns else ln.upper()
            if k in up and not excl.search(ln.upper()):
                amounts = AMOUNT_RE.findall(ln)
=======
TOTAL_KEYS = ["GRAND TOTAL", "TOTAL ROUNDED", "ROUNDED TOTAL", "NET TOTAL", "TOTAL AMOUNT", "AMOUNT DUE", "AMOUNT PAYABLE", "TOTAL"]
TOTAL_EXCLUDE = re.compile(r"SUB|EXCL|QTY|QUANTITY|SAVING|DISCOUNT|POINT|TOTAL\s*GST|TAX", re.IGNORECASE)
ADDR_KW = re.compile(r"\b(JALAN|JLN|TAMAN|TMN|LOT|NO|BANDAR|KAWASAN|SELANGOR|JOHOR|KUALA LUMPUR|KL|PETALING|SHAH ALAM|KLANG|CHERAS|PAHANG|PENANG|WILAYAH)\b", re.IGNORECASE)
POSTCODE = re.compile(r"\b\d{5}\b")
ADDR_STOP = re.compile(r"\b(TEL|FAX|GST|INVOICE|RECEIPT|DATE|CASH|BILL|TAX|DOC|CASHIER)\b", re.IGNORECASE)

COMPANY_HINTS = (
    "sdn", "bhd", "enterprise", "trading", "mart", "store", "restaurant",
    "cafe", "machinery", "gift", "home", "market", "supermarket", "shop",
)
ADDRESS_HINTS = (
    "jalan", "jln", "street", "road", "lorong", "taman", "lot",
    "selangor", "johor", "klang", "kuala lumpur", "penang", "perak", "melaka",
)
NON_COMPANY = re.compile(r"\b(invoice|receipt|cashier|tel|telephone|phone|fax|date|time|member|cash bill|tax invoice)\b", re.I)
DATE_LIKE = re.compile(r"\b\d{1,2}[/.-]\d{1,2}[/.-]\d{2,4}\b")
COMPANY_POSTCODE = re.compile(r"\b\d{5}\b")


def _get_lines(ocr_text: str) -> list[str]:
    if not isinstance(ocr_text, str):
        return []
    return [line.strip() for line in ocr_text.split("\n") if line.strip()]


def _find_company_base(lines: list[str]):
    for i, line in enumerate(lines[:5]):
        if sum(char.isalpha() for char in line) >= 3:
            return line, i
    return None, -1


def _find_date(lines: list[str]):
    for line in lines:
        if "DATE" in line.upper():
            match = DATE_RE.search(line)
            if match:
                return match.group(0).strip()
    match = DATE_RE.search("\n".join(lines))
    return match.group(0).strip() if match else None


def _find_total(lines: list[str]):
    for key in TOTAL_KEYS:
        for i, line in enumerate(lines):
            upper = line.upper()
            if key in upper and not TOTAL_EXCLUDE.search(upper):
                amounts = AMOUNT_RE.findall(line)
>>>>>>> 1e8c6cb (htna)
                if not amounts and i + 1 < len(lines):
                    amounts = AMOUNT_RE.findall(lines[i + 1])
                if amounts:
                    return amounts[-1].replace(" ", "")
<<<<<<< HEAD
    if cfg["total_pos"]:
        n = len(lines)
        cands = []
        for i, ln in enumerate(lines):
            if i >= n * 0.4 and not excl.search(ln.upper()):
                for a in AMOUNT_RE.findall(ln):
                    try:
                        cands.append((_amount_value(a), a))
                    except ValueError:
                        pass
        if cands:
            return max(cands)[1].replace(" ", "")
    return None


# ================================================================ company
_LEGAL = re.compile(r"\b(SDN\.?\s*BHD|BHD|S/?B|ENTERPRISE|TRADING|RESTAURANT|RESTORAN|STORE|MARKET|MART|CAFE|"
                    r"BAKERY|PHARMACY|LTD|INC|CO\.?|PLT|CORPORATION|HOLDINGS|SUPERMARKET|HARDWARE|BOOK|"
                    r"GIFT|HOME|MACHINERY|SHOP|MEDICAL|CLINIC|KEDAI)\b")
_NOISE = re.compile(r"\b(TEL|FAX|PHONE|INVOICE|RECEIPT|TAX|DATE|GST|REG|CASHIER|DOC|BILL|WWW|EMAIL|HP)\b|\bNO\s*[:.]")
_ADDR_CUE = re.compile(r"\b(JALAN|JLN|LORONG|LRG|TAMAN|TMN|BANDAR|KAWASAN|LOT|FLOOR|LEVEL|BLOCK|BLK|MENARA|WISMA|"
                       r"SEKSYEN|PUSAT|KOMPLEKS|MALAYSIA|KUALA LUMPUR|SELANGOR|JOHOR|PENANG|PERAK|KEDAH|SABAH|"
                       r"SARAWAK|MELAKA|PAHANG|PETALING|SHAH ALAM|KLANG|CHERAS|WILAYAH|KL|NO)\b", re.IGNORECASE)
_ADDR_STOP2 = re.compile(r"\b(TEL|FAX|PHONE|GST|INVOICE|RECEIPT|DATE|DOC|CASHIER|EMAIL|WWW|HP|BILL|SLIP|CASH|TAX)\b",
                         re.IGNORECASE)


def _v2_company(lines):
    best = None
    for rank, i in enumerate(range(min(len(lines), 8))):
        l = lines[i].strip()
        u = l.upper()
        if len(l) < 3 or sum(c.isalpha() for c in l) < 3:
            continue
        s = -0.3 * rank
        if _LEGAL.search(u):
            s += 3
        if _NOISE.search(u):
            s -= 4
        if _ADDR_CUE.search(u) or re.search(r"\b\d{5}\b", u):
            s -= 3
        if sum(c.isdigit() for c in l) / len(l) > 0.3:
            s -= 2
        letters = [c for c in l if c.isalpha()]
        up = sum(c.isupper() for c in letters) / len(letters)
        s += 1 if up >= 0.8 else (-1.5 if up == 0 else 0)
        if best is None or s > best[0]:
            best = (s, i)
    if best is None:
        return None, -1
    i = best[1]
    name, end = lines[i].strip(), i
    if (i + 1 < len(lines) and not _LEGAL.search(name.upper())
            and re.match(r"^\s*(SDN\.?\s*BHD|BHD|\(?S/?B\)?)\b", lines[i + 1].upper())):
        name, end = name + " " + lines[i + 1].strip(), i + 1
    return name, end


# ================================================================ address
def _cut_tail(l):
    return re.split(r"\b(?:TEL|PHONE|FAX|HP)\b", l, maxsplit=1, flags=re.I)[0].strip(" ,:-")


def extract_address(lines, cidx, cfg):
    if cidx < 0:
        return None
    if not (cfg["addr_v2"] or cfg["addr_merge"]):
        return _b_address(lines, cidx)           # = baseline, nhung tinh tu dong company da chon
    v2 = cfg["addr_v2"]
    kw = _ADDR_CUE if v2 else ADDR_KW
    stop = _ADDR_STOP2 if v2 else ADDR_STOP
    window = lines[cidx + 1: cidx + 9]
    fix = _cut_tail if v2 else (lambda x: x)
    if not cfg["addr_merge"]:                    # chi addr_v2: gom nhu baseline nhung dau hieu rong hon + cat TEL
        parts = []
        for ln in window:
            if stop.search(ln):
                break
            if kw.search(ln) or POSTCODE.search(ln):
                parts.append(fix(ln))
        return " ".join(p for p in parts if p) or None
    # addr_merge: lay KHOI dong lien tiep co dau hieu dia chi, cho phep hong toi da 1 dong giua khoi
    parts, started, gap = [], False, 0
    for ln in window:
        if stop.search(ln):
            break
        if kw.search(ln) or POSTCODE.search(ln):
            parts.append(fix(ln))
            started, gap = True, 0
        elif started:
            gap += 1
            if gap > 1:
                break
            parts.append(("?", fix(ln)))
    out = []
    for p in parts:
        out.append(p)
    # bo dong 'hong' o cuoi khoi, giu dong 'hong' nam giua hai dong dia chi
    while out and isinstance(out[-1], tuple):
        out.pop()
    return " ".join(p[1] if isinstance(p, tuple) else p for p in out if (p[1] if isinstance(p, tuple) else p)) or None


# ================================================================ API
def extract(text, cfg=None):
    cfg = {**DEFAULT_CFG, **(cfg or {})}
    lines = _get_lines(text)
    if cfg["clean_text"]:
        lines = _clean_lines(lines)
    if cfg["company_v2"]:
        company, cidx = _v2_company(lines)
    else:
        company, cidx = _b_company(lines)
    return dict(company=company, date=extract_date(lines, cfg),
                address=extract_address(lines, cidx, cfg), total=extract_total(lines, cfg))




# ---- tien xu ly anh + OCR (giong 02_ocr.ipynb cua nguoi 1: Tesseract, --oem 3 --psm 6, lang eng) ----
OCR_CONFIG = "--oem 3 --psm 6"
REF_STEPS = ["gray", "resize2"]      # dung nhu OCR CSV cua nguoi 1: grayscale + phong 2x (INTER_CUBIC)


def _deskew(gray):
    import cv2
    import numpy as np
    ink = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
    ys, xs = np.where(ink > 0)
    if len(xs) < 200:
        return gray
    ang = cv2.minAreaRect(np.column_stack([xs, ys]).astype(np.float32))[-1]
    ang = ang - 90 if ang > 45 else ang
    if not 0.3 <= abs(ang) <= 15:
        return gray
    h, w = gray.shape[:2]

    def rot(a):
        M = cv2.getRotationMatrix2D((w / 2, h / 2), a, 1.0)
        return cv2.warpAffine(gray, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)

    def sharp(img):   # dong chu thang -> tong theo hang dao dong manh (tranh nham dau goc giua cac ban OpenCV)
        b = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
        return float(np.var(b.sum(axis=1)))

    r1, r2 = rot(ang), rot(-ang)
    return max([(sharp(gray), gray), (sharp(r1), r1), (sharp(r2), r2)], key=lambda c: c[0])[1]


def preprocess_image(rgb, steps):
    """rgb: ndarray HxWx3 (RGB); steps: danh sach buoc ap dung theo thu tu."""
    import cv2
    out = rgb
    for st in steps:
        if st == "gray":
            out = cv2.cvtColor(out, cv2.COLOR_RGB2GRAY) if out.ndim == 3 else out
        elif st in ("resize2", "resize3"):
            f = 2 if st == "resize2" else 3
            out = cv2.resize(out, None, fx=f, fy=f, interpolation=cv2.INTER_CUBIC)
        elif st == "median":
            out = cv2.medianBlur(out, 3)
        elif st == "clahe":
            out = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8)).apply(out)
        elif st == "otsu":
            out = cv2.threshold(cv2.GaussianBlur(out, (3, 3), 0), 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
        elif st == "adaptive":
            out = cv2.adaptiveThreshold(cv2.GaussianBlur(out, (3, 3), 0), 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                        cv2.THRESH_BINARY, 31, 15)
        elif st == "deskew":
            out = _deskew(out)
        else:
            raise ValueError("buoc tien xu ly khong biet: " + st)
    return out


def ocr_image(pil_image, steps=None):
    import numpy as np
    import pytesseract
    steps = REF_STEPS if steps is None else steps
    img = preprocess_image(np.array(pil_image.convert("RGB")), steps)
    return pytesseract.image_to_string(img, lang="eng", config=OCR_CONFIG)


# ---------------- ham chuan hoa + tai cau hinh dong bang (danh cho nguoi 5) ----------------
from datetime import datetime as _dt
import json as _json
from pathlib import Path as _Path

_DATE_FORMATS = ["%d/%m/%Y","%d-%m-%Y","%d.%m.%Y","%d/%m/%y","%d-%m-%y","%d.%m.%y","%Y-%m-%d","%Y/%m/%d",
                 "%d %b %Y","%d%b%Y","%d-%b-%Y","%d %b %y","%d %B %Y"]

def is_missing(x):
    return x is None or (isinstance(x, float) and x != x) or str(x).strip() == ""

def norm_text(s):
    if is_missing(s): return None
    s = re.sub(r"[^\w\s]", " ", str(s).lower()); return re.sub(r"\s+", " ", s).strip()

def norm_total(s):
    if is_missing(s): return None
    nums = re.findall(r"\d[\d,.]*", str(s).replace(" ", ""))
    if not nums: return None
    tok = nums[-1]
    if re.search(r",\d{2}$", tok): tok = tok[:-3] + "." + tok[-2:]
    tok = tok.replace(",", "")
    try: return f"{float(tok):.2f}"
    except ValueError: return None

def norm_date(s):
    if is_missing(s): return None
    core = re.sub(r"\s*([/\-.])\s*", r"\1", str(s).strip())
    for cand in (core, core.replace(" ", "")):
        for f in _DATE_FORMATS:
            try: return _dt.strptime(cand, f).strftime("%Y-%m-%d")
            except ValueError: pass
    return norm_text(core)

NORM = {"company": norm_text, "address": norm_text, "date": norm_date, "total": norm_total}

def exact(pred, gold, field):
    if is_missing(pred) or is_missing(gold): return 0
    return int(NORM[field](pred) == NORM[field](gold))

_FROZEN_DEFAULT = _Path(__file__).resolve().parents[1] / "outputs" / "improved" / "frozen_config.json"

def _frozen(path=None):
    p = _Path(path) if path else _FROZEN_DEFAULT
    return _json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}

def load_frozen_cfg(path=None):
    """Cau hinh dong bang; neu chua co file (chua chot) thi tam dung TAT CA co bat de demo chay duoc."""
    cfg = _frozen(path).get("cfg")
    return cfg if cfg else {k: True for k in DEFAULT_CFG}

def load_frozen_ocr_steps(path=None):
    return _frozen(path).get("ocr", {}).get("steps", REF_STEPS)

def ocr_frozen(pil_image, path=None):
    """Anh (PIL) -> van ban OCR bang dung buoc tien xu ly da dong bang."""
    return ocr_image(pil_image, load_frozen_ocr_steps(path))

def extract_improved(ocr_text, cfg=None):
    """Ham cho demo.py/Nguoi 5: van ban OCR -> dict 4 truong {company, date, address, total} (gia tri GOC;
    truong khong tim thay = None). Dung cau hinh dong bang trong outputs/improved/frozen_config.json."""
    return extract(ocr_text, cfg if cfg is not None else load_frozen_cfg())

def extract_frozen(ocr_text, path=None):
    return extract(ocr_text, load_frozen_cfg(path))
=======
    return None


def _find_address(lines: list[str], company_idx: int):
    if company_idx < 0:
        return None
    parts = []
    for line in lines[company_idx + 1 : company_idx + 9]:
        if ADDR_STOP.search(line):
            break
        if ADDR_KW.search(line) or POSTCODE.search(line):
            parts.append(line)
    return " ".join(parts) if parts else None


def clean_company_line(value: str) -> str:
    value = unicodedata.normalize("NFKC", str(value))
    return re.sub(r"\s+", " ", value).strip(" \t|:;,-")


def company_candidate(lines: list[str]):
    candidates = []
    for i, original in enumerate(lines[:8]):
        line = clean_company_line(original)
        if not (3 <= len(line) <= 90):
            continue
        if NON_COMPANY.search(line) or DATE_LIKE.search(line) or COMPANY_POSTCODE.search(line):
            continue
        if sum(char.isalpha() for char in line) < 3:
            continue
        low = line.lower()
        score = 0.0
        if any(hint in low for hint in COMPANY_HINTS):
            score += 2.5
        tokens = re.findall(r"[A-Za-z]{2,}", line)
        if len(tokens) >= 2:
            score += 0.8
        score += max(0.0, 0.7 - 0.12 * i)
        if any(hint in low for hint in ADDRESS_HINTS):
            score -= 2.0
        if re.search(r"\b(rm|qty|amount|price|total)\b", low):
            score -= 1.5
        candidates.append((score, -i, line))
    if not candidates:
        return None
    candidates.sort(reverse=True)
    return candidates[0][2]


def extract_improved(ocr_text: str) -> dict:
    lines = _get_lines(ocr_text)
    base_company, company_idx = _find_company_base(lines)

    clean_lines = [
        clean_company_line(line)
        for line in str(ocr_text or "").replace("\x0c", "\n").splitlines()
        if clean_company_line(line)
    ]
    company = company_candidate(clean_lines) or base_company

    return {
        "company": company if company else None,
        "date": _find_date(lines),
        "address": _find_address(lines, company_idx),
        "total": _find_total(lines),
    }
>>>>>>> 1e8c6cb (htna)

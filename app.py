import streamlit as st
import math
import base64
from pathlib import Path

st.set_page_config(page_title="MEKA | تخمین قیمت ۲۰۶", page_icon="🚘", layout="wide", initial_sidebar_state="collapsed")
ROOT=Path(__file__).parent

TRIMS = {
    "تیپ ۱": {"engine":"TU3 • 1.4L","gear":"دستی","base":430,"years":(1380,1381),"body":"هاچ‌بک"},
    "تیپ ۲": {"engine":"TU3 • 1.4L","gear":"دستی","base":590,"years":(1381,1401),"body":"هاچ‌بک"},
    "تیپ ۳": {"engine":"TU3 • 1.4L","gear":"دستی","base":570,"years":(1382,1390),"body":"هاچ‌بک"},
    "تیپ ۳ پانوراما": {"engine":"TU3 • 1.4L","gear":"دستی","base":800,"years":(1401,1402),"body":"هاچ‌بک"},
    "تیپ ۴": {"engine":"TU5 • 1.6L","gear":"اتوماتیک","base":640,"years":(1381,1382),"body":"هاچ‌بک"},
    "تیپ ۵": {"engine":"TU5 • 1.6L","gear":"دستی","base":750,"years":(1382,1400),"body":"هاچ‌بک"},
    "تیپ ۶": {"engine":"TU5 • 1.6L","gear":"اتوماتیک","base":740,"years":(1383,1391),"body":"هاچ‌بک"},
    "SD V8": {"engine":"TU5 • 1.6L","gear":"دستی","base":790,"years":(1385,1400),"body":"صندوقدار"},
    "SD V9": {"engine":"TU5 • 1.6L","gear":"اتوماتیک","base":800,"years":(1385,1391),"body":"صندوقدار"},
    "SD V20": {"engine":"TU3 • 1.4L","gear":"دستی","base":580,"years":(1386,1392),"body":"صندوقدار"},
}
# All base values are deliberately illustrative, NOT live market observations.
COLORS={"سفید":"#f2f4f7","نقره‌ای":"#adb8c5","مشکی":"#263143","خاکستری":"#697887","قرمز":"#e64b52","آبی":"#427cc6"}
def car_svg(color="#f2f4f7", sedan=False):
    rear = '<path d="M560 132 L627 149 L653 181 L560 181 Z" fill="#25354a"/>' if sedan else ''
    roof = 'M212 165 Q248 102 340 99 L488 99 Q548 104 576 166' if sedan else 'M195 168 Q230 105 324 101 L468 101 Q529 108 560 168'
    trunk = 'L642 169 Q675 171 679 192' if sedan else 'L583 169 Q615 171 632 193'
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 760 340" role="img" aria-label="تصویر شماتیک پژو ۲۰۶">
    <defs><linearGradient id="paint" x1="0" y1="0" x2="0.1" y2="1"><stop stop-color="{color}"/><stop offset="1" stop-color="#78879a"/></linearGradient>
    <filter id="sh"><feGaussianBlur stdDeviation="12"/></filter></defs>
    <ellipse cx="390" cy="276" rx="275" ry="21" fill="#0b1627" opacity=".3" filter="url(#sh)"/>
    <path d="M94 203 Q102 178 167 170 L195 168 {roof.replace("M","L",1)} {trunk} L682 223 Q680 249 653 253 L121 253 Q84 248 86 226 Z" fill="url(#paint)" stroke="#c3ceda" stroke-width="3"/>
    <path d="{roof} L539 169 L200 169 Z" fill="#253a50" stroke="#a5b4c4" stroke-width="4"/>
    <path d="M339 102 L345 168 M486 102 L523 168" stroke="#aab9c9" stroke-width="7"/>
    {rear}
    <path d="M123 195 L157 184 L163 203 L111 211 Z" fill="#f7f8ed"/><path d="M613 194 L647 200 L657 212 L616 211 Z" fill="#d64a55"/>
    <path d="M177 228 L579 228" stroke="#233346" stroke-width="3" opacity=".45"/>
    <circle cx="207" cy="252" r="46" fill="#101722"/><circle cx="207" cy="252" r="28" fill="#bfc8d3"/><circle cx="207" cy="252" r="12" fill="#6e7b89"/>
    <circle cx="576" cy="252" r="46" fill="#101722"/><circle cx="576" cy="252" r="28" fill="#bfc8d3"/><circle cx="576" cy="252" r="12" fill="#6e7b89"/>
    <path d="M359 188 L396 188" stroke="#dce3ea" stroke-width="6" stroke-linecap="round"/>
    </svg>"""

st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=Vazirmatn:wght@400;500;600;700;800;900&display=swap');
html,body,[class*="css"],[data-testid="stApp"] {font-family:'Vazirmatn',sans-serif!important;direction:rtl}
.stApp {background:radial-gradient(circle at 15% 0%,#182b40 0,#0a1322 42%,#080e19 100%);color:#eef5fc}
.block-container {max-width:1240px;padding-top:1.5rem;padding-bottom:4rem}
header[data-testid="stHeader"] {background:transparent}
[data-testid="stSidebar"]{direction:rtl}
h1,h2,h3,p,span,label {font-family:'Vazirmatn',sans-serif!important}
.hero {background:linear-gradient(115deg,#142e40,#10202e 58%,#0b1624);border:1px solid #274454;border-radius:28px;padding:34px 38px;margin-bottom:22px;overflow:hidden}
.eyebrow{color:#55e5c1;font-size:13px;font-weight:800;letter-spacing:1px}
.hero h1{font-size:44px;font-weight:900;color:white;margin:12px 0}
.hero p{color:#afc4d2;font-size:16px;line-height:2}
.panel{background:#111e2d;border:1px solid #26394b;border-radius:24px;padding:23px;margin:8px 0 22px}
.stButton>button[kind="primary"]{background:#4de0b5;color:#06251e;border:0;font-weight:900;border-radius:13px;min-height:52px}
.stButton>button{border-radius:13px;min-height:44px;font-family:'Vazirmatn',sans-serif}
[data-baseweb="select"]>div,[data-testid="stNumberInput"] input,[data-testid="stTextInput"] input {background:#182a3b!important;border-color:#30485a!important;color:white!important;border-radius:12px!important}
[data-testid="stMetric"]{background:#15283a;border:1px solid #2d4555;border-radius:16px;padding:17px}
[data-testid="stMetricValue"]{color:#5be9c4}
hr{border-color:#2b4250}
.muted{color:#9eb3c4;font-size:13px}
.pill{display:inline-block;background:#183d3b;color:#67e5c5;padding:7px 14px;border-radius:99px;font-size:12px;font-weight:800;margin:5px 0}
.result{background:linear-gradient(120deg,#173e3c,#123035);border:1px solid #3a9b85;border-radius:24px;padding:24px;margin-top:20px}
.result h2{color:#64f1c9;margin:6px 0}
.meka-topbar{display:flex;justify-content:flex-start;direction:ltr;align-items:center;margin:-4px 0 14px;width:100%}
.meka-topbar img{display:block;width:245px;max-width:65vw;height:auto;object-fit:contain;object-position:left center;filter:drop-shadow(0 2px 10px rgba(74,201,255,.12))}
@media(max-width:600px){.meka-topbar img{width:190px}.hero h1{font-size:32px}}
</style>""",unsafe_allow_html=True)

# Left-aligned MEKA anime brand mark (bundled locally; no external image requests).
logo_bytes = (ROOT / "assets" / "meka_gojo_logo.png").read_bytes()
logo_b64 = base64.b64encode(logo_bytes).decode("ascii")
st.markdown(f"""<div class="meka-topbar"><img src="data:image/png;base64,{logo_b64}" alt="MEKA anime logo" /></div>""", unsafe_allow_html=True)

st.markdown('<div class="hero"><div class="eyebrow">206 STUDIO  /  SMART VALUATION</div><h1>۲۰۶ تو چقدر می‌ارزه؟</h1><p>تیپ خودروت رو انتخاب کن، جزئیاتش رو بگو و در چند ثانیه<br>یک برآورد آزمایشی و شفاف از ارزش خودرو بگیر.</p><span class="pill">✦ طراحی اختصاصی برای خانواده پژو ۲۰۶</span></div>',unsafe_allow_html=True)
st.warning("نسخه نمایشی: قیمت‌های پایه و ضرایب این برنامه فرضی‌اند و به داده زنده بازار متصل نیستند. برای خرید و فروش واقعی قابل استناد نیستند.",icon="⚠️")

st.subheader("۰۱ / تیپ ۲۰۶ خودت رو انتخاب کن")
trim=st.selectbox("تیپ خودرو",list(TRIMS),index=5)
data=TRIMS[trim]
left,right=st.columns([1.2,1],gap="large")
with left:
    st.markdown('<div class="panel">',unsafe_allow_html=True)
    st.markdown(car_svg("#e2e9ef",data["body"]=="صندوقدار"),unsafe_allow_html=True)
    st.markdown(f"### پژو ۲۰۶ {trim}")
    st.caption(f'{data["body"]}  •  موتور {data["engine"]}  •  گیربکس {data["gear"]}')
    st.markdown('</div>',unsafe_allow_html=True)
with right:
    st.markdown("### ۰۲ / مشخصات خودرو")
    year=st.selectbox("سال ساخت",list(range(data["years"][1],data["years"][0]-1,-1)))
    mileage=st.number_input("کارکرد (کیلومتر)",min_value=0,max_value=900000,value=85000,step=5000)
    color=st.selectbox("رنگ بدنه",list(COLORS))
    city=st.selectbox("شهر",["تهران","کرج","اصفهان","مشهد","شیراز","تبریز","سایر شهرها"])
st.markdown("### ۰۳ / وضعیت فنی و بدنه")
a,b,c=st.columns(3)
with a:
    body=st.selectbox("وضعیت رنگ و بدنه",["بی‌رنگ","یک لکه رنگ","دو تا سه لکه رنگ","چند لکه رنگ","رنگ کامل","تعویض قطعه"])
with b:
    chassis=st.selectbox("شاسی و ستون",["سالم","ضربه جزئی","آسیب جدی"])
with c:
    engine=st.selectbox("وضعیت موتور و گیربکس",["عالی","سالم","نیازمند تعمیر","تعمیر اساسی"])
d,e=st.columns(2)
with d:
    ownership=st.selectbox("تعداد مالکان قبلی",["یک مالک","دو مالک","سه مالک یا بیشتر"])
with e:
    insurance=st.slider("ماه باقی‌مانده بیمه شخص ثالث",0,12,7)
notes=st.text_area("توضیحات اختیاری",placeholder="مثلاً: لاستیک‌ها نو هستند، سرویس‌ها منظم انجام شده‌اند...",height=85)
st.caption("توضیحات فعلاً در مدل قیمت‌گذاری پردازش نمی‌شوند؛ برای توسعه نسخه بعدی نگهداری می‌شوند.")

def estimate():
    # Demonstration-only deterministic heuristic; base references year 1400.
    value=float(data["base"])
    value*=1+(year-1400)*0.047
    value*=max(0.68,1-max(0,mileage-50000)*0.00000075)
    value*={"بی‌رنگ":1,"یک لکه رنگ":.965,"دو تا سه لکه رنگ":.92,"چند لکه رنگ":.86,"رنگ کامل":.79,"تعویض قطعه":.81}[body]
    value*={"سالم":1,"ضربه جزئی":.91,"آسیب جدی":.72}[chassis]
    value*={"عالی":1.025,"سالم":1,"نیازمند تعمیر":.88,"تعمیر اساسی":.80}[engine]
    value*={"یک مالک":1.015,"دو مالک":1,"سه مالک یا بیشتر":.98}[ownership]
    value*=1+(insurance-6)*0.001
    return max(80,value)

if st.button("✨ محاسبه تخمین قیمت خودرو",type="primary",use_container_width=True):
    value=estimate()
    low,high=value*.94,value*1.06
    st.session_state["result"]=(trim,year,mileage,color,city,body,chassis,engine,low,high,value)
if "result" in st.session_state:
    r=st.session_state["result"]
    st.markdown(f'<div class="result"><div class="eyebrow">ESTIMATED VALUE • DEMO</div><h2>{r[8]:,.0f} تا {r[9]:,.0f} میلیون تومان</h2><p>برآورد میانی: <b>{r[10]:,.0f} میلیون تومان</b></p><p class="muted">این عدد صرفاً خروجی یک فرمول نمونه است؛ نه قیمت بازار یا پیشنهاد خرید.</p></div>',unsafe_allow_html=True)
    st.caption(f"مبنای محاسبه: ۲۰۶ {r[0]} | سال {r[1]} | {r[2]:,} کیلومتر | {r[4]} | بدنه: {r[5]} | شاسی: {r[6]} | فنی: {r[7]}")
    st.info("برای قیمت‌گذاری معتبر باید داده معاملات واقعی، تاریخ به‌روزرسانی، منطقه و نتایج کارشناسی به مدل اضافه شود.")
st.markdown("---")
st.caption("206 Studio • Prototype v1.0 | مستقل از خودرو۴۵ و بدون وابستگی تجاری به آن")

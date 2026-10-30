import streamlit as st
import requests, base64, html, math
from datetime import date

st.set_page_config(page_title='MEKA 206 | تخمین هوشمند', page_icon='🚙', layout='centered', initial_sidebar_state='collapsed')

TRIMS = {
 'تیپ ۱': ('TU3 · دنده‌ای', 'هاچ‌بک', 1380, 1381),
 'تیپ ۲': ('TU3 · دنده‌ای', 'هاچ‌بک', 1381, 1401),
 'تیپ ۳': ('TU3 · دنده‌ای', 'هاچ‌بک', 1382, 1390),
 'تیپ ۴': ('TU5 · اتوماتیک', 'هاچ‌بک', 1381, 1382),
 'تیپ ۵': ('TU5 · دنده‌ای', 'هاچ‌بک', 1382, 1399),
 'تیپ ۶': ('TU5 · اتوماتیک', 'هاچ‌بک', 1383, 1391),
 'تیپ ۳ پانوراما': ('TU3 · سقف شیشه‌ای', 'هاچ‌بک', 1401, 1402),
 'SD V8': ('TU5 · دنده‌ای', 'صندوق‌دار', 1385, 1400),
 'SD V9': ('TU5 · اتوماتیک', 'صندوق‌دار', 1386, 1391),
 'SD V20': ('TU3 · دنده‌ای', 'صندوق‌دار', 1386, 1391),
}
# Photos are representative 206 body styles, not certified photos of each trim.
PHOTOS = {
 'هاچ‌بک': 'Peugeot 206 - white - Taleghani blv - Nishapur.JPG',
 'صندوق‌دار': 'Peugeot 206 SD 01 2023-06-29.jpg',
}
STEPS = ['مدل خودرو', 'سال و مشخصات', 'کارکرد', 'رنگ و ظاهر', 'بدنه و رنگ‌شدگی', 'تصادف و شاسی', 'وضعیت فنی', 'بیمه و مدارک', 'قیمت و نتیجه']
DEFAULTS = dict(step=0, trim='تیپ ۲', year=1398, mileage=85000, color='سفید', exterior='تمیز و سالم', paint='بدون رنگ', painted_panels=0, accident='بدون تصادف', chassis='سالم', engine='سالم', gearbox='سالم', suspension='سالم', tires='خوب', service='منظم', insurance=8, inspection='معتبر', ownership='سند آماده انتقال', options=[], baseline=0)
for k,v in DEFAULTS.items():
    if k not in st.session_state: st.session_state[k]=v

st.markdown('''<style>
@import url('https://fonts.googleapis.com/css2?family=Vazirmatn:wght@400;500;600;700;800;900&display=swap');
html,body,[class*="css"],.stApp,button,input,textarea {font-family:Vazirmatn,Tahoma,sans-serif!important}
.stApp{background:radial-gradient(ellipse at 12% 0%,#d5fff1 0%,#f4fffc 38%,#f7f8ff 100%);color:#183d40}
.block-container{max-width:820px;padding-top:1.3rem;padding-bottom:5rem}
header[data-testid="stHeader"]{background:transparent}
#MainMenu,footer{visibility:hidden}
.meka-hero{direction:rtl;border-radius:28px;padding:27px 24px;background:linear-gradient(128deg,#093d42,#116e72 57%,#30bba5);color:white;box-shadow:0 18px 45px #0c70602a;margin-bottom:18px;position:relative;overflow:hidden}
.meka-hero:after{content:'✦';position:absolute;font-size:140px;opacity:.09;left:4%;top:-45px}
.brand{font-size:30px;font-weight:900;letter-spacing:1px;direction:ltr;text-align:left;color:#adffe7}
.hero-title{font-size:25px;font-weight:900;margin:9px 0}.hero-sub{font-size:13px;color:#d8fff5;line-height:2}
.stepbox{direction:rtl;background:#ffffffd9;border:1px solid #cdece7;border-radius:20px;padding:17px 20px;margin:12px 0 22px;box-shadow:0 5px 22px #234b4710}
.stProgress>div>div>div{background:linear-gradient(90deg,#7257ee,#45b7ff,#50dbb5)!important}
.stButton>button[kind="primary"],.stFormSubmitButton>button[kind="primary"]{background:linear-gradient(100deg,#7458ed,#3b8ff0)!important;color:white!important;border:0!important;border-radius:15px!important;font-weight:800!important;min-height:49px;box-shadow:0 7px 17px #6359df35}
.stButton>button[kind="secondary"]{border:1px solid #c4dbd9!important;background:white!important;border-radius:15px!important;min-height:49px;color:#23515a!important}
.stButton>button:hover{transform:translateY(-1px)}
[data-testid="stVerticalBlockBorderWrapper"]{border-color:#d4e9e5!important;border-radius:20px!important;background:#ffffffdb!important;box-shadow:0 5px 18px #1e54510b}
[data-testid="stWidgetLabel"] p{font-weight:700!important;color:#1b4a50!important;direction:rtl;text-align:right}
.stRadio>div{direction:rtl;gap:10px}.stRadio label{border:1px solid #dce9eb;border-radius:13px;padding:8px 12px;background:white}
.stSelectbox,.stNumberInput,.stMultiSelect,.stSlider{direction:rtl}
.stAlert{direction:rtl;border-radius:14px}
[data-testid="stMetric"]{background:white;border-radius:16px;padding:13px;border:1px solid #d4e9e5;direction:rtl}
.photo-caption{font-size:11px;color:#577c7e;text-align:right;direction:rtl}
.smallnote{direction:rtl;color:#67858a;font-size:12px;line-height:2}
.result{direction:rtl;background:linear-gradient(135deg,#163e4a,#225a6a);color:white;padding:24px;border-radius:25px;text-align:center}
.result strong{display:block;font-size:30px;color:#9dffe1;margin:13px 0}
@media(max-width:650px){.block-container{padding-left:1rem;padding-right:1rem}.meka-hero{padding:21px 18px}.hero-title{font-size:21px}}
</style>''', unsafe_allow_html=True)

@st.cache_data(ttl=86400,show_spinner=False)
def get_photo(kind):
    # Commons API returns a thumbnail with a source attribution URL.
    filename=PHOTOS[kind]
    try:
        response=requests.get('https://commons.wikimedia.org/w/api.php',params={'action':'query','format':'json','prop':'imageinfo','iiprop':'url','iiurlwidth':680,'titles':'File:'+filename},headers={'User-Agent':'MEKA206EducationalPrototype/1.0 (streamlit app; contact via github)'},timeout=7)
        response.raise_for_status()
        pages=response.json()['query']['pages']
        info=next(iter(pages.values()))['imageinfo'][0]
        return info.get('thumburl',info['url'])
    except Exception:
        return None

def photo(kind):
    url=get_photo(kind)
    if url:
        st.image(url,use_container_width=True)
    else:
        st.markdown('<div style="height:135px;border-radius:15px;background:linear-gradient(130deg,#d9fef1,#dfe6ff);display:grid;place-items:center;font-size:60px">🚙</div>',unsafe_allow_html=True)

def field_radio(label,key,options):
    st.radio(label,options,key=key,horizontal=False)

def next_step():
    st.session_state.step=min(8,st.session_state.step+1)
    st.rerun()
def prev_step():
    st.session_state.step=max(0,st.session_state.step-1)
    st.rerun()

st.markdown('''<div class="meka-hero"><div class="brand">✦ MEKA 206</div><div class="hero-title">ارزیابی هوشمند پژو ۲۰۶ 🚙</div><div class="hero-sub">از انتخاب تیپ تا بررسی فنی؛ همه‌چیز مرحله‌به‌مرحله، ساده و دقیق‌تر.</div></div>''',unsafe_allow_html=True)
step=st.session_state.step
st.markdown(f'<div class="stepbox"><b>مرحله {step+1} از {len(STEPS)} · {STEPS[step]}</b><div class="smallnote">اطلاعات هر مرحله ذخیره می‌شود و می‌توانید به مراحل قبل برگردید.</div></div>',unsafe_allow_html=True)
st.progress((step+1)/len(STEPS))
st.write('')

if step==0:
    st.markdown('### 🚘 تیپ خودروی شما کدام است؟')
    st.caption('تصاویر نماینده نوع بدنه هستند؛ تیپ‌ها از نظر ظاهری اغلب مشابه‌اند.')
    names=list(TRIMS)
    for i in range(0,len(names),2):
        cols=st.columns(2)
        for j,col in enumerate(cols):
            if i+j>=len(names): continue
            name=names[i+j]
            spec,kind,first,last=TRIMS[name]
            with col:
                with st.container(border=True):
                    photo(kind)
                    st.markdown(f'**پژو ۲۰۶ {name}**')
                    st.caption(f'{spec} · {kind}')
                    if st.button('✓ انتخاب شده' if st.session_state.trim==name else 'انتخاب این مدل',key=f'trim_{i+j}',use_container_width=True,type='primary' if st.session_state.trim==name else 'secondary'):
                        st.session_state.trim=name
                        st.session_state.year=min(max(st.session_state.year,first),last)
                        st.rerun()
    st.info('برای تیپ‌های کمیاب یا خاص، بازه سال تولید تقریبی است؛ سال دقیق خودرو را از کارت خودرو وارد کنید.')

elif step==1:
    st.markdown('### 📅 سال ساخت و جزئیات خودرو')
    spec,kind,first,last=TRIMS[st.session_state.trim]
    st.success(f'مدل انتخابی: پژو ۲۰۶ {st.session_state.trim} | {spec}')
    st.selectbox('سال ساخت (شمسی)',list(range(last,first-1,-1)),key='year')
    st.radio('نوع سوخت', ['بنزین'],index=0,disabled=True)
    st.caption('تیپ و گیربکس بر اساس انتخاب مرحله قبل تعیین شده‌اند.')

elif step==2:
    st.markdown('### 🛣️ کارکرد خودرو')
    st.number_input('کیلومتر کارکرد واقعی',min_value=0,max_value=1000000,step=5000,key='mileage',help='عدد کیلومترشمار را وارد کنید؛ اگر تعویض شده، کارکرد واقعی را برآورد کنید.')
    age=max(1,1405-st.session_state.year)
    st.info(f'میانگین کارکرد سالانه این خودرو: حدود {st.session_state.mileage/age:,.0f} کیلومتر (بر اساس سال ۱۴۰۵).')

elif step==3:
    st.markdown('### 🎨 رنگ و وضعیت ظاهری')
    st.selectbox('رنگ بدنه',['سفید','مشکی','نقره‌ای','خاکستری','نوک‌مدادی','قرمز','آبی','سبز','بژ','سایر'],key='color')
    field_radio('وضعیت ظاهری و کابین','exterior',['در حد نو','تمیز و سالم','خط‌وخش جزئی','فرسودگی محسوس'])

elif step==4:
    st.markdown('### 🧰 وضعیت رنگ و بدنه')
    field_radio('رنگ‌شدگی بدنه','paint',['بدون رنگ','لیسه‌گیری / لکه‌گیری','یک قطعه رنگ','دو تا سه قطعه رنگ','بیش از سه قطعه رنگ','دور رنگ','تعویض قطعه بدنه'])
    if st.session_state.paint in ['یک قطعه رنگ','دو تا سه قطعه رنگ','بیش از سه قطعه رنگ','دور رنگ','تعویض قطعه بدنه']:
        st.multiselect('قسمت‌های آسیب‌دیده یا رنگ‌شده (در صورت اطلاع)',['گلگیر جلو راست','گلگیر جلو چپ','درب جلو راست','درب جلو چپ','درب عقب راست','درب عقب چپ','گلگیر عقب راست','گلگیر عقب چپ','کاپوت','سقف','درب صندوق','سپرها'],key='painted_parts')
    st.warning('برای تشخیص رنگ و تعویض قطعه، کارشناسی حضوری معتبرتر از خوداظهاری است.')

elif step==5:
    st.markdown('### 🛡️ تصادف و سلامت سازه')
    field_radio('سابقه تصادف','accident',['بدون تصادف','تصادف جزئی','تصادف متوسط','تصادف شدید'])
    field_radio('شاسی، ستون‌ها و سقف','chassis',['سالم','ضربه جزئی و تعمیرشده','آسیب ساختاری / تعویض'])
    st.warning('آسیب شاسی یا ستون‌ها اثر قابل‌توجهی بر ارزش و ایمنی خودرو دارد.')

elif step==6:
    st.markdown('### 🔧 سلامت فنی و مصرفی‌ها')
    for label,key in [('موتور و روغن‌سوزی','engine'),('گیربکس و کلاچ','gearbox'),('جلوبندی و تعلیق','suspension')]:
        st.selectbox(label,['سالم','نیازمند سرویس جزئی','نیازمند تعمیر اساسی'],key=key)
    st.selectbox('وضعیت لاستیک‌ها',['عالی','خوب','متوسط','نیازمند تعویض'],key='tires')
    st.selectbox('سابقه سرویس و نگهداری',['منظم','نامشخص','نامنظم'],key='service')
    st.multiselect('امکانات یا تغییرات خودرو (اختیاری)',['رینگ اسپرت','مانیتور','دوربین عقب','سنسور پارک','سیستم صوتی ارتقایافته','سانروف غیرفابریک','گازسوز غیرفابریک','تغییرات موتور'],key='options')

elif step==7:
    st.markdown('### 📑 بیمه، معاینه فنی و سند')
    st.slider('ماه‌های باقی‌مانده بیمه شخص ثالث',0,12,key='insurance')
    st.selectbox('معاینه فنی',['معتبر','منقضی','نیاز ندارد / نامشخص'],key='inspection')
    st.selectbox('وضعیت سند و انتقال',['سند آماده انتقال','در رهن / نیازمند فک رهن','دارای مشکل حقوقی یا محدودیت انتقال'],key='ownership')
    st.info('برای تصمیم نهایی خرید، استعلام خلافی، اصالت مدارک و وضعیت حقوقی ضروری است.')

elif step==8:
    st.markdown('### ✨ نتیجه ارزیابی MEKA')
    st.info('این نسخه به قیمت‌های لحظه‌ای بازار متصل نیست. برای جلوگیری از اعلام قیمت غیرواقعی، ابتدا قیمت مبنای یک خودروی مشابه و سالم را وارد کنید.')
    st.number_input('قیمت مبنا برای خودروی مشابه، سالم و با کارکرد متعارف (تومان)',min_value=0,max_value=10000000000,step=10000000,key='baseline',format='%d',help='از چند آگهی و معامله معتبر برای همین تیپ و سال استفاده کنید؛ این عدد را خودتان وارد می‌کنید.')
    year=st.session_state.year
    age=max(1,1405-year)
    expected=age*15000
    # Transparent heuristic adjustments, not market-trained coefficients.
    mileage_delta=max(-0.12,min(0.08,(expected-st.session_state.mileage)/10000*0.006))
    paint_adj={'بدون رنگ':0,'لیسه‌گیری / لکه‌گیری':-.015,'یک قطعه رنگ':-.035,'دو تا سه قطعه رنگ':-.07,'بیش از سه قطعه رنگ':-.11,'دور رنگ':-.16,'تعویض قطعه بدنه':-.12}[st.session_state.paint]
    accident_adj={'بدون تصادف':0,'تصادف جزئی':-.025,'تصادف متوسط':-.075,'تصادف شدید':-.16}[st.session_state.accident]
    chassis_adj={'سالم':0,'ضربه جزئی و تعمیرشده':-.09,'آسیب ساختاری / تعویض':-.23}[st.session_state.chassis]
    exterior_adj={'در حد نو':.025,'تمیز و سالم':0,'خط‌وخش جزئی':-.015,'فرسودگی محسوس':-.045}[st.session_state.exterior]
    tech_adj=sum({'سالم':0,'نیازمند سرویس جزئی':-.025,'نیازمند تعمیر اساسی':-.09}[st.session_state[k]] for k in ['engine','gearbox','suspension'])
    tires_adj={'عالی':.008,'خوب':0,'متوسط':-.008,'نیازمند تعویض':-.018}[st.session_state.tires]
    service_adj={'منظم':.005,'نامشخص':0,'نامنظم':-.02}[st.session_state.service]
    legal_adj={'سند آماده انتقال':0,'در رهن / نیازمند فک رهن':-.025,'دارای مشکل حقوقی یا محدودیت انتقال':-.12}[st.session_state.ownership]
    total=max(-.65,min(.15,mileage_delta+paint_adj+accident_adj+chassis_adj+exterior_adj+tech_adj+tires_adj+service_adj+legal_adj))
    baseline=st.session_state.baseline
    if baseline:
        mid=round(baseline*(1+total)/1000000)*1000000
        low=round(mid*.94/1000000)*1000000
        high=round(mid*1.06/1000000)*1000000
        st.markdown(f'<div class="result">برآورد آزمایشی قیمت خودرو<strong>{mid:,} تومان</strong>بازه سناریویی: {low:,} تا {high:,} تومان</div>',unsafe_allow_html=True)
        st.caption(f'تعدیل مدل آزمایشی نسبت به قیمت مبنا: {total*100:+.1f}٪. بازه ±۶٪ صرفاً سناریوی نمایشی است، نه فاصله اطمینان آماری.')
    else:
        st.warning('برای محاسبه، قیمت مبنای واقعی یک خودروی مشابه را وارد کنید.')
    with st.expander('🔎 خلاصه اطلاعات واردشده',expanded=True):
        rows=[('مدل',f'۲۰۶ {st.session_state.trim}'),('سال',str(year)),('کارکرد',f'{st.session_state.mileage:,} کیلومتر'),('رنگ',st.session_state.color),('بدنه',st.session_state.paint),('تصادف',st.session_state.accident),('شاسی',st.session_state.chassis),('موتور',st.session_state.engine),('گیربکس',st.session_state.gearbox),('بیمه',f'{st.session_state.insurance} ماه'),('مدارک',st.session_state.ownership)]
        for k,v in rows: st.markdown(f'**{k}:** {v}')
    if st.button('🔄 شروع ارزیابی جدید',use_container_width=True):
        for k in DEFAULTS: st.session_state[k]=DEFAULTS[k]
        st.rerun()

st.write('')
back,forward=st.columns([1,2])
with back:
    st.button('→ قبلی',disabled=step==0,on_click=prev_step,use_container_width=True)
with forward:
    if step<8: st.button('ادامه مرحله بعد ←',type='primary',on_click=next_step,use_container_width=True)
    else: st.button('✓ تکمیل ارزیابی',type='primary',disabled=True,use_container_width=True)
st.markdown('<div class="smallnote" style="text-align:center;margin-top:20px">MEKA 206 • نمونه آموزشی مستقل • تصاویر: Wikimedia Commons • برآورد قیمت، کارشناسی رسمی یا پیشنهاد خرید و فروش نیست.</div>',unsafe_allow_html=True)

import streamlit as st
import random
from datetime import datetime
from korean_lunar_calendar import KoreanLunarCalendar

# ============================================================================
# [1] 시스템 설정 & 디자인 (모바일 최적화)
# ============================================================================
st.set_page_config(layout="wide", page_title="천기누설 대만신", initial_sidebar_state="collapsed")

# 폰트 및 디자인 설정 (전통적인 느낌 + 모바일 가독성)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Nanum+Myeongjo:wght@400;700;800&display=swap');
    * {font-family: 'Nanum Myeongjo', serif !important;}
    
    /* 모바일 헤더 */
    h1 {font-size: 28px !important; font-weight: 800; color: #111; text-align: center; margin-bottom: 10px;}
    
    /* 입력폼 박스 디자인 */
    .stForm {background-color: #fcfcfc; padding: 15px; border-radius: 15px; border: 1px solid #ddd; box-shadow: 0 2px 5px rgba(0,0,0,0.05);}
    
    /* 버튼 디자인 (빨간색) */
    div.stButton > button {
        width: 100%; 
        background-color: #d32f2f; 
        color: white; 
        font-weight: bold; 
        font-size: 18px;
        padding: 12px; 
        border-radius: 12px;
        border: none;
    }
    div.stButton > button:hover {background-color: #b71c1c; color: white;}
    
    /* 결과 카드 디자인 */
    .result-card {
        background-color: #fff;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #d32f2f;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        margin-bottom: 15px;
    }
    </style>
""", unsafe_allow_html=True)

# ============================================================================
# [2] 데이터베이스 & 로직
# ============================================================================
TOPICS = [
    "🔮 종합/평생 총운", "🌅 2026년 신년 운세", "💰 금전/재물/횡재운", "🏢 직장/승진/명예운",
    "❤️ 짝사랑/썸/연애운", "👩‍❤️‍👨 궁합/애정/권태기", "💍 결혼/재혼/배우자복", 
    "🏥 건강/질병/사고수", "🏘️ 부동산/매매/문서운"
]
STEMS = {'갑':'甲','을':'乙','병':'丙','정':'丁','무':'戊','기':'己','경':'庚','신':'辛','임':'壬','계':'癸'}
BRANCHES = {'자':'子','축':'丑','인':'寅','묘':'卯','진':'辰','사':'巳','오':'午','미':'未','신':'申','유':'酉','술':'戌','해':'亥'}
Z_TIME = ["자시(23:30~01:29)","축시(01:30~03:29)","인시(03:30~05:29)","묘시(05:30~07:29)","진시(07:30~09:29)","사시(09:30~11:29)","오시(11:30~13:29)","미시(13:30~15:29)","신시(15:30~17:29)","유시(17:30~19:29)","술시(19:30~21:29)","해시(21:30~23:29)"]

def calculate_saju(y, m, d, lunar, yundal, t_idx):
    try:
        cal = KoreanLunarCalendar()
        if lunar:
            if not cal.setLunarDate(y, m, d, yundal): return None, None, "음력 날짜 오류"
            solar = datetime(cal.solarYear, cal.solarMonth, cal.solarDay)
        else:
            try: solar = datetime(y, m, d)
            except: return None, None, "양력 날짜 오류"
            cal.setSolarDate(solar.year, solar.month, solar.day)
        
        raw = cal.getGapJaString().replace('년','').replace('월','').replace('일','').split()
        pillars = []
        for p in raw:
            g = STEMS.get(p[0], "甲")
            j = BRANCHES.get(p[1], "子")
            pillars.append(g+j)
        
        # 시주 계산 (간단 로직)
        gan_list = "甲乙丙丁戊己庚辛壬癸"
        ji_list = "子丑寅卯辰巳午未申酉戌亥"
        d_idx = gan_list.find(pillars[2][0])
        if d_idx == -1: d_idx = 0
        t_idx_calc = (d_idx % 5 * 2 + t_idx) % 10
        pillars.append(gan_list[t_idx_calc] + ji_list[t_idx])
        
        z_map = {'子':'쥐','丑':'소','寅':'호랑이','卯':'토끼','辰':'용','巳':'뱀','午':'말','未':'양','申':'원숭이','酉':'닭','戌':'개','亥':'돼지'}
        zodiac = z_map.get(pillars[0][1], '알수없음')
        
        return solar, pillars, zodiac
    except Exception as e: return None, None, str(e)

def generate_fortune_text(name, zodiac, topic):
    # 운세 멘트 생성기
    intros = [
        f"천지신명께 비나이다. {name} 님의 운세를 살피니, 짙은 안개 속에서 한 줄기 빛이 내리쬐는 형국입니다.",
        f"오래 기다리셨습니다. {name} 님의 사주에는 {zodiac}의 기운이 강하게 서려 있어, 한 번 마음먹은 일은 끝을 보는 성격입니다.",
        f"귀하의 운명 흐름을 보니, 마치 거대한 강물이 바다로 흘러가듯 이제야 비로소 제 자리를 찾아가는 시기입니다."
    ]
    
    details = {
        "재물": "지금은 씨앗을 뿌리는 시기가 아니라 거두는 시기입니다. 묶여있던 자금이 풀리고, 뜻밖의 횡재수가 보입니다. 다만, 남의 말을 듣고 투자하는 것은 금물입니다.",
        "연애": "도화살이 강하게 들어옵니다. 가만히 있어도 주변에 사람이 꼬이는 형국이나, 옥석을 잘 가려야 합니다. 스쳐가는 인연에 마음을 주지 마십시오.",
        "직장": "관운이 비추고 있습니다. 승진이나 이직 제안이 들어올 수 있으며, 윗사람의 인정을 받아 명예가 높아질 운세입니다.",
        "건강": "육체적인 피로보다 정신적인 스트레스가 문제입니다. 머리를 비우는 시간이 필요하며, 특히 소화기 계통을 조심해야 합니다."
    }
    
    selected_detail = ""
    for key, val in details.items():
        if key in topic: selected_detail = val
    if not selected_detail: selected_detail = "전반적으로 운기가 상승곡선을 그리고 있습니다. 막혔던 일들이 귀인의 도움으로 하나둘씩 풀려나갈 것입니다."
    
    return random.choice(intros), selected_detail

# ============================================================================
# [3] 메인 화면 구성
# ============================================================================
def main():
    st.title("⛩️ 천기누설 대만신")
    st.markdown("<div style='text-align: center; color: #666; font-size: 14px;'>신령님의 영험한 기운으로 당신의 운명을 점쳐드립니다.</div>", unsafe_allow_html=True)
    st.markdown("---")
    
    # 입력 폼 (화면 중앙 배치)
    with st.form("input_form"):
        col_name, col_gender = st.columns([2, 1])
        name = col_name.text_input("이름", placeholder="예: 박성우")
        gender = col_gender.selectbox("성별", ["남", "여"])
        
        c1, c2, c3 = st.columns([1.2, 1, 1])
        y = c1.number_input("생년", 1930, 2026, 1980)
        m = c2.selectbox("월", range(1, 13))
        d = c3.selectbox("일", range(1, 32))
        
        chk = st.columns(2)
        lunar = chk[0].checkbox("음력")
        yundal = chk[1].checkbox("윤달")
        
        t_str = st.selectbox("태어난 시", Z_TIME)
        topic = st.selectbox("상담 주제", TOPICS)
        
        st.markdown("<br>", unsafe_allow_html=True)
        submit = st.form_submit_button("🔥 내 운명 확인하기 (Click)")

    if submit:
        # 로딩 효과
        with st.spinner("신령님께 여쭙고 있습니다... 잠시만 기다리시게..."):
            import time
            time.sleep(1.5) # 긴장감 조성
            
            t_idx = Z_TIME.index(t_str)
            s_date, pillars, zodiac = calculate_saju(y, m, d, lunar, yundal, t_idx)
            
            if s_date is None:
                st.error("날짜가 올바르지 않습니다.")
            else:
                intro, detail = generate_fortune_text(name, zodiac, topic)
                
                # --- 결과 화면 ---
                st.markdown("---")
                st.success(f"📢 {name}님({zodiac}띠)의 {topic} 점사 결과가 나왔습니다.")
                
                # 1. 사주 팔자 표
                st.markdown("### 1. 귀하의 사주팔자(四柱八字)")
                c1, c2, c3, c4 = st.columns(4)
                titles = ["년주(조상)", "월주(부모)", "일주(나)", "시주(자식)"]
                for i in range(4):
                    with [c1,c2,c3,c4][i]:
                        st.markdown(f"<div style='background:#f8f9fa; padding:10px; border-radius:5px; text-align:center;'><b>{titles[i]}</b><br><span style='font-size:20px; color:#d32f2f;'>{pillars[i]}</span></div>", unsafe_allow_html=True)
                
                st.markdown("<br>", unsafe_allow_html=True)

                # 2. 상세 풀이
                st.markdown(f"### 2. {topic} 정밀 진단")
                st.markdown(f"""
                <div class="result-card">
                <b>[신령님의 공수]</b><br><br>
                {intro}<br><br>
                <b>[상세 풀이]</b><br>
                {detail}
                </div>
                """, unsafe_allow_html=True)
                
                # 3. 월별 운세 (랜덤 생성)
                st.markdown("### 3. 2026년 월별 흐름")
                luck_chart = []
                col_a, col_b = st.columns(2)
                for i in range(1, 13):
                    score = random.randint(50, 100)
                    star = "⭐" * (score // 20)
                    msg = f"**{i}월 ({score}점):** {star}"
                    if i <= 6: col_a.markdown(msg)
                    else: col_b.markdown(msg)

                # 4. 마무리 조언
                st.markdown("<br>", unsafe_allow_html=True)
                st.info("💡 **개운법(행운을 부르는 법):** 이번 달은 동쪽 방향이 길하며, 검은색 옷보다는 밝은색 옷을 입는 것이 기운을 북돋아 줍니다.")

if __name__ == "__main__":
    main()

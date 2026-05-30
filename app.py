import streamlit as st

st.set_page_config(page_title="마진율 계산기", layout="centered")

# 모바일 화면 극대화를 위한 울트라 초밀착 여백 및 강제 색상 지정 CSS 스타일
st.markdown("""
    <style>
    .block-container {
        padding-top: 0.4rem !important;
        padding-bottom: 0.5rem !important;
        padding-left: 0.5rem !important;
        padding-right: 0.5rem !important;
    }
    div[data-testid="stVerticalBlock"] > div {
        padding-bottom: 0.05rem !important;
        margin-bottom: 0.05rem !important;
    }
    hr {
        margin-top: 0.2rem !important;
        margin-bottom: 0.2rem !important;
    }
    h1, h2, h3, h4, h5 {
        margin-top: 0.05rem !important;
        margin-bottom: 0.08rem !important;
    }
    
    /* 📱 모바일 가로 한 줄 배치 강제 스크립트 */
    div[data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        gap: 2px !important;
        margin-bottom: 0.05rem !important;
        margin-top: 0.05rem !important;
    }
    div[data-testid="column"] {
        flex: 1 1 0% !important;
        min-width: 0 !important;
        padding-left: 1px !important;
        padding-right: 1px !important;
    }
    div[data-testid="column"] button {
        padding: 3px 1px !important;
        font-size: 10px !important;
        width: 100% !important;
    }
    div[data-testid="stRadio"] > label {
        display: none;
    }
    .stCaption {
        margin-top: 1px !important;
        margin-bottom: 1px !important;
        font-size: 11px !important;
    }

    /* 🎨 [완벽 반영] 순서 구조 기반 버튼 색상 강제 오버라이드 */
    /* 2번째 가로 블록(순수익 행)의 3번째 열 (10,000원) -> 파란색 */
    div[data-testid="stHorizontalBlock"]:nth-of-type(2) div[data-testid="column"]:nth-child(3) button {
        background-color: #1d4ed8 !important;
        color: white !important;
        font-weight: bold !important;
        border: none !important;
    }
    /* 3번째 가로 블록(마진율 행)의 3번째 열 (30%) -> 초록색 */
    div[data-testid="stHorizontalBlock"]:nth-of-type(3) div[data-testid="column"]:nth-child(3) button {
        background-color: #15803d !important;
        color: white !important;
        font-weight: bold !important;
        border: none !important;
    }
    /* 3번째 가로 블록(마진율 행)의 5번째 열 (50%) -> 빨간색 */
    div[data-testid="stHorizontalBlock"]:nth-of-type(3) div[data-testid="column"]:nth-child(5) button {
        background-color: #b91c1c !important;
        color: white !important;
        font-weight: bold !important;
        border: none !important;
    }
    
    /* 📦 [강조] 매입가격 입력창 배경색을 진하게 하고 눈에 띄게 변경 */
    div[data-testid="stTextInput"]:nth-of-type(1) input {
        background-color: #1e293b !important;
        color: #f8fafc !important;
        border: 2px solid #14b8a6 !important;
        font-weight: bold !important;
        font-size: 15px !important;
    }
    </style>
""", unsafe_allow_html=True)

# 쇼핑몰 데이터베이스 상단 선언
platform_db = {
    "스마트스토어": {"cat": 3.63, "link": 3.0, "ship": 3.63},
    "쿠팡": {"cat": 11.88, "link": 0.0, "ship": 3.3},
    "11번가": {"cat": 13.0, "link": 2.0, "ship": 3.3},
    "G마켓": {"cat": 13.0, "link": 2.0, "ship": 3.3},
    "옥션": {"cat": 13.0, "link": 2.0, "ship": 3.3},
    "기타 마켓": {"cat": 11.0, "link": 2.0, "ship": 3.3}
}

# 시스템 핵심 세션 상태 초기화
if 'selected_platform' not in st.session_state: st.session_state.selected_platform = "스마트스토어"
if 'ui_sell_price' not in st.session_state: st.session_state.ui_sell_price = "0"
if 'ui_net_profit' not in st.session_state: st.session_state.ui_net_profit = "0"
if 'ui_margin_rate' not in st.session_state: st.session_state.ui_margin_rate = 0.0
if 'last_trigger' not in st.session_state: st.session_state.last_trigger = 'price'

if 'ui_customer_shipping' not in st.session_state: st.session_state.ui_customer_shipping = "0"
if 'ui_buy_price' not in st.session_state: st.session_state.ui_buy_price = "0"
if 'ui_buy_shipping' not in st.session_state: st.session_state.ui_buy_shipping = "3,000"
if 'ui_other_cost' not in st.session_state: st.session_state.ui_other_cost = "500"
if 'ui_seller_shipping' not in st.session_state: st.session_state.ui_seller_shipping = "0"
if 'ui_ad_cost' not in st.session_state: st.session_state.ui_ad_cost = "0"
if 'prev_mode' not in st.session_state: st.session_state.prev_mode = "📦 사입 구조"

# 입력값 변환 콜백 함수들
def handle_price_change():
    raw = st.session_state.ui_sell_price.replace(",", "")
    try: val = int(raw)
    except: val = 0
    st.session_state.ui_sell_price = f"{val:,}"
    st.session_state.last_trigger = 'price'

def handle_profit_change():
    raw = st.session_state.ui_net_profit.replace(",", "")
    try: val = int(raw)
    except: val = 0
    st.session_state.ui_net_profit = f"{val:,}"
    st.session_state.last_trigger = 'profit'

def handle_margin_change():
    st.session_state.last_trigger = 'margin'

def format_generic(key):
    raw = st.session_state[key].replace(",", "")
    try: val = int(raw)
    except: val = 0
    st.session_state[key] = f"{val:,}"

st.title("📊 마진율 계산기")

# 최상단 결과 레이아웃 공간 확보
top_container = st.container()

# 2. 운영 형태 선택 탭
st.markdown("---")
col_mode1, col_mode2 = st.columns([1, 1.3])
with col_mode1:
    st.markdown("##### 📋 운영 형태 선택")
with col_mode2:
    mode = st.radio("운영 형태 선택 라디오", ["📦 사입 구조", "🚚 위탁 구조"], horizontal=True, label_visibility="collapsed")

if mode != st.session_state.prev_mode:
    if mode == "📦 사입 구조":
        st.session_state.ui_buy_shipping = "3,000"
        st.session_state.ui_other_cost = "500"
        st.session_state.last_trigger = 'price'
    else:
        st.session_state.ui_buy_shipping = "0"
        st.session_state.ui_other_cost = "0"
        st.session_state.ui_margin_rate = 30.0
        st.session_state.last_trigger = 'margin'
    st.session_state.prev_mode = mode
    st.rerun()

# 3. 배송비 및 기타 원가 설정부
st.subheader("💰 배송비 및 기타 지출 설정")
st.text_input("고객배송비 (원)", key="ui_customer_shipping", on_change=format_generic, args=("ui_customer_shipping",))
st.text_input("매입운송비 (원)", key="ui_buy_shipping", on_change=format_generic, args=("ui_buy_shipping",))
st.text_input("기타(포장, 사은품) (원)", key="ui_other_cost", on_change=format_generic, args=("ui_other_cost",))
st.text_input("판매자 택배비 (원)", key="ui_seller_shipping", on_change=format_generic, args=("ui_seller_shipping",))
st.text_input("광고비 (원)", key="ui_ad_cost", on_change=format_generic, args=("ui_ad_cost",))

# 4. 수수료 세부 설정
st.markdown("---")
st.subheader("🛒 수수료 세부 설정")
defaults = platform_db[st.session_state.selected_platform]

col_fee1, col_fee2, col_fee3 = st.columns(3)
with col_fee1: cat_rate = st.number_input("카테고리 (%)", value=defaults["cat"], step=0.1)
with col_fee2: link_rate = st.number_input("연동 (%)", value=defaults["link"], step=0.1)
with col_fee3: ship_rate = st.number_input("배송비 (%)", value=defaults["ship"], step=0.1)

vat_rate = st.number_input("부가세율 (%)", value=10, step=1)

# 데이터 파싱 및 연산 준비
def get_val(key):
    try: return int(st.session_state[key].replace(",", ""))
    except: return 0

customer_shipping = get_val("ui_customer_shipping")
buy_price = get_val("ui_buy_price")
buy_shipping = get_val("ui_buy_shipping")
other_cost = get_val("ui_other_cost")
seller_shipping = get_val("ui_seller_shipping")
ad_cost = get_val("ui_ad_cost")

total_cost = buy_price + buy_shipping + other_cost + seller_shipping + ad_cost

def price_from_profit(target_profit):
    pre_vat = target_profit * (1 + vat_rate / 100) if target_profit > 0 else target_profit
    target_settlement = pre_vat + total_cost
    fee_denom = 1 - ((cat_rate + link_rate) / 100)
    if fee_denom > 0:
        price = int((target_settlement - customer_shipping * (1 - ship_rate / 100)) / fee_denom)
        return max(0, price)
    return 0

# 5. 최상단 엔진 렌더링 구역
with top_container:
    col_head1, col_head2 = st.columns([1.3, 1])
    with col_head1: st.markdown("### 🏆 실시간 결과")
    with col_head2: st.selectbox("쇼핑몰 선택", list(platform_db.keys()), key="selected_platform", label_visibility="collapsed")
    
    # [위치 조정 완료] 매입가격이 결과창 바로 밑, 버튼 세트 바로 위로 전진 배치 및 딥네이비 커스텀 스타일링 반영
    st.text_input("📦 매입가격 [제품 원가] (원)", key="ui_buy_price", on_change=format_generic, args=("ui_buy_price",))

    # [한 줄 통합 완료] 순수익 원터치 설정 버튼 7개 가로 올인원 배열
    st.caption("💵 목표 순수익 원터치 설정")
    p_row = st.columns(7)
    profits_layout = [("5천", "5,000"), ("8천", "8,000"), ("1만", "10,000"), ("1.5만", "15,000"), ("2만", "20,000"), ("2.5만", "25,000"), ("3만", "30,000")]
    for idx, (lbl, val) in enumerate(profits_layout):
        if p_row[idx].button(lbl):
            st.session_state["ui_net_profit"] = val
            st.session_state.last_trigger = 'profit'; st.rerun()

    # [간격 정밀 수정 완료] 마진율 10개 버튼 가로 초압축 배치 및 타겟 컬러 바인딩
    st.caption("📈 목표 마진율 원터치 설정")
    m_row = st.columns(10)
    for pct in range(10, 110, 10):
        idx = (pct // 10) - 1
        if m_row[idx].button(f"{pct}%"):
            st.session_state["ui_margin_rate"] = float(pct); st.session_state.last_trigger = 'margin'; st.rerun()

    # 역산 핵심 분기문 처리
    if st.session_state.last_trigger == 'price':
        sell_price = get_val("ui_sell_price")
        total_sales = sell_price + customer_shipping
        platform_fee = (sell_price * (cat_rate + link_rate) / 100) + (customer_shipping * (ship_rate / 100))
        settlement_amount = total_sales - platform_fee
        pre_vat = settlement_amount - total_cost
        est_vat = (pre_vat / (1 + vat_rate/100) * (vat_rate/100)) if pre_vat > 0 else 0
        net_profit = int(pre_vat - est_vat)
        margin_rate = (net_profit / total_cost * 100) if total_cost > 0 else 0.0
        
        st.session_state["ui_net_profit"] = f"{net_profit:,}"
        st.session_state["ui_margin_rate"] = float(margin_rate)
        
    elif st.session_state.last_trigger == 'profit':
        net_profit = get_val("ui_net_profit")
        sell_price = price_from_profit(net_profit)
        margin_rate = (net_profit / total_cost * 100) if total_cost > 0 else 0.0
        
        st.session_state["ui_sell_price"] = f"{sell_price:,}"
        st.session_state["ui_margin_rate"] = float(margin_rate)
        
    elif st.session_state.last_trigger == 'margin':
        margin_rate = st.session_state["ui_margin_rate"]
        net_profit = int(total_cost * (margin_rate / 100))
        sell_price = price_from_profit(net_profit)
        
        st.session_state["ui_sell_price"] = f"{sell_price:,}"
        st.session_state["ui_net_profit"] = f"{net_profit:,}"

    # 판매가격, 최종순수익, 마진율 입력창 간격 조밀화 완료
    col1, col2, col3 = st.columns(3)
    with col1: st.text_input("💰 판매가격 (원)", key="ui_sell_price", on_change=handle_price_change)
    with col2: st.text_input("💸 최종 순수익 (원)", key="ui_net_profit", on_change=handle_profit_change)
    with col3: st.number_input("📈 마진율 (ROI %)", key="ui_margin_rate", step=1.0, on_change=handle_margin_change)

# 6. 하단 접이식 세부 정산서 노출
with st.expander("🔍 상세 정산 데이터 확인"):
    sell_price = get_val("ui_sell_price")
    current_fee = (sell_price * (cat_rate + link_rate) / 100) + (customer_shipping * (ship_rate / 100))
    settlement_amount = sell_price + customer_shipping - current_fee
    net_profit = get_val("ui_net_profit")
    st.write(f"• 현재 적용된 구조: {mode}")
    st.write(f"• 플랫폼 정산금액 (공제 후): {int(settlement_amount):,} 원")
    st.write(f"• 총 매입비용 (고정 원가): {int(total_cost):,} 원")
    st.write(f"• 예상 납부 부가세: {int(net_profit * (vat_rate / 100)) if net_profit > 0 else 0:,} 원")

import streamlit as st

st.set_page_config(page_title="마진율 계산기", layout="centered")

# 모바일 화면 극대화를 위한 울트라 초밀착 여백 CSS 스타일
st.markdown("""
    <style>
    .block-container {
        padding-top: 0.5rem !important;
        padding-bottom: 0.5rem !important;
        padding-left: 0.6rem !important;
        padding-right: 0.6rem !important;
    }
    div[data-testid="stVerticalBlock"] > div {
        padding-bottom: 0.1rem !important;
        margin-bottom: 0.1rem !important;
    }
    hr {
        margin-top: 0.3rem !important;
        margin-bottom: 0.3rem !important;
    }
    h1, h2, h3, h4, h5 {
        margin-top: 0.05rem !important;
        margin-bottom: 0.15rem !important;
    }
    div[data-testid="stRadio"] > label {
        display: none;
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

# 1. 시스템 핵심 세션 상태 초기화
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

# 입력값 변경 시 세자리 콤마 포맷팅 강제 적용 콜백
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

# 최상단 결과 레이아웃 공간 확보 (고정)
top_container = st.container()

# 2. 운영 형태 선택 탭 + 라디오 버튼 한 줄 결합
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

# 3. 금액 원가 입력 섹션 (매입가격 상단 이동으로 제외됨)
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

# 데이터 안전 파싱
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

# 5. 최상단 예약 구역 연산 및 렌더링 엔진
with top_container:
    col_head1, col_head2 = st.columns([1.3, 1])
    with col_head1: st.markdown("### 🏆 실시간 결과")
    with col_head2: st.selectbox("쇼핑몰 선택", list(platform_db.keys()), key="selected_platform", label_visibility="collapsed")
    
    # 순수익 간편 버튼 확장 (5k, 8k, 10k, 15k, 20k, 25k, 30k)
    st.caption("💵 목표 순수익 원터치 설정")
    p_row1 = st.columns(4)
    profits_1 = [("5,000원", "5,000"), ("8,000원", "8,000"), ("10,000원", "10,000"), ("15,000원", "15,000")]
    for i, (lbl, val) in enumerate(profits_1):
        if p_row1[i].button(lbl):
            st.session_state["ui_net_profit"] = val
            st.session_state.last_trigger = 'profit'; st.rerun()
            
    p_row2 = st.columns(4)
    profits_2 = [("20,000원", "20,000"), ("25,000원", "25,000"), ("30,000원", "30,000")]
    for i, (lbl, val) in enumerate(profits_2):
        if p_row2[i].button(lbl):
            st.session_state["ui_net_profit"] = val
            st.session_state.last_trigger = 'profit'; st.rerun()

    # 마진율 간편 버튼 확장 (10% ~ 100% 10단위 배열)
    st.caption("📈 목표 마진율 원터치 설정")
    m_row1 = st.columns(5)
    for i, pct in enumerate(range(10, 60, 10)):
        if m_row1[i].button(f"{pct}%"):
            st.session_state["ui_margin_rate"] = float(pct)
            st.session_state.last_trigger = 'margin'; st.rerun()
    m_row2 = st.columns(5)
    for i, pct in enumerate(range(60, 110, 10)):
        if m_row2[i].button(f"{pct}%"):
            st.session_state["ui_margin_rate"] = float(pct)
            st.session_state.last_trigger = 'margin'; st.rerun()

    # 역산 엔진 구동
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

    # 상단 결과 메인 인풋 필드 3열 배치
    col1, col2, col3 = st.columns(3)
    with col1: st.text_input("💰 판매가격 (원)", key="ui_sell_price", on_change=handle_price_change)
    with col2: st.text_input("💸 최종 순수익 (원)", key="ui_net_profit", on_change=handle_profit_change)
    with col3: st.number_input("📈 마진율 (ROI %)", key="ui_margin_rate", step=1.0, on_change=handle_margin_change)

    # 요청사항 반영: 매입가격을 실시간 결과창 바로 밑(최상단 컨트롤 박스 최하단)으로 이동
    st.text_input("📦 매입가격 [제품 원가] (원)", key="ui_buy_price", on_change=format_generic, args=("ui_buy_price",))
    st.markdown("---")

# 6. 하단 접이식 세부 내역 데이터
with st.expander("🔍 상세 정산 데이터 확인"):
    sell_price = get_val("ui_sell_price")
    current_fee = (sell_price * (cat_rate + link_rate) / 100) + (customer_shipping * (ship_rate / 100))
    settlement_amount = sell_price + customer_shipping - current_fee
    net_profit = get_val("ui_net_profit")
    st.write(f"• 현재 적용된 구조: {mode}")
    st.write(f"• 플랫폼 정산금액 (공제 후): {int(settlement_amount):,} 원")
    st.write(f"• 총 매입비용 (고정 원가): {int(total_cost):,} 원")
    st.write(f"• 예상 납부 부가세: {int(net_profit * (vat_rate / 100)) if net_profit > 0 else 0:,} 원")

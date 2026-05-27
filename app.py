import streamlit as st

st.set_page_config(page_title="마진율 계산기", layout="centered")

# 모바일 화면 밀착 여백 CSS
st.markdown("""
    <style>
    .block-container {
        padding-top: 0.8rem !important;
        padding-bottom: 1rem !important;
        padding-left: 0.8rem !important;
        padding-right: 0.8rem !important;
    }
    div[data-testid="stVerticalBlock"] > div {
        padding-bottom: 0.15rem !important;
        margin-bottom: 0.15rem !important;
    }
    hr {
        margin-top: 0.4rem !important;
        margin-bottom: 0.4rem !important;
    }
    h1, h2, h3, h4 {
        margin-top: 0.1rem !important;
        margin-bottom: 0.2rem !important;
    }
    </style>
""", unsafe_allow_html=True)

# 1. 시스템 핵심 세션 상태 초기화 및 실시간 콜백 선언
if 'ui_sell_price' not in st.session_state: st.session_state.ui_sell_price = "0"
if 'ui_net_profit' not in st.session_state: st.session_state.ui_net_profit = "0"
if 'ui_margin_rate' not in st.session_state: st.session_state.ui_margin_rate = 0.0
if 'last_trigger' not in st.session_state: st.session_state.last_trigger = 'price'

if 'ui_customer_shipping' not in st.session_state: st.session_state.ui_customer_shipping = "0"
if 'ui_buy_price' not in st.session_state: st.session_state.ui_buy_price = "0"
if 'ui_buy_shipping' not in st.session_state: st.session_state.ui_buy_shipping = "3,000"
if 'ui_other_cost' not in st.session_state: st.session_state.ui_other_cost = "300"
if 'ui_seller_shipping' not in st.session_state: st.session_state.ui_seller_shipping = "0"
if 'ui_ad_cost' not in st.session_state: st.session_state.ui_ad_cost = "0"

# [콜백] 사용자가 판매가격을 직접 입력했을 때
def handle_price_change():
    raw = st.session_state.ui_sell_price.replace(",", "")
    try: val = int(raw)
    except: val = 0
    st.session_state.ui_sell_price = f"{val:,}"
    st.session_state.last_trigger = 'price'

# [콜백] 사용자가 최종 순수익을 직접 입력했을 때
def handle_profit_change():
    raw = st.session_state.ui_net_profit.replace(",", "")
    try: val = int(raw)
    except: val = 0
    st.session_state.ui_net_profit = f"{val:,}"
    st.session_state.last_trigger = 'profit'

# [콜백] 사용자가 마진율을 직접 입력했을 때
def handle_margin_change():
    st.session_state.last_trigger = 'margin'

# [콜백] 일반 원가 입력창 세 자리 콤마 자동 생성용
def format_generic(key):
    raw = st.session_state[key].replace(",", "")
    try: val = int(raw)
    except: val = 0
    st.session_state[key] = f"{val:,}"

st.title("📊 마진율 계산기")

# 최상단 결과 레이아웃 공간 확보
top_container = st.container()

# 2. 마켓 기본 데이터 설정
st.subheader("🛒 수수료 및 마켓 설정")
platform_db = {
    "스마트스토어": {"cat": 3.63, "link": 3.0, "ship": 3.63},
    "쿠팡": {"cat": 11.88, "link": 0.0, "ship": 3.3},
    "11번가": {"cat": 13.0, "link": 2.0, "ship": 3.3},
    "G마켓": {"cat": 13.0, "link": 2.0, "ship": 3.3},
    "옥션": {"cat": 13.0, "link": 2.0, "ship": 3.3},
    "기타 마켓": {"cat": 11.0, "link": 2.0, "ship": 3.3}
}
selected_platform = st.selectbox("쇼핑몰 선택", list(platform_db.keys()))
defaults = platform_db[selected_platform]

col_fee1, col_fee2, col_fee3 = st.columns(3)
with col_fee1: cat_rate = st.number_input("카테고리 (%)", value=defaults["cat"], step=0.1)
with col_fee2: link_rate = st.number_input("연동 (%)", value=defaults["link"], step=0.1)
with col_fee3: ship_rate = st.number_input("배송비 (%)", value=defaults["ship"], step=0.1)

vat_rate = st.number_input("부가세율 (%)", value=10, step=1)

# 3. 하단 금액 입력 섹션 (안전한 정수 콤마 콜백 연결)
st.markdown("---")
col_in1, col_in2 = st.columns(2)
with col_in1:
    st.subheader("💰 배송비 설정")
    st.text_input("고객배송비 (원)", key="ui_customer_shipping", on_change=format_generic, args=("ui_customer_shipping",))
with col_in2:
    st.subheader("📦 원가 설정")
    st.text_input("매입가격 (원)", key="ui_buy_price", on_change=format_generic, args=("ui_buy_price",))

st.text_input("매입운송비 (원)", key="ui_buy_shipping", on_change=format_generic, args=("ui_buy_shipping",))
st.text_input("기타(포장, 사은품) (원)", key="ui_other_cost", on_change=format_generic, args=("ui_other_cost",))
st.text_input("판매자 택배비 (원)", key="ui_seller_shipping", on_change=format_generic, args=("ui_seller_shipping",))
st.text_input("광고비 (원)", key="ui_ad_cost", on_change=format_generic, args=("ui_ad_cost",))

# 수치 데이터 안전 파싱 함수
def get_val(key):
    try: return int(st.session_state[key].replace(",", ""))
    except: return 0

customer_shipping = get_val("ui_customer_shipping")
buy_price = get_val("ui_buy_price")
buy_shipping = get_val("ui_buy_shipping")
other_cost = get_val("ui_other_cost")
seller_shipping = get_val("ui_seller_shipping")
ad_cost = get_val("ui_ad_cost")

# 변하지 않는 고정 원가(총 매입비용) 계산
total_cost = buy_price + buy_shipping + other_cost + seller_shipping + ad_cost

# 순수익 타겟 기반 판매가 역산 엔진 함수
def price_from_profit(target_profit):
    pre_vat = target_profit * (1 + vat_rate / 100) if target_profit > 0 else target_profit
    target_settlement = pre_vat + total_cost
    fee_denom = 1 - ((cat_rate + link_rate) / 100)
    if fee_denom > 0:
        price = int((target_settlement - customer_shipping * (1 - ship_rate / 100)) / fee_denom)
        return max(0, price)
    return 0

# 4. 최상단 예약 구역에 양방향 제어 레이아웃 주입
with top_container:
    st.markdown("### 🏆 실시간 결과 및 목표 조정")
    
    # 원터치 고정 마진 버튼 (세션 상태 직접 제어 방식으로 수정)
    btn_col1, btn_col2 = st.columns(2)
    if btn_col1.button("🎁 순수익 5,000원 남기기"):
        st.session_state["ui_net_profit"] = "5,000"
        st.session_state.last_trigger = 'profit'
        st.rerun()
    if btn_col2.button("🎁 순수익 10,000원 남기기"):
        st.session_state["ui_net_profit"] = "10,000"
        st.session_state.last_trigger = 'profit'
        st.rerun()

    # 어떤 입력창이 트리거가 되었느냐에 따라 연동 수식 분기 실행
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

    # 상단 3열 동기화 렌더링
    col1, col2, col3 = st.columns(3)
    with col1: st.text_input("💰 판매가격 (원)", key="ui_sell_price", on_change=handle_price_change)
    with col2: st.text_input("💸 최종 순수익 (원)", key="ui_net_profit", on_change=handle_profit_change)
    with col3: st.number_input("📈 마진율 (ROI %)", key="ui_margin_rate", step=1.0, on_change=handle_margin_change)

    st.markdown("---")

# 5. 접이식 상세 내역 노출
with st.expander("🔍 상세 정산 데이터 확인"):
    sell_price = get_val("ui_sell_price")
    current_fee = (sell_price * (cat_rate + link_rate) / 100) + (customer_shipping * (ship_rate / 100))
    settlement_amount = sell_price + customer_shipping - current_fee
    net_profit = get_val("ui_net_profit")
    st.write(f"• 플랫폼 정산금액 (공제 후): {int(settlement_amount):,} 원")
    st.write(f"• 총 매입비용 (고정 원가): {int(total_cost):,} 원")
    st.write(f"• 예상 납부 부가세: {int(net_profit * (vat_rate / 100)) if net_profit > 0 else 0:,} 원")
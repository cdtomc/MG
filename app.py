import streamlit as st

st.set_page_config(page_title="마진율 계산기", layout="centered")

# 모바일 극밀착 여백 CSS
st.markdown("""
    <style>
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 1rem !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
    }
    div[data-testid="stVerticalBlock"] > div {
        padding-bottom: 0.2rem !important;
        margin-bottom: 0.2rem !important;
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

st.title("📊 마진율 계산기")

# 세션 상태 변수 초기화
if 'sell_price' not in st.session_state: st.session_state.sell_price = 0
if 'net_profit' not in st.session_state: st.session_state.net_profit = 0
if 'margin_rate' not in st.session_state: st.session_state.margin_rate = 0.0

# 최상단 결과 레이아웃 구역 예약
top_container = st.container()

# 1. 쇼핑몰 기본 수수료 세팅
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

# 콤마 자동완성 기능이 탑재된 금액 입력 헬퍼 함수
def safe_money_input(label, default_val, key):
    if key not in st.session_state:
        st.session_state[key] = default_val
    val_str = st.text_input(label, value=f"{st.session_state[key]:,}", key=f"ui_{key}")
    try:
        parsed = int(val_str.replace(",", ""))
    except:
        parsed = 0
    st.session_state[key] = parsed
    return parsed

# 2. 하단 지출/원가 금액 입력부 (전부 자동 콤마 적용)
st.markdown("---")
col_in1, col_in2 = st.columns(2)
with col_in1: customer_shipping = safe_money_input("고객배송비 (원)", 0, "customer_shipping")
with col_in2: buy_price = safe_money_input("매입가격 (원)", 0, "buy_price")

buy_shipping = safe_money_input("매입운송비 (원)", 3000, "buy_shipping")
other_cost = safe_money_input("기타(포장, 사은품) (원)", 300, "other_cost")
seller_shipping = safe_money_input("판매자 택배비 (원)", 0, "seller_shipping")
ad_cost = safe_money_input("광고비 (원)", 0, "ad_cost")

# 원가 고정값 (총 매입비용)
total_cost = buy_price + buy_shipping + other_cost + seller_shipping + ad_cost

# 공통 역산 함수 정의
def calculate_from_profit(target_profit):
    pre_vat = target_profit * (1 + vat_rate / 100) if target_profit > 0 else target_profit
    target_settlement = pre_vat + total_cost
    fee_denom = 1 - ((cat_rate + link_rate) / 100)
    if fee_denom > 0:
        price = int((target_settlement - customer_shipping * (1 - ship_rate / 100)) / fee_denom)
        return max(0, price)
    return 0

# 3. 최상단 예약 컨테이너 연동 제어 구현
with top_container:
    st.markdown("### 🏆 실시간 결과 및 목표 조정")
    
    # 원터치 마진 설정 버튼 추가 (모바일 터치 편의성)
    btn_col1, btn_col2 = st.columns(2)
    with btn_col1:
        if st.button("🎁 순수익 5,000원 남기기"):
            st.session_state.net_profit = 5000
            st.session_state.sell_price = calculate_from_profit(5000)
            st.session_state.margin_rate = (5000 / total_cost * 100) if total_cost > 0 else 0.0
            st.rerun()
    with btn_col2:
        if st.button("🎁 순수익 10,000원 남기기"):
            st.session_state.net_profit = 10000
            st.session_state.sell_price = calculate_from_profit(10000)
            st.session_state.margin_rate = (10000 / total_cost * 100) if total_cost > 0 else 0.0
            st.rerun()

    col1, col2, col3 = st.columns(3)
    with col1:
        ui_p = st.text_input("💰 판매가격 (원)", value=f"{st.session_state.sell_price:,}", key="top_p")
        try: p_val = int(ui_p.replace(",", ""))
        except: p_val = 0
    with col2:
        ui_n = st.text_input("💸 최종 순수익 (원)", value=f"{st.session_state.net_profit:,}", key="top_n")
        try: n_val = int(ui_n.replace(",", ""))
        except: n_val = 0
    with col3:
        m_val = st.number_input("📈 마진율 (ROI %)", value=float(st.session_state.margin_rate), step=1.0, key="top_m")

    # 상단 인터페이스의 값이 수동으로 직접 변경되었는지 추적
    if p_val != st.session_state.sell_price:
        st.session_state.sell_price = p_val
        total_sales = p_val + customer_shipping
        platform_fee = (p_val * (cat_rate + link_rate) / 100) + (customer_shipping * (ship_rate / 100))
        settlement_amount = total_sales - platform_fee
        pre_vat = settlement_amount - total_cost
        est_vat = (pre_vat / (1 + vat_rate/100) * (vat_rate/100)) if pre_vat > 0 else 0
        st.session_state.net_profit = int(pre_vat - est_vat)
        st.session_state.margin_rate = (st.session_state.net_profit / total_cost * 100) if total_cost > 0 else 0.0
        st.rerun()
        
    elif n_val != st.session_state.net_profit:
        st.session_state.net_profit = n_val
        st.session_state.sell_price = calculate_from_profit(n_val)
        st.session_state.margin_rate = (n_val / total_cost * 100) if total_cost > 0 else 0.0
        st.rerun()
        
    elif m_val != st.session_state.margin_rate:
        st.session_state.margin_rate = m_val
        target_p = int(total_cost * (m_val / 100))
        st.session_state.net_profit = target_p
        st.session_state.sell_price = calculate_from_profit(target_p)
        st.rerun()

# 4. 상세 내역 하단 노출
st.markdown("---")
with st.expander("🔍 상세 정산 데이터 확인"):
    current_fee = (st.session_state.sell_price * (cat_rate + link_rate) / 100) + (customer_shipping * (ship_rate / 100))
    st.write(f"• 플랫폼 정산금액 (공제 후): {int(st.session_state.sell_price + customer_shipping - current_fee):,} 원")
    st.write(f"• 총 매입비용 (고정 원가): {int(total_cost):,} 원")
    st.write(f"• 예상 납부 부가세: {int(st.session_state.net_profit * (vat_rate / 100)) if st.session_state.net_profit > 0 else 0:,} 원")
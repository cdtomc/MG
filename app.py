import streamlit as st
import math
import re

st.set_page_config(page_title="마진율 계산기", layout="centered")

# 모바일 화면 극대화를 위한 울트라 초밀착 여백 및 타겟 컬러 지정 CSS 스타일
st.markdown("""
    <style>
    /* 1. 전체 화면 및 요소 간격 조밀화 */
    .block-container {
        padding-top: 0.3rem !important;
        padding-bottom: 0.4rem !important;
        padding-left: 0.5rem !important;
        padding-right: 0.5rem !important;
    }
    div[data-testid="stVerticalBlock"] > div {
        padding-bottom: 0.02rem !important;
        margin-bottom: 0.02rem !important;
    }
    hr {
        margin-top: 0.2rem !important;
        margin-bottom: 0.2rem !important;
    }
    h1, h2, h3, h4, h5 {
        margin-top: 0.02rem !important;
        margin-bottom: 0.05rem !important;
    }
    .stCaption {
        margin-top: 0px !important;
        margin-bottom: 0px !important;
        padding-top: 0px !important;
        padding-bottom: 2px !important;
        font-size: 11px !important;
    }
    
    /* 2. 모바일 가로 한 줄 강제 정렬 */
    div[data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        gap: 2px !important;
        margin-bottom: 0.02rem !important;
        margin-top: 0px !important;
    }
    div[data-testid="column"] {
        flex: 1 1 0% !important;
        min-width: 0 !important;
        padding-left: 1px !important;
        padding-right: 1px !important;
    }
    div[data-testid="column"] button {
        padding: 4px 1px !important;
        font-size: 8.5px !important;
        width: 100% !important;
        letter-spacing: -0.5px !important;
    }
    div[data-testid="stRadio"] > label {
        display: none;
    }

    /* 마커 숨김 */
    .btn-profit-blue,
    .btn-roi-green,
    .btn-roi-red,
    .core-input-marker {
        display: none !important;
        height: 0px !important;
        margin: 0px !important;
        padding: 0px !important;
    }

    /* 3. 목표 설정 버튼 파스텔톤 */
    div[data-testid="column"]:has(.btn-profit-blue) button {
        background-color: #dbeafe !important;
        color: #1e40af !important;
        font-weight: 900 !important;
        border: 1px solid #93c5fd !important;
        box-shadow: 0 1px 2px rgba(30, 64, 175, 0.12) !important;
    }

    div[data-testid="column"]:has(.btn-roi-green) button {
        background-color: #dcfce7 !important;
        color: #166534 !important;
        font-weight: 900 !important;
        border: 1px solid #86efac !important;
        box-shadow: 0 1px 2px rgba(22, 101, 52, 0.12) !important;
    }

    div[data-testid="column"]:has(.btn-roi-red) button {
        background-color: #fee2e2 !important;
        color: #991b1b !important;
        font-weight: 900 !important;
        border: 1px solid #fca5a5 !important;
        box-shadow: 0 1px 2px rgba(153, 27, 27, 0.12) !important;
    }

    div[data-testid="column"]:has(.btn-profit-blue) button:hover {
        background-color: #bfdbfe !important;
    }

    div[data-testid="column"]:has(.btn-roi-green) button:hover {
        background-color: #bbf7d0 !important;
    }

    div[data-testid="column"]:has(.btn-roi-red) button:hover {
        background-color: #fecaca !important;
    }
    
    /* 4. 핵심 입력창: 살짝 진한 회색 박스 + 눈에 띄는 굵은 글씨 */
    div[data-testid="column"]:has(.core-input-marker) input {
        background-color: #d1d5db !important;
        color: #1d4ed8 !important;
        -webkit-text-fill-color: #1d4ed8 !important;
        border: 1.5px solid #94a3b8 !important;
        font-weight: 900 !important;
        font-size: 16px !important;
        letter-spacing: -0.2px !important;
        box-shadow: inset 0 1px 2px rgba(15, 23, 42, 0.10), 0 1px 2px rgba(15, 23, 42, 0.06) !important;
    }

    div[data-testid="column"]:has(.core-input-marker) input:focus {
        background-color: #cbd5e1 !important;
        color: #172554 !important;
        -webkit-text-fill-color: #172554 !important;
        border: 2px solid #2563eb !important;
        box-shadow: 0 0 0 2px rgba(37, 99, 235, 0.18) !important;
    }
    </style>
""", unsafe_allow_html=True)

# 쇼핑몰 데이터베이스
platform_db = {
    "스마트스토어": {"cat": 3.63, "link": 3.0, "ship": 3.63},
    "쿠팡": {"cat": 11.88, "link": 0.0, "ship": 3.3},
    "11번가": {"cat": 13.0, "link": 2.0, "ship": 3.3},
    "G마켓": {"cat": 13.0, "link": 2.0, "ship": 3.3},
    "옥션": {"cat": 13.0, "link": 2.0, "ship": 3.3},
    "기타 마켓": {"cat": 11.0, "link": 2.0, "ship": 3.3}
}

# 플랫폼 수수료 동기화 콜백
def sync_platform_fees():
    d = platform_db[st.session_state.selected_platform]
    st.session_state.cat_rate = d["cat"]
    st.session_state.link_rate = d["link"]
    st.session_state.ship_rate = d["ship"]
    st.session_state.last_trigger = 'price'

# 시스템 핵심 세션 상태 초기화
if 'selected_platform' not in st.session_state:
    st.session_state.selected_platform = "스마트스토어"
if 'cat_rate' not in st.session_state:
    st.session_state.cat_rate = platform_db[st.session_state.selected_platform]["cat"]
if 'link_rate' not in st.session_state:
    st.session_state.link_rate = platform_db[st.session_state.selected_platform]["link"]
if 'ship_rate' not in st.session_state:
    st.session_state.ship_rate = platform_db[st.session_state.selected_platform]["ship"]

if 'ui_sell_price' not in st.session_state:
    st.session_state.ui_sell_price = "0"
if 'ui_net_profit' not in st.session_state:
    st.session_state.ui_net_profit = "0"
if 'ui_margin_rate' not in st.session_state:
    st.session_state.ui_margin_rate = 0.0
if 'last_trigger' not in st.session_state:
    st.session_state.last_trigger = 'price'

if 'ui_customer_shipping' not in st.session_state:
    st.session_state.ui_customer_shipping = "0"
if 'ui_buy_price' not in st.session_state:
    st.session_state.ui_buy_price = "0"
if 'ui_buy_shipping' not in st.session_state:
    st.session_state.ui_buy_shipping = "3,000"
if 'ui_other_cost' not in st.session_state:
    st.session_state.ui_other_cost = "500"
if 'ui_seller_shipping' not in st.session_state:
    st.session_state.ui_seller_shipping = "0"
if 'ui_ad_cost' not in st.session_state:
    st.session_state.ui_ad_cost = "0"
if 'prev_mode' not in st.session_state:
    st.session_state.prev_mode = "📦 사입 구조"

# 입력값 파싱
def parse_money(value):
    cleaned = re.sub(r"[^0-9\\-]", "", str(value))
    try:
        return int(cleaned)
    except:
        return 0

def handle_price_change():
    val = parse_money(st.session_state.ui_sell_price)
    st.session_state.ui_sell_price = f"{val:,}"
    st.session_state.last_trigger = 'price'

def handle_profit_change():
    val = parse_money(st.session_state.ui_net_profit)
    st.session_state.ui_net_profit = f"{val:,}"
    st.session_state.last_trigger = 'profit'

def handle_margin_change():
    st.session_state.last_trigger = 'margin'

def format_generic(key):
    val = parse_money(st.session_state[key])
    st.session_state[key] = f"{val:,}"

st.title("📊 마진율 계산기")

# 최상단 결과 레이아웃 공간 확보
top_container = st.container()

with top_container:
    col_head1, col_head2 = st.columns([1.3, 1])
    with col_head1:
        st.markdown("### 🏆 실시간 결과")
    with col_head2:
        st.selectbox(
            "쇼핑몰 선택",
            list(platform_db.keys()),
            key="selected_platform",
            label_visibility="collapsed",
            on_change=sync_platform_fees
        )

# 2. 운영 형태 선택 탭
st.markdown("---")
col_mode1, col_mode2 = st.columns([1, 1.3])
with col_mode1:
    st.markdown("##### 📋 운영 형태 선택")
with col_mode2:
    mode = st.radio(
        "운영 형태 선택 라디오",
        ["📦 사입 구조", "🚚 위탁 구조"],
        horizontal=True,
        label_visibility="collapsed"
    )

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
col_fee1, col_fee2, col_fee3 = st.columns(3)
with col_fee1:
    cat_rate = st.number_input("카테고리 (%)", step=0.1, key="cat_rate")
with col_fee2:
    link_rate = st.number_input("연동 (%)", step=0.1, key="link_rate")
with col_fee3:
    ship_rate = st.number_input("배송비 (%)", step=0.1, key="ship_rate")

vat_rate = st.number_input("부가세율 (%)", value=10, step=1)

# 데이터 실시간 로드 및 파싱
customer_shipping = parse_money(st.session_state.get("ui_customer_shipping", "0"))
buy_price = parse_money(st.session_state.get("ui_buy_price", "0"))
buy_shipping = parse_money(st.session_state.get("ui_buy_shipping", "0"))
other_cost = parse_money(st.session_state.get("ui_other_cost", "0"))
seller_shipping = parse_money(st.session_state.get("ui_seller_shipping", "0"))
ad_cost = parse_money(st.session_state.get("ui_ad_cost", "0"))

total_cost = buy_price + buy_shipping + other_cost + seller_shipping + ad_cost

# 정방향 마진 계산 함수
def calc_forward_metrics(sell_price):
    total_sales = sell_price + customer_shipping
    platform_fee = (
        sell_price * (st.session_state.cat_rate + st.session_state.link_rate) / 100
    ) + (
        customer_shipping * (st.session_state.ship_rate / 100)
    )
    settlement_amount = total_sales - platform_fee
    pre_vat = settlement_amount - total_cost
    est_vat = (pre_vat / (1 + vat_rate / 100) * (vat_rate / 100)) if pre_vat > 0 else 0
    net_profit = int(round(pre_vat - est_vat))
    margin_rate = (net_profit / total_cost * 100) if total_cost > 0 else 0.0
    return net_profit, margin_rate, settlement_amount, est_vat

# 순수익 타겟 기반 판매가 역산식
def price_from_profit(target_profit):
    pre_vat = target_profit * (1 + vat_rate / 100) if target_profit > 0 else target_profit
    target_settlement = pre_vat + total_cost
    fee_denom = 1 - ((st.session_state.cat_rate + st.session_state.link_rate) / 100)
    if fee_denom > 0:
        price = math.ceil(
            (target_settlement - customer_shipping * (1 - st.session_state.ship_rate / 100)) / fee_denom
        )
        return max(0, price)
    return 0

# 5. 최상단 엔진 렌더링 구역
with top_container:
    # 매입가격 입력창
    buy_col = st.columns(1)[0]
    with buy_col:
        st.markdown('<span class="core-input-marker"></span>', unsafe_allow_html=True)
        st.text_input("📦 매입가격 [제품 원가] (원)", key="ui_buy_price", on_change=format_generic, args=("ui_buy_price",))

    # 목표 순수익 원터치 설정: 1,000원 ~ 30,000원, 1,000원 단위, 3줄
    st.caption("💵 목표 순수익 원터치 설정")

    profit_rows = [
        list(range(1000, 10001, 1000)),
        list(range(11000, 20001, 1000)),
        list(range(21000, 30001, 1000))
    ]

    for row in profit_rows:
        p_cols = st.columns(10)
        for idx, profit_value in enumerate(row):
            with p_cols[idx]:
                if profit_value == 10000:
                    st.markdown('<span class="btn-profit-blue"></span>', unsafe_allow_html=True)

                if st.button(f"{profit_value:,}", key=f"profit_{profit_value}"):
                    st.session_state["ui_net_profit"] = f"{profit_value:,}"
                    st.session_state.last_trigger = 'profit'
                    st.rerun()

    # 목표 ROI 설정
    st.caption("📈 목표 ROI(원가대비 수익률) 설정")
    m_row = st.columns(10)
    for pct in range(10, 110, 10):
        idx = (pct // 10) - 1
        with m_row[idx]:
            if pct == 30:
                st.markdown('<span class="btn-roi-green"></span>', unsafe_allow_html=True)
            elif pct == 50:
                st.markdown('<span class="btn-roi-red"></span>', unsafe_allow_html=True)

            if st.button(f"{pct}%", key=f"margin_{pct}"):
                st.session_state["ui_margin_rate"] = float(pct)
                st.session_state.last_trigger = 'margin'
                st.rerun()

    if total_cost <= 0 and st.session_state.last_trigger == 'margin':
        st.warning("⚠️ 매입가격 또는 원가를 먼저 입력해야 목표 ROI 계산이 가능합니다!")
        st.session_state["ui_margin_rate"] = 0.0
        st.session_state.last_trigger = 'price'

    # 핵심 상호 역산 및 실제값 동기화
    if st.session_state.last_trigger == 'price':
        sell_price = parse_money(st.session_state.ui_sell_price)
        net_profit, margin_rate, settlement_amount, est_vat = calc_forward_metrics(sell_price)
        st.session_state["ui_net_profit"] = f"{net_profit:,}"
        st.session_state["ui_margin_rate"] = float(margin_rate)
        
    elif st.session_state.last_trigger == 'profit':
        target_profit = parse_money(st.session_state.ui_net_profit)
        sell_price = price_from_profit(target_profit)
        net_profit, margin_rate, settlement_amount, est_vat = calc_forward_metrics(sell_price)
        st.session_state["ui_sell_price"] = f"{sell_price:,}"
        st.session_state["ui_net_profit"] = f"{net_profit:,}"
        st.session_state["ui_margin_rate"] = float(margin_rate)
        
    elif st.session_state.last_trigger == 'margin':
        target_margin_rate = st.session_state["ui_margin_rate"]
        target_profit = int(total_cost * (target_margin_rate / 100))
        sell_price = price_from_profit(target_profit)
        net_profit, margin_rate, settlement_amount, est_vat = calc_forward_metrics(sell_price)
        st.session_state["ui_sell_price"] = f"{sell_price:,}"
        st.session_state["ui_net_profit"] = f"{net_profit:,}"
        st.session_state["ui_margin_rate"] = float(margin_rate)

    # 결과 메인 하이라이트 입력창 3열 렌더링
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown('<span class="core-input-marker"></span>', unsafe_allow_html=True)
        st.text_input("💰 판매가격 (원)", key="ui_sell_price", on_change=handle_price_change)
    with col2:
        st.markdown('<span class="core-input-marker"></span>', unsafe_allow_html=True)
        st.text_input("💸 최종 순수익 (원)", key="ui_net_profit", on_change=handle_profit_change)
    with col3:
        st.markdown('<span class="core-input-marker"></span>', unsafe_allow_html=True)
        st.number_input("📈 마진율 (ROI %)", key="ui_margin_rate", step=1.0, on_change=handle_margin_change)

    st.markdown("---")

# 6. 하단 접이식 세부 정산서
with st.expander("🔍 상세 정산 데이터 확인"):
    current_sell_price = parse_money(st.session_state.ui_sell_price)
    actual_profit, actual_roi, actual_settlement, actual_vat = calc_forward_metrics(current_sell_price)
    sales_margin_rate = (actual_profit / current_sell_price * 100) if current_sell_price > 0 else 0.0
    
    st.write(f"• 현재 적용된 구조: {mode}")
    st.write(f"• 플랫폼 정산금액 (공제 후): {int(round(actual_settlement)):,} 원")
    st.write(f"• 총 매입비용 (고정 원가): {int(total_cost):,} 원")
    st.write(f"• 실제 예상 순수익 (올림 반영): {actual_profit:,} 원")
    st.write(f"• 예상 납부 부가세: {int(round(actual_vat)):,} 원")
    st.write(f"• 📊 순수 매출마진율 (판매가 대비): {sales_margin_rate:.2f} %")
    st.caption("※ 부가세 계산은 일반과세자·매입세액 공제 가능 비용을 단순 가정한 참고용 계산입니다.")

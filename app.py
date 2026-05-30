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
        font-size: 9.5px !important;
        width: 100% !important;
    }
    div[data-testid="stRadio"] > label {
        display: none;
    }

    /* 3. 🎨 목표 설정 원터치 버튼군 지정 컬러 오버라이드 */
    /* 순수익 행(7열) 중 3번째 버튼 [10,000원] -> 선명한 블루 */
    div[data-testid="stHorizontalBlock"]:has(div[data-testid="column"]:nth-child(7)) div[data-testid="column"]:nth-child(3) button {
        background-color: #2563eb !important;
        color: white !important;
        font-weight: bold !important;
        border: none !important;
    }
    /* 마진율 행(10열) 중 3번째 버튼 [30%] -> 선명한 그린 */
    div[data-testid="stHorizontalBlock"]:has(div[data-testid="column"]:nth-child(10)) div[data-testid="column"]:nth-child(3) button {
        background-color: #16a34a !important;
        color: white !important;
        font-weight: bold !important;
        border: none !important;
    }
    /* 마진율 행(10열) 중 5번째 버튼 [50%] -> 선명한 레드 */
    div[data-testid="stHorizontalBlock"]:has(div[data-testid="column"]:nth-child(10)) div[data-testid="column"]:nth-child(5) button {
        background-color: #dc2626 !important;
        color: white !important;
        font-weight: bold !important;
        border: none !important;
    }
    
    /* 4. 💎 [색상 교정] 핵심 4대 지표 입력창에만 은은한 하이라이트 주입 (덜 진하고 세련된 소프트 블루 톤) */
    div:has(.core-marker) + div[data-testid="stTextInput"] input,
    div:has(.core-marker) + div[data-testid="stNumberInput"] input {
        background-color: #f0f9ff !important;
        color: #0f172a !important;
        border: 1px solid #38bdf8 !important;
        font-weight: bold !important;
        font-size: 14.5px !important;
        box-shadow: 0 1px 2px rgba(14, 165, 233, 0.05) !important;
    }
    
    .core-marker {
        display: none;
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

# [피드백 7 반영] 글자나 공백이 섞여 들어와도 숫자만 철저하게 발라내는 강력한 정밀 정규식 파싱 함수
def parse_money(value):
    cleaned = re.sub(r"[^0-9\-]", "", str(value))
    try: return int(cleaned)
    except: return 0

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

# [피드백 2 반영] 렌더링 순서 재배치: 선택박스를 코드 최상위 동선으로 끌어올려 데이터 꼬임 원천 차단
with top_container:
    col_head1, col_head2 = st.columns([1.3, 1])
    with col_head1: st.markdown("### 🏆 실시간 결과")
    with col_head2: st.selectbox("쇼핑몰 선택", list(platform_db.keys()), key="selected_platform", label_visibility="collapsed")

defaults = platform_db[st.session_state.selected_platform]

# 2. 운영 형태 선택 탭
st.markdown("---")
col_mode1, col_mode2 = st.columns([1, 1.3])
with col_mode1: st.markdown("##### 📋 운영 형태 선택")
with col_mode2: mode = st.radio("운영 형태 선택 라디오", ["📦 사입 구조", "🚚 위탁 구조"], horizontal=True, label_visibility="collapsed")

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

# 3. 배송비 및 기타 원가 설정부 (기본 순정 색상 유지 파트)
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
with col_fee1: cat_rate = st.number_input("카테고리 (%)", value=defaults["cat"], step=0.1, key="cat_rate")
with col_fee2: link_rate = st.number_input("연동 (%)", value=defaults["link"], step=0.1, key="link_rate")
with col_fee3: ship_rate = st.number_input("배송비 (%)", value=defaults["ship"], step=0.1, key="ship_rate")

vat_rate = st.number_input("부가세율 (%)", value=10, step=1)

# 데이터 실시간 안전 로드
customer_shipping = parse_money(st.session_state.get("ui_customer_shipping", "0"))
buy_price = parse_money(st.session_state.get("ui_buy_price", "0"))
buy_shipping = parse_money(st.session_state.get("ui_buy_shipping", "0"))
other_cost = parse_money(st.session_state.get("ui_other_cost", "0"))
seller_shipping = parse_money(st.session_state.get("ui_seller_shipping", "0"))
ad_cost = parse_money(st.session_state.get("ui_ad_cost", "0"))

total_cost = buy_price + buy_shipping + other_cost + seller_shipping + ad_cost

# [피드백 1 반영] 역산식 무조건 올림(math.ceil) 처리하여 목표 순수익 방어선 100% 사수
def price_from_profit(target_profit):
    pre_vat = target_profit * (1 + vat_rate / 100) if target_profit > 0 else target_profit
    target_settlement = pre_vat + total_cost
    fee_denom = 1 - ((cat_rate + link_rate) / 100)
    if fee_denom > 0:
        price = math.ceil((target_settlement - customer_shipping * (1 - ship_rate / 100)) / fee_denom)
        return max(0, price)
    return 0

# 5. 최상단 엔진 렌더링 구역 구동
with top_container:
    # 매입가격 하이라이트 주입
    st.markdown('<div class="core-marker"></div>', unsafe_allow_html=True)
    st.text_input("📦 매입가격 [제품 원가] (원)", key="ui_buy_price", on_change=format_generic, args=("ui_buy_price",))

    # 목표 순수익 원터치 설정 (정수 콤마 텍스트 전면 교체 완료)
    st.caption("💵 목표 순수익 원터치 설정")
    p_row = st.columns(7)
    profits_layout = [("5,000", "5,000"), ("8,000", "8,000"), ("10,000", "10,000"), ("15,000", "15,000"), ("20,000", "20,000"), ("25,000", "25,000"), ("30,000", "30,000")]
    for idx, (lbl, val) in enumerate(profits_layout):
        if p_row[idx].button(lbl):
            st.session_state["ui_net_profit"] = val
            st.session_state.last_trigger = 'profit'; st.rerun()

    # [피드백 3 반영] 텍스트 명확화: "목표 ROI(원가대비 수익률) 설정"으로 가이드 수정
    st.caption("📈 목표 ROI(원가대비 수익률) 설정")
    m_row = st.columns(10)
    for pct in range(10, 110, 10):
        idx = (pct // 10) - 1
        if m_row[idx].button(f"{pct}%"):
            st.session_state["ui_margin_rate"] = float(pct)
            st.session_state.last_trigger = 'margin'; st.rerun()

    # [피드백 4 반영] 위탁 노원가 예외처리 방어: 원가가 0원일 때 ROI 기반 마진 계산 차단 경고 시스템
    if total_cost <= 0 and st.session_state.last_trigger == 'margin':
        st.warning("⚠️ 매입가격 또는 원가를 먼저 입력해야 목표 ROI 계산이 가능합니다!")
        st.session_state["ui_margin_rate"] = 0.0
        st.session_state.last_trigger = 'price'

    # 핵심 상호 역산 분기 실행
    if st.session_state.last_trigger == 'price':
        sell_price = parse_money(st.session_state.ui_sell_price)
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
        net_profit = parse_money(st.session_state.ui_net_profit)
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

    # 결과 메인 하이라이트 입력창 3열 렌더링
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown('<div class="core-marker"></div>', unsafe_allow_html=True)
        st.text_input("💰 판매가격 (원)", key="ui_sell_price", on_change=handle_price_change)
    with col2:
        st.markdown('<div class="core-marker"></div>', unsafe_allow_html=True)
        st.text_input("💸 최종 순수익 (원)", key="ui_net_profit", on_change=handle_profit_change)
    with col3:
        st.markdown('<div class="core-marker"></div>', unsafe_allow_html=True)
        st.number_input("📈 마진율 (ROI %)", key="ui_margin_rate", step=1.0, on_change=handle_margin_change)

# 6. 하단 접이식 세부 내역 및 면책 조항
st.markdown("---")
with st.expander("🔍 상세 정산 데이터 확인"):
    current_sell_price = parse_money(st.session_state.ui_sell_price)
    current_fee = (current_sell_price * (cat_rate + link_rate) / 100) + (customer_shipping * (ship_rate / 100))
    settlement_amount = current_sell_price + customer_shipping - current_fee
    current_net_profit = parse_money(st.session_state.ui_net_profit)
    
    # [피드백 3 고도화] 실전 이커머스 표준 지표인 매출액 기준 마진율도 서브로 비교 노출하여 시너지 생성
    sales_margin_rate = (current_net_profit / current_sell_price * 100) if current_sell_price > 0 else 0.0
    
    st.write(f"• 현재 적용된 구조: {mode}")
    st.write(f"• 플랫폼 정산금액 (공제 후): {int(settlement_amount):,} 원")
    st.write(f"• 총 매입비용 (고정 원가): {int(total_cost):,} 원")
    st.write(f"• 예상 납부 부가세: {int(current_net_profit * (vat_rate / 100)) if current_net_profit > 0 else 0:,} 원")
    st.write(f"• 📊 순수 매출마진율 (판매가 대비): {sales_margin_rate:.2f} %")
    
    # [피드백 5 반영] 안전을 위한 부가세 계산 가정 참고 가이드 캡션 명시
    st.caption("※ 부가세 계산은 일반과세자·매입세액 공제 가능 비용을 단순 가정한 참고용 계산입니다.")

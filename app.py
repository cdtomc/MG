import streamlit as st

st.set_page_config(page_title="마진율 계산기", layout="centered")

# 모바일 화면 극대화를 위한 초밀착 여백 CSS
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
        margin-top: 0.5rem !important;
        margin-bottom: 0.5rem !important;
    }
    h1, h2, h3, h4 {
        margin-top: 0.1rem !important;
        margin-bottom: 0.3rem !important;
    }
    </style>
""", unsafe_allow_html=True)

st.title("📊 마진율 계산기")

# 양방향 연동을 위한 세션 상태 변수 초기화
if 'sell_price' not in st.session_state: st.session_state.sell_price = 0
if 'net_profit' not in st.session_state: st.session_state.net_profit = 0
if 'margin_rate' not in st.session_state: st.session_state.margin_rate = 0.0
if 'last_changed' not in st.session_state: st.session_state.last_changed = 'price'
if 'prev_sell_price' not in st.session_state: st.session_state.prev_sell_price = 0
if 'prev_net_profit' not in st.session_state: st.session_state.prev_net_profit = 0
if 'prev_margin_rate' not in st.session_state: st.session_state.prev_margin_rate = 0.0

# 최상단 결과창 배치를 위한 컨테이너 예약
top_container = st.container()

# 세 자리마다 콤마(,)를 자동으로 찍어주는 금액 입력기 헬퍼 함수
def get_money_input(label, default_val, session_key):
    if session_key not in st.session_state:
        st.session_state[session_key] = default_val
    ui_val = st.text_input(label, value=f"{st.session_state[session_key]:,}")
    try:
        parsed = int(ui_val.replace(",", ""))
    except:
        parsed = 0
    st.session_state[session_key] = parsed
    return parsed

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
with col_fee1:
    cat_rate = st.number_input("카테고리 (%)", value=defaults["cat"], step=0.1)
with col_fee2:
    link_rate = st.number_input("연동 (%)", value=defaults["link"], step=0.1)
with col_fee3:
    ship_rate = st.number_input("배송비 (%)", value=defaults["ship"], step=0.1)

vat_rate = st.number_input("부가세율 (%)", value=10, step=1)

# 2. 하단 매출/매입 금액 입력부 (자동 콤마 적용)
st.markdown("---")
col_in1, col_in2 = st.columns(2)
with col_in1:
    st.subheader("💰 배송비 설정")
    customer_shipping = get_money_input("고객배송비 (원)", 0, "customer_shipping")
with col_in2:
    st.subheader("📦 원가 설정")
    buy_price = get_money_input("매입가격 (원)", 0, "buy_price")

buy_shipping = get_money_input("매입운송비 (원)", 3000, "buy_shipping")
other_cost = get_money_input("기타(포장, 사은품) (원)", 300, "other_cost")
seller_shipping = get_money_input("판매자 택배비 (원)", 0, "seller_shipping")
ad_cost = get_money_input("광고비 (원)", 0, "ad_cost")

# 고정 원가(총 매입비용) 계산
total_cost = buy_price + buy_shipping + other_cost + seller_shipping + ad_cost

# 3. 최상단 예약 컨테이너 내부 연동 제어 로직
with top_container:
    st.markdown("### 🏆 실시간 결과 및 목표 조정")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        ui_price = st.text_input("💰 판매가격 (원)", value=f"{st.session_state.sell_price:,}")
        try: price_val = int(ui_price.replace(",", ""))
        except: price_val = 0
    with col2:
        ui_profit = st.text_input("💸 최종 순수익 (원)", value=f"{st.session_state.net_profit:,}")
        try: profit_val = int(ui_profit.replace(",", ""))
        except: profit_val = 0
    with col3:
        margin_val = st.number_input("📈 마진율 (ROI %)", value=float(st.session_state.margin_rate), step=1.0)

    # 상단 결과창 입력 컴포넌트 중 어떤 값이 수정되었는지 변동 감지
    top_changed = (price_val != st.session_state.prev_sell_price or 
                   profit_val != st.session_state.prev_net_profit or 
                   margin_val != st.session_state.prev_margin_rate)
    
    if top_changed:
        if price_val != st.session_state.prev_sell_price:
            st.session_state.last_changed = 'price'
            st.session_state.sell_price = price_val
        elif profit_val != st.session_state.prev_net_profit:
            st.session_state.last_changed = 'profit'
            st.session_state.net_profit = profit_val
        elif margin_val != st.session_state.prev_margin_rate:
            st.session_state.last_changed = 'margin'
            st.session_state.margin_rate = margin_val
        
        # 마스터 수식 연산 엔진 실행
        if st.session_state.last_changed == 'price':
            total_sales = st.session_state.sell_price + customer_shipping
            platform_fee = (st.session_state.sell_price * (cat_rate + link_rate) / 100) + (customer_shipping * (ship_rate / 100))
            settlement_amount = total_sales - platform_fee
            pre_vat_margin = settlement_amount - total_cost
            estimated_vat = (pre_vat_margin / (1 + vat_rate/100) * (vat_rate/100)) if pre_vat_margin > 0 else 0
            st.session_state.net_profit = int(pre_vat_margin - estimated_vat)
            st.session_state.margin_rate = (st.session_state.net_profit / total_cost * 100) if total_cost > 0 else 0.0
            
        elif st.session_state.last_changed == 'profit':
            target_profit = st.session_state.net_profit
            pre_vat_margin = target_profit * (1 + vat_rate / 100) if target_profit > 0 else target_profit
            target_settlement = pre_vat_margin + total_cost
            fee_denominator = 1 - ((cat_rate + link_rate) / 100)
            if fee_denominator > 0:
                st.session_state.sell_price = int((target_settlement - customer_shipping * (1 - ship_rate / 100)) / fee_denominator)
                st.session_state.sell_price = max(0, st.session_state.sell_price)
            else:
                st.session_state.sell_price = 0
            st.session_state.margin_rate = (target_profit / total_cost * 100) if total_cost > 0 else 0.0
            
        elif st.session_state.last_changed == 'margin':
            target_profit = int(total_cost * (st.session_state.margin_rate / 100))
            st.session_state.net_profit = target_profit
            pre_vat_margin = target_profit * (1 + vat_rate / 100) if target_profit > 0 else target_profit
            target_settlement = pre_vat_margin + total_cost
            fee_denominator = 1 - ((cat_rate + link_rate) / 100)
            if fee_denominator > 0:
                st.session_state.sell_price = int((target_settlement - customer_shipping * (1 - ship_rate / 100)) / fee_denominator)
                st.session_state.sell_price = max(0, st.session_state.sell_price)
            else:
                st.session_state.sell_price = 0

        # 백업 데이터 동기화 후 즉시 반영 리프레시
        st.session_state.prev_sell_price = st.session_state.sell_price
        st.session_state.prev_net_profit = st.session_state.net_profit
        st.session_state.prev_margin_rate = st.session_state.margin_rate
        st.rerun()
        
    else:
        # 상단 결과창 터치 외에 하단 원가 지출액이 변동된 경우 기본 정방향 계산 처리
        total_sales = st.session_state.sell_price + customer_shipping
        platform_fee = (st.session_state.sell_price * (cat_rate + link_rate) / 100) + (customer_shipping * (ship_rate / 100))
        settlement_amount = total_sales - platform_fee
        pre_vat_margin = settlement_amount - total_cost
        estimated_vat = (pre_vat_margin / (1 + vat_rate/100) * (vat_rate/100)) if pre_vat_margin > 0 else 0
        st.session_state.net_profit = int(pre_vat_margin - estimated_vat)
        st.session_state.margin_rate = (st.session_state.net_profit / total_cost * 100) if total_cost > 0 else 0.0
        
        st.session_state.prev_sell_price = st.session_state.sell_price
        st.session_state.prev_net_profit = st.session_state.net_profit
        st.session_state.prev_margin_rate = st.session_state.margin_rate

# 4. 상세 내역 노출 파트
st.markdown("---")
with st.expander("🔍 상세 정산 데이터 확인"):
    current_fee = (st.session_state.sell_price * (cat_rate + link_rate) / 100) + (customer_shipping * (ship_rate / 100))
    st.write(f"• 플랫폼 정산금액 (공제 후): {int(st.session_state.sell_price + customer_shipping - current_fee):,} 원")
    st.write(f"• 총 매입비용 (고정 원가): {int(total_cost):,} 원")
    st.write(f"• 예상 납부 부가세: {int(st.session_state.net_profit * (vat_rate / 100)) if st.session_state.net_profit > 0 else 0:,} 원")
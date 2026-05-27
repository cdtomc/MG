import streamlit as st

st.set_page_config(page_title="마진율 계산기", layout="centered")

# 모바일 맞춤형 여백 축소 CSS
st.markdown("""
    <style>
    .block-container {
        padding-top: 1.5rem !important;
        padding-bottom: 1rem !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
    }
    div[data-testid="stVerticalBlock"] > div {
        padding-bottom: 0.3rem !important;
        margin-bottom: 0.3rem !important;
    }
    hr {
        margin-top: 0.6rem !important;
        margin-bottom: 0.6rem !important;
    }
    h1, h2, h3, h4 {
        margin-top: 0.2rem !important;
        margin-bottom: 0.4rem !important;
        padding-top: 0rem !important;
        padding-bottom: 0rem !important;
    }
    </style>
""", unsafe_allow_html=True)

st.title("📊 마진율 계산기")

# 상단 결과창 공간 예약
result_container = st.container()

# 1. 수수료 및 마켓 설정
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

# 2. 목표 마진율 역산 입력 (1번 추가 기능)
st.markdown("---")
st.subheader("🎯 목표 마진 판매가 역산")
target_margin_rate = st.number_input("목표 마진율 입력 (%, 원가대비 ROI 기준)", min_value=0.0, max_value=500.0, value=30.0, step=5.0)

# 3. 매출/매입 금액 입력 섹션
st.markdown("---")
col_in1, col_in2 = st.columns(2)
with col_in1:
    st.subheader("💰 매출 입력")
    sell_price = st.number_input("판매가격 (원)", min_value=0, step=1000, value=0)
    customer_shipping = st.number_input("고객배송비 (원)", min_value=0, step=500, value=0)
with col_in2:
    st.subheader("📦 매입 입력")
    buy_price = st.number_input("매입가격 (원)", min_value=0, step=1000, value=0)
    buy_shipping = st.number_input("매입운송비 (원)", min_value=0, step=500, value=3000)

other_cost = st.number_input("기타(포장, 사은품) (원)", min_value=0, step=100, value=300)
seller_shipping = st.number_input("판매자 택배비 (원)", min_value=0, step=500, value=0)
ad_cost = st.number_input("광고비 (원)", min_value=0, step=1000, value=0)

# --- 계산 로직 ---
total_sales = sell_price + customer_shipping
platform_fee = (sell_price * (cat_rate + link_rate) / 100) + (customer_shipping * (ship_rate / 100))
settlement_amount = total_sales - platform_fee
total_cost = buy_price + buy_shipping + other_cost + seller_shipping + ad_cost

# 현재 상태의 순수익 계산
pre_vat_margin = settlement_amount - total_cost
estimated_vat = (pre_vat_margin / (1 + vat_rate/100) * (vat_rate/100)) if pre_vat_margin > 0 else 0
net_profit = pre_vat_margin - estimated_vat
margin_rate = (net_profit / total_cost * 100) if total_cost > 0 else 0

# 목표 판매가 역산 로직 실행
if total_cost > 0:
    target_net_profit = total_cost * (target_margin_rate / 100)
    target_pre_vat_margin = target_net_profit * (1 + vat_rate / 100)
    target_settlement = target_pre_vat_margin + total_cost
    
    # 수수료율을 제한 분모 계산
    fee_denominator = 1 - ((cat_rate + link_rate) / 100)
    if fee_denominator > 0:
        recommended_price = (target_settlement - customer_shipping * (1 - ship_rate / 100)) / fee_denominator
        recommended_price = max(0, recommended_price)
    else:
        recommended_price = 0
else:
    recommended_price = 0

# --- 상단 레이아웃에 실시간 결과 출력 ---
with result_container:
    st.markdown("### 🏆 실시간 계산 결과")
    r_col1, r_col2 = st.columns(2)
    r_col1.metric("💰 최종 순수익", f"{int(net_profit):,} 원")
    r_col2.metric("📈 마진율 (ROI)", f"{margin_rate:.2f} %")
    
    # 역산 결과 제안문구 추가
    if recommended_price > 0:
        st.info(f"💡 목표 마진 {target_margin_rate}%를 얻기 위한 **추천 판매가: {int(recommended_price):,} 원**")
    st.markdown("---")

# 상세 내역은 맨 아래 유지
st.markdown("---")
with st.expander("🔍 상세 정산 데이터 확인"):
    st.write(f"• 정산금액 (공제 후): {int(settlement_amount):,} 원")
    st.write(f"• 총 매입비용: {int(total_cost):,} 원")
    st.write(f"• 예상 부가세: {int(estimated_vat):,} 원")
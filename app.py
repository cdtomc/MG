import streamlit as st

st.set_page_config(page_title="마진율 계산기", layout="centered")

# 제목 변경
st.title("📊 마진율 계산기")

# --- UI 수정: 결과(순수익/마진율)를 최상단으로 이동 ---
# 계산을 위해 입력값들을 먼저 받아야 하므로, UI만 위로 올리고 수식은 하단에서 처리 후 세션 상태를 활용하거나
# 혹은 입력창을 먼저 선언하되 결과 박스를 위에 고정하는 방식입니다.

# 1. 입력 섹션 (결과 도출을 위해 먼저 필요)
st.subheader("🛒 쇼핑몰 및 수수료 설정")
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

# 매출/매입 입력
st.markdown("---")
col_input1, col_input2 = st.columns(2)
with col_input1:
    st.subheader("💰 매출")
    sell_price = st.number_input("판매가격 (원)", min_value=0, step=1000, value=0)
    customer_shipping = st.number_input("고객배송비 (원)", min_value=0, step=500, value=0)
with col_input2:
    st.subheader("📦 매입")
    buy_price = st.number_input("매입가격 (원)", min_value=0, step=1000, value=0)
    buy_shipping = st.number_input("매입운송비 (원)", min_value=0, step=500, value=3000)

other_cost = st.number_input("기타(포장,사은품) (원)", min_value=0, step=100, value=300)
seller_shipping = st.number_input("판매자 택배비 (원)", min_value=0, step=500, value=0)
ad_cost = st.number_input("광고비 (원)", min_value=0, step=1000, value=0)

# --- 계산 로직 ---
total_sales = sell_price + customer_shipping
total_platform_fee = (sell_price * (cat_rate + link_rate) / 100) + (customer_shipping * (ship_rate / 100))
settlement_amount = total_sales - total_platform_fee
total_cost = buy_price + buy_shipping + other_cost + seller_shipping + ad_cost

pre_vat_margin = settlement_amount - total_cost
estimated_vat = (pre_vat_margin / (1 + vat_rate/100) * (vat_rate/100)) if pre_vat_margin > 0 else 0
net_profit = pre_vat_margin - estimated_vat
margin_rate = (net_profit / total_cost * 100) if total_cost > 0 else 0

# --- 최종 결과 (앱 최하단에 배치하되 강조) ---
st.markdown("---")
st.success(f"### 🏆 최종 순수익: **{int(net_profit):,} 원**")
st.info(f"### 📈 최종 마진율(ROI): **{margin_rate:.2f} %**")

with st.expander("🔍 상세 정산 내역 보기"):
    st.write(f"• 플랫폼 정산금액: {int(settlement_amount):,} 원")
    st.write(f"• 총 매입비용: {int(total_cost):,} 원")
    st.write(f"• 예상 부가세: {int(estimated_vat):,} 원")
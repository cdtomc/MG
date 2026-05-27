import streamlit as st

st.set_page_config(page_title="장사왕 st. 프로 마진기", layout="centered")
st.title("👑 장사왕 st. 모바일 계산기 Pro")

# 1. 쇼핑몰 및 세부 수수료 설정 정보
platform_db = {
    "스마트스토어": {"cat": 3.63, "link": 3.0, "ship": 3.63},
    "쿠팡": {"cat": 11.88, "link": 0.0, "ship": 3.3},
    "11번가": {"cat": 13.0, "link": 2.0, "ship": 3.3},
    "G마켓": {"cat": 13.0, "link": 2.0, "ship": 3.3},
    "옥션": {"cat": 13.0, "link": 2.0, "ship": 3.3},
    "기타 마켓": {"cat": 11.0, "link": 2.0, "ship": 3.3}
}

st.subheader("🛒 수수료 및 과세 설정")
selected_platform = st.selectbox("쇼핑몰 선택", list(platform_db.keys()))

# 선택한 마켓의 기본값 가져오기
defaults = platform_db[selected_platform]

# 모바일 가로 배열을 위해 3분할 (수동 수정 가능)
col_fee1, col_fee2, col_fee3 = st.columns(3)
with col_fee1:
    cat_rate = st.number_input("카테고리 (%)", value=defaults["cat"], step=0.1)
with col_fee2:
    link_rate = st.number_input("연동 수수료 (%)", value=defaults["link"], step=0.1)
with col_fee3:
    ship_rate = st.number_input("배송비 수수료 (%)", value=defaults["ship"], step=0.1)

# 부가세 설정 (기본 일반과세자 10%)
vat_rate = st.number_input("부가세율 (%)", value=10, step=1)

st.markdown("---")

# 2. 금액 입력 섹션
st.subheader("💰 매출 입력")
sell_price = st.number_input("판매가격 (원)", min_value=0, step=1000, value=0)
customer_shipping = st.number_input("배송비 [고객부담] (원)", min_value=0, step=500, value=0)

st.subheader("📦 매입 입력")
buy_price = st.number_input("매입가격 (원)", min_value=0, step=1000, value=0)
buy_shipping = st.number_input("매입운송비 (원)", min_value=0, step=500, value=3000) # 기본값 3,000원
other_cost = st.number_input("기타(포장비, 사은품 등) (원)", min_value=0, step=100, value=300) # 기본값 300원

st.subheader("🚚 지출 및 마케팅")
seller_shipping = st.number_input("운임비(택배비) [판매자부담] (원)", min_value=0, step=500, value=0)
ad_cost = st.number_input("광고비(마케팅) (원)", min_value=0, step=1000, value=0)

# 3. 상세 정산 및 부가세 로직 계산
total_sales = sell_price + customer_shipping

# 세부 수수료 계산
fee_cat = sell_price * (cat_rate / 100)
fee_link = sell_price * (link_rate / 100)
fee_ship = customer_shipping * (ship_rate / 100)
total_platform_fee = fee_cat + fee_link + fee_ship

# 정산금액 산출
settlement_amount = total_sales - total_platform_fee

# 총 매입비용 산출
total_cost = buy_price + buy_shipping + other_cost + seller_shipping + ad_cost

# 부가세 계산 (국내 일반과세자 매산 방식: 모든 입출금액이 부가세 포함 기준일 때 마진의 1/11 납부)
pre_vat_margin = settlement_amount - total_cost
if pre_vat_margin > 0:
    estimated_vat = pre_vat_margin / (1 + (vat_rate / 100)) * (vat_rate / 100)
else:
    estimated_vat = 0.0 # 적자일 경우 납부 부가세는 없음 (또는 환급이나 단품 계산에선 0 처리)

# 최종 순수익 및 마진율
net_profit = pre_vat_margin - estimated_vat
margin_rate = (net_profit / total_sales) * 100 if total_sales > 0 else 0.0

st.markdown("---")

# 4. 결과 출력
st.subheader("📊 최종 계산 결과")
st.metric(label="정산금액 (플랫폼 공제 후)", value=f"{int(settlement_amount):,} 원")
st.metric(label="예상 납부 부가세 (10%)", value=f"{int(estimated_vat):,} 원")
st.metric(label="최종 순수익", value=f"{int(net_profit):,} 원")
st.metric(label="최종 마진율", value=f"{margin_rate:.2f} %")

with st.expander("🔍 수수료 상세 보기"):
    st.write(f"• 카테고리 수수료: {int(fee_cat):,}원")
    st.write(f"• 연동 수수료: {int(fee_link):,}원")
    st.write(f"• 배송비 수수료: {int(fee_ship):,}원")
    st.write(f"• 총 수수료 합계: {int(total_platform_fee):,}원")

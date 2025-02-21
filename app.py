import re
import streamlit as st

# ✅ قائمة الوظائف المشبوهة
SUSPICIOUS_FUNCTIONS = {
    "⚠️ عمليات نقل مشبوهة": ["transferFrom", "approve", "setApprovalForAll"],
    "🔴 استدعاءات خارجية خطيرة": ["delegatecall", "callcode", "selfdestruct", "tx.origin", "assembly", "create2"],
    "⚠️ التحكم في ملكية العقد": ["renounceOwnership", "transferOwnership"],
    "⚠️ تعديل الضرائب والرسوم": [
        "setTaxWallet", "_initialBuyTax", "_initialSellTax", "_finalBuyTax", "_finalSellTax",
        "_reduceBuyTaxAt", "_reduceSellTaxAt"
    ],
    "🔴 وظائف تقييد التداول (هاني بوت محتمل)": ["enableTrading", "openTrading", "tradingOpen", "removeLimits"],
    "⚠️ تعاملات مع محافظ مشبوهة": ["_taxWallet", "_vbaddr", "_vitalik", "_hulezhi"],
    "⚠️ قيود بيع وشراء العملات": ["_maxTxAmount", "_maxWalletSize", "add", "del", "isBot", "bots", "canSell"],
    "⚠️ تحويل الضرائب إلى عنوان معين": ["_taxWallet", "sendEthFeeTo"],
    "🔴 التلاعب بعملية التبادل": ["swapTokensForEth", "swapExactTokensForETHSupportingFeeOnTransferTokens"],
    "⚠️ امتلاك المحفظة لصلاحيات عالية": ["onlyOwner", "Ownable", "transferOwnership", "renounceOwnership"],
    "🔴 فرض رسوم تداول متغيرة": ["_initialBuyTax", "_initialSellTax", "_finalBuyTax", "_finalSellTax"]
}

# ✅ استخراج كود العقد الذكي
def extract_smart_contract(text):
    clean_code = re.sub(r'\/\*[\s\S]*?\*\/|\/\/.*', '', text)
    return clean_code.strip()

# ✅ استخراج نسبة عمولة الشراء والبيع
def extract_taxes(code):
    buy_tax_match = re.search(r"_initialBuyTax\s*=\s*(\d+)", code)
    sell_tax_match = re.search(r"_initialSellTax\s*=\s*(\d+)", code)

    buy_tax = int(buy_tax_match.group(1)) if buy_tax_match else 0
    sell_tax = int(sell_tax_match.group(1)) if sell_tax_match else 0

    return buy_tax, sell_tax

# ✅ تحليل كود العقد الذكي
def analyze_contract(code):
    findings = []
    risk_score = 0

    # استخراج الضرائب
    buy_tax, sell_tax = extract_taxes(code)

    for category, functions in SUSPICIOUS_FUNCTIONS.items():
        detected = [f"<code style='color: #ff9900; font-weight: bold;'>{func}</code>" for func in functions if func in code]
        if detected:
            findings.append(f"<b style='color: #333;'>🔹 {category}:</b><br>" + "<br>".join(detected))
            risk_score += len(detected) * 10  

    # 🟢🟡🟠🔴 تصنيف مستوى الخطورة
    if risk_score == 0:
        security_status = "<h3 style='color: green;'>🟢 العقد آمن بنسبة 100%</h3><p>✅ لم يتم العثور على وظائف مشبوهة.</p>"
    elif risk_score <= 30:
        security_status = f"<h3 style='color: yellow;'>🟡 مستوى خطورة منخفض ({risk_score}%)</h3><p>⚠️ يحتوي على بعض الوظائف المشبوهة لكنها ليست بالضرورة خطيرة.</p>"
    elif risk_score <= 70:
        security_status = f"<h3 style='color: orange;'>🟠 مستوى خطورة متوسط ({risk_score}%)</h3><p>⚠️ يحتوي على وظائف قد تكون خطيرة، يُفضل التحقق يدويًا.</p>"
    else:
        security_status = f"<h3 style='color: red;'>🔴 مستوى خطورة عالي جدًا ({risk_score}%)</h3><p>🚨 يحتوي على وظائف مشبوهة جدًا وقد يكون عقدًا احتياليًا!</p>"

    # ✅ إضافة نسبة الضرائب إلى التقرير
    tax_info = f"""
    <h3 style='color: #007bff;'>📊 نسبة العمولات</h3>
    <p><b>💰 عمولة الشراء:</b> {buy_tax}%</p>
    <p><b>💰 عمولة البيع:</b> {sell_tax}%</p>
    """

    result = security_status + tax_info + "<br>".join(findings)
    return result

# ✅ واجهة Streamlit
st.title("🔍 تحليل العقود الذكية")

# ✅ إدخال كود العقد الذكي
code = st.text_area("📌 أدخل كود العقد الذكي هنا:")

# ✅ زر التحليل
if st.button("🔍 تحليل العقد"):
    contract_code = extract_smart_contract(code)
    if contract_code:
        result = analyze_contract(contract_code)
        formatted_result = f"""
        <div dir="rtl" style="text-align: right; font-family: Arial, sans-serif; background-color: #f5f5f5; 
            padding: 20px; border-radius: 10px; box-shadow: 2px 2px 10px rgba(0, 0, 0, 0.1); color: #222;">
            {result}
        </div>
        """
        st.markdown(formatted_result, unsafe_allow_html=True)
    else:
        st.error("❌ لم يتم العثور على كود عقد ذكي صالح! الرجاء إدخال كود صحيح.")

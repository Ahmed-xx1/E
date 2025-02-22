import re
import streamlit as st

# ✅ تخصيص واجهة Streamlit بتصميم متناسق
st.markdown(
    """
    <style>
        body {
            background-color: #f8f9fa;
            color: black;
        }
        .report-container {
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 2px 2px 10px rgba(0, 0, 0, 0.1);
            text-align: right;
        }
        .risk-level {
            font-size: 22px;
            font-weight: bold;
        }
        .high-risk {
            color: red;
        }
        .medium-risk {
            color: orange;
        }
        .low-risk {
            color: green;
        }
        .code-box {
            background-color: #f1f1f1;
            padding: 8px;
            border-radius: 5px;
            font-weight: bold;
            display: inline-block;
        }
        .section-title {
            font-size: 20px;
            font-weight: bold;
            color: #007bff;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# ✅ قائمة الوظائف المشبوهة
SUSPICIOUS_FUNCTIONS = {
    "⚠️ عمليات نقل مشبوهة": ["transferFrom", "approve", "setApprovalForAll"],
    "🔴 استدعاءات خارجية خطيرة": ["delegatecall", "callcode", "selfdestruct", "tx.origin", "assembly", "create2"],
    "⚠️ التحكم في ملكية العقد": ["renounceOwnership", "transferOwnership"],
    "⚠️ تعديل الضرائب والرسوم": ["_initialBuyTax", "_initialSellTax", "_finalBuyTax", "_finalSellTax"],
    "🔴 تقييد التداول (هاني بوت محتمل)": ["enableTrading", "openTrading", "tradingOpen", "removeLimits"],
    "⚠️ تحويل الضرائب إلى عنوان معين": ["_taxWallet", "sendEthFeeTo"],
    "🔴 التلاعب بعملية التبادل": ["swapTokensForEth", "swapExactTokensForETHSupportingFeeOnTransferTokens"]
}

# ✅ أنواع البلاك ليست
BLACKLIST_TYPES = {
    "🔴 حظر المحافظ": ["_isBlacklisted", "blacklist", "addBlacklist", "removeBlacklist", "bots"],
    "⚠️ قيود على البيع والشراء": ["isBot", "canSell", "_maxTxAmount", "_maxWalletSize"],
    "🔴 التقييد الزمني على التداول": ["_initialSellTax", "_finalSellTax", "_preventSwapBefore"]
}

# ✅ قائمة العقود المشهورة لحماية السيولة
LIQUIDITY_LOCK_ADDRESSES = {
    "Unicrypt": "0x8bCb14797B82C56821C8f36aE1b19D0A1cB5e98F",
    "Team Finance": "0xB41f5F9a1734b48E2cb2FF3fA35e1D1B8A21A66E",
    "DxSale": "0xC0A4aCc3734e08A96eB58B27d15cB8E3eC8DdBde"
}

# ✅ استخراج كود العقد الذكي
def extract_smart_contract(text):
    return re.sub(r'\/\*[\s\S]*?\*\/|\/\/.*', '', text).strip()

# ✅ استخراج نسبة عمولة الشراء والبيع
def extract_taxes(code):
    buy_tax_match = re.search(r"_initialBuyTax\s*=\s*(\d+)", code)
    sell_tax_match = re.search(r"_initialSellTax\s*=\s*(\d+)", code)

    buy_tax = int(buy_tax_match.group(1)) if buy_tax_match else 0
    sell_tax = int(sell_tax_match.group(1)) if sell_tax_match else 0

    return buy_tax, sell_tax

# ✅ التحقق من قفل السيولة
def check_liquidity_lock(code):
    for name, address in LIQUIDITY_LOCK_ADDRESSES.items():
        if address.lower() in code.lower():
            return f"<p style='color: green;'>✅ السيولة مقفلة في {name} 🔒</p>"
    return "<p style='color: red;'>🚨 السيولة غير مقفلة! ⚠️</p>"

# ✅ التحقق من وجود بلاك ليست
def check_blacklist(code):
    findings = []
    for category, functions in BLACKLIST_TYPES.items():
        detected = [f"<span class='code-box'>{func}</span>" for func in functions if func in code]
        if detected:
            findings.append(f"<b>{category}:</b> " + ", ".join(detected))
    return findings

# ✅ تحليل كود العقد الذكي
def analyze_contract(code):
    findings = []
    risk_score = 0

    # استخراج الضرائب
    buy_tax, sell_tax = extract_taxes(code)

    for category, functions in SUSPICIOUS_FUNCTIONS.items():
        detected = [f"<span class='code-box'>{func}</span>" for func in functions if func in code]
        if detected:
            findings.append(f"<b>{category}:</b> " + ", ".join(detected))
            risk_score += len(detected) * 10  

    # ✅ التحقق من البلاك ليست
    blacklist_findings = check_blacklist(code)
    if blacklist_findings:
        findings.extend(blacklist_findings)
        risk_score += 20  # إضافة درجة خطورة إذا كان هناك بلاك ليست

    # ✅ التحقق من قفل السيولة
    liquidity_status = check_liquidity_lock(code)

    # 🟢🟡🟠🔴 تصنيف مستوى الخطورة
    if risk_score == 0:
        security_status = "<p class='risk-level low-risk'>🟢 العقد آمن بنسبة 100% ✅</p>"
    elif risk_score <= 30:
        security_status = f"<p class='risk-level medium-risk'>🟡 مستوى خطورة منخفض ({risk_score}%) ⚠️</p>"
    elif risk_score <= 70:
        security_status = f"<p class='risk-level medium-risk'>🟠 مستوى خطورة متوسط ({risk_score}%) ⚠️</p>"
    else:
        security_status = f"<p class='risk-level high-risk'>🔴 مستوى خطورة عالي جدًا ({risk_score}%) 🚨</p>"

    # ✅ إضافة نسبة الضرائب إلى التقرير
    tax_info = f"""
    <div class="section-title">📊 نسبة العمولات</div>
    <p>💰 <b>عمولة الشراء:</b> {buy_tax}%</p>
    <p>💰 <b>عمولة البيع:</b> {sell_tax}%</p>
    """

    result = f"""
    <div class="report-container">
        {security_status}
        {tax_info}
        {liquidity_status}
        {"<br>".join(findings)}
    </div>
    """
    return result

# ✅ واجهة التطبيق
st.title("🔍 تحليل العقود الذكية")
code = st.text_area("📌 أدخل كود العقد الذكي هنا:")

if st.button("تحليل العقد"):
    contract_code = extract_smart_contract(code)
    if contract_code:
        result = analyze_contract(contract_code)
        st.markdown(result, unsafe_allow_html=True)
    else:
        st.error("❌ لم يتم العثور على كود عقد ذكي صالح! الرجاء إدخال كود صحيح.")

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

# ✅ أنواع البلاك ليست
BLACKLIST_TYPES = {
    "🔴 حظر المحافظ (Blacklist Addresses)": ["_isBlacklisted", "blacklist", "addBlacklist", "removeBlacklist", "bots"],
    "⚠️ قيود على البيع والشراء (Anti-Bot Rules)": ["isBot", "canSell", "_maxTxAmount", "_maxWalletSize"],
    "🔴 التقييد الزمني على التداول (Honeypot)": ["_initialSellTax", "_finalSellTax", "_preventSwapBefore"]
}

# ✅ قائمة العقود المشهورة لحماية السيولة
LIQUIDITY_LOCK_ADDRESSES = {
    "Unicrypt": "0x8bCb14797B82C56821C8f36aE1b19D0A1cB5e98F",
    "Team Finance": "0xB41f5F9a1734b48E2cb2FF3fA35e1D1B8A21A66E",
    "DxSale": "0xC0A4aCc3734e08A96eB58B27d15cB8E3eC8DdBde"
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

# ✅ التحقق من قفل السيولة
def check_liquidity_lock(code):
    for name, address in LIQUIDITY_LOCK_ADDRESSES.items():
        if address.lower() in code.lower():
            return f"✅ السيولة مقفلة في {name} 🔒\nتم العثور على عنوان القفل: `{address}`"
    return "🚨 السيولة غير مقفلة! ⚠️"

# ✅ التحقق من وجود بلاك ليست
def check_blacklist(code):
    findings = []
    for category, functions in BLACKLIST_TYPES.items():
        detected = [f"`{func}`" for func in functions if func in code]
        if detected:
            findings.append(f"🔹 **{category}:**\n" + "\n".join(detected))
    return findings

# ✅ تحليل كود العقد الذكي
def analyze_contract(code):
    findings = []
    risk_score = 0

    # استخراج الضرائب
    buy_tax, sell_tax = extract_taxes(code)

    for category, functions in SUSPICIOUS_FUNCTIONS.items():
        detected = [f"`{func}`" for func in functions if func in code]
        if detected:
            findings.append(f"🔹 **{category}:**\n" + "\n".join(detected))
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
        security_status = "🟢 **العقد آمن بنسبة 100%** ✅"
    elif risk_score <= 30:
        security_status = f"🟡 **مستوى خطورة منخفض ({risk_score}%)** ⚠️"
    elif risk_score <= 70:
        security_status = f"🟠 **مستوى خطورة متوسط ({risk_score}%)** ⚠️"
    else:
        security_status = f"🔴 **مستوى خطورة عالي جدًا ({risk_score}%)** 🚨"

    # ✅ إضافة نسبة الضرائب إلى التقرير
    tax_info = f"""
    ### 📊 نسبة العمولات:
    - 💰 **عمولة الشراء:** {buy_tax}%
    - 💰 **عمولة البيع:** {sell_tax}%
    """

    result = f"## {security_status}\n\n{tax_info}\n\n**{liquidity_status}**\n\n" + "\n\n".join(findings)
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
        st.markdown(result, unsafe_allow_html=True)
    else:
        st.error("❌ لم يتم العثور على كود عقد ذكي صالح! الرجاء إدخال كود صحيح.")

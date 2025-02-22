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
            return f"<h3 style='color: green;'>✅ السيولة مقفلة في {name}</h3><p>🔒 تم العثور على عنوان القفل: <b>{address}</b></p>"
    return "<h3 style='color: red;'>🚨 السيولة غير مقفلة!</h3><p>⚠️ لم يتم العثور على أي عقد تأمين للسيولة.</p>"

# ✅ التحقق من وجود بلاك ليست
def check_blacklist(code):
    findings = []
    for category, functions in BLACKLIST_TYPES.items():
        detected = [f"<code style='color: #ff9900; font-weight: bold;'>{func}</code>" for func in functions if func in code]
        if detected:
            findings.append(f"<b style='color: #333;'>🔹 {category}:</b><br>" + "<br>".join(detected))
    return findings

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

    # ✅ التحقق من البلاك ليست
    blacklist_findings = check_blacklist(code)
    if blacklist_findings:
        findings.extend(blacklist_findings)
        risk_score += 20  # إضافة درجة خطورة إذا كان هناك بلاك ليست

    # ✅ التحقق من قفل السيولة
    liquidity_status = check_liquidity_lock(code)

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

    result = security_status + tax_info + liquidity_status + "<br>".join(findings)
    return result

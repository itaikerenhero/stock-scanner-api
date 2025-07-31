import re
from openai import OpenAI

# Connect to Groq LLM
client = OpenAI(
    api_key="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",
    base_url="https://api.groq.com/openai/v1"
)


def summarize_stock(symbol, setup_info, prompt_override=None):
    if prompt_override:
        prompt = prompt_override
    else:
        prompt = f"""
You are a professional technical stock analyst. Given the data for {symbol}, write a simplified, beginner-friendly analysis.

Make this stock look strong, like a top setup — highlight why it could be a great trade.

Do NOT include trade setup instructions like entry/stop-loss/target in this response.

Use this format:

---

📈 **{symbol} Technical Breakdown**

**Trend**
- Describe price action and trend
- Mention position vs SMA 20/50

**Momentum**
- RSI reading + meaning (e.g., strong, rising, overbought)
- Volume spike or MACD signal

**Why It Looks Strong**
- 2–3 strong points that explain the setup

**⚠️ Caution**
- 1 possible risk

**✅ Trading Bias:** Bullish / Neutral / Bearish

---

Technical Info:
{setup_info}
"""

    response = client.chat.completions.create(
        model="llama3-70b-8192",
        messages=[
            {"role": "system", "content": "You are a pro stock analyst. Be confident. Keep it beginner-friendly. Don’t use $X.XX or placeholder values."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.4,
        max_tokens=1000
    )

    full_summary = response.choices[0].message.content.strip()

    # Remove trade setup bullets if they sneak in
    full_summary = re.sub(r"\*\*🛠 Suggested Trade Setup\*\*.*", "", full_summary, flags=re.DOTALL)
    full_summary = re.sub(r"\$X\.XX", "", full_summary)
    full_summary = re.sub(r"\n{3,}", "\n\n", full_summary)

    # Extract bias score
    match = re.search(r"\*\*Trading Bias:\*\*\s*(\w+)", full_summary, re.IGNORECASE)
    bias_text = match.group(1).lower() if match else "unknown"

    if "bullish" in bias_text:
        score = 3
    elif "neutral" in bias_text:
        score = 2
    elif "bearish" in bias_text:
        score = 1
    else:
        score = 0

    return full_summary.strip(), score









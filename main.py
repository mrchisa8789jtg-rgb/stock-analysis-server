from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import yfinance as yf

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"status": "online", "message": "ระบบทำงานปกติ"}

@app.get("/analyze/{symbol}")
def analyze_stock(symbol: str, interval: str = "5m"):
    if not symbol.endswith(".BK"):
        symbol = f"{symbol}.BK"

    try:
        ticker = yf.Ticker(symbol)
        data = ticker.history(period="1d", interval=interval)
        
        if data.empty:
            return {"error": f"ไม่พบข้อมูล {symbol}"}

        latest = data.iloc[-1]
        price = round(float(latest["Close"]), 2)

        data["MA5"] = data["Close"].rolling(window=5).mean()
        data["MA15"] = data["Close"].rolling(window=15).mean()

        ma5_now = float(data["MA5"].iloc[-1])
        ma15_now = float(data["MA15"].iloc[-1])
        
        if ma5_now > ma15_now:
            signal = "ซื้อ"
        elif ma5_now < ma15_now:
            signal = "ขาย"
        else:
            signal = "รอ"

        take_profit = round(price * 1.03, 2)
        stop_loss = round(price * 0.985, 2)

        chart_data = []
        for _, row in data.iterrows():
            chart_data.append({
                "Close": round(float(row["Close"]), 2),
                "MA5": round(float(row["MA5"]), 2) if not row["MA5"] != row["MA5"] else None,
                "MA15": round(float(row["MA15"]), 2) if not row["MA15"] != row["MA15"] else None
            })

        return {
            "symbol": symbol.replace(".BK", ""),
            "price": price,
            "signal": signal,
            "entry_price": price,
            "take_profit_price": take_profit,
            "stop_loss_price": stop_loss,
            "chart": chart_data
        }

    except Exception as e:
        return {"error": str(e)}

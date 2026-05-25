from telethon import TelegramClient, events
import joblib
import json
import pandas as pd
import numpy as np

from memory import update_history, get_features, history
from parser import parse_match

# --- YOUR API ---
api_id = 30680366
api_hash = "a13532c39b889ab227cde5861caa5637"

CHANNEL = "https://t.me/Statistica_Besplatno"

# --- LOAD MODEL ---
model = joblib.load("model_ht.pkl")
features = json.load(open("features.json"))

client = TelegramClient("cloud_session", api_id, api_hash)

print("🔌 Connecting to Telegram...")

# --- FEATURE BUILDER ---
def build_features(timestamp, hist):
    hour = timestamp.hour
    minute = timestamp.minute
    
    return pd.DataFrame([{
        'hour_sin': np.sin(2*np.pi*hour/24),
        'hour_cos': np.cos(2*np.pi*hour/24),
        'minute_sin': np.sin(2*np.pi*minute/60),
        'minute_cos': np.cos(2*np.pi*minute/60),
        'day_of_week': timestamp.weekday(),
        'prev_2_ht_even': hist['prev_2'],
        'prev_3_ht_even': hist['prev_3'],
        'prev_4_ht_even': hist['prev_4'],
        'ht_even_last_5': hist['last_5'],
        'ht_even_last_10': hist['last_10'],
        'ht_streak': hist['streak']
    }])

# --- PRELOAD HISTORY ---
async def preload_history(limit=500):
    print("⏳ Loading past history...")
    
    async for msg in client.iter_messages(CHANNEL, limit=limit):
        if msg.text:
            parsed = parse_match(msg.text, msg.date)
            
            if parsed:
                ht_total = parsed['ht_A'] + parsed['ht_B']
                ht_even = int(ht_total % 2 == 0)
                update_history(ht_even)
    
    print(f"✅ Loaded {len(history)} past matches")

# --- LISTENER ---
@client.on(events.NewMessage(chats=CHANNEL))
async def handler(event):
    
    text = event.message.message
    date = event.message.date
    
    print("\n📩 New message received:")
    print(text)
    
    parsed = parse_match(text, date)
    
    if not parsed:
        print("❌ Could not parse")
        return
    
    hist = get_features()
    
    if hist is None:
        print("⏳ Not enough history yet")
        ht_total = parsed['ht_A'] + parsed['ht_B']
        update_history(int(ht_total % 2 == 0))
        return
    
    # --- BUILD FEATURES ---
    X = build_features(parsed['timestamp'], hist)
    X = X[features]  # ensure correct order
    
    # --- PREDICT ---
    pred = model.predict(X)[0]
    prob = model.predict_proba(X).max()
    
    print(f"🤖 Prediction: {'EVEN' if pred else 'ODD'} ({prob:.2f})")
    
    # --- STRONG FILTER (IMPROVES PROFITABILITY) ---
    if prob > 0.80 and hist['last_10'] > 0.6 and hist['streak'] >= 1:
        print("🔥 STRONG SIGNAL 🔥")
        print(f"💰 BET: {'EVEN' if pred else 'ODD'}")
    else:
        print("⏭️ Skipping (low quality signal)")
    
    # --- UPDATE MEMORY AFTER ---
    ht_total = parsed['ht_A'] + parsed['ht_B']
    ht_even = int(ht_total % 2 == 0)
    update_history(ht_even)

# --- MAIN ---
async def main():
    await preload_history()
    print("🚀 Listening to channel...")
    await client.run_until_disconnected()

with client:
    client.loop.run_until_complete(main())
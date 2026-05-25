<<<<<<< HEAD
import numpy as np

# --- LIVE MEMORY ---
history = []

# how many recent matches to keep in memory
MAX_HISTORY = 200


# --- UPDATE MEMORY ---
def update_history(value):
    """
    value:
        1 = EVEN
        0 = ODD
    """
    
    # safety check
    if value not in [0, 1]:
        print(f"⚠️ Invalid value ignored: {value}")
        return
    
    history.append(int(value))
    
    # keep only latest MAX_HISTORY matches
    if len(history) > MAX_HISTORY:
        history.pop(0)


# --- FEATURE GENERATION ---
def get_features():
    
    # need minimum history
    if len(history) < 10:
        return None
    
    # rolling averages
    last_5 = float(np.mean(history[-5:]))
    last_10 = float(np.mean(history[-10:]))
    
    # optional stronger short-term momentum
    last_3 = float(np.mean(history[-3:]))
    
    # streak calculation
    streak = 0
    
    for i in range(len(history) - 1, 0, -1):
        if history[i] == history[i - 1]:
            streak += 1
        else:
            break
    
    return {
        # previous outcomes
        "prev_2": history[-2],
        "prev_3": history[-3],
        "prev_4": history[-4],
        
        # rolling stats
        "last_3": last_3,
        "last_5": last_5,
        "last_10": last_10,
        
        # streak strength
        "streak": streak,
        
        # optional diagnostics
        "history_size": len(history)

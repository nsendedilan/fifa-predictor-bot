import re

def parse_match(text, date):
    try:
        ht = re.search(r"1 Тайм.*\((\d+)\s:\s(\d+)\)", text)
        
        if not ht:
            return None
        
        ht_A = int(ht.group(1))
        ht_B = int(ht.group(2))
        
        return {
            "ht_A": ht_A,
            "ht_B": ht_B,
            "timestamp": date
        }
    except:
        return None
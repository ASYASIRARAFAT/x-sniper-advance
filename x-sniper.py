import asyncio, random, hashlib, sys, os, requests, re
from telethon import TelegramClient, events, errors

# --- 🎨 PRO COLORS ---
G, Y, R, C, W, B = '\033[92m', '\033[93m', '\033[91m', '\033[96m', '\033[0m', '\033[1m'

# --- ⚙️ CONFIGURATION ---
RAW_LINK = "https://raw.githubusercontent.com/ASYASIRARAFAT/x-sniper-advance/main/approved.txt"
FB_LINK = "https://www.facebook.com/Yasir.Arafat.Hacker.Official"
STOCK_CHANNEL_ID = -1003280015883 
BOT_USERNAME = 'XPrepaidsExchangeBot'

# --- 🛠️ UTILS ---
def ui_header():
    os.system('clear')
    print(f"{C}{B}╔══════════════════════════════════════════════════════════╗")
    print(f"║                {W}{B}CYBER SNIPER v6.0 PRO{C}{B}                     ║")
    print(f"║             {W}THE ULTIMATE HUNTING ENGINE{C}{B}                  ║")
    print(f"╚══════════════════════════════════════════════════════════╝{W}")

def log(msg, type="info"):
    if type == "success": print(f"{G}[✔] {msg}{W}")
    elif type == "error": print(f"{R}[✘] {msg}{W}")
    elif type == "wait": print(f"{Y}[•] {msg}{W}")
    else: print(f"{C}[•] {msg}{W}")

# --- 🔐 SECURITY ---
def get_hwid():
    try:
        import subprocess
        cpu = subprocess.check_output('uname -a', shell=True).decode()
        user = os.popen('whoami').read().strip()
        return hashlib.sha256((cpu + user).encode()).hexdigest()[:12].upper()
    except: return "UNKNOWN-ID"

# --- 🎯 GLOBAL STATE ---
targets = []
is_attacking = False
auto_add_enabled = False
min_bal, max_bal = 0.0, 0.0
reg_required = "no"
click_lock = asyncio.Lock()

# --- ⚙️ SESSION ---
def load_config():
    if os.path.exists("config.txt"):
        with open("config.txt", "r") as f:
            lines = f.read().splitlines()
            if len(lines) >= 2: return int(lines[0]), lines[1]
    ui_header()
    log("Initial Setup Required", "wait")
    api_id = input(f"{C}Enter API ID: {W}"); api_hash = input(f"{C}Enter API Hash: {W}")
    with open("config.txt", "w") as f: f.write(f"{api_id}\n{api_hash}")
    return int(api_id), api_hash

API_ID, API_HASH = load_config()
client = TelegramClient('sniper_session', API_ID, API_HASH)

# --- 🛰️ SCRAPPER (Auto Add with Anti-Duplication) ---
@client.on(events.NewMessage(chats=STOCK_CHANNEL_ID))
async def stock_scrapper(event):
    global targets
    if not auto_add_enabled: return
    text = event.raw_text
    if "Used Google: No" not in text: return 
    try:
        bin_m = re.search(r"BIN: (\d+xx)", text)
        bal_m = re.search(r"Balance: USD \$([\d\.\,]+)", text)
        reg_m = re.search(r"Registered: (\w+)", text)
        if bin_m and bal_m:
            c_bin = bin_m.group(1).lower()
            c_bal = round(float(bal_m.group(1).replace(',', '')), 2)
            is_reg = reg_m.group(1).lower()
            if min_bal <= c_bal <= max_bal:
                if (reg_required == "yes" and is_reg == "true") or (reg_required == "no" and is_reg == "false"):
                    # Target Duplication Check
                    if not any(t['bin'] == c_bin and t['bal'] == c_bal for t in targets):
                        targets.append({'bin': c_bin, 'bal': c_bal})
                        log(f"Auto-Added from Stock: {c_bin} (${c_bal})", "success")
    except: pass

# --- 📩 COMMAND HANDLER ---
@client.on(events.NewMessage(outgoing=True))
async def cmd_handler(event):
    global targets, is_attacking
    t = event.raw_text.lower().strip()
    try:
        if t.startswith("add"):
            _, b, bal = t.split()
            c_bin = b.lower()
            c_bal = round(float(bal), 2)
            # Target Duplication Check
            if not any(target['bin'] == c_bin and target['bal'] == c_bal for target in targets):
                targets.append({'bin': c_bin, 'bal': c_bal})
                log(f"Target Added: {c_bin}", "success")
            else:
                log(f"Target already exists: {c_bin}", "wait")
        elif t.startswith("cancel"):
            idx = int(t.split()[1]) - 1
            if 0 <= idx < len(targets):
                removed = targets.pop(idx)
                log(f"Target Removed: {removed['bin']}", "error")
        elif t == "start":
            is_attacking = True
            log("Sniper Mode: ACTIVE", "success")
        elif t == "stop":
            is_attacking = False
            log("Sniper Mode: PAUSED", "wait")
    except: pass

# --- ⚡ THE HUNTING ENGINE ---
@client.on(events.NewMessage(chats=BOT_USERNAME))
@client.on(events.MessageEdited(chats=BOT_USERNAME))
async def sniper_engine(event):
    global is_attacking
    msg_text = event.message.text.lower()
    
    # 1. Smart Pause (Confirm/Success)
    if "confirm your purchase" in msg_text or "successfully purchased" in msg_text:
        is_attacking = False
        log("PAUSED: Action required in Bot (Confirm/Success).", "wait")
        return
        
    # 2. Ignore Sold Out (Continue Hunting)
    if "already bought" in msg_text or "someone else" in msg_text:
        log("Item Sold Out! Continuing Scan...", "error")
        is_attacking = True
        return
    
    if not is_attacking or not event.message.buttons: return
    if "main listings" not in msg_text and "total cards" not in msg_text: return
    
    btn_to_click = None
    flat = [b for r in event.message.buttons for b in r]
    
    # 3. Advanced 3-Step Purchase Detection
    for i, b in enumerate(flat):
        btn_txt = b.text.lower()
        for t in targets:
            if t['bin'] in btn_txt:
                nums = [round(float(n.replace(',', '')), 2) for n in re.findall(r"\d+\.\d+", btn_txt)]
                if any(abs(n - t['bal']) <= 0.01 for n in nums):
                    log(f"MATCH FOUND: {b.text}", "success")
                    
                    # STEP 1: Same Row
                    for row in event.message.buttons:
                        if b in row:
                            for pb in row:
                                if "purchase" in pb.text.lower():
                                    btn_to_click = pb
                                    break
                            if btn_to_click: break
                    
                    # STEP 2: Next Rows Check
                    if not btn_to_click:
                        row_index = next(idx for idx, r in enumerate(event.message.buttons) if b in r)
                        for r in event.message.buttons[row_index+1:row_index+3]:
                            for pb in r:
                                if "purchase" in pb.text.lower():
                                    btn_to_click = pb
                                    break
                            if btn_to_click: break
                    
                    # STEP 3: Fallback Nearby
                    if not btn_to_click:
                        for pb in flat[i:i+4]:
                            if "purchase" in pb.text.lower():
                                btn_to_click = pb
                                break
                    break
        if btn_to_click: break

    # --- CLICK EXECUTION OR REFRESH ---
    if btn_to_click:
        async with click_lock:
            is_attacking = False # Pause scanning to prevent double-hitting
            log("Executing Purchase Click...", "wait")
            await btn_to_click.click()
            await asyncio.sleep(0.15) # Double Click Delay Optimization
            await btn_to_click.click()
            log("Purchase Completed! Waiting for confirmation...", "success")
            return
    else:
        # Restore Refresh System
        refresh_btn = next((b for b in flat if any(k in b.text for k in ["Refresh","🔄","Reload"])), None)
        if refresh_btn:
            await asyncio.sleep(random.uniform(0.2, 0.4))
            try:
                await refresh_btn.click()
            except: pass

# --- 🖥️ MENU SYSTEM ---
async def main():
    ui_header()
    uid = get_hwid()
    log("Verifying HWID...", "wait")
    try:
        res = requests.get(RAW_LINK, timeout=10).text
        if uid not in res:
            log(f"ACCESS DENIED! HWID: {uid}", "error")
            print(f"{Y}Contact Admin: {FB_LINK}{W}"); sys.exit()
        log("Access Granted!", "success")
    except: log("Security Check Failed!", "error"); sys.exit()
    
    await client.start()
    
    while True:
        ui_header()
        print(f"\n{G}[1]{W} Add Target Manually")
        print(f"{G}[2]{W} Auto-Add (Scrapper) Settings")
        print(f"{G}[3]{W} Show Watchlist & Manage")
        print(f"{G}[4]{W} START HUNTING ENGINE")
        print(f"{R}[X]{W} Exit Tool\n")
        
        choice = input(f"{C}x-sniper> {W}").lower().strip()
        
        if choice == "1":
            try:
                b = input(f"{C}BIN (e.g. 451129xx): {W}").lower()
                bal = round(float(input(f"{C}Balance: {W}")), 2)
                if not any(t['bin'] == b and t['bal'] == bal for t in targets):
                    targets.append({'bin': b, 'bal': bal})
                    log("Target Added Successfully!", "success")
                else:
                    log("Target already exists in Watchlist!", "error")
            except: log("Invalid Input!", "error")
            input("\nEnter to return...")
            
        elif choice == "2":
            try:
                rng = input(f"{C}Range (e.g. 5-20): {W}")
                reg = input(f"{C}Registered (yes/no): {W}").lower()
                l, h = map(float, rng.split('-'))
                globals().update({'min_bal':l, 'max_bal':h, 'reg_required':reg, 'auto_add_enabled':True})
                log("Scrapper Activated!", "success")
            except: log("Invalid Range format!", "error")
            input("\nEnter to return...")
            
        elif choice == "3":
            ui_header()
            print(f"\n{C}--- CURRENT WATCHLIST ---{W}")
            if not targets: print(f"{R}No targets added!{W}")
            for i, t in enumerate(targets, 1):
                print(f"{G}{i}.{W} BIN: {t['bin']} | Bal: ${t['bal']}")
            print(f"\n{Y}Tip: Type 'cancel [number]' in Bot chat to remove targets.{W}")
            input("\nEnter to return...")
            
        elif choice == "4":
            if not targets:
                log("Watchlist is empty! Add targets first.", "error")
                input("\nEnter to return...")
            else:
                globals()['is_attacking'] = True
                ui_header()
                log("SNIPER ENGINE IS LIVE AND SCANNING...", "success")
                log("Send 'start' in Bot chat to resume after a pause.", "wait")
                log("Send 'stop' in Bot chat to pause manually.", "wait")
                print(f"{C}--------------------------------------------------{W}")
                await client.run_until_disconnected()
                
        elif choice == "x":
            log("Exiting Engine...", "wait")
            sys.exit()

if __name__ == "__main__":
    client.loop.run_until_complete(main())

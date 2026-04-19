import asyncio, random, hashlib, sys, os, requests, re
from telethon import TelegramClient, events, errors

# --- 🎨 PRO COLORS ---
G, Y, R, C, W, B = '\033[92m', '\033[93m', '\033[91m', '\033[96m', '\033[0m', '\033[1m'

# --- ⚙️ CONFIGURATION ---
RAW_LINK = "https://raw.githubusercontent.com/ASYASIRARAFAT/x-sniper-advance/main/approved.txt"
FB_LINK = "https://www.facebook.com/Yasir.Arafat.Hacker.Official"
TUTORIAL_LINK = "https://github.com/ASYASIRARAFAT/x-sniper-advance#readme"
STOCK_CHANNEL_ID = -1003280015883 
BOT_USERNAME = 'XPrepaidsExchangeBot'

# --- 🛠️ UI HEADER ---
def ui_header():
    os.system('clear')
    print(f"{C}{B}╔══════════════════════════════════════════════════════════╗")
    print(f"║                      {W}{B}X SNIPER{C}{B}                            ║")
    print(f"║             {Y}Developed By Yasir Arafat{C}{B}                    ║")
    print(f"╚══════════════════════════════════════════════════════════╝{W}")

def log(msg, type="info"):
    if type == "success": print(f"{G}[✔] {msg}{W}")
    elif type == "error": print(f"{R}[✘] {msg}{W}")
    elif type == "wait": print(f"{Y}[•] {msg}{W}")
    else: print(f"{C}[•] {msg}{W}")

# --- ⚡ ASYNC INPUT HANDLER ---
async def async_input(prompt):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, input, prompt)

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

# --- ⚙️ SESSION SETUP ---
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

# --- 🛰️ SCRAPPER 1: STOCK CHANNEL ---
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
            c_bin = bin_m.group(1).lower().replace('x', '')
            c_bal = round(float(bal_m.group(1).replace(',', '')), 2)
            is_reg = reg_m.group(1).lower()
            
            if min_bal <= c_bal <= max_bal:
                if (reg_required == "yes" and is_reg == "true") or (reg_required == "no" and is_reg == "false"):
                    if not any(t['bin'] == c_bin and t['bal'] == c_bal for t in targets):
                        targets.append({'bin': c_bin, 'bal': c_bal})
                        log(f"Auto-Added from Stock: {c_bin} (${c_bal})", "success")
    except: pass

# --- 📩 COMMAND HANDLER (Telegram Stealth Mode) ---
@client.on(events.NewMessage(outgoing=True))
async def cmd_handler(event):
    global targets, is_attacking, auto_add_enabled, min_bal, max_bal, reg_required
    t = event.raw_text.lower().strip()
    is_command = False
    
    try:
        # 🔥 ম্যাজিক ১: 'add 435880xx 10' বা 'buy 435880xx 10'
        if t.startswith("add") or t.startswith("buy"):
            parts = t.split()
            if len(parts) >= 3:
                # 'xx' এবং '$' চিহ্ন মুছে ক্লিন করবে
                c_bin = parts[1].replace('x', '') 
                c_bal = round(float(parts[2].replace('$', '')), 2)
                
                if not any(target['bin'] == c_bin and target['bal'] == c_bal for target in targets):
                    targets.append({'bin': c_bin, 'bal': c_bal})
                    log(f"Target Loaded via Telegram: {c_bin} (${c_bal})", "success")
                else:
                    log(f"Target already exists: {c_bin}", "wait")
                
                is_attacking = True
                log("Sniper Mode ACTIVE", "success")
            is_command = True
            
        # 🔥 ম্যাজিক ২: 'autoadd 2-10 no' 
        elif t.startswith("autoadd"):
            parts = t.split()
            if len(parts) >= 3:
                rng = parts[1]
                reg = parts[2]
                try:
                    l, h = map(float, rng.split('-'))
                    min_bal, max_bal, reg_required = l, h, reg
                    auto_add_enabled = True
                    is_attacking = True 
                    log(f"Auto-Scraper Active! Range: ${l}-${h} | Reg: {reg}", "success")
                except:
                    log("Invalid autoadd format!", "error")
            is_command = True

        elif t.startswith("cancel"):
            idx = int(t.split()[1]) - 1
            if 0 <= idx < len(targets):
                removed = targets.pop(idx)
                log(f"Target Removed: {removed['bin']}", "error")
            is_command = True
            
        elif t == "start":
            is_attacking = True
            log("Sniper Mode ACTIVE", "success")
            is_command = True
            
        elif t == "stop":
            is_attacking = False
            log("Sniper Mode PAUSED", "wait")
            is_command = True
            
        # 🔥 ম্যাজিক ৩: 'confirm'
        elif t == "confirm":
            is_command = True
            log("Auto-Confirm triggered! Searching...", "wait")
            async for msg in client.iter_messages(BOT_USERNAME, limit=5):
                if msg.buttons:
                    for row in msg.buttons:
                        for b in row:
                            if "confirm" in b.text.lower() or "yes" in b.text.lower():
                                await b.click()
                                log("Confirm Button Clicked!", "success")
                                break

        # কমান্ড মেসেজ অটো ডিলিট (যাতে বট এরর না দেয়)
        if is_command:
            try: await event.delete()
            except: pass
            
    except: pass

# --- ⚡ THE HUNTING ENGINE ---
@client.on(events.NewMessage(chats=BOT_USERNAME))
@client.on(events.MessageEdited(chats=BOT_USERNAME))
async def sniper_engine(event):
    global is_attacking
    msg_text = event.message.text.lower()
    
    # 1. Smart Pause
    if "confirm your purchase" in msg_text or "successfully purchased" in msg_text:
        is_attacking = False
        log("PAUSED: Action required in Bot. (Type 'confirm' to auto-click)", "wait")
        return
        
    # 2. Ignore Sold Out
    if "already bought" in msg_text or "someone else" in msg_text:
        log("Item Sold Out! Continuing Scan...", "error")
        is_attacking = True
        return
    
    if not is_attacking or not event.message.buttons: return
    if "main listings" not in msg_text and "total cards" not in msg_text: return
    
    btn_to_click = None
    flat = [b for r in event.message.buttons for b in

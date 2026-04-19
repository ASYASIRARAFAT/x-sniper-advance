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

# --- 🛰️ SCRAPPER: STOCK CHANNEL ---
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

# --- 📩 COMMAND HANDLER (Telegram Smart Interface) ---
@client.on(events.NewMessage(outgoing=True))
async def cmd_handler(event):
    global targets, is_attacking, auto_add_enabled, min_bal, max_bal, reg_required
    t = event.raw_text.lower().strip()
    is_command = False
    try:
        # ১. 'add 435880xx 10' কমান্ড
        if t.startswith("add") or t.startswith("buy"):
            parts = t.split()
            if len(parts) >= 3:
                c_bin = parts[1].replace('x', '') 
                c_bal = round(float(parts[2].replace('$', '')), 2)
                if not any(target['bin'] == c_bin and target['bal'] == c_bal for target in targets):
                    targets.append({'bin': c_bin, 'bal': c_bal})
                    log(f"Target Added: {c_bin} (${c_bal})", "success")
                is_attacking = True
            is_command = True

        # ২. 'autoadd 2-10 no' কমান্ড
        elif t.startswith("autoadd"):
            parts = t.split()
            if len(parts) >= 3:
                try:
                    l, h = map(float, parts[1].split('-'))
                    min_bal, max_bal, reg_required = l, h, parts[2]
                    auto_add_enabled = True
                    is_attacking = True 
                    log(f"Auto-Add Active: {l}-{h} (Reg: {reg_required})", "success")
                except: log("Invalid autoadd format!", "error")
            is_command = True

        # ৩. 'confirm' কমান্ড (অটো ক্লিক)
        elif t == "confirm":
            is_command = True
            log("Auto-Confirm triggered...", "wait")
            async for msg in client.iter_messages(BOT_USERNAME, limit=5):
                if msg.buttons:
                    for row in msg.buttons:
                        for b in row:
                            if any(k in b.text.lower() for k in ["confirm", "yes"]):
                                await b.click()
                                log("Confirm Button Clicked!", "success")
                                break

        # ৪. অন্যান্য কমান্ড (start, stop, cancel)
        elif t.startswith("cancel"):
            idx = int(t.split()[1]) - 1
            if 0 <= idx < len(targets):
                removed = targets.pop(idx)
                log(f"Removed: {removed['bin']}", "error")
            is_command = True
        elif t == "start": is_attacking, is_command = True, True
        elif t == "stop": is_attacking, is_command = False, True
        
        # কমান্ড মেসেজ ডিলিট (যাতে বটের এরর না আসে)
        if is_command:
            try: await event.delete()
            except: pass
    except: pass

# --- ⚡ THE HUNTING ENGINE (Bot Scraper Inside) ---
@client.on(events.NewMessage(chats=BOT_USERNAME))
@client.on(events.MessageEdited(chats=BOT_USERNAME))
async def sniper_engine(event):
    global is_attacking
    msg_text = event.message.text.lower()
    
    if any(k in msg_text for k in ["confirm your purchase", "successfully purchased"]):
        is_attacking = False
        log("PAUSED: Action required in Bot.", "wait")
        return
        
    if any(k in msg_text for k in ["already bought", "someone else"]):
        log("Sold Out! Continuing Scan...", "error")
        is_attacking = True
        return
    
    if not is_attacking or not event.message.buttons: return
    if "main listings" not in msg_text and "total cards" not in msg_text: return
    
    btn_to_click = None
    flat = [b for r in event.message.buttons for b in r]
    BAD_TAGS = ['🅶', '🅿️', 'used', 'relister', '❌'] 
    
    for i, b in enumerate(flat):
        btn_txt = b.text.lower()
        match_found = False
        
        # লজিক ১: ওয়াচলিস্ট থেকে ম্যাচ খোঁজা
        for t in targets:
            if t['bin'] in btn_txt:
                nums = [round(float(n.replace(',', '')), 2) for n in re.findall(r"\d+\.\d+", btn_txt)]
                if any(abs(n - t['bal']) <= 0.01 for n in nums):
                    match_found = True
                    log(f"MATCH FOUND: {b.text}", "success")
                    break
        
        # লজিক ২: বটের মেনু থেকে অটোমেটিক ক্লিন কার্ড ডিটেক্ট করা
        if not match_found and auto_add_enabled and not any(bad in btn_txt for bad in BAD_TAGS):
            bin_match = re.search(r"(\d{6})", btn_txt)
            nums = [round(float(n.replace(',', '')), 2) for n in re.findall(r"\d+\.\d+", btn_txt)]
            if bin_match and nums:
                c_bal = nums[-1]
                if min_bal <= c_bal <= max_bal:
                    if not any(t['bin'] == bin_match.group(1) and t['bal'] == c_bal for t in targets):
                        targets.append({'bin': bin_match.group(1), 'bal': c_bal})
                    match_found = True
                    log(f"AUTO-DETECTED CLEAN: {b.text}", "success")

        if match_found:
            for row in event.message.buttons:
                if b in row:
                    for pb in row:
                        if "purchase" in pb.text.lower(): btn_to_click = pb; break
            if not btn_to_click:
                for pb in flat[i:i+5]:
                    if "purchase" in pb.text.lower(): btn_to_click = pb; break
            break 

    if btn_to_click:
        async with click_lock:
            is_attacking = False 
            log("Executing Purchase...", "wait")
            await btn_to_click.click()
            await asyncio.sleep(0.15) 
            await btn_to_click.click()
            log("Click Sent! Check Bot.", "success")
    else:
        # রিফ্রেশ বাটন হ্যান্ডেলার
        refresh_btn = next((b for b in flat if any(k in b.text.lower() for k in ["refresh", "🔄", "reload"])), None)
        if refresh_btn:
            await asyncio.sleep(random.uniform(0.2, 0.4))
            try: await refresh_btn.click()
            except: pass

# --- 🖥️ MENU SYSTEM (Terminal Interface) ---
async def main():
    ui_header()
    uid = get_hwid()
    log("Verifying HWID Security...", "wait")
    try:
        res = requests.get(RAW_LINK, timeout=10).text
        if uid not in res:
            ui_header()
            log(f"ACCESS DENIED! HWID: {uid}", "error")
            os.system(f"termux-clipboard-set '{uid}' 2>/dev/null")
            os.system(f"termux-open-url '{FB_LINK}' 2>/dev/null")
            sys.exit()
        log("Access Granted!", "success")
    except: 
        log("Internet/Security error!", "error")
        sys.exit()
    
    await client.start()
    
    while True:
        ui_header()
        print(f"\n{G}[1]{W} Add Target Manually")
        print(f"{G}[2]{W} Auto-Add (Scrapper) Settings")
        print(f"{G}[3]{W} Show Watchlist & Manage")
        print(f"{G}[4]{W} START HUNTING ENGINE")
        print(f"{C}[5]{W} Contact with Developer")
        print(f"{C}[6]{W} How to Use (Tutorial)")
        print(f"{R}[X]{W} Exit Tool\n")
        
        choice = (await async_input(f"{C}x-sniper> {W}")).lower().strip()
        
        if choice == "1":
            try:
                b = (await async_input("BIN: ")).replace('x', '')
                bal = round(float((await async_input("Bal: ")).replace('$', '')), 2)
                targets.append({'bin': b, 'bal': bal})
                log("Target Added Successfully!", "success")
            except: log("Invalid Input!", "error")
            await async_input("\nEnter to return...")
        elif choice == "2":
            try:
                rng = await async_input("Range (e.g. 5-10): ")
                reg = await async_input("Reg (yes/no): ")
                l, h = map(float, rng.split('-'))
                globals().update({'min_bal':l, 'max_bal':h, 'reg_required':reg, 'auto_add_enabled':True})
                log("Auto-Add Settings Activated!", "success")
            except: log("Error!", "error")
            await async_input("\nEnter to return...")
        elif choice == "3":
            ui_header()
            print(f"\n{C}--- CURRENT WATCHLIST ---{W}")
            for i, t in enumerate(targets, 1): print(f"{G}{i}.{W} {t['bin']} (${t['bal']})")
            await async_input("\nEnter to return...")
        elif choice == "4":
            globals()['is_attacking'] = True
            ui_header()
            log("SNIPER ENGINE IS LIVE!", "success")
            await client.run_until_disconnected()
        elif choice == "5": os.system(f"termux-open-url '{FB_LINK}'")
        elif choice == "6": os.system(f"termux-open-url '{TUTORIAL_LINK}'")
        elif choice == "x": sys.exit()

if __name__ == "__main__":
    client.loop.run_until_complete(main())

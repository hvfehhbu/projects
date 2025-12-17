import time
import sys
import os
import logging
import datetime # Import datetime
from logging.handlers import RotatingFileHandler
import netifaces
import subprocess
from selenium import webdriver
from selenium_stealth import stealth 
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service

# --- CONFIG ---
CHROMEDRIVER_PATH = "/home/thang/.wdm/drivers/chromedriver/linux64/143.0.7499.42/chromedriver-linux64/chromedriver"
CHECK_TARGET = "8.8.8.8"
CHECK_INTERVAL = 5
FORCE_RELOGIN_TIME = 870 
LOG_FILE = "/home/thang/projects/wifi_bot/wifi_bot.log"
IGNORED_SSIDS = ["iFone", "dhth"] 
TARGET_SSID = "INET - Free Wifi"

# GLOBAL LOCK
IS_PROCESSING = False

# --- LOGGING SETUP ---
logger = logging.getLogger("WifiBot")
logger.setLevel(logging.INFO)
handler = RotatingFileHandler(LOG_FILE, maxBytes=5*1024*1024, backupCount=3)
formatter = logging.Formatter('[%(asctime)s] %(levelname)s: %(message)s', datefmt='%H:%M:%S')
handler.setFormatter(formatter)
logger.addHandler(handler)

console = logging.StreamHandler()
console.setFormatter(formatter)
logger.addHandler(console)

def log(msg):
    logger.info(msg)

# --- CREDENTIALS ---
def get_creds():
    try:
        with open("/home/thang/projects/wifi_bot/creds.txt", "r") as f:
            content = f.read().strip()
            return content.split("|", 1)
    except:
        return "awing15-15", "Awing15-15@2023"

# --- DYNAMIC GATEWAY ---
def get_target_url():
    known_router = "192.168.200.1"
    sys_gw = ""
    try:
        gws = netifaces.gateways()
        sys_gw = gws['default'][netifaces.AF_INET][0]
    except:
        pass

    if sys_gw.startswith("172."):
        return f"http://{known_router}"
    
    return f"http://{known_router}"

def check_internet():
    try:
        subprocess.check_call(["ping", "-c", "1", "-W", "2", "8.8.8.8"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except:
        pass
    try:
        subprocess.check_call(["ping", "-c", "1", "-W", "2", "1.1.1.1"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except:
        return False

# --- TRAFFIC GENERATOR ---
def generate_traffic():
    try:
        subprocess.run(["curl", "-I", "--connect-timeout", "3", "http://www.google.com/generate_204"], 
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except:
        pass

# --- SELF HEALING ---
def cleanup_zombies():
    try:
        subprocess.run(["pkill", "-f", "chrome"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run(["pkill", "-f", "chromedriver"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except:
        pass

# --- NOTIFICATION SYSTEM ---
def send_notification(title, message):
    if os.path.exists("/home/thang/projects/wifi_bot/.no_notify"):
        return

    try:
        ps_script = f"""
        [Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] > $null;
        $template = [Windows.UI.Notifications.ToastNotificationManager]::GetTemplateContent([Windows.UI.Notifications.ToastTemplateType]::ToastText02);
        $textNodes = $template.GetElementsByTagName("text");
        $textNodes.Item(0).AppendChild($template.CreateTextNode("{title}")) > $null;
        $textNodes.Item(1).AppendChild($template.CreateTextNode("{message}")) > $null;
        $notifier = [Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier("KTX Wifi Bot");
        $notification = [Windows.UI.Notifications.ToastNotification]::new($template);
        $notifier.Show($notification);
        """
        subprocess.run(["/mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe", "-Command", ps_script], 
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception as e:
        log(f"   ⚠️ Notify error: {e}")

# --- BLACK BOX RECORDER (New Feature) ---
def capture_debug_info(driver):
    if not driver: return
    try:
        # Tao ten file theo thoi gian
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        log_dir = "/home/thang/projects/wifi_bot/debug_logs"
        os.makedirs(log_dir, exist_ok=True)
        
        # 1. Chup anh man hinh
        img_path = f"{log_dir}/fail_{timestamp}.png"
        driver.save_screenshot(img_path)
        
        # 2. Luu HTML
        html_path = f"{log_dir}/fail_{timestamp}.html"
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(driver.page_source)
            
        log(f"📸 Snapshot saved: {img_path}")
        
        # Tu dong xoa bot file cu neu qua 20 file (tranh day bo nho)
        files = sorted([os.path.join(log_dir, f) for f in os.listdir(log_dir)], key=os.path.getmtime)
        if len(files) > 40: # 20 cap file (png+html)
            for f in files[:-40]:
                os.remove(f)
                
    except Exception as e:
        log(f"⚠️ Failed to capture snapshot: {e}")

def get_driver():
    cleanup_zombies()
    
    chrome_options = Options()
    chrome_options.add_argument("--headless=new") 
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--remote-debugging-port=9222")
    chrome_options.add_argument("--disable-software-rasterizer")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    service = Service(executable_path=CHROMEDRIVER_PATH)
    
    for attempt in range(3):
        try:
            driver = webdriver.Chrome(service=service, options=chrome_options)
            stealth(driver,
                languages=["en-US", "en"],
                vendor="Google Inc.",
                platform="Win32",
                webgl_vendor="Intel Inc.",
                renderer="Intel Iris OpenGL Engine",
                fix_hairline=True,
            )
            
            driver.set_page_load_timeout(10) # FAIL FAST: 10s
            return driver
        except Exception as e:
            if attempt < 2:
                log(f"   ⚠️ Driver init failed (Attempt {attempt+1}/3). Retrying in 2s...")
                time.sleep(2)
                cleanup_zombies()
            else:
                raise e

def perform_logout():
    global IS_PROCESSING
    IS_PROCESSING = True
    
    logout_url = "http://192.168.200.1/logout"
    log(f"🔌 Active Logout via {logout_url}...")
    
    driver = None
    try:
        driver = get_driver()
        driver.set_page_load_timeout(5)
        driver.get(logout_url)
        time.sleep(1)
        log("   -> Logout command sent.")
    except Exception as e:
        log(f"   ⚠️ Logout error: {e}")
    finally:
        IS_PROCESSING = False
        if driver:
            driver.quit()

def perform_login():
    global IS_PROCESSING
    if IS_PROCESSING:
        log("⏳ Login locked (busy). Skipping.")
        return False
        
    IS_PROCESSING = True
    login_url = get_target_url()
    
    log(f"🚀 Login Sequence started. Target Gateway: {login_url}")
    USERNAME, PASSWORD = get_creds()
    driver = None

    try:
        driver = get_driver()
        
        # 1. Trigger Portal
        log("1. Triggering Portal...")
        try: driver.get(login_url)
        except: pass

        # 2. Survey Handling
        try:
            remind_btns = driver.find_elements(By.ID, "remind-me")
            if remind_btns:
                log("   -> Survey 'Remind Me' found. Clicking...")
                remind_btns[0].click()
                time.sleep(1)
                raise Exception("Survey Skipped")

            male_btns = driver.find_elements(By.ID, "male-button")
            if male_btns:
                log("   -> Survey Form detected. Auto-filling...")
                js_script = """
                function setVal(id, val) {
                    var el = document.getElementById(id);
                    if(el) {
                        el.value = val;
                        el.dispatchEvent(new Event('input', {bubbles:true}));
                        el.dispatchEvent(new Event('change', {bubbles:true}));
                        el.dispatchEvent(new Event('blur', {bubbles:true}));
                    }
                }
                """
                driver.execute_script(js_script)
                try: male_btns[0].click()
                except: driver.execute_script("document.getElementById('male-button').click();")
                driver.execute_script("setVal('age-input', '2003');")
                driver.execute_script("setVal('name-input', 'Nguyen Van A');")
                driver.execute_script("setVal('phone-number-input', '0901234567');")
                
                driver.execute_script("""
                    var btn = document.querySelector('button[type=\'submit\']') || document.querySelector('button.btn-primary:not(#male-button):not(#female-button)');
                    if(btn) btn.click();
                """)
                time.sleep(2)
        except Exception as e:
            pass

        # 3. Login
        log("2. Checking for Login/Hidden Form...")
        for i in range(10): 
            try:
                u_inputs = driver.find_elements(By.NAME, "username")
                visible = [u for u in u_inputs if u.is_displayed()]
                
                if visible:
                    log("   -> Visible Login Form. Entering credentials...")
                    visible[0].clear()
                    visible[0].send_keys(USERNAME)
                    driver.find_element(By.NAME, "password").clear()
                    driver.find_element(By.NAME, "password").send_keys(PASSWORD)
                    try: driver.find_element(By.ID, "frmLogin").submit()
                    except: driver.execute_script("document.querySelector('button[type=\'submit\']').click()")
                    break
                
                hidden = driver.find_elements(By.ID, "frmLogin")
                if hidden:
                    log("   -> Hidden Login Form. Force submitting...")
                    driver.execute_script("document.getElementById('frmLogin').submit();")
                    log("   ⚡ Fast checking internet after submit...")
                    for _ in range(15):
                        time.sleep(0.5)
                        if check_internet():
                            log("   ✅ Internet verified early!")
                            send_notification("Wifi Connected", "Login successful!")
                            time.sleep(5) 
                            return True
                    break
            except:
                pass
            time.sleep(0.5)

        # 4. Final check
        log("3. Verifying Internet Access...")
        for _ in range(5): 
            time.sleep(2)
            if check_internet():
                log("✅ LOGIN SUCCESS!")
                send_notification("Wifi Connected", "Login successful!")
                time.sleep(5) 
                return True
        
        # FAIL: Capture Debug Info
        log("❌ Login finished but Internet check failed (Timeout).")
        capture_debug_info(driver) # <--- CAPTURE SNAPSHOT
        return False

    except Exception as e:
        log(f"❌ Critical Error: {e}")
        if driver: capture_debug_info(driver) # <--- CAPTURE SNAPSHOT
        return False
    finally:
        IS_PROCESSING = False
        if driver:
            driver.quit()

def get_current_ssid():
    try:
        output = subprocess.check_output(
            ["/mnt/c/Windows/System32/netsh.exe", "wlan", "show", "interfaces"],
            encoding="utf-8", errors="ignore"
        )
        for line in output.split('\n'):
            if "SSID" in line and "BSSID" not in line:
                parts = line.split(":", 1)
                if len(parts) > 1:
                    return parts[1].strip()
    except Exception as e:
        pass
    return None

def force_wifi_reconnect():
    log(f"🚑 Critical: Forcing reconnect to '{TARGET_SSID}' via Windows netsh...")
    try:
        cmd = ["/mnt/c/Windows/System32/netsh.exe", "wlan", "connect", f"name={TARGET_SSID}"]
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(10)
    except Exception as e:
        log(f"   ⚠️ Reconnect error: {e}")

def main():
    log("=== KTX Wifi Bot v2.9 (Black Box) Started ===")
    target = get_target_url()
    log(f"📍 Target Gateway: {target}")
    
    last_login_time = time.time() if check_internet() else 0
    loop_count = 0
    fail_count = 0
    
    while True:
        is_connected = check_internet()
        current_time = time.time()

        if is_connected and loop_count % 12 == 0:
            generate_traffic()
            fail_count = 0 
        loop_count += 1
        
        if not is_connected:
            current_ssid = get_current_ssid()
            if current_ssid:
                is_ignored = False
                for ignored in IGNORED_SSIDS:
                    if ignored.lower() in current_ssid.lower():
                        is_ignored = True
                        break
                
                if is_ignored:
                    log(f"🛑 Connected to '{current_ssid}'. Ignored. Sleeping...")
                    time.sleep(30)
                    continue

            log("⚠️  Internet LOST. Starting sequence...")
            if perform_login():
                last_login_time = current_time
                fail_count = 0
            else:
                fail_count += 1
                log(f"   ⚠️ Login Failed ({fail_count}/3).")
                
                if fail_count >= 3:
                    force_wifi_reconnect()
                    fail_count = 0
                
                time.sleep(5) 
        
        elif (current_time - last_login_time) > FORCE_RELOGIN_TIME:
            current_ssid = get_current_ssid()
            if current_ssid:
                 is_ignored = False
                 for ignored in IGNORED_SSIDS:
                    if ignored.lower() in current_ssid.lower():
                        is_ignored = True
                        break
                 if is_ignored:
                     time.sleep(CHECK_INTERVAL)
                     continue

            log("⚠️  Session Expiring (Active Refresh). Relogging...")
            
            last_login_time = current_time
            perform_logout()
            perform_login()
        
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
import os
import time
import sys
import logging
import datetime
import subprocess
from logging.handlers import RotatingFileHandler

import netifaces
import fcntl

from selenium import webdriver
from selenium_stealth import stealth
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service


# =========================
# CONFIG
# =========================
CHROMEDRIVER_PATH = "/home/thang/.wdm/drivers/chromedriver/linux64/143.0.7499.42/chromedriver-linux64/chromedriver"

LOG_FILE = "/home/thang/projects/wifi_bot/wifi_bot.log"
DEBUG_DIR = "/home/thang/projects/wifi_bot/debug_logs"

CHECK_INTERVAL = 5                    # seconds
FORCE_RELOGIN_TIME = 870              # seconds

KNOWN_ROUTER = "192.168.200.1"
TARGET_SSID = "INET - Free Wifi"
IGNORED_SSIDS = ["iFone", "dhth"]

# Connectivity check: HTTP 204 beats ping for captive portal
CONNECTIVITY_URLS = [
    "http://connectivitycheck.gstatic.com/generate_204",
    "http://www.google.com/generate_204",
    "http://cp.cloudflare.com/generate_204",
]

# Driver profile isolation (for safe cleanup)
BOT_PROFILE_DIR = "/tmp/wifi_bot_chrome_profile"
BOT_CACHE_DIR = "/tmp/wifi_bot_chrome_cache"

# Single instance lock
LOCK_PATH = "/tmp/wifi_bot.lock"


# =========================
# LOGGING
# =========================
logger = logging.getLogger("WifiBot")
logger.setLevel(logging.INFO)

handler = RotatingFileHandler(LOG_FILE, maxBytes=5 * 1024 * 1024, backupCount=3)
formatter = logging.Formatter("[%(asctime)s] %(levelname)s: %(message)s", datefmt="%H:%M:%S")
handler.setFormatter(formatter)
logger.addHandler(handler)

console = logging.StreamHandler()
console.setFormatter(formatter)
logger.addHandler(console)


def log(msg: str):
    logger.info(msg)


# =========================
# SINGLE INSTANCE
# =========================
class SingleInstance:
    def __init__(self, path=LOCK_PATH):
        self.f = open(path, "w")
        fcntl.flock(self.f, fcntl.LOCK_EX | fcntl.LOCK_NB)


# =========================
# CREDENTIALS
# =========================
def get_creds():
    try:
        with open("/home/thang/projects/wifi_bot/creds.txt", "r") as f:
            content = f.read().strip()
            u, p = content.split("|", 1)
            return u.strip(), p.strip()
    except Exception:
        return "awing15-15", "Awing15-15@2023"


# =========================
# GATEWAY
# =========================
def get_target_url():
    # you can extend this later, but current logic always points to known router
    return f"http://{KNOWN_ROUTER}"


# =========================
# CONNECTIVITY (HTTP 204)
# =========================
def check_internet(timeout_s: int = 2) -> bool:
    # Return True if any URL returns 204
    for url in CONNECTIVITY_URLS:
        try:
            code = subprocess.check_output(
                [
                    "curl",
                    "-sS",
                    "-o",
                    "/dev/null",
                    "--connect-timeout",
                    str(timeout_s),
                    "--max-time",
                    str(timeout_s + 1),
                    "-w",
                    "%{http_code}",
                    url,
                ],
                stderr=subprocess.DEVNULL,
                text=True,
            ).strip()
            if code == "204":
                return True
        except Exception:
            pass
    return False


def generate_keepalive():
    # lightweight keepalive; don't need heavy traffic
    try:
        subprocess.run(
            ["curl", "-sS", "-o", "/dev/null", "--connect-timeout", "2", "--max-time", "3", CONNECTIVITY_URLS[0]],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=4,
        )
    except Exception:
        pass


# =========================
# WINDOWS WIFI (netsh via WSL)
# =========================
NETSH = "/mnt/c/Windows/System32/netsh.exe"


def get_current_ssid():
    try:
        output = subprocess.check_output([NETSH, "wlan", "show", "interfaces"], encoding="utf-8", errors="ignore")
        for line in output.split("\n"):
            if "SSID" in line and "BSSID" not in line:
                parts = line.split(":", 1)
                if len(parts) > 1:
                    return parts[1].strip()
    except Exception:
        pass
    return None


def netsh_disconnect():
    try:
        subprocess.run([NETSH, "wlan", "disconnect"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=6)
    except Exception:
        pass


def connect_target_ssid(timeout_s: int = 18) -> bool:
    log(f"📶 Connecting to '{TARGET_SSID}' (netsh)...")
    netsh_disconnect()
    time.sleep(2)

    try:
        subprocess.run(
            [NETSH, "wlan", "connect", f"name={TARGET_SSID}"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=10,
        )
    except Exception:
        pass

    t0 = time.monotonic()
    while time.monotonic() - t0 < timeout_s:
        ssid = get_current_ssid()
        if ssid and ssid.strip() == TARGET_SSID:
            log("   -> SSID OK")
            return True
        time.sleep(1)

    log("   ⚠️ SSID still not correct")
    return False


def is_ignored_ssid(ssid: str | None) -> bool:
    if not ssid:
        return False
    s = ssid.lower()
    return any(x.lower() in s for x in IGNORED_SSIDS)


# =========================
# NOTIFY
# =========================
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
        subprocess.run(
            ["/mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe", "-Command", ps_script],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=8,
        )
    except Exception as e:
        log(f"⚠️ Notify error: {e}")


# =========================
# DEBUG SNAPSHOT
# =========================
def capture_debug_info(driver, tag="fail"):
    if not driver:
        return
    try:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        os.makedirs(DEBUG_DIR, exist_ok=True)

        img_path = f"{DEBUG_DIR}/{tag}_{timestamp}.png"
        html_path = f"{DEBUG_DIR}/{tag}_{timestamp}.html"
        meta_path = f"{DEBUG_DIR}/{tag}_{timestamp}.txt"

        driver.save_screenshot(img_path)
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(driver.page_source)

        try:
            with open(meta_path, "w", encoding="utf-8") as f:
                f.write(f"URL: {driver.current_url}\n")
                f.write(f"TITLE: {driver.title}\n")
        except Exception:
            pass

        log(f"📸 Snapshot saved: {img_path}")

        # keep last 40 files (png/html/txt => ~120); simple rotation
        files = sorted(
            [os.path.join(DEBUG_DIR, f) for f in os.listdir(DEBUG_DIR)],
            key=os.path.getmtime,
        )
        if len(files) > 120:
            for f in files[:-120]:
                try:
                    os.remove(f)
                except Exception:
                    pass

    except Exception as e:
        log(f"⚠️ Failed to capture snapshot: {e}")


# =========================
# SELENIUM DRIVER (REUSE)
# =========================
_driver = None
_driver_fail = 0


def cleanup_bot_chrome():
    # safer than pkill chrome: kill only processes that mention our profile dir
    try:
        subprocess.run(["pkill", "-f", BOT_PROFILE_DIR], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=5)
    except Exception:
        pass


def create_new_driver():
    os.makedirs(BOT_PROFILE_DIR, exist_ok=True)
    os.makedirs(BOT_CACHE_DIR, exist_ok=True)

    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1280,720")

    # speed/stability flags (keep minimal; add more only if stable)
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-background-networking")
    chrome_options.add_argument("--disable-sync")
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument("--no-first-run")
    chrome_options.add_argument("--no-default-browser-check")
    chrome_options.add_argument("--blink-settings=imagesEnabled=false")

    chrome_options.add_argument(f"--user-data-dir={BOT_PROFILE_DIR}")
    chrome_options.add_argument(f"--disk-cache-dir={BOT_CACHE_DIR}")

    chrome_options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )

    service = Service(executable_path=CHROMEDRIVER_PATH)

    driver = webdriver.Chrome(service=service, options=chrome_options)
    stealth(
        driver,
        languages=["en-US", "en"],
        vendor="Google Inc.",
        platform="Win32",
        webgl_vendor="Intel Inc.",
        renderer="Intel Iris OpenGL Engine",
        fix_hairline=True,
    )
    driver.set_page_load_timeout(8)
    driver.set_script_timeout(8)
    return driver


def get_driver():
    global _driver, _driver_fail

    if _driver is not None:
        try:
            _driver.execute_script("return 1;")
            return _driver
        except Exception:
            try:
                _driver.quit()
            except Exception:
                pass
            _driver = None

    # create with 2 retries (fast)
    cleanup_bot_chrome()
    for attempt in range(2):
        try:
            _driver = create_new_driver()
            _driver_fail = 0
            return _driver
        except Exception as e:
            log(f"⚠️ Driver init failed (Attempt {attempt+1}/2): {e}")
            cleanup_bot_chrome()
            time.sleep(1)

    raise RuntimeError("Failed to init Chrome driver")


def reset_driver():
    global _driver
    try:
        if _driver:
            _driver.quit()
    except Exception:
        pass
    _driver = None
    cleanup_bot_chrome()


# =========================
# PORTAL ACTIONS
# =========================
IS_PROCESSING = False


def perform_logout():
    global IS_PROCESSING
    if IS_PROCESSING:
        log("⏳ Logout locked (busy). Skipping.")
        return

    IS_PROCESSING = True
    driver = None
    try:
        driver = get_driver()
        logout_url = f"http://{KNOWN_ROUTER}/logout"
        log(f"🔌 Active Logout via {logout_url}...")
        try:
            driver.get(logout_url)
        except Exception:
            pass
        time.sleep(0.5)
        log("   -> Logout command sent.")
    except Exception as e:
        log(f"⚠️ Logout error: {e}")
    finally:
        IS_PROCESSING = False


def _handle_survey(driver):
    # Keep your current logic, but make it deterministic
    try:
        btn = driver.find_elements(By.ID, "remind-me")
        if btn:
            log("   -> Survey 'Remind Me' found. Clicking...")
            btn[0].click()
            time.sleep(0.6)
            return True

        male_btns = driver.find_elements(By.ID, "male-button")
        if male_btns:
            log("   -> Survey Form detected. Auto-filling...")
            js = """
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
            driver.execute_script(js)
            try:
                male_btns[0].click()
            except Exception:
                driver.execute_script("document.getElementById('male-button').click();")

            driver.execute_script("setVal('age-input', '2003');")
            driver.execute_script("setVal('name-input', 'Nguyen Van A');")
            driver.execute_script("setVal('phone-number-input', '0901234567');")

            driver.execute_script("""
                var btn = document.querySelector("button[type='submit']") ||
                          document.querySelector("button.btn-primary:not(#male-button):not(#female-button)");
                if(btn) btn.click();
            """)
            time.sleep(1.2)
            return True
    except Exception:
        pass
    return False


def perform_login() -> bool:
    global IS_PROCESSING

    if IS_PROCESSING:
        log("⏳ Login locked (busy). Skipping.")
        return False

    # ensure we are on target SSID (unless ignored)
    ssid = get_current_ssid()
    if ssid and is_ignored_ssid(ssid):
        log(f"🛑 Connected to '{ssid}'. Ignored. Skip login.")
        return False

    if ssid != TARGET_SSID:
        connect_target_ssid()

    IS_PROCESSING = True
    login_url = get_target_url()
    USERNAME, PASSWORD = get_creds()

    driver = None
    try:
        driver = get_driver()
        log(f"🚀 Login Sequence started. Gateway: {login_url}")

        # 1) trigger portal
        log("1) Triggering portal...")
        try:
            driver.get(login_url)
        except Exception:
            pass

        # 2) survey (optional)
        _handle_survey(driver)

        # 3) login submit (visible form OR hidden frmLogin)
        log("2) Searching login form...")
        t0 = time.monotonic()
        submitted = False

        while time.monotonic() - t0 < 6.0:  # fail-fast window
            # visible username field?
            try:
                u_inputs = driver.find_elements(By.NAME, "username")
                visible_u = [u for u in u_inputs if u.is_displayed()]
                if visible_u:
                    log("   -> Visible login form. Filling creds...")
                    visible_u[0].clear()
                    visible_u[0].send_keys(USERNAME)

                    p = driver.find_element(By.NAME, "password")
                    p.clear()
                    p.send_keys(PASSWORD)

                    try:
                        driver.find_element(By.ID, "frmLogin").submit()
                    except Exception:
                        driver.execute_script("var b=document.querySelector(\"button[type='submit']\"); if(b) b.click();")
                    submitted = True
                    break

                # hidden frmLogin?
                hidden = driver.find_elements(By.ID, "frmLogin")
                if hidden:
                    log("   -> Hidden frmLogin detected. Force submit...")
                    driver.execute_script("document.getElementById('frmLogin').submit();")
                    submitted = True
                    break
            except Exception:
                pass

            time.sleep(0.25)

        if not submitted:
            log("❌ No login form found (timeout).")
            capture_debug_info(driver, tag="noform")
            return False

        # 4) quick verify (aggressive)
        log("3) Verifying internet (fast)...")
        t1 = time.monotonic()
        while time.monotonic() - t1 < 8.0:
            if check_internet(timeout_s=2):
                log("✅ LOGIN SUCCESS!")
                send_notification("Wifi Connected", "Login successful!")
                return True
            time.sleep(0.4)

        log("❌ Submit done but internet still not OK.")
        capture_debug_info(driver, tag="timeout")
        return False

    except Exception as e:
        log(f"❌ Critical Error: {e}")
        if driver:
            capture_debug_info(driver, tag="crash")
        # if driver gets weird, reset it
        reset_driver()
        return False

    finally:
        IS_PROCESSING = False


# =========================
# MAIN LOOP
# =========================
def main():
    # single instance lock
    try:
        _lock = SingleInstance()
    except Exception:
        log("🚫 Another instance is running. Exiting.")
        sys.exit(1)

    log("=== KTX Wifi Bot v2.10 (Hardened) Started ===")
    log(f"📍 Target Gateway: {get_target_url()}")

    last_login_time = time.monotonic() if check_internet() else 0.0
    loop_count = 0
    fail_count = 0

    while True:
        now = time.monotonic()
        is_connected = check_internet(timeout_s=2)

        # periodic keepalive
        if is_connected and (loop_count % 12 == 0):
            generate_keepalive()
            fail_count = 0

        loop_count += 1

        if not is_connected:
            ssid = get_current_ssid()
            if ssid and is_ignored_ssid(ssid):
                log(f"🛑 Connected to '{ssid}'. Ignored. Sleeping...")
                time.sleep(30)
                continue

            log("⚠️ Internet LOST. Starting sequence...")

            # backoff: 0.5s, 1s, 2s (bounded)
            backoff = min(2.0, 0.5 * (2 ** min(fail_count, 2)))

            ok = perform_login()
            if ok:
                last_login_time = now
                fail_count = 0
            else:
                fail_count += 1
                log(f"   ⚠️ Login Failed ({fail_count}/3). backoff={backoff:.1f}s")
                time.sleep(backoff)

                if fail_count >= 3:
                    log("🚑 Too many failures: forcing reconnect...")
                    connect_target_ssid()
                    reset_driver()
                    fail_count = 0

        else:
            # active refresh
            if last_login_time > 0 and (now - last_login_time) > FORCE_RELOGIN_TIME:
                ssid = get_current_ssid()
                if ssid and is_ignored_ssid(ssid):
                    time.sleep(CHECK_INTERVAL)
                    continue

                log("⚠️ Session Expiring (Active Refresh). Relogging...")
                last_login_time = now
                perform_logout()
                perform_login()

        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    main()

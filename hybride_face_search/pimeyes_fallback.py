import os
import time
import tempfile
import shutil
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

def fallback_to_pimeyes(image_path: str, results_dir="results") -> dict:
    os.makedirs(results_dir, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    screenshot = os.path.join(results_dir, f"pimeyes_{ts}.png")

    # --- create a disposable copy of your real profile (optional) ---
    real = r"C:\Users\mikre\AppData\Local\Google\Chrome\User Data\Default"
    temp_dir = tempfile.mkdtemp(prefix="pimeyes_profile_")
    shutil.copytree(real, os.path.join(temp_dir, "Default"))

    opts = webdriver.ChromeOptions()
    opts.add_argument(f"--user-data-dir={temp_dir}")
    opts.add_argument("--profile-directory=Default")
    opts.add_argument("--start-maximized")
    opts.add_argument("--no-first-run")
    opts.add_argument("--no-default-browser-check")

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=opts
    )
    wait = WebDriverWait(driver, 20)

    try:
        driver.get("https://pimeyes.com/en")
        print("👉 Navigated to PimEyes")

        # accept cookies
        try:
            wait.until(EC.element_to_be_clickable(
                (By.XPATH, "//button[contains(., 'Allow all')]")
            )).click()
        except:
            pass

        # open modal
        wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button.upload"))).click()

        # reveal input
        driver.execute_script("""
            let el = document.querySelector('#file-input');
            if(el) {
              el.hidden=false; el.style.display='block'; el.disabled=false;
            }
        """)

        # upload
        inp = driver.find_element(By.CSS_SELECTOR, "#file-input")
        inp.send_keys(os.path.abspath(image_path))

        # wait for Turnstile token
        try:
            wait.until(lambda d: d.execute_script(
                "return document.querySelector('input[name=\"cf-turnstile-response\"]').value.length>0"
            ))
            print("✅ Token received")
        except:
            print("⚠️ No token after timeout")

        time.sleep(2)
        driver.save_screenshot(screenshot)
        print("📸 Screenshot saved:", screenshot)
    finally:
        driver.quit()
        # clean up the temp profile
        shutil.rmtree(temp_dir, ignore_errors=True)

    return {"pimeyes_used": True, "pimeyes_screenshot": screenshot, "timestamp": ts}

import os
import time
from datetime import datetime

import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

def fallback_to_pimeyes(image_path: str, results_dir="results") -> dict:
    # 0️⃣ Prepare output folder and timestamp
    os.makedirs(results_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    screenshot_path = os.path.join(results_dir, f"pimeyes_result_{timestamp}.png")

    # 1️⃣ Configure Chrome options
    options = uc.ChromeOptions()
    # Use your real profile; comment out if you prefer a fresh profile
    options.add_argument(r"--user-data-dir=C:\Users\mikre\AppData\Local\Google\Chrome\User Data")
    options.add_argument("--profile-directory=Default")
    options.add_argument("--start-maximized")
    # Prevent any default startup pages
    options.add_argument("--no-first-run")
    options.add_argument("--no-default-browser-check")

    # 2️⃣ Start undetected-chromedriver with webdriver-manager
    service = Service(ChromeDriverManager().install())
    driver = uc.Chrome(options=options, service=service)
    wait = WebDriverWait(driver, 20)

    try:
        # 3️⃣ Ensure a fresh tab is open and navigate
        if len(driver.window_handles) > 1:
            # close any extra tabs
            for handle in driver.window_handles[1:]:
                driver.switch_to.window(handle)
                driver.close()
            driver.switch_to.window(driver.window_handles[0])

        driver.get("https://pimeyes.com/en")
        print("🔗 Navigated to pimeyes.com/en")

        # 4️⃣ Accept cookies
        try:
            btn = wait.until(EC.element_to_be_clickable(
                (By.XPATH, "//button[contains(., 'Allow all')]")
            ))
            btn.click()
            print("✅ Cookies geaccepteerd")
        except:
            print("⚠️ Geen cookie-popup gevonden")

        # 5️⃣ Open upload modal
        wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button.upload"))).click()
        print("✅ Upload-modal geopend")

        # 6️⃣ Reveal the hidden file-input
        driver.execute_script("""
            const el = document.querySelector('#file-input');
            if (el) {
                el.hidden = false;
                el.style.display = 'block';
                el.style.visibility = 'visible';
                el.disabled = false;
            }
        """)
        print("✅ Input-veld zichtbaar gemaakt")

        # 7️⃣ Upload the image
        file_input = driver.find_element(By.CSS_SELECTOR, "#file-input")
        file_input.send_keys(os.path.abspath(image_path))
        print("✅ Bestand geüpload")

        # 8️⃣ Wait for the invisible Turnstile token
        try:
            wait.until(lambda d: d.execute_script(
                "return document.querySelector('input[name=\"cf-turnstile-response\"]').value.length > 0"
            ))
            print("✅ Turnstile-token ontvangen")
        except:
            print("⚠️ Geen Turnstile-token na timeout")

        # 9️⃣ Screenshot the results
        time.sleep(2)
        driver.save_screenshot(screenshot_path)
        print(f"📸 Screenshot opgeslagen: {screenshot_path}")

    finally:
        driver.quit()

    return {
        "pimeyes_used": True,
        "pimeyes_screenshot": screenshot_path,
        "timestamp": timestamp
    }

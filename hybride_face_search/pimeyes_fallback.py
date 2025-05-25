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
    # 0️⃣ Output-map en timestamp
    os.makedirs(results_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    screenshot_path = os.path.join(results_dir, f"pimeyes_result_{timestamp}.png")

    # 1️⃣ Stel ChromeOptions in voor jouw echte Chrome
    options = uc.ChromeOptions()
    # Zet hier het pad naar jouw echte chrome.exe (indien nodig)
    # options.binary_location = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    options.add_argument(r"--user-data-dir=C:\Users\mikre\AppData\Local\Google\Chrome\User Data")
    options.add_argument("--profile-directory=Default")
    options.add_argument("--start-maximized")

    # 2️⃣ Start undetected-chromedriver w/ webdriver-manager voor de driver
    service = Service(ChromeDriverManager().install())
    driver = uc.Chrome(options=options, service=service)
    wait = WebDriverWait(driver, 20)

    try:
        # 3️⃣ Navigeer & accepteer cookies
        driver.get("https://pimeyes.com/en")
        try:
            wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Allow all')]"))).click()
        except:
            pass

        # 4️⃣ Open de upload-modal
        wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button.upload"))).click()

        # 5️⃣ Forceer verborgen input actief
        driver.execute_script("""
            const el = document.querySelector('#file-input');
            if (el) {
                el.hidden = false;
                el.style.display = 'block';
                el.style.visibility = 'visible';
                el.disabled = false;
            }
        """)

        # 6️⃣ Upload je afbeelding
        file_input = driver.find_element(By.CSS_SELECTOR, "#file-input")
        file_input.send_keys(os.path.abspath(image_path))

        # 7️⃣ Wacht op invisible Turnstile-response token
        try:
            wait.until(lambda d: d.execute_script(
                "return document.querySelector('input[name=\"cf-turnstile-response\"]').value.length>0"
            ))
            print("✅ Turnstile-token ontvangen")
        except:
            print("⚠️ Geen Turnstile-token na timeout")

        # 8️⃣ Screenshot van de resultaten
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

from playwright.sync_api import sync_playwright
import time
from datetime import datetime
import os

def fallback_to_pimeyes(image_path: str, results_dir="results") -> dict:
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    screenshot_path = os.path.join(results_dir, f"pimeyes_result_{timestamp}.png")
    os.makedirs(results_dir, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto("https://pimeyes.com/en")

        # Cookies accepteren
        try:
            page.wait_for_selector('button:has-text("Allow all")', timeout=5000)
            page.click('button:has-text("Allow all")')
            print("✅ Cookies geaccepteerd")
        except:
            print("⚠️ Geen cookie-popup gevonden")

        # Klik op upload-knop
        try:
            page.wait_for_selector('button.upload', timeout=8000)
            page.click('button.upload')
        except:
            print("⚠️ Uploadknop niet gevonden")
            browser.close()
            return {}

        # Wacht tot dropzone zichtbaar is
        try:
            page.wait_for_selector('.dropzone-blue.dropzone', timeout=10000)
            print("✅ Dropzone zichtbaar")
        except:
            print("❌ Dropzone niet zichtbaar")
            browser.close()
            return {}

        # Klik op de blauwe dropzone
        try:
            page.click(".dropzone-blue")
            page.wait_for_timeout(500)

            # Forceer zichtbaarheid van input en upload bestand
            page.eval_on_selector('input[type="file"]', 'el => el.style.display = "block"')
            file_input = page.locator('input[type="file"]').first
            file_input.set_input_files(image_path)
            print("✅ Upload geslaagd via JS-injectie")
        except Exception as e:
            print("❌ Upload mislukt:", e)
            browser.close()
            return {}

        # Screenshot na upload
        page.wait_for_timeout(15000)
        page.screenshot(path=screenshot_path)
        browser.close()

    return {
        "pimeyes_used": True,
        "pimeyes_screenshot": screenshot_path,
        "timestamp": timestamp
    }

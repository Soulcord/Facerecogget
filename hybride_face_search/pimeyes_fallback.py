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
        page.click("text=Search by image", timeout=10000)

        input_elem = page.locator('input[type="file"]')
        input_elem.set_input_files(image_path)

        page.wait_for_timeout(15000)
        page.screenshot(path=screenshot_path)

        browser.close()

    return {
        "pimeyes_used": True,
        "pimeyes_screenshot": screenshot_path,
        "timestamp": timestamp
    }
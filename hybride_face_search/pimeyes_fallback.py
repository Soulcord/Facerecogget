from playwright.sync_api import sync_playwright
import os
from datetime import datetime

def fallback_to_pimeyes(image_path: str, results_dir="results") -> dict:
    """
    Upload een afbeelding naar PimEyes door:
    1) Cookies te accepteren
    2) De upload-modal te openen
    3) Het verborgen input#file-input zichtbaar te maken via JS
    4) Direct de afbeelding te uploaden zonder systeem-file-dialog
    5) Automatisch wachten op de Invisible Turnstile-response
    6) Een screenshot nemen van de resultaten
    """

    # 0️⃣ Timestamp en resultaatmap aanmaken
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    screenshot_path = os.path.join(results_dir, f"pimeyes_result_{timestamp}.png")
    os.makedirs(results_dir, exist_ok=True)

    with sync_playwright() as p:
        # 1️⃣ Browser starten
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto("https://pimeyes.com/en")

        # 2️⃣ Cookies accepteren (indien popup)
        try:
            page.wait_for_selector('button:has-text("Allow all")', timeout=5000)
            page.click('button:has-text("Allow all")')
            print("✅ Cookies geaccepteerd")
        except:
            print("⚠️ Geen cookie-popup gevonden")

        # 3️⃣ Upload-modal openen
        page.click("button.upload", timeout=8000)
        page.wait_for_selector('.dropzone-blue.dropzone', timeout=10000)
        print("✅ Upload-modal geopend")

        # 4️⃣ Maak verborgen input zichtbaar en upload
        page.eval_on_selector('#file-input', '''
          el => {
            el.style.display = 'block';
            el.style.visibility = 'visible';
            el.style.opacity = '1';
            el.style.position = 'static';
            el.removeAttribute('hidden');
          }
        ''')
        print("✅ Input-veld zichtbaar gemaakt")
        page.locator('#file-input').first.set_input_files(image_path)
        print("✅ Bestand geüpload via eerste #file-input")

        # ⏱️ Kort wachten zodat Turnstile-response begint
        page.wait_for_timeout(2000)

        # 5️⃣ Wacht op Invisible Turnstile-response token
        try:
            # Wacht tot het hidden input-element aanwezig is
            page.wait_for_selector('input[name="cf-turnstile-response"]', timeout=10000)
            # Poll tot de waarde niet-lege string wordt
            page.wait_for_function(
                "document.querySelector('input[name=\"cf-turnstile-response\"]').value.length > 0",
                timeout=20000
            )
            print("✅ Invisible Turnstile automatisch geslaagd")
        except Exception as e:
            print("⚠️ Turnstile-response niet gevonden of timeout:", e)

        # 6️⃣ Screenshot maken
        page.wait_for_timeout(3000)
        page.screenshot(path=screenshot_path)
        print(f"✅ Screenshot opgeslagen: {screenshot_path}")

        browser.close()

    # 7️⃣ Return metadata
    return {
        "pimeyes_used": True,
        "pimeyes_screenshot": screenshot_path,
        "timestamp": timestamp
    }

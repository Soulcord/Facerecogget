from playwright.sync_api import sync_playwright
import os
from datetime import datetime

def fallback_to_pimeyes(image_path: str, results_dir="results") -> dict:
    """
    Upload een afbeelding naar PimEyes door:
    1) Cookies te accepteren ("Allow all")
    2) De upload-modal te openen (button.upload)
    3) Het verborgen input#file-input zichtbaar te maken via JS
    4) Direct de afbeelding te uploaden zonder systeem-file-dialog
    5) Automatisch wachten op de Invisible Turnstile-response
    6) Een screenshot nemen van de resultaten
    """

    # Timestamp en output-map aanmaken
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    screenshot_path = os.path.join(results_dir, f"pimeyes_result_{timestamp}.png")
    os.makedirs(results_dir, exist_ok=True)

    # Pas deze paden aan naar jouw installatie
    chrome_path    = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    user_data_dir  = r"C:\Users\mikre\AppData\Local\Google\Chrome\User Data\PWProfile"

    with sync_playwright() as p:
        # 1️⃣ Launch jouw echte Chrome met persistent profiel
        context = p.chromium.launch_persistent_context(
            user_data_dir=user_data_dir,
            headless=False,
            executable_path=chrome_path,
            args=["--start-maximized", "--disable-blink-features=AutomationControlled"]
        )
        page = context.pages[0] if context.pages else context.new_page()

        # 2️⃣ Ga naar PimEyes
        page.goto("https://pimeyes.com/en")

        # 3️⃣ Cookies accepteren
        try:
            page.wait_for_selector('button:has-text("Allow all")', timeout=5000)
            page.click('button:has-text("Allow all")')
            print("✅ Cookies geaccepteerd")
        except:
            print("⚠️ Geen cookie-popup gevonden")

        # 4️⃣ Upload-modal openen
        try:
            page.wait_for_selector("button.upload", timeout=10000)
            page.click("button.upload")
            page.wait_for_selector(".dropzone-blue.dropzone", timeout=10000)
            print("✅ Upload-modal geopend")
        except Exception as e:
            print(f"❌ Kon de upload-modal niet openen: {e}")
            context.close()
            return None

        # 5️⃣ Verborgen <input#file-input> zichtbaar maken
        page.evaluate('''() => {
            const el = document.querySelector('#file-input');
            if (el) {
                el.removeAttribute('hidden');
                el.style.display = 'block';
                el.style.visibility = 'visible';
                el.style.opacity = '1';
                el.style.position = 'static';
                el.disabled = false;
            }
        }''')
        print("✅ Input-veld zichtbaar gemaakt")

        # 6️⃣ Bestand uploaden
        try:
            page.locator('#file-input').first.set_input_files(image_path)
            print("✅ Bestand geüpload via eerste #file-input")
        except Exception as e:
            print(f"❌ Upload mislukt: {e}")
            page.screenshot(path=os.path.join(results_dir, f"upload_fail_{timestamp}.png"))
            context.close()
            return None

        # 7️⃣ Kort wachten zodat Turnstile kan verwerken
        page.wait_for_timeout(2000)

        # 8️⃣ Wacht op Invisible Turnstile-response token
        try:
            page.wait_for_selector('input[name="cf-turnstile-response"]', timeout=10000)
            page.wait_for_function(
                "document.querySelector('input[name=\"cf-turnstile-response\"]').value.length > 0",
                timeout=20000
            )
            print("✅ Invisible Turnstile automatisch geslaagd")
        except Exception as e:
            print(f"⚠️ Turnstile-response niet gevonden of timeout: {e}")

        # 9️⃣ Screenshot maken van de resultaten
        page.wait_for_timeout(3000)
        page.screenshot(path=screenshot_path)
        print(f"✅ Screenshot opgeslagen: {screenshot_path}")

        context.close()

    # 🔟 Return metadata
    return {
        "pimeyes_used": True,
        "pimeyes_screenshot": screenshot_path,
        "timestamp": timestamp
    }

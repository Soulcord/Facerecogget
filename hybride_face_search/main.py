import os
import json
from pimeyes_fallback import fallback_to_pimeyes

# Simuleer resultaat van gezichtsmatching
def fake_local_match(image_path):
    return None  # Simuleert "geen match"

def main():
    image_path = "queries/unknown.jpg"  # Voorbeeldpad naar onbekende afbeelding

    result = fake_local_match(image_path)

    if result is None:
        print("❌ Geen lokale match gevonden. Probeer PimEyes...")
        fallback = fallback_to_pimeyes(image_path)
        fallback["match_found"] = False
        fallback["local_match"] = None

        with open("results/output.json", "w") as f:
            json.dump(fallback, f, indent=2)

        print("✅ PimEyes resultaat opgeslagen.")
    else:
        print("✅ Lokale match gevonden:", result)

if __name__ == "__main__":
    main()
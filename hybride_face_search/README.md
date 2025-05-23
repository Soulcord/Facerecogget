# Hybride Gezichtszoeker CLI (met PimEyes fallback)

Deze tool voert gezichtsherkenning uit. Als het gezicht niet lokaal wordt herkend, wordt automatisch een PimEyes-zoekopdracht uitgevoerd.

## Installatie

```bash
pip install -r requirements.txt
playwright install
```

## Gebruik

```bash
python main.py
```

Zorg dat je een afbeelding plaatst in `queries/unknown.jpg` voor deze demo.

## Output

- JSON-bestand in `results/output.json`
- Screenshot van PimEyes-resultaat
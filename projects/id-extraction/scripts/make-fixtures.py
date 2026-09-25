"""Generate fictional text fixtures locally, without external image services."""
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

root = Path("examples")
root.mkdir(exist_ok=True)
font = ImageFont.truetype("DejaVuSans.ttf", 32)
image = Image.new("RGB", (1100, 750), "white")
draw = ImageDraw.Draw(image)
lines = ["SYNTHETIC TEST DOCUMENT - NOT VALID ID", "AUSTRALIA", "PASSPORT",
         "Surname: EXAMPLE", "Given names: ALICE", "Date of birth: 12 MAY 1990",
         "Passport number: T0000001", "Sex: F", "Nationality: AUSTRALIAN",
         "Date of issue: 10 JUN 2020", "Date of expiry: 10 JUN 2030"]
for i, line in enumerate(lines):
    draw.text((30, 25 + i * 60), line, fill="black", font=font)
image.save(root / "synthetic-passport.png")
Image.new("RGB", (800, 600), "white").save(root / "blank.png")
fields = ["document_type", "issuing_country", "issuing_state_or_territory", "first_name",
          "middle_name", "last_name", "full_name", "date_of_birth", "sex", "nationality",
          "document_number", "licence_number", "passport_number", "address", "issue_date", "expiry_date"]
cases = [
    {"id": "synthetic-passport", "image": "synthetic-passport.png", "expected": {
        "document_type": "passport", "first_name": "ALICE", "last_name": "EXAMPLE",
        "date_of_birth": "1990-05-12", "passport_number": "T0000001",
        "sex": "F", "issue_date": "2020-06-10", "expiry_date": "2030-06-10",
        "address": None, "middle_name": None, "licence_number": None,
        "full_name": None, "issuing_state_or_territory": None}},
    {"id": "blank", "image": "blank.png", "expected": dict.fromkeys(fields)},
]
(root / "manifest.json").write_text(json.dumps(cases, indent=2) + "\n")

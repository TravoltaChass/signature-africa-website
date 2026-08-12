#!/usr/bin/env python3
"""Generates admin/config.yml (Decap CMS) fields from content.json so the
editor form always matches exactly what the site reads."""
import json
import os

OUT_DIR = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(OUT_DIR, "content.json"), encoding="utf-8") as f:
    C = json.load(f)

PAGE_LABELS = {
    "global": "Global (Phone, Email, Address)",
    "home": "Home Page",
    "victoria_falls": "Victoria Falls Page",
    "livingstone": "Livingstone Page",
    "kasane": "Kasane Page",
    "fleet": "Our Fleet Page",
    "aviation": "Frontier Aviation Page",
    "contact": "Contact Page",
}

PAGE_ORDER = ["global", "home", "victoria_falls", "livingstone", "kasane", "fleet", "aviation", "contact"]


def label_for(key):
    words = key.replace("_", " ").split()
    small = {"of", "the", "a", "an", "and", "to", "on", "in"}
    out = []
    for i, w in enumerate(words):
        if w.lower() in small and i != 0:
            out.append(w.lower())
        else:
            out.append(w.capitalize())
    return " ".join(out)


def field_for(key, value):
    label = label_for(key)
    if key.endswith("_image"):
        return f'          - {{label: "{label}", name: "{key}", widget: "image"}}'
    is_long = isinstance(value, str) and (len(value) > 70 or "\n" in value)
    widget = "text" if is_long else "string"
    return f'          - {{label: "{label}", name: "{key}", widget: "{widget}"}}'


lines = []
lines.append("backend:")
lines.append("  name: git-gateway")
lines.append("  branch: main")
lines.append("")
lines.append('media_folder: "assets/img/uploads"')
lines.append('public_folder: "assets/img/uploads"')
lines.append("")
lines.append("locale: 'en'")
lines.append("")
lines.append("collections:")
lines.append('  - name: "content"')
lines.append('    label: "Site Content"')
lines.append("    files:")
lines.append('      - file: "content.json"')
lines.append('        label: "All Page Content"')
lines.append('        name: "content"')
lines.append("        fields:")

for page in PAGE_ORDER:
    fields = C[page]
    lines.append(f'          - label: "{PAGE_LABELS.get(page, label_for(page))}"')
    lines.append(f'            name: "{page}"')
    lines.append('            widget: "object"')
    lines.append("            fields:")
    for key, value in fields.items():
        lines.append(field_for(key, value).replace("          - ", "              - "))

yaml_text = "\n".join(lines) + "\n"

admin_dir = os.path.join(OUT_DIR, "admin")
os.makedirs(admin_dir, exist_ok=True)
with open(os.path.join(admin_dir, "config.yml"), "w", encoding="utf-8") as f:
    f.write(yaml_text)

print("wrote", os.path.join(admin_dir, "config.yml"))
print(yaml_text[:1500])

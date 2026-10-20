import fitz

doc = fitz.open("Murtad-V1-27-03-2022.pdf")
p7 = doc[6]
d = p7.get_text("rawdict")

for b in d.get("blocks", []):
    if "lines" in b:
        for l in b["lines"]:
            for sp in l["spans"]:
                for ch in sp.get("chars", []):
                    # ch has: 'c', 'bbox', 'origin', 'glyph'
                    pass

# Let's inspect a sample span's chars
sample_span = d["blocks"][3]["lines"][0]["spans"][0]
print("Span keys:", sample_span.keys())
print("Font:", sample_span["font"])
for ch in sample_span["chars"][:15]:
    print(ch)

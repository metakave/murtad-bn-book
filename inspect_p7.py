import fitz

doc = fitz.open("Murtad-V1-27-03-2022.pdf")
lines = [l for l in doc[6].get_text("text").split("\n") if l.strip()]
for idx, l in enumerate(lines[:10]):
    print(f"L{idx}: {repr(l)}")
    for c in l[:15]:
        print(f"{c}({hex(ord(c))})", end=" ")
    print()

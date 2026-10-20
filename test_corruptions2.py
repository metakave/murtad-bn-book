import fitz

doc = fitz.open("Murtad-V1-27-03-2022.pdf")
cmap_data = doc.xref_stream(2235).decode("latin1", errors="ignore")

# Let's inspect the ToUnicode CMap bfrange and bfchar in detail
for line in cmap_data.split("\n"):
    if "beginbfchar" in line or "beginbfrange" in line:
        print(line)
    elif "<0020>" in line or "<0027>" in line or "<0036>" in line or "<002E>" in line:
        print("   ", line[:80])

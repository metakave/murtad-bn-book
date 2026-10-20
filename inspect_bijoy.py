import fitz

doc = fitz.open("Murtad-V1-27-03-2022.pdf")
page = doc[6]

# Let's inspect raw text stream bytes before CMap mapping
stream = page.get_contents()
for s in stream:
    data = doc.xref_stream(s).decode("latin1", errors="ignore")
    # find lines with Tj
    lines = [l for l in data.split("\n") if "Tj" in l or "TJ" in l]
    print(f"Total Tj/TJ lines: {len(lines)}")
    for l in lines[10:25]:
        print(l)

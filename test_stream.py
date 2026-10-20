import fitz

doc = fitz.open("Murtad-V1-27-03-2022.pdf")
page = doc[6]
stream = page.get_contents()
for s in stream:
    raw = doc.xref_stream(s).decode("latin1", errors="ignore")
    lines = raw.split("\n")
    for l in lines:
        if "Tj" in l or "TJ" in l:
            print(l[:120])

import fitz

doc = fitz.open("Murtad-V1-27-03-2022.pdf")
cmap_data = doc.xref_stream(2235).decode("latin1", errors="ignore")

for line in cmap_data.split("\n"):
    if "0037" in line or "0027" in line or "0039" in line:
        print(line)

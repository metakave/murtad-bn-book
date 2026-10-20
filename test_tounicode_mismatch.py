import fitz

doc = fitz.open("Murtad-V1-27-03-2022.pdf")
cmap_data = doc.xref_stream(2235).decode("latin1", errors="ignore")

# Find line in CMap for 0027 and 0037
for l in cmap_data.split("\n"):
    if "0037" in l:
        print("CMap line for 0037:", l)
    if "0027" in l:
        print("CMap line for 0027:", l)

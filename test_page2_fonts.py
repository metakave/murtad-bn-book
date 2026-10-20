import fitz

doc = fitz.open("Murtad-V1-27-03-2022.pdf")
print("Page 2 fonts:", doc[1].get_fonts())
for f in doc[1].get_fonts():
    xref = f[0]
    print(f"XREF {xref}:", doc.xref_object(xref))

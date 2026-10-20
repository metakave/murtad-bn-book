import fitz

doc = fitz.open('Murtad-V1-27-03-2022.pdf')
# Let us inspect the xrefs of fonts on page 7
for f in doc[6].get_fonts():
    xref = f[0]
    print('XREF:', xref, doc.xref_object(xref))

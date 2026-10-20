import fitz
from fontTools.ttLib import TTFont
import io
import re

doc = fitz.open("Murtad-V1-27-03-2022.pdf")

# Page 7 uses font 27 (Noto Sans Bengali)
fbytes = doc.extract_font(27)
font = TTFont(io.BytesIO(fbytes[3]))
glyphs = font.getGlyphOrder()

# Word: "আইন"
# In PyMuPDF it gave: "আইে"
# Let's find what CIDs were drawn for "আইন" in page 7 stream!
p7_stream = doc.xref_stream(doc[6].get_contents()[0]).decode("latin1", errors="ignore")
# Find line containing "ব্লাসফেমী" or "আইন"
for l in p7_stream.split("\n"):
    if "TJ" in l or "Tj" in l:
        hexes = re.findall(r'<([0-9a-fA-F]+)>', l)
        for h in hexes:
            cids = [int(h[i:i+4], 16) for i in range(0, len(h), 4)]
            # If length is 3 and starts with 0x09 (আ)
            if len(cids) == 3 and cids[0] == 0x09 and cids[1] == 0x0A: # আ ই
                print("Found 'আইন' CIDs:", [f"0x{c:04X}" for c in cids])
                for c in cids:
                    print(f"CID 0x{c:04X} -> Glyph: {glyphs[c]}")

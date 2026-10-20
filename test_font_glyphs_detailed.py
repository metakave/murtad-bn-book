import fitz
from fontTools.ttLib import TTFont
import io

doc = fitz.open("Murtad-V1-27-03-2022.pdf")
fbytes = doc.extract_font(27)
font = TTFont(io.BytesIO(fbytes[3]))
glyphs = font.getGlyphOrder()

# Word: আধুনিক
# Let's see: [<00090026>7<00390037>-10<0027>] TJ [<0014>] TJ
# Indices: 0x09, 0x26, 0x39, 0x37, 0x27, 0x14
cids = [0x09, 0x26, 0x39, 0x37, 0x27, 0x14]
for c in cids:
    print(f"CID 0x{c:04X} ({c}) -> Glyph Name: {glyphs[c] if c < len(glyphs) else 'OUT_OF_RANGE'}")

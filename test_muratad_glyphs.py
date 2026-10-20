import fitz
from fontTools.ttLib import TTFont
import io

doc = fitz.open("Murtad-V1-27-03-2022.pdf")
f_sans = doc.extract_font(27)
font_sans = TTFont(io.BytesIO(f_sans[3]))
glyphs = font_sans.getGlyphOrder()

# Let's inspect line 0 of page 7 stream:
# Word 4 is "মুব়তাদ"
p7_stream = doc.xref_stream(doc[6].get_contents()[0]).decode("latin1", errors="ignore")
line0 = p7_stream.split("\n")[0]
# Word: <002C0039002E002300360025>
# Indices: 0x2C, 0x39, 0x2E, 0x23, 0x36, 0x25
for c in [0x2C, 0x39, 0x2E, 0x23, 0x36, 0x25]:
    print(f"0x{c:02X} -> {glyphs[c]}")

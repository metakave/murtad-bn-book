import fitz
from fontTools.ttLib import TTFont
import io

doc = fitz.open("Murtad-V1-27-03-2022.pdf")

# Let's inspect font 27
fbytes = doc.extract_font(27)
font = TTFont(io.BytesIO(fbytes[3]))
glyphs = font.getGlyphOrder()

# Let's check glyphs for CID 0x27, 0x36, 0x37, 0x3D
print("Glyph 0x27 (39):", glyphs[39])
print("Glyph 0x36 (54):", glyphs[54])
print("Glyph 0x37 (55):", glyphs[55])
print("Glyph 0x3D (61):", glyphs[61])

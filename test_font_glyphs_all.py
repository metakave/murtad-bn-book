import fitz
from fontTools.ttLib import TTFont
import io

doc = fitz.open("Murtad-V1-27-03-2022.pdf")
fbytes = doc.extract_font(27)
font = TTFont(io.BytesIO(fbytes[3]))
glyphs = font.getGlyphOrder()

print(f"Total glyphs: {len(glyphs)}")
for i, g in enumerate(glyphs[:100]):
    print(f"{i:3d} (0x{i:04X}): {g}")

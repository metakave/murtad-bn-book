import fitz
from fontTools.ttLib import TTFont
import io

doc = fitz.open("Murtad-V1-27-03-2022.pdf")
fbytes = doc.extract_font(27)
font = TTFont(io.BytesIO(fbytes[3]))
glyphs = font.getGlyphOrder()
for idx in [0x2B, 0x26F, 0xB2, 0x124, 0xEE, 0x14, 0x1EC, 0x1A0, 0x208, 0x16D]:
    if idx < len(glyphs):
        print(f"Index 0x{idx:X} ({idx}) -> {glyphs[idx]}")

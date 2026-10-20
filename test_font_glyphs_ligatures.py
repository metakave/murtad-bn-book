import fitz
from fontTools.ttLib import TTFont
import io

doc = fitz.open("Murtad-V1-27-03-2022.pdf")
fbytes = doc.extract_font(27)
font = TTFont(io.BytesIO(fbytes[3]))
glyphs = font.getGlyphOrder()

for i in range(80, min(160, len(glyphs))):
    if not glyphs[i].startswith("glyph"):
        print(f"{i:3d} (0x{i:04X}): {glyphs[i]}")
print("--- Check GSUB ---")
if 'GSUB' in font:
    gsub = font['GSUB'].table
    print("Feature list:", [r.FeatureTag for r in gsub.FeatureList.FeatureRecord])

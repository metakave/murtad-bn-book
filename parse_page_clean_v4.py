import fitz
from fontTools.ttLib import TTFont
import io
import re

doc = fitz.open("Murtad-V1-27-03-2022.pdf")

# Page 7 uses 27 for Noto Sans Bengali and 267 for Noto Serif Bengali,Bold
f_sans = doc.extract_font(27)
font_sans = TTFont(io.BytesIO(f_sans[3]))
glyphs_sans = font_sans.getGlyphOrder()

f_serif = doc.extract_font(267)
font_serif = TTFont(io.BytesIO(f_serif[3]))
glyphs_serif = font_serif.getGlyphOrder()

p7_stream = doc.xref_stream(doc[6].get_contents()[0]).decode("latin1", errors="ignore")

curr_font = "sans"
decoded = []
for l in p7_stream.split("\n"):
    if "/F5 " in l or "/F1 " in l:
        curr_font = "sans"
    elif "/F12 " in l or "/F13 " in l:
        curr_font = "serif"
    
    if "TJ" in l or "Tj" in l:
        hexes = re.findall(r'<([0-9a-fA-F]+)>', l)
        text_tokens = []
        for h in hexes:
            for i in range(0, len(h), 4):
                cid = int(h[i:i+4], 16)
                glist = glyphs_serif if curr_font == "serif" else glyphs_sans
                if cid < len(glist):
                    text_tokens.append(glist[cid])
        if text_tokens:
            decoded.append((curr_font, text_tokens))

print(f"Decoded {len(decoded)} glyph groups")
for font_type, tokens in decoded[3:12]:
    print(f"[{font_type}] -> {tokens}")

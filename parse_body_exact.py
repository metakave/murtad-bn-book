import fitz
from fontTools.ttLib import TTFont
import io
import re

doc = fitz.open("Murtad-V1-27-03-2022.pdf")
fbytes = doc.extract_font(27)
font = TTFont(io.BytesIO(fbytes[3]))
glyphs = font.getGlyphOrder()

# Let's inspect the embedded cmap of the TTF itself!
ttf_cmap = {}
for table in font['cmap'].tables:
    if table.isUnicode():
        ttf_cmap = table.cmap
        break

print(f"TTF internal unicode cmap size: {len(ttf_cmap)}")
# Invert TTF cmap: glyph_name -> unicode char
gname_to_unicode = {gname: chr(code) for code, gname in ttf_cmap.items()}

# Let's also parse GSUB ligatures
gsub = font['GSUB'].table
lig_map = {}
for lookup in gsub.LookupList.Lookup:
    for subtable in lookup.SubTable:
        if subtable.LookupType == 4:
            for first_glyph, ligatures in subtable.ligatures.items():
                for lig in ligatures:
                    lig_map[lig.LigGlyph] = [first_glyph] + lig.Component

def expand_glyph(gname):
    if gname in lig_map:
        res = []
        for c in lig_map[gname]:
            res.extend(expand_glyph(c))
        return res
    if gname in gname_to_unicode:
        return [gname_to_unicode[gname]]
    if gname.startswith("uni") and len(gname) == 7:
        try:
            return [chr(int(gname[3:], 16))]
        except:
            pass
    if gname == "space":
        return [" "]
    return [f"<{gname}>"]

# Now test decoding the first Tj line of page 7
# [<00090026>7<00390037>-10<0027>] TJ [<0014>]
# Tokens: 0x09, 0x26, 0x39, 0x37, 0x27, 0x14
cids = [0x09, 0x26, 0x39, 0x37, 0x27, 0x14]
expanded = []
for c in cids:
    g = glyphs[c]
    expanded.extend(expand_glyph(g))

print("Direct glyph expansion for line 1 word 1:")
print("".join(expanded))


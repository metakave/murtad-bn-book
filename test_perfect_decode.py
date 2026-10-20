import fitz
from fontTools.ttLib import TTFont
import io
import re

doc = fitz.open("Murtad-V1-27-03-2022.pdf")

# Extract font 27
fbytes = doc.extract_font(27)
font = TTFont(io.BytesIO(fbytes[3]))
glyphs = font.getGlyphOrder()

# TTF internal unicode cmap
ttf_cmap = {}
for table in font['cmap'].tables:
    if table.isUnicode():
        ttf_cmap = table.cmap
        break
gname_to_unicode = {gname: chr(code) for code, gname in ttf_cmap.items()}

# GSUB ligatures
gsub = font['GSUB'].table
lig_map = {}
for lookup in gsub.LookupList.Lookup:
    for subtable in lookup.SubTable:
        if subtable.LookupType == 4:
            for first_glyph, ligatures in subtable.ligatures.items():
                for lig in ligatures:
                    lig_map[lig.LigGlyph] = [first_glyph] + lig.Component

def expand_glyph(gname, depth=0):
    if depth > 10:
        return []
    if gname in lig_map:
        res = []
        for c in lig_map[gname]:
            res.extend(expand_glyph(c, depth+1))
        return res
    if gname == 'uni09B0':
        return ['র']
    if gname == 'uni09AC':
        return ['ব']
    if gname in gname_to_unicode:
        return [gname_to_unicode[gname]]
    if gname.startswith("uni") and len(gname) == 7:
        try:
            return [chr(int(gname[3:], 16))]
        except:
            pass
    if gname == "space":
        return [" "]
    return []

# Now, let's decode using font glyph names rather than the broken ToUnicode CMap:
print("First 70 glyphs in font:")
for i in range(len(glyphs)):
    exp = "".join(expand_glyph(glyphs[i]))
    if exp:
        print(f"CID 0x{i:04X} ({glyphs[i]}) -> {repr(exp)}")
    if i > 75:
        break

import fitz
from fontTools.ttLib import TTFont
import io
import re

doc = fitz.open("Murtad-V1-27-03-2022.pdf")
fbytes = doc.extract_font(27)
font = TTFont(io.BytesIO(fbytes[3]))
glyphs = font.getGlyphOrder()

ttf_cmap = {}
for table in font['cmap'].tables:
    if table.isUnicode():
        ttf_cmap = table.cmap
        break
gname_to_unicode = {gname: chr(code) for code, gname in ttf_cmap.items()}

lig_map = {}
if 'GSUB' in font:
    gsub = font['GSUB'].table
    for lookup in gsub.LookupList.Lookup:
        for subtable in lookup.SubTable:
            if subtable.LookupType == 4:
                for first_glyph, ligatures in subtable.ligatures.items():
                    for lig in ligatures:
                        lig_map[lig.LigGlyph] = [first_glyph] + lig.Component

def expand(gname, depth=0):
    if depth > 10:
        return []
    if gname in lig_map:
        r = []
        for c in lig_map[gname]:
            r.extend(expand(c, depth+1))
        return r
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

# Test word: আইন
# In stream: <0009000A0027> -> uni0986, uni0987, uni09A8
w_chars = []
for c in [0x09, 0x0A, 0x27]:
    w_chars.extend(expand(glyphs[c]))
print("Result for 'আইন':", "".join(w_chars))

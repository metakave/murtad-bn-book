import fitz
from fontTools.ttLib import TTFont
import io

doc = fitz.open("Murtad-V1-27-03-2022.pdf")
fbytes = doc.extract_font(27)
font = TTFont(io.BytesIO(fbytes[3]))
glyphs = font.getGlyphOrder()

gsub = font['GSUB'].table
ligature_map = {}
for lookup in gsub.LookupList.Lookup:
    for subtable in lookup.SubTable:
        if subtable.LookupType == 4:
            for first_glyph, ligatures in subtable.ligatures.items():
                for lig in ligatures:
                    ligature_map[lig.LigGlyph] = [first_glyph] + lig.Component
        elif subtable.LookupType == 1:
            for inp, out in subtable.mapping.items():
                if out not in ligature_map:
                    ligature_map[out] = [inp]

def glyph_to_chars(gname):
    # If it expands via ligature_map
    if gname in ligature_map:
        res = []
        for c in ligature_map[gname]:
            res.extend(glyph_to_chars(c))
        return res
    if gname.startswith("uni"):
        code = int(gname[3:], 16)
        return [chr(code)]
    if gname == "space":
        return [" "]
    return [f"[{gname}]"]

# Test for word: <00090026>7<00390037>-10<0027>] TJ [<0014>]
# Glyphs: uni0986 (আ), uni09A7 (ধ), uni09C1 (ু), uni09BF (ি), uni09A8 (ন), uni0995 (ক)
# Notice in PDF stream the order was:
# uni0986, uni09A7, uni09C1, uni09BF, uni09A8, uni0995
# In Bengali standard Unicode: আ ধ ু ন ি ক (uni0986 uni09A7 uni09C1 uni09A8 uni09BF uni0995)
# In visual rendering, ি (uni09BF) is rendered before ন (uni09A8)!
# So the PDF stored visual glyph order: uni09BF uni09A8 !
print("Raw visual order in PDF:")
for cid in [0x09, 0x26, 0x39, 0x37, 0x27, 0x14]:
    print(glyphs[cid], "".join(glyph_to_chars(glyphs[cid])))


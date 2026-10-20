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

# Fix known Noto Bengali glyph discrepancies:
# In Assamese/Bengali Noto font:
# uni09B0 is RA in Unicode. If font mapped uni09B0 to ব় (BA + nukta), fix it:
# Let's check what ttf_cmap has for 0x09B0:
print("0x09B0 in ttf_cmap maps to:", ttf_cmap.get(0x09B0))
print("0x09AC in ttf_cmap maps to:", ttf_cmap.get(0x09AC))

lig_map = {}
if 'GSUB' in font:
    gsub = font['GSUB'].table
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

def fix_bengali_visual_order(text):
    # Fix okar split (ে + া -> ো)
    text = text.replace('\u09C7\u09BE', '\u09CB')
    # Fix ba + nukta if accidentally introduced
    text = text.replace('ব়', 'র')
    
    C = r'(?:[\u0995-\u09B9\u09DC-\u09DF]\u09BC?)'
    CLUSTER = rf'(?:{C}(?:\u09CD{C})*)'
    # Pre-kar followed by cluster: (ি|ে|ৈ)(CLUSTER) -> (CLUSTER)\1
    res = re.sub(rf'([\u09BF\u09C7\u09C8])({CLUSTER})', r'\2\1', text)
    return res

# Let's test on page 7 lines

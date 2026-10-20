import fitz
from fontTools.ttLib import TTFont
import io
import re

doc = fitz.open("Murtad-V1-27-03-2022.pdf")

font_cache = {}

def get_font_info(doc, xref, fname):
    if fname in font_cache:
        return font_cache[fname]
    fbytes = doc.extract_font(xref)
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
                        
    info = {
        'glyphs': glyphs,
        'gname_to_unicode': gname_to_unicode,
        'lig_map': lig_map,
    }
    font_cache[fname] = info
    return info

for f in doc[6].get_fonts():
    get_font_info(doc, f[0], f[3])

def expand_glyph(info, gname, depth=0):
    if depth > 10:
        return []
    if gname in info['lig_map']:
        res = []
        for c in info['lig_map'][gname]:
            res.extend(expand_glyph(info, c, depth+1))
        return res
    if gname == 'uni09B0':
        return ['র']
    if gname == 'uni09AC':
        return ['ব']
    if gname in info['gname_to_unicode']:
        return [info['gname_to_unicode'][gname]]
    if gname.startswith("uni") and len(gname) == 7:
        try:
            return [chr(int(gname[3:], 16))]
        except:
            pass
    if gname == "space":
        return [" "]
    return []

def fix_bengali_visual_order(text):
    text = text.replace('\u09C7\u09BE', '\u09CB')
    text = text.replace('ব়', 'র')
    
    # Notice Reph: in the text we see "ধম্ীয়", "নিদে্শের", "মাক্নি", "চচ্া", "পূণ্"
    # Notice the sequence: ক্ + র্ or ম্ + র্ -> Reph should be BEFORE consonant!
    # E.g. ম্ + র্ (0x9ae 0x9cd 0x9b0) -> র্ + ম (0x9b0 0x9cd 0x9ae) = র্ম!
    # In Bengali: র্ম is র + ্ + ম. But in visual typing people typed ম + ্ + র (বা র-ফলা/রেফ)
    text = re.sub(r'([\u0995-\u09B9\u09DC-\u09DF])\u09CDর', r'র\u09CD\1', text)
    
    # Also check "দশে" -> "দেশে", "নতিবাচক" -> "নেতিবাচক", "য শরীয়া" -> "যে শরীয়া", "কানো" -> "কোনো", "জার করে" -> "জোর করে"
    return text

print("Fixing test:")
print(fix_bengali_visual_order("ধম্ীয় নিদে্শের মাক্নি চচ্া পূণ্"))

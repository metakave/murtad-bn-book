import fitz
from fontTools.ttLib import TTFont
import io
import re

doc = fitz.open("Murtad-V1-27-03-2022.pdf")

# Preload fonts
font_info = {}
for f in doc[6].get_fonts():
    xref = f[0]
    fname = f[3]
    if fname not in font_info:
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
        font_info[fname] = {
            'glyphs': glyphs,
            'gname_to_unicode': gname_to_unicode,
            'lig_map': lig_map
        }

def expand(info, gname, depth=0):
    if depth > 10:
        return []
    if gname in info['lig_map']:
        r = []
        for c in info['lig_map'][gname]:
            r.extend(expand(info, c, depth+1))
        return r
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
    
    C = r'(?:[\u0995-\u09B9\u09DC-\u09DF]\u09BC?)'
    CLUSTER = rf'(?:{C}(?:\u09CD{C})*)'
    res = re.sub(rf'([\u09BF\u09C7\u09C8])({CLUSTER})', r'\2\1', text)
    
    # Reph: C + ্ + র্ -> র্ + C
    res = re.sub(r'([\u0995-\u09B9\u09DC-\u09DF])\u09CD\u09CD?([র\u09B0])', lambda m: m.group(2) + '\u09CD' + m.group(1), res)
    
    # Spaced words fix
    res = re.sub(r'ভ\s*ূ\s*ি\s*ম\s*ক\s*া', 'ভূমিকা', res)
    return res

# Let's inspect the exact characters in "আইন" and "ব্লাসফেমী" when extracted through stream!
p7 = doc[6]
# Let's dump all text lines reconstructed from stream without removing spaces between words:

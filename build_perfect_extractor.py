import fitz
from fontTools.ttLib import TTFont
import io
import re

doc = fitz.open("Murtad-V1-27-03-2022.pdf")

# Preload font and GSUB mapping
font_cache = {}

def load_font(xref):
    if xref in font_cache:
        return font_cache[xref]
    fbytes = doc.extract_font(xref)
    font = TTFont(io.BytesIO(fbytes[3]))
    glyphs = font.getGlyphOrder()
    
    # Internal cmap: unicode code -> glyph name
    ttf_cmap = {}
    for table in font['cmap'].tables:
        if table.isUnicode():
            ttf_cmap = table.cmap
            break
            
    # Reverse cmap: glyph name -> unicode char
    g_to_u = {g: chr(code) for code, g in ttf_cmap.items()}
    
    # GSUB SingleSubst reverse (e.g. glyph00492 -> uni09BF)
    single_rev = {}
    # GSUB LigatureSubst (e.g. glyph00178 -> [g1, g2...])
    lig_map = {}
    
    if 'GSUB' in font:
        gsub = font['GSUB'].table
        for lookup in gsub.LookupList.Lookup:
            for subtable in lookup.SubTable:
                if subtable.LookupType == 1: # SingleSubst
                    for k, v in subtable.mapping.items():
                        # v substituted for k, so v resolves back to k
                        single_rev[v] = k
                elif subtable.LookupType == 4: # LigatureSubst
                    for first_glyph, ligatures in subtable.ligatures.items():
                        for lig in ligatures:
                            lig_map[lig.LigGlyph] = [first_glyph] + lig.Component
                            
    info = {
        'glyphs': glyphs,
        'g_to_u': g_to_u,
        'single_rev': single_rev,
        'lig_map': lig_map
    }
    font_cache[xref] = info
    return info

def resolve_glyph(info, gname, depth=0):
    if depth > 10:
        return []
    if gname in info['lig_map']:
        res = []
        for c in info['lig_map'][gname]:
            res.extend(resolve_glyph(info, c, depth+1))
        return res
    if gname in info['single_rev']:
        orig = info['single_rev'][gname]
        return resolve_glyph(info, orig, depth+1)
    if gname == 'uni09B0':
        return ['র']
    if gname == 'uni09AC':
        return ['ব']
    if gname in info['g_to_u']:
        return [info['g_to_u'][gname]]
    if gname.startswith("uni") and len(gname) == 7:
        try:
            return [chr(int(gname[3:], 16))]
        except:
            pass
    if gname == 'space':
        return [' ']
    return []

def fix_bengali_visual_order(text):
    text = text.replace('\u09C7\u09BE', '\u09CB') # okar
    
    # Pre-kar followed by cluster: (ি|ে|ৈ)(CLUSTER) -> (CLUSTER)\1
    C = r'(?:[\u0995-\u09B9\u09DC-\u09DF]\u09BC?)'
    CLUSTER = rf'(?:{C}(?:\u09CD{C})*)'
    res = re.sub(rf'([\u09BF\u09C7\u09C8])({CLUSTER})', r'\2\1', text)
    
    # Reph: C + ্ + র্ -> র্ + C
    res = re.sub(r'([\u0995-\u09B9\u09DC-\u09DF])\u09CD\u09CD?([র\u09B0])', lambda m: m.group(2) + '\u09CD' + m.group(1), res)
    return res

# Test on the word muslimder:
# ['uni09AE', 'uni09C1', 'uni09B8', 'glyph00492', 'uni09B2', 'uni09AE', 'uni09C7', 'uni09A6', 'uni09B0']
info_sans = load_font(27)
test_tokens = ['uni09AE', 'uni09C1', 'uni09B8', 'glyph00492', 'uni09B2', 'uni09AE', 'uni09C7', 'uni09A6', 'uni09B0']
resolved = []
for t in test_tokens:
    resolved.extend(resolve_glyph(info_sans, t))
raw_w = "".join(resolved)
print("Raw resolved:", repr(raw_w))
fixed_w = fix_bengali_visual_order(raw_w)
print("Fixed word:", repr(fixed_w))
print("Is correct 'মুসলিমদের'?", fixed_w == "মুসলিমদের")


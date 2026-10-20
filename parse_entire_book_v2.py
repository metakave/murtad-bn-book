import fitz
from fontTools.ttLib import TTFont
import io
import re

doc = fitz.open("Murtad-V1-27-03-2022.pdf")

font_cache = {}

def load_font(xref):
    if xref in font_cache:
        return font_cache[xref]
    fbytes = doc.extract_font(xref)
    font = TTFont(io.BytesIO(fbytes[3]))
    glyphs = font.getGlyphOrder()
    
    ttf_cmap = {}
    for table in font['cmap'].tables:
        if table.isUnicode():
            ttf_cmap = table.cmap
            break
            
    g_to_u = {g: chr(code) for code, g in ttf_cmap.items()}
    single_rev = {}
    lig_map = {}
    
    if 'GSUB' in font:
        gsub = font['GSUB'].table
        for lookup in gsub.LookupList.Lookup:
            for subtable in lookup.SubTable:
                if subtable.LookupType == 1:
                    for k, v in subtable.mapping.items():
                        # Only map if v is a variant/contextual glyph (e.g. glyphXXXX)
                        if v.startswith('glyph') and not k.startswith('glyph'):
                            single_rev[v] = k
                elif subtable.LookupType == 4:
                    for first_glyph, ligatures in subtable.ligatures.items():
                        for lig in ligatures:
                            if lig.LigGlyph != 'uni09B0':
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
    if gname == 'uni09B0':
        return ['র']
    if gname == 'uni09AC':
        return ['ব']
    if gname.startswith("uni") and len(gname) == 7:
        try:
            return [chr(int(gname[3:], 16))]
        except:
            pass
    if gname in info['g_to_u']:
        return [info['g_to_u'][gname]]
    if gname in info['lig_map']:
        res = []
        for c in info['lig_map'][gname]:
            res.extend(resolve_glyph(info, c, depth+1))
        return res
    if gname in info['single_rev']:
        orig = info['single_rev'][gname]
        return resolve_glyph(info, orig, depth+1)
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

p7 = doc[6]
font_alias_map = {f[4]: load_font(f[0]) for f in p7.get_fonts()}
p7_stream = doc.xref_stream(p7.get_contents()[0]).decode("latin1", errors="ignore")
curr_font = None
decoded_tokens = []
for line in p7_stream.split("\n"):
    fm = re.match(r'/(\w+)\s+([\d\.]+)\s+Tf', line)
    if fm:
        curr_font = font_alias_map.get(fm.group(1))
    
    if ("TJ" in line or "Tj" in line) and curr_font:
        items = re.findall(r'(<[0-9a-fA-F]+>|\([^)]*\)|-?[\d\.]+)', line)
        for it in items:
            if it.startswith("<") and it.endswith(">"):
                h = it[1:-1]
                chars = []
                for i in range(0, len(h), 4):
                    cid = int(h[i:i+4], 16)
                    if cid < len(curr_font['glyphs']):
                        chars.extend(resolve_glyph(curr_font, curr_font['glyphs'][cid]))
                s = "".join(chars)
                decoded_tokens.append(s)
            elif it.startswith("(") and it.endswith(")"):
                decoded_tokens.append(it[1:-1])
            else:
                try:
                    val = float(it)
                    if val < -250:
                        decoded_tokens.append(" ")
                except:
                    pass
    elif "T*" in line:
        decoded_tokens.append("\n")

full_p7 = "".join(decoded_tokens)
full_p7 = fix_bengali_visual_order(full_p7)
print("=== PERFECTLY EXTRACTED PAGE 7 ===")
print(full_p7[:600])


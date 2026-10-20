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
    C = r'(?:[\u0995-\u09B9\u09DC-\u09DF]\u09BC?)'
    CLUSTER = rf'(?:{C}(?:\u09CD{C})*)'
    # 1. Pre-kar followed by cluster: (ি|ে|ৈ)(CLUSTER) -> (CLUSTER)\1
    res = re.sub(rf'([\u09BF\u09C7\u09C8])({CLUSTER})', r'\2\1', text)
    return res

page = doc[6]
stream = page.get_contents()
full_text = []
for s in stream:
    data = doc.xref_stream(s).decode("latin1", errors="ignore")
    current_font = 'ABCDEE+Noto Sans Bengali'
    for line in data.split("\n"):
        fm = re.match(r'/(\w+)\s+([\d\.]+)\s+Tf', line)
        if fm:
            for f in page.get_fonts():
                if f[4] == fm.group(1):
                    current_font = f[3]
                    break
        if "Tj" in line or "TJ" in line:
            hex_parts = re.findall(r'<([0-9a-fA-F]+)>', line)
            if hex_parts and current_font in font_cache:
                info = font_cache[current_font]
                line_chars = []
                for h in hex_parts:
                    for i in range(0, len(h), 4):
                        cid = int(h[i:i+4], 16)
                        if cid < len(info['glyphs']):
                            gname = info['glyphs'][cid]
                            line_chars.extend(expand_glyph(info, gname))
                raw_s = "".join(line_chars)
                fixed_s = fix_bengali_visual_order(raw_s)
                if fixed_s.strip():
                    full_text.append(fixed_s.strip())

print(f"Decoded {len(full_text)} segments:")
for idx, t in enumerate(full_text[:20]):
    print(f"{idx}: {t}")


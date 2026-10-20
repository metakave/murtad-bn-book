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

def clean_bengali_text(text):
    text = text.replace('\u09C7\u09BE', '\u09CB') # okar
    
    # Pre-kar followed by cluster: (ি|ে|ৈ)(CLUSTER) -> (CLUSTER)\1
    C = r'(?:[\u0995-\u09B9\u09DC-\u09DF]\u09BC?)'
    CLUSTER = rf'(?:{C}(?:\u09CD{C})*)'
    text = re.sub(rf'([\u09BF\u09C7\u09C8])({CLUSTER})', r'\2\1', text)
    
    # Reph: C + ্ + র্ -> র্ + C
    text = re.sub(r'([\u0995-\u09B9\u09DC-\u09DF])\u09CD\u09CD?([র\u09B0])', lambda m: m.group(2) + '\u09CD' + m.group(1), text)
    
    # Postposed reph:
    text = re.sub(r'([\u0995-\u09B9\u09DC-\u09DF])([\u09BE-\u09CC])\u09CD', lambda m: 'র্' + m.group(1) + m.group(2), text)
    text = re.sub(r'([\u0995-\u09B9\u09DC-\u09DF])\u09CD([\u09BE-\u09CC])', lambda m: 'র্' + m.group(1) + m.group(2), text)
    text = re.sub(r'([\u0995-\u09B9\u09DC-\u09DF])\u09CD(?=[ \t\n\r।,!?\(\)\"\']|$)', lambda m: 'র্' + m.group(1), text)
    
    # Preposed rafala at start of word:
    text = re.sub(r'(^|[\s\(\"\'])র্([পসবভটডতদকগখয])', lambda m: m.group(1) + m.group(2) + '্' + 'র', text)
    text = re.sub(r'([আআইউএও])র্([পসবভটডতদকগখ])', lambda m: m.group(1) + m.group(2) + '্' + 'র', text)
    
    # Word fixes
    text = text.replace('দে্শে', 'র্দেশে')
    text = text.replace('নিদশ্ন', 'নিদর্শন')
    text = text.replace('ধম্ত্যাগ', 'ধর্মত্যাগ')
    text = text.replace('ধম্নিন্দা', 'ধর্মনিন্দা')
    text = text.replace('সামন্জস্য', 'সামঞ্জস্য')
    text = text.replace('চচ্া', 'চর্চা')
    text = text.replace('উত্স', 'উৎস')
    text = text.replace('ব়', 'র')
    
    return text

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
    elif "T*" in line or "' " in line:
        decoded_tokens.append("\n")

full_p7 = "".join(decoded_tokens)
full_p7 = clean_bengali_text(full_p7)
print("=== PERFECTLY EXTRACTED PAGE 7 ===")
for p in full_p7.split("\n")[:10]:
    if p.strip():
        print(p.strip())


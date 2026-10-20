import fitz
from fontTools.ttLib import TTFont
import io
import re

doc = fitz.open("Murtad-V1-27-03-2022.pdf")

# Preload fonts
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
    # Fix okar split (ে + া -> ো)
    text = text.replace('\u09C7\u09BE', '\u09CB')
    # Fix ba + nukta if accidentally created in decomposed form
    text = text.replace('ব়', 'র')
    
    C = r'(?:[\u0995-\u09B9\u09DC-\u09DF]\u09BC?)'
    CLUSTER = rf'(?:{C}(?:\u09CD{C})*)'
    # Pre-kar followed by cluster: (ি|ে|ৈ)(CLUSTER) -> (CLUSTER)\1
    res = re.sub(rf'([\u09BF\u09C7\u09C8])({CLUSTER})', r'\2\1', text)
    # Consecutive spaces
    res = re.sub(r'[ \t]+', ' ', res)
    return res

page = doc[6]
blocks = page.get_text("blocks")
print(f"Total blocks on page 7: {len(blocks)}")

# Let's inspect text lines from dict
d = page.get_text("rawdict")
lines_output = []
for block in d.get("blocks", []):
    if "lines" in block:
        block_text = []
        for line in block["lines"]:
            line_str = []
            for span in line["spans"]:
                # span has 'chars'
                if "chars" in span:
                    for ch in span["chars"]:
                        c = ch.get("c", "")
                        line_str.append(c)
            raw = "".join(line_str)
            block_text.append(raw)
        p = " ".join(block_text).strip()
        if p:
            lines_output.append(p)

for idx, p in enumerate(lines_output[:8]):
    print(f"P{idx}: {repr(p[:100])}")

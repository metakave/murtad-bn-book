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

# Let's inspect the first 5 Tj lines on page 7
p7_stream = doc.xref_stream(doc[6].get_contents()[0]).decode("latin1", errors="ignore")
info = font_info['ABCDEE+Noto Sans Bengali']

lines = p7_stream.split("\n")
decoded_lines = []
for l in lines:
    if "TJ" in l or "Tj" in l:
        # Check if it has text
        tokens = re.findall(r'(<[0-9a-fA-F]+>|\([^)]*\)|-?[\d\.]+)', l)
        s_chars = []
        for t in tokens:
            if t.startswith("<"):
                h = t[1:-1]
                for i in range(0, len(h), 4):
                    cid = int(h[i:i+4], 16)
                    if cid < len(info['glyphs']):
                        s_chars.extend(expand(info, info['glyphs'][cid]))
            elif t.startswith("("):
                s_chars.append(t[1:-1])
        s = "".join(s_chars)
        if s.strip():
            decoded_lines.append(s)

print(f"Total decoded TJ/Tj lines: {len(decoded_lines)}")
for idx, l in enumerate(decoded_lines[:15]):
    print(f"L{idx:2d}: {repr(l)}")


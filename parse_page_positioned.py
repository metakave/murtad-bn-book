import fitz
from fontTools.ttLib import TTFont
import io
import re

doc = fitz.open("Murtad-V1-27-03-2022.pdf")

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
    
    # Pre-kar followed by cluster: (ি|ে|ৈ)(CLUSTER) -> (CLUSTER)\1
    C = r'(?:[\u0995-\u09B9\u09DC-\u09DF]\u09BC?)'
    CLUSTER = rf'(?:{C}(?:\u09CD{C})*)'
    res = re.sub(rf'([\u09BF\u09C7\u09C8])({CLUSTER})', r'\2\1', text)
    
    # Reph: C + ্ + র্ -> র্ + C
    res = re.sub(r'([\u0995-\u09B9\u09DC-\u09DF])\u09CD\u09CD?([র\u09B0])', lambda m: m.group(2) + '\u09CD' + m.group(1), res)
    
    # Fix broken spaced words
    res = re.sub(r'ভ\s*ূ\s*ি\s*ম\s*ক\s*া', 'ভূমিকা', res)
    res = re.sub(r'([ক-হ])\s+([া-ৌ্])', r'\1\2', res)
    res = re.sub(r'([া-ৌ])\s+([ক-হ])', r'\1\2', res)
    
    return res

def parse_pdf_page_content(doc, page_num):
    page = doc[page_num]
    font_alias_map = {f[4]: f[3] for f in page.get_fonts()}
    
    positioned = []
    current_font = None
    font_size = 12.0
    tm = [1, 0, 0, 1, 0, 0]
    tlm = [1, 0, 0, 1, 0, 0]
    
    for s in page.get_contents():
        raw = doc.xref_stream(s).decode("latin1", errors="ignore")
        lines = raw.split("\n")
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            m_tf = re.search(r'/(\w+)\s+([\d\.]+)\s+Tf', line)
            if m_tf:
                fname = font_alias_map.get(m_tf.group(1))
                if fname and fname in font_info:
                    current_font = font_info[fname]
                font_size = float(m_tf.group(2))
                
            m_tm = re.search(r'([\d\.\-]+)\s+([\d\.\-]+)\s+([\d\.\-]+)\s+([\d\.\-]+)\s+([\d\.\-]+)\s+([\d\.\-]+)\s+Tm', line)
            if m_tm:
                tm = [float(m_tm.group(i)) for i in range(1, 7)]
                tlm = list(tm)
                
            m_td = re.search(r'([\d\.\-]+)\s+([\d\.\-]+)\s+Td', line)
            if m_td:
                tx, ty = float(m_td.group(1)), float(m_td.group(2))
                tlm[4] += tx
                tlm[5] += ty
                tm = list(tlm)
                
            if ("Tj" in line or "TJ" in line) and current_font:
                items = re.findall(r'(<[0-9a-fA-F]+>|\([^)]*\)|-?[\d\.]+)', line)
                curr_x = tm[4]
                curr_y = tm[5]
                text_chars = []
                for it in items:
                    if it.startswith("<") and it.endswith(">"):
                        h = it[1:-1]
                        for i in range(0, len(h), 4):
                            cid = int(h[i:i+4], 16)
                            if cid < len(current_font['glyphs']):
                                gname = current_font['glyphs'][cid]
                                text_chars.extend(expand(current_font, gname))
                    elif it.startswith("(") and it.endswith(")"):
                        text_chars.append(it[1:-1])
                    else:
                        try:
                            val = float(it)
                            if val < -300:
                                text_chars.append(" ")
                        except:
                            pass
                
                txt = "".join(text_chars)
                if txt.strip():
                    positioned.append((curr_x, curr_y, font_size, txt))
    
    positioned.sort(key=lambda item: (-round(item[1], 1), round(item[0], 1)))
    
    lines = []
    curr_line_y = None
    curr_line_items = []
    
    for item in positioned:
        x, y, sz, txt = item
        if curr_line_y is None or abs(y - curr_line_y) > 4:
            if curr_line_items:
                curr_line_items.sort(key=lambda it: it[0])
                line_str = ""
                prev_x = None
                for it in curr_line_items:
                    if prev_x is not None and (it[0] - prev_x > 3):
                        line_str += " "
                    line_str += it[3]
                    prev_x = it[0] + len(it[3]) * 5
                lines.append((curr_line_y, line_str))
            curr_line_y = y
            curr_line_items = [item]
        else:
            curr_line_items.append(item)
            
    if curr_line_items:
        curr_line_items.sort(key=lambda it: it[0])
        line_str = ""
        prev_x = None
        for it in curr_line_items:
            if prev_x is not None and (it[0] - prev_x > 3):
                line_str += " "
            line_str += it[3]
            prev_x = it[0] + len(it[3]) * 5
        lines.append((curr_line_y, line_str))
        
    cleaned_lines = []
    for y, l in lines:
        fixed = fix_bengali_visual_order(l)
        fixed = re.sub(r'[ \t]+', ' ', fixed).strip()
        if fixed:
            cleaned_lines.append(fixed)
            
    return cleaned_lines

p7_lines = parse_pdf_page_content(doc, 6)
for idx, l in enumerate(p7_lines[:15]):
    print(f"{idx:2d}: {l}")


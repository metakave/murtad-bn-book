import fitz
from fontTools.ttLib import TTFont
import io
import re
import json

doc = fitz.open("Murtad-V1-27-03-2022.pdf")

font_cache = {}

def load_font(xref):
    if xref in font_cache:
        return font_cache[xref]
    try:
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
    except Exception as e:
        return None

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
    
    # Comprehensive replacements
    replacements = {
        'দে্শে': 'র্দেশে',
        'নিদশ্ন': 'নিদর্শন',
        'ধম্ত্যাগ': 'ধর্মত্যাগ',
        'ধম্নিন্দা': 'ধর্মনিন্দা',
        'সামন্জস্য': 'সামঞ্জস্য',
        'চচ্া': 'চর্চা',
        'উত্স': 'উৎস',
        'ব়': 'র',
        'মার্তায়': 'মাত্রায়',
        'মাক্নি': 'মার্কিন',
        'যুক্তরাষ্র্ট': 'যুক্তরাষ্ট্র',
        'ধম্হীন': 'ধর্মহীন',
        'ধম্কে': 'ধর্মকে',
        'ধম্ই': 'ধর্মই',
        'ধম্': 'ধর্ম',
        'নিদ্শে': 'নির্দেশ',
        'প্রতির্কিয়া': 'প্রতিক্রিয়া',
        'সূচীপর্ত': 'সূচীপত্র',
        'সষটার': 'স্রষ্টার',
        'পথম': 'প্রথম',
        'পকাশ': 'প্রকাশ',
        'রিসাচ': 'রিসার্চ',
        'সমপাদক': 'সম্পাদক',
        'মোহামমদ': 'মোহাম্মদ',
        'পতিষাতা': 'প্রতিষ্ঠাতা',
        'ইকবরা': 'ইক্বরা',
        'পতিপালক': 'প্রতিপালক',
        'পবিত': 'পবিত্র',
        'পশংসা': 'প্রশংসা',
        'একমাত': 'একমাত্র',
        'তঁার': 'তাঁর',
        'বানদাদের': 'বান্দাদের',
        'অনুগহশীল': 'অনুগ্রহশীল',
        'ধমতযাগের': 'ধর্মত্যাগের',
        'জনয': 'জন্য',
        'হতযা': 'হত্যা',
        'পসগে': 'প্রসঙ্গে',
        'উপসথাপিত': 'উপস্থাপিত',
        'পকৃত': 'প্রকৃত',
        'তাৎপয': 'তাৎপর্য',
        'বনধুকরণ': 'বন্ধুকরণ',
        'পযালোচনা': 'পর্যালোচনা'
    }
    for k, v in replacements.items():
        text = text.replace(k, v)
        
    text = re.sub(r'আল\s+কুরআনের\s+আলোকে\s+মুরতাদ\s+হত্যার\s+অবৈধতা\s+\d+\s*\/\s*193', '', text)
    text = re.sub(r'[ \t]+', ' ', text)
    return text.strip()

def extract_page_text(page_index):
    page = doc[page_index]
    font_alias_map = {}
    for f in page.get_fonts():
        f_info = load_font(f[0])
        if f_info:
            font_alias_map[f[4]] = f_info
            
    contents = page.get_contents()
    if not contents:
        return ""
        
    decoded_tokens = []
    curr_font = None
    
    for s in contents:
        stream_data = doc.xref_stream(s).decode("latin1", errors="ignore")
        for line in stream_data.split("\n"):
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
                        decoded_tokens.append("".join(chars))
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
                decoded_tokens.append("\n\n")

    raw_text = "".join(decoded_tokens)
    return clean_bengali_text(raw_text)

# Table of Contents definition with PDF page numbers
toc_entries = [
    {"id": "intro", "title": "ভূমিকা", "start_page": 7, "end_page": 12},
    {"id": "summary", "title": "এক নজরে মূল প্রতিপাদ্য", "start_page": 13, "end_page": 15},
    {"id": "preliminary", "title": "প্রাথমিক কথা", "start_page": 16, "end_page": 18},
    {"id": "prophet_duty", "title": "রাসূলের দায়িত্ব ও ধর্মীয় স্বাধীনতা", "start_page": 19, "end_page": 36, "subsections": [
        {"title": "[ক] রাসূলের দায়িত্ব শুধুমাত্র বালাগ/প্রচার, ধর্ম অবলম্বনের ক্ষেত্রে প্রত্যেকে স্বাধীন, জবরদস্তির কোনো অবকাশ নেই", "page": 19},
        {"title": "[খ] ইসলামী দাওয়াতের মূল কর্মপন্থা এবং ধর্মীয় স্বাধীনতা সংরক্ষণ", "page": 28}
    ]},
    {"id": "shirk_crime", "title": "শিরকের অপরাধ ও ধর্মীয় স্বাধীনতা", "start_page": 37, "end_page": 43},
    {"id": "propaganda_defense", "title": "ধর্মীয় বিষয়ে মিথ্যারোপ, কটূক্তি ও অপপ্রচারের মোকাবেলায় রাসূল ও মু'মিনদের করণীয়", "start_page": 44, "end_page": 60},
    {"id": "doubt_criticism", "title": "ধর্মবিষয়ে সন্দেহ, সমালোচনামুখী দৃষ্টিভঙ্গি, জিজ্ঞাসা ও জবাব", "start_page": 61, "end_page": 68},
    {"id": "religious_social_crimes", "title": "ধর্মীয় অপরাধ বনাম সামাজিক অপরাধ", "start_page": 69, "end_page": 74},
    {"id": "state_treaties", "title": "রাষ্ট্রীয় কর্তৃত্ব কাঠামো, রাজনৈতিক চুক্তি ও ধর্মীয় স্বাধীনতা", "start_page": 75, "end_page": 97},
    {"id": "apostasy_heresy", "title": "মুরতাদ, ইলহাদ ও তাহরীফ প্রসঙ্গ", "start_page": 98, "end_page": 118, "subsections": [
        {"title": "মুরতাদ প্রসঙ্গ", "page": 98},
        {"title": "ইলহাদ প্রসঙ্গ", "page": 111},
        {"title": "তাহরীফ প্রসঙ্গ", "page": 112}
    ]},
    {"id": "lawful_death_penalty", "title": "ন্যায়সঙ্গত মৃত্যুদণ্ড ও অন্যায় হত্যা", "start_page": 119, "end_page": 124},
    {"id": "apostasy_killing_illegal", "title": "ধর্মত্যাগের জন্য হত্যা অবৈধ", "start_page": 125, "end_page": 135},
    {"id": "unislamic_killing", "title": "ধর্মত্যাগের জন্য হত্যা অনৈসলামিক রীতি", "start_page": 136, "end_page": 138},
    {"id": "verses_analysis", "title": "মুরতাদ হত্যা প্রসঙ্গে উপস্থাপিত আয়াতের প্রকৃত তাৎপর্য", "start_page": 139, "end_page": 160},
    {"id": "constitutional_laws", "title": "সাংবিধানিক আইন-বিধান বনাম নির্বাহী আইন-বিধান", "start_page": 161, "end_page": 174},
    {"id": "hadith_review", "title": "মুরতাদ হত্যা প্রসঙ্গে উপস্থাপিত হাদীসের পর্যালোচনা", "start_page": 175, "end_page": 181},
    {"id": "conclusion", "title": "শেষকথা", "start_page": 182, "end_page": 183},
    {"id": "terminology", "title": "পরিভাষা", "start_page": 184, "end_page": 189},
    {"id": "bibliography", "title": "তথ্যসূত্র ও গ্রন্থপঞ্জি", "start_page": 190, "end_page": 192},
    {"id": "about_book", "title": "বইটি সম্পর্কে", "start_page": 193, "end_page": 193}
]

print("Extracting all 193 pages into book data...")
all_pages = []
for p in range(len(doc)):
    text = extract_page_text(p)
    all_pages.append({
        "pageNumber": p + 1,
        "content": text
    })

chapters = []
for item in toc_entries:
    ch_id = item["id"]
    title = item["title"]
    start_p = item["start_page"]
    end_p = item["end_page"]
    
    ch_pages = [all_pages[p_idx] for p_idx in range(start_p - 1, min(end_p, len(all_pages)))]
    # Filter empty lines and format paragraphs
    paragraphs = []
    for pg in ch_pages:
        raw_paras = pg["content"].split("\n\n")
        for rp in raw_paras:
            clean_p = rp.strip()
            if clean_p and clean_p != title:
                paragraphs.append(clean_p)
                
    # Approximate reading time (average Bengali reading speed: 180 words per minute)
    total_words = sum(len(p.split()) for p in paragraphs)
    est_minutes = max(1, round(total_words / 180))
    
    chapters.append({
        "id": ch_id,
        "title": title,
        "startPage": start_p,
        "endPage": end_p,
        "wordCount": total_words,
        "readTimeMinutes": est_minutes,
        "paragraphs": paragraphs,
        "subsections": item.get("subsections", [])
    })

book_meta = {
    "title": "আল কুরআনের আলোকে মুরতাদ হত্যার অবৈধতা",
    "englishTitle": "The Illegality of Killing an Apostate in the Light of the Quran",
    "compiler": "শওকত জাওহার (রিসার্চ ফেলো, ইক্বরা)",
    "editor": "সাদিক মোহাম্মদ আলম (প্রতিষ্ঠাতা, ইক্বরা)",
    "publisher": "দি ইন্সটিটিউট অব কুরআনিক রিসার্চ এন্ড এ্যাপ্লিকেশন (ইক্বরা)",
    "publicationDate": "মে ২০২২",
    "totalPages": 193,
    "totalChapters": len(chapters),
    "chapters": chapters
}

with open("book_data.json", "w", encoding="utf-8") as f:
    json.dump(book_meta, f, ensure_ascii=False, indent=2)

print(f"Extraction complete! Saved {len(chapters)} chapters into book_data.json.")
for ch in chapters:
    print(f"- {ch['title']} ({ch['startPage']}-{ch['endPage']}): {len(ch['paragraphs'])} paragraphs, {ch['wordCount']} words (~{ch['readTimeMinutes']} min)")


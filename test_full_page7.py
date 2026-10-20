import fitz
from fontTools.ttLib import TTFont
import io
import re

doc = fitz.open("Murtad-V1-27-03-2022.pdf")

# Extract font dictionaries for all fonts used
fonts = {}
for f in doc[6].get_fonts():
    xref = f[0]
    fname = f[3]
    if xref not in fonts:
        try:
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
            fonts[fname] = {
                'glyphs': glyphs,
                'gname_to_unicode': gname_to_unicode,
                'lig_map': lig_map
            }
        except Exception as e:
            pass

print("Loaded fonts:", list(fonts.keys()))


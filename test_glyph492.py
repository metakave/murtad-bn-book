import fitz
from fontTools.ttLib import TTFont
import io

doc = fitz.open("Murtad-V1-27-03-2022.pdf")
f_sans = doc.extract_font(27)
font_sans = TTFont(io.BytesIO(f_sans[3]))

# Let's inspect GSUB of font_sans specifically for glyph00492
gsub = font_sans['GSUB'].table
for idx, lookup in enumerate(gsub.LookupList.Lookup):
    for subtable in lookup.SubTable:
        if subtable.LookupType == 4:
            for first_glyph, ligatures in subtable.ligatures.items():
                for lig in ligatures:
                    if lig.LigGlyph == 'glyph00492':
                        print(f"Found glyph00492 in Lookup {idx} (LigatureSubst): {[first_glyph] + lig.Component}")
        elif subtable.LookupType == 1:
            for k, v in subtable.mapping.items():
                if v == 'glyph00492':
                    print(f"Found glyph00492 in Lookup {idx} (SingleSubst): {k} -> {v}")
                if k == 'glyph00492':
                    print(f"Found glyph00492 as key in SingleSubst: {k} -> {v}")

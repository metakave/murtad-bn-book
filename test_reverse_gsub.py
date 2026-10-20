import fitz
from fontTools.ttLib import TTFont
import io

doc = fitz.open("Murtad-V1-27-03-2022.pdf")
fbytes = doc.extract_font(27)
font = TTFont(io.BytesIO(fbytes[3]))
glyphs = font.getGlyphOrder()

# Let's see if we can trace ligatures from GSUB
gsub = font['GSUB'].table
lookup_list = gsub.LookupList.Lookup

# Build a map from output glyph -> input glyphs
ligature_map = {} # target_glyph -> [input_glyphs]

for lookup in lookup_list:
    for subtable in lookup.SubTable:
        if subtable.LookupType == 4: # LigatureSubst
            for first_glyph, ligatures in subtable.ligatures.items():
                for lig in ligatures:
                    target = lig.LigGlyph
                    components = [first_glyph] + lig.Component
                    ligature_map[target] = components
        elif subtable.LookupType == 1: # SingleSubst
            # mapping from one glyph to another
            for inp, out in subtable.mapping.items():
                pass

print(f"Total ligatures mapped via GSUB: {len(ligature_map)}")
sample_ligs = list(ligature_map.items())[:15]
for target, comp in sample_ligs:
    print(f"{target} -> {comp}")

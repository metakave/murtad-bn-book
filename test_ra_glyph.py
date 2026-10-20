import fitz
from fontTools.ttLib import TTFont
import io

doc = fitz.open("Murtad-V1-27-03-2022.pdf")
fbytes = doc.extract_font(27)
font = TTFont(io.BytesIO(fbytes[3]))
glyphs = font.getGlyphOrder()

# Word: হত্যাব়
# Let's inspect the glyph names of this line:
# আল কুরআনের আলোকে মুরতাদ হত্যার অবৈধতা
page = doc[6]
data = doc.xref_stream(page.get_contents()[0]).decode("latin1", errors="ignore")
for line in data.split("\n"):
    if "<0009002F>" in line: # start of header
        hex_tokens = re.findall(r'<([0-9a-fA-F]+)>', line)
        for h in hex_tokens:
            for i in range(0, len(h), 4):
                cid = int(h[i:i+4], 16)
                print(f"0x{cid:04X} -> {glyphs[cid]}")
        break

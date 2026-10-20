import fitz
from fontTools.ttLib import TTFont
import io

doc = fitz.open("Murtad-V1-27-03-2022.pdf")
# Page 2:
# In PyMuPDF:
# আল কুরআনের আনলোনক
# মুরতোদ
# হতযোর
# অবৈধতো
# শওকত জোওহোর
# সোদদক মমোহোম্মদ আলম

# Let's inspect the stream of page 2 (index 1)
p2 = doc[1]
for s in p2.get_contents():
    raw = doc.xref_stream(s).decode("latin1", errors="ignore")
    for l in raw.split("\n"):
        if "Tj" in l or "TJ" in l:
            print(l[:100])

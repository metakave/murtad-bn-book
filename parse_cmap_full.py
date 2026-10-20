import fitz
import re

doc = fitz.open("Murtad-V1-27-03-2022.pdf")
cmap_data = doc.xref_stream(2235).decode("latin1", errors="ignore")

def parse_cmap(data):
    mapping = {}
    # bfchar
    for match in re.finditer(r'<([0-9a-fA-F]+)>\s+<([0-9a-fA-F]+)>', data):
        src = int(match.group(1), 16)
        dst_hex = match.group(2)
        chars = "".join(chr(int(dst_hex[i:i+4], 16)) for i in range(0, len(dst_hex), 4))
        mapping[src] = chars
    
    # bfrange with list: <start> <end> [ <dst1> <dst2> ... ]
    for match in re.finditer(r'<([0-9a-fA-F]+)>\s+<([0-9a-fA-F]+)>\s+\[([^\]]+)\]', data):
        start = int(match.group(1), 16)
        end = int(match.group(2), 16)
        dsts = re.findall(r'<([0-9a-fA-F]+)>', match.group(3))
        for i, d in enumerate(dsts):
            chars = "".join(chr(int(d[j:j+4], 16)) for j in range(0, len(d), 4))
            mapping[start + i] = chars

    # bfrange sequential: <start> <end> <dst_start>
    # Note: dst_start might be 4 hex chars, e.g. <0985>
    for match in re.finditer(r'<([0-9a-fA-F]+)>\s+<([0-9a-fA-F]+)>\s+<([0-9a-fA-F]{4})>', data):
        start = int(match.group(1), 16)
        end = int(match.group(2), 16)
        dst_val = int(match.group(3), 16)
        for i in range(end - start + 1):
            mapping[start + i] = chr(dst_val + i)
            
    return mapping

m = parse_cmap(cmap_data)
# Let's inspect what PyMuPDF extracts for page 7 line 1
p7 = doc[6]
text = p7.get_text("text")
first_few = text.split("\n")[1:8]
for l in first_few:
    print(repr(l))


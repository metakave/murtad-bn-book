import fitz
import re

doc = fitz.open("Murtad-V1-27-03-2022.pdf")
cmap_data = doc.xref_stream(2235).decode("latin1", errors="ignore")

bfchars = re.findall(r'<([0-9a-fA-F]+)>\s+<([0-9a-fA-F]+)>', cmap_data)
print(f"Found {len(bfchars)} bfchar mappings")
mapping = {}
for src, dst in bfchars:
    mapping[int(src, 16)] = dst

for idx in [0x2B, 0x26F, 0xB2, 0x124, 0xEE, 0x14, 0x1EC, 0x1A0, 0x208, 0x16D]:
    dst = mapping.get(idx)
    if dst:
        chars = "".join(chr(int(dst[i:i+4], 16)) for i in range(0, len(dst), 4))
        print(f"0x{idx:04X} -> {dst} -> {chars}")
    else:
        print(f"0x{idx:04X} -> NOT IN BFCHAR (might be in bfrange)")

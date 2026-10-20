import fitz
import re

doc = fitz.open("Murtad-V1-27-03-2022.pdf")
cmap_data = doc.xref_stream(2235).decode("latin1", errors="ignore")

def parse_adobe_cmap(cmap_str):
    mapping = {}
    
    # Process line by line or block by block
    # bfchar
    bfchar_blocks = re.findall(r'beginbfchar(.*?)endbfchar', cmap_str, re.DOTALL)
    for block in bfchar_blocks:
        for match in re.finditer(r'<([0-9a-fA-F]+)>\s+<([0-9a-fA-F]+)>', block):
            src = int(match.group(1), 16)
            dst_hex = match.group(2)
            chars = "".join(chr(int(dst_hex[i:i+4], 16)) for i in range(0, len(dst_hex), 4))
            mapping[src] = chars

    # bfrange
    bfrange_blocks = re.findall(r'beginbfrange(.*?)endbfrange', cmap_str, re.DOTALL)
    for block in bfrange_blocks:
        # Check for array syntax: <start> <end> [ <dst> <dst> ... ]
        for line in block.strip().split("\n"):
            line = line.strip()
            if not line:
                continue
            m_arr = re.match(r'<([0-9a-fA-F]+)>\s+<([0-9a-fA-F]+)>\s+\[(.*)\]', line)
            if m_arr:
                start = int(m_arr.group(1), 16)
                end = int(m_arr.group(2), 16)
                dsts = re.findall(r'<([0-9a-fA-F]+)>', m_arr.group(3))
                for idx, d in enumerate(dsts):
                    chars = "".join(chr(int(d[i:i+4], 16)) for i in range(0, len(d), 4))
                    mapping[start + idx] = chars
                continue
            
            # Check for range syntax: <start> <end> <dst_start>
            m_rng = re.match(r'<([0-9a-fA-F]+)>\s+<([0-9a-fA-F]+)>\s+<([0-9a-fA-F]+)>', line)
            if m_rng:
                start = int(m_rng.group(1), 16)
                end = int(m_rng.group(2), 16)
                d_hex = m_rng.group(3)
                # If d_hex is 4 hex chars
                if len(d_hex) == 4:
                    base = int(d_hex, 16)
                    for idx in range(end - start + 1):
                        mapping[start + idx] = chr(base + idx)
                else:
                    # Multi-char base
                    base_int = int(d_hex, 16)
                    for idx in range(end - start + 1):
                        # Format back
                        val = hex(base_int + idx)[2:].zfill(len(d_hex))
                        chars = "".join(chr(int(val[i:i+4], 16)) for i in range(0, len(val), 4))
                        mapping[start + idx] = chars
    return mapping

m = parse_adobe_cmap(cmap_data)
print(f"Total CMap entries parsed: {len(m)}")

# Let's inspect some of these entries
for cid in [0x09, 0x14, 0x23, 0x25, 0x26, 0x27, 0x2C, 0x2E, 0x2F, 0x36, 0x37, 0x39, 0x3D]:
    res = m.get(cid, "NONE")
    print(f"CID 0x{cid:04X} -> {repr(res)}")


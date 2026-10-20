import fitz

doc = fitz.open('Murtad-V1-27-03-2022.pdf')
page = doc[6] # page 7
stream = page.get_contents()
for s in stream:
    raw = doc.xref_stream(s).decode('latin1', errors='ignore')
    # find lines with Tj or TJ
    lines = raw.split('
')
    for l in lines:
        if 'Tj' in l or 'TJ' in l:
            if 'Noto' in l or '(' in l or '<' in l:
                print(l[:100])

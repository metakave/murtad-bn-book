
import fitz
doc = fitz.open('Murtad-V1-27-03-2022.pdf')
page = doc[6] # page 7
text = page.get_text('text')
line = text.split('
')[2] # first line after title
print('Raw line:', repr(line))
for ch in line[:30]:
    print(f'{ch} (U+{ord(ch):04X})', end=' ')
print()

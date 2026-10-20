import fitz

doc = fitz.open("Murtad-V1-27-03-2022.pdf")
toc_word = "ভূমিকা" # from doc[4]
body_word = doc[6].get_text("text").split("\n")[1].strip() # "ভূমিকা"
print("TOC word bytes:", [hex(ord(c)) for c in toc_word])
print("Body word bytes:", [hex(ord(c)) for c in body_word])
print("Are they equal?", toc_word == body_word)

# Let's check a sentence from body:
body_s = "আধুনেক সমনে মুসললমনদর"
print("Body sentence characters and codepoints:")
for c in body_s:
    print(f"{c} (U+{ord(c):04X})", end=" ")
print()

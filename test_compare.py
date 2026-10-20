import fitz

doc = fitz.open("Murtad-V1-27-03-2022.pdf")
print("Page 5 (TOC):")
for line in doc[4].get_text("text").split("\n")[:10]:
    if line.strip():
        print("TOC LINE:", line)

print("\nPage 7 (Body):")
for line in doc[6].get_text("text").split("\n")[:10]:
    if line.strip():
        print("BODY LINE:", line)

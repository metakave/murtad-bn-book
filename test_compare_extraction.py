import fitz

doc = fitz.open("Murtad-V1-27-03-2022.pdf")

# Standard extraction
p7_std = doc[6].get_text("text")

print("Standard extraction page 7:")
for l in p7_std.split("\n")[:15]:
    if l.strip():
        print(l.strip())

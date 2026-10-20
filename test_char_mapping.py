import fitz

doc = fitz.open("Murtad-V1-27-03-2022.pdf")
# Let's take page 5 (TOC) which has PERFECT text, and find corresponding pages
# Page 5 has:
# ভূমিকা ... 7
# এক নজরে মূল প্রতিপাদ্য ... 13
# প্রাথমিক কথা ... 16
# রাসূলের দায়িত্ব ও ধর্মীয় স্বাধীনতা ... 19

# Now let's print PyMuPDF's raw string for page 7 vs intended Bengali
raw_p7 = doc[6].get_text("text")
print("Raw PyMuPDF page 7 snippet:")
print(raw_p7[:300])

import unicodedata

# From the decoded string: "মুরত্যদ"
akar_suspect = "মুরত্যদ"[4]
print("Suspect char:", repr(akar_suspect))
print("Codepoint:", hex(ord(akar_suspect)))
print("Name:", unicodedata.name(akar_suspect))

# What is standard Bengali aa-kar?
akar_std = "মুরতাদ"[4]
print("Standard aa-kar:", repr(akar_std))
print("Codepoint:", hex(ord(akar_std)))
print("Name:", unicodedata.name(akar_std))

# What is standard Bengali o-kar?
okar_std = "হলো"[2]
print("Standard o-kar:", repr(okar_std))
print("Codepoint:", hex(ord(okar_std)))
print("Name:", unicodedata.name(okar_std))


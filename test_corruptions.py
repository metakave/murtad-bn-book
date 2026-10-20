samples = [
    ("আনলোনক", "আলোকে"),
    ("মুরতোদ", "মুরতাদ"),
    ("হতযোর", "হত্যার"),
    ("উদোহরে", "উদাহরণ"),
    ("আইে", "আইন"),
    ("েে", "নয়"),
    ("দয", "যে"),
    ("সোনে", "সাথে"),
    ("ৈযোখযো", "ব্যাখ্যা"),
]

for c, i in samples:
    print(f"--- {c} -> {i} ---")
    print("Corrupt: ", [(ch, hex(ord(ch))) for ch in c])
    print("Intended:", [(ch, hex(ord(ch))) for ch in i])

import re

def fix_reph_and_rafala(text):
    # 1. C + VOWEL + ্ -> র্ + C + VOWEL
    text = re.sub(r'([\u0995-\u09B9\u09DC-\u09DF])([\u09BE-\u09CC])\u09CD', lambda m: 'র্' + m.group(1) + m.group(2), text)
    text = re.sub(r'([\u0995-\u09B9\u09DC-\u09DF])\u09CD([\u09BE-\u09CC])', lambda m: 'র্' + m.group(1) + m.group(2), text)
    
    # 2. Reph at end of word or before whitespace/punct:
    text = re.sub(r'([\u0995-\u09B9\u09DC-\u09DF])\u09CD(?=[ \t\n\r।,!?\(\)\"\']|$)', lambda m: 'র্' + m.group(1), text)
    
    # 3. Preposed rafala at start of word:
    text = re.sub(r'(^|[\s\(\"\'])র্([পসবভটডতদকগখয])', lambda m: m.group(1) + m.group(2) + '্' + 'র', text)
    text = re.sub(r'([আআইউএও])র্([পসবভটডতদকগখ])', lambda m: m.group(1) + m.group(2) + '্' + 'র', text)
    
    # Words
    text = text.replace('দে্শে', 'র্দেশে')
    text = text.replace('নিদশ্ন', 'নিদর্শন')
    text = text.replace('ধম্ত্যাগ', 'ধর্মত্যাগ')
    text = text.replace('ধম্নিন্দা', 'ধর্মনিন্দা')
    text = text.replace('সামন্জস্য', 'সামঞ্জস্য')
    
    return text

samples = [
    "সম্পকে্", "র্পচলিত", "সামন্জস্যপূণ্", "নিদে্শের", "ধম্ীয়", "ধম্ত্যাগ", "নিদশ্ন", "র্পভ্যব", "র্পধ্যন", "আর্গহ"
]
for s in samples:
    print(f"{s:15} -> {fix_reph_and_rafala(s)}")

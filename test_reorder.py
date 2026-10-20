import re

def fix_bengali_visual_order(text):
    # In visual order, pre-kar (ি = \u09BF, ে = \u09C7, ৈ = \u09C8) appears BEFORE the consonant/cluster.
    # In logical Unicode order, the consonant/cluster must be BEFORE the vowel sign.
    # A consonant cluster is: (Consonant + Halant)* + Consonant (+ Nuqta)?
    # Consonants in Bengali: \u0995-\u09B9, \u09CE, \u09DC-\u09DF
    # Pre-kar: [\u09BF\u09C7\u09C8]
    # Halant: \u09CD
    # Ra-fala / Ja-fala / etc.
    
    # Regex for a single consonant (including nuqta if any)
    C = r'(?:[\u0995-\u09B9\u09DC-\u09DF]\u09BC?)'
    # Consonant cluster: C (\u09CD C)*
    CLUSTER = rf'(?:{C}(?:\u09CD{C})*)'
    
    # 1. Pre-kar followed by cluster: (ি|ে|ৈ)(CLUSTER) -> (CLUSTER)\1
    # Example: ি ন -> ন ি (নি)
    pattern1 = rf'([\u09BF\u09C7\u09C8])({CLUSTER})'
    res = re.sub(pattern1, r'\2\1', text)
    
    # 2. Reph (র্ = \u09B0\u09CD): in visual order it might be placed after or before, let's test.
    return res

test_word = "আধুিনক"
print("Original:", test_word)
fixed = fix_bengali_visual_order(test_word)
print("Fixed:", fixed)
print("Codepoints:", [f"{c}({hex(ord(c))})" for c in fixed])
print("Is correct 'আধুনিক'?", fixed == "আধুনিক")

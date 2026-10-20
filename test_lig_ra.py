from build_perfect_extractor import load_font

info = load_font(27)
print("uni09B0 in lig_map:", info['lig_map'].get('uni09B0'))

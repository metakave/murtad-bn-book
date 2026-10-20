from parse_entire_book import load_font, resolve_glyph

info = load_font(27)
print("resolve_glyph(info, 'uni09BE'):", resolve_glyph(info, 'uni09BE'))
print("uni09BE in lig_map:", info['lig_map'].get('uni09BE'))
print("uni09BE in single_rev:", info['single_rev'].get('uni09BE'))
print("uni09BE in g_to_u:", repr(info['g_to_u'].get('uni09BE')))

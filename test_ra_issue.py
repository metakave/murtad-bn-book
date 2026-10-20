from build_perfect_extractor import load_font

info = load_font(27)
print("info['g_to_u']['uni09B0']:", repr(info['g_to_u'].get('uni09B0')))
print("In raw resolved: uni09B0 resolved to:", info['glyphs'][46])
# Let's see why ব় appeared!
# Where did 'ব়' come from in 'মুসিলমেদব়'?
tokens = ['uni09AE', 'uni09C1', 'uni09B8', 'glyph00492', 'uni09B2', 'uni09AE', 'uni09C7', 'uni09A6', 'uni09B0']
for t in tokens:
    from build_perfect_extractor import resolve_glyph
    print(t, "->", resolve_glyph(info, t))

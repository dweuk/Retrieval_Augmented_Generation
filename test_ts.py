import tree_sitter_languages
language = tree_sitter_languages.get_language("javascript")
try:
    q = language.query("(identifier) @id")
except Exception as e:
    import traceback
    traceback.print_exc()

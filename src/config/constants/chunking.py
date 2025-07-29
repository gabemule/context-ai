"""
Text Processing & Chunking Constants for Context-AI.

This module contains all constants related to text chunking, language processing,
file extensions, and context assembly.
"""

__all__ = [
    'DEFAULT_CHUNK_SIZE',
    'DEFAULT_CHUNK_OVERLAP',
    'DEFAULT_MIN_CHUNK_SIZE',
    'LANGUAGE_EXTENSIONS',
    'SUPPORTED_EXTENSIONS',
    'EXTENSION_TO_LANGUAGE',
    'LANGUAGE_SEPARATORS',
    'DEFAULT_MAX_CHUNKS',
    'DEFAULT_PRIORITIZE_CROSS_PROJECT',
    'DEFAULT_INCLUDE_METADATA',
    'GUIDELINES_LANGUAGES',
]

# Chunking defaults
DEFAULT_CHUNK_SIZE = 2000
DEFAULT_CHUNK_OVERLAP = 200
DEFAULT_MIN_CHUNK_SIZE = 50

# Context assembly defaults
DEFAULT_MAX_CHUNKS = 8
DEFAULT_PRIORITIZE_CROSS_PROJECT = True
DEFAULT_INCLUDE_METADATA = True

# Guidelines configuration
GUIDELINES_LANGUAGES = ["python", "javascript", "typescript"]  # Supported guideline languages

# Supported file extensions by language
LANGUAGE_EXTENSIONS = {
    "python": {".py", ".pyx", ".pyi", ".pyw"},
    "javascript": {".js", ".jsx", ".mjs", ".cjs"},
    "typescript": {".ts", ".tsx", ".d.ts", ".cts", ".mts"},
    "markdown": {".md", ".mdx", ".markdown"},
    "html": {".html", ".htm", ".xhtml"},
    "css": {".css", ".scss", ".sass", ".less"},
    "json": {".json"},
    "yaml": {".yaml", ".yml"},
    "go": {".go"},
    "rust": {".rs"},
    "java": {".java"},
    "cpp": {".cpp", ".cc", ".cxx", ".c++", ".c", ".h", ".hpp"},
    "vue": {".vue"},
    "svelte": {".svelte"},
    "astro": {".astro"},
    "twig": {".twig"},
    "sql": {".sql"},
    "graphql": {".graphql", ".gql"},
    "xml": {".xml"},
}

# All supported extensions (flattened from LANGUAGE_EXTENSIONS)
SUPPORTED_EXTENSIONS = set()
for extensions in LANGUAGE_EXTENSIONS.values():
    SUPPORTED_EXTENSIONS.update(extensions)

# Extension to language mapping (reverse lookup)
EXTENSION_TO_LANGUAGE = {}
for language, extensions in LANGUAGE_EXTENSIONS.items():
    for ext in extensions:
        EXTENSION_TO_LANGUAGE[ext] = language

# Language-specific text separators for chunking
LANGUAGE_SEPARATORS = {
    "python": [
        "\nclass ",
        "\ndef ",
        "\nfunction ",
        "\nexport ",
        "\nimport ",
        "\n\n",
        "\n",
        " ",
        "",
    ],
    "javascript": [
        "\nclass ",
        "\nfunction ",
        "\nexport ",
        "\nimport ",
        "\nconst ",
        "\nlet ",
        "\n\n",
        "\n",
        " ",
        "",
    ],
    "typescript": [
        "\ninterface ",
        "\ntype ",
        "\nclass ",
        "\nfunction ",
        "\nexport ",
        "\nimport ",
        "\n\n",
        "\n",
        " ",
        "",
    ],
    "html": ["\n<div", "\n<section", "\n<article", "\n<p", "\n\n", "\n", " ", ""],
    "markdown": ["\n# ", "\n## ", "\n### ", "\n#### ", "\n\n", "\n", " ", ""],
    "css": ["\n.", "\n#", "\n@media", "\n@import", "\n\n", "\n", " ", ""],
    "default": ["\n\n", "\n", " ", ""],
}

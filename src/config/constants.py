"""
Configuration constants for Context-AI.
"""

# Claude API Configuration
CLAUDE_MODELS = {
    "claude-3-sonnet": "claude-3-sonnet-20240229",
    "claude-3-haiku": "claude-3-haiku-20240307", 
    "claude-3-opus": "claude-3-opus-20240229",
    "claude-3-5-sonnet": "claude-3-5-sonnet-20241022",
    "claude-4": "claude-sonnet-4-20250514"
}
CLAUDE_DEFAULT_MODEL = "claude-4"
CLAUDE_MAX_TOKENS = 200000
CLAUDE_MAX_RETRIES = 3
CLAUDE_RETRY_DELAY = 1.0  # seconds
CLAUDE_TIMEOUT = 60.0     # seconds

# Dynamic token allocation
CLAUDE_CONTEXT_TOKEN_RATIO = 0.65  # Use 65% of total capacity for context
CLAUDE_RESPONSE_TOKEN_RATIO = 0.8  # Use 80% of remaining capacity for response
CLAUDE_MIN_RESPONSE_TOKENS = 4000  # Minimum response tokens
CLAUDE_MAX_RESPONSE_TOKENS = 12000  # Sanity cap for response tokens

# Chat history management
CHAT_HISTORY_TOKEN_RATIO = 0.3  # Use 30% of context for chat history
CHAT_MAX_HISTORY_TURNS = 10  # Maximum conversation turns to keep
CHAT_MIN_HISTORY_TURNS = 3   # Minimum turns to preserve when truncating
CHAT_SUMMARY_THRESHOLD = 5   # After N turns, start summarizing old history

# Supported file extensions by language
LANGUAGE_EXTENSIONS = {
    "python": {".py", ".pyx", ".pyi"},
    "javascript": {".js", ".jsx", ".mjs"},
    "typescript": {".ts", ".tsx"},
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
    "xml": {".xml"}
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

# Chunking defaults
DEFAULT_CHUNK_SIZE = 2000
DEFAULT_CHUNK_OVERLAP = 200
DEFAULT_MIN_CHUNK_SIZE = 50

# Query and search defaults
DEFAULT_QUERY_RESULTS = 100  # Raw results from vector database (doubled for better quality)
MAX_QUERY_RESULTS = 200     # Maximum allowed per query
DEFAULT_DISPLAY_RESULTS = 20  # Results shown to user (increased - only affects terminal display)
MAX_DISPLAY_RESULTS = 50    # Maximum results to display

# Performance optimization constants
ENABLE_TOKEN_CACHE = True  # Cache token calculations to avoid re-processing
TOKEN_CACHE_SIZE = 200  # Cache recent token calculations
ENABLE_CONTEXT_CACHE = True  # Cache context between chat turns
CONTEXT_CACHE_TTL = 300  # Context cache TTL in seconds

# Prompt configuration
PROMPT_MODE = "standard"  # Modes: "minimal", "standard", "comprehensive", "strict"
ENABLE_CROSS_PROJECT_PROMPTS = True   # Add cross-project analysis instructions
ENABLE_CODING_GUIDELINES = True       # Include coding guidelines in prompts (always when applicable)
GUIDELINES_AUTO_DETECT = True         # Automatically detect when to apply guidelines
GUIDELINES_LANGUAGES = ['javascript', 'typescript']  # Supported guideline languages

# Prompt mode descriptions - each mode builds upon the previous
PROMPT_MODES = {
    "minimal": "Basic context + question only. No additional instructions or analysis prompts. Fastest processing.",
    "standard": "Context + question + cross-project awareness when multiple projects detected. Includes coding guidelines when JS/TS detected.", 
    "comprehensive": "Full cross-project comparison analysis + coding guidelines + architectural insights. Best for complex queries.",
    "strict": "All features + enforced coding standards + detailed code review approach. Best for code generation tasks."
}

# Language-specific text separators for chunking
LANGUAGE_SEPARATORS = {
    "python": ["\nclass ", "\ndef ", "\nfunction ", "\nexport ", "\nimport ", "\n\n", "\n", " ", ""],
    "javascript": ["\nclass ", "\nfunction ", "\nexport ", "\nimport ", "\nconst ", "\nlet ", "\n\n", "\n", " ", ""],
    "typescript": ["\ninterface ", "\ntype ", "\nclass ", "\nfunction ", "\nexport ", "\nimport ", "\n\n", "\n", " ", ""],
    "html": ["\n<div", "\n<section", "\n<article", "\n<p", "\n\n", "\n", " ", ""],
    "markdown": ["\n# ", "\n## ", "\n### ", "\n#### ", "\n\n", "\n", " ", ""],
    "css": ["\n.", "\n#", "\n@media", "\n@import", "\n\n", "\n", " ", ""],
    "default": ["\n\n", "\n", " ", ""]
}

# Context assembly defaults
DEFAULT_MAX_CHUNKS = 8
DEFAULT_PRIORITIZE_CROSS_PROJECT = True
DEFAULT_INCLUDE_METADATA = True

# Storage defaults
DEFAULT_CONFIG_DIR = "~/.context-ai"
DEFAULT_MAX_EMBEDDINGS = 50
DEFAULT_CLEANUP_AFTER_DAYS = 30

# System prompt strategy
DEFAULT_SYSTEM_PROMPT_STRATEGY = "general_assistant_with_reusability_focus"

# Validation constants
MIN_CHUNK_SIZE_LIMIT = 10
MAX_CHUNK_SIZE_LIMIT = 10000
MAX_EMBEDDING_NAME_LENGTH = 100
BYTES_PER_MB = 1024 * 1024
CHARS_PER_TOKEN = 4

# Exit codes
EXIT_SUCCESS = 0
EXIT_ERROR = 1
EXIT_INTERRUPTED = 130

# File filtering constants
MAX_FILE_SIZE_MB = 10
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * BYTES_PER_MB

# Default ignore patterns for Context-AI
DEFAULT_IGNORE_PATTERNS = [
    # Version control
    '.git/',
    '.svn/',
    '.hg/',
    
    # Dependencies
    'node_modules/',
    '__pycache__/',
    '.venv/',
    'venv/',
    'env/',
    '.env/',
    'vendor/',
    
    # Build artifacts
    'dist/',
    'build/',
    'target/',
    'out/',
    '.next/',
    '.nuxt/',
    'coverage/',
    
    # IDE and editors
    '.vscode/',
    '.idea/',
    '*.swp',
    '*.swo',
    '*~',
    '.DS_Store',
    'Thumbs.db',
    
    # Logs and temporary files
    '*.log',
    '*.tmp',
    '*.temp',
    '.cache/',
    'tmp/',
    'temp/',
    
    # Compiled and minified files
    '*.min.js',
    '*.min.css',
    '*.bundle.js',
    '*.bundle.css',
    '*.map',
    
    # Environment and config
    '.env*',
    '*.key',
    '*.pem',
    '*.crt',
    
    # Large binary files
    '*.zip',
    '*.tar',
    '*.tar.gz',
    '*.rar',
    '*.7z',
    '*.exe',
    '*.dll',
    '*.so',
    '*.dylib',
    '*.bin',
    '*.img',
    '*.iso',
]

# Ignore file names
CONTEXTIGNORE_FILENAME = '.contextignore'
GITIGNORE_FILENAME = '.gitignore'

# Sample .contextignore content
SAMPLE_CONTEXTIGNORE_CONTENT = '''# Context-AI ignore patterns
# This file follows .gitignore syntax
# Lines starting with # are comments
# Use ! to negate patterns

# Dependencies and modules
node_modules/
__pycache__/
.venv/
vendor/

# Build artifacts  
dist/
build/
target/
*.min.js
*.bundle.*

# IDE and editor files
.vscode/
.idea/
*.swp
.DS_Store

# Logs and temporary files
*.log
.cache/
tmp/

# Environment files (may contain secrets)
.env*
*.key
*.pem

# Large binary files
*.zip
*.tar.gz
*.exe
*.dll
*.so

# Include important config files
!important-config.json
!docs/*.md
'''
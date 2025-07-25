"""
English programming synonyms and stop words for query expansion.
"""

# Stop words optimized for English programming queries
ENGLISH_STOP_WORDS = {
    # Articles (safe to remove)
    "a",
    "an",
    "the",
    # Common conjunctions (usually safe)
    "and",
    "but",  # "or" removed - important in programming
    # Prepositions (context dependent - being conservative)
    "of",
    "at",
    "by",
    "for",
    "from",
    "with",
    # "in", "on", "to" removed - important in programming
    # Pronouns (usually safe to remove)
    "he",
    "she",
    "it",
    "they",
    "we",
    "you",
    "i",
    # Common verbs (context dependent - being selective)
    "are",
    "was",
    "were",
    "been",
    "being",
    "have",
    "has",
    "had",
    # "is", "be" removed - can be important in programming
    # Common but usually unimportant words
    "this",
    "that",
    "these",
    "those",
    "some",
    "any",
    "all",
    "each",
    "every",
    "more",
    "most",
    "other",
    "such",
    "only",
    "own",
    "same",
    "so",
    "than",
    "too",
    "very",
    "just",
    "now",
    "then",
    "here",
    "there",
    "over",
    "under",
    "again",
    "further",
    "once",
    "also",
    "can",
    "could",
    "should",
    "would",
    "will",
    "shall",
}

# English programming keywords that should NEVER be stop words
ENGLISH_PROGRAMMING_KEYWORDS = {
    # Language keywords and important terms
    "as",
    "if",
    "do",
    "go",
    "or",
    "is",
    "in",
    "on",
    "at",
    "to",
    "be",
    "me",
    # Question words - crucial for programming queries
    "how",
    "what",
    "where",
    "when",
    "why",
    "which",
    "who",
    # Action words important in programming
    "get",
    "set",
    "put",
    "post",
    "use",
    "add",
    "new",
    "old",
    "run",
    "call",
    "make",
    "take",
    "give",
    "find",
    "show",
    "hide",
    # State/direction words important in programming
    "up",
    "down",
    "in",
    "out",
    "on",
    "off",
}

# Functions & Methods
FUNCTIONS_METHODS = {
    "function": [
        "method",
        "func",
        "procedure",
        "routine",
        "callable",
        "subroutine",
        "def",
        "lambda",
    ],
    "method": [
        "function",
        "func",
        "procedure",
        "routine",
        "member function",
        "class method",
    ],
    "callback": ["handler", "listener", "hook", "delegate", "event handler"],
    "hook": ["callback", "handler", "listener", "interceptor", "middleware"],
}

# Classes & Objects
CLASSES_OBJECTS = {
    "class": ["object", "type", "interface", "struct", "entity", "model", "prototype"],
    "object": ["instance", "class", "entity", "model", "item", "element"],
    "interface": ["contract", "protocol", "api", "specification", "abstract class"],
    "struct": ["structure", "record", "type", "class", "object"],
    "prototype": ["template", "blueprint", "pattern", "class"],
}

# Variables & Data
VARIABLES_DATA = {
    "variable": ["var", "field", "property", "attribute", "member", "data"],
    "property": [
        "attribute",
        "field",
        "member",
        "variable",
        "accessor",
        "getter",
        "setter",
    ],
    "field": ["property", "attribute", "member", "variable", "column"],
    "parameter": ["param", "argument", "arg", "input", "variable"],
    "argument": ["param", "parameter", "arg", "input", "value"],
}

# UI Components
UI_COMPONENTS = {
    "component": ["element", "widget", "control", "part", "module", "block"],
    "element": ["component", "widget", "control", "node", "item"],
    "widget": ["component", "element", "control", "ui component"],
    "button": ["btn", "click", "action", "trigger", "control"],
    "input": ["field", "textbox", "form control", "entry"],
    "form": ["form", "input", "dialog", "modal", "panel"],
}

# API & Services
API_SERVICES = {
    "api": ["endpoint", "service", "interface", "method", "route", "resource"],
    "endpoint": ["api", "route", "service", "url", "resource", "path"],
    "service": ["api", "endpoint", "provider", "client", "handler"],
    "route": ["endpoint", "path", "url", "mapping", "handler"],
    "request": ["req", "call", "fetch", "http", "ajax"],
    "response": ["res", "result", "return", "output", "data"],
}

# Error Handling
ERROR_HANDLING = {
    "error": ["exception", "bug", "issue", "problem", "fault", "failure"],
    "exception": ["error", "throw", "catch", "try", "handling"],
    "bug": ["error", "issue", "problem", "defect", "fault"],
    "validation": ["validate", "check", "verify", "sanitize", "rule"],
}

# Configuration & Settings
CONFIG_SETTINGS = {
    "config": ["configuration", "settings", "options", "params", "preferences"],
    "settings": ["config", "configuration", "options", "preferences", "params"],
    "options": ["config", "settings", "parameters", "choices", "flags"],
    "environment": ["env", "config", "setup", "deployment", "runtime"],
}

# Authentication & Security
AUTH_SECURITY = {
    "auth": ["authentication", "login", "security", "credentials", "authorization"],
    "authentication": ["auth", "login", "signin", "verification", "identity"],
    "login": ["signin", "auth", "authentication", "access", "credentials"],
    "token": ["jwt", "session", "auth", "credential", "key"],
    "permission": ["authorization", "access", "role", "privilege", "right"],
}

# Database & Storage
DATABASE_STORAGE = {
    "db": ["database", "storage", "persistence", "data", "repository"],
    "database": ["db", "storage", "datastore", "repository", "persistence"],
    "query": ["select", "search", "find", "filter", "sql"],
    "table": ["collection", "entity", "model", "schema", "relation"],
    "collection": ["table", "list", "array", "set", "group"],
    "repository": ["repo", "storage", "data layer", "dao", "service"],
}

# Testing
TESTING = {
    "test": ["spec", "unit test", "testing", "assertion", "mock"],
    "mock": ["stub", "fake", "spy", "test double", "simulate"],
    "assertion": ["expect", "should", "verify", "check", "test"],
}

# Architecture & Patterns
ARCHITECTURE_PATTERNS = {
    "pattern": ["design pattern", "architecture", "structure", "approach"],
    "architecture": ["structure", "design", "pattern", "framework", "system"],
    "framework": ["library", "toolkit", "platform", "stack", "foundation"],
    "library": ["lib", "framework", "package", "module", "dependency"],
    "module": ["package", "library", "component", "unit", "namespace"],
}

# Development & Process
DEVELOPMENT_PROCESS = {
    "deploy": ["deployment", "release", "publish", "ship", "deliver"],
    "build": ["compile", "bundle", "package", "generate", "create"],
    "debug": ["debugging", "troubleshoot", "diagnose", "trace", "inspect"],
    "refactor": ["refactoring", "restructure", "cleanup", "improve", "reorganize"],
}

# React/Frontend Specific
REACT_FRONTEND = {
    "state": ["data", "store", "model", "context", "props"],
    "props": ["properties", "attributes", "parameters", "data", "state"],
    "component": ["react component", "element", "widget", "view"],
    "hook": ["use hook", "react hook", "custom hook", "state hook"],
    "context": ["provider", "state", "global state", "shared state"],
}

# Node.js/Backend Specific
NODEJS_BACKEND = {
    "middleware": ["handler", "interceptor", "filter", "processor"],
    "router": ["routing", "routes", "handler", "controller"],
    "controller": ["handler", "router", "action", "endpoint"],
    "model": ["schema", "entity", "data model", "object"],
}

# Common Abbreviations
COMMON_ABBREVIATIONS = {
    "utils": ["utilities", "helpers", "tools", "common", "shared"],
    "helpers": ["utils", "utilities", "tools", "common", "shared"],
    "constants": ["const", "config", "static", "definitions", "enums"],
    "types": ["interfaces", "definitions", "declarations", "schemas"],
}

# Combine all categories
ENGLISH_SYNONYMS = {}
for category in [
    FUNCTIONS_METHODS,
    CLASSES_OBJECTS,
    VARIABLES_DATA,
    UI_COMPONENTS,
    API_SERVICES,
    ERROR_HANDLING,
    CONFIG_SETTINGS,
    AUTH_SECURITY,
    DATABASE_STORAGE,
    TESTING,
    ARCHITECTURE_PATTERNS,
    DEVELOPMENT_PROCESS,
    REACT_FRONTEND,
    NODEJS_BACKEND,
    COMMON_ABBREVIATIONS,
]:
    ENGLISH_SYNONYMS.update(category)

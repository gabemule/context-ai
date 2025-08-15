"""
Language Configuration Models for Context-AI.

Defines data structures for programming language configurations including
inheritance, validation, and merging logic. Provides type-safe, validated
models that support complex configuration scenarios.
"""

from typing import Dict, List, Optional, Set

from pydantic import BaseModel, Field, field_validator

__all__ = [
    "ChunkingPriority",
    "LanguageConfig",
    "ResolvedLanguageConfig",
    "GlobalSettings",
    "LanguagesConfig",
    "InheritanceResolver",
    "ConfigMerger",
    "LanguageValidator",
]


class ChunkingPriority:
    """Constants for chunking priority levels - avoiding magic strings."""

    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

    ALL = {HIGH, MEDIUM, LOW}

    @classmethod
    def is_valid(cls, priority: str) -> bool:
        """Validate chunking priority value."""
        return priority.lower() in cls.ALL


class LanguageValidator:
    """Single Responsibility: Validation logic for language configurations."""

    @staticmethod
    def validate_extensions(extensions: List[str]) -> List[str]:
        """Ensure extensions are properly formatted."""
        validated = []
        for ext in extensions:
            if not ext.startswith("."):
                ext = f".{ext}"
            validated.append(ext.lower())
        return validated

    @staticmethod
    def validate_priority(priority: str) -> str:
        """Validate and normalize chunking priority."""
        normalized = priority.lower()
        if not ChunkingPriority.is_valid(normalized):
            raise ValueError(
                f"chunking_priority must be one of: {', '.join(ChunkingPriority.ALL)}"
            )
        return normalized

    @staticmethod
    def validate_separators(separators: List[str]) -> List[str]:
        """Validate separator list is not empty and contains strings."""
        if not separators:
            raise ValueError("separators list cannot be empty")
        if not all(isinstance(sep, str) for sep in separators):
            raise ValueError("all separators must be strings")
        return separators


class ConfigMerger:
    """Single Responsibility: Configuration merging logic with Strategy Pattern."""

    @staticmethod
    def merge_extensions(
        base_extensions: List[str], current_extensions: List[str]
    ) -> List[str]:
        """Merge extensions: current overrides base completely."""
        return current_extensions if current_extensions else base_extensions

    @staticmethod
    def merge_separators(
        base_separators: List[str],
        current_separators: Optional[List[str]],
        additional_separators: Optional[List[str]] = None,
    ) -> List[str]:
        """Merge separators with precedence: additional > current > base."""
        if additional_separators:
            # Additional separators have highest priority
            return additional_separators + base_separators

        # If current separators are explicitly defined, use them; otherwise inherit base
        return current_separators if current_separators is not None else base_separators

    @staticmethod
    def merge_configs(
        base_config: "LanguageConfig", current_config: "LanguageConfig"
    ) -> Dict:
        """Merge two language configurations following inheritance rules."""
        merged_data = base_config.dict()
        current_data = current_config.dict(exclude={"extends"})

        # Update with current data first (priority override for simple fields)
        merged_data.update(current_data)

        # Apply specific merging strategies that override the simple update
        merged_data["extensions"] = ConfigMerger.merge_extensions(
            base_config.extensions, current_config.extensions
        )

        merged_data["separators"] = ConfigMerger.merge_separators(
            base_config.separators or [],
            current_config.separators,
            current_config.additional_separators,
        )

        # Clean up inheritance-specific fields
        merged_data.pop("extends", None)
        merged_data.pop("additional_separators", None)

        return merged_data


class InheritanceResolver:
    """Single Responsibility: Resolve inheritance chains with cycle detection."""

    def __init__(self, languages: Dict[str, "LanguageConfig"]):
        self.languages = languages
        self.resolved_cache: Dict[str, "ResolvedLanguageConfig"] = {}

    def resolve_language(
        self, name: str, visited: Optional[Set[str]] = None
    ) -> "ResolvedLanguageConfig":
        """Resolve inheritance for a specific language."""
        if visited is None:
            visited = set()

        # Check for circular inheritance
        if name in visited:
            cycle_path = " -> ".join(visited) + f" -> {name}"
            raise ValueError(f"Circular inheritance detected: {cycle_path}")

        # Return cached result if available
        if name in self.resolved_cache:
            return self.resolved_cache[name]

        # Validate language exists
        if name not in self.languages:
            raise ValueError(f"Language '{name}' not found (referenced in extends)")

        config = self.languages[name]

        if config.extends:
            # Resolve inheritance chain
            visited.add(name)
            base_config = self.resolve_language(config.extends, visited.copy())
            visited.remove(name)

            # Merge configurations
            merged_data = ConfigMerger.merge_configs(
                base_config.to_language_config(), config
            )
            resolved_config = ResolvedLanguageConfig(**merged_data)
        else:
            # No inheritance, direct conversion
            resolved_config = ResolvedLanguageConfig.from_language_config(config)

        # Cache result
        self.resolved_cache[name] = resolved_config
        return resolved_config

    def resolve_all(self) -> Dict[str, "ResolvedLanguageConfig"]:
        """Resolve inheritance for all languages."""
        resolved = {}
        for name in self.languages:
            resolved[name] = self.resolve_language(name)
        return resolved


class LanguageConfig(BaseModel):
    """
    Immutable configuration for a single programming language.
    Follows Single Responsibility Principle - only data representation.
    """

    name: str = Field(..., description="Display name of the language")
    extensions: List[str] = Field(..., description="File extensions for this language")
    separators: Optional[List[str]] = Field(
        None, description="Text separators for chunking"
    )
    chunking_priority: str = Field(
        ChunkingPriority.MEDIUM, description="Priority for chunking"
    )
    extends: Optional[str] = Field(
        None, description="Language to inherit configuration from"
    )
    additional_separators: Optional[List[str]] = Field(
        None, description="Additional separators to merge"
    )

    @field_validator("extensions")
    @classmethod
    def validate_extensions(cls, v):
        """Delegate validation to specialized validator."""
        return LanguageValidator.validate_extensions(v)

    @field_validator("chunking_priority")
    @classmethod
    def validate_priority(cls, v):
        """Delegate validation to specialized validator."""
        return LanguageValidator.validate_priority(v)

    @field_validator("separators")
    @classmethod
    def validate_separators(cls, v):
        """Delegate validation to specialized validator."""
        if v is None:
            return v  # Allow None for inheritance cases
        return LanguageValidator.validate_separators(v)

    class Config:
        """Pydantic configuration for immutability and JSON encoding."""

        frozen = True  # Immutable for better predictability
        json_encoders = {list: lambda v: v, str: lambda v: v}


class ResolvedLanguageConfig(BaseModel):
    """
    Resolved language configuration with inheritance flattened.
    No inheritance fields - pure resolved configuration.
    """

    name: str
    extensions: List[str]
    separators: List[str]
    chunking_priority: str

    @classmethod
    def from_language_config(cls, config: LanguageConfig) -> "ResolvedLanguageConfig":
        """Create resolved config from regular config (no inheritance)."""
        if config.separators is None:
            raise ValueError(
                f"Language '{config.name}' has no separators and no inheritance"
            )

        return cls(
            name=config.name,
            extensions=config.extensions,
            separators=config.separators,
            chunking_priority=config.chunking_priority,
        )

    def to_language_config(self) -> LanguageConfig:
        """Convert back to LanguageConfig for merging operations."""
        return LanguageConfig(
            name=self.name,
            extensions=self.extensions,
            separators=self.separators,
            chunking_priority=self.chunking_priority,
        )

    class Config:
        """Pydantic configuration."""

        frozen = True  # Immutable resolved configuration
        json_encoders = {list: lambda v: v, str: lambda v: v}


class GlobalSettings(BaseModel):
    """Global settings with clear validation and defaults."""

    default_chunking_priority: str = Field(
        ChunkingPriority.LOW, description="Default priority for new languages"
    )
    auto_detect_languages: bool = Field(
        True, description="Enable automatic language detection"
    )
    cache_language_configs: bool = Field(
        True, description="Cache loaded configurations"
    )
    reload_on_change: bool = Field(True, description="Reload configs when files change")

    @field_validator("default_chunking_priority")
    @classmethod
    def validate_default_priority(cls, v):
        """Validate default chunking priority using centralized validator."""
        return LanguageValidator.validate_priority(v)

    class Config:
        """Pydantic configuration."""

        frozen = True  # Immutable settings


class LanguagesConfig(BaseModel):
    """
    Complete language configuration following Open/Closed Principle.
    Easy to extend with new functionality without modifying existing code.
    """

    languages: Dict[str, LanguageConfig] = Field(
        default_factory=dict, description="Language configurations"
    )
    settings: GlobalSettings = Field(
        default_factory=GlobalSettings, description="Global settings"
    )

    def resolve_inheritance(self) -> Dict[str, ResolvedLanguageConfig]:
        """
        Resolve inheritance using dedicated InheritanceResolver.
        Follows Single Responsibility and Dependency Inversion principles.
        """
        resolver = InheritanceResolver(self.languages)
        return resolver.resolve_all()

    def get_language_names(self) -> List[str]:
        """Get list of all language names."""
        return list(self.languages.keys())

    def has_language(self, name: str) -> bool:
        """Check if language exists in configuration."""
        return name in self.languages

    def add_language(self, name: str, config: LanguageConfig) -> "LanguagesConfig":
        """Add new language configuration (returns new instance for immutability)."""
        new_languages = self.languages.copy()
        new_languages[name] = config
        return LanguagesConfig(languages=new_languages, settings=self.settings)

    class Config:
        """Pydantic configuration."""

        json_encoders = {dict: lambda v: v, list: lambda v: v}

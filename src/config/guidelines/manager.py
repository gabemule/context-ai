"""
Guidelines Manager for Context-AI.

Handles loading, caching and serving of language-specific coding guidelines.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, List, Optional, Protocol

from utils.logging import get_logger

__all__ = [
    'GuidelinesManager',
    'get_guidelines_manager',
]


class FileOperations(Protocol):
    """Protocol for file operations."""
    
    def read_text(self, path: Path) -> str: ...
    def write_text(self, path: Path, content: str) -> None: ...
    def copy_file(self, source: Path, target: Path) -> None: ...
    def list_files(self, directory: Path, pattern: str) -> List[Path]: ...


class PathResolver:
    """Resolve and manage file system paths."""
    
    @staticmethod
    def get_config_directory() -> Path:
        """Get base configuration directory."""
        from config.constants import DEFAULT_CONFIG_DIR
        return Path(DEFAULT_CONFIG_DIR).expanduser()
    
    @staticmethod
    def get_guidelines_directory() -> Path:
        """Get guidelines directory with proper structure."""
        return PathResolver.get_config_directory() / "config" / "guidelines"
    
    @staticmethod
    def get_template_directory() -> Path:
        """Get template directory in source code."""
        return Path(__file__).parent
    
    @staticmethod
    def ensure_directory_exists(path: Path) -> None:
        """Ensure directory exists, creating if necessary."""
        path.mkdir(parents=True, exist_ok=True)


class FileSystemOperations:
    """File system operations with error handling."""
    
    def __init__(self, logger):
        self.logger = logger
    
    def read_text(self, path: Path) -> Optional[str]:
        """Read text file with error handling."""
        try:
            return path.read_text(encoding='utf-8')
        except Exception as e:
            self.logger.error(f"Failed to read {path}: {e}")
            return None
    
    def write_text(self, path: Path, content: str) -> bool:
        """Write text file with error handling."""
        try:
            path.write_text(content, encoding='utf-8')
            return True
        except Exception as e:
            self.logger.error(f"Failed to write {path}: {e}")
            return False
    
    def copy_file(self, source: Path, target: Path) -> bool:
        """Copy file with error handling."""
        try:
            import shutil
            shutil.copy2(source, target)
            self.logger.info(f"Copied: {source.name} -> {target}")
            return True
        except Exception as e:
            self.logger.warning(f"Failed to copy {source.name}: {e}")
            return False
    
    def list_files(self, directory: Path, pattern: str = "*.md") -> List[Path]:
        """List files in directory with pattern."""
        try:
            return list(directory.glob(pattern)) if directory.exists() else []
        except Exception as e:
            self.logger.error(f"Failed to list files in {directory}: {e}")
            return []


class TemplateManager:
    """Manage guideline templates."""
    
    def __init__(self, file_ops: FileSystemOperations):
        self.file_ops = file_ops
        self.logger = file_ops.logger
    
    def get_available_templates(self) -> List[Path]:
        """Get all available template files."""
        template_dir = PathResolver.get_template_directory()
        return self.file_ops.list_files(template_dir, "*.md")
    
    def copy_templates_to_user_directory(self) -> int:
        """Copy all templates to user directory. Returns count of copied files."""
        templates = self.get_available_templates()
        if not templates:
            self.logger.warning("No templates found to copy")
            return 0
        
        guidelines_dir = PathResolver.get_guidelines_directory()
        PathResolver.ensure_directory_exists(guidelines_dir)
        
        copied_count = 0
        for template_path in templates:
            target_path = guidelines_dir / template_path.name
            
            if not target_path.exists():
                if self.file_ops.copy_file(template_path, target_path):
                    copied_count += 1
        
        return copied_count
    
    def get_template_content(self, language: str) -> Optional[str]:
        """Get content of a specific template."""
        template_path = PathResolver.get_template_directory() / f"{language}.md"
        return self.file_ops.read_text(template_path)


class GuidelinesLoader:
    """Load and cache guidelines content."""
    
    def __init__(self, file_ops: FileSystemOperations):
        self.file_ops = file_ops
        self.logger = file_ops.logger
        self._cache: Dict[str, str] = {}
    
    def load_all_guidelines(self) -> Dict[str, str]:
        """Load all available guidelines into memory."""
        guidelines_dir = PathResolver.get_guidelines_directory()
        guideline_files = self.file_ops.list_files(guidelines_dir, "*.md")
        
        guidelines = {}
        for file_path in guideline_files:
            language = file_path.stem
            content = self.file_ops.read_text(file_path)
            
            if content:
                guidelines[language] = content.strip()
                self.logger.debug(f"Loaded guidelines: {language}")
        
        return guidelines
    
    def get_guideline(self, language: str) -> Optional[str]:
        """Get guideline for specific language from cache or disk."""
        if language not in self._cache:
            guidelines_dir = PathResolver.get_guidelines_directory()
            file_path = guidelines_dir / f"{language}.md"
            
            # Check if file exists before trying to read (avoid error logs for missing guidelines)
            if not file_path.exists():
                self.logger.debug(f"No guidelines found for language: {language}")
                return None
            
            content = self.file_ops.read_text(file_path)
            if content:
                self._cache[language] = content.strip()
        
        return self._cache.get(language)
    
    def invalidate_cache(self) -> None:
        """Clear the cache after updates."""
        self._cache.clear()
    
    def get_available_languages(self) -> List[str]:
        """Get list of all available guideline languages."""
        guidelines_dir = PathResolver.get_guidelines_directory()
        files = self.file_ops.list_files(guidelines_dir, "*.md")
        return sorted([f.stem for f in files])


class LanguageAliasManager:
    """Manage language aliases and mappings from languages.yaml."""
    
    def __init__(self):
        self._aliases_cache: Optional[Dict[str, List[str]]] = None
    
    def _get_aliases_from_languages_config(self) -> Dict[str, List[str]]:
        """Get language aliases dynamically from extensions in languages configuration."""
        if self._aliases_cache is not None:
            return self._aliases_cache
        
        try:
            from config.languages.manager import get_languages_manager
            languages_manager = get_languages_manager()
            
            # Get all language configurations
            all_languages = languages_manager.get_all_languages()
            
            # Build aliases dynamically from extensions
            aliases = {}
            for lang_name, lang_config in all_languages.items():
                aliases[lang_name] = []
                
                # Derive aliases from extensions automatically
                for ext in lang_config.extensions:
                    # Remove dot and use as potential alias
                    potential_alias = ext[1:] if ext.startswith('.') else ext
                    
                    # Common patterns for aliases
                    if potential_alias != lang_name and len(potential_alias) <= 4:
                        aliases[lang_name].append(potential_alias)
                
                # Remove duplicates and sort
                aliases[lang_name] = sorted(list(set(aliases[lang_name])))
            
            self._aliases_cache = aliases
            return aliases
            
        except Exception:
            # Minimal fallback if languages config completely unavailable
            return {}
    
    def get_canonical_name(self, language: str) -> str:
        """Get canonical language name from alias."""
        language = language.lower()
        aliases = self._get_aliases_from_languages_config()
        
        # Already canonical
        if language in aliases:
            return language
        
        # Find canonical name from alias
        for canonical, alias_list in aliases.items():
            if language in alias_list:
                return canonical
        
        return language
    
    def get_all_names_for_language(self, canonical_name: str) -> List[str]:
        """Get all names (canonical + aliases) for a language."""
        aliases = self._get_aliases_from_languages_config()
        if canonical_name not in aliases:
            return [canonical_name]
        
        return [canonical_name] + aliases[canonical_name]


class GuidelinesManager:
    """Central coordinator for guideline operations."""
    
    def __init__(self):
        self.logger = get_logger(__name__)
        self.file_ops = FileSystemOperations(self.logger)
        self.template_manager = TemplateManager(self.file_ops)
        self.loader = GuidelinesLoader(self.file_ops)
        self.alias_manager = LanguageAliasManager()
        self._ensure_system_ready()
    
    def _ensure_system_ready(self) -> None:
        """Initialize system with necessary templates."""
        copied_count = self.template_manager.copy_templates_to_user_directory()
        if copied_count > 0:
            self.logger.info(f"Initialized {copied_count} guideline templates")
    
    def get_guideline(self, language: str) -> Optional[str]:
        """Get guideline content for a specific language."""
        canonical = self.alias_manager.get_canonical_name(language)
        return self.loader.get_guideline(canonical)
    
    def get_available_languages(self) -> List[str]:
        """Get list of all available languages."""
        return self.loader.get_available_languages()
    
    def get_guidelines_for_languages(self, languages: List[str]) -> Optional[str]:
        """Get combined guidelines for multiple languages."""
        if not languages:
            return None
        
        unique_guidelines = []
        seen_content = set()
        
        for language in languages:
            content = self.get_guideline(language)
            if content and content not in seen_content:
                unique_guidelines.append(content)
                seen_content.add(content)
        
        if not unique_guidelines:
            return None
        
        if len(unique_guidelines) == 1:
            return unique_guidelines[0]
        
        return self._combine_multiple_guidelines(unique_guidelines)
    
    def save_guideline(self, language: str, content: str) -> bool:
        """Save guideline content to file."""
        canonical = self.alias_manager.get_canonical_name(language)
        guidelines_dir = PathResolver.get_guidelines_directory()
        file_path = guidelines_dir / f"{canonical}.md"
        
        success = self.file_ops.write_text(file_path, content)
        if success:
            self.loader.invalidate_cache()
            self.logger.info(f"Updated guidelines: {canonical}")
        
        return success
    
    def reset_to_default(self, language: str) -> bool:
        """Reset guideline to default template content."""
        canonical = self.alias_manager.get_canonical_name(language)
        default_content = self.template_manager.get_template_content(canonical)
        
        if not default_content:
            self.logger.error(f"No default template found for: {canonical}")
            return False
        
        return self.save_guideline(canonical, default_content)
    
    def reload(self) -> None:
        """Reload all guidelines from disk."""
        self.loader.invalidate_cache()
        self.logger.info("Guidelines cache reloaded")
    
    def _combine_multiple_guidelines(self, guidelines: List[str]) -> str:
        """Combine multiple guidelines with proper formatting."""
        header = "## 📋 Coding Guidelines for Multiple Languages\n\n"
        separator = "\n\n---\n\n"
        return header + separator.join(guidelines)
    
    def get_guideline_file_path(self, language: str) -> Path:
        """Get file path for guideline."""
        canonical = self.alias_manager.get_canonical_name(language)
        guidelines_dir = PathResolver.get_guidelines_directory()
        return guidelines_dir / f"{canonical}.md"


_guidelines_manager: Optional[GuidelinesManager] = None


def get_guidelines_manager() -> GuidelinesManager:
    """Get global GuidelinesManager instance."""
    global _guidelines_manager
    
    if _guidelines_manager is None:
        _guidelines_manager = GuidelinesManager()
    
    return _guidelines_manager


def reset_guidelines_manager() -> None:
    """Reset global instance (for testing)."""
    global _guidelines_manager
    _guidelines_manager = None

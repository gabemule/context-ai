"""
File-based prompt building system for Context-AI.

Loads prompts from configurable Markdown and YAML files instead of hardcoded templates.
Supports multiple prompt modes (minimal, standard, comprehensive, strict) with features
like security instructions, coding guidelines, and cross-project analysis.
"""

import os
import yaml
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

from utils.logging import get_logger


@dataclass
class PromptModeConfig:
    """Configuration for a prompt mode loaded from mode.yaml."""
    name: str
    description: str
    author: str
    version: str
    enabled: bool
    features: Dict[str, bool]


class YamlLoader:
    """Loads and parses YAML files."""
    
    def __init__(self):
        self.logger = get_logger(__name__)
    
    def load_yaml(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """Load and parse YAML file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            
            if not isinstance(data, dict):
                self.logger.error("Invalid YAML structure in %s: expected dict, got %s", 
                                file_path, type(data).__name__)
                return None
            
            return data
            
        except yaml.YAMLError as e:
            self.logger.error("Invalid YAML syntax in %s: %s", file_path, e)
            return None
        except Exception as e:
            self.logger.error("Failed to load YAML from %s: %s", file_path, e)
            return None


class ModeConfigValidator:
    """Validates mode configuration data."""
    
    def __init__(self):
        self.logger = get_logger(__name__)
    
    def validate_config_data(self, data: Dict[str, Any], config_file: Path) -> bool:
        """Validate the structure and content of mode configuration data."""
        # Validate required fields
        required_fields = ['name', 'description', 'author', 'version', 'enabled']
        for field in required_fields:
            if field not in data:
                self.logger.error("Missing required field '%s' in %s", field, config_file)
                return False
            
            # Validate field types
            if field == 'enabled' and not isinstance(data[field], bool):
                self.logger.error("Field 'enabled' must be boolean in %s", config_file)
                return False
            elif field != 'enabled' and not isinstance(data[field], str):
                self.logger.error("Field '%s' must be string in %s", field, config_file)
                return False
        
        # Validate features section
        features = data.get('features', {})
        if not isinstance(features, dict):
            self.logger.error("Features must be a dict in %s", config_file)
            return False
        
        # Validate supported features
        supported_features = {'security', 'cross_analysis', 'guidelines', 'debug'}
        for feature_name, feature_value in features.items():
            if feature_name not in supported_features:
                self.logger.warning("Unknown feature '%s' in %s", feature_name, config_file)
            
            if not isinstance(feature_value, bool):
                self.logger.error("Feature '%s' must be boolean in %s", feature_name, config_file)
                return False
        
        return True


class ModeFileValidator:
    """Validates mode directory files."""
    
    def __init__(self):
        self.logger = get_logger(__name__)
    
    def validate_required_files(self, mode_path: Path) -> bool:
        """Validate that all required files exist and are readable."""
        from config.constants import PROMPT_REQUIRED_FILES
        
        for required_file in PROMPT_REQUIRED_FILES:
            file_path = mode_path / required_file
            if not file_path.exists():
                self.logger.error("Required file '%s' not found in %s", required_file, mode_path)
                return False
            
            # Check if file is readable and not empty
            try:
                if file_path.stat().st_size == 0:
                    self.logger.error("Required file '%s' is empty in %s", required_file, mode_path)
                    return False
                
                # Test read permissions
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read(100)  # Read first 100 chars to test
                    if not content.strip():
                        self.logger.error("Required file '%s' contains only whitespace in %s", required_file, mode_path)
                        return False
                        
            except (OSError, IOError, UnicodeDecodeError) as e:
                self.logger.error("Cannot read required file '%s' in %s: %s", required_file, mode_path, e)
                return False
        
        return True


class PromptConfigLoader:
    """Orchestrates loading and validation of prompt mode configurations."""
    
    def __init__(self):
        self.logger = get_logger(__name__)
        self._config_cache: Dict[str, PromptModeConfig] = {}
        self.yaml_loader = YamlLoader()
        self.config_validator = ModeConfigValidator()
        self.file_validator = ModeFileValidator()
    
    def load_mode_config(self, mode_path: Path) -> Optional[PromptModeConfig]:
        """Load configuration for a specific mode from its mode.yaml file."""
        config_file = mode_path / "mode.yaml"
        
        if not config_file.exists():
            self.logger.debug("No mode.yaml found in %s", mode_path)
            return None
        
        # Check cache first
        cache_key = str(config_file)
        if cache_key in self._config_cache:
            return self._config_cache[cache_key]
        
        # Load YAML data
        data = self.yaml_loader.load_yaml(config_file)
        if not data:
            return None
        
        # Validate configuration data
        if not self.config_validator.validate_config_data(data, config_file):
            return None
        
        # Validate required files
        if not self.file_validator.validate_required_files(mode_path):
            return None
        
        # Create config object
        config = PromptModeConfig(
            name=data['name'],
            description=data['description'],
            author=data['author'],
            version=data['version'],
            enabled=bool(data['enabled']),
            features=data.get('features', {})
        )
        
        # Cache the config
        self._config_cache[cache_key] = config
        
        self.logger.debug("✅ Validated and loaded config for mode: %s v%s", config.name, config.version)
        return config


class PromptFileLoader:
    """Loads Markdown content files for prompt construction."""
    
    def __init__(self):
        self.logger = get_logger(__name__)
        self._file_cache: Dict[str, str] = {}
    
    def load_file(self, file_path: Path) -> Optional[str]:
        """Load content from a Markdown file with caching."""
        if not file_path.exists():
            return None
        
        # Check cache first
        cache_key = str(file_path)
        if cache_key in self._file_cache:
            return self._file_cache[cache_key]
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
            
            # Cache and return
            self._file_cache[cache_key] = content
            self.logger.debug("Loaded file: %s (%d chars)", file_path.name, len(content))
            return content
            
        except Exception as e:
            self.logger.error("Failed to load file %s: %s", file_path, e)
            return None
    
    def load_global_file(self, prompt_base_dir: Path, filename: str) -> Optional[str]:
        """Load a global instruction file."""
        return self.load_file(prompt_base_dir / filename)
    
    def load_mode_file(self, mode_dir: Path, filename: str) -> Optional[str]:
        """Load a mode-specific instruction file."""
        return self.load_file(mode_dir / filename)


class PromptBuilder:
    """
    File-based prompt builder that loads prompts from Markdown and YAML files.
    
    Maintains compatibility with the original PromptBuilder interface while
    providing a fully configurable system based on external files.
    """
    
    def __init__(self):
        self.logger = get_logger(__name__)
        self.config_loader = PromptConfigLoader()
        self.file_loader = PromptFileLoader()
        self._prompt_base_dir = self._get_prompt_directory()
    
    def _get_prompt_directory(self) -> Path:
        """Get the user's prompt configuration directory via StorageManager (centralized)."""
        from config.storage import get_storage_manager
        storage_manager = get_storage_manager()
        return storage_manager.path_manager.prompts_dir
    
    def _get_default_prompt_directory(self) -> Path:
        """Get the default prompt templates directory (src/config/samples/prompts/)."""
        # Get path to the samples/prompts/ directory in the source code
        current_dir = Path(__file__).parent.parent.parent.parent  # Go up to project root
        default_prompt_dir = current_dir / "src" / "config" / "samples" / "prompts"
        return default_prompt_dir
    
    def _ensure_user_prompt_config(self):
        """Ensure user prompt config exists, copy defaults if needed."""
        user_dir = self._prompt_base_dir
        default_dir = self._get_default_prompt_directory()
        
        if user_dir.exists():
            self.logger.debug("User prompt config found at: %s", user_dir)
            # Validate existing config
            self._validate_existing_config(user_dir, default_dir)
            return
        
        if not default_dir.exists():
            self.logger.error("Default prompt templates not found at: %s", default_dir)
            raise RuntimeError(f"Cannot initialize prompt system: default templates not found at {default_dir}")
        
        # Copy defaults to user directory
        self.logger.info("Creating user prompt config by copying defaults...")
        self.logger.info("From: %s", default_dir)
        self.logger.info("To: %s", user_dir)
        
        try:
            shutil.copytree(default_dir, user_dir)
            self.logger.info("✅ User prompt configuration created successfully")
            
        except Exception as e:
            self.logger.error("Failed to copy default prompt config: %s", e)
            raise RuntimeError(f"Cannot initialize prompt system: failed to copy defaults - {e}")
    
    def _validate_existing_config(self, config_dir: Path, default_dir: Path):
        """Validate existing prompt configuration and repair if needed."""
        try:
            from config.constants import PROMPT_GLOBAL_FILES
            
            # Check and repair global files
            for filename in PROMPT_GLOBAL_FILES:
                user_file = config_dir / filename
                if not user_file.exists() or user_file.stat().st_size == 0:
                    self.logger.warning("Missing or empty global file: %s", filename)
                    self._repair_missing_file(user_file, default_dir / filename)
            
            # Check for at least one valid mode
            valid_modes = 0
            for item in config_dir.iterdir():
                if item.is_dir() and not item.name.startswith('.'):
                    if self._validate_mode_directory(item, default_dir):
                        valid_modes += 1
            
            if valid_modes == 0:
                self.logger.error("No valid prompt modes found in %s", config_dir)
                raise RuntimeError("No valid prompt modes available")
            else:
                self.logger.debug("✅ Validated %d prompt modes", valid_modes)
                
        except Exception as e:
            self.logger.error("Error validating prompt config: %s", e)
            # Don't raise here, let the system continue with whatever is available
    
    def _validate_mode_directory(self, mode_dir: Path, default_dir: Path) -> bool:
        """Validate a single mode directory and repair if needed."""
        try:
            from config.constants import PROMPT_REQUIRED_FILES
            
            mode_name = mode_dir.name
            default_mode_dir = default_dir / mode_name
            
            # Check required files
            for filename in PROMPT_REQUIRED_FILES:
                user_file = mode_dir / filename
                if not user_file.exists() or user_file.stat().st_size == 0:
                    self.logger.warning("Missing %s in mode %s", filename, mode_name)
                    
                    # Try to repair from defaults
                    if default_mode_dir.exists():
                        default_file = default_mode_dir / filename
                        if default_file.exists():
                            self._repair_missing_file(user_file, default_file)
                        else:
                            self.logger.error("Cannot repair %s: default not found", filename)
                            return False
                    else:
                        self.logger.error("Cannot repair mode %s: default mode not found", mode_name)
                        return False
            
            # Try to load configuration to validate
            config = self.config_loader.load_mode_config(mode_dir)
            return config is not None and config.enabled
            
        except Exception as e:
            self.logger.error("Error validating mode directory %s: %s", mode_dir, e)
            return False
    
    def _repair_missing_file(self, target_file: Path, source_file: Path):
        """Repair a missing file by copying from source."""
        try:
            if not source_file.exists():
                self.logger.error("Cannot repair %s: source file not found at %s", target_file, source_file)
                return
            
            # Ensure target directory exists
            # Ensure target directory exists via file operations
            from utils.file_operations import get_file_operations
            file_ops = get_file_operations()
            file_ops.ensure_directory_exists(target_file.parent)
            
            # Copy from source
            shutil.copy2(source_file, target_file)
            self.logger.info("✅ Repaired missing file: %s", target_file.name)
            
        except Exception as e:
            self.logger.error("Failed to repair file %s: %s", target_file, e)
    
    def build_prompt(self, question: str, context: Optional[str] = None) -> str:
        """Build prompt based on configured mode using file-based system."""
        if not context:
            return question
        
        # Get prompt mode from user configuration
        from config.settings import get_settings_manager
        settings_manager = get_settings_manager()
        prompt_mode = settings_manager.get_prompt_mode()
        
        # Get mode configuration
        mode_config = self._get_mode_config(prompt_mode)
        if not mode_config:
            available_modes = self.get_available_modes()
            
            if not available_modes:
                error_msg = (
                    f"❌ No prompt modes available!\n"
                    f"   Please check your prompt configuration at: {self._prompt_base_dir}\n"
                    f"   Run 'context-ai --validate-config' to diagnose the issue."
                )
                self.logger.error(error_msg)
                raise RuntimeError("No valid prompt modes found. Configuration may be corrupted.")
            
            # Use standard mode as fallback if it exists
            if "standard" in available_modes:
                self.logger.warning(
                    "⚠️  Mode '%s' not found. Falling back to 'standard' mode.\n"
                    "   Available modes: %s\n"
                    "   You can change mode with: context-ai config set prompt_mode <mode>",
                    prompt_mode, ", ".join(available_modes)
                )
                final_prompt = self._build_file_based_prompt(question, context, "standard", self._get_mode_config("standard"))
                
                # 🆕 NOVO: Log prompt data for fallback mode
                self._log_prompt_if_available(final_prompt, question, context, "standard", self._get_mode_config("standard"))
                return final_prompt
            
            # No fallback available
            error_msg = (
                f"❌ Mode '{prompt_mode}' not found and no 'standard' fallback available!\n"
                f"   Available modes: {', '.join(available_modes)}\n"
                f"   Please set a valid mode with: context-ai config set prompt_mode <mode>\n"
                f"   Or fix your configuration at: {self._prompt_base_dir}"
            )
            self.logger.error(error_msg)
            raise ValueError(f"Invalid prompt mode '{prompt_mode}'. Available: {', '.join(available_modes)}")
        
        # Build prompt using file-based system
        final_prompt = self._build_file_based_prompt(question, context, prompt_mode, mode_config)
        
        # 🆕 NOVO: Log prompt data
        self._log_prompt_if_available(final_prompt, question, context, prompt_mode, mode_config)
        
        return final_prompt
    
    def _get_mode_config(self, mode: str) -> Optional[PromptModeConfig]:
        """Get configuration for the specified mode."""
        mode_dir = self._prompt_base_dir / mode
        if not mode_dir.exists():
            self.logger.debug("Mode directory not found: %s", mode_dir)
            return None
        
        config = self.config_loader.load_mode_config(mode_dir)
        if not config or not config.enabled:
            self.logger.debug("Mode %s is disabled or invalid", mode)
            return None
        
        return config
    
    def _build_file_based_prompt(self, question: str, context: str, mode: str, config: PromptModeConfig) -> str:
        """Build prompt using the file-based system following the defined order."""
        prompt_parts = []
        
        # Initialize language detection data for reuse
        self._last_detected_languages = None
        self._last_guidelines_content = None
        
        # 1. Global instructions (always)
        global_instructions = self.file_loader.load_global_file(self._prompt_base_dir, "global_instructions.md")
        if global_instructions:
            prompt_parts.append(global_instructions)
        
        # 2. Security instructions (if security: true)
        if config.features.get('security', False):
            security_instructions = self.file_loader.load_global_file(self._prompt_base_dir, "security_instructions.md")
            if security_instructions:
                prompt_parts.append(f"\n<security>\n{security_instructions}\n</security>")
        
        # 3. Mode core instructions (always)
        mode_dir = self._prompt_base_dir / mode
        core_instructions = self.file_loader.load_mode_file(mode_dir, "core_instructions.md")
        if core_instructions:
            prompt_parts.append(f"\n<core_instructions>\n{core_instructions}\n</core_instructions>")
        
        # 4. Cross-project analysis (if cross_analysis: true AND multi-project detected)
        if config.features.get('cross_analysis', False) and self._is_cross_project_context(context):
            cross_analysis = self.file_loader.load_mode_file(mode_dir, "cross_analysis.md")
            if cross_analysis:
                prompt_parts.append(f"\n<cross_analysis>\n{cross_analysis}\n</cross_analysis>")
        
        # 5. Coding guidelines (if guidelines: true) - Extract from XML tech_stack
        if config.features.get('guidelines', False):
            # Extract languages from XML context (more efficient than regex)
            detected_languages = self._extract_languages_from_xml_context(context)
            
            if detected_languages:
                self.logger.info(f"✅ Languages from tech_stack: {detected_languages}")
                
                # Get guidelines for detected languages
                try:
                    from config.guidelines import get_guidelines_manager
                    guidelines_manager = get_guidelines_manager()
                    guidelines_content = guidelines_manager.get_guidelines_for_languages(detected_languages)
                    
                    if guidelines_content:
                        prompt_parts.append(f"\n<coding_guidelines>\n{guidelines_content}\n</coding_guidelines>")
                        self.logger.debug(f"Applied guidelines for languages: {', '.join(detected_languages)}")
                        self._last_guidelines_content = guidelines_content
                    else:
                        self.logger.debug(f"No guidelines found for languages: {', '.join(detected_languages)}")
                
                except Exception as e:
                    self.logger.error("Failed to load guidelines: %s", e)
            
            # Store for logging reuse
            self._last_detected_languages = detected_languages
        
        # 6-9. Optional mode files
        from config.constants import PROMPT_OPTIONAL_FILES
        
        for filename in PROMPT_OPTIONAL_FILES:
            content = self.file_loader.load_mode_file(mode_dir, filename)
            if content:
                # Convert filename to section name (e.g., "error_handling.md" -> "error_handling")
                section_name = filename.replace('.md', '')
                prompt_parts.append(f"\n<{section_name}>\n{content}\n</{section_name}>")
        
        # Debug info (if debug: true)
        if config.features.get('debug', False):
            debug_info = self.file_loader.load_mode_file(mode_dir, "debug_info.md")
            if debug_info:
                prompt_parts.append(f"\n<debug>\n{debug_info}\n</debug>")
        
        # Build the final prompt structure
        base_prompt = "".join(prompt_parts)
        
        # Add context and question (context already wrapped by ContextFormatter)
        prompt = f"""{base_prompt}

{context}

<question>
{question}
</question>"""
        
        # Final instructions (if exists)
        final_instructions = self.file_loader.load_mode_file(mode_dir, "final_instructions.md")
        if final_instructions:
            prompt += f"\n\n{final_instructions}"
        
        return prompt
    
    def _is_cross_project_context(self, context: str) -> bool:
        """Check if context contains multiple projects using XML structure."""
        try:
            import xml.etree.ElementTree as ET
            
            # Parse XML context
            root = ET.fromstring(context)
            
            # Check if there are multiple projects in the overview
            projects_elem = root.find('.//projects')
            if projects_elem is not None:
                project_count = len(projects_elem.findall('project'))
                return project_count > 1
                
        except Exception as e:
            self.logger.debug(f"XML parsing failed for cross-project detection, using fallback: {e}")
            # Fallback to old method if XML parsing fails
            return "Cross-Project Analysis" in context and "Project Correlations" in context
        
        return False
    
    def _extract_languages_from_xml_context(self, context: str) -> List[str]:
        """Extract languages from XML context tech_stack."""
        try:
            import xml.etree.ElementTree as ET
            
            # Parse XML context
            root = ET.fromstring(context)
            
            # Extract technology_stack element
            tech_stack_elem = root.find('.//technology_stack')
            if tech_stack_elem is not None and tech_stack_elem.text:
                languages = [lang.strip() for lang in tech_stack_elem.text.split(',')]
                
                # Filter only programming languages with guidelines
                filtered_languages = self._filter_programming_languages(languages)
                
                self.logger.debug(f"🎯 XML parsing: found {len(languages)} languages, {len(filtered_languages)} with guidelines")
                return filtered_languages
                
        except Exception as e:
            self.logger.debug(f"XML parsing failed, trying fallback: {e}")
            # Fallback to regex if XML parsing fails
            return self._extract_languages_fallback(context)
        
        return []
    
    def _filter_programming_languages(self, languages: List[str]) -> List[str]:
        """Filter to only include programming languages with guidelines."""
        try:
            from config.guidelines import get_guidelines_manager
            guidelines_manager = get_guidelines_manager()
            available_guidelines = set(guidelines_manager.get_available_languages())
            
            filtered = [lang for lang in languages if lang in available_guidelines]
            
            if len(filtered) != len(languages):
                filtered_out = set(languages) - set(filtered)
                self.logger.debug(f"🚫 Filtered out languages without guidelines: {filtered_out}")
            
            return filtered
            
        except Exception as e:
            self.logger.error(f"Error filtering languages: {e}")
            return languages
    
    def _extract_languages_fallback(self, context: str) -> List[str]:
        """Fallback regex parsing if XML fails."""
        import re
        
        # Try to find technology_stack in text format
        pattern = r'<technology_stack>([^<]+)</technology_stack>'
        match = re.search(pattern, context)
        
        if match:
            languages = [lang.strip() for lang in match.group(1).split(',')]
            filtered_languages = self._filter_programming_languages(languages)
            
            self.logger.debug(f"📝 Fallback regex: found {len(languages)} languages, {len(filtered_languages)} with guidelines")
            return filtered_languages
        
        self.logger.debug("❌ No technology_stack found in context")
        return []
    
    def discover_available_modes(self) -> Dict[str, PromptModeConfig]:
        """Discover and load all available prompt modes from user config directory."""
        discovered_modes = {}
        
        if not self._prompt_base_dir.exists():
            self.logger.warning("Prompt config directory not found: %s", self._prompt_base_dir)
            return discovered_modes
        
        self.logger.debug("🔍 Discovering modes in: %s", self._prompt_base_dir)
        
        for item in self._prompt_base_dir.iterdir():
            if not item.is_dir() or item.name.startswith('.'):
                continue
                
            mode_name = item.name
            self.logger.debug("📁 Found mode directory: %s", mode_name)
            
            config = self.config_loader.load_mode_config(item)
            if not config:
                self.logger.warning("⚠️ Mode '%s' ignored: invalid or missing mode.yaml", mode_name)
                continue
                
            if not config.enabled:
                self.logger.debug("🚫 Mode '%s' disabled in config", mode_name)
                continue
            
            discovered_modes[mode_name] = config
            self.logger.debug("✅ Mode '%s' loaded: %s v%s", mode_name, config.name, config.version)
        
        self.logger.info("🎯 Discovered %d enabled modes: %s", 
                        len(discovered_modes), 
                        sorted(discovered_modes.keys()))
        
        return discovered_modes

    def get_available_modes(self) -> List[str]:
        """Get list of available prompt modes from user config directory."""
        discovered = self.discover_available_modes()
        return sorted(discovered.keys()) if discovered else ["minimal", "standard", "comprehensive", "strict"]
    
    def get_mode_info(self, mode: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific mode."""
        config = self._get_mode_config(mode)
        if not config:
            return None
        
        mode_dir = self._prompt_base_dir / mode
        
        # Check which optional files exist
        optional_files = {}
        for filename in ["cross_analysis.md", "final_instructions.md", "error_handling.md", 
                        "output_format.md", "validation_rules.md", "debug_info.md"]:
            optional_files[filename] = (mode_dir / filename).exists()
        
        return {
            "name": config.name,
            "description": config.description,
            "author": config.author,
            "version": config.version,
            "enabled": config.enabled,
            "features": config.features,
            "files": {
                "required": {
                    "mode.yaml": True,
                    "core_instructions.md": (mode_dir / "core_instructions.md").exists()
                },
                "optional": optional_files
            },
            "directory": str(mode_dir)
        }
    
    def get_all_modes_info(self) -> Dict[str, Dict[str, Any]]:
        """Get detailed information about all discovered modes."""
        discovered = self.discover_available_modes()
        all_info = {}
        
        for mode_name, config in discovered.items():
            all_info[mode_name] = self.get_mode_info(mode_name)
        
        return all_info
        
    def get_user_config_path(self) -> Path:
        """Get the path to user's prompt configuration directory."""
        return self._prompt_base_dir
    
    def _log_prompt_if_available(self, final_prompt: str, question: str, context: str, mode: str, config: PromptModeConfig):
        """Log prompt data if session logger is available."""
        if not hasattr(self, '_session_logger') or not self._session_logger:
            return
        
        try:
            # Count tokens (simple approximation)
            def count_tokens(text: str) -> int:
                return len(text.split()) + len(text) // 4
            
            # Get all sections for logging
            mode_dir = self._prompt_base_dir / mode
            
            # Load individual sections
            global_instructions = self.file_loader.load_global_file(self._prompt_base_dir, "global_instructions.md") or ""
            security_instructions = self.file_loader.load_global_file(self._prompt_base_dir, "security_instructions.md") if config.features.get('security', False) else ""
            core_instructions = self.file_loader.load_mode_file(mode_dir, "core_instructions.md") or ""
            cross_analysis = self.file_loader.load_mode_file(mode_dir, "cross_analysis.md") if config.features.get('cross_analysis', False) and self._is_cross_project_context(context) else ""
            final_instructions = self.file_loader.load_mode_file(mode_dir, "final_instructions.md") or ""
            
            # Get applicable guidelines (reuse already processed data)
            guidelines = getattr(self, '_last_guidelines_content', '') or ''
            
            # Prepare prompt data for logging
            prompt_data = {
                'final_prompt': final_prompt,
                'sections': {
                    'global_instructions': global_instructions,
                    'security_instructions': security_instructions,
                    'core_instructions': core_instructions,
                    'cross_analysis': cross_analysis,
                    'guidelines': guidelines,
                    'context': context,
                    'question': question,
                    'final_instructions': final_instructions
                },
                'mode_config': {
                    'name': config.name,
                    'description': config.description,
                    'version': config.version,
                    'features': config.features
                },
                'prompt_mode': mode,
                'token_count': count_tokens(final_prompt)
            }
            
            # Send to session logger
            self._session_logger.log_prompt_built(prompt_data)
            
        except Exception as e:
            self.logger.error("Failed to log prompt data: %s", e)


# Global prompt builder instance
_prompt_builder: Optional[PromptBuilder] = None


def get_prompt_builder() -> PromptBuilder:
    """Get global prompt builder instance."""
    global _prompt_builder
    if _prompt_builder is None:
        _prompt_builder = PromptBuilder()
    return _prompt_builder

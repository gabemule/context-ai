"""
Prompt building logic for Context-AI.

Handles construction of prompts based on different modes (minimal, standard,
comprehensive, strict) independent of the AI provider being used.
"""

from typing import Optional

from utils.logging import get_logger

# Global prompt components - avoid repetition across modes
GLOBAL_CODE_ATTRIBUTION = """
**Code Attribution**: When showing existing code examples from the codebase, always \
prefix each code block with a comment indicating the source file path \
(e.g., `// From: path/to/file.tsx`)."""


class PromptBuilder:
    """
    Builds prompts based on configured mode - from minimal to comprehensive.

    This class is AI provider agnostic and focuses purely on prompt construction
    logic based on the configured mode and available context.
    """

    def __init__(self):
        self.logger = get_logger(__name__)

    def build_prompt(self, question: str, context: Optional[str] = None) -> str:
        """Build prompt based on configured mode - from minimal to comprehensive."""
        if not context:
            return question

        from config.constants import PROMPT_MODE

        if PROMPT_MODE == "minimal":
            return self._build_minimal_prompt(question, context)
        elif PROMPT_MODE == "standard":
            return self._build_standard_prompt(question, context)
        elif PROMPT_MODE == "comprehensive":
            return self._build_comprehensive_prompt(question, context)
        elif PROMPT_MODE == "strict":
            return self._build_strict_prompt(question, context)
        else:
            # Default to standard
            return self._build_standard_prompt(question, context)

    def _build_minimal_prompt(self, question: str, context: str) -> str:
        """Build minimal prompt with no extra instructions - fastest processing."""
        return f"""Based on the following context from the codebase, please answer \
the question.
{GLOBAL_CODE_ATTRIBUTION}

## Context:
{context}

## Question:
{question}"""

    def _build_standard_prompt(self, question: str, context: str) -> str:
        """Build standard prompt with cross-project awareness and coding \
guidelines."""
        base_instructions = (
            "Based on the following context from the codebase, "
            "please answer the question."
        )

        # Add global code attribution instruction
        base_instructions += GLOBAL_CODE_ATTRIBUTION

        # Add cross-project hints for multi-project contexts
        is_cross_project = (
            "Cross-Project Analysis" in context and "Project Correlations" in context
        )
        if is_cross_project:
            base_instructions += """

Note: This context contains code from multiple projects - consider \
comparing approaches when relevant."""

        # Always include coding guidelines when applicable
        guidelines = self._get_applicable_guidelines(context, question)
        if guidelines:
            guidelines_section = f"""

{guidelines}

**When providing code examples or suggestions, please follow the above guidelines.**"""
            base_instructions += guidelines_section

        return f"""{base_instructions}

## Context:
{context}

## Question:
{question}"""

    def _build_comprehensive_prompt(self, question: str, context: str) -> str:
        """Build comprehensive prompt with full cross-project analysis and \
architectural insights."""
        base_instructions = (
            "Based on the following context from the codebase, "
            "please answer the question."
        )

        # Add global code attribution instruction with enhanced description
        base_instructions += (
            GLOBAL_CODE_ATTRIBUTION
            + " This helps users understand the context and location of the code."
        )

        # Check if this is cross-project context
        is_cross_project = (
            "Cross-Project Analysis" in context and "Project Correlations" in context
        )

        if is_cross_project:
            from config.constants import ENABLE_CROSS_PROJECT_PROMPTS

            if ENABLE_CROSS_PROJECT_PROMPTS:
                cross_project_instructions = """

**CROSS-PROJECT ANALYSIS**: This context contains code from multiple projects. Please:
- Compare implementations across different projects
- Highlight similarities and differences between approaches
- Identify reusable patterns or components
- Suggest opportunities for standardization or consistency improvements
- Point out which project has the most robust/complete implementation
- Consider architectural differences and their implications
- Recommend best practices based on the patterns observed"""

                base_instructions += cross_project_instructions

        # Always include coding guidelines when applicable
        guidelines = self._get_applicable_guidelines(context, question)
        if guidelines:
            guidelines_section = f"""

{guidelines}

**When providing code examples or suggestions, please follow the above \
guidelines and explain your architectural choices.**"""
            base_instructions += guidelines_section

        return f"""{base_instructions}

## Context:
{context}

## Question:
{question}

Please provide a comprehensive answer with architectural insights and \
best practices recommendations."""

    def _build_strict_prompt(self, question: str, context: str) -> str:
        """Build strict prompt with enforced coding standards and detailed \
code review approach."""
        base_instructions = (
            "Based on the following context from the codebase, please answer the "
            "question with a focus on code quality and best practices."
        )

        # Add global code attribution instruction with strict mode emphasis
        base_instructions += (
            GLOBAL_CODE_ATTRIBUTION
            + " This is essential for code review and understanding implementation context."
        )

        # Always include cross-project analysis when applicable
        is_cross_project = (
            "Cross-Project Analysis" in context and "Project Correlations" in context
        )
        if is_cross_project:
            cross_project_instructions = """

**CODE REVIEW APPROACH**: Analyze implementations across projects and provide \
detailed feedback on:
- Code quality and maintainability differences
- Performance implications of different approaches
- Security considerations
- Testing strategies
- Documentation quality"""
            base_instructions += cross_project_instructions

        # Always try to include guidelines with force=True
        guidelines = self._get_applicable_guidelines(context, question, force=True)
        if guidelines:
            guidelines_section = f"""

{guidelines}

**STRICT ENFORCEMENT**: All code suggestions must strictly adhere to the \
above guidelines. Review existing code for violations and suggest \
improvements."""
            base_instructions += guidelines_section

        return f"""{base_instructions}

## Context:
{context}

## Question:
{question}

Provide a detailed answer with code review insights, strict adherence to \
guidelines, and actionable improvement recommendations."""

    def _get_applicable_guidelines(
        self, context: str, question: str, force: bool = False
    ) -> Optional[str]:
        """Get applicable coding guidelines for the current context and question."""
        try:
            from config.constants import ENABLE_CODING_GUIDELINES

            if not ENABLE_CODING_GUIDELINES and not force:
                return None

            from config.guidelines.manager import get_guidelines_manager

            guidelines_manager = get_guidelines_manager()

            if force:
                # Force mode: try to detect languages and apply guidelines regardless
                languages = guidelines_manager.detect_languages_in_context(context)
                if languages:
                    return guidelines_manager.get_guidelines_for_languages(languages)
                return None
            else:
                return guidelines_manager.get_applicable_guidelines(context, question)

        except Exception as e:
            # Don't let guidelines errors break the main functionality
            self.logger.debug("Failed to load guidelines: %s", e)  # noqa: E501
            return None


# Global prompt builder instance
_prompt_builder: Optional[PromptBuilder] = None


def get_prompt_builder() -> PromptBuilder:
    """Get global prompt builder instance."""
    global _prompt_builder
    if _prompt_builder is None:
        _prompt_builder = PromptBuilder()
    return _prompt_builder

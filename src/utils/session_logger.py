"""
Session logging for Context-AI commands.

Manages detailed logging for individual command sessions including:
- Complete session logs
- Context sent to AI
- Responses received
- Session metadata
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

from utils.logging import get_logger


class CommandSession:
    """Manages logging for a single command session."""
    
    def __init__(self, command_name: str, args: Dict[str, Any]):
        self.command_name = command_name
        self.timestamp = datetime.now()
        self.session_id = self.timestamp.strftime(f"{command_name}_cmd_%Y-%m-%d_%H-%M-%S")
        
        # Create session directory
        from config.constants import DEFAULT_CONFIG_DIR
        config_dir = Path(DEFAULT_CONFIG_DIR).expanduser()
        self.session_dir = config_dir / "logs" / self.session_id
        self.session_dir.mkdir(parents=True, exist_ok=True)
        
        # Session files
        self.log_file = self.session_dir / "session.log"
        self.context_file = self.session_dir / "context_sent.md"
        self.response_file = self.session_dir / "response_received.md"
        self.metadata_file = self.session_dir / "metadata.json"
        
        # Initialize metadata
        self.metadata = {
            "command": command_name,
            "timestamp": self.timestamp.isoformat(),
            "args": args,
            "session_id": self.session_id
        }
        
        self.logger = get_logger(__name__)
        self._write_session_header()
        self.logger.info(f"📁 Session logs: {self.session_dir}")
    
    def save_context(self, context: str, question: str, metadata: Dict[str, Any], guidelines: Optional[str] = None) -> None:
        """Save the context sent to Claude with optional guidelines and structured format."""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Build structured content with XML-like tags for better organization
        content = [
            f"# Context Sent to Claude",
            "",
            "<context_session>",
            "<session_info>",
            f"**Timestamp:** {timestamp}",
            f"**Question:** {question}",
            f"**Token Count:** {metadata.get('token_count', 'unknown')} tokens",
            f"**Active Embeddings:** {', '.join(metadata.get('embeddings_used', []))}",
            "</session_info>",
            ""
        ]
        
        # Add guidelines section if provided
        if guidelines and guidelines.strip():
            content.extend([
                "<applied_guidelines>",
                f"**Guidelines Applied:**",
                "",
                guidelines,
                "</applied_guidelines>",
                ""
            ])
        
        # Add main context content
        content.extend([
            "<context_results>",
            context,
            "</context_results>",
            "</context_session>",
            "",
            "=" * 80,
            ""
        ])
        
        # For chat sessions, append to file. For ask sessions, overwrite
        if self.command_name == "chat":
            # Append mode for chat sessions
            with open(self.context_file, "a", encoding="utf-8") as f:
                if self.context_file.exists() and self.context_file.stat().st_size > 0:
                    f.write("\n\n")  # Add spacing between entries
                f.write("\n".join(content))
        else:
            # Overwrite mode for ask sessions
            self.context_file.write_text("\n".join(content), encoding="utf-8")
        
        self.metadata.update({
            "question": question,
            "context_stats": metadata
        })
        self.logger.info(f"💾 Context saved: {self.context_file}")
    
    def save_response(self, response: str, response_metadata: Dict[str, Any], question: Optional[str] = None) -> None:
        """Save AI provider response with structured format and question context."""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Extract metadata for structured format
        tokens_in = response_metadata.get('tokens_in', 0)
        tokens_out = response_metadata.get('tokens_out', 0)
        duration = response_metadata.get('duration_seconds', 0)
        provider = response_metadata.get('provider', 'AI Provider')
        model = response_metadata.get('model', 'Unknown Model')
        
        # Calculate additional metrics
        total_tokens = tokens_in + tokens_out
        tokens_per_sec = tokens_out / duration if duration > 0 else 0
        context_ratio = (tokens_out / tokens_in * 100) if tokens_in > 0 else 0
        
        # Build structured content with XML-like tags
        content = [
            f"# Response from AI Provider",
            "",
            "<response_session>",
            "<response_info>",
            f"**Timestamp:** {timestamp}",
        ]
        
        # Add question if provided
        if question and question.strip():
            content.append(f"**Question:** {question}")
            
        content.extend([
            f"**Tokens Used:** {tokens_in:,} in + {tokens_out:,} out",
            f"**Duration:** {duration:.1f}s",
        ])
        
        # Add provider and model info if available
        if provider != 'AI Provider':
            content.append(f"**Provider:** {provider}")
        if model != 'Unknown Model':
            content.append(f"**Model:** {model}")
            
        content.extend([
            "</response_info>",
            ""
        ])
        
        # Add performance metrics if meaningful
        if tokens_out > 0 and duration > 0:
            content.extend([
                "<response_metadata>",
                f"**Input Tokens:** {tokens_in:,}",
                f"**Output Tokens:** {tokens_out:,}",
                f"**Total Tokens:** {total_tokens:,}",
                f"**Response Speed:** {tokens_per_sec:.1f} tokens/sec",
                f"**Context Efficiency:** {tokens_in//1000}K context → {tokens_out//1000}K response ({context_ratio:.1f}% ratio)",
                "</response_metadata>",
                ""
            ])
        
        # Add main response content
        content.extend([
            "<api_response>",
            response,
            "</api_response>",
            "</response_session>",
            "",
            "=" * 80,
            ""
        ])
        
        # For chat sessions, append to file. For ask sessions, overwrite
        if self.command_name == "chat":
            # Append mode for chat sessions
            with open(self.response_file, "a", encoding="utf-8") as f:
                if self.response_file.exists() and self.response_file.stat().st_size > 0:
                    f.write("\n\n")  # Add spacing between entries
                f.write("\n".join(content))
        else:
            # Overwrite mode for ask sessions
            self.response_file.write_text("\n".join(content), encoding="utf-8")
        
        self.metadata.update({
            "response_stats": response_metadata
        })
        self.logger.info(f"💾 Response saved: {self.response_file}")
    
    def log_to_session(self, message: str, level: str = "INFO") -> None:
        """Log a message to the session file."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_line = f"[{timestamp}] - {level} - {message}\n"
        
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(log_line)
    
    def finalize(self) -> None:
        """Finalize the session and save metadata."""
        self.metadata["completed_at"] = datetime.now().isoformat()
        self.metadata["duration_seconds"] = (
            datetime.now() - self.timestamp
        ).total_seconds()
        
        self.metadata_file.write_text(
            json.dumps(self.metadata, indent=2, ensure_ascii=False),
            encoding="utf-8"
        )
        self.log_to_session(f"✅ Session completed: {self.session_id}")
        self.logger.info(f"✅ Session completed: {self.session_id}")
    
    def _write_session_header(self) -> None:
        """Write session header to log file."""
        header = [
            f"=== {self.command_name.upper()} COMMAND SESSION ===",
            f"Session ID: {self.session_id}",
            f"Timestamp: {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}",
            f"Command Args: {self.metadata['args']}",
            "",
        ]
        
        # Write to log file
        with open(self.log_file, "w", encoding="utf-8") as f:
            f.write("\n".join(header) + "\n\n")


# Global session instance
_current_session: Optional[CommandSession] = None


def start_command_session(command_name: str, args: Dict[str, Any]) -> CommandSession:
    """Start a new command session."""
    global _current_session
    _current_session = CommandSession(command_name, args)
    return _current_session


def get_current_session() -> Optional[CommandSession]:
    """Get the current command session."""
    return _current_session


def end_command_session() -> None:
    """End the current command session."""
    global _current_session
    if _current_session:
        _current_session.finalize()
        _current_session = None


def log_to_current_session(message: str, level: str = "INFO") -> None:
    """Log a message to the current session if one exists."""
    if _current_session:
        _current_session.log_to_session(message, level)

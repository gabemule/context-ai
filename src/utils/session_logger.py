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
    
    def save_context(self, context: str, question: str, metadata: Dict[str, Any]) -> None:
        """Save the context sent to Claude."""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        content = [
            f"# Context Sent to Claude",
            f"**Timestamp:** {timestamp}",
            f"**Question:** {question}",
            f"**Token Count:** {metadata.get('token_count', 'unknown')} tokens",
            f"**Active Embeddings:** {', '.join(metadata.get('embeddings_used', []))}",
            "",
            "---",
            "",
            context,
            "",
            "=" * 80,
            ""
        ]
        
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
    
    def save_response(self, response: str, response_metadata: Dict[str, Any]) -> None:
        """Save Claude's response."""
        content = [
            f"# Response from Claude",
            f"**Timestamp:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"**Tokens Used:** {response_metadata.get('tokens_in', 0)} in + {response_metadata.get('tokens_out', 0)} out",
            f"**Duration:** {response_metadata.get('duration_seconds', 0):.1f}s",
            "",
            "---",
            "",
            response,
            "",
            "=" * 80,
            ""
        ]
        
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

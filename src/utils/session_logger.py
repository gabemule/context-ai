"""
Session logging for Context-AI commands.

🆕 NEW SYSTEM: Raw, Complete, Future-Ready logging
Following SOLID principles with separated responsibilities.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

from utils.logging import get_logger


class SessionDataManager:
    """Manages session data structures (SRP)."""

    @staticmethod
    def create_chat_session_data(
        session_id: str, timestamp: str, command: str
    ) -> Dict[str, Any]:
        return {
            "session_id": session_id,
            "timestamp": timestamp,
            "command": command,
            "current_turn": 0,
            "total_turns": 0,
            "turns": [],
            "session_totals": {
                "total_tokens": 0,
                "total_prompt_tokens": 0,
                "total_response_tokens": 0,
            },
            "embeddings_used": [],
            "features_enabled": {
                "security": False,
                "cross_analysis": False,
                "guidelines": False,
                "debug": False,
            },
            "performance": {"total_execution_ms": 0},
            "status": "started",
            "error": None,
        }

    @staticmethod
    def create_ask_session_data(
        session_id: str, timestamp: str, command: str
    ) -> Dict[str, Any]:
        return {
            "session_id": session_id,
            "timestamp": timestamp,
            "command": command,
            "user_question": "",
            "prompt_mode": "unknown",
            "model": "unknown",
            "tokens": {"prompt": 0, "response": 0, "total": 0},
            "context": {
                "embeddings_used": [],
                "files_analyzed": 0,
                "similarity_matches": 0,
                "context_relevance": 0.0,
            },
            "prompt_sections": {
                "global_instructions": False,
                "security_instructions": False,
                "core_instructions": False,
                "cross_analysis": False,
                "guidelines": [],
                "final_instructions": False,
            },
            "features_enabled": {
                "security": False,
                "cross_analysis": False,
                "guidelines": False,
                "debug": False,
            },
            "performance": {
                "context_retrieval_ms": 0,
                "prompt_building_ms": 0,
                "claude_response_ms": 0,
                "total_execution_ms": 0,
            },
            "status": "started",
            "error": None,
        }

    @staticmethod
    def create_query_session_data(
        session_id: str, timestamp: str, command: str
    ) -> Dict[str, Any]:
        return {
            "session_id": session_id,
            "timestamp": timestamp,
            "command": command,
            "user_question": "",
            "query_format": "unknown",
            "results_count": 0,
            "result_file": "query_result.txt",
            "context": {
                "embeddings_used": [],
                "files_analyzed": 0,
                "similarity_matches": 0,
                "context_relevance": 0.0,
            },
            "performance": {"context_retrieval_ms": 0, "total_execution_ms": 0},
            "status": "started",
            "error": None,
        }


class FileManager:
    """Manages file operations (SRP)."""

    def __init__(self, session_dir: Path, is_chat: bool):
        self.session_dir = session_dir
        self.is_chat = is_chat
        self.prompt_file = None
        self.response_file = None
        self.logger = get_logger(__name__)

        if not is_chat:
            self.prompt_file = session_dir / "prompt_sent.txt"
            self.response_file = session_dir / "response_received.txt"

    def setup_turn_files(self, turn: int) -> None:
        """Setup files for chat turn."""
        if self.is_chat:
            self.prompt_file = self.session_dir / f"turn{turn}_prompt_sent.txt"
            self.response_file = self.session_dir / f"turn{turn}_response_received.txt"

    def save_prompt(self, prompt: str) -> None:
        """Save RAW prompt to file."""
        try:
            self.prompt_file.write_text(prompt, encoding="utf-8")
            self.logger.debug("💾 Prompt saved: %s", self.prompt_file.name)
        except Exception as e:
            self.logger.error("❌ Failed to save prompt: %s", e)

    def save_response(self, response: str) -> None:
        """Save RAW response to file."""
        try:
            self.response_file.write_text(response, encoding="utf-8")
            self.logger.debug("💾 Response saved: %s", self.response_file.name)
        except Exception as e:
            self.logger.error("❌ Failed to save response: %s", e)

    def save_json(self, filepath: Path, data: Dict[str, Any]) -> None:
        """Save JSON data to file."""
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            self.logger.debug("💾 JSON saved: %s", filepath.name)
        except Exception as e:
            self.logger.error("❌ Failed to save JSON: %s", e)

    def save_query_result(self, result: str) -> None:
        """Save query result to RAW file (SRP)."""
        try:
            query_file = self.session_dir / "query_result.txt"
            query_file.write_text(result, encoding="utf-8")
            self.logger.debug("💾 Query result saved: %s", query_file.name)
        except Exception as e:
            self.logger.error("❌ Failed to save query result: %s", e)


class ChatTurnManager:
    """Manages chat turns (SRP)."""

    def __init__(self):
        self.current_turn = 0
        self.logger = get_logger(__name__)

    def add_turn(self, session_data: Dict[str, Any], question: str) -> Dict[str, Any]:
        """Add new chat turn and return turn data."""
        self.current_turn += 1
        session_data["current_turn"] = self.current_turn

        turn_data = {
            "turn": self.current_turn,
            "timestamp": datetime.now().isoformat(),
            "user_question": question,
            "tokens": {"prompt": 0, "response": 0, "total": 0},
            "prompt_mode": "unknown",
            "model": "unknown",
            "prompt_sections": {
                "global_instructions": False,
                "security_instructions": False,
                "core_instructions": False,
                "cross_analysis": False,
                "guidelines": [],
                "final_instructions": False,
            },
            "performance": {"claude_response_ms": 0},
            "prompt_file": f"turn{self.current_turn}_prompt_sent.txt",
            "response_file": f"turn{self.current_turn}_response_received.txt",
        }

        session_data["turns"].append(turn_data)
        session_data["total_turns"] = len(session_data["turns"])

        self.logger.debug(
            "🔄 Added turn #%d: %s",
            self.current_turn,
            question[:50] + "..." if len(question) > 50 else question,
        )
        return turn_data


class CommandSession:
    """Main session coordinator (follows SRP and DIP)."""

    def __init__(self, command_name: str, args: Dict[str, Any]):
        self.command_name = command_name
        self.timestamp = datetime.now()
        self.session_id = self.timestamp.strftime(
            f"session_{command_name}_%Y-%m-%d_%H-%M-%S"
        )
        self.is_chat = command_name == "chat"

        # Create session directory
        from config.storage import get_storage_manager

        storage_manager = get_storage_manager()
        self.session_dir = storage_manager.path_manager.logs_dir / self.session_id
        self.session_dir.mkdir(parents=True, exist_ok=True)

        # Initialize components (Dependency Injection)
        self.file_manager = FileManager(self.session_dir, self.is_chat)
        self.chat_manager = ChatTurnManager() if self.is_chat else None

        # Initialize session data
        timestamp_iso = self.timestamp.isoformat()
        if self.is_chat:
            self.session_data = SessionDataManager.create_chat_session_data(
                self.session_id, timestamp_iso, command_name
            )
        elif command_name == "query":
            self.session_data = SessionDataManager.create_query_session_data(
                self.session_id, timestamp_iso, command_name
            )
        else:
            self.session_data = SessionDataManager.create_ask_session_data(
                self.session_id, timestamp_iso, command_name
            )

        # Metadata
        self.metadata = {
            "session_classification": {
                "task_type": "unknown",
                "domain": "unknown",
                "technology": "unknown",
                "complexity": "unknown",
                "user_intent": "unknown",
                "programming_language": "unknown",
            },
            "quality_metrics": {
                "context_relevance": 0.0,
                "response_completeness": 0.0,
                "user_satisfaction": None,
                "follow_up_needed": False,
            },
            "content_analysis": {
                "topics_covered": [],
                "code_examples_provided": 0,
                "external_links_referenced": 0,
                "files_mentioned": [],
            },
            "usage_patterns": {
                "time_of_day": self.timestamp.strftime("%H:%M"),
                "day_of_week": self.timestamp.strftime("%A").lower(),
                "prompt_mode_chosen": "unknown",
                "context_heavy": False,
            },
        }

        self.logger = get_logger(__name__)
        self.logger.info(f"📁 Session logs: {self.session_dir}")

    def add_chat_turn(self, question: str) -> None:
        """Add new chat turn."""
        if not self.is_chat:
            return

        turn_data = self.chat_manager.add_turn(self.session_data, question)
        self.file_manager.setup_turn_files(turn_data["turn"])

    def log_prompt_built(self, prompt_data: Dict[str, Any]) -> None:
        """Log prompt data from PromptBuilder."""
        token_count = prompt_data.get("token_count", 0)
        prompt_mode = prompt_data.get("prompt_mode", "unknown")

        if self.is_chat:
            # Update current turn data
            if self.session_data["turns"]:
                current_turn = self.session_data["turns"][-1]
                current_turn.update(
                    {
                        "prompt_mode": prompt_mode,
                        "tokens": {
                            "prompt": token_count,
                            "response": 0,
                            "total": token_count,
                        },
                    }
                )

            # Update features at session level
            mode_config = prompt_data.get("mode_config", {})
            features = mode_config.get("features", {})
            self.session_data["features_enabled"].update(features)
        else:
            # Original ask/query behavior
            self.session_data.update(
                {
                    "user_question": prompt_data.get("sections", {}).get(
                        "question", ""
                    ),
                    "prompt_mode": prompt_mode,
                    "tokens": {
                        "prompt": token_count,
                        "response": 0,
                        "total": token_count,
                    },
                }
            )

            # Update features
            mode_config = prompt_data.get("mode_config", {})
            features = mode_config.get("features", {})
            self.session_data["features_enabled"].update(features)

        # Save RAW prompt
        self.file_manager.save_prompt(prompt_data.get("final_prompt", ""))

        self.logger.debug(
            "🔍 Prompt logged: %s mode, %dK tokens", prompt_mode, token_count // 1000
        )

    def log_response_received(self, response: str) -> None:
        """Log raw response from Claude."""
        self.file_manager.save_response(response)
        self.logger.debug("📝 Response logged: %d chars", len(response))

    def log_query_result(
        self, result: str, question: str, format_type: str, results_count: int
    ) -> None:
        """Log query result and update session data (SRP)."""
        try:
            # Save RAW result to file
            self.file_manager.save_query_result(result)

            # Update session data
            self.session_data.update(
                {
                    "user_question": question,
                    "query_format": format_type,
                    "results_count": results_count,
                }
            )

            self.logger.debug(
                "🔍 Query result logged: %s format, %d results",
                format_type,
                results_count,
            )
        except Exception as e:
            self.logger.error("❌ Failed to log query result: %s", e)

    def save_context(
        self,
        context: str,
        question: str,
        metadata: Dict[str, Any],
        guidelines: Optional[str] = None,
    ) -> None:
        """Update session with context metadata."""
        try:
            if self.is_chat:
                self.session_data["embeddings_used"] = metadata.get(
                    "embeddings_used", []
                )
            else:
                self.session_data["context"]["embeddings_used"] = metadata.get(
                    "embeddings_used", []
                )
                self.session_data["context"]["files_analyzed"] = metadata.get(
                    "results_count", 0
                )
                self.session_data["context"]["similarity_matches"] = metadata.get(
                    "results_count", 0
                )

                if metadata.get("token_count", 0) > 0:
                    relevance = min(1.0, metadata.get("token_count", 0) / 50000)
                    self.session_data["context"]["context_relevance"] = round(
                        relevance, 2
                    )

                if not self.session_data.get("user_question"):
                    self.session_data["user_question"] = question

            self.logger.debug(
                "🔍 Context updated: %d embeddings",
                len(metadata.get("embeddings_used", [])),
            )
        except Exception as e:
            self.logger.error("❌ Failed to update context: %s", e)

    def finalize(self) -> None:
        """Finalize session and save all files."""
        try:
            completion_time = datetime.now()
            self.session_data["status"] = "completed"

            duration_seconds = (completion_time - self.timestamp).total_seconds()
            self.session_data["performance"]["total_execution_ms"] = int(
                duration_seconds * 1000
            )

            # Calculate final totals for chat sessions
            if self.is_chat and self.session_data["turns"]:
                total_prompt = sum(
                    turn["tokens"]["prompt"] for turn in self.session_data["turns"]
                )
                total_response = sum(
                    turn["tokens"]["response"] for turn in self.session_data["turns"]
                )

                self.session_data["session_totals"][
                    "total_prompt_tokens"
                ] = total_prompt
                self.session_data["session_totals"][
                    "total_response_tokens"
                ] = total_response
                self.session_data["session_totals"]["total_tokens"] = (
                    total_prompt + total_response
                )

            self.metadata["completed_at"] = completion_time.isoformat()
            self.metadata["duration_seconds"] = duration_seconds

            # Save files
            self.file_manager.save_json(
                self.session_dir / "session.json", self.session_data
            )
            self.file_manager.save_json(
                self.session_dir / "metadata.json", self.metadata
            )

            self.logger.info("✅ Session completed: %s", self.session_id)
        except Exception as e:
            self.logger.error("❌ Failed to finalize session: %s", e)
            self.session_data["status"] = "error"
            self.session_data["error"] = str(e)


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

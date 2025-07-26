"""
Progress tracking utilities for Context-AI.

Provides rich progress bars and status updates for long-running operations
like embedding generation and file processing.
"""

import time
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Dict, List

from rich.console import Console
from rich.panel import Panel
from rich.progress import (
    BarColumn,
    MofNCompleteColumn,
    Progress,
    SpinnerColumn,
    TaskProgressColumn,
    TextColumn,
    TimeElapsedColumn,
    TimeRemainingColumn,
)
from rich.table import Table

from config.constants import BYTES_PER_MB
from utils.logging import get_logger


class ProgressStats:
    """Statistics for progress tracking."""

    def __init__(self):
        self.start_time = time.time()
        self.files_processed = 0
        self.files_total = 0
        self.bytes_processed = 0
        self.bytes_total = 0
        self.chunks_created = 0
        self.errors_count = 0
        self.current_file = ""
        self.status = "Starting..."

    @property
    def elapsed_time(self) -> float:
        """Get elapsed time in seconds."""
        return time.time() - self.start_time

    @property
    def processing_rate(self) -> float:
        """Get files per second processing rate."""
        if self.elapsed_time > 0:
            return self.files_processed / self.elapsed_time
        return 0.0

    @property
    def completion_percentage(self) -> float:
        """Get completion percentage."""
        if self.files_total > 0:
            return (self.files_processed / self.files_total) * 100
        return 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert stats to dictionary."""
        return {
            "files_processed": self.files_processed,
            "files_total": self.files_total,
            "bytes_processed": self.bytes_processed,
            "bytes_total": self.bytes_total,
            "chunks_created": self.chunks_created,
            "errors_count": self.errors_count,
            "elapsed_time": self.elapsed_time,
            "processing_rate": self.processing_rate,
            "completion_percentage": self.completion_percentage,
            "current_file": self.current_file,
            "status": self.status,
        }


class EmbeddingProgressTracker:
    """
    Rich progress tracker for embedding generation.

    Provides fancy progress bars, file-by-file tracking,
    and real-time statistics for embedding operations.
    """

    def __init__(self, show_details: bool = True):
        """
        Initialize progress tracker.

        Args:
            show_details: Whether to show detailed file-by-file progress
        """
        self.logger = get_logger(__name__)
        self.show_details = show_details
        self.stats = ProgressStats()
        self.console = Console()
        self._progress = None
        self._main_task = None
        self._file_task = None

    def start_embedding_generation(
        self, files: List[Path], embedding_name: str
    ) -> None:
        """
        Start tracking embedding generation progress.

        Args:
            files: List of files to process
            embedding_name: Name of the embedding being created
        """
        self.stats.files_total = len(files)
        self.stats.bytes_total = sum(f.stat().st_size for f in files if f.exists())
        self.stats.status = f"Generating '{embedding_name}'"

        # Create progress display
        self._progress = Progress(
            SpinnerColumn(),
            TextColumn("[bold blue]{task.description}"),
            BarColumn(complete_style="green", finished_style="bold green"),
            MofNCompleteColumn(),
            TaskProgressColumn(),
            TimeElapsedColumn(),
            TimeRemainingColumn(),
            console=self.console,
            expand=True,
        )

        # Create main progress task
        self._main_task = self._progress.add_task(
            f"[bold green]Generating embeddings for '{embedding_name}'",
            total=self.stats.files_total,
        )

        # Show initial stats
        self._show_initial_stats(embedding_name, files)

        self.logger.info(f"Starting embedding generation for {len(files)} files")

    def update_file_progress(self, file_path: Path, chunks_created: int = 0) -> None:
        """
        Update progress for a single file.

        Args:
            file_path: Path to the file being processed
            chunks_created: Number of chunks created from this file
        """
        if not self._progress or self._main_task is None:
            return

        # Update stats
        self.stats.files_processed += 1
        self.stats.current_file = file_path.name
        self.stats.chunks_created += chunks_created

        if file_path.exists():
            self.stats.bytes_processed += file_path.stat().st_size

        # Update progress bar
        self._progress.update(
            self._main_task,
            advance=1,
            description=f"[bold green]Processing: [cyan]{file_path.name}[/cyan]",
        )

        # Show file completion message
        if chunks_created > 0:
            self.console.print(f"  ✅ {file_path.name} → {chunks_created} chunks")
        else:
            self.console.print(f"  ⏭️  {file_path.name} → skipped")

    def update_error(self, file_path: Path, error: str) -> None:
        """
        Update progress for a file error.

        Args:
            file_path: Path to the file that failed
            error: Error message
        """
        self.stats.errors_count += 1
        self.stats.files_processed += 1

        if self._progress and self._main_task is not None:
            self._progress.update(self._main_task, advance=1)

        self.console.print(f"  ❌ {file_path.name} → [red]{error}[/red]")
        self.logger.warning(f"Error processing {file_path}: {error}")

    def finish(self) -> Dict[str, Any]:
        """
        Finish progress tracking and show final statistics.

        Returns:
            Final statistics dictionary
        """
        if self._progress:
            self._progress.stop()

        final_stats = self.stats.to_dict()
        self._show_completion_stats()

        return final_stats

    def _show_initial_stats(self, embedding_name: str, files: List[Path]) -> None:
        """Show initial statistics before processing."""
        # Create stats table
        stats_table = Table(title=f"Embedding Generation: {embedding_name}")
        stats_table.add_column("Metric", style="cyan")
        stats_table.add_column("Value", style="bold white")

        stats_table.add_row("Total Files", str(len(files)))
        stats_table.add_row(
            "Total Size", f"{self.stats.bytes_total / BYTES_PER_MB:.1f} MB"
        )

        # Show file type breakdown
        extensions = {}
        for file_path in files:
            ext = file_path.suffix.lower()
            extensions[ext] = extensions.get(ext, 0) + 1

        ext_info = ", ".join(
            [f"{ext}: {count}" for ext, count in sorted(extensions.items())]
        )
        stats_table.add_row("File Types", ext_info)

        self.console.print(Panel(stats_table, expand=False))
        self.console.print()

    def _show_completion_stats(self) -> None:
        """Show completion statistics."""
        # Create completion stats table
        completion_table = Table(title="✅ Embedding Generation Complete")
        completion_table.add_column("Metric", style="cyan")
        completion_table.add_column("Value", style="bold green")

        completion_table.add_row("Files Processed", str(self.stats.files_processed))
        completion_table.add_row("Chunks Created", str(self.stats.chunks_created))
        completion_table.add_row(
            "Data Processed", f"{self.stats.bytes_processed / BYTES_PER_MB:.1f} MB"
        )
        completion_table.add_row("Time Elapsed", f"{self.stats.elapsed_time:.1f}s")
        completion_table.add_row(
            "Processing Rate", f"{self.stats.processing_rate:.1f} files/sec"
        )

        if self.stats.errors_count > 0:
            completion_table.add_row("Errors", f"[red]{self.stats.errors_count}[/red]")

        self.console.print()
        self.console.print(Panel(completion_table, expand=False))

        # Success message
        if self.stats.errors_count == 0:
            self.console.print(
                f"🎉 [bold green]Successfully created {self.stats.chunks_created} "
                f"chunks "
                f"from {self.stats.files_processed} files![/bold green]"
            )
        else:
            self.console.print(
                f"⚠️  [yellow]Completed with {self.stats.errors_count} errors. "
                f"Created {self.stats.chunks_created} chunks from "
                f"{self.stats.files_processed - self.stats.errors_count} "
                f"files.[/yellow]"
            )


class FileProcessingTracker:
    """
    Simple progress tracker for file processing operations.

    Lighter weight than EmbeddingProgressTracker for basic file operations.
    """

    def __init__(self):
        self.console = Console()
        self.logger = get_logger(__name__)

    @contextmanager
    def track_file_filtering(self, total_files: int):
        """
        Context manager for tracking file filtering progress.

        Args:
            total_files: Total number of files to filter
        """
        with Progress(
            SpinnerColumn(),
            TextColumn("[bold blue]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            MofNCompleteColumn(),
            console=self.console,
        ) as progress:

            task = progress.add_task("[cyan]Filtering files...", total=total_files)

            def update_progress(processed: int = 1):
                progress.update(task, advance=processed)

            yield update_progress

    def show_filtering_results(self, stats: Dict[str, int]) -> None:
        """
        Show file filtering results.

        Args:
            stats: Dictionary with filtering statistics
        """
        # Create results table
        results_table = Table(title="📁 File Filtering Results")
        results_table.add_column("Category", style="cyan")
        results_table.add_column("Count", style="bold white")
        results_table.add_column("Percentage", style="green")

        total = stats.get("total", 0)

        for category, count in stats.items():
            if category != "total" and count > 0:
                percentage = f"{(count / total) * 100:.1f}%" if total > 0 else "0%"

                # Color coding
                if category == "accepted":
                    style = "bold green"
                elif category in ["ignored", "unsupported"]:
                    style = "yellow"
                else:
                    style = "red"

                results_table.add_row(
                    category.replace("_", " ").title(),
                    f"[{style}]{count}[/{style}]",
                    percentage,
                )

        self.console.print(Panel(results_table, expand=False))


def create_embedding_progress_tracker(
    show_details: bool = True,
) -> EmbeddingProgressTracker:
    """
    Factory function to create an embedding progress tracker.

    Args:
        show_details: Whether to show detailed progress

    Returns:
        Configured EmbeddingProgressTracker
    """
    return EmbeddingProgressTracker(show_details)


def create_file_processing_tracker() -> FileProcessingTracker:
    """
    Factory function to create a file processing tracker.

    Returns:
        Configured FileProcessingTracker
    """
    return FileProcessingTracker()

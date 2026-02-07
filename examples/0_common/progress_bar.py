"""
Progress Bar Utility - Console Progress Indicators

Provides visual feedback for long-running operations with clean ASCII graphics.
Based on Go helpers/progress_bar.go design.

Usage:
    # Time-based progress bar
    bar = TimeProgressBar(total_seconds=180, message="Running strategy")
    while running:
        bar.update(elapsed_seconds)
    bar.finish()

    # Known-length operations
    with ProgressBar(total=100, description="Processing") as progress:
        for i in range(100):
            do_work()
            progress.update(i + 1)

    # Indeterminate operations
    with Spinner(description="Initializing") as spinner:
        await initialize()
        spinner.update()
"""

import sys
import time
from typing import Optional


# Visual characters for progress bar
FILLED_CHAR = "█"   # Filled portion
EMPTY_CHAR = "░"    # Empty portion
BAR_WIDTH = 20      # Default width


def clear_line():
    """Clear current console line using carriage return and spaces."""
    # Move to start of line (\r), write spaces to clear, move back
    sys.stdout.write('\r' + ' ' * 120 + '\r')
    sys.stdout.flush()


class TimeProgressBar:
    """
    Time-based progress bar for duration-based operations.

    Output format:
      Running strategy: [█████████░░░░░░░░░░] 45% (27s / 60s) - 33s remaining
    """

    def __init__(self, total_seconds: float, message: str = "Progress", bar_width: int = BAR_WIDTH):
        """
        Initialize time progress bar.

        Args:
            total_seconds: Total duration in seconds
            message: Message to display before bar
            bar_width: Width of bar in characters (default: 20)
        """
        self.total_seconds = total_seconds
        self.message = message
        self.bar_width = bar_width
        self.start_time = time.time()

    def update(self, elapsed: float):
        """
        Update progress bar with current elapsed time.

        Args:
            elapsed: Elapsed time in seconds
        """
        # Calculate progress (0.0 to 1.0)
        progress = min(elapsed / self.total_seconds, 1.0) if self.total_seconds > 0 else 0

        # Build progress bar
        filled_width = int(progress * self.bar_width)
        empty_width = self.bar_width - filled_width
        bar = FILLED_CHAR * filled_width + EMPTY_CHAR * empty_width

        # Calculate metrics
        percent = int(progress * 100)
        remaining = max(0, self.total_seconds - elapsed)

        # Build output string
        output = f"  {self.message}: [{bar}] {percent}% ({elapsed:.0f}s / {self.total_seconds:.0f}s) - {remaining:.0f}s remaining"

        # Clear line and write progress
        clear_line()
        sys.stdout.write(output)
        sys.stdout.flush()

    def finish(self):
        """Complete the progress bar and move to next line."""
        self.update(self.total_seconds)
        print()  # New line


class ProgressBar:
    """
    Progress bar for operations with known item count.

    Output format:
      Processing: [████████████░░░░░░░░] 60% (60/100) 12.5/s
    """

    def __init__(
        self,
        total: int,
        description: str = "",
        bar_length: int = BAR_WIDTH
    ):
        """
        Initialize progress bar.

        Args:
            total: Total number of items
            description: Description to display
            bar_length: Length of bar in characters
        """
        self.total = total
        self.current = 0
        self.description = description
        self.bar_length = bar_length
        self.start_time = time.time()
        self.finished = False

    def update(self, current: Optional[int] = None, increment: int = 1):
        """
        Update progress bar position.

        Args:
            current: Set absolute position (if None, increment instead)
            increment: Amount to increment if current is None
        """
        if self.finished:
            return

        # Update current position
        if current is not None:
            self.current = min(current, self.total)
        else:
            self.current = min(self.current + increment, self.total)

        # Calculate progress
        progress = self.current / self.total if self.total > 0 else 0
        filled = int(progress * self.bar_length)
        empty = self.bar_length - filled

        # Build bar
        bar = FILLED_CHAR * filled + EMPTY_CHAR * empty
        percent = int(progress * 100)

        # Calculate rate
        elapsed = time.time() - self.start_time
        rate = self.current / elapsed if elapsed > 0 else 0

        # Build output
        output = f'  {self.description}: [{bar}] {percent}% ({self.current}/{self.total}) {rate:.1f}/s'

        # Write to console
        clear_line()
        sys.stdout.write(output)
        sys.stdout.flush()

        # Complete when done
        if self.current >= self.total:
            self.finished = True
            print()  # New line

    def close(self):
        """Manually complete the progress bar."""
        if not self.finished:
            self.current = self.total
            self.update(self.current)

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
        return False


class Spinner:
    """
    Animated spinner for indeterminate operations.

    Output format:
      | Connecting... (2.3s)
      / Connecting... (2.4s)
      - Connecting... (2.5s)
      \\ Connecting... (2.6s)
    """

    # ASCII-safe spinner frames
    FRAMES = ['|', '/', '-', '\\']

    def __init__(self, description: str = ""):
        """
        Initialize spinner.

        Args:
            description: Description to display
        """
        self.description = description
        self.frame_index = 0
        self.start_time = time.time()
        self.stopped = False
        self.shown = False

    def update(self):
        """Update spinner animation to next frame."""
        if self.stopped:
            return

        # Get current frame
        frame = self.FRAMES[self.frame_index % len(self.FRAMES)]
        self.frame_index += 1

        # Elapsed time
        elapsed = time.time() - self.start_time

        # Build output
        output = f'  {frame} {self.description}... ({elapsed:.1f}s)'

        # Write to console
        clear_line()
        sys.stdout.write(output)
        sys.stdout.flush()

        self.shown = True

    def finish(self, message: str = "Done"):
        """
        Stop spinner and show completion message.

        Args:
            message: Completion message
        """
        if self.stopped:
            return

        self.stopped = True
        elapsed = time.time() - self.start_time

        # Clear and show final message
        clear_line()
        output = f'  [OK] {self.description}... {message} ({elapsed:.1f}s)\n'
        sys.stdout.write(output)
        sys.stdout.flush()

    def __enter__(self):
        """Context manager entry."""
        self.update()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.finish()
        return False


class CountdownTimer:
    """
    Simple countdown timer without progress bar.

    Output format:
      Starting in: 30s remaining...
      Starting in: 29s remaining...
    """

    def __init__(self, total_seconds: int, message: str = "Countdown"):
        """
        Initialize countdown timer.

        Args:
            total_seconds: Total seconds to count down
            message: Message to display
        """
        self.total_seconds = total_seconds
        self.message = message

    def update(self, remaining: int):
        """
        Update countdown display.

        Args:
            remaining: Remaining seconds
        """
        output = f"  {self.message}: {remaining}s remaining..."
        clear_line()
        sys.stdout.write(output)
        sys.stdout.flush()

    def finish(self):
        """Complete countdown and move to next line."""
        print()  # New line


def demo():
    """Demonstration of progress bar utilities."""
    print("=" * 80)
    print("PROGRESS BAR DEMO")
    print("=" * 80)
    print()

    # Demo 1: Time-based progress bar
    print("1. Time-based Progress Bar (10 seconds):")
    bar = TimeProgressBar(total_seconds=10, message="Running demo")
    start = time.time()
    while True:
        elapsed = time.time() - start
        bar.update(elapsed)
        if elapsed >= 10:
            break
        time.sleep(0.1)
    bar.finish()
    print()

    # Demo 2: Item-based progress bar
    print("2. Item-based Progress Bar:")
    with ProgressBar(total=50, description="Processing items") as progress:
        for i in range(50):
            time.sleep(0.05)
            progress.update(i + 1)
    print()

    # Demo 3: Spinner for indeterminate wait
    print("3. Spinner:")
    with Spinner(description="Initializing") as spinner:
        for _ in range(50):
            time.sleep(0.05)
            spinner.update()
    print()

    # Demo 4: Countdown timer
    print("4. Countdown Timer:")
    countdown = CountdownTimer(total_seconds=5, message="Starting in")
    for remaining in range(5, -1, -1):
        countdown.update(remaining)
        time.sleep(1)
    countdown.finish()
    print()

    print("=" * 80)
    print("Demo completed!")
    print("=" * 80)


if __name__ == "__main__":
    demo()

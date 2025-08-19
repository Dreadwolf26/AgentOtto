import json
from datetime import datetime
from pathlib import Path

from pydantic_core import to_jsonable_python
from pydantic_ai.messages import ModelMessagesTypeAdapter

# Directory to store archives
ARCHIVE_DIR = Path("archives")
ARCHIVE_DIR.mkdir(exist_ok=True)

def save_history(messages, topic: str) -> Path:
    """Save agent messages to a JSON file with a timestamped name."""
    filename = f"{topic}_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.json"
    path = ARCHIVE_DIR / filename
    data = to_jsonable_python(messages)
    path.write_text(json.dumps(data, indent=2))
    return path

def load_history(path: Path):
    """Load messages back from a JSON file."""
    data = json.loads(path.read_text())
    return ModelMessagesTypeAdapter.validate_python(data)

def list_histories() -> list[Path]:
    """List all stored history files."""
    return sorted(ARCHIVE_DIR.glob("*.json"))

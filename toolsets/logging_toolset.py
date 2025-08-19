# toolsets/logging_toolset.py

from __future__ import annotations

import json
import logging
import time
from pathlib import Path
from typing import Any, Optional

from dataclasses import dataclass, field

from pydantic_ai.tools import RunContext
from pydantic_ai.toolsets import WrapperToolset, ToolsetTool, AbstractToolset


def _scrub(value: Any) -> Any:
    """Scrub sensitive content from args/results before logging."""
    try:
        text = json.dumps(value, default=str)
    except Exception:
        return "<unserializable>"

    # Basic redactions (extend as needed)
    text = text.replace("sk-or-", "sk-REDACTED-")
    return json.loads(text)


def make_file_logger(path: str | Path = "logs/tool_calls.jsonl") -> logging.Logger:
    """Create or reuse a JSONL file logger."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger("agent.tools")
    logger.setLevel(logging.INFO)

    if not any(isinstance(h, logging.FileHandler) and getattr(h, "_log_path", None) == str(path) for h in logger.handlers):
        fh = logging.FileHandler(path, encoding="utf-8")
        fh._log_path = str(path)
        fh.setLevel(logging.INFO)
        fh.setFormatter(logging.Formatter("%(message)s"))
        logger.addHandler(fh)

    return logger


@dataclass
class LoggingToolset(WrapperToolset):
    """
    Wrap any toolset and log tool calls (start, finish, error) to a JSONL file.
    Usage: LoggingToolset(wrapped=some_toolset, logger=make_file_logger())
    """

    wrapped: AbstractToolset  # Required by WrapperToolset
    logger: logging.Logger = field(default_factory=make_file_logger)
    wrapper_name: str = "logging_wrapper"

    def __post_init__(self):
        # WrapperToolset expects to be passed `wrapped` to __init__
        super().__init__(self.wrapped)

    async def call_tool(
        self,
        name: str,
        tool_args: dict[str, Any],
        ctx: RunContext,
        tool: ToolsetTool,
    ) -> Any:
        t0 = time.perf_counter()

        record_base = {
            "wrapper": self.wrapper_name,
            "tool_name": name,
            "run_step": getattr(ctx, "run_step", None),
            "model": getattr(getattr(ctx, "model_info", None), "name", None),
            "phase": "start",
            "args": _scrub(tool_args),
        }

        try:
            # Log START
            self.logger.info(json.dumps(record_base, ensure_ascii=False))

            # Run actual tool
            result = await super().call_tool(name, tool_args, ctx, tool)

            # Log SUCCESS
            elapsed = time.perf_counter() - t0
            self.logger.info(json.dumps({
                **record_base,
                "phase": "finish",
                "elapsed_s": round(elapsed, 4),
                "result": _scrub(result),
            }, ensure_ascii=False))

            return result

        except Exception as e:
            # Log ERROR
            elapsed = time.perf_counter() - t0
            self.logger.error(json.dumps({
                **record_base,
                "phase": "error",
                "elapsed_s": round(elapsed, 4),
                "error": repr(e),
            }, ensure_ascii=False))
            raise

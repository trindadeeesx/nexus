import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))
from agents.dominus import DominusAgent
from agents.lucia import LuciaAgent
from runtime.adapters.terminal import TerminalAdapter
from runtime.context import NexusContext
from runtime.runtime import NexusRuntime


def test_terminal_flow():
    ctx = NexusContext()
    ctx.register_adapter("terminal", TerminalAdapter())
    ctx.register_agent("lucia", LuciaAgent())
    ctx.register_agent("dominus", DominusAgent())

    runtime = NexusRuntime(ctx)

    result = runtime.handle_input(
        text="oi lucia",
        user_id="user1",
        stream="terminal",
    )

    print(result)

    assert result["agent"] in ["lucia", "dominus"]
    assert result["action"] is not None


test_terminal_flow()

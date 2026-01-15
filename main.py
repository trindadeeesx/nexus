from agents.dominus import DominusAgent
from agents.lucia import LuciaAgent
from runtime.adapters.terminal import TerminalAdapter
from runtime.context import NexusContext
from runtime.runtime import NexusRuntime


def main():
    ctx = NexusContext()

    ctx.register_adapter("terminal", TerminalAdapter())
    ctx.register_agent("lucia", LuciaAgent())
    ctx.register_agent("dominus", DominusAgent())

    runtime = NexusRuntime(ctx)

    print("Nexus pronto. Digite algo (:exit para sair)\n")

    while True:
        text = input(">>> ")
        if text == ":exit":
            break

        runtime.handle_input(
            text=text,
            user_id="local-user",
            stream="terminal",
        )


if __name__ == "__main__":
    main()

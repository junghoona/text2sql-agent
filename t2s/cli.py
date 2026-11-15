"""Terminal chat: python -m t2s.cli"""
from t2s.agent import ask


def main() -> None:
    print("Text-to-SQL chat. Ctrl+C or 'exit' to quit.")
    messages: list = []
    while True:
        try:
            query = input("\nyou> ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if query.lower() in {"exit", "quit"}:
            break
        if query:
            messages.append({"role": "user", "content": query})
            print(f"\nagent> {ask(messages)}")


if __name__ == "__main__":
    main()

"""Terminal chat: python -m t2s.cli"""
from t2s.agent import ask


def main() -> None:
    print("Text-to-SQL chat. Ctrl+C or 'exit' to quit.")
    messages: list = []
    while True:
        try:
            q = input("\nyou> ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if q.lower() in {"exit", "quit"}:
            break
        if q:
            messages.append({"role": "user", "content": q})
            print(f"\nagent> {ask(messages)}")


if __name__ == "__main__":
    main()

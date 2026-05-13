# src/main.py
"""CLI entry point for the Auto Policy Q&A RAG app."""
from src.rag import ask

def main():
    print("\n=== Auto Policy Q&A ===")
    print("Ask any question...")

    while True:
        question = input("\nAsk a question (or 'quit'): ").strip()

        if question.lower() in {"quit", "exit", "q"}:
            print("Goodbye.")
            break
        if not question:
            continue

        ask(question)

if __name__ == "__main__":
    main()
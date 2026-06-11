# src/main.py
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

        result = ask(question)

        print(f"\nA: {result['answer']}\n")

        if result ["sources"]:
            print("---Sources---")
            for i, source in enumerate(result["sources"], start=1):
                print(f"\n[Source {i}] Score: {source['score']:.4f} | Page: {source['page']} | From: {source['source']}")
                print(f"{source['text'][:200]}...")


if __name__ == "__main__":
    main()
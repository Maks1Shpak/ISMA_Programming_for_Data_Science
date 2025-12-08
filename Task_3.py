def analyze_text(s: str, strip_spaces: bool = True) -> dict:
    if strip_spaces:
        s_proc = s.strip()
    else:
        s_proc = s

    length = len(s_proc)
    words = s_proc.split()
    word_count = len(words)

    title = s_proc.title()
    lower = s_proc.lower()
    upper = s_proc.upper()

    is_title = (s_proc == title)
    is_lower = (s_proc == lower)
    is_upper = (s_proc == upper)

    return {
        "original": s,
        "processed": s_proc,
        "length": length,
        "count_char": length,
        "word_count": word_count,
        "title": title,
        "lower": lower,
        "upper": upper,
        "is_title": is_title,
        "is_lower": is_lower,
        "is_upper": is_upper
    }

def pretty_print(result: dict) -> None:
    print("\nAnalysis Result:")
    print(f"  **original**: {result['original']}")
    print(f"  **processed**: {result['processed']}")
    print(f"  **length**: {result['length']}")
    print(f"  **count_char**: {result['count_char']}")
    print(f"  **word_count**: {result['word_count']}")
    print(f"  **title**: {result['title']}")
    print(f"  **lower**: {result['lower']}")
    print(f"  **upper**: {result['upper']}")
    print(f"  **is_title**: {result['is_title']}")
    print(f"  **is_lower**: {result['is_lower']}")
    print(f"  **is_upper**: {result['is_upper']}\n")

def main():
    print("Enter a string to analyze. To exit, type exit or quit.")
    while True:
        try:
            s = input(">>> ")
        except EOFError:
            print("\nEnd of input. Exiting.")
            break

        if not s:
            print("Empty string. Try again or type exit to exit.")
            continue

        if s.lower() in ("exit", "quit"):
            print("Exiting the program.")
            break

        result = analyze_text(s, strip_spaces=True)
        pretty_print(result)

if __name__ == "__main__":
    main()
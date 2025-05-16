from utils import print_banner
from openai_helper import parse_query_with_gpt

def main():
    print_banner()
    print("Welcome to Chat NBA! Ask me anything about NBA stats.")
    print("(Type 'exit' to quit)\n")

    while True:
        user_input = input("> ")

        if user_input.lower() in ["exit", "quit"]:
            print("Goodbye!")
            break

        print("\nThinking...\n")

        # Get structured intent from GPT
        result = parse_query_with_gpt(user_input)

        # Show result
        print("Parsed intent:")
        print(result)
        print()

if __name__ == "__main__":
    main()

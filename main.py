from utils import print_banner

def main():
    print_banner()
    print("Welcome to Chat NBA! Ask me anything about NBA stats.\n(Type 'exit' to quit)\n")

    while True:
        user_input = input("> ")

        if user_input.lower() in ["exit", "quit"]:
            print("Goodbye!")
            break

        print(f"You asked: {user_input} (feature coming soon!)\n")

if __name__ == "__main__":
    main()

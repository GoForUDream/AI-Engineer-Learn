from .services.greeting_service import build_greeting


def main():
    name = input("Please enter your name: ")
    greeting = build_greeting(name)
    print(greeting)


if __name__ == "__main__":
    main()

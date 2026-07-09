from langchain_core.messages import HumanMessage
from graph import graph
from state import State


def main():
    print("=" * 50)
    print("LangGraph Demo")
    print("Type 'exit' to quit")
    print("=" * 50)

    while True:
        user_input = input("\nYou: ")

        if user_input.strip().lower() == "exit":
            print("Exiting the demo. Goodbye!")
            break

        state: State = {"messages": [HumanMessage(content=user_input)]}

        result = graph.invoke(state)
        print("\nAssistant:", result["messages"][-1].content)


if __name__ == "__main__":
    main()

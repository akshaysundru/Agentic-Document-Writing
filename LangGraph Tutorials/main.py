from dotenv import load_dotenv
from typing import Annotated, Literal
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain.chat_models import init_chat_model
from typing_extensions import TypedDict

llm = init_chat_model(model="llama3.2", model_provider="ollama")

class State(TypedDict):
    messages: Annotated[list, add_messages]

graph_builder = StateGraph(State)

def chatbot(state: State):
    return {"messages": [llm.invoke(state["messages"])]}

graph_builder.add_node("chatbot", chatbot) 
graph_builder.add_edge(start_key=START, end_key="chatbot")
graph_builder.add_edge(start_key="chatbot", end_key=END)

user_input = input("Enter a message: ")

graph = graph_builder.compile()

state = graph.invoke({"messages": [{"role": "user", "content": user_input}]})

print(state["messages"][-1].content)
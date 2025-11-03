from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Annotated, Literal
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, BaseMessage
import os
from pydantic import BaseModel, Field
import operator
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_core.tools import tool
from langchain_community.tools import DuckDuckGoSearchRun
import requests
import random

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

model = ChatGoogleGenerativeAI(
    model= "gemini-2.5-flash",
    temperature=1.0,
    max_retries=2,
    google_api_key=api_key,
)

search_tool = DuckDuckGoSearchRun() 

@tool
def calculator(first_num : float, second_num: float, operation: str) -> dict :
    """
    Perform a basic arithmetic operation on two numbers, 
    supported opertion:add sub, mul
    """
    if operation=="add":
        result = first_num+second_num
    if operation=="sub":
        result = first_num-second_num
    if operation=="mul":
        result = first_num*second_num
    return {
        "first_num":first_num,
        "second_num": second_num,
        "operation" : operation,
        "result" : result
    } 

tools = [search_tool, calculator]
model_with_tools = model.bind_tools(tools)

from langgraph.graph.message import add_messages
class chatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
   

def chat_node(state: chatState):
    messages = state["messages"]
    response = model.invoke(messages)
    return {"messages" : [response]}

tool_node = ToolNode(tools) 

checkpointer = MemorySaver()
graph = StateGraph(chatState)

# add nodes
graph.add_node("chat_node", chat_node)
graph.add_node("tools", tool_node)

# add edges
graph.add_edge(START, "chat_node")
graph.add_conditional_edges("chat_node", tools_condition)
# graph.add_edge("chat_node", END)

# compile graph
workflow = graph.compile(checkpointer=checkpointer)
config = {'configurable': {'thread_id': 1}}
response = workflow.invoke({ "messages": [HumanMessage(content={"what is 2+4"})]}, config=config)
print(response["messages"][-1].content)

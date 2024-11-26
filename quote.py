# https://python.langchain.com/docs/integrations/tools/sql_database/
import sqlite3
from dotenv import load_dotenv
from langchain_community.utilities.sql_database import SQLDatabase
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from langchain import hub

db = SQLDatabase.from_uri("sqlite:///example.db")
print("Available tables:", db.get_table_names())

# Load environment variables from .env file
load_dotenv()

from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4o-mini")

# Use the SQLDatabaseToolkit
from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit

toolkit = SQLDatabaseToolkit(db=db, llm=llm)
toolkit.get_tools()

# -----
prompt_template = hub.pull("langchain-ai/sql-agent-system-prompt")

assert len(prompt_template.messages) == 1
print("Input variables:", prompt_template.input_variables)
system_message = prompt_template.format(dialect="SQLite", top_k=5)

from langgraph.prebuilt import create_react_agent

agent_executor = create_react_agent(
    llm, toolkit.get_tools(), state_modifier=system_message
)

# Loop to continuously ask for user queries
# example_query = "tell me quote which is pending" and "tell me pending quote which was created in feb"
while True:
    user_input = input("Enter your query (or 'q' to quit): ")
    if user_input.strip().lower() == 'q':
        print("Exiting...")
        break

    # Run the agent_executor on user_input
    events = agent_executor.stream(
        {"messages": [("user", user_input)]},
        stream_mode="values",
    )
    for event in events:
        event["messages"][-1].pretty_print()

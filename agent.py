""" Agent that changes the structure of the JSON notes based on the user natural language instructions """

from langchain.chat_models import ChatOpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
import json
import os

import openai
from dotenv import load_dotenv
load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

system_template = """You are an assistant from a note taking application. You are charged with the task of changing the structure of a JSON file representing the organization of a user's notes, based on the user instructions. 


The notes organization tree is represented as a JSON file, which comprises two types of nodes : the folders and the notes. The folders can contain other folders and notes. The notes are leaves of the tree.

A node of the tree, representing a folder or a note, is a JSON object with the following fields:

'id': int (unique identifier of the node),
'name': string (name of the folder or note),
'text': string (only for notes, 'null' value otherwise),
'type': string (either 'folder' or 'file'),
'children': [...] (children nodes of the folder, empty list otherwise)


Here are the actions that you are allowed to perform on the notes tree in JSON format:
- creating a new note
- creating a new folder
- editing an existing note
- moving a note to a folder
- moving a folder (and all its children nodes) to a folder
- deleting a note
- deleting a folder (and all its children nodes)
If the action is not allowed or no instructions are given, return the original notes tree.


You will return return the new notes tree wrapped around triple backticks and the 'json' keyword, like this:
```json
JSON_NOTES_TREE
```


Now, here is the current organization of the notes tree:
{notes_tree}
"""

human_template = """Follow these instructions to modify the organization of the notes tree:
{instructions}

Only return the new organization of the notes tree, don't add any comment, and respect the JSON format encapsulated by the three backsticks and the json tag. If the action is not allowed or no instructions are given, return the original notes tree."""

system_prompt = SystemMessagePromptTemplate.from_template(system_template)
human_prompt = HumanMessagePromptTemplate.from_template(human_template)
CHAT_PROMPT = ChatPromptTemplate.from_messages([system_prompt, human_prompt])

def get_chain(temperature=0):
    llm = ChatOpenAI(model="gpt-4", temperature=temperature)
    chain = LLMChain(llm=llm, prompt=CHAT_PROMPT)
    return chain
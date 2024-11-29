from sqlalchemy import create_engine, text, event
from llama_index.core import SQLDatabase, Settings, PromptTemplate
from llama_index.llms.gemini import Gemini
from llama_index.core.query_engine import NLSQLTableQueryEngine
from typing import List, Dict, Literal
import uuid

MessageType = Dict[Literal["user", "assistant"], str]


# engine = create_engine(connection_string)

# sql_database = SQLDatabase(engine=engine)

# llm = Gemini(
#     model="models/gemini-1.5-flash",
#     api_key=GOOGLE_API_KEY,  # uses GOOGLE_API_KEY env var by default
# )

# query_engine = NLSQLTableQueryEngine(
#     sql_database=sql_database,
#     llm=llm,
#     embed_model='local'
# )

# prefix = ""

# template = (
#     "We have provided context information below. \n"
#     "---------------------\n"
#     "{context_str}"
#     "\n---------------------\n"
#     "Given this information, please answer the question: {query_str}\n"
#     "OUTPUT_FORMAT: {\"type\": \"SUCCESS or ERROR\", \"content\": \"relevant_content\", \"contentType\": \"valid_json_supported_type\", \"tables_used\":[table names]}")

# qa_template = PromptTemplate(template)

# def test():
#     while True:
#         query_str = input("Enter a Query: ")
#         if(query_str.lower() in ["quit", "exit", "q"]):
#             break
#         prefix = qa_template.format(context_str=prefix, query_str=query_str)
#         response = query_engine.query(prefix)
#         for query_id, query_info in response.metadata.items():
#             if('sql_query' in query_info):
#                 sql_query = query_info['sql_query']
#                 print("Query: ", sql_query)
#                 prefix = prefix + "\n<assistant|start> Query Used: " + sql_query + " <assistant|end>\n"
#         prefix = prefix + "\n<assistant|start> Response Formulated: " + response.response + " <assistant|end>\n"

#         print("Result: ", response)
        
    



# class QUERY_ENGINE:
#     def __init__(self, sql_database:SQLDatabase, llm:Gemini, embed_model:str="local"):
#        self.id = uuid.uuid4()
#        self.query_engine = NLSQLTableQueryEngine(sql_database, llm, embed_model) 
    
#     def get_query_engine(self):
#         return self.query_engine


# query_engines: List[Dict[str, NLSQLTableQueryEngine]] = []


# def query_engine_response(query_str: str, chat_history: str, query_engine_id: str):
#     for engine_dict in query_engines:
#         if query_engine_id in engine_dict:
#             return engine_dict[query_engine_id]
#         else:
#             raise KeyError(f"Engine with ID '{query_engine_id}' not found.")
        
#     input_str = qa_template.format(context_str=chat_history, query_str=query_str)
#     response = query_engine.query(input_str)
#     print("Result:", response)
#     return response






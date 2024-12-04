import os

from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
from flask_src.definitions.definitions import MessageType
from flask_src.utils.chat_template import convert_to_chat_template
from flask_src.utils.validation import validate_request_data
from llama_index.core import SQLDatabase, Settings, PromptTemplate
from llama_index.llms.gemini import Gemini
from llama_index.core.query_engine import NLSQLTableQueryEngine
from sqlalchemy import create_engine, text, event
from typing import List, Dict, Literal
import uuid
import re
import json


db_connections: Dict[str, SQLDatabase] = {}
query_engines: Dict[str, NLSQLTableQueryEngine] = {}
chat_histories: Dict[str, List[MessageType]] = {}


template = (
    "We have provided context information below. \n"
    "---------------------\n"
    "{context_str}"
    "\n---------------------\n"
    "Given this information, please answer the question: {query_str}\n"
    "OUTPUT_FORMAT: {\"type\": \"SUCCESS or ERROR\", \"message\": \"final output string\", \"contentType\": \"valid json type of message (example: string)\", \"tables_used\":[table names]}")


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    CORS(app, supports_credentials=True, resources={r"/*": {"origins": "http://localhost:5173"}})
    app.config.from_mapping(
        SECRET_KEY='dev',
    )

    # a simple page that says hello
    @app.route('/hello')
    def hello():
        return 'Hello, World!'
    
    # add connection to db
    @app.route('/connect-db', methods=['POST'])
    @cross_origin()
    def connect_db():
        
        data = request.json

        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        db_user = data.get("db_user")
        db_pswrd = data.get("db_pswrd")
        db_host = data.get("db_host")
        db_name = data.get("db_name")
        connection_string = f"mysql+pymysql://{db_user}:{db_pswrd}@{db_host}/{db_name}"

        engine = create_engine(connection_string)
        sql_database = SQLDatabase(engine=engine)
        id = uuid.uuid4()
        db_connections[id] = sql_database
        return jsonify({"message": "SUCCESS", "content": {"id": id} })
    
    # get db connection by id
    @app.route('/get-db/<db_id>', methods=['GET'])
    @cross_origin()
    def get_db(db_id):
        try:
            db_id = uuid.UUID(db_id)  # Convert string to UUID
        except ValueError:
            return jsonify({"error": "Invalid UUID format"}), 400
        
        if db_id not in db_connections:
            return jsonify({"error": "Incorrect id provided"}), 400
        
        return jsonify({"message":"SUCCESS", "content":{"id": db_id, "db": db_connections[db_id].get_usable_table_names() }})

    @app.route('/chat/gemini/register', methods=["POST"])
    @cross_origin()
    def chat_register_gemini():
        data = request.json

        if not data:
            return jsonify({"error": "No data provided"}), 400
        try:
            db_id:str = data.get("id")
            api_key:str = data.get("api_key")
            model_name:str = data.get("model_name")
        except Exception as e:
            return jsonify({"error": "Bad Request"}), 400
        
        isValid = validate_request_data([db_id, api_key, model_name])
        if not isValid:
            return jsonify({"error": "Bad Request"}), 400
        
        try:
            db_id = uuid.UUID(db_id)  # Convert string to UUID
        except ValueError:
            return jsonify({"error": "Invalid UUID format"}), 400   
        
        if db_id not in db_connections:
            return jsonify({"error": "Incorrect id provided"}), 400
                
        db = db_connections[db_id]
        
        llm = Gemini(
            model="models/" + model_name,
            api_key=api_key,  # uses GOOGLE_API_KEY env var by default
        )
        
        if isinstance(llm, Gemini):
            id = uuid.uuid4()
            query_engine = NLSQLTableQueryEngine(
                sql_database=db,
                llm=llm,
                embed_model='local'
            )
            query_engines[id] = query_engine
            return jsonify({"message":"SUCCESS", "content": {"id": id, "model": model_name}})
        
        return jsonify({"error": "Unable to register, please try again later"}), 500
            
    @app.route('/chat/gemini/room/<chat_id>', methods=['POST'])
    @cross_origin()
    def chat_room_gemini(chat_id):
        data = request.json

        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        query_str = data.get("query")
        
        if query_str is None or not isinstance(query_str, str):
            return jsonify({"error":"Bad Request"}), 400
        
        try:
            chat_id = uuid.UUID(chat_id)  # Convert string to UUID
        except ValueError:
            return jsonify({"error": "Invalid UUID format"}), 400  

        if chat_id not in query_engines:
            return jsonify({"error": "Chat session Id not found"}), 400
        
        query_engine = query_engines[chat_id]
        chat_history = chat_histories.get(chat_id, None)
        
        qa_template = PromptTemplate(template)
        context_str = ""
        if chat_history is not None:
            context_str = convert_to_chat_template(chat_history)
        query = qa_template.format(context_str=context_str, query_str=query_str)
        try:
            res = query_engine.query(query)
            sql_query = ""
            for query_id, query_info in res.metadata.items():
                if('sql_query' in query_info):
                    sql_query = query_info['sql_query']
            try:
                response:str = res.response
                if response.strip().startswith("```json") and response.strip().endswith("```"):
                    match = re.search(r"```json\n(.*?)\n```", response.strip(), re.DOTALL)
                    if match:
                        json_string = match.group(1)
                        try:
                            # Parse the JSON string into a dictionary
                            response_json = json.loads(json_string)

                        except json.JSONDecodeError as e:
                            raise ValueError(f"Error parsing JSON: {e}")
                    else:
                        raise ValueError("JSON content not found within markdown formatting.")
                else:
                    raise ValueError("Invalid markdown formatting.")
            except:
                raise ValueError("response was invalid")
            
            chat_histories.setdefault(chat_id, []).extend([{"user": query_str}, {"assistant": response + f"\nSQL Query Used:{sql_query}\n",}])
            return jsonify({"message":"SUCCESS", "content": {"response": response_json, "sql_query": sql_query}})
        except Exception as e:
            return jsonify({"error": "Internal Server Error", "message": "Unable to process query"}), 500
            
    @app.route('/chat/gemini/history/<chat_id>', methods=['GET'])
    @cross_origin()
    def chat_history_gemini(chat_id):
        try:
            chat_id = uuid.UUID(chat_id)  # Convert string to UUID
        except ValueError:
            return jsonify({"error": "Invalid UUID format"}), 400  
        if chat_id not in chat_histories:
            return jsonify({"error": "Id not valid"}), 400
        
        return jsonify({"message": "SUCCESS", "response": chat_histories[chat_id]})
            
    return app
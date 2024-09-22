import json
import re


class Conceptor : 
    def __init__(self,documents,llm_client,project_idea) :
        self.documents = documents
        self.project_idea = project_idea
        self.llm_client = llm_client
   
    def _create_overview(self):   
    
        def propose_project():
            prompt = """
            Please generate a **Project Overview Document** for a web application ( only serveur side (back end)) with the following sections. Output the content in JSON format:

            {
                "Project Overview Document": {
                "Application Name" : "text here"
                "Introduction": "Provide a brief introduction to the web application, including its purpose and scope.",
                "Objectives": "Outline the key objectives of the project. What are the primary goals that this web application aims to achieve?",
                "Stakeholders": "Identify the main stakeholders involved in this project. Who are the key players, including users, developers, and other parties with a vested interest in the project's success?",
                "Key Features": {
                    "feature name" : "text here",
                    "feature description" : "text here"
                }
                }
            }

            features : 
            default features : User Authentication and Authorization / admin Dashboard /  User Profiles 
            app specefic features : depend on the project idea give me this project features
            be creative generating well described web app ( choose the idea randomly ( about %s))
            Please ensure that each section is clearly labeled and follows this format exactly.
            """ %  self.project_idea

            
            resp = self.llm_client.bard(prompt)
            resp = self.llm_client.extract_substring(resp,'```json','```')

            prompt = f'''this is my Project Overview Document {resp} 
            decompose features into sub features to make the feature more understandable 

            exemple output format needed: 

            '''
            exemple_prompt = """""Key Features": {
                    "feature 1  name" : "text here",
                    "feature 1 description" : "text here",
                    "sub-featues" : {
                    "sub-feature name" : "text here",
                    "sub-feature description" : "text here"
                    },
                    {
                    "feature 2  name" : "text here",
                    "feature 2 description" : "text here",
                    "sub-featues" : {
                    "sub-feature name" : "text here",
                    "sub-feature description" : "text here"
                    },
                    ...
                }
                """
            prompt = prompt + exemple_prompt
            resp = self.llm_client.bard(prompt)
            return resp


        def validate_key_features(data):

            try:
                # Check if the main sections are present
                if "Project Overview Document" not in data:
                    return False

                project_overview = data["Project Overview Document"]
                
                # Check if "Key Features" exists and is a dictionary
                if "Key Features" not in project_overview or not isinstance(project_overview["Key Features"], dict):
                    return False

                # Ensure that each feature in "Key Features" is a dictionary
                for feature, details in project_overview["Key Features"].items():
                    if not isinstance(details, dict):
                        return False

                # If all checks pass, return True
                return True
            except json.JSONDecodeError:
                return False


        flag = False
        resp = propose_project()
        while flag == False : 
            
            resp = self.llm_client.extract_substring(resp,'```json','```')
            try:
                json_data = json.loads(resp)
            except json.JSONDecodeError as e:
                error = e
                print("Invalid JSON string:", e)
                json_data = None

            # Insert the JSON data into MongoDB if it's valid
            if json_data:
                if validate_key_features(json_data):
                    flag = True
                    print("document created succ")
                    return json_data
                else: 
                    print("""overview created is messy , i'll try again""")
                    resp = propose_project()

            else:
                resp = self.llm_client.bard(f"there is a problem in this json sting {error}: Invalid JSON string correct the strecture without editing the content . scape \" if it cause the problem : Json string :{resp}")
            
    def _create_user_roles(self,overview):   

        def propose_user_role(resp):

            base_prompt = f'''based on {resp} '''
            prompt = """
            Please generate a **User Roles** for this web application with the following sections. Output the content in JSON format:
            {
            "User Roles Document": {
                "User role": { 
                "User role name " : "text here",
                "description" : "text here"
                },
            }
            }

            this is describing your web app Non-Functional Requirements
            Please ensure that each section is clearly labeled and follows this format exactly.
            """
            final_prompt = base_prompt + prompt
            user_role = self.llm_client.bard(final_prompt)
            return user_role

        flag = False
        user_role = propose_user_role(overview)
        while flag == False : 
            
            user_role = self.llm_client.extract_substring(user_role,'```json','```')
            try:
                json_data = json.loads(user_role)
            except json.JSONDecodeError as e:
                error = e
                print("Invalid JSON string:", e)
                json_data = None

            # Insert the JSON data into MongoDB if it's valid
            if json_data:
                flag = True
                print("document created succ")
                return json_data
            else:
                resp = self.llm_client.bard(f"there is a problem in this json sting {error}: Invalid JSON string correct the strecture without editing the content . scape \" if it cause the problem : Json string :{user_role}")

    def _create_system_architecture(self,overview):   

        def propose_sys_archi(overview ):

            base_prompt = f'''based on {overview} '''
            prompt = """
            Please generate a **System Architecture** for this web application with the following sections. Output the content in JSON format:
            the application is only back end ( only endpoints )
            {
            "System Architecture document" {
                "Development Strategy" : "develope this sentense to be more clear and pro . sentense : Flask Application with Modular Architecture only back end endpoints " ,
                "Technology Stack" : {
                "Framework" :"Flask (Python)"
                "Database" : "MongoDB"
                "ODM" : "mongoengine"
                "API Design" : "RESTful APIs"
                "Object serialization/deserialization and validation"  : "Flask-Marshmallow"
                "Authentication & Authorization" : "Flask-JWT-Extended"
                "Role-based authorization" : "Flask-Principal"
                "Caching" : "Redis"
                "Logging" : "structlog"
                "Testing" : "pytest"
                "email sender" : "flask-mail"
                "Cross-Origin Resource Sharing" : "flask_cors"
                "File Uploads" : "Flask-Uploads"
                "Form handling and CSRF protection" : "Flask-WTF"
                do not add other fields 
                }

                }
            }

            }
            ps : you must choose : mongo db for the database ,  server-side logic REST APIs  : flash with python 
            this is describing your web app System Architecture 
            Please ensure that each section is clearly labeled and follows this format exactly.
            """
            final_prompt = base_prompt + prompt
            archi = self.llm_client.bard(final_prompt)
            return archi

        flag = False
        archi = propose_sys_archi(overview)
        while flag == False : 
            
            archi = self.llm_client.extract_substring(archi,'```json','```')
            try:
                json_data = json.loads(archi)
            except json.JSONDecodeError as e:
                error = e
                print("Invalid JSON string:", e)
                json_data = None

            if json_data:
                flag = True
                print("document created succ")
                return json_data
            else:
                archi = self.llm_client.bard(f"there is a problem in this json sting {error}: Invalid JSON string correct the strecture without editing the content . scape \" if it cause the problem : Json string :{archi}")

    def _create_features_details(self,overview,users_role,sys_archi): 

        def validate_single_item_json(json_data):
            """
            Validates that the JSON data contains exactly one item that is an object.
            Returns True if valid, False otherwise.
            """
            if not isinstance(json_data, dict):
                return False
            
            # Check if there is exactly one key
            if len(json_data) != 1:
                return False
            
            # Check if the value associated with the single key is a dictionary
            key, value = next(iter(json_data.items()))
            if not isinstance(value, dict):
                return False
            
            return True

        def json_string_to_json_object(queries):
            attemps = 0
            
            while True : 
                resp = self.llm_client.extract_substring(queries,'```json','```')
                try:
                    json_data = json.loads(resp)
                except json.JSONDecodeError as e:
                    error = e
                    print("Invalid JSON string:", e)
                    json_data = None

                # Insert the JSON data into MongoDB if it's valid
                if json_data:
                    return json_data
                elif attemps < 4:
                    resp = self.llm_client.bard(f"there is a problem in this json sting {error}: Invalid JSON string correct the strecture without editing the content . scape \" if it cause the problem : Json string :{resp}")
                    attemps += 1
                else :
                    return None

        def merge_dicts(dicts):
            result = {}
            for d in dicts:
                if not isinstance(d, dict):
                    raise ValueError(f"Expected a dictionary but got {type(d)}")
                for key, value in d.items():
                    if key in result:
                        if isinstance(result[key], dict) and isinstance(value, dict):
                            result[key] = merge_dicts([result[key], value])
                        elif isinstance(result[key], list) and isinstance(value, list):
                            result[key].extend(value)
                        else:
                            result[key] = value
                    else:
                        result[key] = value
            return result


        def propose_features_details(overview,users_role,sys_archi):
            features = []
            project_overview = overview["Project Overview Document"]
            context_prompt = f"this is the general context of the web application : 'project overview' :  {project_overview} ; 'system architecture' : {sys_archi} ; 'users roles': {users_role}"
            output_format_prompt = """
            {
            "feature name" : {
                "endpoints" : {
                                "endpoint1" : "text here"
                                "Methods" : "text here"
                                "Description" : "text here"
                                "who can use this endpoint" : "autorized role"
                                "user story" : "must be detailed "
                                "endpoint request Validation criteria" : "must be detailed"
                                "dependencies" : "if there is a python library that facilite devoloping the logic : be specefic naming the libraries only no extra explanation or options "
                                "notes for devoloper" : "text here"
                                "potantional issus must watch out" : "text here"
                                },
                                {
                                "endpoint2" : "text here"
                                "Methods" : "text here"
                                "Description" : "text here"
                                "who can use this endpoint" : "autorized role"
                                "user story" : "text here"
                                "endpoint request Validation criteria" : "must be detailed"
                                "dependencies" : "if there is a python library that facilite devoloping the logic : be specefic naming the libraries only no extra explanation or options "
                                "notes for devoloper" : 'text here"
                                "potantional issus must watch out" : "text here"
                                }
                                ....
                            }
                        }
            }
            """

            for feature, details in project_overview["Key Features"].items():
                task_prompt = f'''
                **focus only on this feature** : {feature} .
                this is the feature details {details} .
                task : Generate details for this feature (clean and pro)
                Please ensure that each section is clearly labeled and follows this format exactly.
                Output the content in JSON format : 

                '''
                final_prompt = context_prompt + task_prompt + output_format_prompt
                resp = self.llm_client.bard(final_prompt)
                resp = json_string_to_json_object(resp)
                valid = validate_single_item_json(resp)
                while resp is None and not valid: 
                    resp = self.llm_client.bard(final_prompt)
                    resp = json_string_to_json_object(resp)
                    valid = validate_single_item_json(resp)
                features.append(resp)

            combined_json = merge_dicts(features)
            json_string = json.dumps(combined_json, indent=4) 
            return json_string

        attempts = 0  
        flag = False
        features = propose_features_details(overview,users_role,sys_archi)
        while flag == False : 
            
            try:
                json_data = json.loads(features)
            except json.JSONDecodeError as e:
                error = e
                print("Invalid JSON string:", e)
                json_data = None

            # Insert the JSON data into MongoDB if it's valid
            if json_data:
                flag = True
                print("document created succ")
                return json_data
            elif attempts < 5:
                features = self.llm_client.bard(f"there is a problem in this json sting {error}: Invalid JSON string correct the strecture without editing the content . scape \" if it cause the problem : Json string :{features}")
                print("error loop")
                features = self.llm_client.extract_substring(features,'```json','```')
                attempts += 1
            else :
                features = propose_features_details(overview,users_role,sys_archi) 
                attempts = 0

    def _create_database_schema(self,resp,user_role,feature2):   

        def propose_database_schema(resp,user_role,feature2):

            base_prompt = f'''based on : {resp}  and {feature2} and {user_role}'''

            prompt = """
            Please generate a **database schema** for this web application . Output the content in JSON format:
            {
            "Database Schema": {
                "Tables": {
                "Table Name" : {
                    "Columns": {
                    "Column Name" : {
                        "Data Type": "text here",
                        "Constraints": "text here"
                    },
                    ...
                    }
                    "related Table Name"(if exist) : "text here"
                }
                }
                }
            Please ensure that each section is clearly labeled and follows this format exactly.
            User table name must be : "Users" hase a column role, there is no userrole table 
        
            """
            final_prompt = base_prompt + prompt
            database_schema = self.llm_client.bard(final_prompt)
            return database_schema

        flag = False
        database_schema = propose_database_schema(resp,user_role,feature2)
        while flag == False : 
            database_schema = self.llm_client.extract_substring(database_schema,'```json','```')
            try:
                json_data = json.loads(database_schema)
            except Exception as e:
                error = e
                print("Invalid JSON string:", e)
                json_data = None

            # Insert the JSON data into MongoDB if it's valid
            if json_data:
                flag = True
                print("document created succ")
                return json_data
            else:
                resp = self.llm_client.bard(f"there is a problem in this json sting {error}: Invalid JSON string correct the strecture without editing the content . scape \" if it cause the problem : Json string :{database_schema} \n \n output format : Json")

    def concept(self):
        
        overview = self._create_overview()
        user_roles = self._create_user_roles(overview)
        system_architecture = self._create_system_architecture(overview)
        features = self._create_features_details(overview,user_roles,system_architecture)
        database_schema = self._create_database_schema(overview,user_roles,features)
        self.documents.save_document(overview, "overview_document_id")
        self.documents.save_document(user_roles, "user_roles_document_id")
        self.documents.save_document(system_architecture, "archi_document_id")
        self.documents.save_document(database_schema, "database_schema_document_id")
        self.documents.save_document(features, "features_document_id")
        print("Conception is done check the database")
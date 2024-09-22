import re
import yaml
class Debuger :
    def __init__(self,llm_client,skloton_manager,stack,file_name,app_root) :
        self.app_root = app_root
        self.step = 0
        self.file_name = file_name
        self.error = ""
        self.logs = []
        self.stack = stack
        self.skloton_manager = skloton_manager
        self.llm_client = llm_client
        self.envirement = {
            "Os" : "Windows",
            "python version" :"3.11" 
        }

        self.project_skloton = skloton_manager.get_project_skeleton()
        self.role_prompt = f"You are a Expert Debugger specialist in {self.stack} , you are currentrly working on this project ; project shema : {self.project_skloton} exist in : project path :{self.app_root} in this envirement : {self.envirement} "
        self.file_path = self.skloton_manager.find_path(self.file_name)
        self.file_content = self.skloton_manager.get_file_content(self.file_path)
        self.context = f"while running {self.file_name}.py \n \n file content : {self.file_content} \n \n this error raise up . Error : {self.error} "

    def get_depended_files(self):
        extracted_files = []
        pattern = r"[^\\/]+\.py$"

        task_prompt = (
            "Your task is to identify files in the project that depend on this error. "
            "Please ensure that the returned list contains only files that exist in the project schema provided earlier. "
            "(Files that need to be checked or edited to correctly debug the error.)"
        )
        output_format = "List of file_names no eextra markdowns or words"
        exemple_output = "Example output: [config.py, activity.py, test_activity.py]"
        while  len(extracted_files) ==0 :
            # Call the LLM client with the updated prompt
            depended_files_string = self.llm_client.bard(
                f"**Your Role** : {self.role_prompt} \n\n"
                f"**Context** : {self.context} . \n\n"
                f"**Your Task** : {task_prompt} \n\n"
                f"**output_format** : {output_format} \n\n"
                f"**exemple_output** : {exemple_output}"
            )
            depended_files_string = self.llm_client.extract_substring(depended_files_string,"```json","```")
            print(depended_files_string)
            depended_files_string = self.llm_client.extract_substring(depended_files_string,'[',']')
            print(depended_files_string)
            depended_files = depended_files_string.split(',')
            print(depended_files)

            
            for file in depended_files:
                print(file)
                file = file.replace("'","")
                file = file.replace('"','')
                match = re.search(pattern, file)

                print(match)
                if match:
                    extracted_files.append(match.group(0))

            
            print(extracted_files)
            print("in while loop ")

        return extracted_files

    def validate_yaml(self,yaml_text):
        try:
            # Load the YAML data
            data = yaml.safe_load(yaml_text)
        except yaml.YAMLError as e:
            # Print the error details (optional)
            print(f"YAML parsing error: {e}")
            return False
        
        # Define allowed types
        allowed_types = ["commande", "Edit code"]

        # Flag to check if file_name exists
        file_name_exists = False

        # Check each debugging step
        for step in data['Debugging steps']:
            step_type = step.get('type')
            file_name = step.get('file_name')

            # Check if type is valid
            if step_type not in allowed_types:
                print(f"Invalid type: {step_type}. Allowed types are {allowed_types}")
                return False

            # Check if file_name exists in the dictionary
            if file_name:
                file_name_exists = True

        # Return whether file_name exists
        if not file_name_exists:
            print("file_name is missing from the debugging steps.")
            return False
        
        return True

    def genrerate_actions(self ,depended_files,logs = None):
        if logs : 
            previous_unworking_solutions = f"you sugest to me prevously an debugging action but still the smae error : this is the rapport : {logs}"
            context = self.context  + "\n \n" + previous_unworking_solutions
        else :
            context = self.context
        depended_files_with_content = []
        for file in depended_files : 
            file_path = self.skloton_manager.find_path(f"{file}.py")
            content = self.skloton_manager.get_file_content(file_path)
            temp_dict = {
                "file" : file,
                "content" : content
            }
            depended_files_with_content.append(temp_dict)
        
        task_prompt = f"Your task is to debug the error by modifying project files or executing commands based on the error debugging steps. The error must be fully resolved. All code must be complete, and the files must be ready to execute without requiring further edits."
        related_files_prompt = f"Files that need to be checked or edited to correctly debug the error: {depended_files}"
        output_format = """List of steps in YAML format. No extra words or markdowns. The type of actions must be either 'Edit code' or 'commande'. All code provided must be complete and runnable with no missing sections or placeholders (e.g., avoid '...' or incomplete code blocks)."""
        exemple_output = f"""
        Debugging steps:

            -   type: "Edit code"
                file_name: "{self.file_name}.py"
                content: |
                    def example_function():
                        print("This is a complete code snippet without missing sections.")

            -   type: "commande"
                content: |
                    python D:\\salem\\application\\past.py # put the full path dont use relative paths
        """

        actions_yaml_text_= self.llm_client.bard(f"**Your Role** : {self.role_prompt} \n \n **Context** : {context} . \n \n **Your Task** : {task_prompt} \n \n **related files** : {related_files_prompt}  **output_format** : {output_format} \n \n **exemple_output** : {exemple_output}") 
        actions_yaml_text = self.llm_client.extract_substring(actions_yaml_text_,"```yaml","```")
        status = self.validate_yaml(actions_yaml_text)

        while not status :
            actions_yaml_text = self.llm_client.bard(f"**Your Role** : {self.role_prompt} \n \n **Context** : {context} . \n \n **Your Task** : {task_prompt} \n \n **related files** : {related_files_prompt}  **output_format** : {output_format} \n \n **exemple_output** : {exemple_output}") 
            status = self.validate_yaml(actions_yaml_text)
            print("we are in while loop")            
        actions_yaml_obj = yaml.safe_load(actions_yaml_text)
        actions = []
        print(actions_yaml_obj)
        for step in actions_yaml_obj.get('Debugging steps', []):
            type= step['type']
            if type == "commande":
                action = {
                    "type" : type,
                    "content" : step['content']
                }
            else : 
                action = {
                    "type" : type,
                    "file_name" : step['file_name'],
                    "content" : step['content']
                }
         
            actions.append(action)
        return actions
    
    def execute_action(self, action):
        if action["type"] == "commande" :
            content = action["content"]
            success, notes = self.skloton_manager.run_batch_code(content)
            action_summury = self.llm_client.bard(f"summerize shortly this command output \n command : {content} \n `\n output = {notes} ")
        else : 

            content = action["content"]
            file_name = action["file_name"]
            pattern = r"[^\\/]+\.py$"

            # Search for the pattern
            match = re.search(pattern, file_name)


            if match:
                file_name = match.group(0)
                print(file_name) 
            else:
                print("No file_name match found.")
                
            file_path = self.skloton_manager.find_path(file_name)
            print(f"over write in {file_path}")
            old_content = self.skloton_manager.get_file_content(file_path)
            self.skloton_manager.overwrite_file(file_path,content)
            action_summury = self.llm_client.bard(f"summerize shortly this modification in the {file_name} code : \n \n old code : {old_content} \n `\n new code = {content} ")
        
        return action_summury
    
    def log_step(self,action_rapport):
        step_log = {
            "debugging step" : f"{self.step}",
            "error" : f"{self.error}",
            "debugging step rapport" : f"{action_rapport}"
        }
        self.logs.append(step_log)

    def retrive_logs_by_error(self, error_value):
        # Filter logs based on the provided error value
        filtered_logs = [log for log in self.logs if log.get("error") == error_value]
        return filtered_logs
  
    def debug(self):
        
        print(self.file_path)
        success , error = self.skloton_manager.execute_python_file(self.file_path)
        print(success)
        while  success and self.step < 15 : 
            print(f"--------------DEBUG_STEP {self.step}----------------------")
            if self.error == error:
                previous_solutions = self.retrive_logs_by_error(error)
                print(f"this error is reapeaeringg : {error}")
            else : 
                self.error = error
                previous_solutions = None
            print("inter to get depended files")
            depended_files = self.get_depended_files()
            print("inter to gennerate actions")
            actions = self.genrerate_actions(depended_files,previous_solutions)
            print(actions)
            i=0
            step_actions_rapport = []

            for action in actions :
                print("enter to execute")
                feed_back = self.execute_action(action)
                log = {
                    "action_num" : f"action {i}",
                    "rapport" : f"{feed_back}"
                }
                step_actions_rapport.append(log)
                print(log)
                i += 1

            self.log_step(step_actions_rapport)
            success , error = self.skloton_manager.execute_python_file(self.file_path)
            
            self.step += 1

        return success
    


    

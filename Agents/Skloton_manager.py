import os
import re
import shutil
import subprocess
import tempfile


class Skloton_manager:
    def __init__(self,app_root,llm_client) :
        self.app_root = app_root
        self.basic_app_root = r"D:\app_with_auth"
        self.llm_client = llm_client

    def get_project_skeleton(self) -> dict:

        def build_skeleton(path):
            # Dictionary to hold the structure of the current folder
            skeleton = {}
            
            # Iterate over all files and directories in the current directory
            for item in os.listdir(path):
                item_path = os.path.join(path, item)
                
                # Skip directories named 'venv' or '__pycache__'
                if item in ['venv', '__pycache__']:
                    continue
                
                if os.path.isdir(item_path):
                    # If it's a directory, recurse into it and add its structure
                    skeleton[item] = build_skeleton(item_path)
                else:
                    # If it's a file, just add it to the dictionary
                    skeleton[item] = None
                    
            return skeleton
        
        # Build the folder skeleton starting from the given directory
        project_skeleton = build_skeleton(self.app_root)
        
        return project_skeleton

    def find_path(self, file_name):

        # Traverse the directory tree starting at 'root'
        for dirpath, dirnames, filenames in os.walk(self.app_root):
            if file_name in filenames:
                # If the file is found, return the full path
                return os.path.join(dirpath, file_name)
        
        # If the file was not found, return None
        return None
    
    def get_file_content(self,filepath):
        try:
            with open(filepath, 'r') as file:
                # Read the file content and return it
                content = file.read()
            return content
        except FileNotFoundError:
            return "File not found."
        except Exception as e:
            return f"An error occurred: {e}"
    
    def create_min_app(self):
        # Create the full path for the new app
        new_app_path = self.app_root
        
        # Check if the directory already exists
        if not os.path.exists(new_app_path):
            # Create the directory with the given app name
            os.makedirs(new_app_path)
            print(f"Directory created at {self.app_root}")
            # Move (or copy) the contents of basic_app_root to the newly created folder
            try:
                for item in os.listdir(self.basic_app_root):
                    s = os.path.join(self.basic_app_root, item)
                    d = os.path.join(new_app_path, item)
                    if os.path.isdir(s):
                        shutil.copytree(s, d)
                    else:
                        shutil.copy2(s, d)
                print(f"Contents of '{self.basic_app_root}' moved to '{new_app_path}'")
            except Exception as e:
                print(f"An error occurred while moving files: {e}")
        else:
            print(f"Directory  already exists at {self.app_root}")

    def init_env(self,all_dependencies,stack):
        prompt_dep = f"from this dict identify what python libraris should install \n the project keywords : {all_dependencies} , {stack} ; return only unique python libraries (dont repeat exesting ones) \n output format : return  **only** a list of python libraries ( dont give many suggesions libs about the same func just give only one)"
        dep = self.llm_client.bard(prompt_dep)
        env_prompt = f"""Generate a .bat file that  hundle this logic: 
        this the app root : **{self.app_root}**
        python libraris : {dep} 
        logic : 
        - cd the app directory 
        -create virtual env 
        -Upgrade pip, setuptools, and wheel using python -m pip : (python -m pip install --upgrade pip setuptools wheel)
        -install dependencies in virtual env created ( pip install every dependencies identified ) PS : install each library alone and ignore in case of error in instalation , exemple : pip install package-A , pip install package-B ; in case package failed installing ignore it and package-B should be installed
        -create requirements.txt and fill it with dependencies installed
        output Format :  .bat file content
        Advices : 
        - Quotes Around Paths: Ensuring paths with spaces are handled correctly by adding quotes around %APP_ROOT% and the activation path.

        - Error Handling: Added checks after each major step to exit the script if something goes wrong.

        - Correct Activation: Used call to ensure that the activation of the virtual environment works correctly in the batch file context.
        """
        bach = self.llm_client.bard(env_prompt)
        bach_cleaned = self.llm_client.extract_substring(bach,'```batch','```')
        bach_cleaned = bach_cleaned.replace("pause","")
        test_bat = "exit /b \n" + bach_cleaned
        success, notes = self.run_batch_code(test_bat)

        print(success)

        while not success :
            bach = self.llm_client.bard(env_prompt)
            bach_cleaned = self.llm_client.extract_substring(bach,'```batch','```')
            test_bat = "exit /b \n" + bach_cleaned
            success, notes = self.run_batch_code(test_bat)
            print(success)

        print("start execution")
        success, notes = self.run_batch_code(bach_cleaned)
        sumerized_feedback = self.llm_client.bard(f"in the context of executing .bat file  sumerize the output of the execution : {notes}")
        return success, sumerized_feedback

    def run_batch_code(self, bat_code):
        # Path to the virtual environment activation script
        venv_activate_script = os.path.join(self.app_root, 'venv', 'Scripts', 'activate')

        # Check if the virtual environment activation script exists
        if os.path.exists(venv_activate_script):
            # Prepend activation command to batch code
            bat_code = f'call "{venv_activate_script}"\n{bat_code}'

        # Create a temporary file
        with tempfile.NamedTemporaryFile(suffix=".bat", delete=False, mode='w', encoding='utf-8') as temp_bat_file:
            temp_bat_path = temp_bat_file.name
            # Write the batch code to the temp file
            temp_bat_file.write(bat_code)

        try:
            # Run the .bat file and capture the output
            result = subprocess.run(
                temp_bat_path, shell=True, capture_output=True, text=True
            )

            # Check return code to determine success or failure
            success = result.returncode == 0

            # Capture any output or error messages
            notes = result.stdout if success else result.stderr

            return success, notes

        finally:
            # Delete the temp file after execution
            if os.path.exists(temp_bat_path):
                os.remove(temp_bat_path)
        
    def overwrite_file(self, file_path, content):
        try:
            # Ensure the directory exists
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            # Open the file in write mode to overwrite its content
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(content)
            
            return 1

        except IOError as e:
            return f"Error: An IOError occurred while writing to the file '{file_path}'. Details: {e}"
        except Exception as e:
            return f"Error: An unexpected error occurred. Details: {e}"

    def execute_python_file(self, file_path):
        try:
            # Run the Python file using subprocess, capture the output and errors
            result = subprocess.run(['python', file_path], capture_output=True, text=True)

            # If the return code is 0, the execution was successful
            if result.returncode == 0:
                print(result.stderr)
                return True, result.stderr
            else:
                # If there was an error, return status 0 and the error message
                print("13")
                return False, result.stderr

        except Exception as e:
            # If an exception occurs, return status 0 and the error message
            return False, str(e)
            
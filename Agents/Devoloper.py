class Devoloper : 
    def __init__(self,technologie_used,llm_client) :
        self.llm_client = llm_client
        self.technologie_used = technologie_used

    def create_model(self,table,project_skolton,table_details,related_tables):
        context_prompt = f"""you are an flask developer expert ; you are working on a project with flask, this is the application technologie_used : {self.technologie_used} ; \n \n this is the project skoloton : {project_skolton}"""
        specification_prompt = f"""only focusing on {table}.py """
        task_prompt = f"""task : give me the content of the file {table}.py based on this table details : {table_details} \n \n you may need those tables  {related_tables}"""
        
        output_format_prompt = """output format : ONLY Code """
        code = self.llm_client.bard(f"**context**:{context_prompt} \n \n specification :{specification_prompt} \n \n task :{task_prompt} \n \n output_format: {output_format_prompt}" )

        clean_code = self.llm_client.extract_substring(code,'```python','```')
        return clean_code


    def create_role_enum(self,user_roles,project_skolton):
        context_prompt = f"""im working in a project with flask, this is the application technologie_used : {self.technologie_used} ; \n \n this is my project skoloton : {project_skolton}"""
        specification_prompt = f"""only focusing on creating Roles Enum """
        task_prompt = f"""task : give me the content of the file roles.py based on this roles details : {user_roles} \n \n """

        output_format_prompt = """output format : ONLY Code """
        code = self.llm_client.bard(f"**context**:{context_prompt} \n \n specification :{specification_prompt} \n \n task :{task_prompt} \n \n output_format: {output_format_prompt}" )

        clean_code = self.llm_client.extract_substring(code,'```python','```')
        return clean_code

    def syncro_with_auth(self,super_user_code,roles_code) :
        task_prompt = f""" your task is a correct a little mistake in user.py ( that i will provide)
        change only this line in user.py ** roles = me.ListField(me.StringField(choices=[role.value for role in RoleEnum]), default=[RoleEnum.USER.value])**
        set the default=[RoleEnum.USER.value] into existing value in the roles enum .
        -user.py : {super_user_code} 
        -roles.py : {roles_code}
        you must return all the code of user.py (must be runnable)

    """

        output_format_prompt = """output format : ONLY Code """
        code = self.llm_client.bard(f"task :{task_prompt} \n \n output_format: {output_format_prompt}" )

        clean_code = self.llm_client.extract_substring(code,'```python','```')
        return clean_code
    def get_ordre_generating_model(self,database_schema)  : 
        prompt = f"""for this database schema : {database_schema}: give me the write order to create this database , some tables must be created before other that are dipended by them ( FK)
        task : ordre tables from the first must be created to the last
        output format : tables of tables name 
        output exemple : [user,goal,annimation,house,...] no extra words or markdown
        """
        resp = self.llm_client.bard(prompt)
        resp_cleaned = self.llm_client.extract_substring(resp,'[',']')
        ordre = resp_cleaned.split(',')
        return ordre
    
    def code_crud_test_model(self,project_skolton,table,table_code ,  related_code):
        def build_prompt(project_skolton,table,table_code ,  related_code) :
            context_prompt = f"you are an expert devoloper specialist in {self.technologie_used} and you are working on this project : {project_skolton} \n \n"
            task = f"your task is creating a crud ( create , read,update,delete) test using pytest to test this model :{table} code : {table_code}  \\ there is a list of Models code you can check in case you needed one of them to create a working code test : models list : {related_code} \n \n"
            outputformat = "output format : ONLY Code"
            prompt = context_prompt + task + outputformat
            return prompt
        


        prompt = build_prompt(project_skolton,table,table_code ,related_code)
        code =  self.llm_client.bard(prompt)
        code = self.llm_client.extract_substring(code,'```python','```')

        return code

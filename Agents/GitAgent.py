import os
import git
from git import Repo

class GitAgent:
    def __init__(self, repo_path):
        
        self.repo_path = repo_path
        if not os.path.exists(repo_path):
            os.makedirs(repo_path)
        self.repo = None
    
    def init_git(self):
       
        if os.path.exists(os.path.join(self.repo_path, '.git')):
            print("Repository already initialized.")
            self.repo = Repo(self.repo_path)
        else:
            print("Initializing new git repository...")
            self.repo = Repo.init(self.repo_path)
            print(f"Initialized empty Git repository in {self.repo_path}")
    
    def commit(self, message):
   
        if self.repo is None:
            raise Exception("Repository not initialized. Call init_git first.")
        
        # Stage all changes
        self.repo.git.add(A=True)
        
        # Commit with message
        try:
            commit = self.repo.index.commit(message)
            print(f"Committed changes: {commit.hexsha}")
        except Exception as e:
            print(f"Error committing changes: {e}")
    
    def rollback_to_previous_commit(self):

        if self.repo is None:
            raise Exception("Repository not initialized. Call init_git first.")
        
        # Check if there's at least one commit to roll back to
        if len(list(self.repo.iter_commits())) < 2:
            print("No previous commit to roll back to.")
            return

        try:
            # Rollback to the previous commit (reset HEAD to HEAD~1)
            self.repo.git.reset('--hard', 'HEAD~1')
            print("Rolled back to the previous commit.")
        except Exception as e:
            print(f"Error rolling back to previous commit: {e}")


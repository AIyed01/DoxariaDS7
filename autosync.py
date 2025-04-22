import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from git import Repo
import os

class GitAutoSync(FileSystemEventHandler):
    def __init__(self, repo_path):
        self.repo = Repo(repo_path)
        self.branch = "walid"  

    def on_modified(self, event):
        self.sync_changes()

    def on_created(self, event):
        self.sync_changes()

    def sync_changes(self):
        try:
            self.repo.git.add('--all')
            if self.repo.git.diff('--cached'):
                self.repo.git.commit('-m', f"Auto-commit: {time.ctime()}")
                self.repo.git.push('origin', self.branch)
                print(f"Pushed to {self.branch}!")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    path = os.getcwd()
    event_handler = GitAutoSync(path)
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()
    print(f"Watching '{path}' for changes...")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

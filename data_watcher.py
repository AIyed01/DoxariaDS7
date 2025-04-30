import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import os
from nbconvert import PythonExporter
import nbformat

# Paths (use raw strings for Windows paths)
data_path = r"C:\Users\walid\Downloads\DSPI\data_doxaria"
notebook_path = r"C:\Users\walid\Downloads\DSPI\DoxariaDS7\classificationfinal.ipynb"

class NotebookRunner(FileSystemEventHandler):
    def on_modified(self, event):
        if not event.is_directory:  # Only react to file changes
            print(f"Dataset changed: {event.src_path}")
            self.run_notebook()

    def run_notebook(self):
        try:
            # Convert notebook to Python and execute
            with open(notebook_path) as f:
                nb = nbformat.read(f, as_version=4)
            
            exporter = PythonExporter()
            python_code, _ = exporter.from_notebook_node(nb)
            
            exec(python_code, globals())
            print("Notebook executed successfully!")
            
        except Exception as e:
            print(f"Error executing notebook: {e}")

if __name__ == "__main__":
    event_handler = NotebookRunner()
    observer = Observer()
    observer.schedule(event_handler, data_path, recursive=True)
    observer.start()
    print(f"Watching for dataset changes in: {data_path}")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
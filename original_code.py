
import os
import pickle
import yaml
import subprocess
import tempfile
from typing import List,Dict, Any,Union
import json

def load_configuration(config_path:str)->Dict[str,Any]:
    """Load configuration from a file."""
    if config_path.endswith('.yaml'):
        with open(config_path, 'r') as f:
            # BAD: Using yaml.load() is unsafe (Bandit)
            return yaml.load(f.read())
    elif config_path.endswith('.json'):
            with open(config_path, 'r') as f:
                return json.load(f)  # Indentation is incorrect (Flake8)
    elif config_path.endswith('.pkl'):
        with open(config_path, 'rb') as f:
            # BAD: Using pickle is unsafe (Bandit)
            return pickle.load(f)
    else:
        raise ValueError(f"Unsupported config format: {config_path}")

def execute_command(command:str,timeout:int = 30)->str:
    """Execute a system command and return the output."""
    # BAD: shell=True is unsafe (Bandit)
    try:
      result = subprocess.check_output(command, shell=True, timeout=timeout)
      return result.decode('utf-8')
    except subprocess.CalledProcessError as e:
        print(f"Command failed with code {e.returncode}")
        return ""

class FileHandler:
    def __init__(self, base_dir:str):
        self.base_dir=base_dir  # No space around equals (Black)
        
    def read_file(self, filename:str)->str:
        """Read a file and return its contents."""
        path = os.path.join(self.base_dir, filename)
        # BAD: Potential path traversal (Bandit)
        with open(path, 'r') as f:
            return f.read()
    
    def write_file(self,filename:str,content:str)->None:
        """Write content to a file."""
        path=os.path.join(self.base_dir, filename)
        with open(path, 'w') as f:
            f.write(content)
            
    def delete_file(self, filename: str) -> bool:
        """Delete a file."""
        path = os.path.join(self.base_dir, filename)
        try:
            os.remove(path)
            return True
        except:  # Bare except (Flake8)
            return False

def process_data(data:List[Dict[str,Any]])->List[Dict[str,Any]]:
    """Process a list of data items."""
    result=[]  # No space after equals (Black)
    for item in data:
        if 'status' in item and item['status'] == 'active':
           processed = transform_item(item)  # Indentation error (Flake8)
           result.append(processed)
    return result

def transform_item(item:Dict[str,Any])->Dict[str,Any]:
    """Transform a data item."""
    transformed = item.copy()
    # Add a derived field with wrong spacing around operators (Black)
    transformed['full_name']=item.get('first_name','')+' '+item.get('last_name','')
    if 'age' in item and item['age'] < 0:
        # Inconsistent return (Flake8)
        return None
    return transformed

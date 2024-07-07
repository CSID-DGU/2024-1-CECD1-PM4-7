import json
from pathlib import Path
import tkinter as tk
from tkinter import filedialog
import time

project_dir = Path(__file__).resolve().parent.parent.parent
key_folder = project_dir / 'key'


# prompt
def getPrompt(type: str):
    promptPath = str(key_folder / 'prompt.json')
    with open(promptPath, 'r', encoding='utf-8') as f:
        prompt_data = json.load(f)
    prompt = prompt_data[type]
    return prompt


# get model name
def getModelName(type: str):
    modelPath = str(key_folder / 'model.json')
    with open(modelPath, 'r', encoding='utf-8') as f:
        model_data = json.load(f)
    model_name = model_data[type]
    return model_name

# update model name
def updateModelName(type: str, new_model_name: str):
    modelPath = str(key_folder / 'model.json')
    with open(modelPath, 'r', encoding='utf-8') as f:
        model_data = json.load(f)
    model_data[type] = new_model_name
    with open(modelPath, 'w', encoding='utf-8') as f:
        json.dump(model_data, f, ensure_ascii=False, indent=4)

# directory
def open_dialog(isfolder: bool, title="선택", filetypes=None, delay=0.0) -> Path:
    if filetypes is None:
        filetypes = [("All Files", "*.*")]
    time.sleep(delay)
    root = tk.Tk()
    root.withdraw()
    root.lift()
    root.attributes('-topmost', True)
    root.title(title)
    if isfolder:
        path = filedialog.askdirectory()
    else:
        path = filedialog.askopenfilename(filetypes=filetypes)
    root.attributes('-topmost', False)
    root.destroy()
    return Path(path)

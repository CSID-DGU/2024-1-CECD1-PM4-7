import os


def openAIAuth():
    current_dir = os.path.abspath(__file__)
    key_path = os.path.join(current_dir, '..', '..', '..', 'key', 'GPT_3.5_key')
    with open(key_path, 'r') as f:
        return f.read()
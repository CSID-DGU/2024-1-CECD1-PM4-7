"""
main에서 진행하는 것들
1. OpenAI Auth
2. Converting STT or Real input
3. training
4. Evaluation
"""
import os
import sys
authPath = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(authPath)
import auth

# Auth
key = auth.openAIAuth()
print(key)

# Convert

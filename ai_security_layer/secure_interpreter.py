# from interpreter import interpreter
from .security_layer import security_check
from .state_guard import StateGuard
import os
# # 🔥 CONFIGURATION
# interpreter.auto_run = True
# interpreter.llm.model = "ollama/llama3"

import string

def find_files_in_prompt(prompt):
    extensions = [".txt", ".py", ".c", ".sh", ".csv", ".rtf"]
    words = prompt.split()
    
    result = []
    for w in words:
        # Remove trailing punctuation like .,!?;:
        w_clean = w.rstrip(string.punctuation)
        if any(w_clean.endswith(ext) for ext in extensions):
            result.append(w_clean)
    return result

def find_file_contents(filename):
    if os.path.isfile(filename):
        file = open(filename, "r")
        content = file.read()
        return content 
    else:
        print(f"DEBUG: {filename} is not a file")
        return None 

def can_execute(result):
    # Step 2: State Guard
    guard = StateGuard()
    state = guard.transition(result)
    print(f"[STATE] → {state}")

    # Step 3: Decision
    if not guard.can_execute():
        return False
    return True

def run_secure_prompt(prompt, interpreter):
    print(f"\n🧑 User Input: {prompt}")

    # Scan the prompt for safety, as well as any files mentioned inthe prompt 
    
    # Step 1: Security Check for prompt
    result_prompt_only = security_check(prompt)
    print(f"[DEBUG] User Prompt Label: {result_prompt_only['label']}, Confidence: {result_prompt_only['confidence']} ({result_prompt_only['source']})")
    
    if not can_execute(result_prompt_only):
        print(f"❌ BLOCKED: Unsafe or uncertain prompt")
        return

    # Repeat for files with potential indirect injection 
    filenames = find_files_in_prompt(prompt)
    print(f"[DEBUG] Detected filenames: {filenames}")

    for filename in filenames:
        file_contents = find_file_contents(filename)
    
        if file_contents:
            result_file_contents = security_check(file_contents)

            print(f"[DEBUG] File {filename} Label: {result_file_contents['label']}, Confidence: {result_file_contents['confidence']} ({result_file_contents['source']})")
            if not can_execute(result_file_contents):
                print(f"❌ BLOCKED: Unsafe or uncertain file: {filename}")
                return
        else:
            print(f"[DEBUG] Could not get file contents for file {filename}")

    print("✅ SAFE → Sending to Open Interpreter...\n")

    # Step 4: Execute
    try:
        response = interpreter.chat(prompt)
        print("🤖 Interpreter Output:\n", response)

    except Exception as e:
        print("⚠️ Execution Error:\n", str(e))


if __name__ == "__main__":
    while True:
        user_input = input("\nEnter prompt (or 'exit'): ")

        if user_input.lower() == "exit":
            break

        run_secure_prompt(user_input)
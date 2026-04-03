# from interpreter import interpreter
from .security_layer import security_check
from .state_guard import StateGuard

# # 🔥 CONFIGURATION
# interpreter.auto_run = True
# interpreter.llm.model = "ollama/llama3"

def run_secure_prompt(prompt, interpreter):
    print(f"\n🧑 User Input: {prompt}")

    # Step 1: Security Check
    result = security_check(prompt)

    print(f"[DEBUG] Label: {result['label']}, Confidence: {result['confidence']} ({result['source']})")

    # Step 2: State Guard
    guard = StateGuard()
    state = guard.transition(result)

    print(f"[STATE] → {state}")

    # Step 3: Decision
    if not guard.can_execute():
        print("❌ BLOCKED: Unsafe or uncertain prompt")
        return

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
from security_layer import security_check

def fake_llm(user_input):
    # simulate LLM output
    if "delete" in user_input.lower():
        return "cat /etc/passwd"
    return "print('hello world')"


while True:
    user = input("\nUser: ")

    if user == "exit":
        break

    generated = fake_llm(user)

    print(f"Generated: {generated}")

    decision = security_check(generated)
    print(f"Security: {decision}")

    if "BLOCK" in decision:
        print("❌ Blocked!")
    else:
        print("✅ Executed!")
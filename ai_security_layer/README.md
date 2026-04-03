# 🔐 Secure AI Layer for Tool-Using Agents

## 📌 Overview

This project introduces a **security enforcement layer** for AI agents built on top of Open Interpreter.

Modern AI agents can execute code, access files, and run system commands. While powerful, this introduces significant security risks.

This system mitigates those risks by inserting a **pre-execution security layer** that evaluates user input before allowing execution.

---

## 🧠 Motivation

Tool-augmented AI agents (like Open Interpreter) can:

- Execute Python code
- Run shell commands
- Access system resources

However, they **lack built-in security controls**, making them vulnerable to:

- Prompt injection attacks
- Malicious command execution
- Data exfiltration

This project addresses that gap.

---

## 🏗️ Architecture
# 🔐 Secure AI Layer for Tool-Using Agents

## 📌 Overview

This project introduces a **security enforcement layer** for AI agents built on top of Open Interpreter.

Modern AI agents can execute code, access files, and run system commands. While powerful, this introduces significant security risks.

This system mitigates those risks by inserting a **pre-execution security layer** that evaluates user input before allowing execution.

---

## 🧠 Motivation

Tool-augmented AI agents (like Open Interpreter) can:

- Execute Python code
- Run shell commands
- Access system resources

However, they **lack built-in security controls**, making them vulnerable to:

- Prompt injection attacks
- Malicious command execution
- Data exfiltration

This project addresses that gap.

---

## 🏗️ Architecture
User Input
↓
Security Layer (Rules + ML)
↓
StateGuard (Decision Engine)
↓
Open Interpreter (Agent)
↓
Tools (Python / Shell / Files)



---

## 🔒 Key Components

### 1. Security Layer (`security_layer.py`)
- Hybrid detection system:
  - Rule-based filtering (keywords like `rm -rf`, `sudo`, etc.)
  - ML-based classification (SAFE / DANGEROUS)
- Handles uncertain predictions using confidence thresholds

---

### 2. StateGuard (`state_guard.py`)
Implements a simple state machine:

| State      | Description |
|-----------|------------|
| INIT       | Initial state |
| VERIFIED   | Safe to execute |
| BLOCKED    | Unsafe or uncertain |

---

### 3. Secure Interpreter (`secure_interpreter.py`)
- Main entry point
- Integrates:
  - Security layer
  - StateGuard
  - Open Interpreter
- Controls execution flow

---

### 4. Config (`config.py`)
- Confidence thresholds
- Dangerous keyword definitions

---

## ⚙️ Features

- ✅ Blocks dangerous commands before execution
- ✅ Hybrid security (Rule-based + ML)
- ✅ State-based execution control
- ✅ Supports local LLM (via Ollama)
- ✅ Works with Open Interpreter tools (Python, Shell)

---

## 🚀 Setup

### 1. Clone repository

```bash
git clone https://github.com/ghadashaqra/ai-security-layer.git
cd ai-security-layer

### 2. Create virtual environment
python -m venv .venv

### 3. Create virtual environment
pip install -r requirements.txt

### 4. (Optional) Run local LLM with Ollama
brew install ollama
ollama run llama3

### 5. Run the system
python secure_interpreter.py

Examples:
Input: What is artificial intelligence?
Output:
[STATE] → VERIFIED
→ Executed successfully


Input: Delete all system files
Output:
[STATE] → BLOCKED
❌ Execution blocked

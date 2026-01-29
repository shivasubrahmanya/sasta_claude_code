import subprocess
import json
import os
from openai import OpenAI

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

SYSTEM_PROMPT = """
You are a coding agent.

You MUST respond ONLY with valid JSON.
NO explanations. NO markdown.

Allowed actions:

1. read_file
   {"action":"read_file","path":"..."}

2. write_file
   {"action":"write_file","path":"...","content":"..."}

3. edit_file
   {"action":"edit_file","path":"...","old":"...","new":"..."}

4. bash
   {"action":"bash","command":"..."}

5. done
   {"action":"done","message":"..."}

Rules:
- Use tools step by step
- Observe outputs
- Finish only when task is complete
"""

def read_file(path):
    if not os.path.exists(path):
        return f"ERROR: {path} does not exist"
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def write_file(path, content):
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return f"File written: {path}"

def edit_file(path, old, new):
    if not os.path.exists(path):
        return f"ERROR: {path} does not exist"

    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    count = content.count(old)
    if count == 0:
        return "ERROR: target text not found"
    if count > 1:
        return "ERROR: target text not unique"

    content = content.replace(old, new)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

    return f"Edited file: {path}"

BLOCKED = ["rm", "del", "rmdir", "shutdown", "format"]

def run_bash(command):
    for bad in BLOCKED:
        if bad in command.lower():
            return f"ERROR: blocked command -> {bad}"

    result = subprocess.run(
        command,
        shell=True,
        capture_output=True,
        text=True
    )
    return result.stdout + result.stderr

def execute_tool(action):
    name = action["action"]

    if name == "read_file":
        return read_file(action["path"])
    if name == "write_file":
        return write_file(action["path"], action["content"])
    if name == "edit_file":
        return edit_file(action["path"], action["old"], action["new"])
    if name == "bash":
        return run_bash(action["command"])

    return "ERROR: unknown action"

def run_agent(task):
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": task}
    ]

    while True:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0
        )

        ai_text = response.choices[0].message.content
        messages.append({"role": "assistant", "content": ai_text})

        try:
            actions = json.loads(ai_text)
            if isinstance(actions, dict):
                actions = [actions]
        except:
            print("❌ Invalid JSON:")
            print(ai_text)
            break

        for action in actions:
            if action["action"] == "done":
                print("✅", action["message"])
                return

            print("🔧 Action:", action)
            output = execute_tool(action)
            print("📤 Output:\n", output)

            messages.append({
                "role": "user",
                "content": f"Tool output:\n{output}"
            })

if __name__ == "__main__":
    run_agent("Create a Python script with a subtle bug, write a failing test, then fix the bug so the test passes")

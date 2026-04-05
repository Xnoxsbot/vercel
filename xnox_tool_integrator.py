
import os
import json
import re

# Simple, flat function to avoid 'unexpected indent' errors in Xnox
def scan_repository():
    repo_path = "."
    registry = {}
    extensions = ['.ts', '.tsx', '.js', '.jsx']
    signatures = {
        "generate_text": r"generateText\(",
        "stream_text": r"streamText\(",
        "use_chat": r"useChat\(",
        "embed": r"embed\(",
        "tool_call": r"tool\("
    }

    print(f"Starting Xnox scan in: {os.path.abspath(repo_path)}")
    found_count = 0

    for root, dirs, files in os.walk(repo_path):
        if 'node_modules' in dirs:
            dirs.remove('node_modules')
        
        for file in files:
            if any(file.endswith(ext) for ext in extensions):
                path = os.path.join(root, file)
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        for name, pattern in signatures.items():
                            if re.search(pattern, content):
                                tool_id = f"vercel_{name}"
                                registry[tool_id] = {"file": path, "type": "ts_module"}
                except:
                    continue
                found_count += 1

    # Create the memory file for Xnox
    manifest = {
        "tools": registry,
        "instruction": "Use these TS patterns for building websites."
    }
    
    with open("xnox_manifest.json", "w") as f:
        json.dump(manifest, f, indent=4)
    
    print(f"Success! Registered {len(registry)} tools.")
    return len(registry)

if __name__ == "__main__":
    scan_repository()


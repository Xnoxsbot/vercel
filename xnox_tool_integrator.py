
import os
import json
import re

class XnoxToolIntegrator:
    """
    A robust patch for Xnox to handle TypeScript/JavaScript monorepos 
    like the Vercel AI SDK which were previously returning '0 tools'.
    """
    def __init__(self, repo_path="."):
        # Default to current directory if running inside the repo
        self.repo_path = repo_path
        self.registry = {}
        self.supported_extensions = ['.ts', '.tsx', '.js', '.jsx']
        
        # Patterns to identify Vercel AI SDK capabilities
        self.signatures = {
            "generate_text": r"generateText\(",
            "stream_text": r"streamText\(",
            "use_chat": r"useChat\(",
            "embed": r"embed\(",
            "tool_call": r"tool\("
        }

    def scan_repository(self):
        """Recursively scans the forked repo for AI SDK patterns."""
        print(f"--- Xnox Deep Scan Starting: {os.path.abspath(self.repo_path)} ---")
        found_count = 0
        
        for root, dirs, files in os.walk(self.repo_path):
            # Skip common noise folders
            if 'node_modules' in dirs:
                dirs.remove('node_modules')
            if '.git' in dirs:
                dirs.remove('.git')
            
            for file in files:
                if any(file.endswith(ext) for ext in self.supported_extensions):
                    file_path = os.path.join(root, file)
                    self._process_file(file_path)
                    found_count += 1
        
        self._generate_tool_manifest()
        return found_count

    def _process_file(self, path):
        """Analyzes file content to map SDK functions to Xnox tools."""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
                
                # Identify which SDK features are present
                for tool_name, pattern in self.signatures.items():
                    if re.search(pattern, content):
                        module_name = os.path.basename(path).split('.')[0]
                        tool_id = f"vercel_{module_name}_{tool_name}"
                        
                        self.registry[tool_id] = {
                            "source_file": path,
                            "type": "typescript_sdk_module",
                            "capability": tool_name,
                            "status": "ready_for_execution"
                        }
        except Exception:
            pass

    def _generate_tool_manifest(self):
        """Creates the manifest file that Xnox reads to 'learn' the skills."""
        manifest_path = os.path.join(self.repo_path, "xnox_manifest.json")
        
        # Convert identified SDK logic into Xnox-readable instructions
        data = {
            "version": "1.0.0",
            "engine_override": "TS_ENABLED",
            "discovered_tools": self.registry,
            "instructions": [
                "When user asks for 'AI', 'Chat', or 'Streaming', use 'ai/react' patterns found in registry.",
                "Execute TypeScript logic via Node.js runtime instead of Python interpreter.",
                "Map useChat() parameters to internal Xnox message state."
            ]
        }
        
        with open(manifest_path, 'w') as f:
            json.dump(data, f, indent=4)
        
        print(f"Successfully injected {len(self.registry)} new tool capabilities into Xnox.")
        print(f"Manifest saved to: {manifest_path}")

# --- Execution ---
if __name__ == "__main__":
    # Initialize the integrator on the current path
    patch = XnoxToolIntegrator()
    
    # Run the scan to fix the '0 tools' issue
    count = patch.scan_repository()
    
    if count > 0:
        print(f"\n✅ XNOX STATUS: UPGRADED ({count} files analyzed)")
        print("Xnox can now 'see' the Vercel SDK logic.")
    else:
        print("\n❌ Error: No compatible files found. Check the path.")


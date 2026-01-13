import os
import json
import subprocess
import sys
import glob
from typing import Dict, List, Any

CHECKERS = {
    "mypy": ["mypy"],
    "pyrefly": ["pyrefly", "check"],
    "zuban": ["zuban", "check"],
    "ty": ["ty", "check"]
}

BASE_GEN_DIR = "generated_examples"

def get_latest_generation_dir() -> str:
    """Finds the most recent timestamped folder in generated_examples."""
    if not os.path.exists(BASE_GEN_DIR):
        print(f"[ERROR] Directory '{BASE_GEN_DIR}' does not exist.")
        sys.exit(1)
        
    subdirs = [os.path.join(BASE_GEN_DIR, d) for d in os.listdir(BASE_GEN_DIR) 
               if os.path.isdir(os.path.join(BASE_GEN_DIR, d))]
    
    if not subdirs:
        print(f"[ERROR] No generated examples found in '{BASE_GEN_DIR}'.")
        sys.exit(1)
        
    latest = max(subdirs, key=os.path.basename)
    return latest

def run_tool(command: List[str], filepath: str) -> str:
    """Runs a single type checker command on a file."""
    try:
        full_cmd = command + [filepath]
        
        result = subprocess.run(
            full_cmd,
            capture_output=True,
            text=True,
            check=False
        )
        
        output = result.stdout
        if result.stderr:
            output += "\n[STDERR]\n" + result.stderr
            
        return output.strip() if output.strip() else "Success (No Output)"
        
    except FileNotFoundError:
        return f"Error: Command '{command[0]}' not found in PATH."
    except Exception as e:
        return f"Execution Error: {str(e)}"

def main():
    """Finding Python files and run the checkers."""
    target_dir = get_latest_generation_dir()
    source_files_dir = os.path.join(target_dir, "source_files")
    
    if not os.path.exists(source_files_dir):
        print(f"[ERROR] No 'source_files' directory found in {target_dir}")
        sys.exit(1)

    py_files = glob.glob(os.path.join(source_files_dir, "*.py"))
    if not py_files:
        print("[ERROR] No .py files found to check.")
        sys.exit(1)

    print(f"--- Running Type Checkers on {len(py_files)} files ---")
    print(f"Directory: {target_dir}\n")

    all_results = []

    for filepath in py_files:
        filename = os.path.basename(filepath)
        print(f"Checking {filename}...")
        
        file_result = {
            "filename": filename,
            "filepath": filepath,
            "outputs": {}
        }
        
        for tool_name, command in CHECKERS.items():
            # print(f"  > {tool_name}...", end=" ", flush=True)
            output = run_tool(command, filepath)
            file_result["outputs"][tool_name] = output
            # print("Done.")
            
        all_results.append(file_result)

    results_json_path = os.path.join(target_dir, "results.json")
    
    final_output = {
        "timestamp": os.path.basename(target_dir),
        "checkers_used": list(CHECKERS.keys()),
        "results": all_results
    }
    
    with open(results_json_path, "w", encoding="utf-8") as f:
        json.dump(final_output, f, indent=4)

    print(f"\n[SUCCESS] Results saved to: {results_json_path}")

if __name__ == "__main__":
    main()

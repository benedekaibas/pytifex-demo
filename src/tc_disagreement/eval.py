import os
import json
import glob
import sys
from typing import List, Dict
from pydantic import HttpUrl

import time
import random

# Import your existing Gemini Agent class
# Assuming your main pydantic file is named 'agent.py'
try:
    from agent import GetAccessToGemini 
except ImportError:
    # If the import fails, we define a dummy or ask user to fix filename
    print("[ERROR] Could not import GetAccessToGemini. Make sure 'agent.py' exists.")
    sys.exit(1)

BASE_GEN_DIR = "generated_examples"

# We construct the prompt string carefully to avoid breaking the python file formatting
# when displayed in markdown viewers.
TICK = "`" * 3  # Represents the triple backtick

JUDGE_PROMPT_TEMPLATE = f"""
You are an expert Python Static Analysis Judge (PEP 484).
Your goal is to determine if a Type Checker's output is CORRECT or INCORRECT.

### 1. The Source Code
(Pay attention to the logic and any obvious type safety violations)
{TICK}python
{{source_code}}
{TICK}

### 2. The Type Checker Output
Tool Name: {{tool_name}}
Output:
{TICK}text
{{tool_output}}
{TICK}

### 3. Your Task
Determine if the tool's output is **CORRECT** based on strict Python typing rules.
- If the code has a bug/overlap and the tool reports an error -> CORRECT.
- If the code has a bug and the tool says "Success" -> INCORRECT (False Negative).
- If the code is safe and the tool reports an error -> INCORRECT (False Positive).

Reply in this strict format:
VERDICT: [CORRECT/INCORRECT]
REASON: [One sentence explanation]
"""

def get_latest_results_file() -> str:
    """Finds the results.json in the most recent generated folder."""
    if not os.path.exists(BASE_GEN_DIR):
        return None
        
    subdirs = [os.path.join(BASE_GEN_DIR, d) for d in os.listdir(BASE_GEN_DIR) 
               if os.path.isdir(os.path.join(BASE_GEN_DIR, d))]
    
    if not subdirs:
        return None
        
    latest_dir = max(subdirs, key=os.path.basename)
    results_path = os.path.join(latest_dir, "results.json")
    return results_path if os.path.exists(results_path) else None

def evaluate_tool(agent, source_code: str, tool_name: str, output: str) -> Dict:
    """Sends a prompt to Gemini to judge the tool output with Retry Logic."""
    prompt = JUDGE_PROMPT_TEMPLATE.format(
        source_code=source_code,
        tool_name=tool_name,
        tool_output=output
    )
    
    max_retries = 5
    base_delay = 2

    for attempt in range(max_retries):
        try:
            response = agent.predict(prompt)
            
            lines = response.splitlines()
            verdict = "UNKNOWN"
            reason = "Could not parse reason"
            
            for line in lines:
                if line.startswith("VERDICT:"):
                    verdict = line.replace("VERDICT:", "").strip().upper()
                if line.startswith("REASON:"):
                    reason = line.replace("REASON:", "").strip()
                    
            return {"verdict": verdict, "reason": reason}

        except Exception as e:
            error_msg = str(e)
            if "503" in error_msg or "429" in error_msg:
                if attempt < max_retries - 1:
                    sleep_time = (base_delay * (2 ** attempt)) + (random.random() * 0.5)
                    print(f"    [Warn] API Busy (503). Retrying in {sleep_time:.1f}s...")
                    time.sleep(sleep_time)
                    continue
            
            return {"verdict": "ERROR", "reason": f"API Failed: {error_msg}"}

def main():
    # 1. Setup Agent
    token = os.environ.get("GEMINI_API_KEY")
    if not token:
        print("[ERROR] GEMINI_API_KEY not set.")
        return

    # Use Flash for speed
    agent = GetAccessToGemini(
        model="gemini-2.5-flash", 
        token=token,
        api_base=HttpUrl("https://generativelanguage.googleapis.com/v1beta"),
        timeout=30.0,
    )

    # 2. Load Results
    results_path = get_latest_results_file()
    if not results_path:
        print("[ERROR] No results.json found. Run 'run_checkers.py' first.")
        return

    with open(results_path, "r") as f:
        data = json.load(f)

    results = data.get("results", [])
    print(f"--- AI Judge Evaluation on {len(results)} Files ---")
    print(f"Source: {results_path}\n")

    # 3. Evaluation Loop
    tool_stats = {t: {"correct": 0, "total": 0} for t in data.get("checkers_used", [])}

    for file_entry in results:
        filepath = file_entry["filepath"]
        filename = file_entry["filename"]
        
        # Read the source code freshly
        try:
            with open(filepath, "r") as src:
                source_code = src.read()
        except FileNotFoundError:
            print(f"[WARN] Source file not found: {filepath}")
            continue
            
        print(f"Evaluating {filename}...")
        
        for tool, output in file_entry["outputs"].items():
            eval_result = evaluate_tool(agent, source_code, tool, output)
            
            is_correct = "CORRECT" in eval_result["verdict"]
            status_icon = "✅" if is_correct else "❌"
            
            # Update stats
            if tool not in tool_stats: tool_stats[tool] = {"correct": 0, "total": 0}
            tool_stats[tool]["total"] += 1
            if is_correct:
                tool_stats[tool]["correct"] += 1
                
            print(f"  {tool:<10} | {status_icon} {eval_result['verdict']} | {eval_result['reason'][:60]}...")

        print("-" * 60)

    # 4. Final Scorecard
    print("\n" + "="*40)
    print("FINAL TYPE CHECKER LEADERBOARD")
    print("="*40)
    print(f"{'Tool':<15} | {'Accuracy':<10} | {'Score'}")
    print("-" * 40)
    
    for tool, stats in tool_stats.items():
        if stats["total"] > 0:
            acc = (stats["correct"] / stats["total"]) * 100
            print(f"{tool:<15} | {acc:.1f}%      | {stats['correct']}/{stats['total']}")
        else:
            print(f"{tool:<15} | N/A        | 0/0")
    print("="*40)

if __name__ == "__main__":
    main()

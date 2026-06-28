import os
import sys
import subprocess
import re

def get_workspace_dir():
    # Run git to get repo root
    root = subprocess.check_output(['git', 'rev-parse', '--show-toplevel']).decode('utf-8').strip()
    sdd_dir = os.path.join(root, '.superpowers', 'sdd')
    os.makedirs(sdd_dir, exist_ok=True)
    # Ensure ignore file exists
    with open(os.path.join(sdd_dir, '.gitignore'), 'w') as f:
        f.write('*\n')
    return sdd_dir

def task_brief(plan_path, task_num):
    if not os.path.exists(plan_path):
        print(f"Plan file not found: {plan_path}", file=sys.stderr)
        sys.exit(1)
        
    sdd_dir = get_workspace_dir()
    outfile = os.path.join(sdd_dir, f"task-{task_num}-brief.md")
    
    with open(plan_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    # Find heading for the task, e.g. "### Task N:" or "### Task N"
    # We want to extract everything from this heading until the next "### Task M" (where M is a digit)
    lines = content.splitlines()
    task_lines = []
    in_task = False
    in_code_fence = False
    
    # Compile regex to match Task N header (case insensitive, ignoring code fences)
    # Matches: ## Task 1, ### Task 1, # Task 1, etc.
    header_pattern = re.compile(r'^#+\s+Task\s+(\d+)(?:\s|:|$)', re.IGNORECASE)
    
    for line in lines:
        if line.strip().startswith('```'):
            in_code_fence = not in_code_fence
            
        if not in_code_fence:
            m = header_pattern.match(line.strip())
            if m:
                current_num = int(m.group(1))
                if current_num == int(task_num):
                    in_task = True
                elif in_task:
                    # Found another task heading, stop extracting
                    break
        
        if in_task:
            task_lines.append(line)
            
    if not task_lines:
        print(f"Task {task_num} not found in plan", file=sys.stderr)
        sys.exit(1)
        
    with open(outfile, 'w', encoding='utf-8') as f:
        f.write('\n'.join(task_lines) + '\n')
        
    print(f"wrote {outfile}: {len(task_lines)} lines")

def review_package(base, head):
    sdd_dir = get_workspace_dir()
    
    # Get short hashes
    base_short = subprocess.check_output(['git', 'rev-parse', '--short', base]).decode('utf-8').strip()
    head_short = subprocess.check_output(['git', 'rev-parse', '--short', head]).decode('utf-8').strip()
    
    outfile = os.path.join(sdd_dir, f"review-{base_short}..{head_short}.diff")
    
    commits = subprocess.check_output(['git', 'log', '--oneline', f"{base}..{head}"]).decode('utf-8')
    stat = subprocess.check_output(['git', 'diff', '--stat', f"{base}..{head}"]).decode('utf-8')
    diff = subprocess.check_output(['git', 'diff', '-U10', f"{base}..{head}"]).decode('utf-8')
    
    with open(outfile, 'w', encoding='utf-8') as f:
        f.write(f"# Review package: {base}..{head}\n\n")
        f.write("## Commits\n")
        f.write(commits + "\n")
        f.write("## Files changed\n")
        f.write(stat + "\n")
        f.write("## Diff\n")
        f.write(diff + "\n")
        
    commit_count = len(commits.strip().splitlines()) if commits.strip() else 0
    print(f"wrote {outfile}: {commit_count} commit(s), {os.path.getsize(outfile)} bytes")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python sdd_helper.py <command> [args]", file=sys.stderr)
        print("Commands: task-brief <plan_file> <task_num> | review-package <base> <head>", file=sys.stderr)
        sys.exit(1)
        
    cmd = sys.argv[1]
    if cmd == 'task-brief':
        if len(sys.argv) < 4:
            print("Usage: python sdd_helper.py task-brief <plan_file> <task_num>", file=sys.stderr)
            sys.exit(1)
        task_brief(sys.argv[2], sys.argv[3])
    elif cmd == 'review-package':
        if len(sys.argv) < 4:
            print("Usage: python sdd_helper.py review-package <base> <head>", file=sys.stderr)
            sys.exit(1)
        review_package(sys.argv[2], sys.argv[3])
    else:
        print(f"Unknown command: {cmd}", file=sys.stderr)
        sys.exit(1)

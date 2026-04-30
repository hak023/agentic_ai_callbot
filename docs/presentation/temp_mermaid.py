import re
import os
import subprocess

file_path = r'C:\work\workspace_sippbx\sip-pbx\docs\presentation\PROJECT_BRIEF.md'
with open(file_path, 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Update title
text = text.replace('## 4. 핵심 기능 (중요도 순)', '## 4. 핵심 기능')

# 2. Swap '동작 FLOW' and '상세 기능'
pattern = r'(#### 동작 FLOW(?:[^\n]*)\n.*?)(?=#### 상세 기능\n)(#### 상세 기능\n.*?)(?=#### 사용자 스토리\n)'
new_text = re.sub(pattern, r'\2\1', text, flags=re.DOTALL)

if new_text != text:
    print("Successfully swapped FLOW and 상세 기능.")
else:
    print("Failed to swap FLOW and 상세 기능. Please check regex.")

# Let's count how many times it matched
matches = re.findall(pattern, text, flags=re.DOTALL)
print(f"Found {len(matches)} sections to swap.")

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(new_text)

# 3. Extract and replace mermaid blocks
images_dir = r'C:\work\workspace_sippbx\sip-pbx\docs\presentation\images'
os.makedirs(images_dir, exist_ok=True)

mermaid_blocks = re.findall(r'```mermaid\n(.*?)```', new_text, flags=re.DOTALL)
print(f"Found {len(mermaid_blocks)} mermaid blocks.")

for i, block in enumerate(mermaid_blocks, 1):
    mmd_path = os.path.join(images_dir, f'diagram_{i}.mmd')
    png_path = os.path.join(images_dir, f'diagram_{i}.png')
    
    with open(mmd_path, 'w', encoding='utf-8') as f:
        f.write(block.strip())
    
    # Run mmdc
    print(f"Generating diagram_{i}.png...")
    cmd = f'npx -y @mermaid-js/mermaid-cli@11.4.2 -i "{mmd_path}" -o "{png_path}" -b transparent -t neutral'
    subprocess.run(cmd, shell=True, check=True)
    
    # Replace in text
    old_block = f'```mermaid\n{block}```'
    new_block = f'![Diagram {i}](images/diagram_{i}.png)'
    new_text = new_text.replace(old_block, new_block)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(new_text)

print("All done.")

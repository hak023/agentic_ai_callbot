import re
import os
import subprocess

file_path = r'C:\work\workspace_sippbx\sip-pbx\docs\presentation\PROJECT_BRIEF.md'
with open(file_path, 'r', encoding='utf-8') as f:
    text = f.read()

images_dir = r'C:\work\workspace_sippbx\sip-pbx\docs\presentation\images'
os.makedirs(images_dir, exist_ok=True)

mermaid_blocks = re.findall(r'```mermaid\n(.*?)```', text, flags=re.DOTALL)

for i, block in enumerate(mermaid_blocks, 1):
    mmd_path = os.path.join(images_dir, f'diagram_{i}.mmd')
    png_path = os.path.join(images_dir, f'diagram_{i}.png')
    
    with open(mmd_path, 'w', encoding='utf-8') as f:
        f.write(block.strip())
    
    # We will generate it if it's diagram 31 or if it doesn't exist.
    # Actually, we should just check if it exists and has size > 0
    if not os.path.exists(png_path) or os.path.getsize(png_path) == 0:
        print(f"Generating diagram_{i}.png...")
        cmd = f'npx -y @mermaid-js/mermaid-cli@11.4.2 -i "{mmd_path}" -o "{png_path}" -b transparent -t neutral'
        subprocess.run(cmd, shell=True, check=True)
    else:
        print(f"diagram_{i}.png already exists. Skipping.")
    
    old_block = f'```mermaid\n{block}```'
    new_block = f'![Diagram {i}](images/diagram_{i}.png)'
    text = text.replace(old_block, new_block)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(text)

print("All done.")

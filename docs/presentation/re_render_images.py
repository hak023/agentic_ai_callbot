import os
import glob
import subprocess
import json

images_dir = r'C:\work\workspace_sippbx\sip-pbx\docs\presentation\images'
mmd_files = glob.glob(os.path.join(images_dir, '*.mmd'))

# Create a mermaid config file
config = {
    "theme": "default",
    "themeVariables": {
        "fontFamily": "Pretendard, 'Noto Sans KR', 'Malgun Gothic', sans-serif",
        "fontSize": "16px",
        "edgeLabelBackground": "#ffffff",
        "textColor": "#000000"
    },
    "flowchart": {
        "htmlLabels": True,
        "padding": 20
    }
}

config_path = os.path.join(images_dir, 'mermaid_config.json')
with open(config_path, 'w', encoding='utf-8') as f:
    json.dump(config, f, indent=2)

print(f"Found {len(mmd_files)} .mmd files to re-render.")

for mmd_path in mmd_files:
    png_path = mmd_path.replace('.mmd', '.png')
    print(f"Re-rendering {os.path.basename(png_path)}...")
    
    # Use -c config.json instead of -C custom.css
    cmd = f'npx -y @mermaid-js/mermaid-cli@11.4.2 -i "{mmd_path}" -o "{png_path}" -b white -c "{config_path}" -s 4'
    subprocess.run(cmd, shell=True, check=True)

print("All diagrams re-rendered successfully!")

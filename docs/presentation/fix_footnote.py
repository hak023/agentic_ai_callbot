import sys

file_path = r'C:\work\workspace_sippbx\sip-pbx\docs\presentation\PROJECT_BRIEF.md'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Find the footnote
footnote = r'---' + '\n\n' + r'*본 문서는 Agentic AI Callbot 시스템의 대외 소개·발표용 Project Brief입니다.*'
if footnote in content:
    # Remove the footnote from its current position
    content = content.replace(footnote, '')
    
    # Append it to the very end
    content = content.strip() + '\n\n' + footnote + '\n'

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Footnote moved to the end.")
else:
    print("Footnote not found.")

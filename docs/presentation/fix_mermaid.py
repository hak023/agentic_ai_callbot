import re

file_path = r'C:\work\workspace_sippbx\sip-pbx\docs\presentation\PROJECT_BRIEF.md'
with open(file_path, 'r', encoding='utf-8') as f:
    text = f.read()

# Fix the participant End -> EndCall issue
text = text.replace('participant End as End-of-Call Hook', 'participant EndCall as End-of-Call Hook')
text = text.replace('SIP->>End:', 'SIP->>EndCall:')
text = text.replace('End->>End:', 'EndCall->>EndCall:')
text = text.replace('End->>CCDB:', 'EndCall->>CCDB:')
text = text.replace('End->>LLM:', 'EndCall->>LLM:')
text = text.replace('LLM-->>End:', 'LLM-->>EndCall:')

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(text)
print("Fixed participant End.")

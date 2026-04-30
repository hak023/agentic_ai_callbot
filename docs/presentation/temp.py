import re
import os

file_path = r'C:\work\workspace_sippbx\sip-pbx\docs\presentation\PROJECT_BRIEF.md'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Match the misplaced block
pattern = r'(## 5\. 사용 시나리오.*?\n)(?=### 4\.10 착신 제어)'
match = re.search(pattern, content, flags=re.DOTALL)
if not match:
    print('Could not find the misplaced block.')
    exit(1)

misplaced_block = match.group(1)
print(f"Extracted block length: {len(misplaced_block)}")

# Remove the block from the middle
content = content.replace(misplaced_block, '')

# Process the block
match_6_onwards = re.search(r'(## 6\. 운영 가치.*)', misplaced_block, flags=re.DOTALL)
if not match_6_onwards:
    print('Could not find section 6.')
    exit(1)

block = match_6_onwards.group(1)

# Modify section 6
block = block.replace('## 6. 운영 가치 — 시간이 지나면서 좋아지는 구조', '## 5. 기대 효과')
old_benefits = '- 정책·인사말·연결음을 코드 수정 없이 콘솔에서 즉시 변경합니다.'
new_benefits = '- 정책·인사말·연결음을 코드 수정 없이 콘솔에서 즉시 변경합니다.\n- **멀티테넌트 관리**: 하나의 플랫폼 위에서 조직, 매장, 부서별로 데이터가 완벽히 격리된 "나만의 AI"를 가질 수 있습니다. 각 테넌트는 독립적인 지식, 페르소나, 연락처, 정책을 운영하여 맞춤형 고객 경험을 제공합니다.'
block = block.replace(old_benefits, new_benefits)

# Renumber 7 -> 6
block = block.replace('## 7. 적용 대상', '## 6. 적용 대상')

# Modify section 8 -> 7
block = block.replace('## 8. 적용 절차 (도입 단계)', '## 7. 적용 절차 (도입 단계)')
block = re.sub(r'\| \*\*5\. 외부 연동\(선택\)\*\* \|.*?\|\n', '', block)
block = block.replace('| **6. 운영 시작** |', '| **5. 운영 시작** |')
block = block.replace('| **7. 운영 중 개선** |', '| **6. 운영 중 개선** |')

# Renumber 9 -> 8
block = block.replace('## 9. 비전', '## 8. 비전')

# Remove section 10
# Find the footer to keep it
footer_pattern = r'(\n---\n\*본 문서는 Agentic AI Callbot 시스템의 대외 소개·발표용 Project Brief입니다\.\*)'
footer_match = re.search(footer_pattern, block)
if footer_match:
    # Delete from '## 10. 부록' to just before footer
    block = re.sub(r'## 10\. 부록.*?(?=\n---)', '', block, flags=re.DOTALL)

# Append block at the end
content = content.rstrip() + '\n\n---\n\n' + block.strip() + '\n'

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print('Success.')

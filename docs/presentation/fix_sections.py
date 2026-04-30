import re
import os

file_path = r'C:\work\workspace_sippbx\sip-pbx\docs\presentation\PROJECT_BRIEF.md'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Remove 2.4 구현으로는 어떻게 녹였는가 — 질문별 케이스
# We find where 2.4 starts and 2.5 starts (or end of section 2)
# Wait, the user said to remove 2.4 and merge 2.5 into 5.
# Let's extract 2.5 content first.
match_2_5 = re.search(r'(### 2\.5 기대 효과\n.*?\n)(?=---\n*## 3\. )', content, flags=re.DOTALL)
if match_2_5:
    content_2_5 = match_2_5.group(1)
    # Remove 2.5 from content
    content = content.replace(content_2_5, '')
    
    # We need to extract the bullet points from 2.5 and merge them into 5
    # Let's extract just the list:
    list_match = re.search(r'(- .*?)(?=\n*$)', content_2_5, flags=re.DOTALL)
    if list_match:
        list_2_5 = list_match.group(1)
        
        # Now find '## 5. 기대 효과' and its business effects list
        match_5 = re.search(r'(## 5\. 기대 효과.*?\*\*비즈니스 효과\*\*\n\n)(- .*?\n)(?=\n*---)', content, flags=re.DOTALL)
        if match_5:
            prefix_5 = match_5.group(1)
            list_5 = match_5.group(2)
            
            # Combine them: we can put 2.5 list before or after.
            # 2.5 focuses on high-level AI impacts. 5 focuses on operational.
            # Let's combine them and deduplicate if necessary, or just append.
            # Let's append list_2_5 at the start of list_5.
            new_list_5 = list_2_5 + '\n' + list_5
            new_section_5 = prefix_5 + new_list_5
            
            # Replace old section 5 with new section 5
            content = content.replace(match_5.group(0), new_section_5)
        else:
            print('Could not find Section 5 to merge into.')

# 2. Remove 2.4
match_2_4 = re.search(r'(### 2\.4 구현으로는 어떻게 녹였는가 — 질문별 케이스\n.*?\n)(?=---\n*## 3\. )', content, flags=re.DOTALL)
if match_2_4:
    content = content.replace(match_2_4.group(1), '')

# 3. Remove 3.2
match_3_2 = re.search(r'(### 3\.2 통화 한 건의 여정 \(End-to-End\)\n.*?\n)(?=### 3\.3 )', content, flags=re.DOTALL)
if match_3_2:
    content = content.replace(match_3_2.group(1), '')

# 4. Remove 3.5
# 3.5 is the last sub-section of 3
match_3_5 = re.search(r'(### 3\.5 채널 통합 — 음성·문자·연결음·아웃바운드\n.*?\n)(?=---\n*## 4\. )', content, flags=re.DOTALL)
if match_3_5:
    content = content.replace(match_3_5.group(1), '')

# 5. Renumber 3.3 and 3.4 to 3.2 and 3.3
content = content.replace('### 3.3 LangGraph 의도 라우팅 구조', '### 3.2 LangGraph 의도 라우팅 구조')
content = content.replace('### 3.4 멀티테넌트 격리', '### 3.3 멀티테넌트 격리')

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
print('Done.')

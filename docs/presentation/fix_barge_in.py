import os
import subprocess

brief_path = r'C:\work\workspace_sippbx\sip-pbx\docs\presentation\PROJECT_BRIEF.md'
with open(brief_path, 'r', encoding='utf-8') as f:
    text = f.read()

# Replace texts
text = text.replace(
    '- **Barge-in (바지인)** — VAD가 사용자 발화를 감지하는 즉시 `StartInterruptionFrame`으로 TTS를 끊고 새 의도를 처리합니다.',
    '- **스마트 바지인 (Smart Barge-in)** — 단순 VAD 감지로 TTS를 즉시 끊지 않고, STT로 인식된 텍스트의 단어 수와 키워드를 평가하여 단순 맞장구("네", "아하")와 실제 끼어들기를 구분한 뒤 유효한 질문일 때만 TTS를 중단시킵니다.'
)

text = text.replace(
    '  - **시스템 처리** — VAD가 끼어들기를 감지하고 `StartInterruptionFrame`이 TTS를 즉시 중단시킵니다.',
    '  - **시스템 처리** — 스마트 바지인이 단순 추임새가 아닌 실제 질문("잠깐, 주차는...")임을 판정하여 TTS를 중단시킵니다.'
)

text = text.replace(
    '| **자연스러운 대화 (Turn-taking)** | Endpointing, Turn-taking, Barge-in 처리를 통한 자연스러운 대화 전환 및 끼어들기 감지 | VAD 기반 Barge-in(바지인) 구현으로 AI 발화 중 고객이 말하면 즉시 중단(StartInterruptionFrame) 및 새 의도 처리 |',
    '| **자연스러운 대화 (Turn-taking)** | Endpointing, Turn-taking, Barge-in 처리를 통한 자연스러운 대화 전환 및 끼어들기 감지 | 단순 VAD 기반이 아닌 **스마트 바지인(Smart Barge-in)** 구현으로 단순 맞장구와 실제 끼어들기를 구분하여 자연스러운 턴 전환 지원 |'
)

with open(brief_path, 'w', encoding='utf-8') as f:
    f.write(text)

print("Text replaced in PROJECT_BRIEF.md")

# Fix diagram 10
d10_path = r'C:\work\workspace_sippbx\sip-pbx\docs\presentation\images\diagram_10.mmd'
with open(d10_path, 'w', encoding='utf-8') as f:
    f.write("""flowchart LR
    Mic["고객 RTP 입력"] --> VAD["VAD (Silero)\n발화 시작/종료"]
    VAD --> STT["Google STT v2\n(telephony, 16kHz LINEAR16,\n중간 결과 + 최종 결과)"]
    STT --> Deb["STT Debounce\n(짧은 침묵으로 끊긴 문장 병합)"]
    Deb --> Sup["Supersede\n(새 발화 도착 시 진행 LLM Task 취소)"]
    Sup --> LG["LangGraph 의도 처리"]
    LG --> KN["KoreanNumberNormalizer\n(3,500원 → 삼천오백원)"]
    KN --> TTS["Streaming TTS Chirp3-HD-Kore"]
    TTS --> RTP["RTP 출력 (첫 음절 ~1s)"]
    STT -. "스마트 바지인\n(맞장구/끼어들기 판정)" .-> TTS
""")

# Fix diagram 11
d11_path = r'C:\work\workspace_sippbx\sip-pbx\docs\presentation\images\diagram_11.mmd'
with open(d11_path, 'w', encoding='utf-8') as f:
    f.write("""sequenceDiagram
    participant C as 고객
    participant V as VAD
    participant S as STT
    participant L as LangGraph + LLM
    participant T as TTS
    Note over C,T: 통화 연결 직후 인사말 2단계
    T->>C: Phase 1 인사 (KB greeting_phase1)
    T->>C: Phase 2 인사 (KB greeting_phase2)
    C->>V: "내일 저녁 7시에 4명 가능해요?"
    V->>S: UserStartedSpeakingFrame → 음성 프레임 전달
    S->>L: 최종 텍스트 (debounce 병합)
    L->>L: classify → cache → RAG / booking
    L-->>T: 첫 문장 청크 즉시 전달 (스트리밍)
    T-->>C: 첫 음절 송출 (≈1.0s)
    C->>V: AI 발화 중 끼어들기 ("잠깐, 주차는요?")
    V->>S: 음성 프레임 전달
    S->>L: 텍스트 및 길이 평가 (스마트 바지인)
    L->>T: 유효 끼어들기 판정 → TTS 중단 신호
    T-->>C: TTS 즉시 중단
    L->>L: 새 발화 처리
""")

print("Diagram mmd files updated. Now re-rendering diagram_10 and diagram_11...")

images_dir = r'C:\work\workspace_sippbx\sip-pbx\docs\presentation\images'
config_path = os.path.join(images_dir, 'mermaid_config.json')

for i in [10, 11]:
    mmd_p = os.path.join(images_dir, f'diagram_{i}.mmd')
    png_p = os.path.join(images_dir, f'diagram_{i}.png')
    cmd = f'npx -y @mermaid-js/mermaid-cli@11.4.2 -i "{mmd_p}" -o "{png_p}" -b white -c "{config_path}" -s 4'
    subprocess.run(cmd, shell=True, check=True)
    print(f"diagram_{i}.png re-rendered.")

print("Done.")

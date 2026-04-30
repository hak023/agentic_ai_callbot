import sys

file_path = r'C:\work\workspace_sippbx\sip-pbx\docs\presentation\PROJECT_BRIEF.md'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Define the section to append
new_section = """
## 9. 별첨 - AICC 엔지니어링팀 VoiceAgent 기능 비교

AICC 엔지니어링팀의 "Voice Agent Platform" 구축 방향과 본 **Agentic AI Callbot**은 "고객센터 E2E AX(AI Transformation) 및 AI-Native 고객센터 구현"이라는 동일한 비전을 공유합니다. 두 시스템의 핵심 기능과 접근 방식을 비교한 결과는 다음과 같습니다.

### 9.1 공통점 (핵심 아키텍처 및 목표)

| 구분 | AICC 엔지니어링팀 Voice Agent | Agentic AI Callbot (본 시스템) |
|---|---|---|
| **E2E 스트리밍 파이프라인** | STT → LLM → TTS 전 구간 병렬 스트리밍으로 E2E 지연 < 800ms 확보 목표 | Pipecat 프레임워크 기반 VAD → STT → LLM → 스트리밍 TTS 구조 적용 완료 (빠른 응답 속도 확보) |
| **자연스러운 대화 (Turn-taking)** | Endpointing, Turn-taking, Barge-in 처리를 통한 자연스러운 대화 전환 및 끼어들기 감지 | VAD 기반 Barge-in(바지인) 구현으로 AI 발화 중 고객이 말하면 즉시 중단(StartInterruptionFrame) 및 새 의도 처리 |
| **LLM 기반 동적 대화** | 사전 정의 시나리오(룰/인텐트) 한계 극복, 멀티턴 컨텍스트 관리 및 상담사 Handoff | LangGraph 기반 17개 의도 동적 라우팅, RAG 결합 응답, 신뢰도 부족 시 HITL(운영자 개입) 및 상담사 호 전환(Transfer) 지원 |
| **업무 시스템 연계 (Tool-Calling)** | Tool-calling을 통한 CRM·기간계 연계 | LLM의 Tool Use Loop를 활용한 예약 슬롯 조회, 확정, 변경 및 Google Calendar 동기화 |
| **운영 안정성 및 거버넌스** | Human-in-the-Loop(HITL) 승인 도입 (CUA 영역) | 통화 중 AI 자신감(Confidence) 저하 시 즉각적인 HITL 알림 및 운영자 직접 개입/정제 후 음성 송출 지원 |

### 9.2 차이점 및 Agentic AI Callbot의 차별화된 강점

AICC 엔지니어링팀의 자료가 LiveKit, Pipecat 등 오픈소스 기반의 프레임워크 도입 및 CUA(Computer Use Agent)를 통한 백오피스 화면 제어에 초점을 맞추고 있다면, **Agentic AI Callbot**은 실제 PBX 전화망과의 강력한 결합, 자율 학습, 멀티테넌시에 중점을 두어 이미 완성된 "통화 운영 OS"의 형태를 갖추고 있습니다.

| 구분 | AICC 엔지니어링팀 Voice Agent (로드맵) | Agentic AI Callbot (구현 완료) |
|---|---|---|
| **통화망(Telephony) 제어** | SIP, WebRTC 스트리밍 미디어 처리 도입 예정 | 자체 **SIP B2BUA (Call Control)** 내장. 시간/요일/공휴일, VIP/블랙리스트 발신자 필터 등 상황별 라우팅 엔진 완전 통합 |
| **지식 베이스(KB) 관리** | 지식 DB/RAG 연동 계획 | **Active RAG** 적용. 통화 종료 시 질문/답변 자동 추출, HITL 운영자 답변 즉시 캐싱 등 지식이 스스로 자라나는 선순환 구조 완성 |
| **멀티 채널 통합** | 음성 채널 및 화면 조작(CUA) 중심 | 음성 전화, **SIP MESSAGE (문자)**, 대기 시간 연결음(Ringback), 아웃바운드 캠페인이 단일 LLM/지식 위에서 통합 동작 |
| **멀티테넌트 아키텍처** | (언급되지 않음) | 데이터베이스(SQLite)와 벡터DB(ChromaDB) 전반에 걸쳐 `owner` 기반 완벽한 테넌트 격리 구현. 한 플랫폼에서 다수 가맹점 독립 운영 가능 |
| **운영자 경험 (UX)** | 상담사 Handoff 지원 | **GlobalCallDock** 및 1페이지 대시보드를 통해 실시간 STT/TTS 피드, 발신자 과거 30일 통계(CID), 연락처 폴더 트리(DnD) 등 즉각적인 맥락 제공 |
"""

content = content + new_section

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
print("Section 9 added successfully.")

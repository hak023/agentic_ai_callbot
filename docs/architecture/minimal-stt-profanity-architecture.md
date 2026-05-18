# 통화매니저 실시간 STT 도입을 통한 폭언 감지 기능 개발

## 문서 범위

통화매니저·AI 통화비서에 **실시간 STT**를 도입하고, 전사 텍스트로 **폭언·욕설을 감지**해 가입자를 보호하는 아키텍처를 정의한다.

| 구분 | 내용 |
|------|------|
| **목적** | 실시간 STT 기반 폭언·욕설 감지 → 바이토(수집) → 유엔젤 → 통화매니저 AS(호 종료 안내·호 종료) |
| **신규** | AI Call Agent 시스템(STT, NLP, LLM, DB) |
| **기존 활용** | 교환기, 통화매니저 AS, WTIMS, 유엔젤/바이토 API, PC Client |
| **범위 외** | AI Call Agent TTS, NL-IVR, 초기 개발비·운용비(OPEX) |

동일 STT 인프라로 자막·TIP·스팸·CID 등 부가 기능을 제공할 수 있으나, 본 문서의 **아키텍처 중심**은 폭언·욕설 감지 경로이다.

---

## 1. 제공되는 기능 (사용자 관점)

호 종료 안내 방송은 **통화매니저 AS** 기존 음성으로 재생한다(AI Call Agent TTS 미사용).

| # | 기능 | 가치 | 실현 수단 |
|---|------|------|-----------|
| 1 | **폭언·욕설 실시간 감지 및 호 종료 안내** *(핵심)* | 통화 중 폭언·욕설 감지 후 정책에 따라 안내 방송·호 종료로 가입자 보호 | STT → 1차 NLP → 2차 LLM → 바이토 → 유엔젤 → 통화매니저 AS |
| 2 | **실시간 통화 자막** | interim/final·화자 구분 자막(폭언 감지 입력) | STT 스트리밍, RTP 미러 |
| 3 | **실시간 대화 TIP** | 맥락 맞는 정책·FAQ 힌트 | VectorDB + LLM |
| 4 | **주의·블랙·스팸 사전 알림** | 인입 시 위험 번호 안내 | RDB·스팸 레지스트리 |
| 5 | **자동 연락처 등록** | 통화 기반 연락처 반영 | RDB·[`CID 구현 보고서`](../reports/2026-04/2026-04-21_1340_CID_DUAL_LINE_CONTACTS_STATS_IMPL.md) |
| 6 | **CID 맥락·의도** | 벨 직후 직전 통화 요약·의도 태그 | caller-context API, 통화 후 LLM |

### 1.1 폭언·욕설 감지 흐름

```mermaid
sequenceDiagram
    participant WT as WTIMS
    participant STT as STT
    participant AIR as AI Call Agent
    participant NLP as 1차 NLP
    participant LLM as 2차 LLM
    participant B as 바이토 API
    participant U as 유엔젤 API
    participant CM as 통화매니저 AS

    WT->>STT: RTP
    STT->>AIR: 전사 (interim/final)
    AIR->>NLP: 텍스트 윈도우
    NLP-->>AIR: 1차 후보·점수
    alt 1차 미달
        AIR->>AIR: 자막·부가 처리
    else 1차 후보
        AIR->>LLM: 전사 윈도우·메타
        LLM-->>AIR: 2차 확정
        opt 폭언 확정
            AIR->>B: 폭언 내용·전사·호 정보
            B->>U: 연동
            U->>CM: 안내 방송·호 종료
            CM->>CM: 안내 방송 송출
            AIR->>AIR: 감사 로그 (PostgreSQL)
        end
    end
```

| 단계 | 주체 | 처리 |
|------|------|------|
| 수집 | WTIMS → STT → AI Call Agent | RTP 미러, interim/final 전사, 호·화자 메타 |
| 1차 | 경량 NLP | 금칙어·패턴·경량 분류, 저지연 후보 |
| 2차 | LLM | 문맥 기반 확정, 오탐 완화 |
| 조치 | 바이토 → 유엔젤 → 통화매니저 AS | 폭언 수집, 호 종료 안내·호 종료 |
| 사후 | AI Call Agent, PostgreSQL | 감사 로그, 통화 종료 후 요약·최종 판단 |

---

## 2. 아키텍처

### 2.1 논리 계층

```
┌─────────────────────────────────────────────────────────┐
│  단말·API        바이토 API ── PC Client                │
│                  유엔젤 API                             │
├─────────────────────────────────────────────────────────┤
│  AI (신규)       AI Call Agent ─ STT / NLP / LLM        │
│                  PostgreSQL · VectorDB (동일 호스트)   │
├─────────────────────────────────────────────────────────┤
│  코어 (기존)     교환기 ─ 통화매니저 AS ─ WTIMS         │
└─────────────────────────────────────────────────────────┘
```

| 계층 | 구성 | 역할 |
|------|------|------|
| **코어** | 교환기, 통화매니저 AS, WTIMS | 호 설정, RTP, **호 종료 안내 방송** |
| **AI** | AI Call Agent, STT, NLP, LLM, DB | 전사, 폭언 감지, 이력·TIP·스팸 |
| **연동·단말** | 유엔젤 API, 바이토 API, PC Client | 수집·호 제어 지시, 자막·CID·경고 UI |

### 2.2 물리 구성

```mermaid
flowchart TB
    subgraph CORE["코어 (기존)"]
        EX[교환기] --> CM[통화매니저 AS]
        CM --> WT[WTIMS]
    end

    subgraph AI["AI Call Agent (신규)"]
        AIR[AI Call Agent 서버<br/>API + Runtime 통합]
        STT[STT 처리부]
        NLP[1차 NLP]
        LLM[2차 LLM]
        DB[(PostgreSQL)]
        VDB[(VectorDB)]
    end

    subgraph EXT["연동·단말 (기존)"]
        B[바이토 API]
        U[유엔젤 API]
        PC[PC Client]
    end

    WT -->|RTP| STT
    WT -->|호 세션| AIR
    STT --> AIR
    AIR --> NLP
    AIR --> LLM
    AIR --> DB
    AIR --> VDB
    AIR <-->|폭언·자막·TIP| B
    B <--> U
    U -->|호 제어| CM
    B --> PC
```

### 2.3 데이터 경로

| ID | 경로 | 트리거 |
|----|------|--------|
| P-1 | WTIMS → STT → AI Call Agent → NLP → LLM → 바이토 → 유엔젤 → 통화매니저 AS | 폭언 2차 확정 |
| P-2 | STT → AI Call Agent → 바이토 → PC Client | 상시(자막) |
| P-3 | 전사 → VectorDB → LLM → 바이토 → PC | TIP 요청 |
| P-4 | AI Call Agent ↔ PostgreSQL | 이력·감사·스팸·연락처 |
| P-5 | 인입 시 PostgreSQL 조회 → 바이토 → PC | 스팸·주의 번호 |

### 2.4 설계 원칙

1. **폭언 감지 우선** — STT·1차 NLP·2차 LLM·외부 연동(P-1)을 최우선 경로로 설계한다.
2. **단일 통합 노드** — API/Realtime, Runtime, 기존 GW를 AI Call Agent 서버로 통합한다.
3. **DB 동거** — PostgreSQL과 VectorDB는 AI Call Agent와 **동일 호스트**에 둔다.
4. **STT 선택 가능** — 자체 GPU STT 또는 Cloud STT(옵션 A/B, §4).
5. **코어 비침해** — 교환기·통화매니저 AS·WTIMS 구조는 유지하고, AI는 RTP 미러·API 연동으로만 접근한다.

---

## 3. AI Call Agent — 노드별 기능

신규·추가되는 AI 측 구성만 기술한다. 코어·API·단말은 기존 자산이다.

| 노드 | 배치 | 기능 | 연관 §1 |
|------|------|------|---------|
| **AI Call Agent 서버** | 신규 1대(± HA) | 세션·Realtime, 감지 오케스트레이션, 바이토/유엔젤 연동, TIP·스팸·CID API | #1~#6 |
| **STT 처리부** | 통합 서버 내 또는 GPU 분리 | RTP → interim/final 전사, 화자·시각 메타 | #1, #2 |
| **1차 NLP** | 통합 서버 (CPU) | 폭언·욕설 후보·점수 (저지연) | #1 |
| **2차 LLM** | 통합 또는 GPU | 폭언 확정, 요약·스팸·CID·TIP | #1, #3, #4, #6 |
| **PostgreSQL** | 동일 호스트 | 이력·전사·폭언 감사·스팸·연락처 | #1, #4~#6 |
| **VectorDB** | 동일 호스트 | 지식 임베딩·TIP 검색 | #3 |

### 3.1 배포 옵션

| 옵션 | 구성 | 특성 |
|------|------|------|
| **A** | 통합 서버 1 + GPU 1~2 (STT·sLLM) + DB 동거 | 망 내 STT·LLM, CAPEX ↑ |
| **B** | 통합 서버 1 (STT·LLM은 Cloud API) | CAPEX ↓, STT·LLM **OPEX 별도** |

### 3.2 도입하지 않는 노드

| 항목 | 사유 |
|------|------|
| AIR GW | API·Runtime 통합으로 불필요 |
| AI Call Agent TTS | 호 안내는 통화매니저 AS; NL-IVR 제외 |

---

## 4. CAPEX (서버·HW)

서버·HW 구매비만 ROM으로 산정한다. 개발비·운용비·Cloud API 종량제는 포함하지 않는다.

| 항목 | 옵션 A | 옵션 B |
|------|--------|--------|
| AI Call Agent 통합 서버 | CPU 16~32C, RAM 64~128GB | 동일 또는 RAM 소폭 축소 |
| GPU (STT·sLLM) | 1~2대 (A10/L4급) | 없음 |
| 스토리지 | NVMe SSD | NVMe SSD |
| **합계 (ROM)** | **약 1.1억 ~ 1.7억 원** | **약 0.35억 ~ 0.55억 원** |

---

## 부록

### A. 참고 문서

[prd.md](../product/prd.md) · [prd-detailed-phase1-4.md](../product/prd-detailed-phase1-4.md) · [CALL_HISTORY_AND_CONTENT_DESIGN.md](../design/CALL_HISTORY_AND_CONTENT_DESIGN.md) · [CDR_ENHANCEMENT_DESIGN.md](../design/CDR_ENHANCEMENT_DESIGN.md)

### B. 부가 기능 요약

**스팸 공유** — STT·LLM 분류 → 공용 DB upsert → 타 가입자 착신 시 조회 → PC 표시.

**VectorDB** — 메뉴얼·FAQ 청크 임베딩, TIP용 RAG, 운영자 HITL(선택).

**SIP PBX** — Webhook, CDR, Prometheus 등 기존 기능은 AI와 병행.

### C. PRD 대비 범위 외

| 항목 | 비고 |
|------|------|
| NL-IVR·Dynamic ARS (AI TTS) | 텍스트·폭언 감지 중심 |
| Active RAG 통화 주도 | TIP 보조만 |
| 멀티 에이전트 (Phase 4) | 별도 검토 |
| 오디오 직접 감정 분석 | STT+LLM 중심, 옵션 |

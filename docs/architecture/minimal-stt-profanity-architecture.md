# 지능망 AI Call Agent - Minimal Architecture (STT & 폭언 감지 전용)

## 개요
본 문서는 기존 통신 노드(교환기, 통화매니저AS, WTIMS)를 활용하되, **실시간 STT 및 폭언/욕설 감지**라는 핵심 목적에 맞추어 최소한의 리소스로 경량화된 아키텍처를 설계합니다.

### 주요 설계 원칙
1. **목적 특화**: 실시간 STT 변환과 경량 NLP(실시간 폭언 감지), 그리고 통화 종료 후 LLM(최종 판단)만 수행합니다.
2. **단일 서버 통합**: 복잡한 라우팅(GW), 데이터베이스(PostgreSQL, Qdrant(VectorDB)), 그리고 음성 합성(TTS) 구성 요소를 제거하고 API/Realtime과 AI Runtime을 단일 서버로 통합합니다.
3. **STT 벤더 유연성**: 자체 구축 STT 외에도 Google, AWS, Azure, Naver CLOVA 등 외부 클라우드 STT 솔루션을 선택지로 열어두어 초기 도입 비용 및 운영 비용을 유연하게 산정합니다.
4. **기존 연동 유지**: 코어망 및 외부 API(유엔젤/바이토)와의 연동(0.7억 예상)은 기존대로 유지합니다.

---

## 1. 아키텍처 다이어그램 (경량화 버전)

```mermaid
flowchart LR
    subgraph CORE["기존 코어 통신 영역"]
        EX["교환기 노드 N개"] --> CM["통화매니저AS"] --> WT["WTIMS RTP"]
    end
    
    subgraph ACA["AI Call Agent 시스템 (단일 통합 + STT/LLM)"]
        API_AIR["AI Call Agent 서버<br/>(API + Runtime 통합)"]
        STT["STT 처리부<br/>(자체 구축 or 외부 Cloud API)"]
        NLP_LLM["폭언 감지 모델<br/>(실시간 경량 NLP + 통화 후 LLM)"]
    end
    
    subgraph EXT["외부 연동"]
        UAPI["통화매니저 API (유엔젤)"]
        BAPI["통화매니저 API (바이토)"]
    end

    %% 연결 관계
    WT -->|RTP 스트림 직접 전달| STT
    WT -->|통합 시그널 (호 세션 정보)| API_AIR
    API_AIR <-->|실시간 텍스트 수신| STT
    API_AIR <-->|텍스트 분석 요청| NLP_LLM
    
    UAPI <--> API_AIR
    BAPI <--> API_AIR
```

---

## 2. 핵심 데이터 플로우

1. **호 인입 및 RTP 분기**: 사용자의 통화(INVITE)가 교환기를 거쳐 통화매니저AS와 WTIMS로 연결됩니다. WTIMS는 통화의 음성(RTP) 스트림을 복제하여 **STT 처리부**로 전송합니다.
2. **시그널 및 런타임 제어**: WTIMS는 통화 세션 정보를 단일화된 **AI Call Agent 서버**로 릴레이합니다.
3. **실시간 STT 및 경량 NLP**:
   - STT 모듈이 음성을 실시간 텍스트로 변환하여 AI Call Agent로 전달합니다.
   - AI Call Agent는 경량화된 NLP 언어 모델을 호출하여 실시간으로 폭언/욕설 키워드를 감지합니다.
4. **통화 종료 후 LLM 판단**:
   - 통화가 종료되면 전체 텍스트 전사(Transcript) 데이터를 LLM에 전달합니다.
   - LLM은 전체 문맥을 분석하여 최종적인 폭언 여부 및 강도를 판별하고, 결과를 통화매니저 API 측으로 반환/기록합니다.

---

## 3. 구성 요소 상세 (제외 및 통합 내역)

### 3.1 유지 및 통합되는 구성 요소
- **기존 코어 (교환기, 통화매니저AS, WTIMS)**: 구조 변경 없이 그대로 활용.
- **AI Call Agent 서버**: 기존에 분리되었던 `API/Realtime` 서버와 `AI Runtime` 서버, 그리고 연동 `GW`를 하나의 애플리케이션/서버 노드로 통합하여 운용 (메모리 및 네트워크 I/O 오버헤드 감소).
- **폭언 감지 모델 서버 (NLP + LLM)**: 
  - **경량 NLP 모델**: 단어/구문 기반의 빠르고 가벼운 모델로 실시간 필터링.
  - **LLM**: sLLM (예: Llama 3 8B, Qwen 등) 또는 Cloud LLM API를 사용하여 문맥 기반 최종 판별.

### 3.2 선택형 구성 요소 (STT)
실시간 STT는 운영 예산과 보안 요구사항에 따라 벤더 선택이 가능합니다.
- **옵션 A (자체 구축)**: 오픈소스(Faster-Whisper 등) 기반 GPU 서버 구축. 초기 CAPEX가 높으나 유지비용이 저렴함.
- **옵션 B (Cloud STT)**: Google Cloud Speech-to-Text, AWS Transcribe, Azure Speech, Naver CLOVA 등. 초기 도입비용(CAPEX)을 낮추고 종량제(OPEX)로 전환.

### 3.3 완전히 제거된 구성 요소
- ❌ **AIR GW**: API/Runtime 통합으로 내부 라우팅이 불필요해져 제거.
- ❌ **DBMS (PostgreSQL, Qdrant)**: 실시간 폭언 감지 및 단순 상태 전달 목적이므로 영구 저장용 RDB나 벡터 DB(RAG 용도) 불필요. 호 상태는 인메모리 처리.
- ❌ **TTS Server**: 음성 합성(안내 방송 등) 목적이 없으므로 제거.

---

## 4. 최소 구성 예상 비용 산출 (ROM)

경량화된 아키텍처를 기반으로 한 도입 비용 요약입니다. DB와 TTS, 분산 런타임이 빠짐에 따라 하드웨어 및 소프트웨어 개발비가 대폭 축소됩니다.

| 항목 | 구분 | 예상 비용 (ROM) | 비고 |
|------|------|-----------------|------|
| **기존 연동 개발비** | 기존 자산 연동 | **0.7억 원** | WTIMS, 통화매니저 API(유엔젤/바이토) 연동은 기존 산출과 동일 |
| **소프트웨어 개발비** | AI Call Agent 개발 | **약 3.5억 ~ 4.5억 원** | 단일 통합 서버 개발, 경량 NLP 및 LLM 연동, STT 모듈 통합 (RAG, TTS, 복잡한 DB 트랜잭션 로직 제외로 대폭 감소) |
| **인프라/HW (옵션 A)** | STT 자체 구축 시 | **약 1.0억 ~ 1.5억 원** | 통합 서버(CPU/RAM) + STT 및 sLLM 구동용 GPU 서버(예: 1~2대) |
| **인프라/HW (옵션 B)** | Cloud STT/LLM 사용 시| **약 0.2억 ~ 0.4억 원** | 통합 서버(CPU/RAM)만 온프레미스 구축. STT/LLM은 월 과금(OPEX) 처리 |

### 총 도입 비용 비교
- **STT 자체 구축 시 (CAPEX 집중)**: 약 **5.2억 ~ 6.7억 원**
- **Cloud STT/LLM 사용 시 (초기 투자 최소화)**: 약 **4.4억 ~ 5.6억 원** (클라우드 API 사용량에 따른 월별 OPEX 별도 산정 필요)

> **비고**: Cloud API (Google, Naver 등) 사용 시 분당/초당 과금 정책에 따라 월 1만 시간 통화 시 수백만 원 대의 월 고정비가 발생할 수 있으므로, 연간 유지보수 비용 산정 시 트래픽 볼륨에 따른 OPEX 비교가 필수적입니다.

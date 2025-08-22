# ADK Memory Example

Google ADK (Agent Development Kit)를 사용한 날씨 정보 제공 에이전트 예제 프로젝트입니다.

## 프로젝트 개요

이 프로젝트는 Google ADK를 사용하여 날씨 정보를 제공하는 AI 에이전트를 구현한 예제입니다. 에이전트는 사용자가 특정 도시의 날씨를 묻는 질문에 대해 모의 날씨 데이터를 기반으로 응답합니다.

## 주요 기능

- **날씨 정보 제공**: 뉴욕, 런던, 도쿄의 모의 날씨 데이터 제공
- **한국어 지원**: 한국어로 날씨 정보를 질문할 수 있음
- **Google Gemini 모델**: Gemini 2.0 Flash 모델을 사용한 AI 응답
- **세션 관리**: 대화 히스토리 및 상태 관리

## 기술 스택

- **Python 3.13+**
- **Google ADK 1.11.0+**
- **Google Gemini API**
- **asyncio**: 비동기 처리
- **uv**: Python 패키지 관리

## 설치 및 설정

### 1. 저장소 클론

```bash
git clone https://github.com/[username]/adk-memory-example.git
cd adk-memory-example
```

### 2. 의존성 설치

```bash
uv sync
```

### 3. 환경 변수 설정

`.env` 파일을 생성하고 Google API 키를 설정하세요:

```bash
GOOGLE_API_KEY=your_google_api_key_here
```

Google AI Studio에서 API 키를 발급받을 수 있습니다: https://aistudio.google.com/app/apikey

## 사용법

### 기본 실행

```bash
# 영어 버전
uv run main.py

# 한국어 버전
uv run main_ko.py
```

### ADK Web Agents로 실행

```bash
uv run adk web agents
```

## 프로젝트 구조

```
adk-memory-example/
├── agents/
│   └── weather_agent/
│       ├── __init__.py
│       └── agent.py          # 날씨 에이전트 정의
├── shared/
│   ├── constants.py          # 모델 상수 정의
│   └── types.ts             # TypeScript 타입 정의
├── main.py                   # 영어 버전 메인 실행 파일
├── main_ko.py               # 한국어 버전 메인 실행 파일
├── pyproject.toml           # 프로젝트 설정
└── README.md                # 프로젝트 문서
```

## 에이전트 기능

### get_weather 도구

- **입력**: 도시 이름 (예: "New York", "London", "Tokyo")
- **출력**: 날씨 정보 또는 오류 메시지
- **지원 도시**: 뉴욕, 런던, 도쿄

### 예시 사용법

```python
# 에이전트에게 날씨 질문
"What is the weather like in London?"
"오늘의 뉴욕 날씨는 어때?"
"How about Tokyo?"
```

## 개발 환경

- **Python**: 3.13 이상
- **패키지 관리**: uv
- **AI 모델**: Google Gemini 2.0 Flash
- **비동기 처리**: asyncio

## 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.

## 기여하기

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 문의사항

프로젝트에 대한 질문이나 제안사항이 있으시면 이슈를 생성해 주세요.

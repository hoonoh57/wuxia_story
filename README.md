# Wuxia Story - AI-Powered Multi-Agent Story Generation

## 프로젝트 개요

Wuxia Story는 무협 웹소설을 AI와 인간 협업으로 생성하는 멀티 에이전트 시스템입니다.

### 핵심 특징
- **5개 에이전트**: Material → Narrator → Story → Language → Prompt
- **6단계 파이프라인**: 소재선정 → 세계관설계 → 에피소드구조 → 씬서술 → 영상프롬프트 → 최종승인
- **듀얼모드 디스패처**: A(인간중계) / B(자동화) / C(혼합) 모드 지원
- **버전 히스토리**: 모든 생성/수정을 StepVersion으로 추적

## 설치 및 실행

### 필수 요구사항
- Python 3.10+
- Gemini API 키

### 설치
```bash
git clone https://github.com/your-repo/wuxia-story.git
cd wuxia-story
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 환경 설정
```bash
cp .env.example .env
# .env 파일에 GEMINI_API_KEY 입력
```

### 실행
```bash
python src/main.py
```

## 프로젝트 구조

```
wuxia-story/
├── docs/              # 설계 문서
├── src/               # 소스 코드
│   ├── agents/        # 5개 에이전트
│   ├── core/          # 핵심 인프라
│   ├── data/          # 데이터 레이어
│   └── ui/            # PySide6 UI
├── projects/          # 프로젝트 데이터
└── tests/             # 테스트
```

## 문서

- [ARCHITECTURE.md](docs/ARCHITECTURE.md) - 전체 아키텍처
- [AGENT_SPECS.md](docs/AGENT_SPECS.md) - 에이전트 상세 스펙
- [WORKFLOW.md](docs/WORKFLOW.md) - 단계별 워크플로우
- [SKILL_FILES/](docs/SKILL_FILES/) - 마스터 시스템 프롬프트 및 스킬

## 라이선스

MIT License

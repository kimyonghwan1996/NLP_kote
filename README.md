# NLP KOTE (Korean Text Extraction)

NLP 기반 한국어 텍스트 추출 및 처리 프로젝트입니다.

## 🎯 프로젝트 소개

이 프로젝트는 한국어 텍스트 데이터를 수집, 처리, 분석하기 위한 엔드-투-엔드 NLP 파이프라인입니다.

## 📁 프로젝트 구조

```
NLP_kote/
├── airflow/              # Apache Airflow 워크플로우 및 DAG 정의
├── docker/               # Docker 관련 설정 파일
├── spark/                # Apache Spark 처리 로직
├── scraping/             # 웹 스크래핑 모듈
├── docker-compose.yml    # Docker Compose 설정
├── pyproject.toml        # Python 프로젝트 설정 (Poetry)
└── poetry.lock           # 의존성 Lock 파일
```

## 🚀 시작하기

### 필수 조건

- Python 3.8+
- Docker & Docker Compose
- Poetry (Python 패키지 관리)

### 설치 방법

1. 저장소 클론
```bash
git clone https://github.com/kimyonghwan1996/NLP_kote.git
cd NLP_kote
```

2. 의존성 설치 (Poetry 사용)
```bash
poetry install
```

3. Docker로 실행 (선택사항)
```bash
docker-compose up
```

## 📚 주요 모듈

### Scraping (`scraping/`)
한국어 텍스트 데이터 수집을 위한 웹 스크래핑 모듈

### Spark (`spark/`)
대규모 데이터 처리를 위한 Apache Spark 기반 로직

### Airflow (`airflow/`)
데이터 파이프라인 오케스트레이션 및 스케줄링

## 🛠️ 개발

### 코드 포맷팅
```bash
poetry run black .
```

### 테스트 실행
```bash
poetry run pytest
```

## 📝 라이선스

MIT License

## 👤 기여자

- kimyonghwan1996

---

추가 정보나 이슈는 [GitHub Issues](https://github.com/kimyonghwan1996/NLP_kote/issues)에서 보고해주세요.
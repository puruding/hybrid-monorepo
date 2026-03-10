# LGU+ CSV-DB Data Comparison Tool

LGU+에서 제공한 CSV 파일(시리얼번호, 제품명)과 LGU MariaDB의 장비 데이터를 비교하여 데이터 불일치를 식별하고 리포트를 생성하는 도구

## 기능

1. **데이터 비교**: Source(CSV)와 Target(DB) 시리얼 번호 및 제품명 비교
2. **중복 감지**: 각 데이터셋의 시리얼 번호 중복 감지 및 보고
3. **제품별 집계**: 제품명별 Source/Target 카운트 비교
4. **리포트 생성**: Excel/CSV 형식의 상세 비교 리포트

## 설치

```bash
# 가상환경 생성
python -m venv .venv

# 가상환경 활성화
# Windows
.venv\Scripts\activate
# Linux/Mac
source .venv/bin/activate

# 의존성 설치
pip install -e ".[dev]"
```

## 설정

`.env` 파일에 데이터베이스 접속 정보 설정:

```env
LGU_DB_HOST=10.165.200.216
LGU_DB_PORT=3306
LGU_DB_NAME=mss_uplus
LGU_DB_USER=servicedesk
LGU_DB_PASSWORD=your_password
```

## 사용법

### 기본 사용

```bash
# 기본 비교 실행 (lgu_serial.csv 와 LGU+ DB 비교)
python -m src compare

# 특정 CSV 파일 지정
python -m src compare --csv data/my_serial.csv

# CSV 출력 형식 사용
python -m src compare --format csv

# Excel과 CSV 모두 출력
python -m src compare --format both

# 헤더가 있는 CSV 파일
python -m src compare --csv data.csv --header

# 출력 디렉토리 지정
python -m src compare --output reports/

# 불일치 항목 표시 개수 조절
python -m src compare --show-mismatches 20
```

### 명령어 옵션

| 옵션 | 단축 | 설명 | 기본값 |
|------|------|------|--------|
| `--csv` | `-c` | Source CSV 파일 경로 | `lgu_serial.csv` |
| `--format` | `-f` | 출력 형식 (xlsx/csv/both) | `xlsx` |
| `--output` | `-o` | 출력 디렉토리 | `output/` |
| `--header/--no-header` | | CSV 헤더 유무 | `--no-header` |
| `--show-mismatches` | `-m` | 표시할 불일치 수 | `10` |

### 버전 확인

```bash
python -m src version
```

## 출력 리포트

### Excel 리포트 (`.xlsx`)

| 시트 | 내용 |
|------|------|
| Summary | 전체 요약 통계 |
| Product Counts | 제품명별 Source/Target 카운트 비교 |
| Name Mismatches | 시리얼 일치, 제품명 불일치 목록 |
| Source Only | Source에만 존재하는 레코드 |
| Target Only | Target에만 존재하는 레코드 |
| Duplicates | 중복 시리얼 번호 목록 |

### 콘솔 출력 예시

```
╭──────────────────────────────────────────────────╮
│         LGU+ Data Comparison Report              │
│              2026-03-03 14:30:00                 │
╰──────────────────────────────────────────────────╯

              Summary
┌───────────────────────────────┬─────────┐
│ Metric                        │   Value │
├───────────────────────────────┼─────────┤
│ Total Source Records          │   3,245 │
│ Total Target Records          │   3,198 │
│                               │         │
│ Extra Duplicate Source        │       3 │
│ Extra Duplicate Target        │       2 │
│                               │         │
│ Unique Source Serials         │   3,242 │
│ Unique Target Serials         │   3,196 │
│                               │         │
│ Matched                       │   3,097 │
│ Name Mismatch                 │      45 │
│ Source Only                   │     100 │
│ Target Only                   │      54 │
└───────────────────────────────┴─────────┘
```

## 개발

### 테스트 실행

```bash
# 모든 테스트
pytest

# 커버리지 포함
pytest --cov=src --cov-report=html

# 단위 테스트만
pytest tests/unit

# 통합 테스트만
pytest tests/integration
```

### 타입 체크

```bash
mypy src
```

## 아키텍처

```
compare_data/
├── src/
│   ├── domain/         # 순수 비즈니스 로직 (의존성 없음)
│   │   ├── models.py   # 데이터 모델
│   │   ├── comparator.py  # 비교 알고리즘
│   │   └── aggregator.py  # 집계 알고리즘
│   │
│   ├── application/    # 유스케이스
│   │   ├── ports.py    # 포트 인터페이스
│   │   └── compare_usecase.py  # 비교 유스케이스
│   │
│   ├── infrastructure/ # 외부 시스템 어댑터
│   │   ├── csv_reader.py   # CSV 파일 리더
│   │   ├── db_reader.py    # DB 리더
│   │   └── report_writer.py  # 리포트 생성기
│   │
│   ├── config/         # 설정 관리
│   │   └── settings.py
│   │
│   └── cli/            # CLI 인터페이스
│       └── commands.py
│
└── tests/
    ├── unit/           # 단위 테스트
    └── integration/    # 통합 테스트
```

## 라이선스

Internal use only.

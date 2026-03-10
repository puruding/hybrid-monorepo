**프로젝트의 목적**
- LGU+에서 제공한 시리얼번호와 제품명으로 구성된 CSV파일을 분석하여, .env에 파일에 기록된 Source System: LGU MariaDB DataBase의 시리얼번호와 제품명과 비교하는 프로그램을 개발한다.
이 때 source는 CSV파일을 target은 .env 파일에 기록된 LGU MariaDB DataBase로 명칭을 사용한다.

**프로젝트의 기능**
1. source, target 의 제품명을 그룹핑하여 각 시스템의 제품명을 count를 구한다.
2. source의 시리얼번호와 target의 시리얼번호가 동일하지만 source의 제품명과 target의 제품명이 다른 경우, 불일치 내역(Source제품명, Target제품명)을 모두 리포트한다.
3. source의 시리얼번호가 target에 없는 정보를 찾아낸다.
4. target의 시리얼번호가 source에 없는 정보를 찾아낸다.

D:\02.project\21.asset_mgr_system\ams\compare_data\lgu_serial.csv 파일 구성
- A열 : 시리얼번호
- B열 : 제품명 


**테이블 정보**
1. 필수 쿼리 조건
EqpmTbl
- delYn<>'y' 인 것만 사용
CscoEqpmTbl
- delYn<>'y' 인 것만 사용
- regDtime 이 2025-01-01 이후인 것만 사용

2. join 조건
select * 
from EqpmTbl a, CscoEqpmTbl b 
where a.cscoEqpmCd=b.cscoEqpmCd and a.eqpmCd=b.eqpmCd and a.delYn<>'y' and b.delYn<>'y';

3. 추가 조건
--- LGU+ ---
**임대인 제품**
 EqpmTbl
	- owns = 0(임대)  (참고 : 웹에서 임대인 경우 rntl in (0:LGU, 1:타사, 2:C1) 조합으로 사용하고 있음)
**회선(52), 웹서버(82) 제외**
 EqpmTbl
	- eqpmGrpCd not in (52, 82)

**식별번호에 vip단어가 포함된 제품 제외**
 EqpmTbl
	- rcgnNo not like '%VIP%'

4. 컬럼 정보
CREATE TABLE `EqpmTbl` (
  `eqpmCd` int(11) NOT NULL AUTO_INCREMENT,
  `rcgnNo` varchar(128) NOT NULL COMMENT '장비식별번호',
  `eqpmGrpCd` int(11) NOT NULL COMMENT '장비그룹코드',
  `useYn` char(1) DEFAULT 'n' COMMENT '사용여부',
  `eqpmDesc` varchar(256) DEFAULT NULL COMMENT '장비설명',
  `delYn` char(1) DEFAULT 'n' COMMENT '장비상태',
  `regr` varchar(16) DEFAULT NULL COMMENT '등록자',
  `regDtime` datetime DEFAULT NULL COMMENT '등록일시',
  `modr` varchar(16) DEFAULT NULL COMMENT '수정자',
  `modDtime` datetime DEFAULT NULL COMMENT '수정일시',
  `salesCharge` varchar(16) DEFAULT NULL COMMENT '영업담당',
  `cscoCd` int(11) DEFAULT NULL COMMENT '고객사',
  `cscoEqpmCd` int(11) DEFAULT NULL COMMENT '고객장비코드',
  `strtDate` date DEFAULT NULL COMMENT '시작,입고',
  `endDate` date DEFAULT NULL COMMENT '종료,출고',
  `owns` char(1) DEFAULT '0' COMMENT '소유권 0:임대, 1:판매',
  `rntl` char(1) DEFAULT '0' COMMENT '임대 0:LGU, 1:타사, 2:C1',
  `rntlConm` varchar(32) DEFAULT NULL COMMENT '임대회사',
  PRIMARY KEY (`eqpmCd`)
) ENGINE=InnoDB AUTO_INCREMENT=3934 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci COMMENT='장비정보';

-- mss_uplus.CscoEqpmTbl definition

CREATE TABLE `CscoEqpmTbl` (
  `cscoEqpmCd` int(11) NOT NULL AUTO_INCREMENT COMMENT '고객장비코드',
  `cscoCd` int(11) NOT NULL COMMENT '고객사코드',
  `eqpmCd` int(11) NOT NULL COMMENT '장비코드',
  `eqpmNm` varchar(128) NOT NULL COMMENT '장비제품명',
  `eqpmIp` varchar(64) NOT NULL COMMENT 'IP',
  `eqpmTp` char(1) DEFAULT NULL COMMENT '장비유형(1:관제장비,2:비관제장비)',
  `rqrNm` varchar(128) DEFAULT NULL COMMENT '장비명',
  `instPos` varchar(128) DEFAULT NULL COMMENT '설치위치',
  `instDt` date DEFAULT NULL COMMENT '설치일자',
  `accsAcct` varchar(16) DEFAULT NULL COMMENT '접근계정',
  `accsMeth` varchar(4) DEFAULT NULL COMMENT '접근방법',
  `owns` char(1) DEFAULT '0' COMMENT '소유권 0:임대, 1:판매',
  `rntl` char(1) DEFAULT '0' COMMENT '임대 0:C1, 1:타사',
  `rntlConm` varchar(32) DEFAULT NULL COMMENT '임대회사',
  `passwd` varchar(128) DEFAULT NULL COMMENT '장비비밀번호',
  `passwdDesc` varchar(256) DEFAULT NULL COMMENT '장비비밀번호설명',
  `svcStrtDt` date DEFAULT NULL COMMENT '서비스시작일',
  `svcEndDt` date DEFAULT NULL COMMENT '서비스종료일',
  `billingDt` date DEFAULT NULL COMMENT '과금일자',
  `cmpsFileYn` char(1) DEFAULT NULL COMMENT '구성도첨부여부',
  `aplctFileYn` char(1) DEFAULT NULL COMMENT '개통신청서첨부여부',
  `finFileYn` char(1) DEFAULT NULL COMMENT '완료보고서첨부여부',
  `fwSec` varchar(256) DEFAULT NULL COMMENT '방화벽구간',
  `esmRefCd` varchar(16) DEFAULT NULL COMMENT 'ESM자산코드',
  `esmRefNm` varchar(64) DEFAULT NULL COMMENT 'ESM자산명',
  `esmRefSvr` int(11) DEFAULT NULL COMMENT 'ESM서버구분',
  `emailRcv` char(1) DEFAULT 'n' COMMENT '이메일수신여부',
  `smsRcv` char(1) DEFAULT 'n' COMMENT 'sms수신여부',
  `blockApiType` char(1) DEFAULT NULL COMMENT '방화벽차단구분',
  `delYn` char(1) DEFAULT 'n' COMMENT '삭제여부',
  `regr` varchar(16) NOT NULL COMMENT '등록자',
  `regDtime` datetime NOT NULL DEFAULT current_timestamp() COMMENT '등록일시',
  `modr` varchar(16) NOT NULL COMMENT '수정자',
  `modDtime` datetime NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp() COMMENT '수정일시',
  `backupDtime` datetime DEFAULT NULL COMMENT '장비백업일시',
  `vdom` varchar(256) DEFAULT NULL COMMENT '방화벽vdom',
  `subscriptionNo` varchar(128) DEFAULT NULL COMMENT '임대가입번호',
  `registrationNo` varchar(128) DEFAULT NULL COMMENT '청약가입번호',
  `lineNo` varchar(32) DEFAULT NULL COMMENT '회선번호',
  `blockFw` varchar(512) DEFAULT NULL COMMENT '차단방화벽cd',
  `cscoEqpmDesc` varchar(2048) DEFAULT NULL COMMENT '고객장비설명',
  `fwCliPort` int(11) NOT NULL DEFAULT 0 COMMENT '방화벽Cli포트',
  `backupTypeCd` int(11) NOT NULL DEFAULT 0 COMMENT '백업타입코드',
  `trmDtime` datetime DEFAULT NULL,
  `adminAccsAcct` varchar(64) DEFAULT NULL,
  `adminPasswd` varchar(64) DEFAULT NULL,
  `fwMachinePort` int(11) DEFAULT NULL,
  `chkRptSct` char(1) DEFAULT '0' COMMENT '장비정검보고서유형(0:해당없음,1:월간,2:분기)',
  `stdPrice` int(11) DEFAULT NULL COMMENT '정산표준가액',
  `instCost` int(11) DEFAULT NULL COMMENT '설치비',
  `instCostDt` date DEFAULT NULL COMMENT '설치비수금일자',
  `lineProduct` varchar(50) DEFAULT NULL COMMENT '회선상품명',
  `lineType` char(1) DEFAULT NULL COMMENT '회선유형(1:신규/2:변경/3:기존)',
  `mustReceiveSms` char(1) DEFAULT 'n' COMMENT '침해위협이벤트SMS꼭수신',
  PRIMARY KEY (`cscoEqpmCd`,`cscoCd`,`eqpmCd`)
) ENGINE=InnoDB AUTO_INCREMENT=3826 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci COMMENT='고객사자산현황';

---

# LGU+ CSV-DB 비교 프로그램 개발계획

## 1. 프로젝트 개요

### 1.1 목적
LGU+에서 제공한 CSV 파일(시리얼번호, 제품명)과 LGU MariaDB의 장비 데이터를 비교하여 데이터 불일치를 식별하고 리포트를 생성하는 도구

### 1.2 용어 정의
| 용어 | 설명 |
|------|------|
| **Source** | CSV 파일 (lgu_serial.csv) |
| **Target** | LGU MariaDB (mss_uplus) |
| **시리얼번호** | EqpmTbl.rcgnNo (장비식별번호) |
| **제품명** | CscoEqpmTbl.eqpmNm (장비제품명) |

---

## 2. 아키텍처 설계

### 2.1 모듈 구조 (Hexagonal Architecture)
```
compare_data/
├── .env                          # DB 접속 정보 (기존)
├── lgu_serial.csv               # 소스 데이터 (기존)
├── plan.md                      # 기획 문서 (기존)
├── pyproject.toml               # 프로젝트 설정
├── README.md                    # 사용법 문서
│
├── src/
│   ├── __init__.py
│   ├── __main__.py              # CLI 진입점
│   │
│   ├── domain/                  # 순수 비즈니스 로직 (의존성 0%)
│   │   ├── __init__.py
│   │   ├── models.py            # EquipmentRecord, ComparisonResult
│   │   ├── comparator.py        # 비교 로직 (핵심 알고리즘)
│   │   └── aggregator.py        # 집계 로직 (count by product)
│   │
│   ├── application/             # 유스케이스, 포트 정의
│   │   ├── __init__.py
│   │   ├── ports.py             # DataSource, DataTarget 인터페이스
│   │   ├── compare_usecase.py   # 비교 유스케이스 오케스트레이션
│   │   └── report_usecase.py    # 리포트 생성 유스케이스
│   │
│   ├── infrastructure/          # 외부 시스템 어댑터
│   │   ├── __init__.py
│   │   ├── csv_reader.py        # CSV 파일 리더 (빠른 성능)
│   │   ├── db_reader.py         # SQLAlchemy 기반 DB 리더
│   │   └── report_writer.py     # Excel/CSV 리포트 출력
│   │
│   ├── config/                  # 설정 관리
│   │   ├── __init__.py
│   │   ├── settings.py          # Pydantic Settings
│   │   └── loader.py            # .env 로더
│   │
│   └── cli/                     # CLI 인터페이스
│       ├── __init__.py
│       └── commands.py          # Typer 기반 명령어
│
├── tests/                       # 테스트
│   ├── __init__.py
│   ├── conftest.py              # 공통 fixtures
│   ├── unit/
│   │   ├── domain/
│   │   │   ├── test_comparator.py
│   │   │   └── test_aggregator.py
│   │   └── infrastructure/
│   │       ├── test_csv_reader.py
│   │       └── test_db_reader.py
│   └── integration/
│       └── test_compare_flow.py
│
└── output/                      # 결과 출력 디렉토리 (gitignore)
    └── .gitkeep
```

### 2.2 계층별 책임

| 계층 | 책임 | 의존성 |
|------|------|--------|
| **domain/** | 비교 알고리즘, 데이터 모델 | 없음 (순수 Python) |
| **application/** | 유스케이스 오케스트레이션 | domain만 의존 |
| **infrastructure/** | 외부 I/O (Excel, DB, Report) | application 포트 구현 |
| **cli/** | 사용자 인터페이스 | application 유스케이스 호출 |

---

## 3. 데이터 모델

### 3.1 도메인 모델 (domain/models.py)

```python
from dataclasses import dataclass
from typing import Optional
from enum import Enum


class MatchStatus(Enum):
    """비교 결과 상태"""
    MATCHED = "matched"              # 완전 일치
    NAME_MISMATCH = "name_mismatch"  # 시리얼 일치, 제품명 불일치
    SOURCE_ONLY = "source_only"      # Source에만 존재
    TARGET_ONLY = "target_only"      # Target에만 존재


@dataclass(frozen=True)
class EquipmentRecord:
    """장비 레코드 (불변 객체)"""
    serial_number: str          # 시리얼번호
    product_name: str           # 제품명
    source: str = "unknown"     # 출처 ("source" or "target")


@dataclass
class ComparisonResult:
    """개별 비교 결과"""
    serial_number: str
    status: MatchStatus
    source_product_name: Optional[str] = None
    target_product_name: Optional[str] = None


@dataclass
class ProductCount:
    """제품별 카운트"""
    product_name: str
    source_count: int
    target_count: int
    diff: int  # source_count - target_count


@dataclass
class DuplicateRecord:
    """중복 레코드 정보"""
    serial_number: str           # 중복된 시리얼번호
    product_names: List[str]     # 해당 시리얼의 모든 제품명
    occurrence_count: int        # 전체 출현 횟수 (첫 번째 포함, 예: 2번 나타나면 2)
    source: str                  # "source" or "target"

    # 주의: extra_duplicate_count를 계산할 때는 occurrence_count - 1을 사용


@dataclass
class ComparisonSummary:
    """비교 결과 요약 (수학적 정합성 보장)"""
    # 원본 데이터 (중복 포함)
    total_source: int                    # 원본 Source 레코드 수 (중복 포함)
    total_target: int                    # 원본 Target 레코드 수 (중복 포함)

    # 중복 통계 (추가 중복분만 카운트)
    extra_duplicate_source_count: int    # Source 추가 중복 레코드 수 (첫 번째 제외)
    extra_duplicate_target_count: int    # Target 추가 중복 레코드 수 (첫 번째 제외)

    # 중복 제거 후 유니크 시리얼 수
    unique_source_count: int             # 중복 제거 후 유니크 Source 시리얼 수
    unique_target_count: int             # 중복 제거 후 유니크 Target 시리얼 수

    # 비교 결과 (유니크 시리얼 기준)
    matched_count: int                   # 완전 일치 (유니크 시리얼 기준)
    name_mismatch_count: int             # 제품명 불일치 (유니크 시리얼 기준)
    source_only_count: int               # Source에만 존재 (유니크 시리얼 기준)
    target_only_count: int               # Target에만 존재 (유니크 시리얼 기준)

    # 수식 검증 (자동 계산 가능):
    # total_source = unique_source_count + extra_duplicate_source_count
    # total_target = unique_target_count + extra_duplicate_target_count
    # unique_source_count = matched_count + name_mismatch_count + source_only_count
    # unique_target_count = matched_count + name_mismatch_count + target_only_count
```

### 3.2 포트 인터페이스 (application/ports.py)

```python
from abc import ABC, abstractmethod
from typing import List
from src.domain.models import EquipmentRecord


class EquipmentDataPort(ABC):
    """데이터 소스 포트 (어댑터 패턴)"""

    @abstractmethod
    def load_records(self) -> List[EquipmentRecord]:
        """장비 레코드 로드"""
        pass

    @abstractmethod
    def get_record_count(self) -> int:
        """레코드 수 반환"""
        pass
```

---

## 4. 데이터 흐름

### 4.1 전체 흐름

```
┌─────────────────────────────────────────────────────────────────┐
│                         CLI (commands.py)                       │
│                    python -m src compare                        │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                  Application Layer (UseCase)                    │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ CompareUseCase.execute()                                  │  │
│  │   1. source_raw = Load source data (CSV)                 │  │
│  │   2. target_raw = Load target data (DB)                  │  │
│  │   3. results, duplicates, summary, source_clean,          │  │
│  │      target_clean = Comparator(source_raw, target_raw)    │  │
│  │      ↑ 우선 중복을 감지하고, 순수 유니크 레코드 분리         │  │
│  │   4. product_counts = Aggregator(source_clean, target_clean) │  │
│  │      ↑ 가짜 재고(중복)가 제거된 "유니크" 기준으로 제품별 집계 │  │
│  │   5. Generate Report(product_counts, results,             │  │
│  │                      duplicates, summary)                 │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
          │                                        │
          ▼                                        ▼
┌──────────────────────┐              ┌────────────────────────┐
│   CSVReader          │              │     DBReader           │
│   (infrastructure)   │              │   (infrastructure)     │
│                      │              │                        │
│  lgu_serial.csv      │              │  EqpmTbl JOIN          │
│  - 1열: serial       │              │  CscoEqpmTbl           │
│  - 2열: product_name │              │  WHERE delYn<>'y'      │
└──────────────────────┘              └────────────────────────┘
          │                                        │
          ▼                                        ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Domain Layer (Pure Logic)                    │
│                                                                 │
│  ┌─────────────────────┐         ┌─────────────────────────┐   │
│  │    Comparator       │         │     Aggregator          │   │
│  │                     │         │                         │   │
│  │  • matched          │         │  • count by product     │   │
│  │  • name_mismatch    │         │  • source vs target     │   │
│  │  • source_only      │         │  • diff calculation     │   │
│  │  • target_only      │         │                         │   │
│  └─────────────────────┘         └─────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                  ReportWriter (infrastructure)                  │
│                                                                 │
│  output/comparison_report_20260303_143000.xlsx                  │
│  - Sheet 1: Summary (전체 요약)                                  │
│  - Sheet 2: Product Counts (제품별 카운트 비교)                  │
│  - Sheet 3: Name Mismatches (제품명 불일치)                      │
│  - Sheet 4: Source Only (Source에만 존재)                       │
│  - Sheet 5: Target Only (Target에만 존재)                       │
└─────────────────────────────────────────────────────────────────┘
```

### 4.2 DB 쿼리

```sql
-- Target 데이터 추출 쿼리
SELECT
    a.rcgnNo AS serial_number,
    b.eqpmNm AS product_name
FROM EqpmTbl a
INNER JOIN CscoEqpmTbl b
    ON a.cscoEqpmCd = b.cscoEqpmCd
    AND a.eqpmCd = b.eqpmCd
WHERE a.delYn <> 'y'
  AND b.delYn <> 'y'
  AND b.regDtime >= '2025-01-01'
  AND a.owns = '0'
  AND a.eqpmGrpCd NOT IN (52, 82)
  AND a.rcgnNo NOT LIKE '%VIP%';
```

---

## 5. 비교 알고리즘 설계

### 5.1 핵심 알고리즘 (domain/comparator.py)

```python
def compare_datasets(
    source_records: List[EquipmentRecord],
    target_records: List[EquipmentRecord]
) -> Tuple[List[ComparisonResult], List[DuplicateRecord], ComparisonSummary, List[EquipmentRecord], List[EquipmentRecord]]:
    """
    두 데이터셋 비교 (Fault-Tolerant)

    시리얼 번호 중복 처리:
    - 중복 발견 시 프로세스를 중단하지 않음
    - 중복 레코드는 비교에서 제외하고 별도 리스트에 보관
    - 첫 번째 레코드만 비교에 사용 (deterministic)

    시간복잡도: O(n + m) where n=source, m=target
    공간복잡도: O(n + m)

    Returns:
        Tuple[비교결과 리스트, 중복레코드 리스트, 통계 요약, source_clean, target_clean]
    """
    # 1. 중복 감지 및 분리 (O(n))
    source_clean, source_duplicates = _extract_duplicates(source_records, "source")
    target_clean, target_duplicates = _extract_duplicates(target_records, "target")

    # 2. 중복 제거된 데이터로 딕셔너리 변환 (O(n) + O(m))
    source_map: Dict[str, EquipmentRecord] = {
        r.serial_number: r for r in source_clean
    }
    target_map: Dict[str, EquipmentRecord] = {
        r.serial_number: r for r in target_clean
    }

    results: List[ComparisonResult] = []

    # 3. Source 기준 비교 (O(n))
    for serial, source_rec in source_map.items():
        if serial in target_map:
            target_rec = target_map[serial]
            if source_rec.product_name == target_rec.product_name:
                status = MatchStatus.MATCHED
            else:
                status = MatchStatus.NAME_MISMATCH
            results.append(ComparisonResult(
                serial_number=serial,
                status=status,
                source_product_name=source_rec.product_name,
                target_product_name=target_rec.product_name
            ))
        else:
            results.append(ComparisonResult(
                serial_number=serial,
                status=MatchStatus.SOURCE_ONLY,
                source_product_name=source_rec.product_name
            ))

    # 4. Target Only 찾기 (O(m))
    for serial, target_rec in target_map.items():
        if serial not in source_map:
            results.append(ComparisonResult(
                serial_number=serial,
                status=MatchStatus.TARGET_ONLY,
                target_product_name=target_rec.product_name
            ))

    # 5. 요약 집계
    all_duplicates = source_duplicates + target_duplicates
    summary = _calculate_summary(
        results,
        total_source=len(source_records),
        total_target=len(target_records),
        extra_duplicate_source_count=sum(d.occurrence_count - 1 for d in source_duplicates),
        extra_duplicate_target_count=sum(d.occurrence_count - 1 for d in target_duplicates),
        unique_source_count=len(source_clean),
        unique_target_count=len(target_clean)
    )

    return results, all_duplicates, summary, source_clean, target_clean


def _extract_duplicates(
    records: List[EquipmentRecord],
    source: str
) -> Tuple[List[EquipmentRecord], List[DuplicateRecord]]:
    """
    중복 레코드 추출 및 분리 (Fault-Tolerant)

    전략:
    - 중복된 시리얼의 첫 번째 레코드만 유지 (deterministic)
    - 나머지는 중복 리스트로 분리

    Args:
        records: 검증할 레코드 리스트
        source: 데이터 출처 ("source" or "target")

    Returns:
        (중복 제거된 레코드 리스트, 중복 레코드 정보 리스트)
    """
    from collections import defaultdict

    # 시리얼별 레코드 그룹핑
    serial_groups: Dict[str, List[EquipmentRecord]] = defaultdict(list)
    for record in records:
        serial_groups[record.serial_number].append(record)

    clean_records: List[EquipmentRecord] = []
    duplicate_records: List[DuplicateRecord] = []

    for serial, group in serial_groups.items():
        if len(group) == 1:
            # 유일한 레코드 - 그대로 사용
            clean_records.append(group[0])
        else:
            # 중복 발견
            # 첫 번째 레코드는 비교에 사용
            clean_records.append(group[0])

            # 중복 정보 기록
            duplicate_records.append(DuplicateRecord(
                serial_number=serial,
                product_names=[r.product_name for r in group],
                occurrence_count=len(group),
                source=source
            ))

    return clean_records, duplicate_records
```

### 5.2 집계 알고리즘 (domain/aggregator.py)

```python
def aggregate_by_product(
    source_clean: List[EquipmentRecord],  # 중복 제거된 데이터
    target_clean: List[EquipmentRecord]   # 중복 제거된 데이터
) -> List[ProductCount]:
    """
    제품명별 카운트 집계 (유니크 데이터 기준)

    ⚠️ 중요: 이 함수는 Comparator에서 중복 입력(휴먼 에러)이 걸러진 **순수 유니크** 데이터를 입력받습니다.

    목적:
    - 가짜 재고(중복)를 배제한, 실제 물리적 보유 현황 및 카운트 파악
    - 정확하고 신뢰성 있는 Source/Target 간의 시리얼 기반 제품 분포 비교

    Args:
        source_clean: 중복 제거된 순수 Source 데이터
        target_clean: 중복 제거된 순수 Target 데이터

    Returns:
        제품명별 source/target 카운트 및 차이

    Example:
        입력 Source: [SN001-FortiGate, SN002-Cisco]  # 중복 걸러진 2건
        입력 Target: [SN001-FortiGate]               # 1건

        결과:
        - FortiGate: Source=1, Target=1, Diff=0
        - Cisco:     Source=1, Target=0, Diff=+1
    """
    source_counts = Counter(r.product_name for r in source_clean)
    target_counts = Counter(r.product_name for r in target_clean)

    all_products = set(source_counts.keys()) | set(target_counts.keys())

    return [
        ProductCount(
            product_name=product,
            source_count=source_counts.get(product, 0),
            target_count=target_counts.get(product, 0),
            diff=source_counts.get(product, 0) - target_counts.get(product, 0)
        )
        for product in sorted(all_products)
    ]
```

---

## 6. 출력 형식 및 리포트 구조

### 6.1 Excel 리포트 (기본 출력)

**파일명**: `output/comparison_report_YYYYMMDD_HHMMSS.xlsx`

| Sheet | 내용 | 컬럼 |
|-------|------|------|
| Summary | 전체 요약 통계 | 항목, 값 |
| Product Counts | 제품별 카운트 비교 | 제품명, Source수, Target수, 차이 |
| Name Mismatches | 시리얼 일치 + 제품명 불일치 | 시리얼번호, Source제품명, Target제품명 |
| Source Only | Source에만 있는 레코드 | 시리얼번호, 제품명 |
| Target Only | Target에만 있는 레코드 | 시리얼번호, 제품명 |
| **Duplicates** | **중복 시리얼 번호 목록** | **시리얼번호, 출처, 중복횟수, 제품명 목록** |

### 6.2 Console 출력 (Rich Table)

```
╭──────────────────────────────────────────────────────────╮
│               LGU+ Data Comparison Report                │
│                    2026-03-03 14:30:00                   │
╰──────────────────────────────────────────────────────────╯

📊 Summary
┌───────────────────────────────┬─────────┐
│ Metric                        │ Value   │
├───────────────────────────────┼─────────┤
│ Total Source Records          │ 3,245   │
│ Total Target Records          │ 3,198   │
│ Extra Duplicate Source        │ 3       │
│ Extra Duplicate Target        │ 2       │
│ Unique Source Serials         │ 3,242   │
│ Unique Target Serials         │ 3,196   │
│ ───────────────────────────── │ ─────── │
│ Matched                       │ 3,097   │
│ Name Mismatch                 │ 45      │
│ Source Only                   │ 100     │
│ Target Only                   │ 54      │
└───────────────────────────────┴─────────┘

✅ 수식 검증:
   3,245 = 3,242 + 3     (Total Source = Unique + Extra Dup)
   3,198 = 3,196 + 2     (Total Target = Unique + Extra Dup)
   3,242 = 3,097 + 45 + 100   (Unique Source = Matched + Mismatch + Source Only)
   3,196 = 3,097 + 45 + 54    (Unique Target = Matched + Mismatch + Target Only)

⚠️  Name Mismatches (showing first 10)
┌──────────────────┬──────────────────┬──────────────────┐
│ Serial Number    │ Source Product   │ Target Product   │
├──────────────────┼──────────────────┼──────────────────┤
│ SN001234         │ FortiGate 100F   │ FortiGate 100E   │
│ ...              │ ...              │ ...              │
└──────────────────┴──────────────────┴──────────────────┘

Report saved to: output/comparison_report_20260303_143000.xlsx
```

### 6.3 CSV 출력 (옵션)

```bash
python -m src compare --format csv
```

---

## 7. 에러 핸들링 전략

### 7.1 예외 계층 구조

```python
# src/domain/exceptions.py

class CompareDataError(Exception):
    """베이스 예외"""
    pass


class DataLoadError(CompareDataError):
    """데이터 로드 실패"""
    pass


class CSVReadError(DataLoadError):
    """CSV 파일 읽기 실패"""
    pass


class DatabaseConnectionError(DataLoadError):
    """DB 연결 실패"""
    pass


class ValidationError(CompareDataError):
    """데이터 유효성 검증 실패"""
    pass


class ReportGenerationError(CompareDataError):
    """리포트 생성 실패"""
    pass
```

### 7.2 에러 처리 전략

| 에러 유형 | 처리 방식 | 사용자 메시지 |
|-----------|-----------|---------------|
| CSV 파일 없음 | 즉시 종료 | "CSV file not found: {path}" |
| CSV 형식 오류 | 즉시 종료 | "Invalid CSV format: expected 2 columns (serial, product)" |
| CSV 인코딩 오류 | UTF-8 재시도 | "Encoding error, trying UTF-8" |
| **시리얼 번호 중복** | **경고 후 계속** | **"⚠️  SOURCE에 추가 중복 시리얼 3건 발견 - Duplicates 시트 참고"** |
| DB 연결 실패 | 재시도 3회 후 종료 | "Database connection failed after 3 attempts" |
| DB 쿼리 오류 | 즉시 종료 | "Query execution failed: {error}" |
| 빈 데이터셋 | 경고 후 계속 | "Warning: Source/Target dataset is empty" |
| 출력 디렉토리 없음 | 자동 생성 | (silent) |

### 7.3 로깅 전략

```python
# structlog 기반 구조화된 로깅
import structlog

logger = structlog.get_logger()

# 예시
logger.info("data_loaded", source="csv", record_count=3245)
logger.warning("empty_dataset", source="target")
logger.error("db_connection_failed", host="10.165.200.216", attempt=3)
```

---

## 8. 테스트 전략

### 8.1 테스트 계층

| 계층 | 커버리지 목표 | 주요 테스트 |
|------|---------------|-------------|
| Unit (domain) | 95% | Comparator, Aggregator 로직 |
| Unit (infra) | 80% | ExcelReader, DBReader 개별 |
| Integration | 70% | 전체 흐름 E2E |

### 8.2 단위 테스트 예시

```python
# tests/unit/domain/test_comparator.py

class TestComparator:
    def test_all_matched(self):
        """모든 레코드가 일치하는 경우"""
        source = [EquipmentRecord("SN001", "Product A")]
        target = [EquipmentRecord("SN001", "Product A")]

        results, duplicates, summary, _, _ = compare_datasets(source, target)

        assert summary.matched_count == 1
        assert summary.name_mismatch_count == 0
        assert len(duplicates) == 0

    def test_name_mismatch(self):
        """시리얼 일치, 제품명 불일치"""
        source = [EquipmentRecord("SN001", "Product A")]
        target = [EquipmentRecord("SN001", "Product B")]

        results, duplicates, summary, _, _ = compare_datasets(source, target)

        assert summary.name_mismatch_count == 1
        assert results[0].source_product_name == "Product A"
        assert results[0].target_product_name == "Product B"

    def test_source_only(self):
        """Source에만 존재하는 레코드"""
        source = [EquipmentRecord("SN001", "Product A")]
        target = []

        results, duplicates, summary, _, _ = compare_datasets(source, target)

        assert summary.source_only_count == 1

    def test_target_only(self):
        """Target에만 존재하는 레코드"""
        source = []
        target = [EquipmentRecord("SN001", "Product A")]

        results, duplicates, summary, _, _ = compare_datasets(source, target)

        assert summary.target_only_count == 1

    def test_duplicate_serial_in_source(self):
        """Source에 중복 시리얼이 있는 경우 - 첫 번째만 비교, 나머지는 중복 리스트"""
        source = [
            EquipmentRecord("SN001", "Product A"),
            EquipmentRecord("SN002", "Product B"),
            EquipmentRecord("SN001", "Product C")  # 중복!
        ]
        target = [EquipmentRecord("SN001", "Product A")]

        results, duplicates, summary, _, _ = compare_datasets(source, target)

        # 중복 감지
        assert len(duplicates) == 1
        assert duplicates[0].serial_number == "SN001"
        assert duplicates[0].occurrence_count == 2
        assert duplicates[0].product_names == ["Product A", "Product C"]
        assert duplicates[0].source == "source"

        # 첫 번째 레코드로 비교 수행
        assert summary.matched_count == 1  # SN001 Product A와 매칭
        assert summary.extra_duplicate_source_count == 1  # 추가 중복 1건 (2번째만)
        assert summary.total_source == 3  # 원본 전체
        assert summary.unique_source_count == 2  # 유니크 시리얼 (SN001, SN002)

    def test_duplicate_serial_in_target(self):
        """Target에 중복 시리얼이 있는 경우 - 첫 번째만 비교"""
        source = [EquipmentRecord("SN001", "Product A")]
        target = [
            EquipmentRecord("SN001", "Product A"),
            EquipmentRecord("SN001", "Product B")  # 중복!
        ]

        results, duplicates, summary, _, _ = compare_datasets(source, target)

        # 중복 감지
        assert len(duplicates) == 1
        assert duplicates[0].serial_number == "SN001"
        assert duplicates[0].source == "target"
        assert summary.extra_duplicate_target_count == 1  # 추가 중복 1건 (2번째만)
        assert summary.total_target == 2  # 원본 전체
        assert summary.unique_target_count == 1  # 유니크 시리얼 (SN001만)

    def test_multiple_duplicates(self):
        """여러 시리얼이 중복된 경우 - 모두 별도 리스트에 보고"""
        source = [
            EquipmentRecord("SN001", "Product A"),
            EquipmentRecord("SN001", "Product B"),  # 중복1
            EquipmentRecord("SN002", "Product C"),
            EquipmentRecord("SN002", "Product D"),  # 중복2
        ]
        target = []

        results, duplicates, summary, _, _ = compare_datasets(source, target)

        # 2개의 중복 그룹 감지
        assert len(duplicates) == 2
        duplicate_serials = {d.serial_number for d in duplicates}
        assert "SN001" in duplicate_serials
        assert "SN002" in duplicate_serials

        # 전체 추가 중복 레코드 수
        assert summary.extra_duplicate_source_count == 2  # (2-1) + (2-1) = 2
        assert summary.total_source == 4  # 원본 전체
        assert summary.unique_source_count == 2  # 유니크 시리얼 (SN001, SN002)

    def test_duplicate_first_record_used_in_comparison(self):
        """중복 시 첫 번째 레코드가 비교에 사용되는지 검증"""
        source = [
            EquipmentRecord("SN001", "Product A"),  # 첫 번째
            EquipmentRecord("SN001", "Product B"),  # 중복
        ]
        target = [EquipmentRecord("SN001", "Product A")]

        results, duplicates, summary, _, _ = compare_datasets(source, target)

        # 첫 번째 레코드(Product A)로 비교되어 매칭
        assert summary.matched_count == 1
        match_result = next(r for r in results if r.status == MatchStatus.MATCHED)
        assert match_result.source_product_name == "Product A"

    def test_large_dataset_performance(self):
        """대용량 데이터셋 성능 테스트 (10만건)"""
        source = [EquipmentRecord(f"SN{i:06d}", f"Product {i % 100}")
                  for i in range(100_000)]
        target = source.copy()

        import time
        start = time.time()
        results, duplicates, summary, _, _ = compare_datasets(source, target)
        elapsed = time.time() - start

        assert elapsed < 5.0  # 5초 이내 완료
        assert summary.matched_count == 100_000
        assert summary.extra_duplicate_source_count == 0  # 중복 없음
        assert summary.total_source == 100_000
        assert summary.unique_source_count == 100_000
```

### 8.3 통합 테스트

```python
# tests/integration/test_compare_flow.py

@pytest.fixture
def sample_csv_file(tmp_path):
    """테스트용 CSV 파일 생성"""
    # csv 모듈로 임시 CSV 생성
    ...

@pytest.fixture
def mock_db_data():
    """테스트용 DB 데이터 Mock"""
    ...

def test_full_comparison_flow(sample_csv_file, mock_db_data):
    """전체 비교 흐름 테스트"""
    usecase = CompareUseCase(
        source_port=CSVReader(sample_csv_file),
        target_port=MockDBReader(mock_db_data)
    )

    result = usecase.execute()

    assert result.summary is not None
    assert result.report_path.exists()
```

---

## 9. 구현 단계별 계획

### Phase 1: 프로젝트 기반 구축 (1일)
- [x] 프로젝트 구조 생성
- [x] pyproject.toml 설정
- [x] .env 로더 및 Settings 구현
- [x] 테스트 환경 구성 (pytest, conftest.py)

### Phase 2: 도메인 레이어 구현 (1일)
- [x] 데이터 모델 (EquipmentRecord, ComparisonResult, **DuplicateRecord** 등)
- [x] 예외 클래스
- [x] **중복 레코드 추출 함수** (_extract_duplicates) - Fault-Tolerant
- [x] Comparator 비교 알고리즘 (중복 분리 및 별도 반환)
- [x] Aggregator 집계 알고리즘
- [x] 단위 테스트 작성 (90%+ 커버리지, 중복 케이스 포함)

### Phase 3: 인프라스트럭처 레이어 구현 (1.5일)
- [x] CSVReader (Python 내장 csv 모듈)
- [x] DBReader (SQLAlchemy)
- [x] ReportWriter (Excel, CSV)
- [x] 단위 테스트 작성

### Phase 4: 애플리케이션 레이어 구현 (0.5일)
- [x] CompareUseCase
- [x] ReportUseCase
- [x] 통합 테스트

### Phase 5: CLI 구현 (0.5일)
- [x] Typer 기반 명령어
- [x] Rich 콘솔 출력
- [x] 진행률 표시

### Phase 6: 문서화 및 마무리 (0.5일)
- [x] README.md 작성
- [x] 사용 예시 문서
- [x] 최종 테스트 및 검증

**예상 총 소요 시간: 5일**

---

## 10. 기술 스택

### 10.1 핵심 라이브러리

| 라이브러리 | 버전 | 용도 |
|------------|------|------|
| Python | 3.11+ | 런타임 |
| pydantic | >=2.0 | 데이터 모델, 설정 |
| pydantic-settings | >=2.0 | .env 로딩 |
| sqlalchemy | >=2.0 | DB 연결 |
| pymysql | >=1.1 | MariaDB 드라이버 |
| csv | 내장 | CSV 파일 읽기 (빠른 성능) |
| openpyxl | >=3.1 | Excel 리포트 출력 |
| typer | >=0.9 | CLI |
| rich | >=13.0 | 콘솔 출력 |
| structlog | >=24.0 | 구조화된 로깅 |

### 10.2 개발/테스트 라이브러리

| 라이브러리 | 버전 | 용도 |
|------------|------|------|
| pytest | >=8.0 | 테스트 프레임워크 |
| pytest-cov | >=4.0 | 커버리지 리포트 |
| pytest-mock | >=3.12 | Mocking |

### 10.3 pyproject.toml

```toml
[project]
name = "lgu-data-compare"
version = "1.0.0"
description = "LGU+ CSV-DB Data Comparison Tool"
requires-python = ">=3.11,<3.13"
dependencies = [
    "pydantic>=2.0.0",
    "pydantic-settings>=2.0.0",
    "sqlalchemy>=2.0.0",
    "pymysql>=1.1.0",
    "openpyxl>=3.1.0",  # Excel 리포트 출력용
    "typer>=0.9.0",
    "rich>=13.0.0",
    "structlog>=24.0.0",
    "python-dotenv>=1.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "pytest-cov>=4.0.0",
    "pytest-mock>=3.12.0",
]

[project.scripts]
lgu-compare = "src.cli.commands:app"
```

---

## 11. 성능 고려사항

### 11.1 현재 설계의 적용 범위

| 데이터 규모 | 현재 설계 적합성 | 권장 사항 |
|-------------|------------------|-----------|
| ~10,000건 | ✅ 최적 (메모리 ~10MB) | 현재 Hash Map 방식 그대로 사용 |
| 10,000~100,000건 | ⚠️ 주의 (메모리 ~100MB) | 메모리 모니터링 필요 |
| 100,000건+ | ❌ 부적합 | **Two-Pointer 알고리즘으로 재설계 필요** (11.3 참고) |

### 11.2 현재 설계의 제약 (Hash Map 방식)

#### 장점
- **시간복잡도**: O(n + m) - 최고 속도
- **구현 단순성**: 직관적이고 유지보수 쉬움
- **랜덤 액세스**: 시리얼 번호로 즉시 조회 가능

#### 제약 (핵심)
- **공간복잡도**: **O(n + m)** - 전체 데이터를 메모리에 로드 필수
  - **이유**: `source_map = {r.serial_number: r for r in source_clean}` 구조상 전체 레코드를 딕셔너리로 변환해야 비교 가능
  - **결과**: CSV/DB에서 아무리 조금씩 읽어와도(Generator/Chunk), 비교 단계에서 결국 전체 메모리 사용
- **메모리 예상량**:
  - 1만 건: ~10 MB
  - 10만 건: ~100 MB
  - 100만 건: ~1 GB (실용적 한계)
- **병렬처리**: 현재 버전에서는 미포함 (필요시 향후 추가)

### 11.3 대용량 데이터 처리 전략 (향후 확장)

**⚠️ 중요**: 현재의 Hash Map 기반 비교 알고리즘(`compare_datasets`)은 **전체 메모리 로드가 필수**입니다. CSV/DB Reader에서 Generator나 Chunk 방식을 써도 `source_map`, `target_map` 딕셔너리를 만드는 순간 메모리에 전체 데이터가 올라갑니다.

진정한 메모리 최적화(O(1) 공간복잡도)를 위해서는 **비교 알고리즘 자체를 변경**해야 합니다.

#### Two-Pointer (투 포인터) 알고리즘 기반 재설계

**핵심 아이디어**: 양쪽 데이터를 **정렬**한 후, **한 줄씩 스트리밍**하면서 두 포인터로 비교

**알고리즘 개요**:
```python
# 1. 양쪽 데이터 정렬 (DB: ORDER BY, CSV: 사전 정렬)
source_stream = sorted_csv_reader("lgu_serial.csv")  # Generator
target_stream = sorted_db_reader("SELECT ... ORDER BY rcgnNo")  # Generator

# 2. Two-Pointer 비교 (메모리 O(1))
source_cursor = next(source_stream, None)
target_cursor = next(target_stream, None)

while source_cursor or target_cursor:
    if source_cursor and target_cursor:
        if source_cursor.serial_number == target_cursor.serial_number:
            # 매칭 또는 제품명 불일치 판정
            compare(source_cursor, target_cursor)
            source_cursor = next(source_stream, None)
            target_cursor = next(target_stream, None)
        elif source_cursor.serial_number < target_cursor.serial_number:
            # Source Only
            report_source_only(source_cursor)
            source_cursor = next(source_stream, None)
        else:
            # Target Only
            report_target_only(target_cursor)
            target_cursor = next(target_stream, None)
    elif source_cursor:
        report_source_only(source_cursor)
        source_cursor = next(source_stream, None)
    else:
        report_target_only(target_cursor)
        target_cursor = next(target_stream, None)
```

**필요 조건**:
1. **DB 쿼리 수정**: `ORDER BY a.rcgnNo` 추가
   ```sql
   SELECT a.rcgnNo, b.eqpmNm
   FROM EqpmTbl a
   JOIN CscoEqpmTbl b ON ...
   WHERE a.delYn <> 'y' AND b.delYn <> 'y'
     AND b.regDtime >= '2025-01-01'
     AND a.owns = '0'
     AND a.eqpmGrpCd NOT IN (52, 82)
     AND a.rcgnNo NOT LIKE '%VIP%'
   ORDER BY a.rcgnNo;  -- 정렬 필수!
   ```

2. **CSV 사전 정렬**: 대용량 파이썬 스크립트 작성 시 인메모리 정렬(`sorted()`)은 메모리를 한꺼번에 사용하므로 피하고, **OS 수준의 External Sort 명령어**를 호출하는 방식을 권장합니다.
   ```bash
   # O(1) 제너레이터 메모리 원칙을 지키기 위해 OS 디스크 기반 정렬명령어 활용
   # 시리얼번호(1번째 열) 기준으로 정렬 후 새 파일 생성
   sort -t, -k1 lgu_serial.csv -o lgu_serial_sorted.csv
   ```

3. **Generator 기반 Reader**:
   ```python
   def sorted_csv_reader(path: str) -> Iterator[EquipmentRecord]:
       """정렬된 CSV 파일을 한 줄씩 스트리밍"""
       with open(path, 'r', encoding='utf-8') as f:
           reader = csv.reader(f)
           next(reader)  # 헤더 스킵
           for row in reader:
               yield EquipmentRecord(serial_number=row[0], product_name=row[1])

   def sorted_db_reader(query: str) -> Iterator[EquipmentRecord]:
       """정렬된 DB 쿼리 결과를 한 줄씩 스트리밍"""
       with engine.connect() as conn:
           result = conn.execution_options(stream_results=True).execute(text(query))
           for row in result:
               yield EquipmentRecord(serial_number=row.rcgnNo, product_name=row.eqpmNm)
   ```

4. **도메인 계층 함수 재설계**: `compare_datasets_streaming(source_iter, target_iter)`
   - 입력: `Iterator[EquipmentRecord]` (리스트 아님!)
   - 출력: Generator로 비교 결과 한 줄씩 반환
   - 메모리: O(1) (현재 커서 2개만 유지)

**성능 비교**:

| 방식 | 시간복잡도 | 공간복잡도 | 100만 건 메모리 | 적용 시점 |
|------|------------|------------|----------------|-----------|
| **현재 (Hash Map)** | O(n + m) | **O(n + m)** | ~1 GB | 10만 건 이하 |
| **Two-Pointer** | O(n log n + m log m) | **O(1)** | ~10 MB | 10만 건 이상 |

> **참고**: Two-Pointer 방식은 정렬 비용(O(n log n))이 추가되지만, 데이터가 이미 정렬되어 있거나 DB 인덱스가 있으면 정렬 비용은 무시할 수 있습니다.

**언제 전환해야 하는가?**:
- **현재 Hash Map 방식**: 데이터 10만 건 이하, 메모리 여유 있을 때
- **Two-Pointer 방식**: 데이터 10만 건 이상, 메모리 제약 있을 때 (예: 클라우드 환경, 컨테이너)

---

## 12. 확장성 고려사항

### 12.1 향후 확장 시나리오

| 시나리오 | 현재 설계의 대응 |
|----------|------------------|
| 다른 소스 추가 (CSV, API) | `EquipmentDataPort` 인터페이스 구현 |
| 다른 DB 추가 (Center) | `DBReader` 파라미터화 (system_id) |
| 비교 필드 추가 | `EquipmentRecord` 필드 확장 |
| 다른 출력 형식 | `ReportWriter` 전략 패턴 |

### 12.2 확장 예시: Center DB 추가

```python
# 기존 코드 변경 없이 새 어댑터만 추가
class CenterDBReader(EquipmentDataPort):
    """Center DB용 어댑터"""

    def __init__(self, connection_string: str):
        self.connection_string = connection_string

    def load_records(self) -> List[EquipmentRecord]:
        # Center DB 전용 쿼리
        query = """
            SELECT rcgnNo, eqpmNm
            FROM EqpmTbl a
            JOIN CscoEqpmTbl b ON ...
            WHERE a.delYn <> 'y' AND b.delYn <> 'y'
              AND b.regDtime >= '2025-01-01'
              AND a.owns = '0'
              AND a.eqpmGrpCd NOT IN (52, 82)
              AND a.rcgnNo NOT LIKE '%VIP%'
        """
        ...
```

### 12.3 설정 파일 확장

```yaml
# config/compare.yaml (향후)
sources:
  - type: csv
    path: lgu_serial.csv
    columns:
      serial: A
      product: B

  - type: database
    system_id: LGU
    connection: ${LGU_DB_CONNECTION}

targets:
  - type: database
    system_id: LGU
    connection: ${LGU_DB_CONNECTION}

output:
  format: excel  # excel, csv, json
  path: output/
```

---

## 13. 실행 방법

### 13.1 기본 실행

```bash
cd d:\02.project\21.asset_mgr_system\ams\compare_data

# 가상환경 활성화
.venv\Scripts\activate  # Windows

# 의존성 설치
pip install -e ".[dev]"

# 비교 실행
python -m src compare

# 또는 CLI 명령어
lgu-compare
```

### 13.2 CLI 옵션

```bash
# 기본 실행 (Excel 리포트 출력)
lgu-compare

# CSV 형식으로 출력
lgu-compare --format csv

# 특정 출력 디렉토리 지정
lgu-compare --output-dir ./reports

# 상세 로그 출력
lgu-compare --verbose

# 드라이런 (DB 연결만 테스트)
lgu-compare --dry-run
```

---

## 14. 체크리스트

### 14.1 구현 전 확인사항
- [ ] .env 파일에 DB 접속 정보 확인
- [ ] lgu_serial.csv 파일 존재 및 형식 확인 (UTF-8 인코딩)
- [ ] DB 테이블 접근 권한 확인
- [ ] Python 3.11+ 설치 확인

### 14.2 테스트 확인사항
- [ ] 단위 테스트 80%+ 커버리지
- [ ] **중복 시리얼 처리 테스트** (Fault-Tolerant, 첫 번째 레코드 사용 검증)
- [ ] 엣지 케이스 테스트 (빈 데이터, 특수문자 등)
- [ ] 실제 데이터로 통합 테스트
- [ ] 성능 테스트 (예상 데이터 규모)

### 14.3 배포 확인사항
- [ ] README.md 완성
- [ ] .gitignore 설정 (output/, .env)
- [ ] 예시 실행 결과 문서화

---

**작성일**: 2026-03-03
**작성자**: Prometheus (Planning Consultant)
**버전**: 1.0
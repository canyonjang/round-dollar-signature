# 리비전 분석 실행 가이드 (BigQuery 콘솔)

목표: 심사자 요구(회귀식·세분화 셀·일 단위 군집 표준오차, 라벨 기반 검증, 금액 가중, Tron 재현)를
**원천 데이터 스캔 최소 횟수**로 처리합니다. 비싼 쿼리는 R01(이더리움 1회)과 R03(Tron 1개월) 두 개뿐이고,
나머지는 작은 집계 테이블만 읽어 사실상 무료입니다.

| 순서 | 파일 | 비용 | 결과 |
|---|---|---|---|
| 1 | (업로드) `data/labels_eth_mainnet.csv` | 무료 | 테이블 `labels_eth` |
| 2 | `R00_schema_check_tron_polygon.sql` | 거의 0 | Tron/Polygon 컬럼, contracts 최신성 확인 |
| 3 | `R01_build_cells_eth_2025.sql` | **큼 (1회)** | 테이블 `eth_cells2025` (1GB 미만) |
| 4 | `R02a_cells_day.sql` | 거의 0 | `R02a_cells_day.csv` |
| 5 | `R02b_cells_attributes.sql` | 거의 0 | `R02b_cells_attr.csv` |
| 6 | `R03_tron_usdt_month.sql` | **중간 (1개월)** | `R03_tron_cells.csv` |
| 7 | `R04_polygon_month_optional.sql` | 중간, 선택 | `R04_polygon_cells.csv` |

## 0. 준비 (한 번만)

1. BigQuery 콘솔에서 사용할 프로젝트를 고릅니다. 결제 계정이 없는 **샌드박스**여도 됩니다
   (쿼리 월 1TB 무료, 저장 10GB, 테이블은 60일 뒤 자동 삭제).
2. 프로젝트 옆 ⋮ → **Create dataset** → Dataset ID `rds_revision`, Location **US** (공개 데이터가 US에 있음).
3. **비용 안전장치**: 쿼리 편집기 상단 **More → Query settings → Advanced options →
   Maximum bytes billed**에 `800000000000`(800GB)을 넣습니다. 이 한도를 넘는 쿼리는 실행되지 않고
   오류만 나므로 요금 사고가 나지 않습니다.
4. 모든 SQL 파일의 `YOUR_PROJECT`를 실제 프로젝트 ID로 바꿉니다(편집기에서 찾아 바꾸기).

## 1. 라벨 테이블 업로드

`rds_revision` 옆 ⋮ → **Create table** → Source: **Upload** → `labels_eth_mainnet.csv` 선택 →
Table 이름 `labels_eth` → Schema는 **자동 감지를 끄고** "텍스트로 수정"에 `address:STRING,category:STRING,name_tag:STRING` 입력 → Advanced options에서 **Header rows to skip = 1** → Create.
(자동 감지를 쓰면 `0x…` 주소가 숫자(FLOAT64)로 잘못 인식되어 라벨이 매칭되지 않습니다.)
(Etherscan 태그 공개본 eth-labels, 86,924개 주소: 거래소 30,703 / DeFi·브리지·MEV 19,681 /
결제대행사 42 / 발행사 14 / 기타 36,484)

## 2. R00 실행 (거의 무료)

결과에서 Tron과 Polygon `logs`의 `address`, `topics`, `data`, `transaction_hash`, `block_timestamp`가
보이고 `topics`가 `ARRAY<STRING>`이면 R03/R04를 그대로 쓰면 됩니다. 다르면 결과를 캡처해서 보내 주세요.
파일 맨 아래 두 번째 쿼리(`latest_contract_creation`)도 실행해 2025년 12월 이후 날짜가 나오는지 확인합니다. 그보다 이르면 EOA/컨트랙트 구분이 부정확해지므로 알려 주세요.

## 3. R01 실행 (유일하게 큰 이더리움 쿼리)

1. 쿼리를 붙여넣으면 편집기 오른쪽 위에 **"This query will process ___ GB"** 가 뜹니다(드라이런, 무료).
   **이 숫자를 먼저 알려 주세요.** 800GB 한도 안이면 그대로 실행하면 됩니다.
2. 실행 후 파일 맨 아래 주석의 **Sanity check** 쿼리를 실행합니다. 결과가 기존
   `data/02_single_multi.csv`(예: USDT single 70,461,151건, 30.21%)와 **정확히 같아야** 합니다.
   다르면 다음 단계로 가지 말고 결과를 보내 주세요.

## 4–5. R02a, R02b 실행 → CSV 저장

각각 실행 후 **Save results → CSV (local file)**. 파일이 커서 로컬 저장이 안 되면 **CSV (Google Drive)**.
파일 이름: `R02a_cells_day.csv`, `R02b_cells_attr.csv`.

## 6. R03 Tron (2025년 6월 한 달)

Tron 테이블은 **월 단위 파티션**이라 하루만 골라도 한 달치가 과금됩니다. 그래서 한 달이 최소 단위입니다.
드라이런 숫자를 확인하고 실행 → `R03_tron_cells.csv`로 저장.
숫자가 크게 나오면(예: 500GB 이상) 실행 전에 알려 주세요.

## 7. R04 Polygon (선택)

R03까지 무료 한도 안에서 끝났고 여유가 있을 때만. USDC를 저수수료 체인에서 보여줄 수 있어 R3에 대한 답이 강해집니다.

## 8. 결과 전달

CSV 4개(또는 3개)를 이 대화에 올려 주시면 표·그림·응답서 문장으로 바로 이어갑니다.
직접 돌리려면 `code/` 폴더에서:

```bash
pip install pandas numpy statsmodels
python test_cellreg.py     # 회귀 엔진 검증(기존 Table 1 재현 + 미시 OLS와 일치 확인)
python rev_tables.py       # figures/rev/ 에 표 T1–T5와 revision_results.md 생성
```

## 9. 끝난 뒤 정리

`eth_cells2025`는 1GB 미만이라 저장비가 거의 없지만, 게재 확정 후 삭제해도 됩니다
(재현 패키지에는 CSV가 들어가므로 테이블이 필요 없음).

## 어느 심사자 지적에 쓰이는가

| 산출물 | 대응 |
|---|---|
| T1 회귀식·표준 표 형식, 일 FE, issuer×size×day FE, 일 군집 SE, 금액 가중 | R1 #1–#3, 에디터 |
| T2 표본 제한 강건성(거래소·발행사 제외, 비라벨만, 상위 1,000 주소 제외, EOA 간, 직접호출 vs 컨트랙트 경유) | R1 #3, R2, R3 #1·#3, R4 #2 |
| T3 상대방 구성 + 결제대행사(PSP) 정답 라벨에서의 whole-dollar·whole-cent·$X.99 비율 | R3 (a) 검증, R1 #4(4.99 가격), R4 #2 |
| T4 건수 vs 금액 가중 비율 | R4 #1 |
| T5 Tron(·Polygon) 재현, 같은 달 이더리움과 비교, placebo 사다리 | R1 #5, R3 #4, R4 #3, R5 |

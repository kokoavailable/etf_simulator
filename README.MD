## 프로젝트 설명

채권 수익률을 평가해 음의 구간에는 방어자산인 단기채 etf, 양의 구간에는 QQQ, GLD, SPY 중 수익률이 높은 상위 두개에 투자하는 전략 프로젝트입니다. 이를 위해 데이터를 수집및 가공하고, 결과를 API로 제공합니다.

## 사용방법

### 1. 의존성 설치 및 환경설정

#### [Local]
프로젝트 폴더로 이동 후 아래 명령어 실행:
```sh
pip install -r requirements.txt
```

#### [Dev]
Docker 환경에서 실행:
```sh
docker compose up -d --build
```
실행 시 FastAPI 컨테이너와 함께 DB 컨테이너, 스크립트가 백그라운드에서 실행됩니다.

---

### 2. Docker 컨테이너 관리

#### 모든 컨테이너 중지
```sh
docker stop $(docker ps -q) && docker rm $(docker ps -aq)
```

#### 모든 컨테이너 삭제
```sh
docker rm $(docker ps -aq)
```

#### 사용하지 않는 컨테이너, 네트워크, 이미지 삭제
```sh
docker system prune -a
```

---

### 3. Postgres 세팅 (Mac)

#### [Local]
```sh
brew install postgresql
brew services start postgresql
```

슈퍼유저로 접속:
```sh
psql -U postgres
```

사용자 생성 및 DB 설정:
```sql
CREATE USER '원하는사용자' WITH PASSWORD '원하는비밀번호';
CREATE DATABASE '원하는사용자' OWNER '원하는비밀번호';
```

GUI 툴 연결 or 터미널 접속:
```sh
psql -U '사용자' -h 127.0.0.1 -p 5432 -d '비밀번호'
```

#### [Dev]
```sh
docker compose up -d --build
```

Postgres 컨테이너 내부에서 접속:
```sh
docker exec -it postgres_db psql -U backtest -d backtest
```

---

### 4. Script 실행 및 Cronjob 설정

#### [Local]
```sh
cd scripts
python3 fetch_stock_daily.py
python3 save_csv.py
```

#### [Dev] (Docker 에서 Cron 스케줄링 설정)
즉시 실행:
```sh
docker compose run --rm scripts python /app/scripts/fetch_stock_daily.py
```
```sh
docker compose run --rm scripts python /app/scripts/save_csv.py
```

---

### 5. API 서버 실행 (Mac)

#### [Local]
```sh
cd app
uvicorn main:app --reload
```
Swagger 문서 확인:
[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

#### [Dev]
Swagger 문서 확인:
[http://0.0.0.0:8000/docs](http://0.0.0.0:8000/docs)

---

### 6. 테스트 실행
```python
"""
>>> add(2, 3)
    5
>>> add(-1, 1)
    0
"""
```

해당형식으로 독스트링에 테스트 케이스가 추가 돼 있습니다. 핵심적인 service 로직에 테스트 케이스가 적용되어 있습니다.

```python
if __name__ == "__main__":
    import doctest
    doctest.testmod()
```

해당 파일에 다음과 같은 코드가 추가되어 있다면, 

```sh
python -m doctest -v app/services/calculation.py
```

다음과 같은 명령어로 해당 파일을 실행시켜 테스트 케이스 검증이 가능합니다.
---

## ETC

### 프로젝트 성과 및 후기

본 프로젝트는 FastAPI 서버와 데이터 수집을 위한 스크립트로 구성되었습니다.

#### 성과
1. Python 코드 컨벤션을 준수하였으며, `pylint` 검사 결과 10.00에 수렴.
2. 실행 환경을 로컬 환경과 Docker 자동화 배포 환경(개발기)으로 분리.
3.  주요 엣지 케이스(28~31일, 휴장일 데이터 삽입, 매매일 계산 등)를 고려하여 적극적으로  반영.
4. 로깅 최적화(`%s lazy`).
5. doctest 를 활용한 edge case 테스트

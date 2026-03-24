# Apache Paimon Hands-on Lab

Apache Paimon의 실시간 스트리밍 데이터 파이프라인 구축 Quickstart

## Apache Paimon이란?

Flink Table Store에서 출발하여 2024년 ASF Top-Level Project로 승격된 **streaming-first 데이터 레이크 포맷**.

LSM Tree 기반 스토리지 엔진으로 고빈도 실시간 upsert를 효율적으로 처리하며, 네이티브 changelog(`+I`/`-U`/`+U`/`-D`) 시맨틱을 제공함.

## 아키텍처

```
Wikipedia SSE  →  Python Bridge  →  Kafka (KRaft)  →  Flink SQL  →  Paimon (MinIO)  →  DuckDB
```

| 컴포넌트 | 역할 |
|----------|------|
| Wikipedia SSE | 위키피디아 실시간 편집 이벤트 소스 |
| Python Bridge | SSE → Kafka 브릿지 (`sse_bridge.py`) |
| Kafka | KRaft 모드 메시지 브로커 |
| Flink SQL | 스트리밍 ETL (Kafka → Paimon) |
| Paimon (MinIO) | S3 호환 스토리지의 LSM 기반 데이터 레이크 |
| DuckDB | PyPaimon을 통한 분석 (DW) |

## 사전 준비

- Docker Desktop 4.x+
- Python 3.9+
- uv (Python 패키지 매니저)

## Quick Start

### 1. 인프라 실행

```bash
docker compose up -d --build
```

### 2. SSE → Kafka 브릿지 실행

```bash
uv run python sse_bridge.py
```

### 3. Flink SQL 테이블 생성

```bash
docker exec -it flink-jobmanager ./bin/sql-client.sh embedded
```

아래 SQL을 **한 문장씩** 실행합니다:

```sql
CREATE CATALOG paimon_catalog WITH (
  'type' = 'paimon',
  'warehouse' = 's3://warehouse/paimon',
  's3.endpoint' = 'http://minio:9000',
  's3.access-key' = 'admin',
  's3.secret-key' = 'password123',
  's3.path.style.access' = 'true'
);

USE CATALOG paimon_catalog;

CREATE DATABASE IF NOT EXISTS wikidb;

USE wikidb;
```

### 4. DuckDB에서 조회 (PyPaimon)

```bash
uv run python paimon_example.py
```

## 서비스 포트

| 서비스 | URL |
|--------|-----|
| MinIO Console | http://localhost:9001 (admin / password123) |
| Flink Web UI | http://localhost:8081 |
| Kafbat UI | http://localhost:8080 |
| Kafka (호스트 접근) | localhost:9094 |

## 참고 자료

- [Apache Paimon 공식 문서](https://paimon.apache.org/docs/master/)
- [Jack Vanlightly - Understanding Apache Paimon Consistency Model](https://jack-vanlightly.com/analyses/2024/7/3/understanding-apache-paimon-consistency-model-part-1)
- [Naver D2 - Apache Paimon 소개](https://d2.naver.com/helloworld/2766731)

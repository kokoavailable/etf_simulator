"""
FastAPI 메인 애플리케이션 모듈.
이 모듈은 FastAPI 서버를 실행하는 진입점입니다.
"""
from mangum import Mangum # AWS Lambda에서 FastAPI를 실행하기 위한 라이브러리
from fastapi import FastAPI # FastAPI 웹 프레임워크
from common.common import engine # SQLAlchemy 엔진 (DB 연결시 사용)
from model.model import Base # SQLAlchemy 모델의 베이스 클래스
from api.v1.routers import router

app = FastAPI() # FastAPI 객체를 생성한다.

Base.metadata.create_all(bind=engine) # Model. metadata 에 저장된 정보를 바탕으로 데이터베이스 테이블을 생성한다.

app.include_router(router) # API 라우터를 FastAPI 애플리케이션에 추가한다.

# 헬스 체크 API
# 도커 환경에서 컨테이너 상태를 주기적으로 확인하는데 사용한다.
@app.get("/")
async def health_check():
    """
    서버 상태 확인 API, 도커 컨테이너 헬스체크 용
    """
    return {"status": "OK"}

handler = Mangum(app) # AWS Lambda에서 FastAPI를 실행하기 위한 핸들러

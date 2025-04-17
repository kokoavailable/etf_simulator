"""
FastAPI 메인 애플리케이션 모듈.
이 모듈은 FastAPI 서버를 실행하는 진입점입니다.
"""
import sys
from pathlib import Path

# Path 객체로 파일 경로를 받은뒤, 해당 파일의 부모 디렉토리를 sys.path에 추가한다.
sys.path.append(str(Path(__file__).resolve().parent)) # pylint: disable=wrong-import-position

from mangum import Mangum # AWS Lambda에서 FastAPI를 실행하기 위한 라이브러리
from fastapi import FastAPI
from common.common import engine
from model.model import Base
from api.v1.routers import router

app = FastAPI() # FastAPI 객체를 생성한다.

Base.metadata.create_all(bind=engine) # Model. metadata 에 저장된 정보를 바탕으로 데이터베이스 테이블을 생성한다.

app.include_router(router) # API 라우터를 FastAPI 애플리케이션에 추가한다.

@app.get("/")
async def health_check():
    """
    서버 상태 확인 API, 도커 컨테이너 헬스체크 용
    """
    return {"status": "OK"}

handler = Mangum(app) # AWS Lambda에서 FastAPI를 실행하기 위한 핸들러

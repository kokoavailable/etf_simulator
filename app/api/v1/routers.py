"""
api.v1.routers 모듈

이 모듈은 FastAPI 라우터를 정의하며, API 엔드포인트를 구성하는 역할을 합니다.
각 엔드포인트는 api.v1.endpoints에서 정의된 라우터를 포함합니다.

/v1/api/calculation: 계산 관련 API 엔드포인트를 관리하는 라우터
"""
from fastapi import APIRouter
from api.v1.endpoints import calculation

router = APIRouter()

router.include_router(calculation.router, prefix="/v1/api/calculation", tags=["v1"])

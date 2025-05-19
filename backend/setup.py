from setuptools import setup, find_packages

setup(
    name="etf_simulator",
    version="0.1.0",
    packages=find_packages(where="."),
    package_dir={"": "."},
    install_requires=[
        "fastapi",
        "sqlalchemy",
        "mangum",
        # 필요시 추가
    ],
)
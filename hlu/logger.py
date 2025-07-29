import logging
import os

def setup_logger():
    # 로그 디렉토리 생성 (존재하지 않으면)
    os.makedirs("logs", exist_ok=True)
    # 로그파일 생성
    logger = logging.getLogger("HLU")
    logger.setLevel(logging.INFO)

    # 이 밑으로는 로그 작성시 필요한 기능
    # 파일 핸들러 및 포매터 설정
    file_handler = logging.FileHandler("logs/hlu.log")
    formatter = logging.Formatter('[%(asctime)s] %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)

    # 핸들러가 없을 때만 추가
    if not logger.handlers:
        logger.addHandler(file_handler)

    # 로거 반환
    return logger

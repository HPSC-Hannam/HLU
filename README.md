# HLU

HPSC Linux Updater

python3 hlu/main.py check = 업데이트 체크

python3 hlu/main.py update --download-only = 업데이트 다운로드만 함

python3 hlu/main.py update = 업데이트 다운로드 후 설치

python3 hlu/main.py update --yes = 업데이트 시 사용자 확인 건너뛰기

python3 hlu/main.py update --dry-run = 업데이트 테스트

python3 hlu/main.py monitor = 1분마다 check 수행

python3 hlu/main.py monitor --interval INTERVAL = INTERVAL에 집어넣은 초 간격으로 check 수행

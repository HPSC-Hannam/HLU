import subprocess
import re
import logging
import subprocess
import re
import logging
import time
from datetime import datetime

def get_upgradable_packages(logger):
    """업데이트 가능한 패키지 리스트 반환"""
    # apt 명령어로 업그레이드 가능한 패키지 목록 조회
    result = subprocess.run(['apt', 'list', '--upgradable'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if result.returncode != 0:
        # 패키지 목록 조회 실패 시
        logger.error("Failed to fetch upgradable package list: %s", result.stderr)
        return []

    lines = result.stdout.strip().split('\n')
    if len(lines) <= 1:
        # 업그레이드 가능한 패키지가 없는 경우
        return []

    packages = []
    for line in lines[1:]:  # 첫 번째 줄은 "Listing..."
        parts = line.split()
        if len(parts) >= 1:
            pkg_name = parts[0].split('/')[0]  # 패키지명 추출
            packages.append(pkg_name)

    return packages

def check_updates(logger):
    """업데이트 가능한 패키지 출력"""
    logger.info("Checking for available updates...")
    packages = get_upgradable_packages(logger)

    if not packages:
        # 모든 패키지가 최신인 경우
        print("[✓] All packages are up to date.")
        logger.info("No packages to update.")
        return

    # 패키지 정보 헤더 출력
    print(f"{'Package':30}{'Installed':20}{'Candidate'}")
    print("-" * 70)

    for pkg in packages:
        # 설치된 버전 조회
        dpkg = subprocess.run(['dpkg-query', '-W', '-f=${Version}', pkg],
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        installed = dpkg.stdout.strip() if dpkg.returncode == 0 else 'N/A'

        # 업그레이드 후보 버전 조회
        policy = subprocess.run(['apt-cache', 'policy', pkg],
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        m = re.search(r'Candidate:\s*(\S+)', policy.stdout)
        candidate = m.group(1) if m else 'unknown'

        # 패키지명, 설치버전, 후보버전 출력
        print(f"{pkg:30}{installed:20}{candidate}")

    # 업그레이드 가능한 패키지 개수 로그 남김
    logger.info(f"{len(packages)} packages can be upgraded.")

def monitor_updates(logger, interval=60):
    """1분마다 주기적으로 check 수행"""
    logger.info("Starting background monitor loop...")

    while True:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"\n[{now}] Checking for updates...")

        packages = get_upgradable_packages(logger)
        if packages:
            # 업그레이드 가능한 패키지가 있을 때 메시지
            print(f"[!] {len(packages)} packages can be upgraded:")
            for pkg in packages:
                print(f"  - {pkg}")
            logger.info(f"{len(packages)} upgradable packages detected.")
        else:
            # 업그레이드 가능한 패키지가 없을 때 메시지
            print("[✓] No updates available.")
            logger.info("No packages to update.")

        time.sleep(interval)

def update_packages(logger, download_only=False, auto_confirm=False, dry_run=False):
    logger.info(f"Update started: download_only={download_only}, auto_confirm={auto_confirm}, dry_run={dry_run}")

    if dry_run:
        # 드라이런 모드: 실제 명령 실행하지 않음
        print("[DRY RUN] No commands will be executed.")
        if download_only:
            print("Command: sudo apt-get -d upgrade -y")
        else:
            print("Command sequence:")
            print("  sudo apt-get update")
            print("  sudo apt-get upgrade -y")
        logger.info("Dry run completed.")
        return

    if download_only:
        # 다운로드만 수행하는 경우 메시지
        logger.info("Downloading updates only...")
        try:
            result = subprocess.run(['sudo', 'apt-get', '-d', 'upgrade', '-y'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if result.returncode == 0:
                # 다운로드 성공시 메시지
                logger.info("Package download succeeded")
                print("[✔] Package download complete.")
            else:
                # 다운로드 실패시 메시지
                logger.error("Package download failed:\n%s", result.stderr)
                print("[!] Download failed:\n", result.stderr)
        except Exception as e:
            # 예외 발생 시 메시지
            logger.exception("Exception during download: %s", str(e))
            print("[!] Unexpected error during download.")
        return

    # 설치 경로
    if not auto_confirm:
        # 사용자에게 설치 여부 확인
        print("[!] Package installation will update your system.")
        confirm = input("Proceed with installation? [y/N]: ").strip().lower()
        if confirm != 'y':
            # 사용자가 취소한 경우 메시지
            print("[i] Installation cancelled.")
            logger.info("User cancelled installation.")
            return

    logger.info("Running apt-get update...")
    update_result = subprocess.run(['sudo', 'apt-get', 'update'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if update_result.returncode != 0:
        # 패키지 목록 갱신 실패시 메시지
        logger.error("apt-get update failed:\n%s", update_result.stderr)
        print("[!] Failed to update package lists:\n", update_result.stderr)
        return

    logger.info("Running apt-get upgrade...")
    upgrade_result = subprocess.run(['sudo', 'apt-get', 'upgrade', '-y'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if upgrade_result.returncode == 0:
        # 설치 성공시 메시지
        logger.info("Package installation succeeded")
        print("[✔] Installation complete.")
    else:
        # 설치 실패시 메시지
        logger.error("Package installation failed:\n%s", upgrade_result.stderr)
        print("[!] Installation failed:\n", upgrade_result.stderr)
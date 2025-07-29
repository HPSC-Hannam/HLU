import subprocess
import re
import logging

def check_updates(logger):
    logger.info("Gathering upgradable package version status...")

    # 1) 설치된 모든 패키지와 현재 버전 목록 취득
    dpkg = subprocess.run(
        ['dpkg-query', '-W', '-f=${binary:Package}\\t${Version}\\n'],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )
    if dpkg.returncode != 0:
        logger.error("dpkg-query failed: %s", dpkg.stderr)
        print("[!] Failed to retrieve installed package list.")
        return

    installed_lines = dpkg.stdout.splitlines()

    # 2) 헤더 출력
    header = f"{'Package':30}{'Installed':20}{'Candidate'}"
    print(header)
    print('-' * len(header))

    # 3) 각 패키지별로 apt-cache policy 실행하여 Candidate 버전 파싱
    for line in installed_lines:
        pkg, installed_ver = line.split('\t', 1)
        policy = subprocess.run(
            ['apt-cache', 'policy', pkg],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        if policy.returncode != 0:
            logger.warning("apt-cache policy failed for %s: %s", pkg, policy.stderr)
            continue

        m = re.search(r'Candidate:\s*(\S+)', policy.stdout)
        candidate = m.group(1) if m and m.group(1) != '(none)' else None

        # 4) 설치 버전과 후보 버전이 다르고 후보가 None이 아닐 때만 출력
        if candidate and candidate != installed_ver:
            print(f"{pkg:30}{installed_ver:20}{candidate}")

    logger.info("Upgradable package version status displayed.")

def download_updates(logger):
    logger.info("Attempting to download upgradable packages...")
    try:
        result = subprocess.run(['sudo', 'apt-get', '-d', 'upgrade', '-y'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode == 0:
            logger.info("Package download succeeded")
            print("[✔] Package download complete.")
        else:
            logger.error("Package download failed:\n%s", result.stderr)
            print("[!] Download failed:\n", result.stderr)
    except Exception as e:
        logger.exception("Exception occurred during download: %s", str(e))
        print("[!] Unexpected error during download.")

def install_updates(logger, auto_confirm=False):
    logger.info("Preparing to install downloaded updates...")

    if not auto_confirm:
        print("[!] Package installation may change your system.")
        confirm = input("Proceed with installation? [y/N]: ").strip().lower()
        if confirm != 'y':
            print("[i] Installation cancelled.")
            logger.info("User cancelled installation.")
            return

    logger.info("Starting package installation...")
    try:
        result = subprocess.run(['sudo', 'apt-get', 'upgrade', '-y'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode == 0:
            logger.info("Package installation succeeded")
            print("[✔] Installation complete.")
        else:
            logger.error("Package installation failed:\n%s", result.stderr)
            print("[!] Installation failed:\n", result.stderr)
    except Exception as e:
        logger.exception("Exception during install: %s", str(e))
        print("[!] Unexpected error during installation.")

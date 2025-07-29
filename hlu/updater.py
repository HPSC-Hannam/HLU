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

def update_packages(logger, download_only=False, auto_confirm=False, dry_run=False):
    logger.info(f"Update started: download_only={download_only}, auto_confirm={auto_confirm}, dry_run={dry_run}")

    if dry_run:
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
        logger.info("Downloading updates only...")
        try:
            result = subprocess.run(['sudo', 'apt-get', '-d', 'upgrade', '-y'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if result.returncode == 0:
                logger.info("Package download succeeded")
                print("[✔] Package download complete.")
            else:
                logger.error("Package download failed:\n%s", result.stderr)
                print("[!] Download failed:\n", result.stderr)
        except Exception as e:
            logger.exception("Exception during download: %s", str(e))
            print("[!] Unexpected error during download.")
        return

    # Install path
    if not auto_confirm:
        print("[!] Package installation will update your system.")
        confirm = input("Proceed with installation? [y/N]: ").strip().lower()
        if confirm != 'y':
            print("[i] Installation cancelled.")
            logger.info("User cancelled installation.")
            return

    logger.info("Running apt-get update...")
    update_result = subprocess.run(['sudo', 'apt-get', 'update'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if update_result.returncode != 0:
        logger.error("apt-get update failed:\n%s", update_result.stderr)
        print("[!] Failed to update package lists:\n", update_result.stderr)
        return

    logger.info("Running apt-get upgrade...")
    upgrade_result = subprocess.run(['sudo', 'apt-get', 'upgrade', '-y'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if upgrade_result.returncode == 0:
        logger.info("Package installation succeeded")
        print("[✔] Installation complete.")
    else:
        logger.error("Package installation failed:\n%s", upgrade_result.stderr)
        print("[!] Installation failed:\n", upgrade_result.stderr)
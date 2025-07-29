import argparse
from logger import setup_logger
from updater import check_updates, update_packages, monitor_updates

def main():
    # 로거 설정
    logger = setup_logger()

    # 명령행 인자 파서 생성
    parser = argparse.ArgumentParser(prog='HLU', description='HPSC Linux Updater')
    subparsers = parser.add_subparsers(dest='command', help='Sub-commands')

    # 'check' 서브커맨드: 업데이트 확인
    parser_check = subparsers.add_parser('check', help='Check for package updates')

    # 'update' 서브커맨드: 업데이트 다운로드/설치
    parser_update = subparsers.add_parser('update', help='Download and/or install updates')
    parser_update.add_argument('--download-only', action='store_true', help='Only download updates, do not install')
    parser_update.add_argument('--yes', action='store_true', help='Automatically confirm installation')
    parser_update.add_argument('--dry-run', action='store_true', help='Show what would be done without executing')

    # 'monitor' 서브커맨드: 백그라운드 모니터 실행
    parser_monitor = subparsers.add_parser('monitor', help='Run background update monitor')
    parser_monitor.add_argument('--interval', type=int, default=60, help='Check interval in seconds (default: 60)')

    # 인자 파싱
    args = parser.parse_args()

    # 명령에 따라 함수 실행
    if args.command == 'check':
        check_updates(logger)
    elif args.command == 'update':
        update_packages(logger, download_only=args.download_only, auto_confirm=args.yes, dry_run=args.dry_run)
    elif args.command == 'monitor':
        monitor_updates(logger, interval=args.interval)
    else:
        # 명령이 없을 경우 도움말 출력
        parser.print_help()

# 메인 함수 실행
if __name__ == '__main__':
    main()

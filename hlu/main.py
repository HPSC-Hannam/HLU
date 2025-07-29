import argparse
from logger import setup_logger
from updater import check_updates, update_packages, monitor_updates

def main():
    logger = setup_logger()

    parser = argparse.ArgumentParser(prog='HLU', description='HPSC Linux Updater')
    subparsers = parser.add_subparsers(dest='command', help='Sub-commands')

    parser_check = subparsers.add_parser('check', help='Check for package updates')

    parser_update = subparsers.add_parser('update', help='Download and/or install updates')
    parser_update.add_argument('--download-only', action='store_true', help='Only download updates, do not install')
    parser_update.add_argument('--yes', action='store_true', help='Automatically confirm installation')
    parser_update.add_argument('--dry-run', action='store_true', help='Show what would be done without executing')
    parser_monitor = subparsers.add_parser('monitor', help='Run background update monitor')
    parser_monitor.add_argument('--interval', type=int, default=60, help='Check interval in seconds (default: 60)')

    args = parser.parse_args()

    if args.command == 'check':
        check_updates(logger)
    elif args.command == 'update':
        update_packages(logger, download_only=args.download_only, auto_confirm=args.yes, dry_run=args.dry_run)
    elif args.command == 'monitor':
        monitor_updates(logger, interval=args.interval)
    else:
        parser.print_help()

if __name__ == '__main__':
    main()

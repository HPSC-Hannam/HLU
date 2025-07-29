import argparse
from logger import setup_logger
from updater import check_updates, download_updates, install_updates

def main():
    logger = setup_logger()

    parser = argparse.ArgumentParser(prog='HLU', description='HPSC Linux Updater')
    subparsers = parser.add_subparsers(dest='command', help='Sub-commands')

    parser_check = subparsers.add_parser('check', help='Check for package updates')
    parser_download = subparsers.add_parser('download', help='Download available updates')
    
    parser_install = subparsers.add_parser('install', help='Install downloaded updates')
    parser_install.add_argument('--yes', action='store_true', help='Auto-confirm package installation')

    args = parser.parse_args()

    if args.command == 'check':
        check_updates(logger)
    elif args.command == 'download':
        download_updates(logger)
    elif args.command == 'install':
        install_updates(logger, auto_confirm=args.yes)
    else:
        parser.print_help()

if __name__ == '__main__':
    main()

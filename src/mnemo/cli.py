import sys


def main() -> None:
    if len(sys.argv) > 1 and sys.argv[1] == "import":
        from mnemo.import_cli import main as import_main

        import_main(sys.argv[2:])
        return

    if len(sys.argv) > 1 and sys.argv[1] == "graph":
        from mnemo.graph_cli import main as graph_main

        graph_main(sys.argv[2:])
        return

    if len(sys.argv) > 1 and sys.argv[1] == "setup":
        from mnemo.setup_cli import main as setup_main

        setup_main(sys.argv[2:])
        return

    from mnemo.server import main as server_main

    server_main()

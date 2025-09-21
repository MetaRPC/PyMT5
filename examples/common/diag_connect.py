import os, asyncio, socket, ssl
import grpc
from grpc.experimental import aio as grpc_aio

HOST, PORT = (os.getenv("GRPC_SERVER", "mt5.mrpc.pro:443").split(":")[0],
              int(os.getenv("GRPC_SERVER", "mt5.mrpc.pro:443").split(":")[1]))

async def main():
    print(f"[1] DNS resolve {HOST}…")
    try:
        addrs = socket.getaddrinfo(HOST, PORT, type=socket.SOCK_STREAM)
        print("    OK:", [a[4][0] for a in addrs])
    except Exception as e:
        print("    FAIL DNS:", e); return

    print(f"[2] TCP connect {HOST}:{PORT}…")
    try:
        r, w = await asyncio.open_connection(HOST, PORT)
        w.close(); await w.wait_closed()
        print("    OK")
    except Exception as e:
        print("    FAIL TCP:", e); return

    print(f"[3] TLS handshake {HOST}:{PORT}…")
    try:
        ctx = ssl.create_default_context()
        r, w = await asyncio.open_connection(HOST, PORT, ssl=ctx, server_hostname=HOST)
        w.close(); await w.wait_closed()
        print("    OK")
    except Exception as e:
        print("    FAIL TLS:", e); return

    print(f"[4] gRPC channel_ready (TLS) {HOST}:{PORT}…")
    try:
        creds = grpc.ssl_channel_credentials()
        ch = grpc_aio.secure_channel(f"{HOST}:{PORT}", creds)
        await asyncio.wait_for(ch.channel_ready(), timeout=10)
        print("    OK (channel ready)")
    except Exception as e:
        print("    FAIL gRPC TLS:", e)

if __name__ == "__main__":
    asyncio.run(main())

    """
    Network sanity check to GRPC_SERVER (HOST:PORT)

    What it does (in order):
    1) DNS: resolve HOST → print resolved IPs
    2) TCP: open a plain TCP connection to HOST:PORT
    3) TLS: perform TLS handshake (SNI = HOST)
    4) gRPC: create a secure aio channel and await channel_ready()

    Environment:
    - GRPC_SERVER (default: "mt5.mrpc.pro:443")

    Output:
    - Prints "OK"/"FAIL ..." per step and stops on the first failure.

    How to run:
    - python -m examples.net_sanity   # or use your actual filename/module path
    """
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║ FILE app/config.py — MT5 connection/config dataclass                         ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ Purpose: Hold MT5 account and endpoint defaults.                             ║
║ Notes: Use either server_name or host:port. Keep password in env.            ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""
from dataclasses import dataclass
from typing import Optional

@dataclass
class MT5Config:
    user: int                               # MT5 account login (required)
    password: str                           # MT5 account password (required; do not log)
    grpc_server: str = "mt5.mrpc.pro:443"   # gRPC gateway endpoint
    server_name: Optional[str] = None       # Preferred: connect_by_server_name
    host: Optional[str] = None              # Alternative: connect_by_host_port
    port: int = 443                         # Port for host/port connection
    base_chart_symbol: str = "EURUSD"       # Default symbol for charts/snapshots
    timeout_seconds: int = 60               # Network/request timeout (seconds)


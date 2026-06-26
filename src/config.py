"""Carregamento de configuração e variáveis de ambiente.

Lê o arquivo `.env` (via python-dotenv) e expõe as configurações da aplicação.
O provedor de IA é o Ollama local (Mistral), que não usa chave de API — basta o
endereço do servidor e o nome do modelo.
"""

from __future__ import annotations

import os
import socket
import struct
from dataclasses import dataclass

from dotenv import load_dotenv

DEFAULT_OLLAMA_MODEL = "mistral"
DEFAULT_OLLAMA_PORT = 11434
_PROC_NET_ROUTE = "/proc/net/route"


class ConfigError(RuntimeError):
    """Erro de configuração (ex.: variável de ambiente obrigatória ausente)."""


@dataclass(frozen=True)
class Settings:
    """Configurações da aplicação carregadas do ambiente."""

    ollama_host: str
    ollama_model: str


def _wsl_default_gateway() -> str | None:
    """IP do gateway padrão — no WSL2 (NAT) é o IP do host Windows.

    Lê ``/proc/net/route`` e devolve o gateway da rota default (Destination
    0.0.0.0). Devolve ``None`` se não houver rota default ou o arquivo não existir.
    """
    try:
        with open(_PROC_NET_ROUTE, encoding="utf-8") as handle:
            next(handle, None)  # cabeçalho
            for line in handle:
                fields = line.split()
                # Destination == 00000000 (0.0.0.0) → rota default.
                if len(fields) > 2 and fields[1] == "00000000":
                    gateway_hex = fields[2]  # little-endian hex
                    return socket.inet_ntoa(struct.pack("<L", int(gateway_hex, 16)))
    except (OSError, ValueError):
        pass
    return None


def _default_ollama_host() -> str:
    """Descobre o endereço padrão do servidor Ollama.

    No WSL2 com o Ollama no host Windows, o IP do host é o gateway padrão. Se não
    for possível detectá-lo, cai para ``localhost``.
    """
    host = _wsl_default_gateway() or "localhost"
    return f"http://{host}:{DEFAULT_OLLAMA_PORT}"


def load_settings() -> Settings:
    """Carrega as variáveis do `.env` e retorna um objeto ``Settings``.

    ``OLLAMA_HOST`` do ambiente tem prioridade; se ausente, o host é detectado
    automaticamente (útil no WSL apontando para o host Windows).
    """
    load_dotenv()

    host = os.getenv("OLLAMA_HOST", "").strip() or _default_ollama_host()

    return Settings(
        ollama_host=host,
        ollama_model=os.getenv("OLLAMA_MODEL", DEFAULT_OLLAMA_MODEL),
    )

"""Render nftables egress snippet from OPS-14 allow-list (oneshot-c229)."""

from __future__ import annotations

from labcore.ops.egress_allowlist import STATIC_HOSTS, build_egress_allowlist

ARTEFACT_ID = "OPS.EGRESS.NFT"


def render_nft(hosts: list[str] | None = None) -> str:
    host_list = hosts if hosts is not None else sorted(build_egress_allowlist() | set(STATIC_HOSTS))
    lines = [
        "# ARW ML Lab worker egress allow-list (OPS-14 / ST-OPS-08)",
        "# Review before `nft -f`. Default policy should deny outbound except DNS + allowlist.",
        "table inet lab_egress {",
        "  set allow_hosts {",
        "    type ipv4_addr",
        "    flags interval",
        "    # Resolve hostnames on the VPS before loading, e.g.:",
    ]
    for h in host_list:
        lines.append(f"    # getent ahostsv4 {h}")
    lines.extend(
        [
            "  }",
            "  chain output {",
            "    type filter hook output priority 0; policy drop;",
            "    ct state established,related accept",
            "    oif lo accept",
            "    udp dport 53 accept",
            "    tcp dport 53 accept",
            "    # After filling set allow_hosts with resolved IPs:",
            "    # ip daddr @allow_hosts tcp dport {80,443} accept",
            "  }",
            "}",
            "",
            "# Hostname allow-list (resolve at apply time):",
        ]
    )
    for h in host_list:
        lines.append(f"# ALLOW_HOST {h}")
    lines.append("")
    return "\n".join(lines)


def assert_egress_nft_ready() -> dict[str, object]:
    out = render_nft()
    if "ALLOW_HOST" not in out or "lab_egress" not in out:
        raise AssertionError("rendered nft snippet incomplete")
    return {"id": ARTEFACT_ID, "seed": 42, "hosts_n": out.count("ALLOW_HOST")}

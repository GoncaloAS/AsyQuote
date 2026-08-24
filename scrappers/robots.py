"""Minimal, correct robots.txt matching.

`urllib.robotparser` mishandles wildcard paths: it reports
`Disallow: /*pt/carrinho` as allowing `/pt/carrinho`. Since the whole point of
consulting robots.txt is to obey it, the matching is done here instead, to the
rules in RFC 9309: `*` matches any run of characters, `$` anchors the end, and
the longest matching rule wins with Allow breaking ties.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from urllib.parse import unquote, urlparse


def _to_regex(pattern: str) -> re.Pattern[str]:
    anchored_end = pattern.endswith("$")
    if anchored_end:
        pattern = pattern[:-1]
    parts = [re.escape(p) for p in pattern.split("*")]
    return re.compile("^" + ".*".join(parts) + ("$" if anchored_end else ""))


@dataclass
class Rules:
    """The merged rules that apply to one user agent."""

    allow: list[tuple[int, re.Pattern[str]]] = field(default_factory=list)
    disallow: list[tuple[int, re.Pattern[str]]] = field(default_factory=list)
    crawl_delay: float | None = None
    content_signal: str | None = None
    matched_agent: str | None = None

    def allows(self, url: str) -> bool:
        path = unquote(urlparse(url).path) or "/"
        if urlparse(url).query:
            path += "?" + urlparse(url).query

        best_allow = max((n for n, p in self.allow if p.match(path)), default=-1)
        best_disallow = max((n for n, p in self.disallow if p.match(path)), default=-1)
        if best_disallow < 0:
            return True
        # Ties go to Allow, per RFC 9309.
        return best_allow >= best_disallow


def parse(text: str, user_agent: str) -> Rules:
    """Collect every group that applies to `user_agent`, plus the `*` fallback."""
    agent = user_agent.split("/")[0].lower()
    groups: dict[str, Rules] = {}
    current: list[str] = []
    expecting_agents = True

    for raw in text.splitlines():
        line = raw.split("#", 1)[0].strip()
        if not line or ":" not in line:
            continue
        field_name, _, value = line.partition(":")
        field_name = field_name.strip().lower()
        value = value.strip()

        if field_name == "user-agent":
            if not expecting_agents:
                current = []
                expecting_agents = True
            current.append(value.lower())
            groups.setdefault(value.lower(), Rules(matched_agent=value))
            continue

        expecting_agents = False
        if not current:
            continue
        for name in current:
            rules = groups[name]
            if field_name == "disallow" and value:
                rules.disallow.append((len(value), _to_regex(value)))
            elif field_name == "allow" and value:
                rules.allow.append((len(value), _to_regex(value)))
            elif field_name == "disallow" and not value:
                rules.allow.append((1, _to_regex("/")))  # empty Disallow allows all
            elif field_name == "crawl-delay":
                try:
                    rules.crawl_delay = float(value)
                except ValueError:
                    pass
            elif field_name == "content-signal":
                rules.content_signal = value

    # Most specific agent wins; fall back to '*'.
    for name in sorted(groups, key=len, reverse=True):
        if name != "*" and name in agent:
            return groups[name]
    return groups.get("*", Rules(matched_agent="*"))

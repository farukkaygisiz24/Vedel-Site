"""Case-insensitive search that respects Turkish İ/I on PostgreSQL and SQLite."""

from __future__ import annotations

from django.db.models import CharField, Q, TextField
from django.db.models.lookups import IContains

_I_CHARS = 'iıIİ'


class ILike(IContains):
    """ILIKE on Postgres; UPPER/LIKE elsewhere (sqlite tests)."""

    lookup_name = 'ilike'

    def as_sql(self, compiler, connection):
        lhs, lhs_params = self.process_lhs(compiler, connection)
        rhs, rhs_params = self.process_rhs(compiler, connection)
        params = list(lhs_params) + list(rhs_params)
        if connection.vendor == 'postgresql':
            return '%s ILIKE %s' % (lhs, rhs), params
        return 'UPPER(%s) LIKE UPPER(%s)' % (lhs, rhs), params


def register_search_lookups() -> None:
    CharField.register_lookup(ILike, 'ilike')
    TextField.register_lookup(ILike, 'ilike')


def tr_i_variants(token: str) -> list[str]:
    """Expand i/ı/I/İ so ASCII 'makin' matches stored 'MAKİN'."""
    token = str(token or '')
    if not token:
        return []
    variants = ['']
    for ch in token:
        options = list(_I_CHARS) if ch in _I_CHARS else [ch]
        variants = [prefix + opt for prefix in variants for opt in options]
    seen: dict[str, None] = {}
    for item in variants:
        seen.setdefault(item, None)
    return list(seen)


def q_search(token: str, *fields: str) -> Q:
    token = str(token or '').strip()
    if not token or not fields:
        return Q()
    variants = tr_i_variants(token) or [token]
    query = Q()
    for field in fields:
        for variant in variants:
            query |= Q(**{f'{field}__ilike': variant})
    return query

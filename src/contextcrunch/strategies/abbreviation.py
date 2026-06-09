from __future__ import annotations

import re

from contextcrunch.strategies.base import BaseStrategy
from contextcrunch.types import Change

_ABBREVIATIONS: dict[str, str] = {
    "please": "pls",
    "because": "bcz",
    "about": "abt",
    "between": "btw",
    "please create": "create",
    "please implement": "implement",
    "please write": "write",
    "please make": "make",
    "please add": "add",
    "please build": "build",
    "please develop": "develop",
    "would you": "pls",
    "could you": "pls",
    "can you": "pls",
    "i would like": "want",
    "i want": "want",
    "i need": "need",
    "we need": "need",
    "you need": "need",
    "there is": "",
    "there are": "",
    "there will be": "",
    "we have": "have",
    "you have": "have",
    "i have": "have",
    "this is": "this",
    "that is": "that",
    "it is": "",
    "what is": "what",
    "which is": "which",
    "who is": "who",
    "where is": "where",
    "when is": "when",
    "how is": "how",
    "we are": "we",
    "you are": "you",
    "they are": "they",
    "i am": "i",
    "that will": "that",
    "this will": "this",
    "function": "fn",
    "functions": "fns",
    "variable": "var",
    "variables": "vars",
    "parameter": "param",
    "parameters": "params",
    "argument": "arg",
    "arguments": "args",
    "attribute": "attr",
    "attributes": "attrs",
    "property": "prop",
    "properties": "props",
    "method": "meth",
    "methods": "meths",
    "class": "cls",
    "classes": "clss",
    "object": "obj",
    "objects": "objs",
    "instance": "inst",
    "instances": "insts",
    "value": "val",
    "values": "vals",
    "string": "str",
    "strings": "strs",
    "integer": "int",
    "integers": "ints",
    "boolean": "bool",
    "booleans": "bools",
    "number": "num",
    "numbers": "nums",
    "array": "arr",
    "arrays": "arrs",
    "list": "lst",
    "lists": "lsts",
    "dictionary": "dict",
    "dictionaries": "dicts",
    "tuple": "tup",
    "tuples": "tups",
    "set": "st",
    "sets": "sts",
    "database": "db",
    "databases": "dbs",
    "table": "tbl",
    "tables": "tbls",
    "column": "col",
    "columns": "cols",
    "record": "rec",
    "records": "recs",
    "query": "qry",
    "queries": "qrys",
    "server": "srv",
    "servers": "srvs",
    "client": "clt",
    "clients": "clts",
    "request": "req",
    "requests": "reqs",
    "response": "rsp",
    "responses": "rsps",
    "message": "msg",
    "messages": "msgs",
    "package": "pkg",
    "packages": "pkgs",
    "module": "mod",
    "modules": "mods",
    "library": "lib",
    "libraries": "libs",
    "directory": "dir",
    "directories": "dirs",
    "folder": "dir",
    "folders": "dirs",
    "file": "f",
    "files": "fs",
    "path": "pth",
    "paths": "pths",
    "configuration": "cfg",
    "configurations": "cfgs",
    "implementation": "impl",
    "implementations": "impls",
    "documentation": "doc",
    "documentations": "docs",
    "specification": "spec",
    "specifications": "specs",
    "application": "app",
    "applications": "apps",
    "environment": "env",
    "environments": "envs",
    "development": "dev",
    "production": "prod",
    "administration": "admin",
    "administrator": "admin",
    "administrators": "admins",
    "authentication": "auth",
    "authorization": "authz",
    "communication": "comm",
    "communications": "comms",
    "connection": "conn",
    "connections": "conns",
    "component": "comp",
    "components": "comps",
}

_ABBREV_PATTERN = re.compile(
    r"\b(" + "|".join(re.escape(k) for k in sorted(_ABBREVIATIONS.keys(), key=len, reverse=True)) + r")\b",
    re.IGNORECASE,
)

_CONTEXT_REMOVAL = [
    (re.compile(r"\b(?:as an?|acting as an?|in the role of an?|as if you were an?)\s+(?:AI|assistant|expert|senior|professional|specialist|developer|engineer|programmer|designer|architect)\b", re.IGNORECASE), ""),
    (re.compile(r"\byou are an?\s+(?:AI|expert|assistant|professional|senior|specialist|developer|engineer)\b", re.IGNORECASE), ""),
    (re.compile(r"\byou are a\s+proficient\s+\w+\b", re.IGNORECASE), ""),
    (re.compile(r"\bas an?\s+(?:AI|LLM|assistant|language model)\s*,?\s*", re.IGNORECASE), ""),
    (re.compile(r"\bI'm an?\s+(?:AI|assistant|language model)\b", re.IGNORECASE), ""),
    (re.compile(r"\bI don't have (?:access to|the ability to|the capability to)\b", re.IGNORECASE), "cannot"),
    (re.compile(r"\bI cannot (?:access|browse|look up|search for|find)\b", re.IGNORECASE), ""),
    (re.compile(r"\bI (?:don't|do not) (?:know|understand|see|have that information)\b", re.IGNORECASE), ""),
    (re.compile(r"\bLet me know if you (?:have|need|want)\b", re.IGNORECASE), ""),
    (re.compile(r"\bFeel free to\s+", re.IGNORECASE), ""),
    (re.compile(r"\bIf you have any (?:questions|concerns|issues|problems),?\s*(?:please\s+)?(?:let me know|ask|tell me)\b", re.IGNORECASE), ""),
    (re.compile(r"\bPlease let me know if you need (?:anything else|further assistance|more help)\b", re.IGNORECASE), ""),
]


class AbbreviationStrategy(BaseStrategy):
    @property
    def name(self) -> str:
        return "abbreviation"

    @property
    def tier(self) -> int:
        return 3

    def apply(self, text: str, normalized_text: str | None = None) -> tuple[str, list[Change]]:
        changes: list[Change] = []
        result = text

        result, c = self._apply_abbreviations(result)
        changes.extend(c)

        result, c = self._remove_context(result)
        changes.extend(c)

        return result, changes

    def _apply_abbreviations(self, text: str) -> tuple[str, list[Change]]:
        changes: list[Change] = []

        def repl(m: re.Match[str]) -> str:
            original = m.group()
            key = original.lower()
            replacement = _ABBREVIATIONS.get(key)
            if replacement is None:
                return original
            if original[0].isupper() and replacement:
                replacement = replacement[0].upper() + replacement[1:]
            changes.append(self._make_change(original, replacement, m.start(), m.end()))
            return replacement

        result = _ABBREV_PATTERN.sub(repl, text)
        return result, changes

    def _remove_context(self, text: str) -> tuple[str, list[Change]]:
        changes: list[Change] = []
        result = text
        for pattern, replacement in _CONTEXT_REMOVAL:
            new_result = pattern.sub(lambda m, r=replacement: self._replace_ctx(m, r, changes), result)
            if new_result != result:
                result = new_result
        return result, changes

    def _replace_ctx(self, match: re.Match[str], replacement: str, changes: list[Change]) -> str:
        original = match.group()
        expanded = match.expand(replacement) if "\\" in replacement else replacement
        if expanded != original:
            changes.append(self._make_change(original, expanded, match.start(), match.end()))
        return expanded

#!/usr/bin/env python3
"""Direct Lanhu CLI for the lanhu-skill package."""

from __future__ import annotations

import argparse
import asyncio
import importlib.util
import json
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlparse


SCRIPT_DIR = Path(__file__).resolve().parent
VENDOR_PATH = SCRIPT_DIR / "vendor" / "lanhu_impl.py"
_VENDOR_MODULE = None


def _load_vendor_module():
    global _VENDOR_MODULE
    if _VENDOR_MODULE is not None:
        return _VENDOR_MODULE
    spec = importlib.util.spec_from_file_location("lanhu_skill_vendor", VENDOR_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load vendor module from {VENDOR_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    _VENDOR_MODULE = module
    return module


def classify_url(url: str) -> dict[str, Any]:
    parsed = urlparse(url)
    query = parse_qs(parsed.query)
    if parsed.fragment:
        fragment_query = parsed.fragment.split("?", 1)
        if len(fragment_query) == 2:
            query.update(parse_qs(fragment_query[1]))
    has_sid = "sid" in query
    has_tid = "tid" in query
    has_pid = "pid" in query
    has_doc_id = "docId" in query

    if "/link/#/invite" in url or has_sid:
        kind = "invite"
    elif has_tid and has_pid and has_doc_id:
        kind = "prd"
    elif has_tid and has_pid:
        kind = "design"
    else:
        kind = "unknown"

    return {
        "status": "success",
        "url": url,
        "kind": kind,
        "has_tid": has_tid,
        "has_pid": has_pid,
        "has_doc_id": has_doc_id,
        "has_sid": has_sid,
    }


def _coerce_multi(values: list[str] | None) -> str | list[str] | None:
    if values is None:
        return None
    if len(values) == 1:
        return values[0]
    return values


def _serialize(value: Any) -> Any:
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, dict):
        return {key: _serialize(item) for key, item in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [_serialize(item) for item in value]
    path = getattr(value, "path", None)
    if path is not None:
        return {"type": "image", "path": str(path)}
    return repr(value)


async def _run_async_command(args: argparse.Namespace) -> Any:
    command = args.command
    if command == "classify-url":
        return classify_url(args.url)
    lanhu_impl = _load_vendor_module()
    if command == "resolve-invite":
        return await lanhu_impl.lanhu_resolve_invite_link(args.url)
    if command == "get-pages":
        return await lanhu_impl.lanhu_get_pages(args.url)
    if command == "analyze-pages":
        page_names = _coerce_multi(args.page_names)
        return await lanhu_impl.lanhu_get_ai_analyze_page_result(
            args.url,
            page_names,
            mode=args.mode,
            analysis_mode=args.analysis_mode,
        )
    if command == "get-designs":
        return await lanhu_impl.lanhu_get_designs(args.url)
    if command == "analyze-designs":
        design_names = _coerce_multi(args.design_names)
        return await lanhu_impl.lanhu_get_ai_analyze_design_result(
            args.url,
            design_names,
            analysis_mode=args.analysis_mode,
        )
    if command == "get-design-slices":
        return await lanhu_impl.lanhu_get_design_slices(
            args.url,
            args.design_name,
            include_metadata=args.include_metadata,
        )
    if command == "say":
        mentions = args.mentions or None
        return await lanhu_impl.lanhu_say(
            url=args.url,
            summary=args.summary,
            content=args.content,
            mentions=mentions,
            message_type=args.message_type,
        )
    if command == "say-list":
        return await lanhu_impl.lanhu_say_list(
            url=args.url,
            filter_type=args.filter_type,
            search_regex=args.search_regex,
            limit=args.limit,
        )
    if command == "say-detail":
        message_ids: int | list[int]
        if len(args.message_ids) == 1:
            message_ids = args.message_ids[0]
        else:
            message_ids = args.message_ids
        return await lanhu_impl.lanhu_say_detail(
            message_ids=message_ids,
            url=args.url,
            project_id=args.project_id,
        )
    if command == "say-edit":
        return await lanhu_impl.lanhu_say_edit(
            url=args.url,
            message_id=args.message_id,
            summary=args.summary,
            content=args.content,
            mentions=args.mentions,
        )
    if command == "say-delete":
        return await lanhu_impl.lanhu_say_delete(args.url, args.message_id)
    if command == "get-members":
        return await lanhu_impl.lanhu_get_members(args.url)
    raise ValueError(f"Unsupported command: {command}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Lanhu skill direct CLI. Runs vendored Lanhu logic without MCP registration."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    classify = subparsers.add_parser("classify-url", help="Classify a Lanhu URL.")
    classify.add_argument("--url", required=True)

    resolve = subparsers.add_parser("resolve-invite", help="Resolve a Lanhu invite link.")
    resolve.add_argument("--url", required=True)

    get_pages = subparsers.add_parser("get-pages", help="List PRD/prototype pages.")
    get_pages.add_argument("--url", required=True)

    analyze_pages = subparsers.add_parser(
        "analyze-pages", help="Analyze PRD/prototype pages."
    )
    analyze_pages.add_argument("--url", required=True)
    analyze_pages.add_argument("--page-names", nargs="+", required=True)
    analyze_pages.add_argument("--mode", default="full", choices=["text_only", "full"])
    analyze_pages.add_argument(
        "--analysis-mode",
        default="developer",
        choices=["developer", "tester", "explorer", "clarifier", "backend_designer", "api_designer"],
    )

    get_designs = subparsers.add_parser("get-designs", help="List design images.")
    get_designs.add_argument("--url", required=True)

    analyze_designs = subparsers.add_parser(
        "analyze-designs", help="Analyze one or more design images."
    )
    analyze_designs.add_argument("--url", required=True)
    analyze_designs.add_argument("--design-names", nargs="+", required=True)
    analyze_designs.add_argument(
        "--analysis-mode",
        default="developer",
        choices=["developer", "tester", "explorer", "clarifier", "backend_designer", "api_designer"],
    )

    slices = subparsers.add_parser("get-design-slices", help="List slices for a design.")
    slices.add_argument("--url", required=True)
    slices.add_argument("--design-name", required=True)
    slices.add_argument(
        "--include-metadata",
        action=argparse.BooleanOptionalAction,
        default=True,
    )

    say = subparsers.add_parser("say", help="Post a team message.")
    say.add_argument("--url", required=True)
    say.add_argument("--summary", required=True)
    say.add_argument("--content", required=True)
    say.add_argument("--mentions", nargs="*")
    say.add_argument(
        "--message-type",
        choices=["normal", "task", "question", "urgent", "knowledge"],
    )

    say_list = subparsers.add_parser("say-list", help="List project or global messages.")
    say_list.add_argument("--url", default=None)
    say_list.add_argument("--filter-type")
    say_list.add_argument("--search-regex")
    say_list.add_argument("--limit", type=int)

    say_detail = subparsers.add_parser("say-detail", help="Show message details.")
    say_detail.add_argument("--message-ids", nargs="+", type=int, required=True)
    say_detail.add_argument("--url")
    say_detail.add_argument("--project-id")

    say_edit = subparsers.add_parser("say-edit", help="Edit a message.")
    say_edit.add_argument("--url", required=True)
    say_edit.add_argument("--message-id", type=int, required=True)
    say_edit.add_argument("--summary")
    say_edit.add_argument("--content")
    say_edit.add_argument("--mentions", nargs="*")

    say_delete = subparsers.add_parser("say-delete", help="Delete a message.")
    say_delete.add_argument("--url", required=True)
    say_delete.add_argument("--message-id", type=int, required=True)

    members = subparsers.add_parser("get-members", help="List collaborators.")
    members.add_argument("--url", required=True)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        payload = asyncio.run(_run_async_command(args))
    except KeyboardInterrupt:
        return 130
    except Exception as exc:
        print(json.dumps({"status": "error", "message": str(exc)}, ensure_ascii=False))
        return 1

    print(json.dumps(_serialize(payload), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

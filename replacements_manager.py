import os
import json
import re
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple

DEFAULT_REPLACEMENTS_PATH = os.path.expanduser("~/.call_recorder_replacements.json")

def build_regex_pattern(find: str, case_sensitive: bool = False, whole_word: bool = True) -> re.Pattern:
    """
    Compiles a robust regular expression for search and replacement,
    handling Unicode characters and word boundaries correctly.
    """
    escaped = re.escape(find)
    if whole_word:
        # Match word boundaries for unicode alphanumeric characters
        starts_with_word = bool(re.match(r"^\w", find, re.UNICODE))
        ends_with_word = bool(re.search(r"\w$", find, re.UNICODE))
        
        prefix = r"(?<!\w)" if starts_with_word else r"(?<!\S)"
        suffix = r"(?!\w)" if ends_with_word else r"(?!\S)"
        pattern = f"{prefix}{escaped}{suffix}"
    else:
        pattern = escaped

    flags = re.UNICODE
    if not case_sensitive:
        flags |= re.IGNORECASE

    return re.compile(pattern, flags)


class ReplacementsManager:
    """
    Manages centralized replacement rules for transcriptions.
    Allows saving frequently misspelled terms (technical jargon, acronyms)
    and automatically detecting and replacing them in transcripts.
    """

    def __init__(self, filepath: Optional[str] = None):
        if not filepath:
            filepath = os.environ.get("CALL_RECORDINGS_REPLACEMENTS_PATH", DEFAULT_REPLACEMENTS_PATH)
        self.filepath = os.path.abspath(filepath)

    def _save_raw(self, items: List[Dict[str, Any]]):
        """Writes items atomically to disk."""
        dir_path = os.path.dirname(self.filepath)
        if dir_path:
            os.makedirs(dir_path, exist_ok=True)
        tmp_path = self.filepath + ".tmp"
        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump(items, f, ensure_ascii=False, indent=2)
        os.replace(tmp_path, self.filepath)

    def get_replacements(self) -> List[Dict[str, Any]]:
        """Returns list of replacement rules."""
        if not os.path.exists(self.filepath):
            return []
        try:
            with open(self.filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    return data
                return []
        except Exception as e:
            print(f"Error loading replacements: {e}")
            return []

    def add_replacement(
        self,
        find: str,
        replace: str,
        case_sensitive: bool = False,
        whole_word: bool = True
    ) -> Dict[str, Any]:
        """
        Adds or updates a replacement rule.
        If a rule with identical `find` and `case_sensitive` exists, updates it.
        """
        find_clean = find.strip()
        if not find_clean:
            raise ValueError("El término a buscar no puede estar vacío.")

        replace_clean = replace.strip()
        items = self.get_replacements()
        now_iso = datetime.now().isoformat()

        # Check existing
        existing_idx = -1
        for idx, item in enumerate(items):
            same_find = item.get("find", "").strip() == find_clean if case_sensitive else item.get("find", "").strip().lower() == find_clean.lower()
            if same_find and bool(item.get("case_sensitive", False)) == bool(case_sensitive):
                existing_idx = idx
                break

        if existing_idx >= 0:
            item = items[existing_idx]
            item["replace"] = replace_clean
            item["whole_word"] = bool(whole_word)
            item["case_sensitive"] = bool(case_sensitive)
            item["updated_at"] = now_iso
            items[existing_idx] = item
        else:
            rule_id = f"rep_{uuid.uuid4().hex[:10]}"
            item = {
                "id": rule_id,
                "find": find_clean,
                "replace": replace_clean,
                "case_sensitive": bool(case_sensitive),
                "whole_word": bool(whole_word),
                "created_at": now_iso,
                "updated_at": now_iso
            }
            items.append(item)

        self._save_raw(items)
        return item

    def update_replacement(
        self,
        rule_id: str,
        find: str,
        replace: str,
        case_sensitive: bool = False,
        whole_word: bool = True
    ) -> Optional[Dict[str, Any]]:
        """Updates an existing replacement rule by ID."""
        find_clean = find.strip()
        if not find_clean:
            raise ValueError("El término a buscar no puede estar vacío.")

        items = self.get_replacements()
        now_iso = datetime.now().isoformat()
        found_item = None

        for idx, item in enumerate(items):
            if item.get("id") == rule_id:
                item["find"] = find_clean
                item["replace"] = replace.strip()
                item["case_sensitive"] = bool(case_sensitive)
                item["whole_word"] = bool(whole_word)
                item["updated_at"] = now_iso
                items[idx] = item
                found_item = item
                break

        if found_item:
            self._save_raw(items)
        return found_item

    def delete_replacement(self, rule_id: str) -> bool:
        """Deletes a rule by ID."""
        items = self.get_replacements()
        new_items = [it for it in items if it.get("id") != rule_id]
        if len(new_items) == len(items):
            return False
        self._save_raw(new_items)
        return True

    def set_replacements(self, rules: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Replaces entire list of rules."""
        sanitized = []
        now_iso = datetime.now().isoformat()
        for r in rules:
            find_clean = str(r.get("find", "")).strip()
            if not find_clean:
                continue
            rule_id = r.get("id") or f"rep_{uuid.uuid4().hex[:10]}"
            sanitized.append({
                "id": rule_id,
                "find": find_clean,
                "replace": str(r.get("replace", "")).strip(),
                "case_sensitive": bool(r.get("case_sensitive", False)),
                "whole_word": bool(r.get("whole_word", True)),
                "created_at": r.get("created_at") or now_iso,
                "updated_at": now_iso
            })
        self._save_raw(sanitized)
        return sanitized

    def detect_matches_in_segments(
        self,
        segments: List[Dict[str, Any]],
        rules: Optional[List[Dict[str, Any]]] = None
    ) -> List[Dict[str, Any]]:
        """
        Detects which centralized replacement rules have matches across the segments.
        Returns list of matched rule descriptors with match count and segment IDs.
        """
        if rules is None:
            rules = self.get_replacements()

        if not rules or not segments:
            return []

        results = []
        for rule in rules:
            find_term = rule.get("find", "").strip()
            if not find_term:
                continue
            regex = build_regex_pattern(
                find=find_term,
                case_sensitive=rule.get("case_sensitive", False),
                whole_word=rule.get("whole_word", True)
            )

            total_count = 0
            matching_segments = []

            for idx, seg in enumerate(segments):
                text = seg.get("text", "")
                if not text:
                    continue
                matches = list(regex.finditer(text))
                if matches:
                    total_count += len(matches)
                    matching_segments.append({
                        "segment_index": idx,
                        "segment_id": seg.get("id", idx + 1),
                        "count": len(matches)
                    })

            if total_count > 0:
                results.append({
                    "id": rule.get("id"),
                    "find": find_term,
                    "replace": rule.get("replace", ""),
                    "case_sensitive": rule.get("case_sensitive", False),
                    "whole_word": rule.get("whole_word", True),
                    "count": total_count,
                    "segments": matching_segments
                })

        return results

    def apply_rules_to_segments(
        self,
        segments: List[Dict[str, Any]],
        rule_ids: Optional[List[str]] = None,
        custom_rules: Optional[List[Dict[str, Any]]] = None
    ) -> Tuple[List[Dict[str, Any]], int, Dict[str, int]]:
        """
        Applies replacement rules to all segments.
        If `rule_ids` is provided, only rules matching those IDs are applied.
        Returns:
            (updated_segments, total_replaced_count, stats_by_rule_find)
        """
        if custom_rules is not None:
            rules_to_apply = custom_rules
        else:
            all_rules = self.get_replacements()
            if rule_ids is not None:
                id_set = set(rule_ids)
                rules_to_apply = [r for r in all_rules if r.get("id") in id_set]
            else:
                rules_to_apply = all_rules

        if not rules_to_apply or not segments:
            return segments, 0, {}

        # Prepare compiled regexes
        compiled = []
        for r in rules_to_apply:
            find_term = r.get("find", "").strip()
            if not find_term:
                continue
            rep_text = r.get("replace", "")
            reg = build_regex_pattern(
                find=find_term,
                case_sensitive=r.get("case_sensitive", False),
                whole_word=r.get("whole_word", True)
            )
            compiled.append((r, reg, rep_text))

        total_replaced = 0
        stats: Dict[str, int] = {}
        updated_segments = []

        for seg in segments:
            seg_copy = dict(seg)
            text = seg_copy.get("text", "")
            for rule, reg, rep_text in compiled:
                # Count matches
                matches = list(reg.finditer(text))
                if matches:
                    count = len(matches)
                    text = reg.sub(rep_text, text)
                    total_replaced += count
                    find_key = rule.get("find", "")
                    stats[find_key] = stats.get(find_key, 0) + count
            seg_copy["text"] = text
            updated_segments.append(seg_copy)

        return updated_segments, total_replaced, stats

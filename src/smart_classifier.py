import re, difflib, unicodedata
from typing import Optional, Callable
from data_types import AppType, WindowInfo, WindowNames


# ---- Helper normalizers ----
def _normalize_for_comparison(s: Optional[str]) -> str:
    """Lower, NFKC-normalize, remove surrounding whitespace and collapse separators."""
    if not s:
        return ""
    s = unicodedata.normalize("NFKC", str(s))
    s = s.lower()
    # Replace common separators with a single space
    s = re.sub(r"[._/\\\-]+", " ", s)
    # Remove any remaining non-alphanumeric (leave spaces)
    s = re.sub(r"[^0-9a-z\s]+", "", s)
    return re.sub(r"\s+", " ", s).strip()

def _strip_common_ext(s: str) -> str:
    """Remove common executable / file extensions for tighter matching"""
    return re.sub(r"\.(exe|bat|cmd|com|sh|app|bin|msi)$", "", s, flags=re.IGNORECASE)

def _tokenize(s: str) -> list[str]:
    return [t for t in s.split() if t and len(t) > 1]


def _fuzzy_ratio(a: str, b: str) -> float:
    if not a or not b:
        return 0.0
    return difflib.SequenceMatcher(None, a, b).ratio()


# ---- Smart classifier ----
class SmartClassifier:
    def __init__(
        self,
        window_names: WindowNames,  # WindowNames instance from load_app_lists()
        *,
        # weights (tune to prefer process match vs title match)
        proc_exact_weight: float = 2.0,
        proc_contains_weight: float = 1.0,
        proc_fuzzy_weight: float = 0.9,
        title_phrase_weight: float = 1.6,
        title_word_weight: float = 1.0,
        title_fuzzy_weight: float = 0.6,
        # thresholds
        fuzzy_threshold_proc: float = 0.82,
        fuzzy_threshold_title: float = 0.75,
        # final decision thresholds
        min_decision_score: float = 1.2,   # below this -> NEUTRAL
        min_margin: float = 0.3            # if top two scores too close -> NEUTRAL
    ):
        # store weights & thresholds
        self.w = {
            "proc_exact": proc_exact_weight,
            "proc_contains": proc_contains_weight,
            "proc_fuzzy": proc_fuzzy_weight,
            "title_phrase": title_phrase_weight,
            "title_word": title_word_weight,
            "title_fuzzy": title_fuzzy_weight,
        }
        self.t_proc = fuzzy_threshold_proc
        self.t_title = fuzzy_threshold_title
        self.min_score = min_decision_score
        self.min_margin = min_margin

        # normalize and prepare lists (safe against None)
        prod = window_names.productive
        dist = window_names.distracting

        self.prod_apps = self._normalize_apps_list(prod.apps or [])
        self.dist_apps = self._normalize_apps_list(dist.apps or [])
        self.prod_keywords = self._normalize_keywords_list(prod.keywords or [])
        self.dist_keywords = self._normalize_keywords_list(dist.keywords or [])

        # compile word-boundary regex for faster title exact-word checks
        self._prod_kw_regex = [re.compile(r"\b" + re.escape(k) + r"\b") for k in self.prod_keywords if k]
        self._dist_kw_regex = [re.compile(r"\b" + re.escape(k) + r"\b") for k in self.dist_keywords if k]

    def _normalize_apps_list(self, apps: list[str]) -> list[str]:
        out = []
        for a in apps:
            if not a:
                continue
            raw = str(a).strip()
            # keep both with/without extension normalized (so both "code" and "code exe" match)
            base = _strip_common_ext(raw)
            out.append(_normalize_for_comparison(base))
            out.append(_normalize_for_comparison(raw))
        # dedupe while keeping order
        seen = set()
        result = []
        for x in out:
            if x and x not in seen:
                seen.add(x)
                result.append(x)
        return result

    def _normalize_keywords_list(self, keywords: list[str]) -> list[str]:
        return [ _normalize_for_comparison(k) for k in keywords if k ]

    # ----- scoring helpers -----
    def _score_process(self, proc_raw: str, apps_list: list[str]) -> float:
        proc_norm = _normalize_for_comparison(proc_raw)
        proc_norm = _strip_common_ext(proc_norm)
        if not proc_norm:
            return 0.0

        best = 0.0
        for app in apps_list:
            if not app:
                continue
            # exact or endswith (exact filename match is strongest)
            if proc_norm == app or proc_norm.endswith(" " + app) or proc_norm.endswith(app):
                best = max(best, self.w["proc_exact"])
                break  # exact match wins quickly
            # containment (substring)
            if app in proc_norm:
                best = max(best, self.w["proc_contains"])
                continue
            # fuzzy
            r = _fuzzy_ratio(app, proc_norm)
            if r >= self.t_proc:
                best = max(best, self.w["proc_fuzzy"] * r)
        return best

    def _score_title(self, title_raw: str, keywords: list[str], kw_regex_list: list[re.Pattern]) -> float:
        title_norm = _normalize_for_comparison(title_raw)
        if not title_norm:
            return 0.0

        score = 0.0
        tokens = _tokenize(title_norm)

        for kw, regex in zip(keywords, kw_regex_list):
            if not kw:
                continue
            # phrase (substring) match -> strong
            if kw in title_norm:
                score += self.w["title_phrase"]
                continue
            # word-boundary match (single-word matches)
            if regex.search(title_norm):
                score += self.w["title_word"]
                continue
            # fuzzy against tokens
            best = 0.0
            for t in tokens:
                r = _fuzzy_ratio(kw, t)
                if r > best:
                    best = r
            if best >= self.t_title:
                score += self.w["title_fuzzy"] * best
        return score

    # ----- public classify API -----
    def classify(
        self, win_info: dict[WindowInfo, Optional[str | int]],
        *, process_getter: Callable[[int], str]
    ) -> AppType:
        """
        Args:
            win_info (dict): Dict-like with keys of `WindowInfo` containing `NAME` and `PROCESS_ID` (or process name).
            process_getter (Callable): Callable that given a process id returns a process name (use `get_process_name()`).
        
        Returns:
            AppType: The classification of the currently focused window process.
        """
        title = (win_info.get(WindowInfo.NAME) or "")  # raw title
        proc_id = win_info.get(WindowInfo.PROCESS_ID)
        # accept a string process name directly if provided; otherwise, resolve via `process_getter()`
        proc_name = ""
        if isinstance(proc_id, str):
            proc_name = proc_id
        else:
            try:
                proc_name = process_getter(proc_id)
            except Exception:
                proc_name = ""

        # compute scores
        prod_score = 0.0
        dist_score = 0.0

        prod_score += self._score_process(proc_name, self.prod_apps)
        dist_score += self._score_process(proc_name, self.dist_apps)

        # title keyword scoring (zip-safe: both lists aligned)
        # We prepare zipped lists (keyword, regex) for productve/distracting
        prod_score += self._score_title(title, self.prod_keywords, self._prod_kw_regex)
        dist_score += self._score_title(title, self.dist_keywords, self._dist_kw_regex)

        # final decision logic
        # if both below min_score => NEUTRAL
        if max(prod_score, dist_score) < self.min_score:
            return AppType.NEUTRAL

        # if scores too close => NEUTRAL (avoid flip-flopping)
        if abs(prod_score - dist_score) < self.min_margin:
            return AppType.NEUTRAL

        return AppType.PRODUCTIVE if prod_score > dist_score else AppType.DISTRACTING

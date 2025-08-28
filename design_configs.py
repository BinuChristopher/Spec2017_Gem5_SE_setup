from typing import Dict, List,Optional
import re

def make_design_configs(designs, assoc: int, fast_ways: int = None) -> Dict[str, Dict]:
    """
    Return a dict of {design_name: { 'l1d': {...}, 'l2': {...} }}.

    designs   : iterable of names, e.g. ['CSM', 'ATOR']
    assoc     : L2 associativity (e.g., 4, 8, 16)
    fast_ways : how many 'fast' MSB ways (defaults to assoc//2)
    """
    def two_bucket(fast_val: int, slow_val: int) -> List[int]:
        f = assoc // 2 if fast_ways is None else fast_ways
        if not (0 <= f <= assoc):
            raise ValueError(f"fast_ways must be in [0,{assoc}]")
        return [fast_val] * f + [slow_val] * (assoc - f)
    """
    As Priority ways accessed in parallel with tags, we run the config in sequential mode,
    so for priority ways only diffrence of tag and data is taken as data latency
    """
    def three_bucket(priorities:int, diffrence:int, fast_val: int, slow_val: int) -> List[int]:
        f = assoc // 2 if fast_ways is None else fast_ways
        if not (0 <= f <= assoc):
            raise ValueError(f"fast_ways must be in [0,{assoc}]")
        p = min(priorities, f) 
        return [diffrence]*(p) + [fast_val] * (f-p) + [slow_val] * (assoc - f)
    
    def parse_ator_priority(key: str) -> Optional[int]:
        """'ator'→0, 'ator_p'→1, 'ator_2p'→2, ... ; return None if not an ATOR key."""
        s = key.strip().lower()
        if s == "ator":
            return 0
        m = re.fullmatch(r"ator_(?:(\d+)p|p)", s)
        if m:
            return int(m.group(1) or 1)
        return None

    base_l1d = {
        "tag_latency": 2,
        "data_latency": 2,
        "wd_latencies": [2, 2],
        "rd_latencies": [2, 2],
        "wt_latencies": [2, 2],
        "rt_latencies": [2, 2],
    }

    out: Dict[str, Dict] = {}
    for name in designs:
        key = name.strip().lower()
        #csm - sequential run, csm_par - parallel run
        if key in ("csm, csm_par"):
            out[name] = {
                "l1d": dict(base_l1d),
                "l2": {
                    "tag_latency": 10,
                    "data_latency": 10,
                    "wd_latencies": two_bucket(23, 45),
                    "rd_latencies": two_bucket(6, 10),
                    "wt_latencies": two_bucket(11, 22),
                    "rt_latencies": two_bucket(3, 5),
                },
            }
            #ator - sequential run
        elif key in ("ator"):
            out[name] = {
                "l1d": dict(base_l1d),
                "l2": {
                    "tag_latency": 6,
                    "data_latency": 10,
                    "wd_latencies": two_bucket(23, 45),
                    "rd_latencies": two_bucket(6, 10),
                    "wt_latencies": [11] * assoc,
                    "rt_latencies": [3] * assoc,
                },
            }
            #ator_par - parallel run , same as ATOR with all LSB ways taken as parallel
        elif key in ("ator_par"):
            out[name] = {
                "l1d": dict(base_l1d),
                "l2": {
                    "tag_latency": 6,
                    "data_latency": 10,
                    "wd_latencies": two_bucket(23, 45),
                    "rd_latencies": two_bucket(6, 10),
                    "wt_latencies": [11] * assoc,
                    "rt_latencies": [3] * assoc,
                },
            }
            #ATOR P - sequential run with priority way's data latency given values of only the diffrence in tag to data latency
        elif (p := parse_ator_priority(key)) is not None:
            f_cap = assoc // 2 if fast_ways is None else min(fast_ways, assoc // 2)
            if p > f_cap:
                    raise ValueError(
                        f"Design '{name}': priorities ({p}) exceed allowed fast ways "
                        f"({f_cap}) for assoc={assoc}"
                    )
            p = min(p, f_cap)
            out[name] = {
                "l1d": dict(base_l1d),
                "l2": {
                    "tag_latency": 6,
                    "data_latency": 10,
                    "wd_latencies": three_bucket(p, 12,23, 45),
                    "rd_latencies": three_bucket(p, 3, 6, 10),
                    "wt_latencies": [11] * assoc,
                    "rt_latencies": [3] * assoc,
                },
            }
        else:
            raise ValueError(f"Unknown design '{name}'. Supported: csm, csm_par, ATOR, ATOR_Par, ATOR_P")
    return out


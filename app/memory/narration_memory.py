
def already_narrated(name, narrated):
    return name in narrated

def record(name, narrated):
    if name not in narrated:
        narrated.append(name)
    return narrated

def filter_candidates(candidates, narrated):
    return [c for c in candidates if not already_narrated(c.name, narrated)]
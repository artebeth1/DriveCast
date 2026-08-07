from app.memory.research_cache import ResearchCache, cosine
from app.agents.researcher import Research

def fake_embed(text):
    # deterministic: same text → same vector; different text → different vector
    if "Willis" in text:
        return [1.0, 0.0, 0.0]
    if "Sears" in text:
        return [0.99, 0.01, 0.0]   # near-identical → should HIT Willis
    return [0.0, 1.0, 0.0]          # everything else → orthogonal → MISS

def test_miss_on_empty_cache():
    cache = ResearchCache(embed_fn=fake_embed)
    assert cache.lookup("Willis Tower") is None

def test_store_then_hit():
    cache = ResearchCache(embed_fn=fake_embed)
    r = Research(summary="tall building", fun_facts=[])
    cache.store("Willis Tower", r, [])
    result = cache.lookup("Willis Tower")      # same → vector identical → hit
    assert result is not None

def test_below_threshold_misses():
    cache = ResearchCache(embed_fn=fake_embed)
    r = Research(summary="tall building", fun_facts=[])
    cache.store("Willis Tower", r, [])
    assert cache.lookup("some park") is None   # orthogonal vector → below 0.85 → miss

def test_semantic_near_match_hits():
    cache = ResearchCache(embed_fn=fake_embed)
    r = Research(summary="tall building", fun_facts=[])
    cache.store("Willis Tower", r, [])
    result = cache.lookup("Sears Tower")   # different string, near vector → hit
    assert result is not None
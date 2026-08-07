import numpy as np
from google import genai
from app.config import GEMINI_API_KEY
client = genai.Client()

def cosine(a, b):
    a, b = np.array(a), np.array(b)
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

THRESHOLD = 0.85

                      
def _real_embed(text):
    return client.models.embed_content(
        model="gemini-embedding-001",
        contents=text,
    ).embeddings[0].values


class ResearchCache:
    def __init__(self, embed_fn=_real_embed):
        self.entries = []
        self.embed = embed_fn        # injected dependency

    def store(self, query_text, research, sources):
        vector = self.embed(query_text)      # was: client.models.embed_content(...)
        self.entries.append((vector, research, sources))

    def lookup(self, query_text):
        query_vec = self.embed(query_text)   # same
        best_score, best_entry = 0, None
        for vector, research, sources in self.entries:
            score = cosine(query_vec, vector)
            if score > best_score:
                best_score, best_entry = score, (research, sources)
        if best_score >= THRESHOLD:
            return best_entry, best_score
        return None
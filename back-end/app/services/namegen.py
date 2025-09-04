from transformers import pipeline, AutoTokenizer
from app.config import settings
generator = pipeline(
    'text-generation',
    model='microsoft/DialoGPT-medium',
    tokenizer=AutoTokenizer.from_pretrained('microsoft/DialoGPT-medium'),
)
def brainstorm(keywords: list[str], niche: str, max_len: int = 10) -> list[str]:
    prompt = f'Generate 20 brandable .com/.io/.ai domains for a {niche} startup using keywords: {",".join(keywords)}. Return one per line.'
    out = generator(prompt, max_new_tokens=120, do_sample=True, top_p=0.9)
    lines = out[0]['generated_text'].splitlines()
    return [l.strip().lower() for l in lines if '.' in l][:max_len]

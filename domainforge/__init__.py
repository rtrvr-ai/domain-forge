"""
DomainForge — find brandable, *available* domain names end to end.

A founder gives a vibe (a brief and/or one or two seed words); DomainForge
expands that into thousands of candidates (curated corpus + Datamuse word
graph + combinations + optional LLM creativity), scores them for
brandability, checks real availability across the TLDs you care about, and
hands back a ranked shortlist.

Works fully offline-of-LLM (algorithmic only). Plug in a Claude / OpenAI /
Gemini / OpenRouter key for a smarter seed pool and a curated shortlist.
"""

__version__ = "1.0.0"
__all__ = ["__version__"]

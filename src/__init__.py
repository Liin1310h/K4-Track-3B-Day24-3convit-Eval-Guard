# Windows: torch's c10.dll fails to initialise (WinError 1114) if torch is imported after
# ragas/nemoguardrails load their native deps, so load it first when it is installed.
try:
    import torch  # noqa: F401
except Exception:
    pass

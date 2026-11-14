"""Thin, typed wrappers around external HTTP APIs (TVmaze, OMDb, Discord).

Each client receives a shared `httpx.Client`, which tests replace with one backed by
`httpx.MockTransport`, so no real network calls are made in tests.
"""

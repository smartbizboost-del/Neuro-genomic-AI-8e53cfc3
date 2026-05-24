"""Streamlit Cloud entrypoint for Neuro-Genomic AI."""

from __future__ import annotations

import runpy

import streamlit as st


def main() -> None:
	try:
		runpy.run_module("src.dashboard.app", run_name="__main__")
	except Exception as exc:
		st.error("The dashboard failed to start. See the exception details below.")
		st.exception(exc)
		st.stop()


main()

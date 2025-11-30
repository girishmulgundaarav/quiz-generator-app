import streamlit as st
from streamlit_autorefresh import st_autorefresh
import random


def shuffle_questions(quiz):
    """Randomly shuffle the questions."""
    random.shuffle(quiz)
    return quiz


def start_timer(total_seconds):
    """
    Sidebar timer with animated button look.
    """

    # If timer disabled → do nothing
    if not st.session_state.get("timer_enabled", False):
        return

    # Initialize running flag
    if "timer_running" not in st.session_state:
        st.session_state.timer_running = True

    # Initialize remaining seconds (only once)
    if "remaining" not in st.session_state:
        initial = st.session_state.get("seconds", total_seconds)
        try:
            initial = int(initial)
        except:
            initial = total_seconds
        st.session_state.remaining = initial

    # If timer already finished
    if not st.session_state.timer_running:
        with st.sidebar:
            st.markdown(
                "<div class='timer-button' style='background:#555;'>⏳ Time's Up!</div>",
                unsafe_allow_html=True
            )
        return

    rem = st.session_state.get("remaining", 0)

    # TIMER RUNNING
    if rem > 0:
        mins, secs = divmod(rem, 60)
        with st.sidebar:
            st.markdown(
                f"<div class='timer-button'>⏱ {mins:02d}:{secs:02d}</div>",
                unsafe_allow_html=True
            )

        # Decrement time
        st.session_state.remaining = rem - 1

        # Auto-refresh after 1 sec
        st_autorefresh(interval=1000, key="sidebar_timer_refresh")

    else:
        # TIME UP
        with st.sidebar:
            st.markdown(
                "<div class='timer-button' style='background:#444;'>⏳ Time's Up!</div>",
                unsafe_allow_html=True
            )
        st.session_state.timer_running = False

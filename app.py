"""Streamlit dashboard for Lok Sabha election insights."""

from __future__ import annotations

import json
import os
from functools import lru_cache
from typing import Dict, List, Optional, Tuple

import pandas as pd
import plotly.express as px
import requests
import streamlit as st

API_BASE_URL = os.environ.get("ELECTIONS_API_URL", "http://127.0.0.1:8000")
INDIA_GEOJSON_URL = (
    "https://raw.githubusercontent.com/geohacker/india/master/district/india_district.geojson"
)


@st.cache_data(ttl=3600)
def fetch_geojson() -> dict:
    response = requests.get(INDIA_GEOJSON_URL, timeout=30)
    response.raise_for_status()
    return response.json()


def api_get(path: str, params: Optional[List[Tuple[str, str]]] = None) -> list | dict:
    url = f"{API_BASE_URL}{path}"
    response = requests.get(url, params=params, timeout=30)
    response.raise_for_status()
    return response.json()


@st.cache_data(ttl=600)
def get_filters() -> dict:
    return api_get("/filters")


def build_params(filters: Dict) -> List[Tuple[str, str]]:
    params: List[Tuple[str, str]] = []
    if filters.get("year"):
        params.append(("year", str(filters["year"])))
    if filters.get("state"):
        params.append(("state", filters["state"]))
    if filters.get("gender"):
        params.append(("gender", filters["gender"]))
    if filters.get("constituency"):
        params.append(("constituency", filters["constituency"]))
    for party in filters.get("parties", []):
        params.append(("parties", party))
    return params


@st.cache_data(ttl=600)
def get_party_seat_share(filters: Dict):
    params = build_params(filters)
    return api_get("/party-seat-share", params)


@st.cache_data(ttl=600)
def get_state_turnout(filters: Dict):
    params = build_params(filters)
    return api_get("/state-turnout", params)


@st.cache_data(ttl=600)
def get_gender_representation(filters: Dict):
    params = []
    if filters.get("year"):
        params.append(("year", str(filters["year"])))
    return api_get("/gender-representation", params)


@st.cache_data(ttl=600)
def get_top_vote_share(filters: Dict, limit: int = 5):
    params = []
    if filters.get("year"):
        params.append(("year", str(filters["year"])))
    params.append(("limit", str(limit)))
    return api_get("/top-vote-share", params)


@st.cache_data(ttl=600)
def get_margin_distribution(filters: Dict):
    params = build_params(filters)
    return api_get("/margin-distribution", params)


def search_candidates(query: str, filters: Dict):
    params = build_params(filters)
    params.append(("query", query))
    return api_get("/search", params)


@st.cache_data(ttl=600)
def get_analytics():
    results = {
        "turnout": api_get("/analytics/highest-turnout"),
        "seat_change": api_get("/analytics/seat-change"),
        "women": api_get("/analytics/women-participation"),
        "close_margins": api_get("/analytics/close-margins"),
        "vote_trend": api_get("/analytics/vote-share-trend"),
        "education": api_get("/analytics/education-win-rate"),
    }
    return results


def render_seat_share(data: List[dict]):
    if not data:
        st.info("No seat share data for this selection.")
        return
    df = pd.DataFrame(data)
    pivot = df.pivot_table(index="year", columns="party", values="seats", aggfunc="sum").fillna(0)
    fig = px.bar(
        pivot,
        x=pivot.index,
        y=pivot.columns,
        title="Party-wise Seat Share",
        labels={"value": "Seats", "year": "Year"},
    )
    fig.update_layout(barmode="stack", legend_title_text="Party")
    st.plotly_chart(fig, use_container_width=True)


def render_turnout_map(data: List[dict]):
    if not data:
        st.info("No turnout data for this selection.")
        return

    df = pd.DataFrame(data)
    geojson = fetch_geojson()
    df["state_key"] = df["state_name"].str.lower().str.replace(r"[^a-z]", "", regex=True)

    features = geojson.get("features", [])
    for feature in features:
        state_name = feature["properties"].get("NAME_1", "")
        feature["properties"]["state_key"] = (
            state_name.lower().replace(" ", "").replace("&", "and")
        )

    fig = px.choropleth(
        df,
        geojson=geojson,
        locations="state_key",
        color="turnout_pct",
        hover_name="state_name",
        featureidkey="properties.state_key",
        color_continuous_scale="Purples",
        labels={"turnout_pct": "Turnout %"},
        title="Average Turnout by State",
    )
    fig.update_geos(fitbounds="locations", visible=False)
    st.plotly_chart(fig, use_container_width=True)


def render_gender_trend(data: List[dict]):
    if not data:
        st.info("No gender trend data.")
        return
    df = pd.DataFrame(data)
    df["gender_label"] = df["gender"].map({"F": "Female", "M": "Male"}).fillna("Other")
    fig = px.line(
        df,
        x="year",
        y="total_candidates",
        color="gender_label",
        title="Candidates by Gender over Time",
        labels={"total_candidates": "Candidates", "year": "Year"},
    )
    st.plotly_chart(fig, use_container_width=True)


def render_vote_share_donut(data: List[dict]):
    if not data:
        st.info("No vote share data.")
        return
    df = pd.DataFrame(data)
    fig = px.pie(
        df,
        values="vote_pct",
        names="party",
        title="Top Parties by Vote Share",
        hole=0.45,
    )
    st.plotly_chart(fig, use_container_width=True)


def render_margin_histogram(data: List[dict]):
    if not data:
        st.info("No margin data.")
        return
    df = pd.DataFrame(data)
    fig = px.histogram(
        df,
        x="margin",
        nbins=30,
        title="Distribution of Victory Margins",
        labels={"margin": "Margin (votes)"},
    )
    st.plotly_chart(fig, use_container_width=True)


def render_search(filters: Dict):
    st.subheader("Search Candidate / Constituency")
    query = st.text_input("Enter candidate or constituency name", "")
    if len(query.strip()) < 3:
        st.caption("Enter at least 3 characters to search.")
        return
    with st.spinner("Fetching matches..."):
        results = search_candidates(query.strip(), filters)
    if not results:
        st.info("No matches found.")
        return
    df = pd.DataFrame(results)
    df = df[
        [
            "year",
            "state_name",
            "constituency_name",
            "candidate_name",
            "party",
            "gender",
            "votes",
            "margin",
        ]
    ]
    st.dataframe(df, use_container_width=True, hide_index=True)


def render_analytics():
    data = get_analytics()
    st.subheader("Analytical Highlights")
    col1, col2, col3 = st.columns(3)
    turnout = data["turnout"]
    col1.metric(
        "Highest Turnout (2019)",
        f"{turnout['state_name']}",
        f"{turnout['turnout_pct']:.2f}%",
    )
    seat_change = data["seat_change"]
    col2.metric(
        "Biggest Seat Swing",
        f"{seat_change['party']} ({seat_change['year']})",
        f"{seat_change['seat_change']:+}",
    )
    women = data["women"]
    col3.metric("Women Participation", f"{women['percentage']:.2f}%")

    st.markdown("#### Closest Contests")
    st.table(pd.DataFrame(data["close_margins"]))

    st.markdown("#### National vs Regional Vote Share (Latest)")
    latest_year = max(item["year"] for item in data["vote_trend"])
    trend_df = pd.DataFrame([item for item in data["vote_trend"] if item["year"] == latest_year])
    st.dataframe(trend_df, hide_index=True)

    st.markdown("#### Education & Win Rate")
    st.dataframe(pd.DataFrame(data["education"]).head(5), hide_index=True)


def main():
    st.set_page_config(
        page_title="Indian General Election Dashboard",
        layout="wide",
    )
    st.title("Indian General Election Insights (1991-2019)")
    st.caption("Powered by Lok Dhaba (TCPD) · Backend: FastAPI · Frontend: Streamlit")

    filters = get_filters()
    sidebar = st.sidebar
    sidebar.header("Filters")

    selected_year = sidebar.selectbox("Year", options=filters["years"], index=len(filters["years"]) - 1)
    selected_state = sidebar.selectbox("State/UT", options=["All"] + filters["states"])
    selected_gender = sidebar.selectbox("Gender", options=["All"] + filters["genders"])
    selected_parties = sidebar.multiselect(
        "Parties",
        options=filters["parties"],
        default=[],
        help="Select parties to highlight seat share",
    )
    selected_constituency = sidebar.selectbox(
        "Constituency", options=["All"] + filters["constituencies"], index=0
    )

    active_filters = {
        "year": selected_year,
        "state": None if selected_state == "All" else selected_state,
        "gender": None if selected_gender == "All" else selected_gender,
        "parties": selected_parties,
        "constituency": None if selected_constituency == "All" else selected_constituency,
    }

    col_a, col_b = st.columns(2)
    with col_a:
        render_seat_share(get_party_seat_share(active_filters))
    with col_b:
        render_turnout_map(get_state_turnout(active_filters))

    col_c, col_d = st.columns(2)
    with col_c:
        render_gender_trend(get_gender_representation(active_filters))
    with col_d:
        render_vote_share_donut(get_top_vote_share(active_filters))

    col_e, col_f = st.columns(2)
    with col_e:
        render_margin_histogram(get_margin_distribution(active_filters))
    with col_f:
        render_search(active_filters)

    render_analytics()


if __name__ == "__main__":
    main()


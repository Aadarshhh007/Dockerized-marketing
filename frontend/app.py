import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
from datetime import datetime

API_BASE_URL = os.getenv("API_BASE_URL", "http://backend:8000/api/v1")

st.set_page_config(
    page_title="Marketing Service Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
    }
    .status-active   { color: #22c55e; font-weight: bold; }
    .status-draft    { color: #3b82f6; font-weight: bold; }
    .status-paused   { color: #f59e0b; font-weight: bold; }
    .status-completed { color: #6b7280; font-weight: bold; }
</style>
""", unsafe_allow_html=True)


def fetch(path: str, default=None):
    try:
        r = requests.get(f"{API_BASE_URL}{path}", timeout=5)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        st.warning(f"API unavailable: {e}. Showing sample data.")
        return default


SAMPLE_CAMPAIGNS = [
    {"id": 1, "name": "Summer Sale 2025", "status": "active", "budget": 15000.0, "start_date": "2025-06-01", "end_date": "2025-08-31", "target_audience": "Customers 25-45"},
    {"id": 2, "name": "Product Launch Q3", "status": "draft", "budget": 50000.0, "start_date": "2025-07-15", "end_date": "2025-09-15", "target_audience": "Premium segment"},
    {"id": 3, "name": "Re-engagement Drive", "status": "paused", "budget": 8000.0, "start_date": "2025-04-01", "end_date": "2025-06-30", "target_audience": "Lapsed customers"},
]

SAMPLE_STATS = [
    {"campaign_id": 1, "campaign_name": "Summer Sale 2025", "total_users": 3, "active_users": 3, "budget": 15000.0, "status": "active"},
    {"campaign_id": 2, "campaign_name": "Product Launch Q3", "total_users": 1, "active_users": 1, "budget": 50000.0, "status": "draft"},
    {"campaign_id": 3, "campaign_name": "Re-engagement Drive", "total_users": 1, "active_users": 0, "budget": 8000.0, "status": "paused"},
]

SAMPLE_USERS = [
    {"id": 1, "name": "Alice Johnson", "email": "alice@example.com", "phone": "+1-555-0101", "campaign_id": 1, "subscribed": True},
    {"id": 2, "name": "Bob Smith", "email": "bob@example.com", "phone": "+1-555-0102", "campaign_id": 1, "subscribed": True},
    {"id": 3, "name": "Carol White", "email": "carol@example.com", "phone": None, "campaign_id": 2, "subscribed": True},
    {"id": 4, "name": "David Lee", "email": "david@example.com", "phone": "+1-555-0104", "campaign_id": 3, "subscribed": False},
    {"id": 5, "name": "Eva Martinez", "email": "eva@example.com", "phone": "+1-555-0105", "campaign_id": 1, "subscribed": True},
]


with st.sidebar:
    st.image("https://via.placeholder.com/200x60?text=MarketingOS", width=200)
    st.markdown("---")
    page = st.radio(
        "Navigate",
        ["Dashboard", "Campaigns", "Users", "Analytics", "Add Campaign", "Add User"],
        index=0,
    )
    st.markdown("---")
    health = fetch("/health", {"status": "unknown", "version": "N/A"})
    status_color = "🟢" if health.get("status") == "healthy" else "🔴"
    st.markdown(f"**API Status:** {status_color} {health.get('status', 'unknown').capitalize()}")
    st.markdown(f"**Version:** {health.get('version', 'N/A')}")
    st.markdown(f"**API URL:** `{API_BASE_URL}`")


if page == "Dashboard":
    st.title("📊 Marketing Service Dashboard")
    st.markdown(f"*Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")
    st.markdown("---")

    campaigns = fetch("/campaigns", SAMPLE_CAMPAIGNS)
    stats = fetch("/stats", SAMPLE_STATS)
    users = fetch("/users", SAMPLE_USERS)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Campaigns", len(campaigns))
    with col2:
        active = len([c for c in campaigns if c["status"] == "active"])
        st.metric("Active Campaigns", active)
    with col3:
        total_budget = sum(c["budget"] for c in campaigns)
        st.metric("Total Budget", f"${total_budget:,.0f}")
    with col4:
        st.metric("Total Users", len(users))

    st.markdown("---")

    col_left, col_right = st.columns(2)

    with col_left:
        st.subheader("Campaign Status Distribution")
        status_counts = {}
        for c in campaigns:
            status_counts[c["status"]] = status_counts.get(c["status"], 0) + 1
        fig = px.pie(
            values=list(status_counts.values()),
            names=list(status_counts.keys()),
            color_discrete_sequence=px.colors.qualitative.Set3,
        )
        st.plotly_chart(fig, use_container_width=True)

    with col_right:
        st.subheader("Budget by Campaign")
        df_stats = pd.DataFrame(stats)
        if not df_stats.empty:
            fig2 = px.bar(
                df_stats,
                x="campaign_name",
                y="budget",
                color="status",
                labels={"campaign_name": "Campaign", "budget": "Budget ($)"},
                color_discrete_sequence=px.colors.qualitative.Pastel,
            )
            fig2.update_layout(xaxis_tickangle=-30)
            st.plotly_chart(fig2, use_container_width=True)

    st.subheader("Users per Campaign")
    df_stats = pd.DataFrame(stats)
    if not df_stats.empty:
        fig3 = px.bar(
            df_stats,
            x="campaign_name",
            y=["total_users", "active_users"],
            barmode="group",
            labels={"campaign_name": "Campaign", "value": "Users"},
            color_discrete_sequence=["#3b82f6", "#22c55e"],
        )
        st.plotly_chart(fig3, use_container_width=True)


elif page == "Campaigns":
    st.title("📋 Campaigns")

    status_filter = st.selectbox("Filter by Status", ["All", "active", "draft", "paused", "completed"])
    path = "/campaigns" if status_filter == "All" else f"/campaigns?status={status_filter}"
    campaigns = fetch(path, SAMPLE_CAMPAIGNS)

    if status_filter != "All":
        campaigns = [c for c in campaigns if c["status"] == status_filter]

    if campaigns:
        df = pd.DataFrame(campaigns)
        df["budget"] = df["budget"].apply(lambda x: f"${x:,.2f}")
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("No campaigns found.")


elif page == "Users":
    st.title("👥 Users")

    campaigns = fetch("/campaigns", SAMPLE_CAMPAIGNS)
    campaign_options = {"All": None} | {c["name"]: c["id"] for c in campaigns}
    selected = st.selectbox("Filter by Campaign", list(campaign_options.keys()))
    selected_id = campaign_options[selected]

    path = f"/users?campaign_id={selected_id}" if selected_id else "/users"
    users = fetch(path, SAMPLE_USERS)

    if users:
        df = pd.DataFrame(users)
        df["subscribed"] = df["subscribed"].apply(lambda x: "✅ Yes" if x else "❌ No")
        st.dataframe(df, use_container_width=True, hide_index=True)
        st.markdown(f"**Total: {len(users)} users**")
    else:
        st.info("No users found.")


elif page == "Analytics":
    st.title("📈 Analytics")

    stats = fetch("/stats", SAMPLE_STATS)
    df = pd.DataFrame(stats)

    if not df.empty:
        st.subheader("Campaign Performance Summary")
        st.dataframe(df, use_container_width=True, hide_index=True)

        st.subheader("Engagement Rate by Campaign")
        df["engagement_rate"] = (df["active_users"] / df["total_users"].replace(0, 1) * 100).round(1)
        fig = px.bar(
            df,
            x="campaign_name",
            y="engagement_rate",
            color="status",
            labels={"engagement_rate": "Engagement Rate (%)", "campaign_name": "Campaign"},
            text="engagement_rate",
        )
        fig.update_traces(texttemplate="%{text}%", textposition="outside")
        fig.update_layout(xaxis_tickangle=-30, yaxis_range=[0, 120])
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("Budget Utilisation Overview")
        fig2 = go.Figure(go.Indicator(
            mode="gauge+number",
            value=sum(df["active_users"]),
            title={"text": "Total Active Users"},
            gauge={"axis": {"range": [0, sum(df["total_users"]) + 1]}, "bar": {"color": "#3b82f6"}},
        ))
        st.plotly_chart(fig2, use_container_width=True)


elif page == "Add Campaign":
    st.title("➕ Add New Campaign")

    with st.form("campaign_form"):
        name = st.text_input("Campaign Name *")
        description = st.text_area("Description")
        budget = st.number_input("Budget ($) *", min_value=0.0, value=10000.0, step=500.0)
        target_audience = st.text_input("Target Audience")
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("Start Date")
        with col2:
            end_date = st.date_input("End Date")
        submitted = st.form_submit_button("Create Campaign", type="primary")

    if submitted:
        if not name:
            st.error("Campaign Name is required.")
        else:
            payload = {
                "name": name,
                "description": description,
                "budget": budget,
                "target_audience": target_audience,
                "start_date": str(start_date),
                "end_date": str(end_date),
            }
            try:
                r = requests.post(f"{API_BASE_URL}/campaigns", json=payload, timeout=5)
                r.raise_for_status()
                st.success(f"Campaign '{name}' created successfully!")
                st.json(r.json())
            except Exception as e:
                st.warning(f"Could not reach API ({e}). In production, this would save your campaign.")
                st.json({**payload, "id": "preview", "status": "draft"})


elif page == "Add User":
    st.title("➕ Add New User")

    campaigns = fetch("/campaigns", SAMPLE_CAMPAIGNS)
    campaign_map = {c["name"]: c["id"] for c in campaigns}

    with st.form("user_form"):
        name = st.text_input("Full Name *")
        email = st.text_input("Email Address *")
        phone = st.text_input("Phone Number")
        campaign = st.selectbox("Assign to Campaign", ["(none)"] + list(campaign_map.keys()))
        submitted = st.form_submit_button("Add User", type="primary")

    if submitted:
        if not name or not email:
            st.error("Name and Email are required.")
        else:
            payload = {
                "name": name,
                "email": email,
                "phone": phone or None,
                "campaign_id": campaign_map.get(campaign),
            }
            try:
                r = requests.post(f"{API_BASE_URL}/users", json=payload, timeout=5)
                r.raise_for_status()
                st.success(f"User '{name}' added successfully!")
                st.json(r.json())
            except Exception as e:
                st.warning(f"Could not reach API ({e}). In production, this would save the user.")
                st.json({**payload, "id": "preview", "subscribed": True})

import os, sys
import pandas as pd
import plotly.express as px
import streamlit as st

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.snowflake_connection import get_connection

st.set_page_config(page_title="Student Placement Analytics Platform", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
    .stApp { background-color: var(--background-color); color: var(--text-color); transition: all 0.2s ease; }
    section[data-testid="stSidebar"], div[data-testid="stSidebarUserContent"] {
        background-color: var(--secondary-background-color) !important;
        border-right: 1px solid rgba(128, 128, 128, 0.15);
        transition: all 0.2s ease;
    }
    section[data-testid="stSidebar"] * { color: var(--text-color); }
    .kpi-card {
        background-color: var(--secondary-background-color);
        border: 1px solid rgba(128, 128, 128, 0.18);
        border-radius: 8px;
        height: 140px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        text-align: center;
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.04);
    }
    .kpi-title { color: var(--text-color); opacity: 0.7; font-size: 0.78rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 6px; }
    .kpi-value { color: var(--text-color); font-size: 1.75rem; font-weight: 700; line-height: 1.1; margin-bottom: 6px; }
    .kpi-sub { color: #2563EB; font-size: 0.8rem; font-weight: 500; }
    .page-title { font-size: 1.75rem; font-weight: 700; color: var(--text-color); margin-bottom: 4px; }
    .page-desc { color: var(--text-color); opacity: 0.7; font-size: 0.92rem; margin-bottom: 22px; }
</style>
""", unsafe_allow_html=True)

PRIMARY_COLOR, SECONDARY_COLOR = "#2563EB", "#64748B"

@st.cache_data(ttl=600)
def load_data(query: str) -> pd.DataFrame:
    conn = get_connection()
    try:
        df = pd.read_sql(query, conn)
        df.columns = [c.upper() for c in df.columns]
        return df
    finally:
        conn.close()

def header(title: str, desc: str):
    st.markdown(f'<div class="page-title">{title}</div><div class="page-desc">{desc}</div>', unsafe_allow_html=True)

def kpi_card(title: str, value, sub: str) -> str:
    return f'<div class="kpi-card"><div class="kpi-title">{title}</div><div class="kpi-value">{value}</div><div class="kpi-sub">{sub}</div></div>'

def chart_theme(fig, height=320):
    fig.update_layout(height=height, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(family="sans-serif", color="rgba(128, 128, 128, 0.85)"), margin=dict(l=20, r=20, t=30, b=20))
    fig.update_xaxes(showgrid=True, gridcolor="rgba(128, 128, 128, 0.12)")
    fig.update_yaxes(showgrid=True, gridcolor="rgba(128, 128, 128, 0.12)")
    return fig

def render_sidebar() -> str:
    st.sidebar.title("Placement Analytics")
    st.sidebar.caption("Enterprise Snowflake Platform")
    page = st.sidebar.radio("Navigation", ["Executive Summary", "College Performance", "Company Insights", "Offer Explorer"])
    st.sidebar.markdown("---")
    st.sidebar.markdown("**Environment Status**\n\nSnowflake: Connected  \nDatabase: PLACEMENT_DB  \nSchema: SEM")
    return page

def render_executive_summary():
    header("Executive Placement Overview", "High-level placement metrics, offer statuses, compensation benchmarks, and recruiter volume.")
    df = load_data("SELECT * FROM PLACEMENT_DB.SEM.V_EXECUTIVE_SUMMARY")
    if df.empty:
        return st.warning("No summary data available.")

    r = df.iloc[0]
    cols = st.columns(6)
    cards = [
        ("Total Offers", int(r['TOTAL_OFFERS']), f"{int(r['TOTAL_CANDIDATES'])} Candidates"),
        ("Accepted Offers", int(r['ACCEPTED_OFFERS']), f"{r['ACCEPTANCE_RATE_PCT']}% Acceptance"),
        ("Joined Offers", int(r['JOINED_OFFERS']), f"{r['JOIN_CONVERSION_RATE_PCT']}% Conversion"),
        ("Placement Rate", f"{r['PLACEMENT_RATE_PCT']}%", "Overall Cohort"),
        ("Average CTC", f"{float(r['AVG_CTC']):.1f} <span style='font-size:1rem;font-weight:500;'>LPA</span>", f"Range: {float(r['MIN_CTC']):.1f} - {float(r['MAX_CTC']):.1f}"),
        ("Median CTC", f"{float(r['MEDIAN_CTC']):.1f} <span style='font-size:1rem;font-weight:500;'>LPA</span>", f"{int(r['TOTAL_COMPANIES'])} Companies"),
    ]
    for col, (title, val, sub) in zip(cols, cards):
        col.markdown(kpi_card(title, val, sub), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Offers by Status")
        status_df = load_data("SELECT offer_status, COUNT(*) as offer_count FROM PLACEMENT_DB.SEM.V_OFFER_EXPLORER GROUP BY offer_status ORDER BY offer_count DESC")
        fig = px.bar(status_df, x="OFFER_STATUS", y="OFFER_COUNT", text="OFFER_COUNT", color_discrete_sequence=[PRIMARY_COLOR], labels={"OFFER_STATUS": "Status", "OFFER_COUNT": "Offers"})
        fig.update_traces(textposition='outside')
        st.plotly_chart(chart_theme(fig), use_container_width=True)

    with c2:
        st.subheader("Average CTC by Offer Level")
        lvl_df = load_data("SELECT offer_level, ROUND(AVG(ctc_lpa), 2) as avg_ctc FROM PLACEMENT_DB.SEM.V_OFFER_EXPLORER GROUP BY offer_level ORDER BY avg_ctc DESC")
        fig = px.bar(lvl_df, x="OFFER_LEVEL", y="AVG_CTC", text="AVG_CTC", color_discrete_sequence=[SECONDARY_COLOR], labels={"OFFER_LEVEL": "Offer Type", "AVG_CTC": "Average CTC (LPA)"})
        fig.update_traces(texttemplate='%{text} LPA', textposition='outside')
        st.plotly_chart(chart_theme(fig), use_container_width=True)

    c3, c4 = st.columns(2)
    with c3:
        st.subheader("Top Recruiters by Offer Count")
        top_df = load_data("SELECT company_name, COUNT(*) as offers, ROUND(AVG(ctc_lpa), 2) as avg_ctc FROM PLACEMENT_DB.SEM.V_OFFER_EXPLORER GROUP BY company_name ORDER BY offers DESC, avg_ctc DESC LIMIT 7")
        fig = px.bar(top_df, x="OFFERS", y="COMPANY_NAME", orientation='h', text="OFFERS", color_discrete_sequence=[PRIMARY_COLOR], labels={"OFFERS": "Offers", "COMPANY_NAME": "Company"})
        fig.update_traces(textposition='outside')
        fig.update_layout(yaxis=dict(autorange="reversed"))
        st.plotly_chart(chart_theme(fig), use_container_width=True)

    with c4:
        st.subheader("Offer Date Timeline")
        t_df = load_data("SELECT offer_date, COUNT(*) as offers FROM PLACEMENT_DB.SEM.V_OFFER_EXPLORER GROUP BY offer_date ORDER BY offer_date")
        fig = px.line(t_df, x="OFFER_DATE", y="OFFERS", markers=True, color_discrete_sequence=[PRIMARY_COLOR], labels={"OFFER_DATE": "Date", "OFFERS": "Offers Extended"})
        st.plotly_chart(chart_theme(fig), use_container_width=True)

def render_college_performance():
    header("College Performance Benchmark", "Placement metrics by college, tier performance, academic program analysis, and graduation year trends.")
    df = load_data("SELECT * FROM PLACEMENT_DB.SEM.V_COLLEGE_PERFORMANCE")
    if df.empty:
        return st.warning("No college performance data found.")

    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Placement Rate by College")
        agg = df.groupby("COLLEGE_NAME").agg(JOINED=("JOINED_OFFERS", "sum"), STUDENTS=("STUDENT_COUNT", "sum")).reset_index()
        agg["RATE"] = (100.0 * agg["JOINED"] / agg["STUDENTS"].replace(0, 1)).round(1)
        fig = px.bar(agg.sort_values(by="RATE"), x="RATE", y="COLLEGE_NAME", orientation='h', text="RATE", color_discrete_sequence=[PRIMARY_COLOR], labels={"RATE": "Rate (%)", "COLLEGE_NAME": "College"})
        fig.update_traces(texttemplate='%{text}%', textposition='outside')
        st.plotly_chart(chart_theme(fig, 340), use_container_width=True)

    with c2:
        st.subheader("Offers by College Tier")
        tier_df = load_data("SELECT college_tier, COUNT(*) as offers, ROUND(AVG(ctc_lpa), 2) as avg_ctc FROM PLACEMENT_DB.SEM.V_OFFER_EXPLORER GROUP BY college_tier ORDER BY college_tier")
        fig = px.bar(tier_df, x="COLLEGE_TIER", y="OFFERS", text="AVG_CTC", color_discrete_sequence=[SECONDARY_COLOR], labels={"COLLEGE_TIER": "Tier", "OFFERS": "Offers"})
        fig.update_traces(texttemplate='Avg: %{text} LPA', textposition='outside')
        st.plotly_chart(chart_theme(fig, 340), use_container_width=True)

    c3, c4 = st.columns(2)
    with c3:
        st.subheader("Average CTC by Branch")
        b_df = load_data("SELECT branch, ROUND(AVG(ctc_lpa), 2) as avg_ctc FROM PLACEMENT_DB.SEM.V_OFFER_EXPLORER GROUP BY branch ORDER BY avg_ctc DESC")
        fig = px.bar(b_df, x="BRANCH", y="AVG_CTC", text="AVG_CTC", color_discrete_sequence=[PRIMARY_COLOR], labels={"BRANCH": "Branch", "AVG_CTC": "Avg CTC (LPA)"})
        fig.update_traces(texttemplate='%{text} LPA', textposition='outside')
        st.plotly_chart(chart_theme(fig), use_container_width=True)

    with c4:
        st.subheader("Offers by Graduation Year")
        g_df = load_data("SELECT grad_year, COUNT(*) as offers FROM PLACEMENT_DB.SEM.V_OFFER_EXPLORER GROUP BY grad_year ORDER BY grad_year")
        fig = px.bar(g_df, x="GRAD_YEAR", y="OFFERS", text="OFFERS", color_discrete_sequence=[SECONDARY_COLOR], labels={"GRAD_YEAR": "Graduation Year", "OFFERS": "Offers"})
        fig.update_traces(textposition='outside')
        st.plotly_chart(chart_theme(fig), use_container_width=True)

    st.subheader("College Performance Details")
    cols = ["COLLEGE_NAME", "COLLEGE_TIER", "COLLEGE_CITY", "PROGRAM", "BRANCH", "TOTAL_OFFERS", "ACCEPTED_OFFERS", "JOINED_OFFERS", "PLACEMENT_RATE_PCT", "AVG_CTC"]
    st.dataframe(df[cols], use_container_width=True)

def render_company_insights():
    header("Company & Recruiter Insights", "Hiring volume by industry, acceptance rate, job cities, and compensation packages.")
    df = load_data("SELECT * FROM PLACEMENT_DB.SEM.V_COMPANY_INSIGHTS")
    if df.empty:
        return st.warning("No company insight data available.")

    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Offers by Industry")
        ind_df = df.groupby("INDUSTRY")["TOTAL_OFFERS"].sum().reset_index().sort_values(by="TOTAL_OFFERS", ascending=False)
        fig = px.bar(ind_df, x="TOTAL_OFFERS", y="INDUSTRY", orientation='h', text="TOTAL_OFFERS", color_discrete_sequence=[PRIMARY_COLOR], labels={"TOTAL_OFFERS": "Offers", "INDUSTRY": "Industry"})
        fig.update_traces(textposition='outside')
        fig.update_layout(yaxis=dict(autorange="reversed"))
        st.plotly_chart(chart_theme(fig), use_container_width=True)

    with c2:
        st.subheader("Top Job Cities")
        city_df = load_data("SELECT job_city, COUNT(*) as offers FROM PLACEMENT_DB.SEM.V_OFFER_EXPLORER GROUP BY job_city ORDER BY offers DESC LIMIT 7")
        fig = px.bar(city_df, x="JOB_CITY", y="OFFERS", text="OFFERS", color_discrete_sequence=[SECONDARY_COLOR], labels={"JOB_CITY": "Job City", "OFFERS": "Offers"})
        fig.update_traces(textposition='outside')
        st.plotly_chart(chart_theme(fig), use_container_width=True)

    st.subheader("Recruiter Performance Table")
    cols = ["COMPANY_NAME", "INDUSTRY", "SIZE_BAND", "ROLE_TITLE", "OFFER_LEVEL", "TOTAL_OFFERS", "ACCEPTED_OFFERS", "JOINED_OFFERS", "ACCEPTANCE_RATE_PCT", "AVG_CTC"]
    st.dataframe(df[cols], use_container_width=True)

def render_explorer():
    header("Offer Explorer", "Filterable offer-level records with dynamic aggregations and CSV data export.")
    df = load_data("SELECT * FROM PLACEMENT_DB.SEM.V_OFFER_EXPLORER")
    if df.empty:
        return st.warning("No offer records found.")

    with st.expander("Filter Controls", expanded=True):
        f1, f2, f3, f4 = st.columns(4)
        c_filter = f1.multiselect("College", sorted(df["COLLEGE_NAME"].dropna().unique()))
        t_filter = f1.multiselect("College Tier", sorted(df["COLLEGE_TIER"].dropna().unique()))
        co_filter = f2.multiselect("Company", sorted(df["COMPANY_NAME"].dropna().unique()))
        i_filter = f2.multiselect("Industry", sorted(df["INDUSTRY"].dropna().unique()))
        p_filter = f3.multiselect("Program", sorted(df["PROGRAM"].dropna().unique()))
        b_filter = f3.multiselect("Branch", sorted(df["BRANCH"].dropna().unique()))
        s_filter = f4.multiselect("Offer Status", sorted(df["OFFER_STATUS"].dropna().unique()))
        ci_filter = f4.multiselect("Job City", sorted(df["JOB_CITY"].dropna().unique()))

    filtered = df.copy()
    filter_map = [
        ("COLLEGE_NAME", c_filter), ("COLLEGE_TIER", t_filter),
        ("COMPANY_NAME", co_filter), ("INDUSTRY", i_filter),
        ("PROGRAM", p_filter), ("BRANCH", b_filter),
        ("OFFER_STATUS", s_filter), ("JOB_CITY", ci_filter)
    ]
    for col, vals in filter_map:
        if vals:
            filtered = filtered[filtered[col].isin(vals)]

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Filtered Offers", len(filtered))
    m2.metric("Filtered Avg CTC", f"{filtered['CTC_LPA'].mean():.2f} LPA" if not filtered.empty else "N/A")
    m3.metric("Accepted Count", int(filtered['IS_ACCEPTED'].sum()) if not filtered.empty else 0)
    m4.metric("Joined Count", int(filtered['IS_JOINED'].sum()) if not filtered.empty else 0)

    st.markdown("<br>", unsafe_allow_html=True)
    cols = ["OFFER_ID", "OFFER_DATE", "STUDENT_ID", "PROGRAM", "BRANCH", "CGPA_BAND", "COLLEGE_NAME", "COLLEGE_TIER", "COMPANY_NAME", "INDUSTRY", "ROLE_TITLE", "OFFER_LEVEL", "CTC_LPA", "JOB_CITY", "OFFER_STATUS"]
    st.dataframe(filtered[cols], use_container_width=True)

    csv_data = filtered.to_csv(index=False).encode('utf-8')
    st.download_button("Download Filtered Records as CSV", data=csv_data, file_name="placement_offers_filtered.csv", mime="text/csv")

def main():
    page = render_sidebar()
    views = {
        "Executive Summary": render_executive_summary,
        "College Performance": render_college_performance,
        "Company Insights": render_company_insights,
        "Offer Explorer": render_explorer
    }
    views.get(page, render_executive_summary)()

if __name__ == "__main__":
    main()

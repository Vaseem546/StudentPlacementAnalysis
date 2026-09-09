import os, sys, pandas as pd, plotly.express as px, streamlit as st

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.snowflake_connection import get_connection

st.set_page_config(page_title="Student Placement Analytics Platform", layout="wide", initial_sidebar_state="expanded")
st.markdown("""<style>
    .stApp { background-color: var(--background-color); color: var(--text-color); }
    section[data-testid="stSidebar"] { background-color: var(--secondary-background-color) !important; border-right: 1px solid rgba(128,128,128,0.15); }
    .kpi-card { background-color: var(--secondary-background-color); border: 1px solid rgba(128,128,128,0.18); border-radius: 8px; height: 130px; display: flex; flex-direction: column; justify-content: center; align-items: center; text-align: center; }
    .kpi-title { opacity: 0.7; font-size: 0.78rem; font-weight: 600; text-transform: uppercase; margin-bottom: 4px; }
    .kpi-value { font-size: 1.7rem; font-weight: 700; line-height: 1.1; margin-bottom: 4px; }
    .kpi-sub { color: #2563EB; font-size: 0.8rem; font-weight: 500; }
    .page-title { font-size: 1.75rem; font-weight: 700; margin-bottom: 2px; }
    .page-desc { opacity: 0.7; font-size: 0.9rem; margin-bottom: 20px; }
</style>""", unsafe_allow_html=True)

CLR1, CLR2 = "#2563EB", "#64748B"

@st.cache_data(ttl=600)
def load_data(q: str):
    conn = get_connection()
    try:
        df = pd.read_sql(q, conn)
        df.columns = [c.upper() for c in df.columns]
        return df
    finally:
        conn.close()

def header(title, desc):
    st.markdown(f'<div class="page-title">{title}</div><div class="page-desc">{desc}</div>', unsafe_allow_html=True)

def chart_panel(col, title, fig, h=320, tmpl=None, rev_y=False):
    with col:
        st.subheader(title)
        fig.update_layout(height=h, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(family="sans-serif", color="rgba(128,128,128,0.85)"), margin=dict(l=20, r=20, t=30, b=20))
        fig.update_xaxes(showgrid=True, gridcolor="rgba(128,128,128,0.12)").update_yaxes(showgrid=True, gridcolor="rgba(128,128,128,0.12)")
        if rev_y: fig.update_layout(yaxis=dict(autorange="reversed"))
        if tmpl: fig.update_traces(texttemplate=tmpl, textposition="outside")
        elif any(getattr(d, "text", None) is not None for d in fig.data): fig.update_traces(textposition="outside")
        st.plotly_chart(fig, use_container_width=True)

def render_sidebar():
    st.sidebar.title("Placement Analytics")
    page = st.sidebar.radio("Navigation", ["Executive Summary", "College Performance", "Company Insights", "Offer Explorer"])
    st.sidebar.markdown("---\n**Snowflake:** Connected  \n**Database:** PLACEMENT_DB  \n**Schema:** SEM")
    return page

def render_executive_summary():
    header("Executive Placement Overview", "High-level placement metrics, offer statuses, compensation benchmarks, and recruiter volume.")
    df = load_data("SELECT * FROM PLACEMENT_DB.SEM.V_EXECUTIVE_SUMMARY")
    if df.empty: return st.warning("No summary data available.")
    r = df.iloc[0]
    cards = [
        ("Total Offers", int(r['TOTAL_OFFERS']), f"{int(r['TOTAL_CANDIDATES'])} Candidates"),
        ("Accepted Offers", int(r['ACCEPTED_OFFERS']), f"{r['ACCEPTANCE_RATE_PCT']}% Acceptance"),
        ("Joined Offers", int(r['JOINED_OFFERS']), f"{r['JOIN_CONVERSION_RATE_PCT']}% Conversion"),
        ("Placement Rate", f"{r['PLACEMENT_RATE_PCT']}%", "Overall Cohort"),
        ("Average CTC", f"{float(r['AVG_CTC']):.1f} <span style='font-size:1rem;font-weight:500;'>LPA</span>", f"Range: {float(r['MIN_CTC']):.1f} - {float(r['MAX_CTC']):.1f}"),
        ("Median CTC", f"{float(r['MEDIAN_CTC']):.1f} <span style='font-size:1rem;font-weight:500;'>LPA</span>", f"{int(r['TOTAL_COMPANIES'])} Companies"),
    ]
    for col, (t, v, s) in zip(st.columns(6), cards):
        col.markdown(f'<div class="kpi-card"><div class="kpi-title">{t}</div><div class="kpi-value">{v}</div><div class="kpi-sub">{s}</div></div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    chart_panel(c1, "Offers by Status", px.bar(load_data("SELECT offer_status, COUNT(*) as cnt FROM PLACEMENT_DB.SEM.V_OFFER_EXPLORER GROUP BY offer_status ORDER BY cnt DESC"), x="OFFER_STATUS", y="CNT", text="CNT", color_discrete_sequence=[CLR1], labels={"OFFER_STATUS": "Status", "CNT": "Offers"}))
    chart_panel(c2, "Average CTC by Offer Level", px.bar(load_data("SELECT offer_level, ROUND(AVG(ctc_lpa), 2) as avg_ctc FROM PLACEMENT_DB.SEM.V_OFFER_EXPLORER GROUP BY offer_level ORDER BY avg_ctc DESC"), x="OFFER_LEVEL", y="AVG_CTC", text="AVG_CTC", color_discrete_sequence=[CLR2], labels={"OFFER_LEVEL": "Offer Type", "AVG_CTC": "Average CTC (LPA)"}), tmpl='%{text} LPA')
    c3, c4 = st.columns(2)
    chart_panel(c3, "Top Recruiters by Offer Count", px.bar(load_data("SELECT company_name, COUNT(*) as offers, ROUND(AVG(ctc_lpa), 2) as avg_ctc FROM PLACEMENT_DB.SEM.V_OFFER_EXPLORER GROUP BY company_name ORDER BY offers DESC, avg_ctc DESC LIMIT 7"), x="OFFERS", y="COMPANY_NAME", orientation='h', text="OFFERS", color_discrete_sequence=[CLR1], labels={"OFFERS": "Offers", "COMPANY_NAME": "Company"}), rev_y=True)
    chart_panel(c4, "Offer Date Timeline", px.line(load_data("SELECT offer_date, COUNT(*) as offers FROM PLACEMENT_DB.SEM.V_OFFER_EXPLORER GROUP BY offer_date ORDER BY offer_date"), x="OFFER_DATE", y="OFFERS", markers=True, color_discrete_sequence=[CLR1], labels={"OFFER_DATE": "Date", "OFFERS": "Offers Extended"}))

def render_college_performance():
    header("College Performance Benchmark", "Placement metrics by college, tier performance, academic program analysis, and graduation year trends.")
    df = load_data("SELECT * FROM PLACEMENT_DB.SEM.V_COLLEGE_PERFORMANCE")
    if df.empty: return st.warning("No college performance data found.")
    c1, c2 = st.columns(2)
    agg = df.groupby("COLLEGE_NAME").agg(JOINED=("JOINED_OFFERS", "sum"), STUDENTS=("STUDENT_COUNT", "sum")).reset_index()
    agg["RATE"] = (100.0 * agg["JOINED"] / agg["STUDENTS"].replace(0, 1)).round(1)
    chart_panel(c1, "Placement Rate by College", px.bar(agg.sort_values(by="RATE"), x="RATE", y="COLLEGE_NAME", orientation='h', text="RATE", color_discrete_sequence=[CLR1], labels={"RATE": "Rate (%)", "COLLEGE_NAME": "College"}), tmpl='%{text}%')
    chart_panel(c2, "Offers by College Tier", px.bar(load_data("SELECT college_tier, COUNT(*) as offers, ROUND(AVG(ctc_lpa), 2) as avg_ctc FROM PLACEMENT_DB.SEM.V_OFFER_EXPLORER GROUP BY college_tier ORDER BY college_tier"), x="COLLEGE_TIER", y="OFFERS", text="AVG_CTC", color_discrete_sequence=[CLR2], labels={"COLLEGE_TIER": "Tier", "OFFERS": "Offers"}), tmpl='Avg: %{text} LPA')
    c3, c4 = st.columns(2)
    chart_panel(c3, "Average CTC by Branch", px.bar(load_data("SELECT branch, ROUND(AVG(ctc_lpa), 2) as avg_ctc FROM PLACEMENT_DB.SEM.V_OFFER_EXPLORER GROUP BY branch ORDER BY avg_ctc DESC"), x="BRANCH", y="AVG_CTC", text="AVG_CTC", color_discrete_sequence=[CLR1], labels={"BRANCH": "Branch", "AVG_CTC": "Avg CTC (LPA)"}), tmpl='%{text} LPA')
    chart_panel(c4, "Offers by Graduation Year", px.bar(load_data("SELECT grad_year, COUNT(*) as offers FROM PLACEMENT_DB.SEM.V_OFFER_EXPLORER GROUP BY grad_year ORDER BY grad_year"), x="GRAD_YEAR", y="OFFERS", text="OFFERS", color_discrete_sequence=[CLR2], labels={"GRAD_YEAR": "Graduation Year", "OFFERS": "Offers"}))
    st.subheader("College Performance Details")
    st.dataframe(df[["COLLEGE_NAME", "COLLEGE_TIER", "COLLEGE_CITY", "PROGRAM", "BRANCH", "TOTAL_OFFERS", "ACCEPTED_OFFERS", "JOINED_OFFERS", "PLACEMENT_RATE_PCT", "AVG_CTC"]], use_container_width=True)

def render_company_insights():
    header("Company & Recruiter Insights", "Hiring volume by industry, acceptance rate, job cities, and compensation packages.")
    df = load_data("SELECT * FROM PLACEMENT_DB.SEM.V_COMPANY_INSIGHTS")
    if df.empty: return st.warning("No company insight data available.")
    c1, c2 = st.columns(2)
    ind_df = df.groupby("INDUSTRY")["TOTAL_OFFERS"].sum().reset_index().sort_values(by="TOTAL_OFFERS", ascending=False)
    chart_panel(c1, "Offers by Industry", px.bar(ind_df, x="TOTAL_OFFERS", y="INDUSTRY", orientation='h', text="TOTAL_OFFERS", color_discrete_sequence=[CLR1], labels={"TOTAL_OFFERS": "Offers", "INDUSTRY": "Industry"}), rev_y=True)
    chart_panel(c2, "Top Job Cities", px.bar(load_data("SELECT job_city, COUNT(*) as offers FROM PLACEMENT_DB.SEM.V_OFFER_EXPLORER GROUP BY job_city ORDER BY offers DESC LIMIT 7"), x="JOB_CITY", y="OFFERS", text="OFFERS", color_discrete_sequence=[CLR2], labels={"JOB_CITY": "Job City", "OFFERS": "Offers"}))
    st.subheader("Recruiter Performance Table")
    st.dataframe(df[["COMPANY_NAME", "INDUSTRY", "SIZE_BAND", "ROLE_TITLE", "OFFER_LEVEL", "TOTAL_OFFERS", "ACCEPTED_OFFERS", "JOINED_OFFERS", "ACCEPTANCE_RATE_PCT", "AVG_CTC"]], use_container_width=True)

def render_explorer():
    header("Offer Explorer", "Filterable offer-level records with dynamic aggregations and CSV data export.")
    df = load_data("SELECT * FROM PLACEMENT_DB.SEM.V_OFFER_EXPLORER")
    if df.empty: return st.warning("No offer records found.")
    filtered = df.copy()
    with st.expander("Filter Controls", expanded=True):
        f_cols = st.columns(4)
        for i, (l, col) in enumerate([("College", "COLLEGE_NAME"), ("College Tier", "COLLEGE_TIER"), ("Company", "COMPANY_NAME"), ("Industry", "INDUSTRY"), ("Program", "PROGRAM"), ("Branch", "BRANCH"), ("Offer Status", "OFFER_STATUS"), ("Job City", "JOB_CITY")]):
            sel = f_cols[i // 2].multiselect(l, sorted(df[col].dropna().unique()))
            if sel: filtered = filtered[filtered[col].isin(sel)]
    m = st.columns(4)
    m[0].metric("Filtered Offers", len(filtered))
    m[1].metric("Filtered Avg CTC", f"{filtered['CTC_LPA'].mean():.2f} LPA" if not filtered.empty else "N/A")
    m[2].metric("Accepted Count", int(filtered['IS_ACCEPTED'].sum()) if not filtered.empty else 0)
    m[3].metric("Joined Count", int(filtered['IS_JOINED'].sum()) if not filtered.empty else 0)
    st.markdown("<br>", unsafe_allow_html=True)
    cols = ["OFFER_ID", "OFFER_DATE", "STUDENT_ID", "PROGRAM", "BRANCH", "CGPA_BAND", "COLLEGE_NAME", "COLLEGE_TIER", "COMPANY_NAME", "INDUSTRY", "ROLE_TITLE", "OFFER_LEVEL", "CTC_LPA", "JOB_CITY", "OFFER_STATUS"]
    st.dataframe(filtered[cols], use_container_width=True)
    st.download_button("Download Filtered Records as CSV", data=filtered.to_csv(index=False).encode('utf-8'), file_name="placement_offers_filtered.csv", mime="text/csv")

def main():
    views = {"Executive Summary": render_executive_summary, "College Performance": render_college_performance, "Company Insights": render_company_insights, "Offer Explorer": render_explorer}
    views.get(render_sidebar(), render_executive_summary)()

if __name__ == "__main__":
    main()

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import io

st.set_page_config(page_title="Predictive Stock Dashboard", layout="wide")

# ----------------------------
# Config / Defaults
# ----------------------------
DEFAULT_WATCHLIST = [
    "AAPL","MSFT","AMZN","GOOGL","META","NVDA","TSLA",
    "BRK.B","JPM","V","MA","UNH","XOM","JNJ","PG","HD",
    "KO","PEP","COST","AVGO"
]

DATE_COL = "date"
NAME_COL = "Name"
RET_COL = "predicted_daily_return"
VOL_COL = "predicted_volatility"
SIG_COL = "signal"

# Your CSV column is spelled "confdence_score" per your message.
# We’ll support both spellings to be safe.
CONF_CANDIDATES = ["confdence_score", "confidence_score"]

PCT_FMT = ".2%"  # for daily decimal values shown as percent


# ----------------------------
# Data Loading
# ----------------------------
@st.cache_data(show_spinner=False)
def load_data_from_bytes(file_bytes: bytes) -> pd.DataFrame:
    return pd.read_csv(io.BytesIO(file_bytes))

@st.cache_data(show_spinner=False)
def load_data_from_path(path: str) -> pd.DataFrame:
    return pd.read_csv(path)

def standardize_df(df: pd.DataFrame) -> tuple[pd.DataFrame, str | None]:
    """Validate, clean, standardize column types. Returns cleaned df and detected confidence col (or None)."""
    required = {NAME_COL, DATE_COL, RET_COL, VOL_COL, SIG_COL}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"CSV missing required columns: {sorted(list(missing))}")

    # Detect confidence column if present
    conf_col = None
    for c in CONF_CANDIDATES:
        if c in df.columns:
            conf_col = c
            break

    # Parse date
    df[DATE_COL] = pd.to_datetime(df[DATE_COL], errors="coerce")

    # Normalize Name (tickers)
    df[NAME_COL] = df[NAME_COL].astype(str).str.strip().str.upper()
    df[NAME_COL] = df[NAME_COL].str.replace("-", ".", regex=False)  # BRK-B -> BRK.B

    # Numeric coercion
    df[RET_COL] = pd.to_numeric(df[RET_COL], errors="coerce")
    df[VOL_COL] = pd.to_numeric(df[VOL_COL], errors="coerce")

    if conf_col:
        df[conf_col] = pd.to_numeric(df[conf_col], errors="coerce")

    # Clean/standardize signal
    df[SIG_COL] = (
        df[SIG_COL].astype(str).str.strip().str.lower()
        .replace({"b": "buy", "s": "sell"})
    )

    # Drop unusable rows
    df = df.dropna(subset=[NAME_COL, DATE_COL, RET_COL, VOL_COL, SIG_COL])

    # Keep only buy/sell signals (prevents unexpected values from polluting charts)
    df = df[df[SIG_COL].isin(["buy", "sell"])]

    # Sort
    df = df.sort_values([NAME_COL, DATE_COL]).reset_index(drop=True)

    return df, conf_col


# ----------------------------
# Sidebar: Inputs
# ----------------------------
st.sidebar.title("Filters")

uploaded = st.sidebar.file_uploader("Upload CSV", type=["csv"])
data_path = st.sidebar.text_input("…or CSV Path", "/home/controlm/labs/sp500-analytics-ai/data/sp500_predictions.csv")

try:
    if uploaded is not None:
        raw_df = load_data_from_bytes(uploaded.getvalue())
    else:
        raw_df = load_data_from_path(data_path)

    df, CONF_COL = standardize_df(raw_df)

except Exception as e:
    st.error(f"Failed to load/parse data: {e}")
    st.stop()

all_names = sorted(df[NAME_COL].unique().tolist())

# Default watchlist: keep only those present
default_list = [x for x in DEFAULT_WATCHLIST if x in all_names]
if len(default_list) == 0:
    default_list = all_names[: min(10, len(all_names))]

# Optional ticker search for convenience
ticker_search = st.sidebar.text_input("Search tickers (optional)", "")
filtered_options = (
    [n for n in all_names if ticker_search.upper() in str(n).upper()]
    if ticker_search else all_names
)

selected_names = st.sidebar.multiselect(
    "Select Stocks",
    options=filtered_options,
    default=[x for x in default_list if x in filtered_options] if ticker_search else default_list
)

# Date range
min_date = df[DATE_COL].min()
max_date = df[DATE_COL].max()

date_range = st.sidebar.date_input(
    "Date Range",
    value=(min_date.date(), max_date.date()),
    min_value=min_date.date(),
    max_value=max_date.date()
)

# Default to Average over Range (your requirement)
agg_mode = st.sidebar.radio(
    "Ranking / Entity Aggregation",
    options=["Latest in Range", "Average over Range"],
    index=1,  # ✅ Default to Average over Range
    help="Controls Top Gainers/Decliners and Entity summary charts."
)

top_n = st.sidebar.slider("Top N (Gainers/Decliners)", 5, 50, 10)

# Optional confidence filter if confidence column exists
if CONF_COL:
    st.sidebar.markdown("---")
    conf_min = float(np.nanmin(df[CONF_COL])) if df[CONF_COL].notna().any() else 0.0
    conf_max = float(np.nanmax(df[CONF_COL])) if df[CONF_COL].notna().any() else 1.0
    step = (conf_max - conf_min) / 100 if conf_max > conf_min else 0.01
    conf_filter = st.sidebar.slider(
        "Min Confidence Score",
        min_value=float(conf_min),
        max_value=float(conf_max),
        value=float(conf_min),
        step=float(step)
    )
else:
    conf_filter = None


# ----------------------------
# Apply Filters
# ----------------------------
start_date, end_date = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])

fdf = df[(df[DATE_COL] >= start_date) & (df[DATE_COL] <= end_date)].copy()

if conf_filter is not None and CONF_COL:
    fdf = fdf[fdf[CONF_COL] >= conf_filter]

# Time series subset for selected stocks
ts_df = fdf[fdf[NAME_COL].isin(selected_names)].copy()


# ----------------------------
# Helper functions
# ----------------------------
def latest_snapshot(frame: pd.DataFrame) -> pd.DataFrame:
    """Return latest row per Name within current filtered range."""
    idx = frame.groupby(NAME_COL)[DATE_COL].idxmax()
    return frame.loc[idx].copy()

def entity_summary(frame: pd.DataFrame, mode: str) -> pd.DataFrame:
    """
    Compute per-entity metrics used for bar charts + pie breakdown.
    Returns columns: Name, return_metric, vol_metric, count
    """
    if frame.empty:
        return pd.DataFrame(columns=[NAME_COL, "return_metric", "vol_metric", "count"])

    if mode == "Latest in Range":
        snap = latest_snapshot(frame)
        out = snap[[NAME_COL, RET_COL, VOL_COL]].copy()
        out["count"] = 1
        out = out.rename(columns={RET_COL: "return_metric", VOL_COL: "vol_metric"})
        return out
    else:
        out = frame.groupby(NAME_COL).agg(
            return_metric=(RET_COL, "mean"),
            vol_metric=(VOL_COL, "mean"),
            count=(RET_COL, "size")
        ).reset_index()
        return out

summary = entity_summary(fdf, agg_mode)


# ----------------------------
# Header / KPIs
# ----------------------------
st.title("Predictive Stock Dashboard")

c1, c2, c3, c4 = st.columns(4)
c1.metric("Rows (filtered)", f"{len(fdf):,}")
c2.metric("Stocks in dataset", f"{len(all_names):,}")
c3.metric("Selected stocks", f"{len(selected_names):,}")
c4.metric("Date range", f"{start_date.date()} → {end_date.date()}")

st.markdown("---")


# =========================================================
# Chart 1: Predicted Daily Return over Time (signals on hover)
# =========================================================
st.subheader("1) Predicted Daily Return over Time (Signals shown on hover)")

if ts_df.empty:
    st.info("No data for the selected filters/stocks.")
else:
    # Build hover fields: show signal always, show confidence if available
    hover_data = {
        SIG_COL: True,
        RET_COL: False,   # we’ll format return in hovertemplate
        VOL_COL: False,   # optional; keep off by default
        DATE_COL: False,
        NAME_COL: False
    }
    if CONF_COL:
        hover_data[CONF_COL] = True

    fig1 = px.line(
        ts_df,
        x=DATE_COL,
        y=RET_COL,
        color=NAME_COL,
        title="Predicted Daily Return (Selected Stocks)",
        hover_data=hover_data
    )

    # Format y-axis as percent (daily decimal -> %)
    fig1.update_yaxes(tickformat=PCT_FMT, title_text="Predicted Daily Return (%)")

    # Custom hover to show signal prominently (no markers needed)
    if CONF_COL:
        fig1.update_traces(
            hovertemplate=(
                "Stock: %{legendgroup}<br>"
                "Date: %{x|%Y-%m-%d}<br>"
                "Return: %{y:.2%}<br>"
                f"Signal: %{{customdata[0]}}<br>"
                f"Confidence: %{{customdata[1]:.3f}}"
                "<extra></extra>"
            ),
            customdata=np.stack([ts_df[SIG_COL], ts_df[CONF_COL]], axis=-1)
        )
    else:
        fig1.update_traces(
            hovertemplate=(
                "Stock: %{legendgroup}<br>"
                "Date: %{x|%Y-%m-%d}<br>"
                "Return: %{y:.2%}<br>"
                f"Signal: %{{customdata[0]}}"
                "<extra></extra>"
            ),
            customdata=np.stack([ts_df[SIG_COL]], axis=-1)
        )

    fig1.update_layout(legend_title_text="Stock", height=480)
    st.plotly_chart(fig1, use_container_width=True)

st.markdown("---")


# =========================================================
# Chart 2 & 3: Top Predicted Gainers / Decliners (all stocks)
# =========================================================
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("2) Top Predicted Gainers (All Stocks)")
    if summary.empty:
        st.info("No data available for this date range / filters.")
    else:
        top_gainers = summary.sort_values("return_metric", ascending=False).head(top_n)
        fig2 = px.bar(
            top_gainers,
            x="return_metric",
            y=NAME_COL,
            orientation="h",
            title=f"Top {top_n} Predicted Gainers ({agg_mode})",
            labels={"return_metric": "Predicted Daily Return (%)", NAME_COL: "Stock"}
        )
        fig2.update_xaxes(tickformat=PCT_FMT)
        fig2.update_layout(height=420, yaxis={"categoryorder": "total ascending"})
        st.plotly_chart(fig2, use_container_width=True)

with col_right:
    st.subheader("3) Top Predicted Decliners (All Stocks)")
    if summary.empty:
        st.info("No data available for this date range / filters.")
    else:
        top_decliners = summary.sort_values("return_metric", ascending=True).head(top_n)
        fig3 = px.bar(
            top_decliners,
            x="return_metric",
            y=NAME_COL,
            orientation="h",
            title=f"Top {top_n} Predicted Decliners ({agg_mode})",
            labels={"return_metric": "Predicted Daily Return (%)", NAME_COL: "Stock"}
        )
        fig3.update_xaxes(tickformat=PCT_FMT)
        fig3.update_layout(height=420, yaxis={"categoryorder": "total descending"})
        st.plotly_chart(fig3, use_container_width=True)

st.markdown("---")


# =========================================================
# Chart 4: Predicted Volatility by Entity
# =========================================================
st.subheader("4) Predicted Volatility by Entity")
if summary.empty:
    st.info("No data available for this date range / filters.")
else:
    top_vol = summary.sort_values("vol_metric", ascending=False).head(50)  # cap for readability
    fig4 = px.bar(
        top_vol.sort_values("vol_metric", ascending=True),
        x="vol_metric",
        y=NAME_COL,
        orientation="h",
        title=f"Predicted Daily Volatility by Entity ({agg_mode}) — Top 50 shown",
        labels={"vol_metric": "Predicted Daily Volatility (%)", NAME_COL: "Stock"}
    )
    fig4.update_xaxes(tickformat=PCT_FMT)
    fig4.update_layout(height=520)
    st.plotly_chart(fig4, use_container_width=True)

# =========================================================
# Chart 5: Predicted Daily Return by Entity
# =========================================================
st.subheader("5) Predicted Daily Return by Entity")
if summary.empty:
    st.info("No data available for this date range / filters.")
else:
    top_ret = summary.reindex(summary["return_metric"].abs().sort_values(ascending=False).index).head(50)
    fig5 = px.bar(
        top_ret.sort_values("return_metric", ascending=True),
        x="return_metric",
        y=NAME_COL,
        orientation="h",
        title=f"Predicted Daily Return by Entity ({agg_mode}) — Top 50 by |return| shown",
        labels={"return_metric": "Predicted Daily Return (%)", NAME_COL: "Stock"}
    )
    fig5.update_xaxes(tickformat=PCT_FMT)
    fig5.update_layout(height=520)
    st.plotly_chart(fig5, use_container_width=True)

st.markdown("---")


# =========================================================
# Chart 6: Signal Distribution - Buy vs. Sell
# =========================================================
st.subheader("6) Signal Distribution — Buy vs. Sell")
if fdf.empty:
    st.info("No data available for this date range / filters.")
else:
    sig_counts = fdf[SIG_COL].value_counts().reset_index()
    sig_counts.columns = [SIG_COL, "count"]

    fig6 = px.pie(
        sig_counts,
        names=SIG_COL,
        values="count",
        title="Signal Distribution (Filtered Data)",
        hole=0.35
    )
    fig6.update_layout(height=420)
    st.plotly_chart(fig6, use_container_width=True)

# =========================================================
# Chart 7: Volatility Breakdown by Entity (Top 9 + Others avg)
# =========================================================
st.subheader("7) Volatility Breakdown by Entity (Top 9 + Others Avg)")
if summary.empty:
    st.info("No data available for this date range / filters.")
else:
    vol_rank = summary.sort_values("vol_metric", ascending=False).copy()
    top9 = vol_rank.head(9).copy()
    others = vol_rank.iloc[9:].copy()

    pie_df = top9[[NAME_COL, "vol_metric"]].rename(columns={"vol_metric": "value"}).copy()

    if not others.empty:
        others_avg = others["vol_metric"].mean()  # ✅ average volatility of remaining entities
        pie_df = pd.concat(
            [pie_df, pd.DataFrame({NAME_COL: ["Others (avg)"], "value": [others_avg]})],
            ignore_index=True
        )

    pie_df["value"] = pie_df["value"].clip(lower=0)

    fig7 = px.pie(
        pie_df,
        names=NAME_COL,
        values="value",
        title=f"Volatility Breakdown ({agg_mode}): Top 9 + Others (avg)"
    )
    fig7.update_traces(
        textposition="inside",
        textinfo="percent+label",
        hovertemplate="%{label}<br>Daily volatility: %{value:.2%}<br>Share of pie: %{percent}<extra></extra>"
    )
    fig7.update_layout(height=520)
    st.plotly_chart(fig7, use_container_width=True)

st.markdown("---")


# =========================================================
# Download filtered data
# =========================================================
st.subheader("Download")

if fdf.empty:
    st.info("Nothing to download (filtered dataset is empty).")
else:
    csv_buffer = io.StringIO()
    fdf.to_csv(csv_buffer, index=False)

    download_name = f"predictions_filtered_{start_date.date()}_to_{end_date.date()}.csv"

    st.download_button(
        label="⬇️ Download Filtered CSV",
        data=csv_buffer.getvalue(),
        file_name=download_name,
        mime="text/csv"
    )

with st.expander("Show filtered data preview"):
    st.dataframe(fdf.head(200), use_container_width=True)

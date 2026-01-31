# app.py
import os
import io
import numpy as np
import pandas as pd
import altair as alt
import streamlit as st

st.set_page_config(page_title="S&P 500 — 4-Chart Dashboard", layout="wide")

# =============================
# Settings & constants
# =============================
DEFAULT_CSV_PATH = "data/sp500_5yr.csv"
DEFAULT_PARQUET_PATH = "data/sp500_5yr.parquet"

DATE_COL = "date"
TICKER_COL = "Name"  # exact column name from your schema
OHLC_COLS = ["open", "high", "low", "close"]
VOLUME_COL = "volume"

# =============================
# Helpers
# =============================
def optimize_dtypes(df: pd.DataFrame) -> pd.DataFrame:
    """Downcast numeric columns and set category for ticker to save memory."""
    if DATE_COL in df.columns and not np.issubdtype(df[DATE_COL].dtype, np.datetime64):
        df[DATE_COL] = pd.to_datetime(df[DATE_COL], errors="coerce")
    if TICKER_COL in df.columns:
        df[TICKER_COL] = df[TICKER_COL].astype("category")
    for c in OHLC_COLS:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce", downcast="float")
    if VOLUME_COL in df.columns:
        df[VOLUME_COL] = pd.to_numeric(df[VOLUME_COL], errors="coerce", downcast="integer")
    return df


def validate_schema(df: pd.DataFrame):
    required = {DATE_COL, TICKER_COL, *OHLC_COLS, VOLUME_COL}
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(
            f"Missing required columns: {missing}. "
            f"Expected columns: {sorted(required)}"
        )


def add_return_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Adds:
      - daily_return_close: close->close % change (decimal, e.g., 0.0123 = 1.23%)
      - intraday_return_pct: (close-open)/open * 100 (already in percent units)
    """
    df = df.sort_values([TICKER_COL, DATE_COL]).reset_index(drop=True)

    # Close->Close daily return (decimal)
    df["daily_return_close"] = (
        df.groupby(TICKER_COL, observed=True)["close"].pct_change()
    )

    # Intraday daily % change per your formula (in percent units)
    # Keep full precision; we can round at display time.
    df["intraday_return_pct"] = ((df["close"] - df["open"]) / df["open"]) * 100.0

    return df


@st.cache_data(show_spinner=False)
def load_parquet(parquet_path: str) -> pd.DataFrame:
    df = pd.read_parquet(parquet_path)
    df = optimize_dtypes(df)
    validate_schema(df)
    df = add_return_columns(df)
    return df


@st.cache_data(show_spinner=False)
def convert_csv_bytes_to_parquet_and_load(csv_bytes: bytes, parquet_path: str | None = None) -> pd.DataFrame:
    df = pd.read_csv(
        io.BytesIO(csv_bytes),
        parse_dates=[DATE_COL],
        low_memory=False
    )
    df = optimize_dtypes(df)
    validate_schema(df)
    df = add_return_columns(df)
    if parquet_path:
        os.makedirs(os.path.dirname(parquet_path), exist_ok=True)
        df.to_parquet(parquet_path, index=False)
    return df


@st.cache_data(show_spinner=False)
def csv_to_parquet_once_and_load(csv_path: str, parquet_path: str) -> pd.DataFrame:
    if os.path.exists(parquet_path):
        return load_parquet(parquet_path)
    if not os.path.exists(csv_path):
        raise FileNotFoundError(
            f"Neither Parquet ({parquet_path}) nor CSV ({csv_path}) found. "
            "Upload a CSV via the sidebar or place your file at the default path."
        )
    df = pd.read_csv(csv_path, parse_dates=[DATE_COL], low_memory=False)
    df = optimize_dtypes(df)
    validate_schema(df)
    df = add_return_columns(df)
    os.makedirs(os.path.dirname(parquet_path), exist_ok=True)
    df.to_parquet(parquet_path, index=False)
    return df


def cap_selection(seq, n=20):
    return list(seq)[: n]


# =============================
# Sidebar: Data source
# =============================
with st.sidebar:
    st.header("Data")
    uploaded = st.file_uploader(
        "Upload CSV (date, open, high, low, close, volume, Name)",
        type=["csv"]
    )
    use_default = st.checkbox(f"Use default path ({DEFAULT_CSV_PATH})", value=not uploaded)
    st.caption("Tip: First run converts CSV → Parquet for faster reloads.")
    if st.button("Clear cache"):
        st.cache_data.clear()
        st.toast("Cache cleared.", icon="✅")

# Load data
try:
    if uploaded is not None and not use_default:
        df = convert_csv_bytes_to_parquet_and_load(
            csv_bytes=uploaded.getvalue(),
            parquet_path=DEFAULT_PARQUET_PATH  # persist for speed
        )
    else:
        df = csv_to_parquet_once_and_load(DEFAULT_CSV_PATH, DEFAULT_PARQUET_PATH)
except Exception as e:
    st.error(f"Failed to load data: {e}")
    st.stop()

# =============================
# Globals & Filters (apply ONLY to charts 1 & 4)
# =============================
all_tickers = list(
    df[TICKER_COL].cat.categories
    if pd.api.types.is_categorical_dtype(df[TICKER_COL])
    else df[TICKER_COL].unique()
)
all_tickers_sorted = sorted(all_tickers)

with st.sidebar:
    st.header("Filters (apply to Charts 1 & 4 only)")
    default_selection = [t for t in ["AAPL", "MSFT", "AMZN", "GOOGL", "META", "NVDA"] if t in all_tickers_sorted][:6] \
                        or all_tickers_sorted[:6]
    sel_tickers = st.multiselect("Tickers", options=all_tickers_sorted, default=default_selection)

    date_min, date_max = df[DATE_COL].min(), df[DATE_COL].max()
    dr = st.date_input("Date range", value=(date_min, date_max),
                       min_value=date_min, max_value=date_max)

    st.subheader("Chart 4 Return Basis")
    ret_basis = st.radio(
        "Select return for Daily Return vs. Volatility",
        options=["Close→Close", "Intraday (Open→Close)"],
        index=0,
        help="Close→Close uses pct_change(close). Intraday uses (close-open)/open."
    )

    st.subheader("Scatter Plot Tickers (Chart 4)")
    st.caption("Pick up to 20 for the scatter.")
    scatter_candidates = sel_tickers or all_tickers_sorted
    scatter_tickers = st.multiselect(
        "Scatter tickers (max 20)",
        options=scatter_candidates,
        default=cap_selection(scatter_candidates, 20)
    )
    if len(scatter_tickers) > 20:
        st.warning("You selected more than 20 tickers for the scatter; showing the first 20.")
        scatter_tickers = cap_selection(scatter_tickers, 20)

# Build filtered view (for Charts 1 & 4 only)
if isinstance(dr, tuple):
    start_date, end_date = pd.to_datetime(dr[0]), pd.to_datetime(dr[1])
else:
    # safety fallback
    start_date, end_date = df[DATE_COL].min(), df[DATE_COL].max()

mask = (df[DATE_COL] >= start_date) & (df[DATE_COL] <= end_date)
if sel_tickers:
    mask &= df[TICKER_COL].isin(sel_tickers)
df_filtered = df.loc[mask].copy()

# =============================
# Title & Counters
# =============================
st.title("S&P 500 — 4-Chart Dashboard")
c1, c2 = st.columns(2)
c1.metric("Total tickers in dataset", len(all_tickers_sorted))
c2.metric("Tickers selected (Charts 1 & 4)", len(sel_tickers) if len(sel_tickers) else 0)

# =============================
# Chart 1 — Closing price over time (FILTERED)
# =============================
st.subheader("1) Closing Price Over Time (Filtered by tickers & date)")
if df_filtered.empty:
    st.info("No data for the selected tickers/date range.")
else:
    price_chart = alt.Chart(df_filtered).mark_line().encode(
        x=alt.X(f"{DATE_COL}:T", title="Date"),
        y=alt.Y("close:Q", title="Close Price"),
        color=alt.Color(f"{TICKER_COL}:N", title="Ticker"),
        tooltip=[DATE_COL, TICKER_COL, "close"]
    ).properties(height=360)
    st.altair_chart(price_chart, use_container_width=True)

# =============================
# Charts 2 & 3 — Top 20 across FULL dataset using your formula
# =============================
# Average intraday return (Open->Close %), computed across ALL dates, per ticker
stats_all = (
    df.groupby(TICKER_COL, observed=True)
      .agg(
          avg_intraday_return_pct=("intraday_return_pct", "mean"),
          n_days=("intraday_return_pct", "count")
      )
      .reset_index()
      .dropna(subset=["avg_intraday_return_pct"])
)

# Chart 2 — Top 20 Gainers (ALL)
st.subheader("2) Top 20 Gainers — Avg Daily % Change (Open→Close) — All Stocks")
gainers = stats_all.sort_values("avg_intraday_return_pct", ascending=False).head(20)
if gainers.empty:
    st.info("No gainers available.")
else:
    g_chart = alt.Chart(gainers).mark_bar().encode(
        x=alt.X("avg_intraday_return_pct:Q", title="Avg Daily % Change", axis=alt.Axis(format=".2f")),
        y=alt.Y(f"{TICKER_COL}:N", sort="-x", title="Ticker"),
        tooltip=[
            TICKER_COL,
            alt.Tooltip("avg_intraday_return_pct:Q", title="Avg Daily % Change", format=".2f"),
            "n_days"
        ]
    ).properties(height=max(300, 20 * len(gainers)))
    st.altair_chart(g_chart, use_container_width=True)

# Chart 3 — Top 20 Decliners (ALL)
st.subheader("3) Top 20 Decliners — Avg Daily % Change (Open→Close) — All Stocks")
decliners = stats_all.sort_values("avg_intraday_return_pct", ascending=True).head(20)
if decliners.empty:
    st.info("No decliners available.")
else:
    d_chart = alt.Chart(decliners).mark_bar(color="#d62728").encode(
        x=alt.X("avg_intraday_return_pct:Q", title="Avg Daily % Change", axis=alt.Axis(format=".2f")),
        y=alt.Y(f"{TICKER_COL}:N", sort="x", title="Ticker"),
        tooltip=[
            TICKER_COL,
            alt.Tooltip("avg_intraday_return_pct:Q", title="Avg Daily % Change", format=".2f"),
            "n_days"
        ]
    ).properties(height=max(300, 20 * len(decliners)))
    st.altair_chart(d_chart, use_container_width=True)

# =============================
# Chart 4 — Daily Return vs. Volatility (FILTERED, up to 20 points)
# =============================
st.subheader("4) Daily Return vs. Volatility — Filtered (Avg vs Std Dev)")

if df_filtered.empty:
    st.info("No tickers to display for the selected filters.")
else:
    # Choose return basis
    if ret_basis == "Close→Close":
        ret_col = "daily_return_close"     # decimal units
        x_title = "Volatility (Std Dev of Daily Return, decimal)"
        y_title = "Average Daily Return (decimal)"
        x_axis = alt.Axis(format="%")
        y_axis = alt.Axis(format="%")
        # convert to % formatting by axis; data kept as decimals
    else:
        ret_col = "intraday_return_pct"    # percent units already
        x_title = "Volatility (Std Dev of Daily % Change)"
        y_title = "Average Daily % Change"
        x_axis = alt.Axis(format=".2f")
        y_axis = alt.Axis(format=".2f")

    stats_filtered = (
        df_filtered.groupby(TICKER_COL, observed=True)
                   .agg(
                       avg_return=(ret_col, "mean"),
                       volatility=(ret_col, "std"),
                       n_days=(ret_col, "count")
                   )
                   .reset_index()
                   .dropna(subset=["avg_return"])
    )

    if stats_filtered.empty:
        st.info("No computed stats for the selected filters.")
    else:
        scatter_df = stats_filtered.copy()
        # Apply user-selected tickers cap for scatter
        if scatter_tickers:
            scatter_df = scatter_df[scatter_df[TICKER_COL].isin(scatter_tickers)]
        if len(scatter_df) > 20:
            st.info("Showing first 20 tickers on the scatter plot (per your cap).")
            scatter_df = scatter_df.iloc[:20]

        scatter = alt.Chart(scatter_df).mark_circle(size=120).encode(
            x=alt.X("volatility:Q", title=x_title, axis=x_axis),
            y=alt.Y("avg_return:Q", title=y_title, axis=y_axis),
            color=alt.Color(f"{TICKER_COL}:N", title="Ticker"),
            tooltip=[
                TICKER_COL,
                alt.Tooltip("avg_return:Q", title=y_title, format=".4f"),
                alt.Tooltip("volatility:Q", title=x_title, format=".4f"),
                "n_days"
            ]
        ).properties(height=360)

        labels = scatter.mark_text(align="left", dx=7, dy=0).encode(
            text=f"{TICKER_COL}:N"
        )

        st.altair_chart(scatter + labels, use_container_width=True)

st.caption(
    "Notes: Charts 2 & 3 use the entire dataset and compute the average of (close - open) / open × 100 per ticker. "
    "Charts 1 & 4 respect the selected tickers and date range. "
    "Chart 4 lets you choose Close→Close or Intraday basis."
)

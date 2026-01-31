import streamlit as st
import pandas as pd
import requests
import time
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from scipy.stats import beta
from datetime import datetime
import os

# --- Configuration & Styles ---
st.set_page_config(
    page_title="Agentic Payment Ops", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Premium Look
st.markdown("""
<style>
    .metric-card {
        background-color: #1E1E1E;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #333;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    .metric-value {
        font-size: 2em;
        font-weight: bold;
        color: #ffffff;
    }
    .metric-label {
        font-size: 0.9em;
        color: #aaaaaa;
    }
    .stHeader {
        background: -webkit-linear-gradient(left, #ff4b4b, #ff9068);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    /* Status Indicators */
    .status-dot {
        height: 10px;
        width: 10px;
        border-radius: 50%;
        display: inline-block;
        margin-right: 5px;
    }
    /* Increase spacing between tabs */
    button[data-baseweb="tab"] {
        margin-right: 50px;
        font-size: 1.1rem;
    }
</style>
""", unsafe_allow_html=True)

# --- State Management ---
if "events" not in st.session_state:
    st.session_state.events = []
if "simulation_running" not in st.session_state:
    st.session_state.simulation_running = False

API_URL = os.getenv("API_URL", "http://localhost:8000")

# --- Helper Functions ---
def fetch_system_status():
    try:
        resp = requests.get(f"{API_URL}/system/status", timeout=1)
        if resp.status_code == 200:
            return resp.json()
    except:
        return None
    return None

def generate_mock_transaction():
    import random
    import uuid
    amounts = [50, 100, 250, 1000, 5000]
    currencies = ["USD", "EUR", "GBP"]
    return {
        "transaction_id": str(uuid.uuid4()),
        "amount": random.choice(amounts),
        "currency": random.choice(currencies),
        "payment_method": "credit_card",
        "merchant_id": "merchant_001"
    }

def run_simulation_step(speed):
    if st.session_state.simulation_running:
        tx = generate_mock_transaction()
        try:
            start_t = time.time()
            resp = requests.post(f"{API_URL}/process", json=tx)
            latency_ms = (time.time() - start_t) * 1000
            
            if resp.status_code == 200:
                data = resp.json()
                data.update(tx)
                data["timestamp"] = datetime.now()
                data["latency"] = latency_ms
                st.session_state.events.append(data)
                # Keep buffer manageable
                if len(st.session_state.events) > 100:
                    st.session_state.events.pop(0)
        except Exception as e:
            # Silence transient connection errors to avoid UI spam in high load
            # st.toast(f"Simulation Error: {e}")
            time.sleep(1) # Backoff on error
        
        # Enforce minimum sleep to prevent UI freezing (max 2 req/s effectively if speed=5)
        # "Light" mode: ensure at least 0.5s sleep always
        sleep_time = max(0.5, 1.0 / speed)
        time.sleep(sleep_time)
        st.rerun()

# --- Sidebar ---
with st.sidebar:
    st.header("Simulation Controls")
    
    sim_speed = st.slider("Traffic Speed (req/s)", 0.5, 5.0, 1.0)
    
    c1, c2 = st.columns(2)
    if st.session_state.simulation_running:
        if c1.button("Stop", type="primary", use_container_width=True):
            st.session_state.simulation_running = False
            st.rerun()
    else:
        if c1.button("Start", type="primary", use_container_width=True):
            st.session_state.simulation_running = True
            st.rerun()
            
    if c2.button("Clear Data", use_container_width=True):
        st.session_state.events = []
        st.rerun()

    st.divider()
    
    st.subheader("Chaos Engineering")
    # st.info("💡 To inject faults, modify the mocks in `agents/tools.py` directly (future feature: UI toggles).")
    
    with st.expander("Fault Injection", expanded=False):
        target_gw = st.selectbox("Target Gateway", ["Issuer_Alpha", "Issuer_Beta", "Issuer_Gamma"])
        
        # We need to maintain state for these sliders, ideally fetching current config
        # For simplicity, we'll just set it blindly for now, or use defaults
        new_sr = st.slider("Success Rate", 0.0, 1.0, 0.95, key="sr_slider")
        new_lat = st.slider("Mean Latency (s)", 0.0, 2.0, 0.2, key="lat_slider")
        
        if st.button("Apply Faults", type="secondary", use_container_width=True):
            try:
                payload = {
                    "gateway": target_gw,
                    "success_rate": new_sr,
                    "latency_mean": new_lat
                }
                resp = requests.post(f"{API_URL}/system/config", json=payload)
                if resp.status_code == 200:
                    st.toast(f"Updated {target_gw} configuration!")
                else:
                    st.error("Failed to update config")
            except Exception as e:
                st.error(f"Error: {e}")

    st.divider()
    st.subheader("Manual Trigger")
    with st.form("manual_tx_form", clear_on_submit=False):
        m_amt = st.number_input("Amount", 1, 10000, 100)
        m_curr = st.selectbox("Currency", ["USD", "EUR", "GBP", "JPY", "AUD", "CAD", "INR", "CNY", "CHF", "SGD"])
        m_method = st.selectbox("Payment Method", ["Credit Card", "PayPal", "Bank Transfer", "Crypto", "Apple Pay"])
        m_btn = st.form_submit_button("Process Transaction", type="primary")
        
        if m_btn:
            import uuid
            tx_data = {
                "transaction_id": str(uuid.uuid4()),
                "amount": m_amt,
                "currency": m_curr,
                "payment_method": m_method,
                "merchant_id": "manual_user"
            }
            try:
                start_t = time.time()
                resp = requests.post(f"{API_URL}/process", json=tx_data)
                latency_ms = (time.time() - start_t) * 1000
                
                if resp.status_code == 200:
                    data = resp.json()
                    data.update(tx_data)
                    data["timestamp"] = datetime.now()
                    data["latency"] = latency_ms
                    st.session_state.events.append(data)
                    st.toast(f"Transaction Processed! {data['success']}")
                else:
                    st.error(f"API Error: {resp.status_code}")
            except Exception as e:
                st.error(f"Connection Error: {e}")

# --- Main Layout ---
st.title("Agentic Payment Operations")

tab1, tab2, tab3 = st.tabs(["Live Operations", "Agent Brain", "Analytics"])

# --- TAB 1: Live Operations ---
with tab1:
    # KPI Row
    df = pd.DataFrame(st.session_state.events)
    
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    
    if not df.empty:
        success_rate = (df["success"].sum() / len(df)) * 100
        avg_latency = df["latency"].mean()
        intervention_count = df[df["intervention_plan"].notnull()].shape[0]
        total_vol = df["amount"].sum() if "amount" in df.columns else 0 # Mock amount not always in resp, need to fix if wanted
        
        kpi1.metric("Success Rate", f"{success_rate:.1f}%", delta_color="normal")
        kpi2.metric("Avg Latency", f"{avg_latency:.0f} ms")
        kpi3.metric("Agent Interventions", intervention_count)
        kpi4.metric("Total Transactions", len(df))
    else:
        for k in [kpi1, kpi2, kpi3, kpi4]:
            k.metric("Waiting...", "-")

    st.divider()
    
    st.divider()
    
    # --- Full Width Feed ---
    st.subheader("Transaction Feed")
    if not df.empty:
        # Table with styling
        # Ensure "amount" and "currency" are available (might be missing in old session state data)
        if "amount" not in df.columns:
            df["amount"] = 0
        if "currency" not in df.columns:
            df["currency"] = "USD"
        if "payment_method" not in df.columns:
            df["payment_method"] = "CC"
            
        display_df = df[["timestamp", "transaction_id", "amount", "currency", "payment_method", "route_decision", "success", "latency", "last_error"]].sort_values("timestamp", ascending=False)
        
        event = st.dataframe(
            display_df,
            column_config={
                "success": st.column_config.CheckboxColumn("Status"),
                "latency": st.column_config.NumberColumn("Wait (ms)", format="%d"),
                "timestamp": st.column_config.DatetimeColumn("Time", format="HH:mm:ss"),
                "amount": st.column_config.NumberColumn("Amt", format="$%d"),
                "transaction_id": st.column_config.TextColumn("Tx ID", width="small"),
                "payment_method": st.column_config.TextColumn("Method", width="small"),
                "route_decision": st.column_config.TextColumn("Bank / Gateway", width="medium"),
                "currency": st.column_config.TextColumn("Cur", width="small"),
                "last_error": st.column_config.TextColumn("Error", width="small")
            },
            use_container_width=True,
            hide_index=True,
            selection_mode="single-row",
            on_select="rerun"
        )
    else:
        st.info("Start simulation or use Manual Trigger to see transactions.")

    # --- Agent Decision Section (Below Feed) ---
    st.divider()
    st.subheader("Agent Decision & Recovery")
    
    # Logic to get selected row
    # (Streamlit selection API is a bit tricky, doing simple last-item fallback for now if nothing selected)
    # In real app, we'd use session state to track selection.
    
    selected_tx = None
    if not df.empty:
        # Check if user selected something in the dataframe above
        # Note: st.dataframe with on_select returns selection state but doesn't simply return the selected row data directly in a way easier than this hack for now without session state complexity.
        # Let's stick to showing the LATEST transaction by default if nothing is explicitly active, 
        # or just show the latest one to keep it responsive.
        selected_tx = df.iloc[-1] # Default to latest for immediate feedback
    
    if selected_tx is not None:
        st.markdown(f"**Transaction:** `{selected_tx['transaction_id']}`")
        
        # Reasoning Box
        with st.container(border=True):
            st.markdown("#### Recovery Agent Thoughts")
            if selected_tx.get("intervention_plan"):
                st.warning(f"Action Taken: **{selected_tx['intervention_plan']}**")
                # We need the full history to show the reasoning text, which is inside the history list
                # The API returns 'history'. Let's find the recovery step.
                history = selected_tx.get("history", [])
                recovery_step = next((x for x in history if x.get("step") == "recovery"), None)
                if recovery_step:
                    analysis = recovery_step.get("analysis", {})
                    
                    # Show summary and detailed reasoning
                    st.markdown(f"**Issue:** {analysis.get('summary', 'N/A')}")
                    
                    # Make reasoning expanded and use markdown for better readability
                    with st.expander("See Reasoning Trace", expanded=True):
                        # Using markdown with code block for structure but keeping it readable
                        reasoning_text = analysis.get("reason", "No detailed reasoning available.")
                        st.markdown(f"```text\n{reasoning_text}\n```")
                else:
                    st.success("Transaction successful. No agent intervention needed.")

        # Execution Path
        st.markdown("#### Execution Path")
        history = selected_tx.get("history", [])
        for step in history:
            icon = "[OK]" if step.get("result") == "success" else "[ERR]" if "error" in step else "[INFO]"
            text = f"**{step['step']}**"
            if "gateway" in step:
                text += f" -> {step['gateway']}"
            if "error" in step:
                text += f" (Error: {step['error']})"
            st.markdown(f"{icon} {text}")
    else:
        st.info("Select a transaction to see agent details.")


# --- TAB 2: Agent Brain ---
with tab2:
    st.subheader("Thompson Sampling State (The Router)")
    
    system_status = fetch_system_status()
    
    if system_status:
        c_brain_1, c_brain_2 = st.columns([2, 1])
        
        with c_brain_1:
            # Plot Beta Distributions
            x = np.linspace(0, 1, 500)
            fig = go.Figure()
            
            router_state = system_status.get("router", {})
            for gateway, params in router_state.items():
                a, b_val = params["alpha"], params["beta"]
                y = beta.pdf(x, a, b_val)
                
                # Dynamic color based on mean
                mean = a / (a + b_val)
                color = "green" if mean > 0.8 else "orange" if mean > 0.5 else "red"
                
                fig.add_trace(go.Scatter(
                    x=x, y=y, mode='lines', name=f"{gateway} (μ={mean:.2f})",
                    fill='tozeroy'
                ))
            
            fig.update_layout(
                title="Gateway Success Probability Distributions",
                xaxis_title="Probability of Success",
                yaxis_title="Density",
                template="plotly_dark",
                margin=dict(l=20, r=20, t=40, b=20),
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)

        with c_brain_2:
            st.markdown("### Circuit Breakers")
            sentinel_state = system_status.get("sentinel", {})
            
            for gw, state in sentinel_state.items():
                status = state.get("status", "CLOSED")
                color = "#00ff00" if status == "CLOSED" else "#ffa500" if status == "HALF_OPEN" else "#ff0000"
                
                with st.container(border=True):
                    st.markdown(f"**{gw}**")
                    st.markdown(f"<span style='color:{color}; font-weight:bold'>● {status}</span>", unsafe_allow_html=True)
                    window = state.get("window", [])
                    st.text(f"Window: {window}")

    else:
        st.error("Cannot connect to Agent System API.")

# --- TAB 3: Analytics ---
with tab3:
    if not df.empty:
        st.subheader("Routing Distribution")
        counts = df["route_decision"].value_counts().reset_index()
        fig_pie = px.pie(counts, values="count", names="route_decision", hole=0.4, template="plotly_dark")
        st.plotly_chart(fig_pie, use_container_width=True)
        
        st.subheader("Latency Distribution")
        fig_hist = px.histogram(df, x="latency", nbins=20, color="route_decision", template="plotly_dark")
        st.plotly_chart(fig_hist, use_container_width=True)
    else:
        st.info("No data yet.")

# --- Background Runner ---
if st.session_state.simulation_running:
    run_simulation_step(sim_speed)

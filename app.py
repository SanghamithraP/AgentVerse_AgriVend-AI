import streamlit as st
import asyncio
import os
import random
from dotenv import load_dotenv
from groq import AsyncGroq

# Pull structural math and database dependencies from your api_connectors script
from api_connectors import resolve_optimized_mandi_math, COIMBATORE_MARKETS, CROP_MARKET_ROUTING

# Load environment variables
load_dotenv()

# Initialize Groq Async Client inside Streamlit Session State
if "groq_client" not in st.session_state:
    st.session_state.groq_client = AsyncGroq(api_key=os.getenv("GROQ_API_KEY"))

UPGRADED_MODEL = "qwen/qwen3.6-27b"

# --- ASYNC AGENT LOGIC ---
async def run_agents_concurrently(commodity_name, local_block, total_kg, metrics):
    """Fires both the Price Predictor and Logistics Calculator agents at the same time."""
    client = st.session_state.groq_client
    
    # Mandi Price Predictor Agent - Hides all internal processing or progress notes
    mandi_system = (
        "You are an expert Indian APMC Price Analyst. Do not show your thinking process, "
        "step-by-step decisions, or any introductory sentences. Output exactly three lines. "
        "Line 1: State the optimal mandi location and its target trading price per quintal. "
        "Line 2: State the final calculated gross revenue for the harvest volume. "
        "Line 3: Provide a single short sentence regarding local market price sustainability."
    )
    mandi_user = (
        f"Crop Type: {commodity_name} | Volume: {total_kg} kg | Sourced from: {local_block} block.\n"
        f"Optimal Regional Market Identified: {metrics['target_mandi_name']} ({metrics['target_mandi_location']})\n"
        f"Target Trading Index: ₹{metrics['mandi_rate_per_qtl']}/Quintal.\n"
        f"Evaluated Gross Harvest Revenue: ₹{metrics['gross_revenue_inr']} before transport subtractions."
    )
    
    # Logistics Fleet Controller Agent - Hides all internal processing or progress notes
    logistics_system = (
        "You are an AI Agricultural Logistics Controller. Do not show your thinking process, "
        "step-by-step decisions, or any introductory sentences. Output exactly three lines. "
        "Line 1: State the assigned truck type and true travel distance. "
        "Line 2: State the estimated trip duration and freight cost calculation. "
        "Line 3: Provide a single brief traffic routing tip."
    )
    logistics_user = (
        f"Route Mapping: From {local_block.capitalize()} to {metrics['target_mandi_name']}.\n"
        f"Payload Weight: {total_kg} kg.\n"
        f"True Distance Network metrics: {metrics['distance_km']} km (Estimated ETA: {metrics['duration_str']}).\n"
        f"Deployment asset assigned: {metrics['allocated_vehicle']} | Fixed Freight Overhead Invoice cost: ₹{metrics['freight_cost_inr']}."
    )

    # Trigger both Groq tasks simultaneously over non-blocking network streams
    task1 = client.chat.completions.create(
        model=UPGRADED_MODEL, 
        messages=[{"role": "system", "content": mandi_system}, {"role": "user", "content": mandi_user}], 
        temperature=0.1
    )
    task2 = client.chat.completions.create(
        model=UPGRADED_MODEL, 
        messages=[{"role": "system", "content": logistics_system}, {"role": "user", "content": logistics_user}], 
        temperature=0.1
    )
    
    res1, res2 = await asyncio.gather(task1, task2)
    
    # CRITICAL FIX: Added [0] index to prevent 'list object has no attribute message' crash
    return res1.choices[0].message.content, res2.choices[0].message.content


# --- STREAMLIT UI DESIGN ---
st.set_page_config(page_title="Coimbatore Agribusiness Multi-Agent Core", page_icon="🌴", layout="wide")

# Dashboard Headers
st.title("🌴 Coimbatore Agribusiness Multi-Agent System Core")
st.markdown("Automated localized mandi price arbitration and logistics routing powered by **Groq AI (Qwen 3.6 27B)**.")

st.divider() 

# Split layout: 1/3 Left panel for inputs, 2/3 Right panel for results dashboard
col1, col2 = st.columns([1, 2], gap="large")

with col1:
    st.header("📋 Farmer Inputs")
    
    block_options = [b.capitalize() for b in COIMBATORE_MARKETS.keys()]
    local_block = st.selectbox("Select Your Local Block Location:", options=sorted(block_options))
    
    crop_options = [c.title() for c in CROP_MARKET_ROUTING.keys()]
    commodity_name = st.selectbox("Select Crop Type:", options=sorted(list(set(crop_options))))
    
    total_kg = st.number_input("Enter Total Harvest Quantity (in kg):", min_value=1.0, value=500.0, step=50.0)
    
    st.markdown("---")
    submit_btn = st.button("🚀 Invoke Multi-Agent Core", use_container_width=True)

with col2:
    st.header("📊 Multi-Agent Insight Dashboard")
    
    if submit_btn:
        metrics = resolve_optimized_mandi_math(local_block, commodity_name, total_kg)
        
        # Render high-utility visual metric summary dashboard cards
        metric_col1, metric_col2, metric_col3 = st.columns(3)
        with metric_col1:
            st.metric(label="🎯 Best Target Mandi", value=metrics['target_mandi_location'])
        with metric_col2:
            st.metric(label="📐 Route Distance", value=f"{metrics['distance_km']} km", delta=metrics['duration_str'], delta_color="inverse")
        with metric_col3:
            st.metric(label="💰 Net Realized Profit", value=f"₹{metrics['net_profit_inr']:,}", delta=f"-₹{metrics['freight_cost_inr']:,} Freight", delta_color="off")
            
        st.markdown(f"**Selected Transit Asset Class:** `{metrics['allocated_vehicle']}`")
        st.markdown("---")
        
        # ADDED FEATURE: Simple, High-Utility Backend Calculation Breakdown Explainer
        with st.expander("⚙️ View Backend Computation Breakdown", expanded=True):
            st.markdown(f"""
            *   **Distance calculation:** Calculated using the geographic **Haversine formula** between coordinates, adding a `1.25x` road path correction factor.
            *   **Gross Revenue:** `{total_kg} kg` converted to `{total_kg/100:.2f} Quintals` × Mandi Rate `₹{metrics['mandi_rate_per_qtl']}/Qtl` = **`₹{metrics['gross_revenue_inr']:,}`**.
            *   **Freight Cost Formula:** Distance `{metrics['distance_km']} km` × Vehicle Per-KM Commercial Tariff Rate = **`₹{metrics['freight_cost_inr']:,}`**.
            *   **Net Profit Formula:** Gross Revenue `₹{metrics['gross_revenue_inr']:,}` − Freight Cost `₹{metrics['freight_cost_inr']:,}` = **`₹{metrics['net_profit_inr']:,}`**.
            """)
        
        with st.spinner("🤖 Multi-Agent neural layers thinking concurrently..."):
            try:
                mandi_brief, logistics_brief = asyncio.run(
                    run_agents_concurrently(commodity_name, local_block, total_kg, metrics)
                )
                
                # Render Agent 1 Output Display Window
                with st.container(border=True):
                    st.subheader("📊 AGENT 1: Mandi Price Predictor Brief")
                    st.markdown(mandi_brief)
                    
                st.markdown("<br>", unsafe_allow_html=True)
                
                # Render Agent 2 Output Display Window
                with st.container(border=True):
                    st.subheader("🚛 AGENT 2: Logistics Controller Brief")
                    st.markdown(logistics_brief)
                    
                st.success("✅ Execution workflow completed. Summary optimized.")
                
            except Exception as e:
                st.error(f"❌ Core Execution Error: {str(e)}")
                st.info("Ensure your GROQ_API_KEY is properly saved inside your local hidden `.env` file configuration.")
    else:
        st.info("Please adjust input parameters on the left and click 'Invoke Multi-Agent Core' to stream neural agribusiness recommendations.")

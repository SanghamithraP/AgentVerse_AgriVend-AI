import asyncio
import os
from dotenv import load_dotenv
from groq import AsyncGroq

from api_connectors import resolve_optimized_mandi_math

load_dotenv()
client = AsyncGroq(api_key=os.getenv("GROQ_API_KEY"))
UPGRADED_MODEL = "qwen/qwen3.6-27b"

# --- AGENT 1: Mandi Price Predictor Agent ---
async def agent_mandi_predictor(commodity: str, local_block: str, total_kg: float, metrics: dict):
    system_prompt = (
        "You are an expert Indian APMC Price Analyst specializing in Western Tamil Nadu markets. "
        "Formulate a concise 2-sentence market prediction overview confirming the target mandi rate per quintal, "
        "gross revenue, and immediate pricing sustainability factors."
    )
    user_prompt = (
        f"Crop Type: {commodity} | Volume: {total_kg} kg | Sourced from: {local_block} block.\n"
        f"Optimal Regional Market Identified: {metrics['target_mandi_name']} ({metrics['target_mandi_location']})\n"
        f"Target Trading Index: ₹{metrics['mandi_rate_per_qtl']}/Quintal.\n"
        f"Evaluated Gross Harvest Revenue: ₹{metrics['gross_revenue_inr']} before transport subtractions."
    )
    response = await client.chat.completions.create(
        model=UPGRADED_MODEL, messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}], temperature=0.2
    )
    return response.choices[0].message.content

# --- AGENT 2: Logistics Calculator Agent ---
async def agent_logistics_calculator(local_block: str, total_kg: float, metrics: dict):
    system_prompt = (
        "You are an AI Agricultural Logistics Fleet Controller. Output a strict 2-sentence supply chain routing summary "
        "detailing vehicle choice, trip duration windows, freight overheads, and local transit viability."
    )
    user_prompt = (
        f"Route Mapping: From {local_block.capitalize()} to {metrics['target_mandi_name']}.\n"
        f"Payload Weight: {total_kg} kg.\n"
        f"True Distance Network metrics: {metrics['distance_km']} km (Estimated ETA: {metrics['duration_str']}).\n"
        f"Deployment asset assigned: {metrics['allocated_vehicle']} | Fixed Freight Overhead Invoice cost: ₹{metrics['freight_cost_inr']}."
    )
    response = await client.chat.completions.create(
        model=UPGRADED_MODEL, messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}], temperature=0.2
    )
    return response.choices[0].message.content

# --- CENTRAL SYSTEM COORDINATOR ---
async def main():
    print("=" * 60)
    print(" 🌴 COIMBATORE REGION MULTI-AGENT LOCAL SYSTEM CORE 🌴 ")
    print("=" * 60)
    print("Valid Blocks: Coimbatore (Central), Pollachi, Anaimalai, Annur, Karamadai,")
    print("              Kinathukkadavu, Malayadipalayam, Negamam, Sulur, Thondamuthur\n")
    
    local_block = input("1. Enter Your Coimbatore Local Block Location: ").strip()
    commodity_name = input("2. Enter Crop Type (e.g., Small Onion, Sugarcane Jaggery): ").strip()
    
    try:
        total_kg = float(input("3. Enter Total Quantity of Harvested Crop type (in kg): ").strip())
        if total_kg <= 0: 
            total_kg = 100.0
    except ValueError:
        print("⚠️ Formatting layout error. Defaulting payload calculation to 500 kg baseline.")
        total_kg = 500.0

    # Calculate optimal market matrix parameters
    metrics = resolve_optimized_mandi_math(local_block, commodity_name, total_kg)
    
    print(f"\n⚙️ [Arbitration Engine] Processing complete. Total calculated cargo load: {total_kg} kg.")
    print("🚀 Spawning asynchronous Groq processing pipelines...")
    
    task_mandi = asyncio.create_task(agent_mandi_predictor(commodity_name, local_block, total_kg, metrics))
    task_logistics = asyncio.create_task(agent_logistics_calculator(local_block, total_kg, metrics))
    
    mandi_brief, logistics_brief = await asyncio.gather(task_mandi, task_logistics)
    
    print("\n" + "=" * 60)
    print("       🌾 COIMBATORE INTERNAL AGRIBUSINESS INSIGHT SHIELD       ")
    print("=" * 60)
    print(f"📍 Local Crop Origin       : {local_block.capitalize()}, Coimbatore, TN")
    print(f"🎯 Target Optimized Mandi   : {metrics['target_mandi_name']}")
    print(f"📐 True Routing Distance    : {metrics['distance_km']} km (ETA: {metrics['duration_str']})")
    print(f"🚚 Allocated Truck Asset    : {metrics['allocated_vehicle']}")
    print(f"💰 Net Realized Profit      : ₹{metrics['net_profit_inr']} (Net of ₹{metrics['freight_cost_inr']} transport cost)")
    print("-" * 60)
    print(f"📊 AGENT 1: APMC PRICE MONITOR BRIEF:\n{mandi_brief.strip()}")
    print("-" * 60)
    print(f"🚛 AGENT 2: LOGISTICS CONTROLLER BRIEF:\n{logistics_brief.strip()}")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())

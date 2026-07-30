import math
import random

# Real rule-based pricing and spatial database for the Coimbatore region
COIMBATORE_MARKETS = {
    "coimbatore (central)": {"name": "M.G.R. Central Wholesale Mandi", "base_price": 2800, "lat": 10.998, "lon": 76.961},
    "pollachi": {"name": "Pollachi Central Coconut Market Yard", "base_price": 3100, "lat": 10.659, "lon": 77.008},
    "anaimalai": {"name": "Anaimalai Regulated Market Committee", "base_price": 3050, "lat": 10.583, "lon": 76.929},
    "annur": {"name": "Annur Weekly Shandy APMC Yard", "base_price": 2600, "lat": 11.233, "lon": 77.100},
    "karamadai": {"name": "Karamadai Local Agro Assembly Yard", "base_price": 2750, "lat": 11.242, "lon": 76.958},
    "kinathukkadavu": {"name": "Kinathukkadavu Tomato Auction Mandi", "base_price": 2950, "lat": 10.817, "lon": 77.018},
    "malayadipalayam": {"name": "Malayadipalayam Local Sub-Market", "base_price": 2850, "lat": 10.840, "lon": 77.120},
    "negamam": {"name": "Negamam Copra Drying & Trading Hub", "base_price": 3000, "lat": 10.741, "lon": 77.108},
    "sulur": {"name": "Sulur Agro Logistics Terminus", "base_price": 2700, "lat": 11.027, "lon": 77.123},
    "thondamuthur": {"name": "Thondamuthur Vegetables Collection Centre", "base_price": 2900, "lat": 10.993, "lon": 76.828}
}

# 24 Crops categorized with explicit premium regional mandi nodes
CROP_MARKET_ROUTING = {
    # Horticultural Crops & Fruits
    "coconut": "pollachi", "banana": "coimbatore (central)", "mango": "karamadai", "grapes": "thondamuthur", "arecanut": "anaimalai",
    # Vegetables & Spices
    "tomato": "kinathukkadavu", "small onion": "sulur", "shallots": "sulur", "curry leaves": "karamadai", "brinjal": "thondamuthur", 
    "bhendi": "annur", "gourds": "thondamuthur", "chillies": "annur", "turmeric": "malayadipalayam",
    # Cereals, Millets & Pulses
    "paddy": "coimbatore (central)", "ragi": "annur", "cholam": "sulur", "sorghum": "sulur", "maize": "sulur", "cumbu": "annur", "pearl millet": "annur",
    # Oilseeds & Commercial Crops
    "groundnut": "malayadipalayam", "gingelly": "malayadipalayam", "sunflower": "sulur", "castor": "annur", "cotton": "coimbatore (central)", 
    "tobacco": "negamam", "sugarcane jaggery": "anaimalai"
}

def calculate_haversine_distance(lat1, lon1, lat2, lon2):
    """Computes realistic road paths from geographic displacements."""
    R = 6371.0 
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return round((R * c) * 1.25, 1)

def resolve_optimized_mandi_math(origin_block: str, crop_name: str, total_kg: float) -> dict:
    """Calculates distances and selects the most profitable mandi using kg weight inputs."""
    origin = origin_block.lower().strip()
    crop = crop_name.lower().strip()
    
    if origin not in COIMBATORE_MARKETS:
        origin = "coimbatore (central)"
        
    origin_meta = COIMBATORE_MARKETS[origin]
    premium_mandi_id = CROP_MARKET_ROUTING.get(crop, "coimbatore (central)")
    
    # 1 Quintal = 100 kg. Calculate total quintals for market pricing context.
    total_quintals = total_kg / 100.0
    total_tonnage = total_kg / 1000.0
    
    best_mandi_id = None
    max_net_profit = -float('inf')
    computed_logistics_matrix = {}
    
    for mandi_id, market_meta in COIMBATORE_MARKETS.items():
        distance = calculate_haversine_distance(origin_meta["lat"], origin_meta["lon"], market_meta["lat"], market_meta["lon"])
        if distance < 2.0: 
            distance = 5.0
            
        # Select logistics vehicle class dynamically based on total kg payload
        if total_kg <= 1500:
            vehicle = "Tata Ace (Mini Truck)"
            cost_per_km = 16
        elif total_kg <= 6000:
            vehicle = "6-Wheeler Eicher Truck"
            cost_per_km = 26
        else:
            vehicle = "10-Wheeler Open Commercial Carrier"
            cost_per_km = 38
            
        freight_expense = round(distance * cost_per_km)
        base_rate = market_meta["base_price"]
        
        # Apply 15% price realization premium at the designated category hub
        if mandi_id == premium_mandi_id:
            base_rate = round(base_rate * 1.15)
            
        gross_value = round(base_rate * total_quintals)
        net_profit = gross_value - freight_expense
        
        if net_profit > max_net_profit:
            max_net_profit = net_profit
            best_mandi_id = mandi_id
            computed_logistics_matrix = {
                "target_mandi_name": market_meta["name"],
                "target_mandi_location": mandi_id.capitalize(),
                "distance_km": distance,
                "duration_str": f"{max(1, round((distance / 40) * 60)) // 60}h {max(1, round((distance / 40) * 60)) % 60}m",
                "allocated_vehicle": vehicle,
                "freight_cost_inr": freight_expense,
                "mandi_rate_per_qtl": base_rate,
                "gross_revenue_inr": gross_value,
                "net_profit_inr": net_profit
            }
            
    return computed_logistics_matrix

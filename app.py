import math
import streamlit as st
import pandas as pd
import re

# ==========================================
# PART 1: THE PURDY MATH ENGINE
# ==========================================

PTABLE = [
    40.0, 11.000, 50.0, 10.9960, 60.0, 10.9830, 70.0, 10.9620, 80.0, 10.934, 90.0, 10.9000, 100.0, 10.8600,
    110.0, 10.8150, 120.0, 10.765, 130.0, 10.7110, 140.0, 10.6540, 150.0, 10.5940, 160.0, 10.531, 170.0, 10.4650,
    180.0, 10.3960, 200.0, 10.2500, 220.0, 10.096, 240.0, 9.9350, 260.0, 9.7710, 280.0, 9.6100, 300.0, 9.455,
    320.0, 9.3070, 340.0, 9.1660, 360.0, 9.0320, 380.0, 8.905, 400.0, 8.7850, 450.0, 8.5130, 500.0, 8.2790,
    550.0, 8.083, 600.0, 7.9210, 700.0, 7.6690, 800.0, 7.4960, 900.0, 7.32000, 1000.0, 7.18933, 1200.0, 6.98066,
    1500.0, 6.75319, 2000.0, 6.50015, 2500.0, 6.33424, 3000.0, 6.21913, 3500.0, 6.13510, 4000.0, 6.07040,
    4500.0, 6.01822, 5000.0, 5.97432, 6000.0, 5.90181, 7000.0, 5.84156, 8000.0, 5.78889, 9000.0, 5.74211,
    10000.0, 5.70050, 12000.0, 5.62944, 15000.0, 5.54300, 20000.0, 5.43785, 25000.0, 5.35842, 30000.0, 5.29298,
    35000.0, 5.23538, 40000.0, 5.18263, 50000.0, 5.08615, 60000.0, 4.99762, 80000.0, 4.83617, 100000.0, 4.68988
]

def frac(d):
    if d < 110: return 0
    if d == 42195 or d == 21097.5: return 0 
    laps = math.floor(d / 400)
    meters = d - laps * 400
    partlap = 0
    if meters <= 50: partlap = 0
    elif meters <= 150: partlap = meters - 50
    elif meters <= 250: partlap = 100
    elif meters <= 350: partlap = 100 + (meters - 250)
    elif meters <= 400: partlap = 200
    return (laps * 200 + partlap) / d

def get_base_variables(dist):
    c1, c2, c3 = 0.20, 0.08, 0.0065
    d = 0.1
    i = 0
    while dist > d and i < len(PTABLE) - 2:
        d = PTABLE[i]
        i += 2
    i -= 2
    if i < 2: i = 2
    d3, t3 = PTABLE[i], PTABLE[i] / PTABLE[i + 1]
    d1, t1 = PTABLE[i - 2], PTABLE[i - 2] / PTABLE[i - 1]
    t = t1 + (t3 - t1) * (dist - d1) / (d3 - d1)
    v = dist / t
    t950 = t + c1 + c2 * v + c3 * frac(dist) * v * v
    k = 0.0654 - 0.00258 * v
    a = 85 / k
    b = 1 - 950 / a
    return t950, a, b

def purdy_classic(dist, tsec):
    vars = get_base_variables(dist)
    if not vars: return 0
    t950, a, b = vars
    p = a * (t950 / tsec - b)
    return round(p, 2)

def get_equivalent_time(target_dist, points):
    vars = get_base_variables(target_dist)
    if not vars: return 0
    t950, a, b = vars
    denominator = (points / a) + b
    if denominator <= 0: return 0 
    return t950 / denominator

def format_time(seconds):
    if seconds <= 0: return "0.00"
    seconds = round(seconds, 2)
    hrs = int(seconds // 3600)
    mins = int((seconds % 3600) // 60)
    secs = seconds % 60
    if hrs > 0: return f"{hrs}:{mins:02d}:{secs:05.2f}"
    else: return f"{mins}:{secs:05.2f}"

# ==========================================
# PART 2: THE STREAMLIT WEB INTERFACE
# ==========================================

st.set_page_config(page_title="Purdy Points Calculator", layout="wide")
st.title("🏃 Purdy Points & Race Calculator")

tab1, tab2, tab3, tab4 = st.tabs(["Individual", "Relay (Simple)", "Relay (Conversions)", "Bulk Seeding Pipeline"])

# ------------------------------------------
# TAB 1: INDIVIDUAL CALCULATOR
# ------------------------------------------
with tab1:
    st.subheader("Individual Performance Conversions")
    col1, col2, col3, col4 = st.columns(4)
    raw_dist = col1.number_input("Distance", min_value=0, value=1500, step=10)
    unit = col2.selectbox("Unit", ["Meters", "Miles", "Kilometers"])
    minutes = col3.number_input("Minutes", min_value=0, value=3, step=1)
    seconds = col4.number_input("Seconds", min_value=0.0, max_value=59.99, value=30.0, step=0.1)

    if unit == "Miles": dist = float(raw_dist) * 1609.344
    elif unit == "Kilometers": dist = float(raw_dist) * 1000.0
    else: dist = float(raw_dist)

    total_seconds = (minutes * 60) + seconds

    if total_seconds > 0:
        score = purdy_classic(dist, total_seconds)
        st.metric(label="Purdy Points", value=f"{score:.2f}")

        st.markdown("### Equivalent Times")
        target_distances = [
            ("200m", 200), ("300m", 300), ("400m", 400), ("500m", 500),
            ("600m", 600), ("800m", 800), ("1000m", 1000), ("1200m", 1200),
            ("1500m", 1500), ("1600m", 1600), ("1 Mile", 1609.344), ("3000m", 3000),
            ("3200m", 3200), ("2 Mile", 3218.688), ("5k", 5000)
        ]
        
        c1, c2 = st.columns(2)
        for i in range(0, len(target_distances), 2):
            name1, dist1 = target_distances[i]
            c1.write(f"**{name1}:** {format_time(get_equivalent_time(dist1, score))}")
            if i + 1 < len(target_distances):
                name2, dist2 = target_distances[i+1]
                c2.write(f"**{name2}:** {format_time(get_equivalent_time(dist2, score))}")

# ------------------------------------------
# TAB 2: RELAY CALCULATOR (SIMPLE SUM)
# ------------------------------------------
with tab2:
    st.subheader("Standard Relay Addition")
    total_simple_sec = 0.0
    for i in range(4):
        col1, col2, col3 = st.columns([1, 2, 2])
        col1.write(f"**Leg {i+1}**")
        m = col2.number_input("Minutes", min_value=0, value=0, step=1, key=f"s_m_{i}")
        s = col3.number_input("Seconds", min_value=0.0, max_value=59.99, value=0.0, step=0.1, key=f"s_s_{i}")
        total_simple_sec += (m * 60) + s
    st.markdown("---")
    st.subheader(f"⏱️ Total Time: {format_time(total_simple_sec)}")

# ------------------------------------------
# TAB 3: RELAY CALCULATOR WITH CONVERSIONS
# ------------------------------------------
relay_choices = ["200m", "300m", "400m", "500m", "600m", "800m", "1000m", "1200m", "1500m", "1600m", "1 Mile"]
relay_dist_map = {"200m": 200, "300m": 300, "400m": 400, "500m": 500, "600m": 600, "800m": 800, "1000m": 1000, "1200m": 1200, "1500m": 1500, "1600m": 1600, "1 Mile": 1609.344}
preset_map = {"Custom (Manual)": None, "4x200m": ["200m", "200m", "200m", "200m"], "4x400m": ["400m", "400m", "400m", "400m"], "4x800m": ["800m", "800m", "800m", "800m"], "4x1 mile": ["1 Mile", "1 Mile", "1 Mile", "1 Mile"], "SMR": ["200m", "200m", "400m", "800m"], "DMR": ["1200m", "400m", "800m", "1600m"]}

def update_preset():
    selection = st.session_state.preset_dropdown
    distances = preset_map.get(selection)
    if distances:
        for i in range(4): st.session_state[f"c_out_{i}"] = distances[i]

for i in range(4):
    if f"c_in_{i}" not in st.session_state: st.session_state[f"c_in_{i}"] = "400m"
    if f"c_out_{i}" not in st.session_state: st.session_state[f"c_out_{i}"] = "400m"

with tab3:
    st.subheader("Relay Calculator with Purdy Conversions")
    st.selectbox("Event Preset:", list(preset_map.keys()), key="preset_dropdown", on_change=update_preset)
    total_conv_sec = 0.0
    for i in range(4):
        c1, c2, c3, c4, c5 = st.columns([1, 1.5, 2, 2, 2])
        c1.write(f"**Leg {i+1}**")
        m = c2.number_input("Min", min_value=0, value=0, step=1, key=f"c_m_{i}")
        s = c3.number_input("Sec", min_value=0.0, max_value=59.99, value=0.0, step=0.1, key=f"c_s_{i}")
        in_choice = c4.selectbox("Input Event", relay_choices, key=f"c_in_{i}")
        out_choice = c5.selectbox("Convert To", relay_choices, key=f"c_out_{i}")
        leg_total_sec = (m * 60) + s
        if leg_total_sec > 0:
            pts = purdy_classic(relay_dist_map[in_choice], leg_total_sec)
            conv_sec = get_equivalent_time(relay_dist_map[out_choice], pts)
            rounded_sec = round(conv_sec, 2)
            total_conv_sec += rounded_sec
            c5.caption(f"**Converted: {format_time(rounded_sec)}**")
        else:
            c5.caption(f"**Converted: 0.00**")
    st.markdown("---")
    st.subheader(f"🚀 Relay Composite Time: {format_time(total_conv_sec)}")

# ------------------------------------------
# TAB 4: THE BULK SEEDING PIPELINE (CSV UPLOAD)
# ------------------------------------------
with tab4:
    st.subheader("Bulk Seeding Pipeline (CSV Standardizer)")
    st.markdown("""
    **Instructions:**
    1. Select the target championship event you are seeding.
    2. Upload the official CSV export from Athletic.net.
    3. Click **Generate Conversions** to calculate the alternate scenarios!
    """)
    
    target_event = st.radio("Target Seeding Event:", ["1 Mile", "2 Mile"], index=0, horizontal=True)
    
    uploaded_file = st.file_uploader("Upload Athletic.net Entries CSV", type=["csv"])
    
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        
        st.write("Preview of uploaded data:")
        st.dataframe(df.head(3), use_container_width=True)
        
        if st.button("Generate Conversions", type="primary"):
            results = []
            for index, row in df.iterrows():
                
                raw_final = str(row.get('Final Seed', ''))
                raw_auto = str(row.get('Auto Time', ''))
                
                times_final = re.findall(r'\d+:\d{2}(?:\.\d+)?', raw_final)
                times_auto = re.findall(r'\d+:\d{2}(?:\.\d+)?', raw_auto)
                
                if not times_final: 
                    continue
                
                final_time = times_final[-1]
                
                # Check if Final Seed matches the Auto Time perfectly
                is_auto_match = False
                if times_auto and times_final[-1] == times_auto[-1]:
                    is_auto_match = True
                
                parts = final_time.split(':')
                total_sec = (int(parts[0]) * 60) + float(parts[1])
                
                u_comment = str(row.get('User Comment', ''))
                h_comment = str(row.get('Host Comment', ''))
                combined_notes = f"{u_comment} {h_comment}".replace("nan", "").strip()
                
                athlete_name = str(row.get("Athlete Name", ""))
                affiliation = str(row.get("Affiliation", ""))
                
                if target_event == "1 Mile":
                    if is_auto_match:
                        val_1500 = "-"
                        val_1600 = "-"
                    else:
                        pts_1500 = purdy_classic(1500.0, total_sec)
                        val_1500 = format_time(get_equivalent_time(1609.344, pts_1500))
                        
                        pts_1600 = purdy_classic(1600.0, total_sec)
                        val_1600 = format_time(get_equivalent_time(1609.344, pts_1600))
                        
                    results.append({
                        "Name": athlete_name,
                        "Team": affiliation,
                        "Input Time": final_time,
                        "Original Notes": combined_notes,
                        "1 Mile (if 1500m)": val_1500,
                        "1 Mile (if 1600m)": val_1600,
                        "1 Mile (if 1 Mile)": final_time
                    })
                    
                elif target_event == "2 Mile":
                    if is_auto_match:
                        val_3000 = "-"
                        val_3200 = "-"
                    else:
                        pts_3000 = purdy_classic(3000.0, total_sec)
                        val_3000 = format_time(get_equivalent_time(3218.688, pts_3000))
                        
                        pts_3200 = purdy_classic(3200.0, total_sec)
                        val_3200 = format_time(get_equivalent_time(3218.688, pts_3200))
                        
                    results.append({
                        "Name": athlete_name,
                        "Team": affiliation,
                        "Input Time": final_time,
                        "Original Notes": combined_notes,
                        "2 Mile (if 3000m)": val_3000,
                        "2 Mile (if 3200m)": val_3200,
                        "2 Mile (if 2 Mile)": final_time
                    })
            
            if results:
                res_df = pd.DataFrame(results)
                st.success("Conversions complete!")
                st.dataframe(res_df, use_container_width=True)
                
                file_label = target_event.replace(" ", "_").lower()
                csv_data = res_df.to_csv(index=False).encode('utf-8')
                
                st.download_button(label="Download Results as CSV", data=csv_data, file_name=f"bulk_seeds_{file_label}.csv", mime="text/csv")
            else:
                st.error("No valid times found to convert. Check your data format.")

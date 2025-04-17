
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from fpdf import FPDF
from io import BytesIO

st.set_page_config(page_title="雙螺桿擠壓模擬器 v3.5（簡化解釋版）", layout="centered")
st.title("🛠️ 雙螺桿擠壓模擬器 v3.5（簡化解釋版）")

def get_flavor_profiles():
    return {
        "玉米粉": {"expansion": 2.0, "crisp": 6.0, "flavor": "甜香"},
        "小麥粉": {"expansion": 1.8, "crisp": 5.5, "flavor": "穀香"},
        "裸麥粉": {"expansion": 1.5, "crisp": 5.0, "flavor": "堅果風"},
        "高蛋白粉": {"expansion": 1.2, "crisp": 3.5, "flavor": "麥皮香"},
        "馬鈴薯澱粉": {"expansion": 2.2, "crisp": 4.5, "flavor": "黏稠"},
        "全麥粉": {"expansion": 1.3, "crisp": 4.2, "flavor": "纖維感"}
    }

material_options = list(get_flavor_profiles().keys())

st.sidebar.header("參數設定")
temp = st.sidebar.slider("筒溫 (°C)", 60, 180, 140)
rpm = st.sidebar.slider("轉速 (rpm)", 100, 600, 300)
moisture = st.sidebar.slider("水含量 (%)", 10, 25, 15)
fat = st.sidebar.slider("油脂含量 (%)", 0, 15, 5)
screw_diameter = st.sidebar.slider("螺桿直徑 (mm)", 20, 60, 30)
screw_length = st.sidebar.slider("螺桿長度 (mm)", 500, 1500, 1000)
feed_rate = st.sidebar.slider("喂料速率 (kg/h)", 10, 100, 30)
die_diameter = st.sidebar.slider("模口孔徑 (mm)", 2, 10, 5)

st.subheader("🔢 混合原料設定（總和需為100%）")
blend_dict = {}
total_ratio = 0
for mat in material_options:
    ratio = st.number_input(f"{mat} 比例 (%)", min_value=0, max_value=100, value=0, step=5)
    if ratio > 0:
        blend_dict[mat] = ratio
        total_ratio += ratio

def simulate(temp, rpm, moisture, fat, screw_diameter, screw_length, feed_rate, die_diameter, blend_dict):
    flavor_profiles = get_flavor_profiles()
    total = sum(blend_dict.values())
    expansion, crispness, stickiness = 0, 0, 0
    flavor_counts = {}
    for mat, ratio in blend_dict.items():
        weight = ratio / total
        profile = flavor_profiles[mat]
        expansion += profile["expansion"] * weight
        crispness += profile["crisp"] * weight
        stickiness += (10 - profile["crisp"]) * weight
        flavor_counts[profile["flavor"]] = flavor_counts.get(profile["flavor"], 0) + round(weight * 100)
    aw = round(0.65 + 0.01 * (moisture - 15) - 0.005 * fat, 2)
    density = round(0.2 + 0.005 * (100 - expansion * 50), 2)
    pressure = round(0.1 * rpm * moisture / screw_diameter, 2)
    energy = round((temp * rpm * (1 + fat / 10)) / (100000 + feed_rate * 100), 3)
    return {
        "膨發指數": round(expansion, 2),
        "酥脆度": round(crispness, 2),
        "水活性": aw,
        "黏性": round(stickiness, 2),
        "體積密度": density,
        "桶內壓力 (bar)": pressure,
        "預估能耗 (kWh/kg)": energy
    }, flavor_counts

if total_ratio == 100:
    if st.button("🚀 執行模擬"):
        results, flavors = simulate(temp, rpm, moisture, fat, screw_diameter, screw_length, feed_rate, die_diameter, blend_dict)
        st.subheader("📊 模擬結果")
        for k, v in results.items():
            st.write(f"{k}：{v}")

        with st.expander("🧾 參數解釋"):
            st.markdown("""
- **膨發指數**：擠壓後產品膨大的程度，數值越高表示膨化越明顯。
- **酥脆度**：預估口感的脆感程度，數值越高表示更酥脆。
- **水活性**：代表產品中水分活躍程度，越高代表保存性越低。
- **黏性**：內部結構的黏聚程度，過高可能造成口感軟糯或粘牙。
- **體積密度**：擠壓後單位體積的質量，數值高表示較緊實密集。
- **桶內壓力**：模擬擠壓過程中筒內產生的壓力，過高可能增加機器負荷。
- **預估能耗**：製作每公斤產品所需的電能，越低表示越節能。
""")

        st.subheader("🎨 風味描述")
        st.write("綜合風味組成：", "、".join([f"{k}（{v}%）" for k, v in flavors.items()]))
else:
    st.warning(f"⚠️ 原料總比例需為 100%，目前為 {total_ratio}%。")

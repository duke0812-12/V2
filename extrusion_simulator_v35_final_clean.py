
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from fpdf import FPDF
from io import BytesIO
import os

st.set_page_config(page_title="雙螺桿擠壓模擬器 v3.5（含能耗預測）", layout="centered")
st.title("⚙️ 雙螺桿擠壓模擬器 v3.5（含能耗預測）")

def get_flavor_profiles():
    return {
        "玉米粉": {"expansion": 2.0, "crisp": 6.0, "flavor": "甜香"},
        "小麥粉": {"expansion": 1.8, "crisp": 5.5, "flavor": "穀香"},
        "裸麥粉": {"expansion": 1.5, "crisp": 5.0, "flavor": "堅果風"},
        "高蛋白粉": {"expansion": 1.2, "crisp": 4.0, "flavor": "麩皮香"},
        "馬鈴薯澱粉": {"expansion": 2.2, "crisp": 6.5, "flavor": "鬆化"},
    }

material_options = list(get_flavor_profiles().keys())

st.header("📊 參數設定")
temp = st.slider("筒溫 (°C)", 60, 180, 140)
rpm = st.slider("轉速 (rpm)", 100, 600, 300)
moisture = st.slider("水含量 (%)", 10, 25, 15)
fat = st.slider("油脂含量 (%)", 0, 15, 5)
screw_diameter = st.slider("螺桿直徑 (mm)", 20, 60, 30)
screw_length = st.slider("螺桿長度 (mm)", 400, 1500, 1000)
feed_rate = st.slider("喂料速率 (kg/h)", 5, 200, 60)
die_diameter = st.slider("模口孔徑 (mm)", 2, 20, 6)
pressure = st.slider("筒內壓力 (bar)", 20, 200, 80)

st.header("🔢 混合原料設定（總和需為100%）")
blend_dict = {}
total_ratio = 0
for mat in material_options:
    ratio = st.number_input(f"{mat} 比例 (%)", min_value=0, max_value=100, value=0, step=5)
    if ratio > 0:
        blend_dict[mat] = ratio
        total_ratio += ratio

def simulate_blended_formula(temp, rpm, moisture, fat, feed_rate, die_diameter, screw_diameter, screw_length, pressure, blend_dict):
    flavor_profiles = get_flavor_profiles()
    total_ratio = sum(blend_dict.values())
    expansion = 0
    crisp = 0
    flavors = []

    for mat, ratio in blend_dict.items():
        weight = ratio / total_ratio
        expansion += flavor_profiles[mat]["expansion"] * weight
        crisp += flavor_profiles[mat]["crisp"] * weight
        flavors.append(flavor_profiles[mat]["flavor"])

    water_activity = round(moisture / 22, 2)
    density = round(1.4 - 0.3 * (expansion - 1.0), 2)
    stickiness = round(3.0 + fat * 0.1 - moisture * 0.05, 2)
    energy = round((0.0008 * temp + 0.0006 * rpm + 0.0012 * feed_rate + 0.0004 * pressure) / 10, 3)
    flavor_desc = pd.Series(flavors).value_counts(normalize=True).apply(lambda x: f"{int(x*100)}%").to_dict()
    appearance = "偏膨鬆" if expansion > 1.8 else "偏密實"
    color = "金黃色" if temp >= 130 else "淡黃色"

    return {
        "膨發指數": round(expansion, 2),
        "酥脆度": round(crisp, 2),
        "水活性": water_activity,
        "黏性": stickiness,
        "外觀": appearance,
        "色澤": color,
        "感官風味": flavor_desc,
        "體積密度": density,
        "預估能耗 (kWh/kg)": energy,
    }

if st.button("🚀 執行模擬"):
    if total_ratio != 100:
        st.warning("⚠️ 原料總比例需為 100%，目前為 {}%".format(total_ratio))
    else:
        result = simulate_blended_formula(temp, rpm, moisture, fat, feed_rate, die_diameter, screw_diameter, screw_length, pressure, blend_dict)
        st.subheader("📊 模擬結果")
        for k, v in result.items():
            if isinstance(v, dict):
                st.markdown(f"**{k}：** " + "、".join([f"{flv}（{ratio}）" for flv, ratio in v.items()]))
            else:
                st.markdown(f"**{k}：** {v}")

        with st.expander("📝 模擬指標說明"):
            st.markdown("""
- **膨發指數**: 產品體積與原料體積之比，反映膨化程度。
- **酥脆度**: 根據原料特性預估的口感酥脆指數（越高越酥脆）。
- **黏性**: 原料黏附程度，數值越高代表越黏手或濕軟。
- **體積密度**: 每立方公分產品的重量，反映結構緊實程度。
- **感官風味強度**: 依配方比例推算的綜合風味比例。
""")

        st.subheader("📈 數值圖表")
        df = pd.DataFrame({
            "膨發指數": [result["膨發指數"]],
            "酥脆度": [result["酥脆度"]],
            "水活性": [result["水活性"]],
            "黏性": [result["黏性"]],
            "體積密度": [result["體積密度"]],
            "預估能耗 (kWh/kg)": [result["預估能耗 (kWh/kg)"]],
        })
        st.bar_chart(df.T)

        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", "B", 16)
        pdf.cell(200, 10, "雙螺桿擠壓模擬報告 v3.5", ln=True, align="C")
        pdf.set_font("Arial", "", 12)
        pdf.ln(5)
        pdf.multi_cell(0, 8, f"操作參數:\n筒溫: {temp} C，轉速: {rpm} rpm，水含量: {moisture}% ，油脂: {fat}%\n喂料速率: {feed_rate} kg/h，模口孔徑: {die_diameter} mm，螺桿直徑: {screw_diameter} mm，螺桿長度: {screw_length} mm，筒內壓力: {pressure} bar")
        pdf.ln(5)
        pdf.multi_cell(0, 8, "原料組合: " + ", ".join([f"{k} {v}%" for k, v in blend_dict.items()]))
        pdf.ln(5)
        for k, v in result.items():
            if isinstance(v, dict):
                desc = "、".join([f"{fk}（{fv}）" for fk, fv in v.items()])
                pdf.cell(0, 10, f"{k}: {desc}", ln=True)
            else:
                pdf.cell(0, 10, f"{k}: {v}", ln=True)

        pdf_buffer = BytesIO()
        pdf.output(pdf_buffer)
        st.download_button("📥 下載報告", data=pdf_buffer.getvalue(), file_name="extrusion_report_v35.pdf")

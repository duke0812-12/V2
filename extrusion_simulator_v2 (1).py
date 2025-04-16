
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from fpdf import FPDF
from io import BytesIO
import os

st.set_page_config(page_title="雙螺桿擠壓模擬器", layout="centered")

st.title("🌽 雙螺桿擠壓機參數模擬器 v2")
st.markdown("支援：原料混合｜批次模擬｜風味預測｜匯出報告 📄")

# --------- 原料資料 ---------
def get_flavor_profiles():
    return {
        "玉米粉":     {"expansion": 2.0, "crisp": 6.0, "flavor": "甜香"},
        "小麥粉":     {"expansion": 1.8, "crisp": 5.5, "flavor": "穀香"},
        "裸麥粉":     {"expansion": 1.5, "crisp": 5.0, "flavor": "堅果風"},
        "高蛋白粉":  {"expansion": 1.2, "crisp": 4.0, "flavor": "豆粉味"},
        "馬鈴薯澱粉": {"expansion": 2.2, "crisp": 6.5, "flavor": "脆口澱粉香"},
        "全麥粉":     {"expansion": 1.6, "crisp": 5.2, "flavor": "麩皮香、纖維感"}
    }

material_options = list(get_flavor_profiles().keys())
target_options = ["膨發零食", "酥餅", "夾心餅體"]

# --------- 使用者參數輸入 ---------
st.sidebar.header("參數設定")
temp = st.sidebar.slider("筒溫（℃）", 60, 180, 140)
rpm = st.sidebar.slider("轉速（rpm）", 100, 600, 300)
moisture = st.sidebar.slider("水含量（%）", 10, 25, 15)
fat = st.sidebar.slider("油脂含量（%）", 0, 15, 5)
target_product = st.sidebar.selectbox("產品目標", target_options)

# --------- 混合原料比例輸入 ---------
st.subheader("🔢 混合原料設定（總和需為100%）")
blend_dict = {}
total_ratio = 0
for mat in material_options:
    ratio = st.number_input(f"{mat} 比例（%）", min_value=0, max_value=100, value=0, step=5)
    if ratio > 0:
        blend_dict[mat] = ratio
        total_ratio += ratio

# --------- 模擬計算函數 ---------
def simulate_blended_formula(temp, rpm, moisture, fat, blend_dict):
    flavor_profiles = get_flavor_profiles()
    total_ratio = sum(blend_dict.values())
    expansion = 0
    crisp = 0
    flavors = []
    for mat, ratio in blend_dict.items():
        weight = ratio / total_ratio
        if mat in flavor_profiles:
            expansion += flavor_profiles[mat]["expansion"] * weight
            crisp += flavor_profiles[mat]["crisp"] * weight
            flavors.append((flavor_profiles[mat]["flavor"], weight))
    expansion = round(expansion + (temp - 100) * 0.005 - moisture * 0.01 + fat * 0.01, 2)
    crisp = round(crisp + (rpm - 300) * 0.005 - fat * 0.1 + moisture * 0.05, 2)
    water_aw = round(0.6 + moisture * 0.01 - temp * 0.001, 2)
    stickiness = round(1 + fat * 0.1 + moisture * 0.1 - rpm * 0.002, 2)
    appearance = "膨鬆偏亮" if expansion > 2 else "偏密實"
    color = "金黃色" if temp >= 140 else "淺黃"
    flavor_desc = "、".join([f"{f[0]}（{int(f[1]*100)}%）" for f in flavors])
    return {
        "膨發指數": expansion,
        "酥脆度": crisp,
        "水活性": water_aw,
        "黏性": stickiness,
        "外觀": appearance,
        "色澤": color,
        "風味描述": f"綜合風味：{flavor_desc}"
    }

# --------- 模擬與輸出 ---------
if total_ratio == 100:
    if st.button("🚀 執行模擬"):
        results = simulate_blended_formula(temp, rpm, moisture, fat, blend_dict)
        st.subheader("📊 模擬結果")
        for k, v in results.items():
            st.write(f"**{k}**：{v}")

        # 儲存紀錄
        sim_row = {"筒溫": temp, "轉速": rpm, "水": moisture, "油": fat}
        sim_row.update(results)
        pd.DataFrame([sim_row]).to_csv("simulation_history.csv", mode="a", header=not os.path.exists("simulation_history.csv"), index=False)

        # 圖表顯示
        st.subheader("📈 數值圖表")
        fig, ax = plt.subplots()
        keys = ["膨發指數", "酥脆度", "水活性", "黏性"]
        vals = [results[k] for k in keys]
        ax.bar(keys, vals)
        st.pyplot(fig)

        # 匯出 PDF
        if st.button("📄 匯出 PDF 報告"):
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", "B", 16)
            pdf.cell(200, 10, "雙螺桿擠壓模擬報告", ln=True, align="C")
            pdf.set_font("Arial", "", 12)
            pdf.ln(5)
            pdf.multi_cell(0, 8, f"原料組合：{', '.join([f'{k} {v}%' for k,v in blend_dict.items()])}")
            pdf.cell(0, 10, f"產品目標：{target_product}", ln=True)
            pdf.cell(0, 10, f"筒溫：{temp}°C，轉速：{rpm} rpm，水：{moisture}%，油：{fat}%", ln=True)
            pdf.ln(5)
            pdf.set_font("Arial", "B", 13)
            pdf.cell(0, 10, "模擬預測：", ln=True)
            pdf.set_font("Arial", "", 12)
            for k, v in results.items():
                pdf.cell(0, 10, f"{k}：{v}", ln=True)
            pdf.ln(5)
            pdf.set_font("Arial", "I", 11)
            pdf.multi_cell(0, 8, "📘 模擬指標說明：\n\n- 膨發指數：1.0~1.5 緊實，1.6~2.0 輕酥，2.1+ 高膨發\n- 酥脆度：<4 軟，4~5.5 中，>5.5 脆\n- 黏性：<2 好操作，>3 較難成型")
            pdf_buffer = BytesIO()
            pdf.output(pdf_buffer)
            st.download_button("⬇️ 下載報告", data=pdf_buffer.getvalue(), file_name="extrusion_report.pdf")
else:
    st.warning("⚠️ 原料總比例需為 100%，目前為 {}%".format(total_ratio))

# --------- 批次模擬上傳 ---------
st.subheader("📁 批次模擬上傳（CSV）")
csv_file = st.file_uploader("上傳含欄位：原料、筒溫、轉速、水含量、油脂含量", type="csv")
if csv_file:
    df = pd.read_csv(csv_file)
    batch_results = []
    for _, row in df.iterrows():
        blend = {mat: row[mat] for mat in material_options if mat in row and row[mat] > 0}
        res = simulate_blended_formula(row["筒溫"], row["轉速"], row["水含量"], row["油脂含量"], blend)
        res.update(blend)
        batch_results.append(res)
    df_out = pd.DataFrame(batch_results)
    st.dataframe(df_out)
    st.download_button("⬇️ 下載模擬結果 CSV", data=df_out.to_csv(index=False), file_name="batch_simulation_results.csv")

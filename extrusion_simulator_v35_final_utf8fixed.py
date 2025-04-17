
import streamlit as st

# 範例：修正 PDF 輸出中的特殊字元問題
temp, rpm, moisture, fat = 140, 300, 15, 5

st.title("雙螺桿擠壓模擬器 v3.5（修正完成）")
st.write(f"操作參數：\n筒溫：{temp}°C, 轉速：{rpm} rpm, 水含量：{moisture}%, 油脂：{fat}%")

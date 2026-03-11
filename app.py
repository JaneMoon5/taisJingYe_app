import streamlit as st
import pandas as pd
from PIL import Image
import os

# 页面标题
st.set_page_config(page_title="精华消息检索", layout="wide")
st.title("📚 精华消息检索系统")

# 加载数据（使用缓存，避免重复读取）
@st.cache_data
def load_data():
    df = pd.read_csv('taisJingYe.csv', encoding='utf-8-sig')
    # 如果日期列需要处理，可以转换
    return df

df = load_data()

# 侧边栏：搜索条件
st.sidebar.header("🔍 搜索条件")

# 关键词搜索（在多个文本列中搜索）
search_term = st.sidebar.text_input("关键词（搜索头衔、名字、内容等）")

# 按设精人筛选
setjingren_list = ['全部'] + sorted(df['设精人'].unique().tolist())
selected_setjingren = st.sidebar.selectbox("设精人", setjingren_list)

# 按格式筛选
format_list = ['全部'] + sorted(df['格式'].unique().tolist())
selected_format = st.sidebar.selectbox("格式", format_list)

# 按日期范围筛选
st.sidebar.subheader("日期范围")
df['日期'] = pd.to_datetime(df['日期'])
min_date = df['日期'].min().date()
max_date = df['日期'].max().date()
start_date = st.sidebar.date_input("开始日期", min_date)
end_date = st.sidebar.date_input("结束日期", max_date)

# 应用筛选
filtered_df = df.copy()

if search_term:
    # 在多个文本列中搜索（如果列名不同，请修改）
    text_cols = ['头衔', '名字', '内容', '设精人']
    mask = filtered_df[text_cols].apply(
        lambda row: row.astype(str).str.contains(search_term, case=False, na=False).any(), axis=1
    )
    filtered_df = filtered_df[mask]

if selected_setjingren != '全部':
    filtered_df = filtered_df[filtered_df['设精人'] == selected_setjingren]

if selected_format != '全部':
    filtered_df = filtered_df[filtered_df['格式'] == selected_format]

# 日期筛选
filtered_df = filtered_df[
    (filtered_df['日期'].dt.date >= start_date) & 
    (filtered_df['日期'].dt.date <= end_date)
]

# 显示统计信息
st.write(f"共找到 **{len(filtered_df)}** 条记录")

# 显示数据表格
st.dataframe(filtered_df, use_container_width=True)

# 如果包含图片路径，可以显示图片预览（可选）
if '内容' in filtered_df.columns and filtered_df['格式'].str.contains('图片').any():
    st.subheader("🖼️ 图片预览")
    # 只显示格式为图片的行
    img_df = filtered_df[filtered_df['格式'] == '图片']
    for idx, row in img_df.iterrows():
        img_path = row['内容']  # 假设图片路径存在'内容'列
        if os.path.exists(img_path):
            st.write(f"**{row['名字']}**")
            st.image(img_path, width=300)
        else:
            st.write(f"❌ 图片不存在：{img_path}")
            
            
            
            
# 在终端中，进入 app.py 所在目录，执行：
#                                   streamlit run app.py
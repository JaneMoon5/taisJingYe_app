import streamlit as st
import pandas as pd
import os

# 页面设置
st.set_page_config(page_title="精华消息检索", layout="wide")
st.title("📚 精华消息检索系统")

# 加载数据（缓存）
@st.cache_data
def load_data():
    df = pd.read_csv('taisJingYe.csv', encoding='utf-8-sig')
    df['日期'] = pd.to_datetime(df['日期'])
    return df

df = load_data()

# ---------- 侧边栏筛选 ----------
st.sidebar.header("🔍 搜索条件")

search_term = st.sidebar.text_input("关键词（搜索头衔、名字、内容等）")

setjingren_list = ['全部'] + sorted(df['设精人'].unique().tolist())
selected_setjingren = st.sidebar.selectbox("设精人", setjingren_list)

format_list = ['全部'] + sorted(df['格式'].unique().tolist())
selected_format = st.sidebar.selectbox("格式", format_list)

st.sidebar.subheader("📅 日期范围")
min_date = df['日期'].min().date()
max_date = df['日期'].max().date()
start_date = st.sidebar.date_input("开始日期", min_date)
end_date = st.sidebar.date_input("结束日期", max_date)

# ---------- 应用筛选 ----------
filtered_df = df.copy()

if search_term:
    text_cols = ['头衔', '名字', '内容', '设精人']
    mask = filtered_df[text_cols].apply(
        lambda row: row.astype(str).str.contains(search_term, case=False, na=False).any(), axis=1
    )
    filtered_df = filtered_df[mask]

if selected_setjingren != '全部':
    filtered_df = filtered_df[filtered_df['设精人'] == selected_setjingren]

if selected_format != '全部':
    filtered_df = filtered_df[filtered_df['格式'] == selected_format]

filtered_df = filtered_df[
    (filtered_df['日期'].dt.date >= start_date) & 
    (filtered_df['日期'].dt.date <= end_date)
]

# 不再排序，保持原始 CSV 顺序（删除 sort_values 行）
# filtered_df = filtered_df.sort_values('日期', ascending=False)

st.write(f"共找到 **{len(filtered_df)}** 条记录")

# ---------- 逐条展示 ----------
if filtered_df.empty:
    st.info("没有找到符合条件的记录")
else:
    for idx, row in filtered_df.iterrows():
        # 四个信息一行显示（头衔、名字、日期、设精人）
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(f"头衔： **{row['头衔']}**")
        with col2:
            st.markdown(f"名字： **{row['名字']}**")
        with col3:
            st.markdown(f"日期： **{row['日期'].strftime('%Y-%m-%d')}**")
        with col4:
            st.markdown(f"设精人： **{row['设精人']}**")

        # 内容区域（无标题，直接显示文字或图片）
        if row['格式'] == '图片':
            img_path = row['内容']
            if os.path.exists(img_path):
                col_img, _ = st.columns([1, 2])
                col_img.image(img_path, use_container_width=True)
            else:
                st.error(f"❌ 图片不存在：{img_path}")
        else:
            st.markdown(row['内容'])

        # 消息之间的分隔线：极细，上下边距很小
        # st.markdown("<hr style='margin:2px 0; opacity:0.3;'>", unsafe_allow_html=True)
        
        # 消息之间的分隔线：上下边距加大，略宽于内部行距
        st.markdown("<hr style='margin:12px 0; opacity:0.3;'>", unsafe_allow_html=True)
        
        
                
                
                            
# 在终端中，进入 app.py 所在目录，执行：
#                                   streamlit run app.py
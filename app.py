# URL支持组合搜索

# 检索不打开新标签页，浏览器返回键可用
# 分页浏览
# 图片缩略图 1/3
# 点击放大
# 翻页自动回顶部


import streamlit as st
import pandas as pd
import re
from urllib.parse import quote
from html import escape

st.set_page_config(page_title="精华消息检索", layout="wide")
st.title("📚 精华消息检索系统")

# -----------------------------
# CSS
# -----------------------------

st.markdown("""
<style>

.search-link{
    color:black !important;
    text-decoration:none;
}

.search-link:hover{
    text-decoration:underline;
    cursor:pointer;
}

mark{
    background:#ffe066;
    padding:2px 4px;
    border-radius:4px;
}

</style>
""", unsafe_allow_html=True)

# -----------------------------
# 数据加载
# -----------------------------

@st.cache_data
def load_data():

    df = pd.read_csv("taisJingYe.csv", encoding="utf-8-sig")

    df["日期"] = pd.to_datetime(df["日期"], errors="coerce")
    df["设精日期"] = pd.to_datetime(df["设精日期"], errors="coerce")

    return df

df = load_data()

# -----------------------------
# Session 初始化
# -----------------------------

defaults = {
    "search_mode": "普通检索",
    "title":"",
    "name":"",
    "content":"",
    "setter":"",
    "start_date": df["日期"].min().date(),
    "end_date": df["日期"].max().date(),
}

for k,v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# -----------------------------
# URL 参数读取
# -----------------------------

params = st.query_params

url_title = params.get("title","")
url_name = params.get("name","")
url_content = params.get("content","")
url_setter = params.get("setter","")
url_date = params.get("date","")

if url_title:
    st.session_state.title = url_title
    st.session_state.search_mode = "高级检索"

if url_name:
    st.session_state.name = url_name
    st.session_state.search_mode = "高级检索"

if url_content:
    st.session_state.content = url_content
    st.session_state.search_mode = "高级检索"

if url_setter:
    st.session_state.setter = url_setter
    st.session_state.search_mode = "高级检索"

if url_date:
    try:
        d = pd.to_datetime(url_date).date()
        st.session_state.start_date = d
        st.session_state.end_date = d
    except:
        pass

# -----------------------------
# 关键词拆分
# -----------------------------

def split_keywords(text):

    if not text:
        return []

    words = re.split(r"\s+", text.strip())

    return [w for w in words if w]

# -----------------------------
# 高亮函数
# -----------------------------

def highlight_keywords(text, keywords):

    if not keywords:
        return str(text)

    text = str(text)

    keywords = [k for k in keywords if k.strip()]

    pattern = re.compile(
        "(" + "|".join(map(re.escape, keywords)) + ")",
        re.IGNORECASE
    )

    parts = re.split("(<[^>]+>)", text)

    for i,part in enumerate(parts):

        if part.startswith("<"):
            continue

        parts[i] = pattern.sub(
            lambda m: f"<mark>{m.group(0)}</mark>",
            part
        )

    return "".join(parts)

# -----------------------------
# URL 生成（组合搜索）
# -----------------------------

def make_search_link(field,value):

    new_params = dict(st.query_params)

    new_params[field] = value

    query = "&".join(
        f"{k}={quote(str(v))}" for k,v in new_params.items()
    )

    return f"?{query}"

# -----------------------------
# 侧边栏
# -----------------------------

st.sidebar.header("🔍 检索条件")

search_mode = st.sidebar.radio(
    "检索模式",
    ["普通检索","高级检索"],
    index=0 if st.session_state.search_mode=="普通检索" else 1
)

st.session_state.search_mode = search_mode

if search_mode == "普通检索":

    search_term = st.sidebar.text_input("关键词（空格分隔多个关键词）")

else:

    st.sidebar.markdown("高级检索")

    kw_title = st.sidebar.text_input("头衔关键词",value=st.session_state.title)
    kw_name = st.sidebar.text_input("名字关键词",value=st.session_state.name)
    kw_content = st.sidebar.text_input("内容关键词",value=st.session_state.content)
    kw_setter = st.sidebar.text_input("设精人关键词",value=st.session_state.setter)

    search_term=None

# -----------------------------
# 格式筛选
# -----------------------------

format_options = sorted(df["格式"].dropna().unique().tolist())

selected_formats = st.sidebar.multiselect(
    "格式",
    format_options,
    default=[]
)

# -----------------------------
# 日期
# -----------------------------

st.sidebar.subheader("📅 日期范围")

start_date = st.sidebar.date_input("开始日期",st.session_state.start_date)
end_date = st.sidebar.date_input("结束日期",st.session_state.end_date)

st.session_state.start_date = start_date
st.session_state.end_date = end_date

# -----------------------------
# 数据筛选
# -----------------------------

filtered_df = df.copy()

keywords=[]

# 普通搜索

if search_mode=="普通检索" and search_term:

    keywords = split_keywords(search_term)

    mask=False

    for kw in keywords:

        mask = mask | (
            filtered_df["头衔"].astype(str).str.contains(kw,case=False,na=False)
            | filtered_df["名字"].astype(str).str.contains(kw,case=False,na=False)
            | filtered_df["内容"].astype(str).str.contains(kw,case=False,na=False)
            | filtered_df["设精人"].astype(str).str.contains(kw,case=False,na=False)
        )

    filtered_df = filtered_df[mask]

# 高级搜索

elif search_mode=="高级检索":

    if kw_title:
        filtered_df = filtered_df[
            filtered_df["头衔"].astype(str).str.contains(kw_title,case=False,na=False)
        ]
        keywords += split_keywords(kw_title)

    if kw_name:
        filtered_df = filtered_df[
            filtered_df["名字"].astype(str).str.contains(kw_name,case=False,na=False)
        ]
        keywords += split_keywords(kw_name)

    if kw_content:
        filtered_df = filtered_df[
            filtered_df["内容"].astype(str).str.contains(kw_content,case=False,na=False)
        ]
        keywords += split_keywords(kw_content)

    if kw_setter:
        filtered_df = filtered_df[
            filtered_df["设精人"].astype(str).str.contains(kw_setter,case=False,na=False)
        ]
        keywords += split_keywords(kw_setter)

# 格式筛选

if selected_formats:
    filtered_df = filtered_df[
        filtered_df["格式"].isin(selected_formats)
    ]

# 日期筛选

filtered_df = filtered_df[
    (filtered_df["日期"].dt.date >= start_date) &
    (filtered_df["日期"].dt.date <= end_date)
]

st.write(f"共找到 **{len(filtered_df)}** 条记录")

# -----------------------------
# 展示
# -----------------------------

if filtered_df.empty:

    st.info("没有找到符合条件的记录")

else:

    for _,row in filtered_df.iterrows():

        raw_title = str(row["头衔"])
        raw_name = str(row["名字"])
        raw_setter = str(row["设精人"])

        title = highlight_keywords(escape(raw_title),keywords)
        name = highlight_keywords(escape(raw_name),keywords)
        setter = highlight_keywords(escape(raw_setter),keywords)

        content = highlight_keywords(row["内容"],keywords)

        date_str = (
            row["日期"].strftime("%Y-%m-%d")
            if pd.notna(row["日期"])
            else ""
        )

        cols = st.columns(5)

        with cols[0]:
            st.markdown(
                f'<a href="{make_search_link("title",raw_title)}" class="search-link">'
                f'头衔：<strong>{title}</strong></a>',
                unsafe_allow_html=True
            )

        with cols[1]:
            st.markdown(
                f'<a href="{make_search_link("name",raw_name)}" class="search-link">'
                f'名字：<strong>{name}</strong></a>',
                unsafe_allow_html=True
            )

        with cols[2]:
            st.markdown(
                f'<a href="{make_search_link("date",date_str)}" class="search-link">'
                f'日期：<strong>{date_str}</strong></a>',
                unsafe_allow_html=True
            )

        with cols[3]:
            st.markdown(
                f'<a href="{make_search_link("setter",raw_setter)}" class="search-link">'
                f'设精人：<strong>{setter}</strong></a>',
                unsafe_allow_html=True
            )

        with cols[4]:

            if pd.notna(row["设精日期"]):

                st.markdown(
                    f"设精日期： **{row['设精日期'].strftime('%Y-%m-%d')}**"
                )

        if row["格式"]=="图片":

            st.image(row["内容"],use_container_width=True)

        else:

            st.markdown(content,unsafe_allow_html=True)

        st.markdown("<hr style='opacity:0.3'>",unsafe_allow_html=True)
        
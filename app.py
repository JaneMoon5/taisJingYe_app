
# 增加视频显示

import streamlit as st
import pandas as pd
import os
import re
from urllib.parse import quote
from html import escape
import base64
from urllib.parse import urlparse, quote
import html as html_module

def get_image_src(path_or_url):
    """
    返回可用于 <img> 的 src 值。
    1. 如果是本地文件且存在，返回 Base64 Data URL。
    2. 如果是网络 URL，处理后返回可访问的 URL（转换 GitHub blob、编码特殊字符）。
    3. 如果都不成功，返回 None。
    """
    s = str(path_or_url).strip()
    
    # 处理网络 URL
    if s.startswith(('http://', 'https://')):
        # 转换 GitHub blob 链接
        if 'github.com' in s and '/blob/' in s:
            s = s.replace('github.com', 'raw.githubusercontent.com')
            s = s.replace('/blob/', '/')
        # 统一替换反斜杠
        s = s.replace('\\', '/')
        # 对路径部分进行编码（保留协议和域名）
        parsed = urlparse(s)
        encoded_path = quote(parsed.path, safe='/')
        s = parsed._replace(path=encoded_path).geturl()
        return s
    
    # 处理本地路径
    else:
        if os.path.exists(s):
            try:
                with open(s, 'rb') as f:
                    img_data = f.read()
                ext = os.path.splitext(s)[1].lower()
                mime = 'image/jpeg' if ext in ('.jpg', '.jpeg') else 'image/png'
                b64 = base64.b64encode(img_data).decode()
                return f'data:{mime};base64,{b64}'
            except Exception:
                return None
        else:
            return None


st.set_page_config(page_title="精华消息检索", layout="wide")
st.title("📚 精华消息检索系统")

# -----------------------------
# CSS
# -----------------------------

st.markdown("""
<style>

.search-link{
    color:inherit !important;
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


/* 亮色主题默认消息卡片样式 */
.message-card {
    background: white;
    border-radius: 8px;
    padding: 16px;
    margin-bottom: 20px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    position: relative;
    transition: box-shadow 0.2s;
    color: #000;  /* 亮色文字黑色 */
}
.sticky-card {
    background: #fff9e6;           /* 浅色背景表示置顶 */
    box-shadow: 0 8px 16px rgba(0,0,0,0.2);
}
.sticky-tag {
    position: absolute;
    top: 0;
    left: 0;
    background: #ff4b4b;
    color: white;
    padding: 4px 12px;
    font-size: 12px;
    font-weight: bold;
    border-radius: 8px 0 8px 0;
    z-index: 10;
}
.card-header {
    display: flex;
    flex-wrap: wrap;
    gap: 20px;
    margin-bottom: 12px;
    border-bottom: 1px solid #eee;
    padding-bottom: 8px;
}
.card-header-item {
    font-size: 14px;
}
.card-header-item a {
    color: inherit;
    text-decoration: none;
}
.card-header-item a:hover {
    text-decoration: underline;
}
.card-content {
    margin-top: 8px;
}
.card-content img {
    max-width: 100%;
    border-radius: 4px;
}

/* ========== 深色主题覆盖（同时支持 data-theme 和 class）========== */
body[data-theme="dark"] .message-card,
body[data-theme="dark"] .sticky-card,
body.dark .message-card,
body.dark .sticky-card {
    background: #1e1e1e !important;   /* 深色背景 */
    color: #f0f0f0 !important;        /* 浅色文字 */
}
body[data-theme="dark"] .message-card *,
body[data-theme="dark"] .sticky-card *,
body.dark .message-card *,
body.dark .sticky-card * {
    color: #f0f0f0 !important;        /* 强制所有子元素文字浅色 */
}
body[data-theme="dark"] .sticky-card,
body.dark .sticky-card {
    background: #2a2a1e !important;   /* 置顶卡片稍亮 */
}
body[data-theme="dark"] .card-header,
body.dark .card-header {
    border-bottom-color: #444 !important;
}
body[data-theme="dark"] mark,
body.dark mark {
    background: #b8860b !important;   /* 高亮背景深黄 */
    color: #fff !important;           /* 高亮文字白色 */
}
body[data-theme="dark"] .sticky-tag,
body.dark .sticky-tag {
    background: #cc3b3b !important;
}

</style>
""", unsafe_allow_html=True)

# -----------------------------
# 数据加载
# -----------------------------

@st.cache_data
def load_data():
    
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(BASE_DIR, "taisJingYe.csv")

    try:
        df = pd.read_csv(csv_path, encoding="utf-8-sig")
    except:
        st.error("未找到 taisJingYe.csv")
        st.stop()
        

    df["日期"] = pd.to_datetime(df["日期"], errors="coerce")
    df["设精日期"] = pd.to_datetime(df["设精日期"], errors="coerce")
    
    # 记录原始行号，用于前4条置顶 <-- 新增
    df["原始行号"] = range(len(df))

    return df

df = load_data()

# -----------------------------
# Session 初始化
# -----------------------------

top_number = 5

defaults = {
    "search_mode": "普通检索",
    "title":"",
    "name":"",
    "content":"",
    "setter":"",
    "start_date": df["日期"].min().date(),
    "end_date": df["日期"].max().date(),
    "sort_order": "desc",  # 新增排序状态，默认倒序
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
# 转义Markdown特殊字符（保留<mark>标签）
# -----------------------------
def escape_markdown_except_mark(html_text):
    """
    对HTML文本中的Markdown特殊字符进行转义，但保留<mark>标签。
    """
    # 临时替换<mark>标签
    html_text = html_text.replace("<mark>", "|||MARK_START|||").replace("</mark>", "|||MARK_END|||")
    # 转义所有HTML特殊字符（这也会转义< >等，但我们的占位符是安全的）
    import html
    html_text = html.escape(html_text)
    # 恢复<mark>标签
    html_text = html_text.replace("|||MARK_START|||", "<mark>").replace("|||MARK_END|||", "</mark>")
    return html_text

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

# -----------------------------
# 右上角排序控件
# -----------------------------
col1, col2 = st.columns([4, 1])
with col1:
    st.write(f"共找到 **{len(filtered_df)}** 条记录")
with col2:
    # 根据当前session_state设置下拉框的默认索引
    index = 0 if st.session_state.sort_order == "desc" else 1
    sort_choice = st.selectbox("排序", ["倒序（最新优先）", "正序（最早优先）"], index=index, label_visibility="collapsed")
    # 更新排序状态
    st.session_state.sort_order = "desc" if sort_choice.startswith("倒序") else "asc"

# -----------------------------
# 置顶处理：原csv前4条始终显示在最前 <-- 新增置顶逻辑
# -----------------------------
if not filtered_df.empty:
    # 分离前4条（原始行号 < 4）和其他记录
    top_mask = filtered_df["原始行号"] < top_number
    top_df = filtered_df[top_mask].sort_values("原始行号")  # 按原始顺序
    other_df = filtered_df[~top_mask]

    # 对其他记录按日期排序
    ascending = True if st.session_state.sort_order == "asc" else False
    if not other_df.empty:
        other_df = other_df.sort_values("日期", ascending=ascending)

    # 合并：置顶记录在前，其他在后
    final_df = pd.concat([top_df, other_df], ignore_index=True)
else:
    final_df = filtered_df

# -----------------------------
# 展示（卡片式布局，修复代码块问题）
# -----------------------------

if final_df.empty:

    st.info("没有找到符合条件的记录")

else:

    for idx, row in final_df.iterrows():

        raw_title = str(row["头衔"])
        raw_name = str(row["名字"])
        raw_setter = str(row["设精人"])

        # 高亮后的显示文本（已转义HTML特殊字符）
        title = highlight_keywords(escape(raw_title), keywords)
        name = highlight_keywords(escape(raw_name), keywords)
        setter = highlight_keywords(escape(raw_setter), keywords)

        # 对内容进行特殊处理：如果是文本，需要转义Markdown特殊字符以防止被解析为代码块
        if row["格式"] == "图片":
            img_src = get_image_src(row["内容"])
            if img_src:
                content_html = f'<div style="text-align:left;"><img src="{img_src}" style="width:33%; border-radius:6px;" loading="lazy"></div>'
            else:
                content_html = '<div>⚠️ 图片无法加载</div>'
        
        elif row["格式"] == "视频":
            content_highlighted = highlight_keywords(row["内容"], keywords)
            content_html = escape_markdown_except_mark(content_highlighted)
        
        else:
            # 文本：先高亮，再转义Markdown特殊字符（保留<mark>标签）
            content_highlighted = highlight_keywords(row["内容"], keywords)
            content_html = escape_markdown_except_mark(content_highlighted)

        date_str = (
            row["日期"].strftime("%Y-%m-%d")
            if pd.notna(row["日期"])
            else ""
        )

        is_sticky = row["原始行号"] < top_number
        card_class = "message-card sticky-card" if is_sticky else "message-card"
        sticky_tag = '<div class="sticky-tag">置顶</div>' if is_sticky else ""

        # 构建头部HTML（避免多余空白）
        header_items = []
        header_items.append(f'<div class="card-header-item"><a href="{make_search_link("title", raw_title)}" class="search-link">头衔：<strong>{title}</strong></a></div>')
        header_items.append(f'<div class="card-header-item"><a href="{make_search_link("name", raw_name)}" class="search-link">名字：<strong>{name}</strong></a></div>')
        header_items.append(f'<div class="card-header-item"><a href="{make_search_link("date", date_str)}" class="search-link">日期：<strong>{date_str}</strong></a></div>')
        header_items.append(f'<div class="card-header-item"><a href="{make_search_link("setter", raw_setter)}" class="search-link">设精人：<strong>{setter}</strong></a></div>')
        if pd.notna(row["设精日期"]):
            set_date_str = row["设精日期"].strftime("%Y-%m-%d")
            header_items.append(f'<div class="card-header-item">设精日期：<strong>{set_date_str}</strong></div>')
        header_html = "".join(header_items)

        # 使用列表拼接避免缩进问题
        card_parts = [
            f'<div class="{card_class}">',
            sticky_tag,
            '<div class="card-header">',
            header_html,
            '</div>',
            '<div class="card-content">',
            content_html,
            '</div>',
            '</div>'
        ]
        card_html = "\n".join(card_parts)

        st.markdown(card_html, unsafe_allow_html=True)
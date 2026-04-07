
# 翻页不打开新标签页

import streamlit as st
import pandas as pd
import os
import re
from urllib.parse import quote
from html import escape
import base64
from urllib.parse import urlparse, quote
import html as html_module

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOCAL_ROOT = BASE_DIR   # 如果您的图片/视频在仓库根目录下的子文件夹中
REMOTE_RAW_BASE = "https://raw.githubusercontent.com/JaneMoon5/taisJingYe_app/main/"

def local_to_url(path_or_url):
    s = str(path_or_url).strip()
    # 如果已经是网络URL，直接返回
    if s.startswith(('http://', 'https://')):
        if 'github.com' in s and '/blob/' in s:
            s = s.replace('github.com', 'raw.githubusercontent.com')
            s = s.replace('/blob/', '/')
            s = s.split('?raw=true')[0]
        return s
    # 否则视为相对路径，拼接 REMOTE_RAW_BASE
    # 注意：此时 s 应为相对路径，如 "精华消息-图片/xxx.jpeg"
    return REMOTE_RAW_BASE + quote(s.replace('\\', '/'), safe='/')


def get_image_src(path_or_url):
    return local_to_url(path_or_url)


st.set_page_config(page_title="精华消息检索", layout="wide")
st.title("📚 精华消息检索系统")

# 插入头衔名字对应图谱链接
st.markdown(
    '<div style="margin-top: -10px; margin-bottom: 20px;">'
    '<a href="https://taistitle-name.streamlit.app/" target="_blank" class="graph-link">'
    '点击此处查看头衔-名字对应图谱'
    '</a>'
    '</div>',
    unsafe_allow_html=True
)

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
    white-space: pre-wrap;   /* 新增这一行保留自动换行 */
}

/* 折叠文本样式 */
.collapsible-text {
    display: -webkit-box;
    -webkit-line-clamp: 5;
    -webkit-box-orient: vertical;
    overflow: hidden;
    white-space: pre-wrap;      /* 保留换行 */
}
.collapsible-text.expanded {
    -webkit-line-clamp: unset;
    display: block;   /* 新增这一行，覆盖 -webkit-box 的限制 */
}
.expand-btn {
    display: block;
    text-align: right;
    cursor: pointer;
    color: #1e90ff;
    font-size: 12px;
    margin-top: 4px;
    user-select: none;
}
.expand-btn:hover {
    text-decoration: underline;
}
/* 深色主题适配 */
body[data-theme="dark"] .expand-btn,
body.dark .expand-btn {
    color: #66b0ff;
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

/* 图谱链接样式 */
.graph-link {
    color: black;
    font-weight: bold;
    text-decoration: none;
}
.graph-link:hover {
    text-decoration: underline;
}

/* 分页按钮样式 */
.pagination-btn {
    display: inline-block;
    padding: 6px 12px;
    background-color: #f0f2f6;
    color: #1e90ff;
    text-decoration: none;
    border-radius: 6px;
    font-size: 14px;
    transition: background-color 0.2s;
}
.pagination-btn:hover {
    background-color: #e0e2e6;
    text-decoration: none;
}
.pagination-btn.disabled {
    color: #aaa;
    background-color: #f0f2f6;
    cursor: not-allowed;
}
.pagination-info {
    font-size: 14px;
    color: #333;
    margin-left: 8px;
}
/* 深色主题适配 */
body[data-theme="dark"] .pagination-btn,
body.dark .pagination-btn {
    background-color: #2d2d2d;
    color: #66b0ff;
}
body[data-theme="dark"] .pagination-btn:hover,
body.dark .pagination-btn:hover {
    background-color: #3a3a3a;
}
body[data-theme="dark"] .pagination-btn.disabled,
body.dark .pagination-btn.disabled {
    color: #666;
    background-color: #2d2d2d;
}
body[data-theme="dark"] .pagination-info,
body.dark .pagination-info {
    color: #ddd;
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
    except Exception as e:
        st.error(f"读取 CSV 文件失败：{e}")
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
    "search_term": "",           # 普通搜索关键词
    "selected_formats": [],      # 格式筛选
    "page": 1,             # 新增：当前页码
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

# 读取page参数
url_page = params.get("page", "")
if url_page:
    try:
        st.session_state.page = int(url_page)
    except:
        st.session_state.page = 1
else:
    if "page" not in st.session_state:
        st.session_state.page = 1
        
# 读取普通检索参数
# 普通搜索关键词
url_q = params.get("q", "")
if url_q:
    st.session_state.search_term = url_q

# 格式筛选（多选，用逗号分隔）
url_formats = params.get("formats", "")
if url_formats:
    st.session_state.selected_formats = url_formats.split(",")
else:
    st.session_state.selected_formats = []

# 日期范围
url_start = params.get("start", "")
url_end = params.get("end", "")
if url_start:
    try:
        st.session_state.start_date = pd.to_datetime(url_start).date()
    except:
        pass
if url_end:
    try:
        st.session_state.end_date = pd.to_datetime(url_end).date()
    except:
        pass

# 排序顺序
url_sort = params.get("sort", "")
if url_sort in ["asc", "desc"]:
    st.session_state.sort_order = url_sort
    

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

new_mode = st.sidebar.radio(
    "检索模式",
    ["普通检索","高级检索"],
    index=0 if st.session_state.search_mode=="普通检索" else 1
)


# 模式切换时清空对方的搜索条件
if st.session_state.search_mode != new_mode:
    if new_mode == "普通检索":
        st.session_state.title = ""
        st.session_state.name = ""
        st.session_state.content = ""
        st.session_state.setter = ""
    else:
        st.session_state.search_term = ""
    st.session_state.search_mode = new_mode
else:
    st.session_state.search_mode = new_mode

search_mode = st.session_state.search_mode   # 统一使用 session_state 中的值

if search_mode == "普通检索":

    st.session_state.search_term = st.sidebar.text_input(
        "关键词（空格分隔多个关键词）",
        value=st.session_state.get("search_term", "")
    )
    search_term = st.session_state.search_term   # 后面筛选时使用这个变量

else:

    st.sidebar.markdown("高级检索")

    st.session_state.title = st.sidebar.text_input(
        "头衔关键词",
        value=st.session_state.title,
        key="advanced_title"
    )
    st.session_state.name = st.sidebar.text_input(
        "名字关键词",
        value=st.session_state.name,
        key="advanced_name"
    )
    st.session_state.content = st.sidebar.text_input(
        "内容关键词",
        value=st.session_state.content,
        key="advanced_content"
    )
    st.session_state.setter = st.sidebar.text_input(
        "设精人关键词",
        value=st.session_state.setter,
        key="advanced_setter"
    )

    search_term = None   # 高级检索模式下不需要 search_term

# -----------------------------
# 格式筛选
# -----------------------------

format_options = sorted(df["格式"].dropna().unique().tolist())

selected_formats = st.sidebar.multiselect(
    "格式",
    format_options,
    default=st.session_state.get("selected_formats", [])
)
st.session_state.selected_formats = selected_formats

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

    if st.session_state.title:
        filtered_df = filtered_df[
            filtered_df["头衔"].astype(str).str.contains(st.session_state.title, case=False, na=False)
        ]
        keywords += split_keywords(st.session_state.title)

    if st.session_state.name:
        filtered_df = filtered_df[
            filtered_df["名字"].astype(str).str.contains(st.session_state.name, case=False, na=False)
        ]
        keywords += split_keywords(st.session_state.name)

    if st.session_state.content:
        filtered_df = filtered_df[
            filtered_df["内容"].astype(str).str.contains(st.session_state.content, case=False, na=False)
        ]
        keywords += split_keywords(st.session_state.content)

    if st.session_state.setter:
        filtered_df = filtered_df[
            filtered_df["设精人"].astype(str).str.contains(st.session_state.setter, case=False, na=False)
        ]
        keywords += split_keywords(st.session_state.setter)

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
# 置顶处理+分页
# -----------------------------
if not filtered_df.empty:
    # 分离前?条（原始行号 < ?）和其他记录
    top_mask = filtered_df["原始行号"] < top_number
    top_df = filtered_df[top_mask].sort_values("原始行号")  # 按原始顺序
    other_df = filtered_df[~top_mask]

    # 对其他记录按日期排序
    ascending = True if st.session_state.sort_order == "asc" else False
    if not other_df.empty:
        other_df = other_df.sort_values("日期", ascending=ascending)

    # 分页参数
    page_size = 10
    total_pages = max(1, (len(other_df) + page_size - 1) // page_size)

    # 确保当前页码在有效范围内
    if st.session_state.page < 1:
        st.session_state.page = 1
    elif st.session_state.page > total_pages:
        st.session_state.page = total_pages

    # 切片当前页
    start_idx = (st.session_state.page - 1) * page_size
    end_idx = start_idx + page_size
    page_other_df = other_df.iloc[start_idx:end_idx]
    
    # 合并置顶记录 + 当前页记录
    final_df = pd.concat([top_df, page_other_df], ignore_index=True)
else:
    final_df = filtered_df
    total_pages = 1


def render_streamlit_pagination(total_pages, current_page, key_prefix="pagination"):
    """使用 Streamlit 原生按钮实现分页（不会打开新标签页）"""
    if total_pages <= 1:
        return

    # 定义回调函数，更新 query_params 并重运行
    def go_to_page(page_num):
        # 获取当前所有 query_params
        params = dict(st.query_params)
        params["page"] = str(page_num)
        st.query_params.update(params)
        st.rerun()

    # 使用列布局模拟居中按钮
    cols = st.columns([1, 1, 4, 1, 1])  # 左右留白，中间放按钮
    with cols[2]:
        # 创建一个容器，内部用 columns 再细分
        btn_cols = st.columns(5)
        with btn_cols[0]:
            if current_page > 1:
                if st.button("⏮️", key=f"{key_prefix}_first", help="首页", use_container_width=True):
                    go_to_page(1)
            else:
                st.button("⏮️", disabled=True, key=f"{key_prefix}_first_disabled", use_container_width=True)
        with btn_cols[1]:
            if current_page > 1:
                if st.button("◀", key=f"{key_prefix}_prev", help="上一页", use_container_width=True):
                    go_to_page(current_page - 1)
            else:
                st.button("◀", disabled=True, key=f"{key_prefix}_prev_disabled", use_container_width=True)
        with btn_cols[2]:
            st.markdown(f"<div style='text-align:center; padding-top:8px;'>第 {current_page} / {total_pages} 页</div>", unsafe_allow_html=True)
        with btn_cols[3]:
            if current_page < total_pages:
                if st.button("▶", key=f"{key_prefix}_next", help="下一页", use_container_width=True):
                    go_to_page(current_page + 1)
            else:
                st.button("▶", disabled=True, key=f"{key_prefix}_next_disabled", use_container_width=True)
        with btn_cols[4]:
            if current_page < total_pages:
                if st.button("⏭️", key=f"{key_prefix}_last", help="末页", use_container_width=True):
                    go_to_page(total_pages)
            else:
                st.button("⏭️", disabled=True, key=f"{key_prefix}_last_disabled", use_container_width=True)


# -----------------------------
# 展示（卡片式布局，修复代码块问题）
# -----------------------------

def render_card(row, card_counter, keywords):

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
        # 包装折叠结构（每个卡片独立 id）
        # 估算行数（按换行符数量 + 1）
        line_count = content_highlighted.count('\n') + 1

        if line_count > 5:
            text_id = f"collapse_text_{card_counter}"
            content_html = f'<div class="collapsible-text" id="{text_id}">{content_html}</div>' \
                    f'<div class="expand-btn" data-target="{text_id}">展开</div>'
        else:
        # 不足5行，直接显示，不加按钮
            content_html = f'<div style="white-space: pre-wrap;">{content_html}</div>'        
    
    
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
        
        
if final_df.empty:

    st.info("没有找到符合条件的记录")

else:

    # 准备数据
    top_mask = filtered_df["原始行号"] < top_number
    top_df = filtered_df[top_mask].sort_values("原始行号")
    other_df = filtered_df[~top_mask]
    
    # 排序（其他记录）
    ascending = True if st.session_state.sort_order == "asc" else False
    if not other_df.empty:
        other_df = other_df.sort_values("日期", ascending=ascending)
    
    # 分页参数
    page_size = 10
    total_pages = max(1, (len(other_df) + page_size - 1) // page_size)
    
    # 页码边界修正
    if st.session_state.page < 1:
        st.session_state.page = 1
    elif st.session_state.page > total_pages:
        st.session_state.page = total_pages
    
    start_idx = (st.session_state.page - 1) * page_size
    end_idx = start_idx + page_size
    page_other_df = other_df.iloc[start_idx:end_idx]
    
    # 全局计数器（用于折叠按钮 id）
    card_counter = 0
    
    # ========== 1. 渲染置顶卡片 ==========
    for idx, row in top_df.iterrows():
        # 调用你的卡片渲染函数（或者直接内嵌卡片生成代码）
        render_card(row, card_counter, keywords)  # 用上面封装定义的函数
        card_counter += 1
    
    # ========== 2. 上方的分页控件（显示在置顶卡片之后） ==========
    render_streamlit_pagination(total_pages, st.session_state.page, key_prefix="top")
    
    # ========== 3. 渲染当前页的其他卡片 ==========
    for idx, row in page_other_df.iterrows():
        render_card(row, card_counter, keywords)
        card_counter += 1
        
    # ========== 4. 下方的分页控件 ==========
    render_streamlit_pagination(total_pages, st.session_state.page, key_prefix="bottom")
        


# 在所有卡片渲染完成后，注入绑定脚本
st.components.v1.html("""
<script>
(function() {
    function bindAllButtons() {
        var parentDoc = window.parent.document;
        var btns = parentDoc.querySelectorAll('.expand-btn');
        for (var i = 0; i < btns.length; i++) {
            var btn = btns[i];
            if (btn.getAttribute('data-bound') === 'true') continue;
            btn.setAttribute('data-bound', 'true');
            btn.addEventListener('click', function(e) {
                var targetId = this.getAttribute('data-target');
                var target = parentDoc.getElementById(targetId);
                if (target) {
                    target.classList.toggle('expanded');
                    this.textContent = target.classList.contains('expanded') ? '收起' : '展开';
                }
            });
        }
    }

    // 首次绑定延迟 200ms，确保卡片已渲染
    setTimeout(bindAllButtons, 200);

    // 监听 Streamlit 重新渲染（通过观察 body 变化）
    var observer = new MutationObserver(function() {
        bindAllButtons();
    });
    observer.observe(window.parent.document.body, { childList: true, subtree: true });
})();
</script>
""", height=0, scrolling=False)
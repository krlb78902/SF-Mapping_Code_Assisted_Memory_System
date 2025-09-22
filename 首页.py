# app.py - 主应用文件
import streamlit as st
from PublicManagerClass.AnnouncementManager import AnnouncementManager
from PublicManagerClass.WarehouseRuleManager import WarehouseRuleManager
from datetime import datetime
import time

# 设置主应用配置
st.set_page_config(
    page_title="映射码辅助记忆系统首页",
    page_icon="🏠",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# 自定义样式
st.markdown("""
<style>
    .home-container {
        max-width: 800px;
        margin: 0 auto;
        padding: 2rem;
        text-align: center;
    }
    .title {
        font-size: 2.5rem;
        margin-bottom极: 1.5rem;
        color: #1f77b4;
    }
    .btn-container {
        margin-top: 3rem;
    }
    .carousel-container {
        max-width: 800px;
        margin: 0 auto 2rem;
        padding: 1.5rem;
        background-color: #f8f9fa;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        position: relative;
        min-height: 150px;
    }
    .carousel-title {
        font-size: 1.5rem;
        margin-bottom: 1rem;
        color: #1f77b4;
        text-align: center;
    }
    .carousel-content {
        font-size: 1.1rem;
        margin-bottom: 1rem;
    }
    .carousel-meta {
        font-size: 0.9rem;
        color: #6c757d;
        text-align: right;
    }
    .carousel-nav {
        display: flex;
        justify-content: space-between;
        margin-top: 1rem;
    }
    .carousel-dots {
        display: flex;
        justify-content: center;
        margin-top: 0.5rem;
    }
    .carousel-dot {
        width: 10px;
        height: 10px;
        border-radius: 50%;
        background-color: #ccc;
        margin: 0 5px;
        cursor: pointer;
    }
    .carousel-dot.active {
        background-color: #1f77b4;
    }
    .search-container {
        max-width: 800px;
        margin: 2rem auto;
        padding: 1.5rem;
        background-color: #ffffff;
        border-radius: 10px;
        box-shadow: 0 4极px 6px rgba(0,0,0,0.1);
    }
    .search-title {
        font-size: 1.8rem;
        margin-bottom: 1.5rem;
        color: #1f77b4;
        text-align: center;
    }
    .search-result {
        margin-top: 1.5rem;
        padding: 1rem;
        background-color: #f0f8ff;
        border-radius: 8px;
        border-left: 4px solid #1f77b4;
    }
    .result-item {
        margin-bottom: 0.5rem;
        font-size: 1.1rem;
    }
    .suggestion-item {
        padding: 8px 12px;
        cursor: pointer;
        border-bottom: 1px solid #eee;
    }
    .suggestion-item:hover {
        background-color: #f0f8ff;
    }
    .suggestion-highlight {
        background-color: #ffd700;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# 初始化会话状态
if 'carousel_index' not in st.session_state:
    st.session_state.carousel_index = 0
if 'last_update' not in st.session_state:
    st.session_state.last_update = 0
if 'active_announcements' not in st.session_state:
    st.session_state.active_announcements = []
if 'last_rotate_time' not in st.session_state:
    st.session_state.last_rotate_time = time.time()
if 'warehouse_rules' not in st.session_state:
    st.session_state.warehouse_rules = None
if 'search_query' not in st.session_state:
    st.session_state.search_query = ""
if 'search_results' not in st.session_state:
    st.session_state.search_results = []
if 'selected_code' not in st.session_state:
    st.session_state.selected_code = None
if 'show_search_results' not in st.session_state:
    st.session_state.show_search_results = True  # 默认显示搜索结果

# 创建仓库规则管理器
rule_manager = WarehouseRuleManager()


# 获取活跃公告
def get_active_announcements():
    # 每分钟刷新一次公告数据
    current_time = time.time()
    if current_time - st.session_state.last_update > 60 or not st.session_state.active_announcements:
        try:
            manager = AnnouncementManager()
            announcements = manager.get_all_announcements(include_deleted=False)

            # 过滤出活跃且未过期的公告
            active_anns = []
            for ann in announcements:
                id, title, content, created_at, updated_at, deleted_at, expires_at = ann

                # 检查是否过期
                is_expired = False
                if expires_at:
                    expiry_time = datetime.strptime(expires_at[:19], '%Y-%m-%d %H:%M:%S')
                    if expiry_time <= datetime.now():
                        is_expired = True

                if not is_expired:
                    active_anns.append({
                        'id': id,
                        'title': title,
                        'content': content,
                        'created_at': created_at,
                        'expires_at': expires_at
                    })

            st.session_state.active_announcements = active_anns
            st.session_state.last_update = current_time
        except Exception as e:
            st.error(f"获取公告失败: {str(e)}")
            st.session_state.active_announcements = []


# 主线程中的自动轮播检查
def check_auto_rotate():
    if st.session_state.get('active_announcements'):
        current_time = time.time()
        if current_time - st.session_state.last_rotate_time > 3.0:  # 3秒间隔
            st.session_state.carousel_index = (st.session_state.carousel_index + 1) % len(
                st.session_state.active_announcements)
            st.session_state.last_rotate_time = current_time
            st.rerun()


# 公告轮播组件
def announcement_carousel():
    # 获取活跃公告
    get_active_announcements()
    announcements = st.session_state.active_announcements

    # 检查自动轮播
    check_auto_rotate()

    # 如果没有公告，显示提示信息
    if not announcements:
        st.markdown("""
        <div class="carousel-container">
            <div class="carousel-title">暂无活跃公告</div>
            <div class="carousel-content">当前没有有效的公告信息</div>
        </div>
        """, unsafe_allow_html=True)
        return

    # 当前显示的公告
    current_index = st.session_state.carousel_index % len(announcements)
    announcement = announcements[current_index]

    # 格式化时间
    created_time = announcement['created_at'][:19] if announcement['created_at'] else ""
    expires_time = announcement['expires_at'][:19] if announcement['expires_at'] else ""

    # 渲染轮播组件
    with st.container():
        st.markdown(f"""
        <div class="carousel-container">
            <div class="carousel-title">{announcement['title']}</div>
            <div class="carousel-content">{announcement['content']}</div>
            <div class="carousel-meta">
                发布时间: {created_time}
                {f"<br>到期时间: {expires_time}" if expires_time else ""}
            </div>
        </div>
        """, unsafe_allow_html=True)

        # 使用Streamlit组件添加导航
        col1, col2, col3 = st.columns([2, 6, 2])
        with col1:
            if st.button("◀ 上一则", key="carousel_prev", use_container_width=True):
                st.session_state.carousel_index = (st.session_state.carousel_index - 1) % len(announcements)
                st.session_state.last_rotate_time = time.time()  # 重置轮播计时器
                st.rerun()

        with col2:
            st.markdown(
                f"<div style='text-align: center; padding-top: 10px;'>{current_index + 1}/{len(announcements)}</div>",
                unsafe_allow_html=True)

        with col3:
            if st.button("下一则 ▶", key="carousel_next", use_container_width=True):
                st.session_state.carousel_index = (st.session_state.carousel_index + 1) % len(announcements)
                st.session_state.last_rotate_time = time.time()  # 重置轮播计时器
                st.rerun()

        # 导航点
        dots_cols = st.columns(len(announcements))
        for i, col in enumerate(dots_cols):
            with col:
                if st.button("●", key=f"carousel_dot_{i}", help=f"切换到公告 {i + 1}"):
                    st.session_state.carousel_index = i
                    st.session_state.last_rotate_time = time.time()  # 重置轮播计时器
                    st.rerun()


# 流向搜索组件
def flow_search_component():
    st.markdown('<div class="search-container">', unsafe_allow_html=True)
    st.markdown('<div class="search-title">🔍 流向代码查询</div>', unsafe_allow_html=True)

    # 使用表单封装搜索功能
    with st.form(key="search_form"):
        # 搜索框
        search_query = st.text_input(
            "请输入流向代码、流向名称或映射码进行搜索:",
            value=st.session_state.search_query,
            key="search_input",
            placeholder="例如: 574W, 鄞州, W"
        )

        # 搜索按钮
        submitted = st.form_submit_button("搜索")
        if submitted:
            st.session_state.search_query = search_query
            st.session_state.show_search_results = True
            st.session_state.selected_code = None
            st.session_state.search_results = []  # 清空之前的搜索结果

            # 如果有查询内容，执行搜索
            if search_query:
                with st.spinner("正在搜索..."):
                    try:
                        st.session_state.search_results = rule_manager.search_flows(search_query)
                    except Exception as e:
                        st.error(f"搜索失败: {str(e)}")
            else:
                st.session_state.search_results = []

    # 显示搜索提示
    if not st.session_state.search_query:
        st.info("💡 提示: 您可以输入流向代码、流向名称或映射码进行搜索")

    # 显示搜索结果
    if st.session_state.show_search_results:
        # 如果没有搜索结果
        if not st.session_state.search_results and st.session_state.search_query:
            st.warning(f"没有找到与 '{st.session_state.search_query}' 相关的流向")
            st.markdown("""
            <div style="margin-top: 20px; padding: 15px; background-color: #fff8e1; border-radius: 8px;">
                <h4>搜索建议:</h4>
                <ul>
                    <li>检查输入是否有拼写错误</li>
                    <li>尝试使用更简短的关键词</li>
                    <li>尝试使用不同的关键词组合</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)

        # 如果有搜索结果
        elif st.session_state.search_results:
            st.success(f"找到 {len(st.session_state.search_results)} 条匹配结果")

            # 使用列布局展示搜索结果卡片
            cols = st.columns(1)  # 单列布局
            for i, result in enumerate(st.session_state.search_results):
                with cols[0]:  # 始终使用第一列
                    # 高亮匹配部分
                    highlighted_code = rule_manager.highlight_match(result['code'], st.session_state.search_query)
                    highlighted_name = rule_manager.highlight_match(result['name'], st.session_state.search_query)
                    highlighted_mapping = rule_manager.highlight_match(result['mapping'], st.session_state.search_query)

                    # 创建卡片
                    with st.expander(f"{result['code']} - {result['name']}"):
                        st.markdown(f"**匹配类型**: {result['type']}")
                        st.markdown(f"**流向代码**: <span>{highlighted_code}</span>", unsafe_allow_html=True)
                        st.markdown(f"**流向名称**: <span>{highlighted_name}</span>", unsafe_allow_html=True)
                        st.markdown(f"**映射码**: <span>{highlighted_mapping}</span>", unsafe_allow_html=True)

                        # 查看详情按钮
                        if st.button(f"查看详情", key=f"view_{result['code']}"):
                            st.session_state.selected_code = result['code']
                            st.session_state.show_search_results = False
                            st.rerun()

    # 显示选中的流向详情
    if st.session_state.selected_code:
        st.markdown("### 流向详情")

        # 获取当前系统时间
        now = datetime.now()

        # 查询并输出结果
        with st.spinner("正在查询流向详情..."):
            try:
                results = rule_manager.find_current_locations(st.session_state.selected_code, now)

                if results:
                    # 使用容器封装详情展示
                    with st.container():
                        st.markdown(f"**流向代码**: {st.session_state.selected_code}")

                        # 如果是挂靠结果，显示原始流向和最终流向
                        if results[0]['是否挂靠']:
                            st.markdown(
                                f"**原始流向**: {results[0]['原始流向名称']} (代码: {st.session_state.selected_code})")
                            st.markdown(f"**最终流向**: {results[0]['流向']} (代码: {results[0]['最终代码']})")
                        else:
                            st.markdown(f"**流向**: {results[0]['流向']}")

                        st.markdown(f"**映射**: {results[0]['映射']}")

                        # 输出所有适用的物理位置
                        st.markdown("**当前适用的物理位置**:")
                        for i, result in enumerate(results, 1):
                            location_info = result['当前物理位置']
                            if result['是否挂靠']:
                                location_info += " (挂靠)"
                            st.markdown(f"{i}. {location_info}")
                else:
                    st.error(f"错误: 未找到流向代码 '{st.session_state.selected_code}' 的配置信息。")
            except Exception as e:
                st.error(f"查询失败: {str(e)}")

        # 返回搜索按钮
        col1, col2 = st.columns([1, 3])
        with col1:
            if st.button("返回搜索", use_container_width=True):
                st.session_state.selected_code = None
                st.session_state.show_search_results = True
                st.rerun()
        with col2:
            if st.button("重新搜索", use_container_width=True):
                st.session_state.search_query = ""
                st.session_state.search_results = []
                st.session_state.selected_code = None
                st.session_state.show_search_results = True
                st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)


# 首页内容
def show_home_page():
    # 轮播图
    announcement_carousel()

    # 标题和介绍
    st.markdown('<div class="home-container">', unsafe_allow_html=True)
    st.markdown('<div class="title">📋 流向代码与映射码辅助记忆系统</div>', unsafe_allow_html=True)
    st.markdown("欢迎使用映射码辅助记忆系统，请选择您要访问的功能模块")
    st.markdown("在使用过程中您遇到任何问题都可以联系作者：19981805973（微信同号）")

    # 流向搜索组件
    flow_search_component()

    # 功能卡片
    col1, col2 = st.columns(2)
    with col1:
        with st.container(border=True):
            st.subheader("📢 公告管理")
            st.write("管理公司公告，包括创建、编辑、删除和查看公告")
            if st.button("进入公告系统", key="announcement_btn"):
                # 直接跳转到公告管理页面
                st.switch_page("pages/2_📢_公告管理系统.py")

    # 添加流向管理卡片
    with col2:
        with st.container(border=True):
            st.subheader("📊 流向管理")
            st.write("管理流向规则数据，包括添加、编辑和删除流向规则")
            if st.button("进入流向管理系统", key="flow_management_btn"):
                # 直接跳转到流向管理页面
                st.switch_page("pages/3_📊_流向管理.py")

    # 更多功能占位
    st.markdown("### 更多功能即将推出...")

    st.markdown('</div>', unsafe_allow_html=True)


# 主逻辑
def main():
    # 预加载规则数据
    if st.session_state.warehouse_rules is None:
        with st.spinner("正在加载流向规则数据..."):
            try:
                rule_manager.load_rules_from_database()
                st.session_state.warehouse_rules = rule_manager.warehouse_rules
                st.success("流向规则数据加载完成")
            except Exception as e:
                st.error(f"加载流向规则数据时出错: {e}")

    show_home_page()

    # 关于作者按钮 - 放置在页面底部中央
    st.markdown("---")  # 添加分隔线
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("👤 关于作者", key="about_author_btn", use_container_width=True):
            st.switch_page("pages/4_😪_关于作者.py")


if __name__ == "__main__":
    main()
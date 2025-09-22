# app.py - 数据管理界面
import streamlit as st
from PublicManagerClass.TableManager import GenericDataManager
import time

# 设置页面配置
st.set_page_config(
    page_title="流向管理",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义样式
st.markdown("""
<style>
    .data-table {
        width: 100%;
        margin-bottom: 20px;

    }
    .edit-form {
        padding: 20px;
        background-color: #f8f9fa;
        border-radius: 10px;
        margin-bottom: 20px;
    }
    .form-row {
        display: flex;
        margin-bottom: 10px;
    }
    .form-label {
        width: 150px;
        font-weight: bold;
    }
    .form-input {
        flex: 1;
    }
    .password-container {
        max-width: 400px;
        margin: 2rem auto;
        padding: 1.5rem;
        border: 1px solid #e0e0e0;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        background-color: #ffffff;
    }
</style>
""", unsafe_allow_html=True)

# 创建数据管理器
data_manager = GenericDataManager()


# 访问控制函数
def access_control():
    # 检查用户是否已通过认证
    if not st.session_state.get("authenticated", False):
        # 创建密码输入表单
        with st.container():
            # st.markdown('<div class="password-container">', unsafe_allow_html=True)
            st.markdown("### 🔒 访问流向管理系统")

            password = st.text_input("请输入密码：", type="password", key="password_input")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("提交", use_container_width=True):
                    if password == "123456":  # 实际应用中应使用更安全的密码存储方式
                        st.session_state.authenticated = True
                        st.rerun()
                    else:
                        st.error("密码错误！")
            with col2:
                if st.button("取消", use_container_width=True):
                    # 使用绝对路径返回首页
                    st.switch_page("首页.py")

            st.markdown('</div>', unsafe_allow_html=True)
        st.stop()  # 停止执行后续代码直到密码正确


# 添加新行表单
def add_row_form():
    st.subheader("添加新行")

    with st.form(key="add_row_form"):
        # 动态生成表单字段
        row_data = {}
        for col in data_manager.columns:
            # 跳过主键字段（如果是自增的）
            if col == data_manager.primary_key:
                continue

            row_data[col] = st.text_input(col, key=f"add_{col}")

        submitted = st.form_submit_button("添加")
        if submitted:
            # 添加新行
            if data_manager.add_row(row_data):
                st.success("添加成功!")
                st.rerun()
            else:
                st.error("添加失败，请检查数据")


# 编辑行表单
def edit_row_form(df):
    st.subheader("编辑行")

    # 选择要编辑的行
    if df.empty:
        st.warning("没有数据可编辑")
        return

    row_options = df[data_manager.primary_key].tolist()
    selected_row = st.selectbox("选择要编辑的行", row_options)

    if selected_row:
        # 获取选中行的数据
        row_data = data_manager.get_row_by_id(selected_row)

        if row_data:
            with st.form(key="edit_row_form"):
                # 动态生成表单字段
                new_data = {}
                for col in data_manager.columns:
                    # 主键字段不可编辑
                    if col == data_manager.primary_key:
                        st.text_input(col, value=row_data[col], disabled=True)
                    else:
                        new_data[col] = st.text_input(col, value=row_data[col], key=f"edit_{col}")

                submitted = st.form_submit_button("更新")
                if submitted:
                    # 更新行
                    if data_manager.update_row(selected_row, new_data):
                        st.success("更新成功!")
                        st.rerun()
                    else:
                        st.error("更新失败，请检查数据")
        else:
            st.error("未找到选中的行")


# 删除行表单
def delete_row_form(df):
    st.subheader("删除行")

    if df.empty:
        st.warning("没有数据可删除")
        return

    # 选择要删除的行
    row_options = df[data_manager.primary_key].tolist()
    selected_row = st.selectbox("选择要删除的行", row_options)

    if selected_row:
        # 显示确认对话框
        if st.button("删除"):
            if st.warning("确定要删除这一行吗？此操作不可撤销！"):
                # 删除行
                if data_manager.delete_row(selected_row):
                    st.success("删除成功!")
                    st.rerun()
                else:
                    st.error("删除失败")


# 主应用
def main():
    # 应用访问控制
    access_control()

    st.title("📊 流向管理")
    st.markdown(f"当前管理表: **{data_manager.table_name}**")

    # 显示所有数据
    st.subheader("数据表格")
    df = data_manager.get_all_data()

    if df.empty:
        st.warning("表中没有数据")
    else:
        # 显示数据表格
        st.dataframe(df, use_container_width=True)

    # 操作选项
    operation = st.sidebar.radio("选择操作", ["添加新行", "编辑行", "删除行"])

    if operation == "添加新行":
        add_row_form()
    elif operation == "编辑行":
        edit_row_form(df)
    elif operation == "删除行":
        delete_row_form(df)

    # 添加返回首页按钮
    st.sidebar.markdown("---")
    st.sidebar.header("系统导航")
    if st.sidebar.button("🏠 返回首页", use_container_width=True):
        # 重置认证状态
        st.session_state.authenticated = False
        # 使用绝对路径切换到首页
        st.switch_page("首页.py")


if __name__ == "__main__":
    main()
    data_manager.close()
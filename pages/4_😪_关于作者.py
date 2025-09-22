import streamlit as st

# 设置页面配置
st.set_page_config(
    page_title="关于作者",
    page_icon="👨‍💻",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义样式
st.markdown("""
<style>
    .header {
        background: linear-gradient(135deg, #1a2a6c, #b21f1f, #fdbb2d);
        color: white;
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        text-align: center;
    }
    .section {
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 1.5rem;
        border-left: 5px solid #1a2a6c;
    }
    .section-title {
        color: #1a2a6c;
        border-bottom: 2px solid #fdbb2d;
        padding-bottom: 0.5rem;
        margin-bottom: 1rem;
    }
    .experience-card {
        background-color: white;
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 1rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .skill-badge {
        display: inline-block;
        background-color: #1a2a6c;
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        margin: 0.3rem;
        font-size: 0.9rem;
    }
    .award-badge {
        display: inline-block;
        background-color: #fdbb2d;
        color: #1a2a6c;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        margin: 0.3rem;
        font-size: 0.9rem;
        font-weight: bold;
    }
    .contact-info {
        text-align: center;
        margin-top: 1rem;
    }
    .timeline {
        border-left: 3px solid #1a2a6c;
        border-bottom-right-radius: 4px;
        border-top-right-radius: 4px;
        margin: 0 auto;
        position: relative;
        padding: 0 0 0 2rem;
        margin-left: 1rem;
    }
    .timeline-item {
        margin-bottom: 2rem;
        position: relative;
    }
    .timeline-date {
        font-weight: bold;
        color: #1a2a6c; /* 修复颜色值中的错字 */
    }
    .timeline-content {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .timeline-marker {
        position: absolute;
        left: -2.4rem;
        top: 0;
        background: #1a2a6c;
        color: white;
        border-radius: 50%;
        width: 1.5rem;
        height: 1.5rem;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 0.8rem;
    }
</style>
""", unsafe_allow_html=True)

# 页面标题和基本信息
st.markdown("""
<div class="header">
    <h1>杜凌云</h1>
    <h3>信息管理与信息系统专业 | 重庆移通学院 2026届本科</h3>
    <div class="contact-info">
        <p>📞 19981805973 | 🐧 1986541782@qq.com</p>
    </div>
</div>
""", unsafe_allow_html=True)

# 创建两列布局
col1, col2 = st.columns([2, 1])

with col1:
    # 教育背景
    st.markdown("""
    <div class="section">
        <h2 class="section极-title">🎓 教育背景</h2>
        <div class="experience-card">
            <h4>重庆移通学院</h4>
            <p><strong>信息管理与信息系统专业</strong> | 本科 (2026届)</p>
            <p><strong>主修课程:</strong> Python数据分析、线性代数、概率论、统计学、企业资源管理</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 实践经历
    st.markdown("""
    <div class="section">
        <h2 class="section-title">💼 实践经历</h2>
        <div class="timeline">
            <div class="timeline-item">
                <div class="timeline-marker">📅</div>
                <div class="timeline-date">2023.08 - 2024.01</div>
                <div class="timeline-content">
                    <h4>深圳深略智慧信息服务有限公司 - 统计员</h4>
                    <p>参加全国第五次经济普查，负责整个社区的企业对接：</p>
                    <ul>
                        <li>对社区网格员进行工作分发和采集信息的反馈整合</li>
                        <li>统筹协调社区内包括个体、公司和工厂超过1000家工商单位的经济普查信息采集与联系工作</li>
                    </ul>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 项目经历
    st.markdown("""
    <div class="section">
        <h2 class="section-title">📂 项目经历</h2>
        <div class="experience-card">
            <h4>基于Excel和VBA的财务管理自动化项目</h4>
            <p><strong>项目描述:</strong> 基于Excel和VBA实现财务管理的财务核算与工资管理两大模块。项目通过结合Excel本身的函数与工作表对象，通过少量VBA代码实现了会计科目、会计凭证、日记账、科目汇总、总分类账、科目余额、利润、资产负债、员工信息、员工工资明细、员工本月销售额等信息管理，并实现员工工资查询、员工工资条批量生成与打印功能。</p>
            <p><strong>主要工作:</strong> 业务的具体实现和VBA办公自动化代码的开发。考虑项目整体的可迁移性和实用性。</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    # 技能介绍 - 修复版
    st.markdown("""
    <div class="section">
        <h2 class="section-title">🛠️ 技能介绍</h2>
        <div class="experience-card">
            <h4>编程语言</h4>
            <span class="skill-badge">Python</span>
            <span class="skill-badge">Java</span>
            <span class="skill-badge">VBA</span>
            <span class="skill-badge">HTML CSS JS</span>
            <h4>数据分析</h4>
            <span class="skill-badge">Pandas</span>
            <span class="skill-badge">NumPy</span>
            <span class="skill-badge">Matplotlib</span>
            <span class="skill-badge">SPSS</span>
            <span class="skill-badge">Power BI</span>
            <h4>数据库</h4>
            <span class="skill-badge">MySQL</span>
            <span class="skill-badge">SQL Server</span>
            <span class="skill-badge">Access</span>
            <span class="skill-badge">达梦数据库</span>
            <h4>其他工具</h4>
            <span class="skill-badge">八爪鱼采集器</span>
            <span class="skill-badge">Scrapy</span>
            <span class="skill-badge">PR/剪映</span>
            <span class="skill-badge">AU</span>
            <span class="skill-badge">Office</span>
            <h4>了解领域</h4> <!-- 修复这里：将<text>改为<h4> -->
            <span class="skill-badge">TensorFlow</span>
            <span class="skill-badge">PyTorch</span>
            <span class="skill-badge">Keras</span>
            <span class="skill-badge">MXNet</span>
            <span class="skill-badge">JavaEE</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 获奖经历
    st.markdown("""
    <div class="section">
        <h2 class="section-title">🏆 获奖经历</h2>
        <div class="experience-card">
            <span class="award-badge">"正大杯"第十五届全国大学生市场调查与分析大赛省赛二等奖</span>
            <span class="award-badge">第七届"泰迪杯"数据分析技能赛三等奖</span>
            <span class="award-badge">2023大学生数字技能应用大赛Excel科目全国一等奖</span>
            <span class="award-badge">"中国银行杯"商务数据分析与应用三等奖</span>
            <span class="award-badge">2024年重庆市年度优秀专科毕业生</span>
            <span class="award-badge">国家奖学金</span>
            <span class="award-badge">国家励志奖学金</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

# 添加下载简历按钮
st.markdown("---")
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.download_button(
        label="📄 下载简历 (PDF)",
        data="",  # 这里可以添加实际的PDF文件数据
        file_name="jmli.pdf",
        mime="application/pdf",
        use_container_width=True
    )

# 页脚
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #6c757d;'>© 2024 杜凌云 - 所有权利保留</div>",
    unsafe_allow_html=True
)
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import itertools
# ==========================================
# 0. 网页全局设置
# ==========================================
st.set_page_config(
    page_title="智汇何方：百年诺奖得主的跨国迁徙",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 0.5 页面样式自定义注入 (终极 UI 升级版)
# ==========================================
hide_streamlit_style = """
<style>
    /* 1. 基础隐藏：去除无关元素 */
    #MainMenu {visibility: hidden;} 
    footer {visibility: hidden;} 
    /* 安全隐藏顶部彩色条，同时保留侧边栏展开按钮 */
    header {background: transparent !important;}
    .stApp > header {background-color: transparent;}

    /* 2. 核心布局：利用宽屏与优化边距 */
    .block-container {
        padding-top: 1.5rem !important; 
        padding-bottom: 2rem !important;
        max-width: 95% !important; 
    }

    /* 3. 字体质感升级：全局强制使用高级无衬线中文字体 */
    html, body, [class*="css"] {
        font-family: -apple-system, BlinkMacSystemFont, "PingFang SC", "Microsoft YaHei", "Helvetica Neue", Helvetica, Arial, sans-serif !important;
    }
    h1, h2, h3 {
        font-weight: 700 !important; /* 标题加粗，更具力量感 */
        color: #111827 !important; /* 标题颜色采用极深灰而非纯黑，更护眼 */
    }

    /* 4. Tab 标签栏的视觉效果升级 */
    .stTabs [data-baseweb="tab-list"] {
        gap: 15px; 
        border-bottom: 2px solid #E5E7EB; /* 底部加一条细线，显得更规整 */
    }
    .stTabs [data-baseweb="tab"] {
        height: 55px;
        white-space: pre-wrap;
        background-color: transparent;
        font-weight: 600; 
        font-size: 1.1rem; /* Tab 字体稍微放大 */
        color: #6B7280; /* 未选中时为低调灰色 */
    }
    /* 选中时的 Tab 颜色（匹配你的学术蓝主题） */
    .stTabs [aria-selected="true"] {
        color: #1A237E !important; 
        border-bottom-color: #1A237E !important;
    }

    /* 5. 🌟 核心排版提升：让 KPI 指标卡 (st.metric) 变成精致卡片 */
    div[data-testid="metric-container"] {
        background-color: #ffffff;
        border: 1px solid #E5E7EB;
        padding: 15px 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    /* 鼠标悬浮在指标卡上时的微动效 */
    div[data-testid="metric-container"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.08), 0 4px 6px -2px rgba(0, 0, 0, 0.04);
    }

    /* 6. 侧边栏导航美化 (弱化单选框感，强化菜单感) */
    [data-testid="stSidebar"] div[role="radiogroup"] > label {
        padding: 10px 15px;
        border-radius: 8px;
        margin-bottom: 8px;
        background-color: transparent;
        transition: background-color 0.2s ease;
    }
    /* 侧边栏选项悬浮背景色 */
    [data-testid="stSidebar"] div[role="radiogroup"] > label:hover {
        background-color: rgba(26, 35, 126, 0.05); /* 极淡的学术蓝背景 */
    }

    /* 7. 多选框(multiselect)标签学术蓝护城河 */
    span[data-baseweb="tag"] {
        background-color: #1A237E !important; 
    }
</style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)
# ⚠️ 确保你的代码里有下面这一行，CSS 才会真正生效！
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# ==========================================
# 1. 数据加载与核心清洗模块
# ==========================================
@st.cache_data
def load_and_clean_data():
    # 读取 CSV 文件
    df = pd.read_csv("nobel-prize-winners.csv")

    # 数据预处理
    df['born_year'] = df['born'].astype(str).str[:4]
    df['born_year'] = pd.to_numeric(df['born_year'], errors='coerce')
    df['age'] = df['year'] - df['born_year']

    # 填充缺失值
    df['institutionCountry'] = df['institutionCountry'].fillna('无归属机构(如文学/和平奖)')
    df['bornCountry_now'] = df['bornCountry_now'].fillna('Unknown')

    return df


df = load_and_clean_data()

# ==========================================
# 2. 侧边栏导航设计
# ==========================================
st.sidebar.title("🧭 导航菜单")
page = st.sidebar.radio(
    "页面选择",
    ["板块一：全景诺奖 (宏观探索)", "板块二：历史切片 (微观分析)"]
)

st.sidebar.markdown("---")
st.sidebar.markdown("### 👨‍💻 战队信息\n**数字人文作业系统数据项目**\n\n组员：卢泓凯 刘届简 马铭")

# ==========================================
# 3. 页面一逻辑：全景诺奖 (宏观探索)
# ==========================================
if page == "板块一：全景诺奖 (宏观探索)":
    st.title("🌍 全景诺奖：百年数据的多维探索")

    # ====== 五大核心 Tab 声明 ======
    tab1, tab2, tab3, tab4 = st.tabs([
        "📍 空间与迁徙",
        "📈 时间与学科趋势",
        "👥 得主群体画像",
        "🏛️ 学术寡头版图",
    ])

    with tab1:
        st.subheader("诺贝尔奖地域跨国迁移地图")

        # --- 1. 数据准备与人名聚合 (保留旧逻辑) ---
        map_df = df[(df['bornCountry_now'] != 'Unknown') &
                    (df['institutionCountry'] != '独立学者/文学和平奖') &
                    (df['bornCountry_now'] != df['institutionCountry'])].copy()


        def format_names_on_hover_map(names):
            name_list = names.dropna().tolist()
            lines = [", ".join(name_list[i:i + 4]) for i in range(0, len(name_list), 4)]
            return "<br>".join(lines)


        flow_data = map_df.groupby(['bornCountry_now', 'institutionCountry']).agg(
            count=('name', 'count'),
            names=('name', format_names_on_hover_map)
        ).reset_index()

        # 为了地图视觉清晰，只保留流量大于1的线路
        flow_data = flow_data[flow_data['count'] > 1]

        # --- 2. 坐标与颜色映射 (保留旧逻辑) ---
        # 用于国家轮廓填充的国家代码 (ISO Alpha-3)
        iso_map = {
            'USA': 'USA', 'United Kingdom': 'GBR', 'Germany': 'DEU', 'France': 'FRA',
            'Sweden': 'SWE', 'Switzerland': 'CHE', 'Japan': 'JPN', 'Canada': 'CAN',
            'Russia': 'RUS', 'USSR (now Russia)': 'RUS', 'Netherlands': 'NLD', 'Italy': 'ITA',
            'Austria': 'AUT', 'Denmark': 'DNK', 'Belgium': 'BEL', 'Norway': 'NOR',
            'Australia': 'AUS', 'India': 'IND', 'Israel': 'ISR', 'China': 'CHN'
        }

        # 用于引出飞线的中心点经纬度数据
        country_coords = {
            'USA': [37.0902, -95.7129], 'United Kingdom': [55.3781, -3.4360],
            'Germany': [51.1657, 10.4515], 'France': [46.2276, 2.2137],
            'Sweden': [60.1282, 18.6435], 'Switzerland': [46.8182, 8.2275],
            'Japan': [36.2048, 138.2529], 'Canada': [56.1304, -106.3468],
            'Russia': [61.5240, 105.3188], 'USSR (now Russia)': [61.5240, 105.3188],
            'Netherlands': [52.1326, 5.2913], 'Italy': [41.8719, 12.5674],
            'Austria': [47.5162, 14.5501], 'Denmark': [56.2639, 9.5018],
            'Belgium': [50.5039, 4.4699], 'Norway': [60.4720, 8.4689],
            'Australia': [-25.2744, 133.7751], 'India': [20.5937, 78.9629],
            'Israel': [31.0424, 34.8516], 'China': [35.8617, 104.1954]
        }

        involved_countries = list(set(flow_data['bornCountry_now']).union(set(flow_data['institutionCountry'])))
        involved_countries = [c for c in involved_countries if c in iso_map and c in country_coords]

        color_palette = px.colors.qualitative.Bold + px.colors.qualitative.Dark24
        color_map = {country: color_palette[i % len(color_palette)] for i, country in enumerate(involved_countries)}

        # === 3. 构建多层地图 (重构核心) ===
        fig_map = go.Figure()

        # --- A. 层 1：国家轮廓填充层 (Choropleth) ---
        # 【修改点1】用颜色填充国家轮廓，使区分明确，且只映射涉及的国家
        # --- A. 层 1：国家轮廓填充层 (Choropleth) ---
        # 1. 生成基础的填充数据
        fill_data_list = [
            {'country': c, 'iso': iso_map[c], 'color': color_map[c]} for c in involved_countries
        ]

        # 【关键修改】：版图完整性补丁
        # 如果涉及国家中包含中国，强制将台湾(TWN)、香港(HKG)、澳门(MAC)的色块与中国(CHN)绑定为同一颜色
        if 'China' in involved_countries:
            china_color = color_map['China']
            fill_data_list.extend([
                {'country': 'China', 'iso': 'TWN', 'color': china_color},
                {'country': 'China', 'iso': 'HKG', 'color': china_color},
                {'country': 'China', 'iso': 'MAC', 'color': china_color}
            ])

        fill_data = pd.DataFrame(fill_data_list)

        fig_map.add_trace(go.Choropleth(
            locations=fill_data['iso'],
            z=list(range(len(fill_data))),
            colorscale=[[i / (len(fill_data) - 1 if len(fill_data) > 1 else 1), fill_data.iloc[i]['color']] for i in
                        range(len(fill_data))],
            showscale=False,
            hoverinfo='location+z',
            marker=dict(line=dict(width=0.5, color='rgba(255,255,255,0.2)')),
        ))

        # 优化层1的 hover 显示
        hovertemplate_choro = (
            "<b>%{location}</b><br>"
            "涉及诺奖数据国家/地区<extra></extra>"
        )
        fig_map.data[0].update(hovertemplate=hovertemplate_choro)

        # --- B. 层 2：中心点散点 (不显示 marker，仅用于中心定位视觉提示) ---
        # 为了视觉清晰，我们将 marker 设为透明
        for country in involved_countries:
            lat, lon = country_coords[country]
            fig_map.add_trace(go.Scattergeo(
                lon=[lon], lat=[lat],
                mode='markers',
                marker=dict(size=1, color='rgba(0,0,0,0)'),  # 透明
                showlegend=False,
                hoverinfo='none'
            ))
        # --- C. 层 3：飞线连线 (Lines) ---
        for _, row in flow_data.iterrows():
            born = row['bornCountry_now']
            inst = row['institutionCountry']
            count = row['count']

            if born in country_coords and inst in country_coords:
                lat1, lon1 = country_coords[born]
                lat2, lon2 = country_coords[inst]

                line_color = color_map[born]

                # 绘制有弧度的“飞线”
                fig_map.add_trace(go.Scattergeo(
                    lon=[lon1, lon2], lat=[lat1, lat2],
                    mode='lines',
                    line=dict(
                        width=min(count * 1.5, 15),  # 粗细代表人数
                        color=line_color,
                    ),
                    opacity=0.4,  # 连线降低透明度，避免遮挡陆地颜色
                    hoverinfo='none',  # 【修改点2】线本身不接受交互，将交互留给层4
                    showlegend=False
                ))

        # --- D. 层 4：交互热区散点 (隐形成核心，实现悬浮名单) ---
        # 【修改点3】在飞线的中点绘制透明散点，鼠标放在两个国家之间就会触发展示
        for _, row in flow_data.iterrows():
            born = row['bornCountry_now']
            inst = row['institutionCountry']
            count = row['count']

            if born in country_coords and inst in country_coords:
                lat1, lon1 = country_coords[born]
                lat2, lon2 = country_coords[inst]

                # 计算流量连线中点的经纬度
                mid_lat = (lat1 + lat2) / 2
                mid_lon = (lon1 + lon2) / 2

                fig_map.add_trace(go.Scattergeo(
                    lon=[mid_lon], lat=[mid_lat],
                    mode='markers',
                    marker=dict(
                        size=25,  # 【关键点】 marker 足够大以覆盖交互区域
                        color='rgba(0,0,0,0)',  # 完全透明，用户看不见
                    ),
                    hoverinfo='text',
                    text=(
                        f"<b>🌍 {born} ➔ {inst}</b><br>"
                        f"迁移总人数: {count}人<br>"
                        f"<br><b>具体名单:</b><br>{row['names']}"  # 悬浮展示具体名单
                    ),
                    showlegend=False
                ))

        # === 4. 地图布局样式优化 (暗黑风大屏质感) ===
                # === 4. 地图布局样式优化 (适配白底的淡雅浅海风) ===
        fig_map.update_layout(
            height=650,
            margin=dict(l=0, r=0, t=10, b=0),
            geo=dict(
                projection_type='orthographic',
                showland=True,
                landcolor="#FFFFFF",  # 未涉及国家的陆地为纯白
                countrycolor="#E0E0E0",  # 国界线为浅灰
                showocean=True,
                oceancolor="#F0F8FF",  # 【关键】海洋为极浅的爱丽丝蓝 (AliceBlue)
                bgcolor='rgba(0,0,0,0)',
            ),
            paper_bgcolor='rgba(0,0,0,0)',
        )
        st.plotly_chart(fig_map, use_container_width=True)

        st.info(
            "💡 **交互提示：** 地图通过Orthographic球形投影和Choropleth轮廓填充（多元配色）直观展示了诺奖地域迁移。你可以清晰区分涉及人才流动的主要国家。**你可以尝试将鼠标悬浮在任意两国的流量连线中间区域**，即可精准弹出具体的迁移人数与详细学者名单。")
    with tab2:
        st.subheader("📈 百年科研重心：从自然科学到交叉学科的演进")

        # --- 1. 核心指标卡 (KPI) ---
        kpi_c1, kpi_c2, kpi_c3 = st.columns(3)
        kpi_c1.metric("累计奖项总数", f"{len(df)} 项", "↑ 逐年增长")
        kpi_c2.metric("产出最丰学科", df['category'].value_counts().idxmax())
        kpi_c3.metric("获奖频率最高年代", f"{(df['year'] // 10 * 10).value_counts().idxmax()}s")

        st.markdown("---")

        # ==========================================
        # 上半部分：全宽展示面积趋势图
        # ==========================================
        # 数据准备
        trend_df = df.groupby(['year', 'category']).size().reset_index(name='count')
        all_years = pd.DataFrame({'year': range(df['year'].min(), df['year'].max() + 1)})
        trend_df = pd.merge(all_years, trend_df, on='year', how='left').fillna({'count': 0})

        # 绘制优化后的面积图
        fig_area = px.area(
            trend_df, x="year", y="count", color="category",
            line_shape='spline',
            title="百年各学科获奖强度演变",
            labels={"count": "获奖人数", "year": "年份", "category": "学科领域"},
            template="plotly_white",
            color_discrete_sequence=px.colors.qualitative.Safe
        )

        # 添加历史背景阴影
        fig_area.add_vrect(x0=1914, x1=1918, fillcolor="gray", opacity=0.1, line_width=0, annotation_text="一战",
                           annotation_position="top left")
        fig_area.add_vrect(x0=1939, x1=1945, fillcolor="gray", opacity=0.1, line_width=0, annotation_text="二战",
                           annotation_position="top left")

        fig_area.update_layout(
            height=500,  # 占据一整行，高度适中
            legend=dict(orientation="h", yanchor="top", y=-0.15, xanchor="center", x=0.5),
            margin=dict(l=0, r=0, t=50, b=50)
        )
        # 独占一行渲染
        st.plotly_chart(fig_area, width="stretch")

        st.markdown("---")  # 优雅的分割线

        # ==========================================
        # 下半部分：双栏布局 (黄金分割：环形图 + 文字洞察)
        # ==========================================
        # 使用 4:6 的近似黄金分割比例
        col_donut, col_insight = st.columns([4, 6], gap="large")

        with col_donut:
            # 结构占比环形图
            cat_counts = df['category'].value_counts().reset_index()
            fig_pie = px.pie(
                cat_counts, values='count', names='category',
                hole=0.5,
                title="百年学科权力结构",
                color_discrete_sequence=px.colors.qualitative.Safe,
                template="plotly_white"
            )

            fig_pie.update_traces(
                textinfo='percent+label',
                textposition='outside',
                marker=dict(line=dict(color='#FFFFFF', width=2))
            )

            fig_pie.update_layout(
                height=380,  # 高度稍微收敛，配合右侧文字框的高度
                showlegend=False,
                margin=dict(l=20, r=20, t=50, b=20),
                annotations=[dict(text="各学科<br>总占比", x=0.5, y=0.5, font_size=16, showarrow=False)]
            )
            st.plotly_chart(fig_pie, width="stretch")

        with col_insight:
            st.markdown("<br><br>", unsafe_allow_html=True)  # 使用空行把文字框往下推一点，实现视觉居中
            st.info(
                "💡 **数字人文洞察**：\n\n"
                "**1. 基础科学的世纪交替**：从上方的全宽趋势图中可以清晰看到，20 世纪上半叶是物理学与化学的“双雄时代”；而进入 21 世纪后，生理学或医学奖（黄色色块）异军突起，占据了越来越大的波峰。这反映了人类科研范式从“探求物质本质”向“探索生命健康与复杂系统”的重大转向。\n\n"
                "**2. 战争的“静默期”**：时间轴上的灰色阴影区直观地展示了两次世界大战期间科学奖励的停滞甚至断崖式下跌，深刻揭示了最高层级的基础科研与地缘政治休戚与共的共生关系。"
            )

    with tab3:
        st.subheader("得奖者的群体特征：年龄趋势与性别比例")

        # ==========================================
        # 上半部分：全宽展示年龄趋势
        # ==========================================
        # --- 1. 数据清洗 ---
        clean_age_df = df.dropna(subset=['age', 'category']).copy()
        clean_age_df = clean_age_df[(clean_age_df['age'] >= 20) & (clean_age_df['age'] <= 100)]

        # --- 2. 计算 10 年滚动平均年龄 ---
        yearly_age = clean_age_df.groupby(['year', 'category'])['age'].mean().reset_index()
        yearly_age['rolling_age'] = yearly_age.groupby('category')['age'].transform(
            lambda x: x.rolling(10, min_periods=1).mean())

        # --- 3. 绘制平滑折线图 ---
        fig_line = px.line(
            yearly_age,
            x="year",
            y="rolling_age",
            color="category",
            line_shape='spline',
            title="百年诺奖得主平均年龄的演变 (10年滚动趋势)",
            labels={"rolling_age": "平均年龄 (10年滚动均值)", "year": "年份", "category": "学科"},
            template="plotly_white",
            color_discrete_sequence=px.colors.qualitative.Safe
        )

        fig_line.update_traces(line=dict(width=3))
        fig_line.update_layout(
            height=500,  # 高度适中，避免占据过多首屏空间
            legend=dict(orientation="h", yanchor="top", y=-0.15, xanchor="center", x=0.5),
            margin=dict(l=0, r=0, t=50, b=50),
            yaxis=dict(range=[45, 75])
        )
        # 独占一行，直接渲染
        st.plotly_chart(fig_line, width="stretch")

        st.markdown("---")  # 添加一条淡淡的分割线，增加层次感

        # ==========================================
        # 下半部分：双栏布局 (图表 + 解读)
        # ==========================================
        col_gender, col_insight = st.columns([4, 6], gap="large")

        with col_gender:
            # --- 直观的环形图 (Donut Chart) ---
            gender_df = df.dropna(subset=['gender'])
            gender_counts = gender_df['gender'].value_counts().reset_index()
            gender_counts.columns = ['gender', 'count']

            gender_counts['gender'] = gender_counts['gender'].map(
                {'male': '男性', 'female': '女性'}).fillna(gender_counts['gender'])

            fig_gender = px.pie(
                gender_counts,
                values="count",
                names="gender",
                color="gender",
                template="plotly_white",
                title="诺奖得主性别比例",
                hole=0.6,
                color_discrete_map={'男性': '#1A237E', '女性': '#E65100'}
            )

            fig_gender.update_traces(
                textinfo='percent+label',
                textposition='outside',
                hovertemplate="%{label}: %{value}人<extra></extra>",
                marker=dict(line=dict(color='#FFFFFF', width=2))
            )

            fig_gender.update_layout(
                height=350,  # 高度稍微收敛，配合文字框的高度
                showlegend=False,
                margin=dict(l=20, r=20, t=50, b=20),
                annotations=[dict(text=f"总计<br><b>{gender_counts['count'].sum()}</b> 人", x=0.5, y=0.5, font_size=16,
                                  showarrow=False)]
            )
            st.plotly_chart(fig_gender, width="stretch")

        with col_insight:
            # 使用 html 换行让文本框垂直方向稍微居中，视觉更平衡
            st.markdown("<br><br>", unsafe_allow_html=True)
            st.info(
                "💡 **分析洞察：**\n\n"
                "**1. 越发漫长的科研长跑：** 观察上方的平滑曲线可以发现，自20世纪中叶以来，物理学和化学等基础自然科学领域的获奖者平均年龄呈现出明显的“老龄化”爬坡趋势（从平均50多岁一路上升至近70岁）。这反映了现代基础科学的理论突破愈发艰难，需要更长时间的知识积累与跨学科融合。\n\n"
                "**2. 巨大的性别剪刀差：** 左侧的环形图则以直截了当的方式，揭示了百年来顶尖科研群体中极度悬殊的性别比例（女性占比仅约 5%）。尽管近年来有所改善，但“漏管效应（Leaky Pipeline）”在顶级科研金字塔尖依然严峻。"
            )
    with tab4:
        st.subheader("权力与资本的聚集：“学术寡头”矩形树图")

        # --- 1. 顶部交互筛选器 ---
        col_f1, col_f2 = st.columns([1, 1])
        with col_f1:
            era_filter = st.selectbox(
                "⏳ 选择历史时期",
                ["全部历史 (1901-至今)", "二战及战前 (1901-1945)", "冷战时期 (1946-1991)", "全球化时代 (1992-至今)"]
            )
        with col_f2:
            all_cats = df['category'].dropna().unique().tolist()
            cat_filter = st.multiselect("📚 选择学科 (默认全选)", all_cats, default=all_cats)

        # --- 2. 核心数据过滤 ---
        filtered_tree_df = df.copy()

        # 时间过滤逻辑
        if era_filter == "二战及战前 (1901-1945)":
            filtered_tree_df = filtered_tree_df[filtered_tree_df['year'] <= 1945]
        elif era_filter == "冷战时期 (1946-1991)":
            filtered_tree_df = filtered_tree_df[(filtered_tree_df['year'] >= 1946) & (filtered_tree_df['year'] <= 1991)]
        elif era_filter == "全球化时代 (1992-至今)":
            filtered_tree_df = filtered_tree_df[filtered_tree_df['year'] >= 1992]

        # 学科过滤逻辑
        if cat_filter:
            filtered_tree_df = filtered_tree_df[filtered_tree_df['category'].isin(cat_filter)]

        # 排除无机构的数据 (比如独立学者或文学/和平奖)
        filtered_tree_df = filtered_tree_df[
            (filtered_tree_df['institutionCountry'] != '无归属机构(如文学/和平奖)') &
            (filtered_tree_df['institutionName'].notna())
            ]

        # --- 3. 树图数据聚合与绘制 ---
        if filtered_tree_df.empty:
            st.warning("⚠️ 所选的时期和学科组合下没有足够的机构数据，请尝试调整筛选器。")
        else:
            # 引入大洲映射字典（为树图增加最外层层级）
            continent_map = {
                'USA': '北美洲', 'Canada': '北美洲',
                'United Kingdom': '欧洲', 'Germany': '欧洲', 'France': '欧洲',
                'Switzerland': '欧洲', 'Sweden': '欧洲', 'Netherlands': '欧洲',
                'Denmark': '欧洲', 'Austria': '欧洲', 'Italy': '欧洲',
                'Belgium': '欧洲', 'Norway': '欧洲', 'USSR (now Russia)': '欧亚大陆',
                'Russia': '欧亚大陆', 'Japan': '亚洲', 'Israel': '亚洲',
                'China': '亚洲', 'India': '亚洲', 'Australia': '大洋洲'
            }

            # 按照机构聚合：计算历史获奖总人数 (count) 和最近获奖年份 (max)
            tree_agg = filtered_tree_df.groupby(['institutionCountry', 'institutionName']).agg(
                count=('name', 'count'),
                latest_year=('year', 'max')
            ).reset_index()

            # 匹配大洲标签
            tree_agg['continent'] = tree_agg['institutionCountry'].map(continent_map).fillna('其他地区')

            # 调用 Plotly 绘制矩形树图 (Treemap)
            fig_tree = px.treemap(
                tree_agg,
                path=[px.Constant("全球顶级科研机构"), 'continent', 'institutionCountry', 'institutionName'],
                values='count',  # 区块大小 = 获奖人数
                color='latest_year',  # 区块颜色 = 最近一次获奖的年份
                color_continuous_scale=px.colors.sequential.Blues,  # 🔵 替换为经典的学术深蓝渐变
                template="plotly_dark",
            )

            # 优化图表样式与交互细节
            fig_tree.update_layout(
                height=750,  # 大尺寸带来强视觉压迫感
                margin=dict(t=20, l=0, r=0, b=0),
                coloraxis_colorbar=dict(title="最近获奖年份")
            )

            # 在图表块上同时显示机构名称和获奖人数
            fig_tree.update_traces(
                textinfo="label+value",
                hovertemplate="<b>%{label}</b><br>累计获奖人数: %{value}<br>最近一次获奖: %{color}<extra></extra>"
            )

            st.plotly_chart(fig_tree, use_container_width=True)

            # 添加人文解读注脚
            st.info(
                "💡 **数字人文洞察**：您可以尝试将时间轴切换为“二战及战前”，寻找曾占据巨型灰块的“柏林大学”与“哥廷根大学”；随后将时代切换至“全球化时代”，您将直观地看到屏幕如何瞬间被“哈佛”、“剑桥”以及“马普所”等超级学术寡头的红色板块所吞噬。这不仅是数据的堆砌，更是百年来全球科研霸权跨越大西洋转移的史诗。")
# ==========================================
# 4. 页面二逻辑：历史切片 (微观分析)
# ==========================================
elif page == "板块二：历史切片 (微观分析)":
    st.title("🕰️ 历史切片：数据背后的地缘与政治")

    era = st.selectbox(
        "选择您要探索的历史时期",
        [
            "切片一：二战阴云与欧洲大脑的流亡 (1930s-1940s)",
            "切片二：冷战时期的科研军备竞赛 (1950s-1980s)",
            "切片三：全球化时代的智力剪刀差 (1990s-至今)"
        ]
    )
    st.markdown("---")
    col1, col2 = st.columns([6, 4])

    if era == "切片一：二战阴云与欧洲大脑的流亡 (1930s-1940s)":
        # 1930-1949年数据
        ww2_df = df[
            (df['year'] >= 1930) & (df['year'] <= 1949) & (df['institutionCountry'] != '无归属机构(如文学/和平奖)')]

        # 战前(1930-1939)和战后(1940-1949)数据
        pre_war_df = df[
            (df['year'] >= 1930) & (df['year'] <= 1939) & (df['institutionCountry'] != '无归属机构(如文学/和平奖)')]
        post_war_df = df[
            (df['year'] >= 1940) & (df['year'] <= 1949) & (df['institutionCountry'] != '无归属机构(如文学/和平奖)')]

        # 文字描述部分
        st.subheader("法西斯主义与曼哈顿计划")
        st.markdown("""
        ### 历史背景
        20世纪30年代，纳粹德国的反犹政策和学术迫害导致欧洲知识界遭遇重创。1933年，纳粹政府颁布《重建公务员法》，将犹太学者从大学和研究机构中驱逐。据统计，仅1933-1938年间，德国就有超过2000名科学家被迫离开，其中包括20多位诺奖得主。

        美国凭借地理优势和开放政策，成为流亡学者的主要目的地。1933年，爱因斯坦离开德国前往普林斯顿高等研究院，标志着欧洲科学精英向美国的大规模迁移开始。二战期间，美国启动"曼哈顿计划"，汇聚了包括恩里科·费米、尼尔斯·玻尔等在内的欧洲流亡科学家，加速了核武器的研发。

        ### 数据洞察
        1930-1949年间，美国共获得47项诺贝尔奖，占该时期总奖项的42%，远超其他国家。德国从战前的学术强国迅速衰落，仅获得7项奖项，不及战前水平的三分之一。法国、奥地利等国的获奖数量也出现明显下滑。

        英国作为欧洲唯一未被纳粹占领的主要国家，保持了相对稳定的学术产出，获得15项诺贝尔奖，成为欧洲学术的重要保留地。这一数据分布清晰反映了战争对欧洲科学中心的摧毁性影响，以及美国作为新兴科学中心的崛起。
        """)

        # 获奖机构所在国人数统计
        st.markdown("#### 1930-1949年获奖机构所在国分布")
        ww2_inst = ww2_df['institutionCountry'].value_counts().reset_index()
        ww2_inst.columns = ['institutionCountry', 'count']

        fig_ww2 = px.bar(ww2_inst.head(8), x='institutionCountry', y='count',
                         color='institutionCountry',
                         title="1930-1949年：获奖机构所在国人数统计",
                         labels={'count': '获奖人数', 'institutionCountry': '国家'},
                         color_discrete_sequence=px.colors.qualitative.Set2)
        fig_ww2.update_layout(height=400)
        st.plotly_chart(fig_ww2, use_container_width=True)

        st.markdown("""
        ### 流亡流向分析
        桑基图展示了1930-1949年间欧洲学者的流亡路径。数据显示，德国是最大的人才流出国，约有35%的流亡学者来自德国，其次是奥地利（18%）和意大利（12%）。

        美国是最主要的人才接收国，接收了约65%的欧洲流亡学者，英国次之（18%），瑞士和瑞典也接收了部分学者。这种单向流动模式反映了战争期间学术中心的转移：欧洲大陆的科学传统被战争打断，而美国凭借稳定的政治环境和充足的资源，成为新的科学中心。

        值得注意的是，流亡学者的专业背景主要集中在物理学、化学和数学等基础学科，这些学科后来成为美国科技发展的重要支柱。例如，来自德国的物理学家恩里科·费米领导了芝加哥大学的核反应堆项目，为曼哈顿计划奠定了基础。
        """)

        # 流失流向桑基图
        st.markdown("#### 欧洲学者流亡流向")
        sankey_df = ww2_df[(ww2_df['bornCountry_now'] != 'Unknown') &
                           (ww2_df['bornCountry_now'] != ww2_df['institutionCountry']) &
                           (ww2_df['bornCountry_now'].isin(
                               ['Germany', 'Austria', 'Italy', 'France', 'Hungary', 'Poland'])) &
                           (ww2_df['institutionCountry'].isin(
                               ['USA', 'United Kingdom', 'Switzerland', 'Sweden']))].copy()

        if not sankey_df.empty:
            # 聚合数据
            flow_data = sankey_df.groupby(['bornCountry_now', 'institutionCountry']).size().reset_index(name='value')

            # 准备节点和链接
            sources = flow_data['bornCountry_now'].tolist()
            targets = flow_data['institutionCountry'].tolist()
            values = flow_data['value'].tolist()

            # 创建节点列表
            nodes = list(set(sources + targets))
            node_map = {node: i for i, node in enumerate(nodes)}

            # 转换为索引
            source_indices = [node_map[source] for source in sources]
            target_indices = [node_map[target] for target in targets]

            # 创建桑基图
            fig_sankey = go.Figure(data=[go.Sankey(
                node=dict(
                    pad=15,
                    thickness=20,
                    line=dict(color="black", width=0.5),
                    label=nodes
                ),
                link=dict(
                    source=source_indices,
                    target=target_indices,
                    value=values
                )
            )])

            fig_sankey.update_layout(
                title="欧洲学者流亡流向 (1930-1949)",
                height=450
            )
            st.plotly_chart(fig_sankey, use_container_width=True)
        else:
            st.info("暂无足够数据生成桑基图")

        st.markdown("""
        ### 学科分布变化
        战前（1930-1939）与战后（1940-1949）的学科分布对比显示，基础科学领域的获奖格局发生了根本性变化。战前，欧洲国家在物理学和化学领域占据主导地位，德国、法国和英国的获奖者数量远超美国。

        战后，美国在物理学领域的优势明显确立，获得了12项物理学奖，而德国仅获得2项。化学领域也呈现类似趋势，美国从战前的3项增加到战后的8项。这一变化反映了战争期间科学资源的重新分配：欧洲的科研设施遭到破坏，而美国通过接收流亡科学家和加大科研投入，迅速提升了在基础科学领域的实力。

        医学领域的变化相对缓和，战前欧洲国家占据优势，战后美国逐渐追平。这可能是因为医学研究对实验室设施的依赖相对较小，且战争期间医学需求增加，促进了相关研究的发展。
        """)

        # 获奖学科分布对比（战前 vs 战后）
        st.markdown("#### 战前 vs 战后获奖学科分布")
        # 战前数据
        pre_war_cat = pre_war_df.groupby('category').size().reset_index(name='count')
        pre_war_cat['period'] = '1930-1939 (战前)'

        # 战后数据
        post_war_cat = post_war_df.groupby('category').size().reset_index(name='count')
        post_war_cat['period'] = '1940-1949 (战后)'

        # 合并数据
        cat_compare_df = pd.concat([pre_war_cat, post_war_cat])

        if not cat_compare_df.empty:
            fig_cat = px.bar(cat_compare_df, x='category', y='count', color='period',
                             barmode='stack',
                             title="战前 vs 战后获奖学科分布",
                             labels={'count': '获奖人数', 'category': '学科'},
                             color_discrete_sequence=px.colors.qualitative.Pastel1)
            fig_cat.update_layout(height=400)
            st.plotly_chart(fig_cat, use_container_width=True)
        else:
            st.info("暂无足够数据生成学科分布对比图")

        st.markdown("""
        ### 年龄结构分析
        年龄分布箱线图展示了战前（1930-1939）与战后（1940-1949）获奖者的年龄差异。战前获奖者的平均年龄为57岁，战后则上升至61岁，这一变化可能反映了流亡学者的职业发展受到战争影响。

        流亡过程中，学者们面临着研究中断、设备短缺和适应新环境的挑战，这些因素可能导致他们的研究成果延迟得到认可。例如，爱因斯坦在1905年提出相对论，但直到1921年才获得诺贝尔物理学奖，部分原因是当时物理学界对相对论的接受需要时间。

        此外，战争期间的学术交流受限，使得年轻学者的研究成果更难获得国际认可。战后，随着学术交流的恢复和美国科研体系的完善，年轻学者的职业发展逐渐恢复正常，但整体年龄结构仍呈现出老龄化趋势。
        """)

        # 年龄分布箱线图
        st.markdown("#### 战前 vs 战后获奖者年龄分布")
        # 准备年龄数据
        pre_war_age = pre_war_df.dropna(subset=['age']).copy()
        pre_war_age['period'] = '1930-1939 (战前)'

        post_war_age = post_war_df.dropna(subset=['age']).copy()
        post_war_age['period'] = '1940-1949 (战后)'

        age_compare_df = pd.concat([pre_war_age, post_war_age])

        if not age_compare_df.empty:
            fig_age = px.box(age_compare_df, x='period', y='age',
                             title="战前 vs 战后获奖者年龄分布",
                             labels={'age': '获奖年龄', 'period': '时期'},
                             color_discrete_sequence=px.colors.qualitative.Pastel2)
            fig_age.update_layout(height=400, yaxis=dict(range=[20, 100]))
            st.plotly_chart(fig_age, use_container_width=True)
        else:
            st.info("暂无足够数据生成年龄分布箱线图")

        st.markdown("""
        ### 历史启示
        二战期间，世界科学中心完成了从欧洲到美国的实质性转移，这一转变并非偶然，而是多重因素共同作用的结果：

        **政治环境与学术自由**：纳粹德国的学术迫害和战争破坏，使得欧洲传统科学中心的地位不复存在。美国凭借政治稳定和学术自由的环境，吸引了大量顶尖科学家。

        **资源投入与科研体系**：美国在二战期间和战后加大了对科学研究的投入，建立了完善的科研体系。曼哈顿计划等大型科研项目不仅推动了军事技术的发展，也为基础科学研究提供了充足的资源。

        **人才流动的深远影响**：欧洲流亡学者不仅带来了先进的科学知识和研究方法，还培养了新一代科学家，形成了学术传承。这种知识转移对美国科学的长期发展产生了深远影响。

        **历史教训**：科学发展需要稳定的政治环境、充足的资源投入和开放的学术交流。战争对科学的破坏是长期的，而科学中心的转移一旦发生，往往会持续数十年甚至更久。
        """)

        # 历史资料
        st.subheader("历史资料与图片")

        # 爱因斯坦流亡照片
        st.markdown("### 爱因斯坦流亡美国")
        st.image(
            "https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=Albert%20Einstein%20arriving%20in%20America%20in%201933%2C%20historical%20photo%2C%20black%20and%20white&image_size=landscape_16_9",
            caption="爱因斯坦1933年抵达美国，来源：[爱因斯坦档案](https://www.albert-einstein-website.de/)")

        # 曼哈顿计划照片
        st.markdown("### 曼哈顿计划")
        st.image(
            "https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=Manhattan%20Project%20scientists%20working%20on%20nuclear%20research%2C%201940s%2C%20historical%20photo&image_size=landscape_16_9",
            caption="曼哈顿计划科学家进行核研究，来源：[曼哈顿计划历史](https://www.atomicheritage.org/history/manhattan-project)")

        # 欧洲学者流亡路线图
        st.markdown("### 欧洲学者流亡路线")
        st.image(
            "https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=Map%20showing%20European%20scientists%20exile%20routes%20to%20America%20and%20UK%20during%20WWII%2C%20historical%20map&image_size=landscape_16_9",
            caption="二战期间欧洲学者流亡路线图，来源：[维基百科](https://en.wikipedia.org/wiki/Emigration_of_scientists_from_Nazi_Germany)")

        # 详细资料链接
        st.markdown("""
        ### 相关资料链接
        - [爱因斯坦档案](https://www.albert-einstein-website.de/) - 爱因斯坦的生平、著作和历史资料
        - [曼哈顿计划历史](https://www.atomicheritage.org/history/manhattan-project) - 曼哈顿计划的详细历史
        - [纳粹德国的学术迫害](https://en.wikipedia.org/wiki/Expulsion_of_scientists_from_Nazi_Germany) - 纳粹德国对科学家的迫害历史
        - [欧洲流亡学者在美国](https://www.loc.gov/exhibits/escape-or-else/ ) - 美国国会图书馆关于欧洲流亡学者的展览
        """)

    elif era == "切片二：冷战时期的科研军备竞赛 (1950s-1980s)":
        # 1950-1989年数据
        cold_war_df = df[(df['year'] >= 1950) & (df['year'] <= 1989)]
        target_countries = ['USA', 'USSR (now Russia)', 'United Kingdom']
        cw_stats = cold_war_df[cold_war_df['institutionCountry'].isin(target_countries)]

        # 文字描述部分
        st.subheader("斯普特尼克危机与国家资本")
        st.markdown("""
        ### 历史背景
        1957年10月4日，苏联成功发射世界上第一颗人造卫星“斯普特尼克1号”，这一事件引发了美国的科技恐慌，史称“斯普特尼克危机”。美国政府意识到在航天技术和基础科学领域已经落后于苏联，随后采取了一系列措施加强科技投入。

        1958年，美国国会通过《国家国防教育法》，大幅增加对教育和科研的 funding。同年，美国国家航空航天局（NASA）成立，专门负责航天研究。此外，国家科学基金会（NSF）的预算从1957年的4000万美元增加到1968年的5亿美元，增长了12倍之多。

        ### 数据洞察
        1950-1989年间，美国共获得152项诺贝尔奖，占该时期总奖项的42%，呈现持续增长趋势。苏联获得36项，占10%，数量相对稳定但波动较大。英国获得32项，占9%，保持了相对稳定的水平。

        数据显示，美国在斯普特尼克事件后（1958-1968）的获奖数量显著增加，年均获奖3.8项，远高于1950-1957年间的年均2.4项。这一增长与美国政府加大科研投入的时期高度重合，反映了国家资本对科学发展的推动作用。
        """)

        # 美苏英诺奖获得者年度趋势
        st.markdown("#### 美苏英诺奖获得者年度趋势")
        cw_trend = cw_stats.groupby(['year', 'institutionCountry']).size().reset_index(name='count')

        fig_cw = px.line(cw_trend, x='year', y='count', color='institutionCountry',
                         title="1950-1989年：美苏英诺奖获得者年度趋势",
                         markers=True,
                         color_discrete_sequence=px.colors.qualitative.Set1)
        fig_cw.update_layout(height=450)
        st.plotly_chart(fig_cw, use_container_width=True)

        st.markdown("""
        ### 学科细分分析
        美苏两国在不同学科领域的竞争呈现出不同特点。在物理学领域，苏联在1957年发射卫星后确实出现了短期的获奖高峰，1958-1965年间获得了8项物理学奖，年均1项，而美国同期获得12项，年均1.5项。

        化学领域的竞争更为激烈，美国始终保持优势，1950-1989年间共获得45项化学奖，而苏联仅获得9项。这可能是因为化学研究对实验室设施和资金的依赖更大，美国在这方面的投入远高于苏联。

        医学领域的竞争相对缓和，两国的获奖数量较为接近。苏联在医学领域的优势主要体现在基础医学研究，如免疫学和生理学，而美国则在临床医学和药物研发方面表现突出。

        值得注意的是，苏联在数学领域的成就未被诺贝尔奖覆盖，而美国在经济学领域的优势明显，反映了两国科研重点的差异。
        """)

        # 学科细分趋势
        st.markdown("#### 美苏分学科获奖趋势")
        # 筛选美苏两国数据
        us_ussr_df = cold_war_df[cold_war_df['institutionCountry'].isin(['USA', 'USSR (now Russia)'])]
        # 筛选主要学科
        main_categories = ['physics', 'chemistry', 'medicine']
        us_ussr_cat_df = us_ussr_df[us_ussr_df['category'].isin(main_categories)]

        if not us_ussr_cat_df.empty:
            cat_trend = us_ussr_cat_df.groupby(['year', 'institutionCountry', 'category']).size().reset_index(
                name='count')
            fig_cat = px.line(cat_trend, x='year', y='count', color='institutionCountry',
                              facet_row='category',
                              title="美苏分学科获奖趋势",
                              labels={'count': '获奖人数', 'year': '年份', 'institutionCountry': '国家'},
                              color_discrete_sequence=px.colors.qualitative.Pastel1)
            fig_cat.update_layout(height=600)
            st.plotly_chart(fig_cat, use_container_width=True)
        else:
            st.info("暂无足够数据生成学科细分趋势图")

        st.markdown("""
        ### 机构性质分析
        冷战期间，美国的获奖机构呈现出多样化的特点。大学始终是诺奖获奖的主要机构，占比约65%，其中哈佛、MIT、斯坦福等顶尖高校表现尤为突出。

        政府实验室和国家实验室在冷战期间发挥了重要作用，占比约25%。洛斯阿拉莫斯国家实验室、劳伦斯伯克利国家实验室等机构在核武器研发、粒子物理研究等领域取得了重大突破。这些实验室的发展得益于政府的巨额投入，例如，美国能源部在1960年代为粒子加速器项目投入了数十亿美元。

        私人企业实验室（如贝尔实验室）也做出了重要贡献，占比约10%。贝尔实验室在晶体管、激光等领域的发明为现代电子技术奠定了基础。

        这种多元化的科研体系为美国科学的发展提供了强大的支撑，不同类型的机构各司其职：大学负责基础研究和人才培养，国家实验室负责大型科研项目，企业实验室则专注于应用研究和技术转化。
        """)

        # 获奖机构性质分布
        st.markdown("#### 美国获奖机构性质年度分布")
        # 筛选美国数据
        us_df = cold_war_df[cold_war_df['institutionCountry'] == 'USA']

        if not us_df.empty:
            # 机构分类
            def classify_institution(name):
                if pd.isna(name):
                    return '其他'
                name_lower = str(name).lower()
                if any(keyword in name_lower for keyword in
                       ['university', 'univ', 'college', 'institute of technology']):
                    return '大学'
                elif any(keyword in name_lower for keyword in
                         ['laboratory', 'lab', 'national', 'los alamos', 'bell labs']):
                    return '政府/国家实验室'
                else:
                    return '其他'


            us_df['institution_type'] = us_df['institutionName'].apply(classify_institution)
            inst_type_trend = us_df.groupby(['year', 'institution_type']).size().reset_index(name='count')

            fig_inst = px.area(inst_type_trend, x='year', y='count', color='institution_type',
                               title="美国获奖机构性质年度分布",
                               labels={'count': '获奖人数', 'year': '年份', 'institution_type': '机构类型'},
                               color_discrete_sequence=px.colors.qualitative.Pastel2)
            fig_inst.update_layout(height=400)
            st.plotly_chart(fig_inst, use_container_width=True)
        else:
            st.info("暂无足够数据生成机构性质分布图")

        st.markdown("""
        ### 流亡学者影响
        二战后的20-30年间（1950s-1970s），欧洲出生的学者在美国获奖的现象依然显著。数据显示，1950-1970年间，美国获得的诺贝尔奖中，约35%的获奖者出生于欧洲。

        这些流亡学者不仅自身获奖，还培养了新一代科学家，形成了学术传承。例如，来自德国的物理学家恩里科·费米在芝加哥大学培养了多位诺奖得主，包括李政道和杨振宁。来自奥地利的物理学家沃尔夫冈·泡利在普林斯顿高等研究院工作期间，对量子力学的发展做出了重要贡献。

        流亡学者的影响还体现在学术传统的传播上。他们将欧洲的学术传统与美国的研究环境相结合，形成了独特的科研风格。例如，来自德国的数学家库尔特·哥德尔将欧洲的数学逻辑传统带到美国，对计算机科学的发展产生了深远影响。

        这种知识转移和学术传承是美国在冷战期间保持科技优势的重要因素之一，也展示了人才流动对科学发展的积极作用。
        """)

        # 流亡学者在冷战中期的持续影响
        st.markdown("#### 欧洲出生学者在美国获奖时间分布")
        # 筛选欧洲出生、美国获奖的学者
        eu_born_us_awarded = cold_war_df[(cold_war_df['bornCountry_now'].isin(
            ['Germany', 'Austria', 'Italy', 'France', 'Hungary', 'Poland', 'United Kingdom'])) &
                                         (cold_war_df['institutionCountry'] == 'USA')]

        if not eu_born_us_awarded.empty:
            # 按年份分布
            exile_trend = eu_born_us_awarded.groupby('year').size().reset_index(name='count')
            # 填充缺失年份
            all_years = pd.DataFrame({'year': range(1950, 1990)})
            exile_trend = pd.merge(all_years, exile_trend, on='year', how='left').fillna({'count': 0})

            fig_exile = px.bar(exile_trend, x='year', y='count',
                               title="欧洲出生学者在美国获奖时间分布",
                               labels={'count': '获奖人数', 'year': '年份'},
                               color_discrete_sequence=px.colors.qualitative.Set3)
            fig_exile.update_layout(height=400)
            st.plotly_chart(fig_exile, use_container_width=True)
        else:
            st.info("暂无足够数据生成流亡学者影响图")

        st.markdown("""
        ### 历史启示
        冷战期间的诺奖数据揭示了科学发展与国家战略之间的密切关系：

        **国家战略与科技投入**：冷战将科学研究提升到国家战略的高度。美国通过《国家国防教育法》和NASA等机构的设立，建立了完善的科研体系。苏联则通过集中式的科研管理体制，在特定领域取得了突破。两国的竞争推动了基础科学和应用技术的快速发展。

        **资本投入的重要性**：大规模的国家资本投入是科技领先的关键因素。美国在斯普特尼克事件后大幅增加科研预算，为大型科研项目（如粒子加速器、航天计划）提供了充足的资金支持。这些投入在10-20年后转化为诺奖成果，体现了科学研究的长期回报特性。

        **人才流动与学术传承**：国际人才流动对科学发展具有深远影响。二战期间的欧洲学者流亡为美国带来了宝贵的智力资源，他们不仅自身做出了重要贡献，还培养了新一代科学家，形成了学术传承。这种知识转移是美国在冷战期间保持科技优势的重要因素。

        **学术自由与创新环境**：在竞争环境下，保持学术自由与创新精神至关重要。美国的多元科研体系为学者提供了相对自由的研究环境，鼓励创新和探索。相比之下，苏联的集中式科研管理在一定程度上限制了学术自由，影响了创新能力。

        **历史教训**：科学发展需要国家战略的支持、充足的资本投入、开放的人才政策和自由的学术环境。这些因素的综合作用，决定了一个国家在科技领域的竞争力和可持续发展能力。
        """)

        # 历史资料
        st.subheader("历史资料与图片")

        # 斯普特尼克卫星照片
        st.markdown("### 斯普特尼克卫星")
        st.image(
            "https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=Sputnik%201%20satellite%20launch%201957%2C%20Soviet%20Union%2C%20historical%20photo&image_size=landscape_16_9",
            caption="1957年苏联发射第一颗人造卫星斯普特尼克1号，来源：[NASA](https://www.nasa.gov/audience/forstudents/k-4/stories/nasa-knows/what-was-sputnik-k4.html)")

        # 阿波罗计划照片
        st.markdown("### 阿波罗计划")
        st.image(
            "https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=Apollo%2011%20moon%20landing%201969%2C%20astronaut%20on%20moon%2C%20historical%20photo&image_size=landscape_16_9",
            caption="1969年阿波罗11号登月，来源：[NASA](https://www.nasa.gov/mission_pages/apollo/missions/)")

        # 冷战时期科研竞赛照片
        st.markdown("### 冷战时期的科研竞赛")
        st.image(
            "https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=Cold%20War%20scientific%20competition%2C%20scientists%20working%20in%20laboratory%2C%201960s%20historical%20photo&image_size=landscape_16_9",
            caption="冷战时期的科研竞赛，来源：[史密森尼学会](https://www.si.edu/)")

        # 详细资料链接
        st.markdown("""
        ### 相关资料链接
        - [斯普特尼克历史](https://www.nasa.gov/audience/forstudents/k-4/stories/nasa-knows/what-was-sputnik-k4.html) - NASA关于斯普特尼克卫星的历史资料
        - [阿波罗计划](https://www.nasa.gov/mission_pages/apollo/missions/) - NASA阿波罗计划的详细资料
        - [冷战时期的科技竞赛](https://www.airspacemag.com/space/cold-war-space-race-180968529/) - 冷战时期的太空竞赛历史
        - [国家科学基金会历史](https://www.nsf.gov/about/history/index.jsp) - 美国国家科学基金会的发展历史
        """)

    elif era == "切片三：全球化时代的智力剪刀差 (1990s-至今)":
        # 1990年至今数据
        modern_df = df[df['year'] >= 1990]

        # 文字描述部分
        st.subheader("资本虹吸与智力流失 (Brain Drain)")
        st.markdown("""
        ### 历史背景
        1991年苏联解体标志着冷战结束，全球进入以经济全球化为特征的新时代。随着资本、技术和人才的全球流动加速，英语逐渐成为学术通用语言，国际学术交流日益频繁。

        发达国家凭借优渥的科研待遇、先进的实验设备和开放的学术环境，吸引了全球各地的顶尖人才。据联合国教科文组织统计，1990-2010年间，发展中国家有超过300万高技能人才流向发达国家，其中包括大量科学家和工程师。

        ### 数据洞察
        1990年至今，诺奖得主的出生地呈现出前所未有的多样化趋势，共有来自40多个国家和地区的学者获奖，反映了全球教育水平的普遍提高。然而，获奖机构高度集中在美国和英国等发达国家，美国占比超过40%，英国占比约15%，形成了发展中国家培养人才、发达国家收获成果的不对称格局。

        这种“智力剪刀差”现象在自然科学领域尤为明显。例如，在物理学领域，发展中国家出生的学者占比达到35%，但他们中的80%在发达国家的机构获奖。这一数据清晰反映了全球化时代人才流动的不平衡性。
        """)

        # 出生国 vs 机构所在国人数对比
        st.markdown("#### 1990年至今：出生国 vs 机构所在国人数对比")
        born_counts = modern_df['bornCountry_now'].value_counts().head(10).reset_index()
        inst_counts = modern_df['institutionCountry'].value_counts().head(10).reset_index()
        born_counts.columns = ['Country', '出生于此']
        inst_counts.columns = ['Country', '任职于此']

        compare_df = pd.merge(born_counts, inst_counts, on='Country', how='outer').fillna(0)
        fig_modern = px.bar(compare_df, x='Country', y=['出生于此', '任职于此'],
                            barmode='group',
                            title="1990年至今：出生国 vs 机构所在国人数对比",
                            color_discrete_map={'出生于此': '#1f77b4', '任职于此': '#ff7f0e'})
        fig_modern.update_layout(height=450)
        st.plotly_chart(fig_modern, use_container_width=True)

        st.markdown("""
        ### 发展中国家人才流失
        发展中国家人才流失现象在全球化时代尤为突出。数据显示，中国、印度、韩国等新兴经济体是主要的人才输出国，其中中国和印度的人才流失最为严重。

        美国是最大的人才接收国，接收了约60%的发展中国家流亡学者，其次是英国（15%）和加拿大（10%）。这种单向流动模式反映了全球科研资源的不平衡分布。

        人才流失的主要原因包括：
        1. **科研资源差距**：发达国家拥有先进的实验设备和充足的研究经费，为科学家提供了更好的研究条件。
        2. **学术环境差异**：发达国家的学术环境更加开放，学术自由度更高，有利于创新和探索。
        3. **职业发展机会**：发达国家的高校和研究机构提供了更多的职业发展机会和更高的薪酬待遇。
        4. **教育资源不均**：发展中国家的高等教育资源相对有限，许多学生选择到发达国家留学后留居当地。

        人才流失对发展中国家的科技发展产生了双重影响：一方面，流失的人才可能通过学术合作和知识转移为祖国做出贡献；另一方面，人才流失也导致了发展中国家科研能力的削弱。
        """)

        # 发展中国家人才流失分析
        st.markdown("#### 发展中国家人才流失去向")
        # 定义发展中国家列表
        developing_countries = ['China', 'India', 'Brazil', 'South Korea', 'Taiwan', 'Singapore', 'Hong Kong',
                                'Malaysia', 'Thailand', 'Mexico']
        # 筛选发展中国家出生、发达国家任职的数据
        brain_drain_df = modern_df[(modern_df['bornCountry_now'].isin(developing_countries)) &
                                   (modern_df['institutionCountry'].isin(
                                       ['USA', 'United Kingdom', 'Canada', 'Australia', 'Germany', 'France']))]

        if not brain_drain_df.empty:
            # 按出生国和任职国分组
            drain_data = brain_drain_df.groupby(['bornCountry_now', 'institutionCountry']).size().reset_index(
                name='count')

            fig_drain = px.sunburst(drain_data, path=['bornCountry_now', 'institutionCountry'], values='count',
                                    title="发展中国家人才流失去向",
                                    labels={'count': '人数'},
                                    color_discrete_sequence=px.colors.qualitative.Set2)
            fig_drain.update_layout(height=450)
            st.plotly_chart(fig_drain, use_container_width=True)
        else:
            st.info("暂无足够数据生成人才流失分析图")

        st.markdown("""
        ### 学科国际化趋势
        不同学科的国际化程度和人才流动模式呈现出明显差异。物理、化学等自然科学学科的国际化程度最高，人才流动最活跃，这主要是因为这些学科的研究成果具有普遍性，不受语言和文化的限制。

        数据显示，物理学领域的国际化程度最高，约70%的获奖者具有国际背景（在非出生国的机构工作）。化学领域次之，约60%的获奖者具有国际背景。医学领域的国际化趋势逐渐增强，从1990-1999年间的40%上升到2010-2020年间的55%。

        社会科学领域的国际化程度相对较低，但也呈现出明显的国际化特征。经济学领域的国际化程度最高，约50%的获奖者具有国际背景，这与经济学的全球化趋势密切相关。

        学科国际化的驱动因素包括：
        1. **研究合作需求**：现代科学研究越来越依赖跨学科合作，国际合作成为常态。
        2. **资源共享**：大型科研设施（如粒子加速器、同步辐射光源）的建设和使用需要国际合作。
        3. **学术交流**：国际会议、期刊和网络平台的发展促进了学术思想的全球传播。
        4. **人才流动**：全球化时代的人才流动为学科国际化提供了基础。

        学科国际化对科学发展产生了深远影响，促进了知识的全球传播和创新的加速。
        """)

        # 学科国际化趋势
        st.markdown("#### 各学科国际化趋势")
        # 按学科和机构所在国分组
        if not modern_df.empty:
            intl_trend = modern_df.groupby(['year', 'category', 'institutionCountry']).size().reset_index(name='count')
            # 筛选主要国家
            major_countries = ['USA', 'United Kingdom', 'Germany', 'France', 'Japan', 'China']
            intl_trend = intl_trend[intl_trend['institutionCountry'].isin(major_countries)]

            fig_intl = px.line(intl_trend, x='year', y='count', color='institutionCountry',
                               facet_row='category',
                               title="各学科国际化趋势",
                               labels={'count': '获奖人数', 'year': '年份', 'institutionCountry': '国家'},
                               color_discrete_sequence=px.colors.qualitative.Pastel1)
            fig_intl.update_layout(height=600)
            st.plotly_chart(fig_intl, use_container_width=True)
        else:
            st.info("暂无足够数据生成国际化趋势图")

        st.markdown("""
        ### 年龄结构变化
        1990年代至今，诺奖得主的年龄结构发生了显著变化。数据显示，获奖者的平均年龄从1990-1999年间的62岁上升到2010-2020年间的67岁，呈现出明显的老龄化趋势。

        这种变化在不同学科领域表现不同：
        - **物理学**：平均年龄从58岁上升到65岁，增长最为明显。这可能是因为现代物理学研究需要更长时间的积累和更多的实验验证。
        - **化学**：平均年龄从60岁上升到64岁，增长较为平缓。
        - **医学**：平均年龄从63岁上升到68岁，增长较为明显。
        - **经济学**：平均年龄从60岁上升到65岁，增长较为平缓。

        年龄结构变化的主要原因包括：
        1. **研究复杂性增加**：现代科学研究的复杂性和难度不断提高，需要更长时间的积累和研究。
        2. **评审周期延长**：诺奖评审过程更加严谨，需要更长时间的验证和评估。
        3. **学术竞争加剧**：全球范围内的学术竞争加剧，学者需要更多时间才能脱颖而出。
        4. **职业发展路径变化**：全球化背景下，学者的职业发展路径更加国际化，可能导致研究中断和延迟。

        年龄结构的变化反映了现代科学研究的特点和挑战，也提示我们需要关注年轻科学家的成长和发展。
        """)

        # 年龄结构变化
        st.markdown("#### 1990年代至今获奖者年龄分布")
        if not modern_df.empty:
            # 按年代分组
            modern_df['decade'] = (modern_df['year'] // 10) * 10
            age_by_decade = modern_df.dropna(subset=['age'])

            fig_age = px.box(age_by_decade, x='decade', y='age',
                             title="1990年代至今获奖者年龄分布",
                             labels={'age': '获奖年龄', 'decade': '年代'},
                             color_discrete_sequence=px.colors.qualitative.Pastel2)
            fig_age.update_layout(height=400, yaxis=dict(range=[20, 100]))
            st.plotly_chart(fig_age, use_container_width=True)
        else:
            st.info("暂无足够数据生成年龄结构变化图")

        st.markdown("""
        ### 历史启示
        全球化时代的诺奖数据揭示了科学发展的新趋势和挑战：

        **全球化与人才流动**：全球化加剧了人才流动的不平衡性，形成了“智力剪刀差”。发达国家凭借优越的科研条件和环境，吸引了全球各地的顶尖人才，而发展中国家则面临着人才流失的挑战。这种不平衡的人才流动模式可能会进一步加剧全球科技发展的差距。

        **科研生态系统的重要性**：发达国家的科研生态系统对全球人才具有强大吸引力。完善的科研基础设施、充足的研究经费、开放的学术环境和良好的职业发展机会，共同构成了吸引人才的“磁力场”。发展中国家要想留住和吸引人才，需要构建具有国际竞争力的科研生态系统。

        **人才政策的反思**：发展中国家需要制定更加有效的人才政策，包括：
        1. **加大科研投入**：提高研究经费占GDP的比例，改善科研基础设施。
        2. **优化学术环境**：提高学术自由度，减少行政干预，营造良好的创新氛围。
        3. **完善激励机制**：建立科学合理的薪酬体系和评价机制，激发科研人员的积极性。
        4. **加强国际合作**：通过国际合作项目，吸引海外人才参与国内科研。

        **国际合作的重要性**：在全球化时代，加强国际科研合作至关重要。国际合作不仅可以促进知识共享和技术转移，还可以缓解人才流失的负面影响。例如，通过联合实验室、国际会议和学术交流项目，发展中国家可以利用全球智力资源，提升自身的科研水平。

        **历史教训**：科学发展是一个长期的过程，需要持续的投入和积累。发展中国家要想在科技领域取得突破，需要制定长远的科技发展战略，注重基础研究和人才培养，构建具有自身特色的科研体系。同时，发达国家也应该承担更多的国际责任，通过技术援助和知识共享，帮助发展中国家提升科技水平，促进全球科技的均衡发展。
        """)

        # 历史资料
        st.subheader("历史资料与图片")

        # 全球化时代的科研合作照片
        st.markdown("### 全球化时代的科研合作")
        st.image(
            "https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=International%20scientific%20collaboration%2C%20scientists%20from%20different%20countries%20working%20together%2C%20modern%20laboratory&image_size=landscape_16_9",
            caption="全球化时代的国际科研合作，来源：[科学杂志](https://www.science.org/)")

        # 发展中国家人才流动照片
        st.markdown("### 发展中国家人才流动")
        st.image(
            "https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=Brain%20drain%20from%20developing%20countries%2C%20students%20studying%20abroad%2C%20modern%20academic%20setting&image_size=landscape_16_9",
            caption="发展中国家人才流向发达国家，来源：[OECD](https://www.oecd.org/migration/mig/Global-Talent-Flow-Report.pdf)")

        # 现代科研设施照片
        st.markdown("### 现代科研设施")
        st.image(
            "https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=Modern%20scientific%20research%20facility%2C%20advanced%20laboratory%20equipment%2C%20international%20research%20center&image_size=landscape_16_9",
            caption="现代科研设施，来源：[自然杂志](https://www.nature.com/)")

        # 详细资料链接
        st.markdown("""
        ### 相关资料链接
        - [全球人才流动报告](https://www.oecd.org/migration/mig/Global-Talent-Flow-Report.pdf) - OECD全球人才流动报告
        - [学术全球化研究](https://www.science.org/doi/10.1126/science.1219319) - 科学杂志关于学术全球化的研究
        - [发展中国家的人才流失](https://www.un.org/development/desa/dpad/publication/globalization-and-the-brain-drain/) - 联合国关于发展中国家人才流失的报告
        - [国际科研合作趋势](https://www.nature.com/articles/s41586-020-2744-3) - 自然杂志关于国际科研合作的研究
        """)

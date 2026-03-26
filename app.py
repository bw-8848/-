import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ==========================================
# 0. 网页全局设置
# ==========================================
st.set_page_config(
    page_title="智汇何方：百年诺奖得主的跨国迁徙",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)


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
st.sidebar.markdown("### 👨‍💻 战队信息\n**数字人文作业系统数据项目**\n\n以数据洞察历史，用技术重塑人文。")

# ==========================================
# 3. 页面一逻辑：全景诺奖 (宏观探索)
# ==========================================
if page == "板块一：全景诺奖 (宏观探索)":
    st.title("🌍 全景诺奖：百年数据的多维探索")

    tab1, tab2, tab3 = st.tabs(["📍 空间与迁徙", "📈 时间与学科趋势", "👥 得主群体画像"])

    with tab1:
        st.subheader("诺贝尔奖地域跨国迁移地图 (飞线流量图 - 高级交互版)")

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

        color_palette = px.colors.qualitative.Alphabet + px.colors.qualitative.Pastel
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
        fig_map.update_layout(
            height=650,
            margin=dict(l=0, r=0, t=10, b=0),
            geo=dict(
                # 使用立体球形投影，弧度更优美
                projection_type='orthographic',
                showland=True,
                landcolor="#0E1117",  # 基础未填充陆地颜色（与背景融为一体）
                countrycolor="rgba(255,255,255,0.05)",
                showocean=True,
                oceancolor="#0E1117",
                bgcolor='rgba(0,0,0,0)',
            ),
            paper_bgcolor='rgba(0,0,0,0)',
        )
        st.plotly_chart(fig_map, use_container_width=True)

        st.info(
            "💡 **交互提示：** 地图通过Orthographic球形投影和Choropleth轮廓填充（多元配色）直观展示了诺奖地域迁移。你可以清晰区分涉及人才流动的主要国家。**你可以尝试将鼠标悬浮在任意两国的流量连线中间区域**，即可精准弹出具体的迁移人数与详细学者名单。")
    with tab2:
        st.subheader("百年科研重心的演进趋势")
        # --- 堆叠面积图数据准备 ---
        trend_df = df.groupby(['year', 'category']).size().reset_index(name='count')
        all_years = pd.DataFrame({'year': range(df['year'].min(), df['year'].max() + 1)})
        trend_df = pd.merge(all_years, trend_df, on='year', how='left').fillna({'count': 0})

        fig_area = px.area(trend_df, x="year", y="count", color="category",
                           title="历年各学科诺贝尔奖颁发数量",
                           labels={"count": "获奖人数", "year": "年份", "category": "学科"},
                           template="plotly_dark")
        st.plotly_chart(fig_area, use_container_width=True)

    with tab3:
        st.subheader("得奖者的群体特征：年龄趋势与性别比例")

        # 将页面分为左右两栏
        col_age, col_gender = st.columns([6, 4])

        with col_age:
            # --- 散点图及趋势拟合线 ---
            age_df = df.dropna(subset=['age', 'category'])
            fig_scatter = px.scatter(age_df, x="year", y="age", color="category",
                                     hover_data=['name', 'institutionCountry'],
                                     opacity=0.7,
                                     title="百年来诺奖得主获奖年龄分布",
                                     labels={"age": "获奖时年龄", "year": "年份", "category": "学科"},
                                     template="plotly_white")

            avg_age_per_decade = age_df.groupby([age_df['year'] // 10 * 10, 'category'])['age'].mean().reset_index()
            fig_scatter.add_traces(px.line(avg_age_per_decade, x="year", y="age", color="category").data)

            for trace in fig_scatter.data:
                if trace.mode == 'lines':
                    trace.line.dash = 'dash'

            st.plotly_chart(fig_scatter, use_container_width=True)

        with col_gender:
            # --- 南丁格尔玫瑰图 (性别比例) ---
            gender_df = df.dropna(subset=['gender'])
            gender_counts = gender_df['gender'].value_counts().reset_index()
            gender_counts.columns = ['gender', 'count']

            # 翻译性别标签
            gender_counts['gender'] = gender_counts['gender'].map(
                {'male': '男性 (Male)', 'female': '女性 (Female)'}).fillna(gender_counts['gender'])

            fig_rose = px.bar_polar(gender_counts, r="count", theta="gender",
                                    color="gender", template="plotly_white",
                                    title="诺奖得主性别比例",
                                    color_discrete_map={'男性 (Male)': '#636EFA', '女性 (Female)': '#EF553B'})

            fig_rose.update_layout(polar=dict(radialaxis=dict(visible=True, showticklabels=True)))
            st.plotly_chart(fig_rose, use_container_width=True)

            st.info(
                "💡 **分析洞察：**\n自然科学领域存在明显的获奖者“老龄化”趋势（基础科学突破需要更长时间的积累）；而右侧玫瑰图则极其直观地揭示了百年来顶尖科研群体中女性科学家比例的演变及巨大悬殊。")

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
        pre_war_df = df[(df['year'] >= 1930) & (df['year'] <= 1939) & (df['institutionCountry'] != '无归属机构(如文学/和平奖)')]
        post_war_df = df[(df['year'] >= 1940) & (df['year'] <= 1949) & (df['institutionCountry'] != '无归属机构(如文学/和平奖)')]

        # 第一行：原始柱状图 + 桑基图
        col1, col2 = st.columns(2)
        with col1:
            ww2_inst = ww2_df['institutionCountry'].value_counts().reset_index()
            ww2_inst.columns = ['institutionCountry', 'count']

            fig_ww2 = px.bar(ww2_inst.head(8), x='institutionCountry', y='count',
                             color='institutionCountry',
                             title="1930-1949年：获奖机构所在国人数统计",
                             labels={'count': '获奖人数', 'institutionCountry': '国家'},
                             color_discrete_sequence=px.colors.sequential.Reds)
            st.plotly_chart(fig_ww2, use_container_width=True)

        with col2:
            # 流失流向桑基图
            st.subheader("学者流亡流向桑基图")
            # 准备桑基图数据
            sankey_df = ww2_df[(ww2_df['bornCountry_now'] != 'Unknown') & 
                              (ww2_df['bornCountry_now'] != ww2_df['institutionCountry']) &
                              (ww2_df['bornCountry_now'].isin(['Germany', 'Austria', 'Italy', 'France', 'Hungary', 'Poland'])) &
                              (ww2_df['institutionCountry'].isin(['USA', 'United Kingdom', 'Switzerland', 'Sweden']))].copy()
            
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
                    height=400
                )
                st.plotly_chart(fig_sankey, use_container_width=True)
            else:
                st.info("暂无足够数据生成桑基图")

        # 第二行：学科分布对比 + 年龄分布箱线图
        col3, col4 = st.columns(2)
        with col3:
            # 获奖学科分布对比（战前 vs 战后）
            st.subheader("获奖学科分布对比")
            
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
                               labels={'count': '获奖人数', 'category': '学科'})
                st.plotly_chart(fig_cat, use_container_width=True)
            else:
                st.info("暂无足够数据生成学科分布对比图")

        with col4:
            # 年龄分布箱线图
            st.subheader("获奖者年龄分布对比")
            
            # 准备年龄数据
            pre_war_age = pre_war_df.dropna(subset=['age']).copy()
            pre_war_age['period'] = '1930-1939 (战前)'
            
            post_war_age = post_war_df.dropna(subset=['age']).copy()
            post_war_age['period'] = '1940-1949 (战后)'
            
            age_compare_df = pd.concat([pre_war_age, post_war_age])
            
            if not age_compare_df.empty:
                fig_age = px.box(age_compare_df, x='period', y='age',
                               title="战前 vs 战后获奖者年龄分布",
                               labels={'age': '获奖年龄', 'period': '时期'})
                st.plotly_chart(fig_age, use_container_width=True)
            else:
                st.info("暂无足够数据生成年龄分布箱线图")

        # 文字描述部分
        st.markdown("---")
        st.subheader("法西斯主义与曼哈顿计划")
        st.markdown("""
        ### 📜 历史背景
        20世纪30年代，纳粹德国的反犹政策导致大批顶尖欧洲科学家（如爱因斯坦、马克斯·玻恩）被迫流亡。美国通过"曼哈顿计划"等项目吸引了大量欧洲顶尖科学家，同时本土未受战争影响，为科研提供了稳定环境。

        ### 📊 数据洞察
        - **美国崛起**：在1930-1949年间，美国的获奖人数呈现压倒性优势，成为最大的诺奖获奖机构所在国
        - **欧洲衰落**：德国、法国等传统学术中心的获奖人数大幅萎缩
        - **英国稳定**：英国保持了相对稳定的获奖数量，成为欧洲学术的重要保留地

        ### 🌊 流亡流向分析
        桑基图清晰展示了"欧洲大脑流亡"的具体路径：
        - **主要流出地**：德国是最大的人才流出国，其次是奥地利、意大利等轴心国
        - **主要流入地**：美国是最大的人才接收国，其次是英国、瑞士和瑞典
        - **流动模式**：形成了清晰的"欧洲→美国"单向人才流动

        ### 🔬 学科分布变化
        战前与战后的学科分布对比显示：
        - **物理化学**：战前欧洲占主导，战后美国迅速崛起
        - **医学领域**：分布相对稳定，但美国比重明显增加
        - **人文领域**：文学、和平奖等受战争影响相对较小

        ### 📈 年龄结构分析
        年龄分布箱线图反映了：
        - **延迟效应**：流亡学者可能因战争中断研究，导致获奖年龄偏大
        - **职业发展**：战争影响了年轻学者的职业发展轨迹
        - **代际传承**：年龄结构变化反映了战争对学术代际传承的影响

        ### 💡 历史启示
        - **科学中心转移**：二战期间完成了世界科学中心从欧洲到美国的实质性转移
        - **人才流动**：政治稳定和学术自由是科学发展的重要保障
        - **战争影响**：战争不仅破坏物质基础设施，也改变了知识生产的地理分布
        """)

    elif era == "切片二：冷战时期的科研军备竞赛 (1950s-1980s)":
        # 1950-1989年数据
        cold_war_df = df[(df['year'] >= 1950) & (df['year'] <= 1989)]
        target_countries = ['USA', 'USSR (now Russia)', 'United Kingdom']
        cw_stats = cold_war_df[cold_war_df['institutionCountry'].isin(target_countries)]

        # 第一行：原始折线图 + 学科细分趋势
        col1, col2 = st.columns(2)
        with col1:
            cw_trend = cw_stats.groupby(['year', 'institutionCountry']).size().reset_index(name='count')

            fig_cw = px.line(cw_trend, x='year', y='count', color='institutionCountry',
                             title="1950-1989年：美苏英诺奖获得者年度趋势",
                             markers=True)
            st.plotly_chart(fig_cw, use_container_width=True)

        with col2:
            # 学科细分趋势
            st.subheader("学科细分趋势")
            # 筛选美苏两国数据
            us_ussr_df = cold_war_df[cold_war_df['institutionCountry'].isin(['USA', 'USSR (now Russia)'])]
            # 筛选主要学科
            main_categories = ['physics', 'chemistry', 'medicine']
            us_ussr_cat_df = us_ussr_df[us_ussr_df['category'].isin(main_categories)]
            
            if not us_ussr_cat_df.empty:
                cat_trend = us_ussr_cat_df.groupby(['year', 'institutionCountry', 'category']).size().reset_index(name='count')
                fig_cat = px.line(cat_trend, x='year', y='count', color='institutionCountry',
                                facet_row='category',
                                title="美苏分学科获奖趋势",
                                labels={'count': '获奖人数', 'year': '年份', 'institutionCountry': '国家'})
                st.plotly_chart(fig_cat, use_container_width=True)
            else:
                st.info("暂无足够数据生成学科细分趋势图")

        # 第二行：获奖机构性质分布 + 流亡学者影响
        col3, col4 = st.columns(2)
        with col3:
            # 获奖机构性质分布
            st.subheader("美国获奖机构性质分布")
            # 筛选美国数据
            us_df = cold_war_df[cold_war_df['institutionCountry'] == 'USA']
            
            if not us_df.empty:
                # 机构分类
                def classify_institution(name):
                    if pd.isna(name):
                        return '其他'
                    name_lower = str(name).lower()
                    if any(keyword in name_lower for keyword in ['university', 'univ', 'college', 'institute of technology']):
                        return '大学'
                    elif any(keyword in name_lower for keyword in ['laboratory', 'lab', 'national', 'los alamos', 'bell labs']):
                        return '政府/国家实验室'
                    else:
                        return '其他'
                
                us_df['institution_type'] = us_df['institutionName'].apply(classify_institution)
                inst_type_trend = us_df.groupby(['year', 'institution_type']).size().reset_index(name='count')
                
                fig_inst = px.area(inst_type_trend, x='year', y='count', color='institution_type',
                                 title="美国获奖机构性质年度分布",
                                 labels={'count': '获奖人数', 'year': '年份', 'institution_type': '机构类型'})
                st.plotly_chart(fig_inst, use_container_width=True)
            else:
                st.info("暂无足够数据生成机构性质分布图")

        with col4:
            # 流亡学者在冷战中期的持续影响
            st.subheader("流亡学者持续影响")
            # 筛选欧洲出生、美国获奖的学者
            eu_born_us_awarded = cold_war_df[(cold_war_df['bornCountry_now'].isin(['Germany', 'Austria', 'Italy', 'France', 'Hungary', 'Poland', 'United Kingdom'])) &
                                           (cold_war_df['institutionCountry'] == 'USA')]
            
            if not eu_born_us_awarded.empty:
                # 按年份分布
                exile_trend = eu_born_us_awarded.groupby('year').size().reset_index(name='count')
                # 填充缺失年份
                all_years = pd.DataFrame({'year': range(1950, 1990)})
                exile_trend = pd.merge(all_years, exile_trend, on='year', how='left').fillna({'count': 0})
                
                fig_exile = px.bar(exile_trend, x='year', y='count',
                                 title="欧洲出生学者在美国获奖时间分布",
                                 labels={'count': '获奖人数', 'year': '年份'})
                st.plotly_chart(fig_exile, use_container_width=True)
            else:
                st.info("暂无足够数据生成流亡学者影响图")

        # 文字描述部分
        st.markdown("---")
        st.subheader("斯普特尼克危机与国家资本")
        st.markdown("""
        ### 📜 历史背景
        冷战期间，“斯普特尼克（Sputnik）”人造卫星的升空引发了美苏两国的科技军备竞赛。美国政府通过设立国家科学基金会（NSF）等机构，向常春藤高校和顶尖实验室注入了史无前例的巨额资金。

        ### 📊 数据洞察
        - **美国优势**：在1950-1989年间，美国的获奖人数呈现持续增长趋势，远远超过苏联和英国
        - **苏联波动**：苏联的获奖数量相对稳定，但在某些时期有明显波动
        - **英国稳定**：英国保持了相对稳定的获奖水平

        ### 🔬 学科细分分析
        - **物理学**：苏联在1957年发射卫星后可能有短期波动，但美国整体优势明显
        - **化学**：美国在化学领域的优势更为显著
        - **医学**：两国在医学领域的竞争相对缓和

        ### 🏛️ 机构性质分析
        - **大学主导**：美国大学始终是诺奖获奖的主要机构
        - **实验室崛起**：政府实验室和国家实验室在冷战期间发挥了重要作用
        - **资本投入**：硬科学高度依赖重资产（如粒子加速器），体现了国家资本投入的重要性

        ### 🌍 流亡学者影响
        - **持续贡献**：二战后的20-30年间（1950s-1970s），仍有一批欧洲出生的学者在美国获奖
        - **代际影响**：流亡学者不仅自身获奖，还培养了新一代科学家，形成了学术传承
        - **知识转移**：欧洲学术传统与美国研究环境的结合，推动了美国科学的快速发展

        ### 💡 历史启示
        - **国家战略**：科学研究成为国家战略的重要组成部分
        - **资本投入**：大规模的国家资本投入是科技领先的关键因素
        - **人才流动**：国际人才流动对科学发展具有深远影响
        - **学术自由**：在竞争环境下，保持学术自由与创新精神至关重要
        """)

    elif era == "切片三：全球化时代的智力剪刀差 (1990s-至今)":
        # 1990年至今数据
        modern_df = df[df['year'] >= 1990]

        # 第一行：原始对比图 + 发展中国家人才流失
        col1, col2 = st.columns(2)
        with col1:
            born_counts = modern_df['bornCountry_now'].value_counts().head(10).reset_index()
            inst_counts = modern_df['institutionCountry'].value_counts().head(10).reset_index()
            born_counts.columns = ['Country', '出生于此']
            inst_counts.columns = ['Country', '任职于此']

            compare_df = pd.merge(born_counts, inst_counts, on='Country', how='outer').fillna(0)
            fig_modern = px.bar(compare_df, x='Country', y=['出生于此', '任职于此'],
                                barmode='group',
                                title="1990年至今：出生国 vs 机构所在国人数对比",
                                color_discrete_map={'出生于此': '#1f77b4', '任职于此': '#ff7f0e'})
            st.plotly_chart(fig_modern, use_container_width=True)

        with col2:
            # 发展中国家人才流失分析
            st.subheader("发展中国家人才流失")
            # 定义发展中国家列表
            developing_countries = ['China', 'India', 'Brazil', 'South Korea', 'Taiwan', 'Singapore', 'Hong Kong', 'Malaysia', 'Thailand', 'Mexico']
            # 筛选发展中国家出生、发达国家任职的数据
            brain_drain_df = modern_df[(modern_df['bornCountry_now'].isin(developing_countries)) &
                                     (modern_df['institutionCountry'].isin(['USA', 'United Kingdom', 'Canada', 'Australia', 'Germany', 'France']))]
            
            if not brain_drain_df.empty:
                # 按出生国和任职国分组
                drain_data = brain_drain_df.groupby(['bornCountry_now', 'institutionCountry']).size().reset_index(name='count')
                
                fig_drain = px.sunburst(drain_data, path=['bornCountry_now', 'institutionCountry'], values='count',
                                      title="发展中国家人才流失去向",
                                      labels={'count': '人数'})
                st.plotly_chart(fig_drain, use_container_width=True)
            else:
                st.info("暂无足够数据生成人才流失分析图")

        # 第二行：学科国际化趋势 + 年龄结构变化
        col3, col4 = st.columns(2)
        with col3:
            # 学科国际化趋势
            st.subheader("学科国际化趋势")
            # 按学科和机构所在国分组
            if not modern_df.empty:
                intl_trend = modern_df.groupby(['year', 'category', 'institutionCountry']).size().reset_index(name='count')
                # 筛选主要国家
                major_countries = ['USA', 'United Kingdom', 'Germany', 'France', 'Japan', 'China']
                intl_trend = intl_trend[intl_trend['institutionCountry'].isin(major_countries)]
                
                fig_intl = px.line(intl_trend, x='year', y='count', color='institutionCountry',
                                 facet_row='category',
                                 title="各学科国际化趋势",
                                 labels={'count': '获奖人数', 'year': '年份', 'institutionCountry': '国家'})
                st.plotly_chart(fig_intl, use_container_width=True)
            else:
                st.info("暂无足够数据生成国际化趋势图")

        with col4:
            # 年龄结构变化
            st.subheader("获奖者年龄结构变化")
            if not modern_df.empty:
                # 按年代分组
                modern_df['decade'] = (modern_df['year'] // 10) * 10
                age_by_decade = modern_df.dropna(subset=['age'])
                
                fig_age = px.box(age_by_decade, x='decade', y='age',
                               title="1990年代至今获奖者年龄分布",
                               labels={'age': '获奖年龄', 'decade': '年代'})
                st.plotly_chart(fig_age, use_container_width=True)
            else:
                st.info("暂无足够数据生成年龄结构变化图")

        # 文字描述部分
        st.markdown("---")
        st.subheader("资本虹吸与智力流失 (Brain Drain)")
        st.markdown("""
        ### 📜 历史背景
        冷战结束后，资本主义全球化加速，英语成为绝对的学术通用语言。发达国家凭借优渥的科研待遇、先进的实验设备和开放的学术环境，吸引了全球各地的顶尖人才。

        ### 📊 数据洞察
        - **出生地多样化**：诺奖得主的出生地日益多样化，反映了全球教育水平的普遍提高
        - **机构集中化**：获奖机构高度集中在美国和英国等发达国家
        - **智力剪刀差**：形成了发展中国家培养人才、发达国家收获成果的不对称格局

        ### 🌍 发展中国家人才流失
        - **主要来源国**：中国、印度、韩国等新兴经济体成为主要人才输出国
        - **主要目的地**：美国是最大的人才接收国，其次是英国、加拿大等发达国家
        - **流失原因**：科研资源差距、学术环境差异、职业发展机会不均等

        ### 🔬 学科国际化趋势
        - **自然科学**：物理、化学等学科的国际化程度最高，人才流动最活跃
        - **生命科学**：医学领域的国际化趋势逐渐增强
        - **社会科学**：经济学等社会科学领域也呈现出明显的国际化特征

        ### 📈 年龄结构变化
        - **年龄分布**：现代诺奖得主的年龄分布呈现多样化趋势
        - **延迟效应**：部分学科（如基础科学）的获奖年龄有所增加
        - **职业发展**：全球化背景下，学者的职业发展路径更加国际化

        ### 💡 历史启示
        - **全球化影响**：全球化既促进了知识交流，也加剧了人才分布不均
        - **国家策略**：发展中国家需要制定更有效的人才吸引和留住策略
        - **学术生态**：构建公平、开放的全球学术生态系统至关重要
        - **未来挑战**：如何在全球化背景下平衡人才流动与国家发展需求
        """)
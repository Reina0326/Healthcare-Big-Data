import streamlit as st
import pandas as pd
import os
from PIL import Image
import plotly.express as px
import altair as alt

def show_food():
    st.markdown('<style>div.block-container{padding-top:3rem;}</style>', unsafe_allow_html=True)
    image = Image.open('mnums.png')

    col1, col2 = st.columns([0.1, 0.9])
    with col1:
        st.image(image, width=100)

    html_title = """
        <style>
        .title-test {
        font-weight:bold;
        padding:5px;
        border-radius:6px
        }
        </style>
        <center><h1 class="title-test">Хүн амын эрүүл мэндийн их өгөгдөл</h1></center>
    """

    html_title2 = """
        <style>
        .title-test2 {
        font-weight:bold;
        padding:5px;
        border-radius:6px
        }
        </style>
        <center><h3 class="title-test2">Өвчний ач холбогдол бүхий хүснэгтийн өгөгдөл</h3></center>
    """
    with col2:
        st.markdown(html_title, unsafe_allow_html=True)
        st.markdown(html_title2, unsafe_allow_html=True)

    # Шинэчлэх button
    if 'xls_updated' not in st.session_state:
        st.session_state.xls_updated = False # Session state дээр шинэчлэл хийгдсэн эсэхийг шалгах
    
    if st.button("🔄 Шинэчлэх"):
        st.session_state.xls_updated = True
    elif st.session_state.xls_updated:
        st.info("Өгөгдөл шинэчлэгдсэн, шинэ өгөгдлийг ачааллаж байна.")

    # COLOR BLIND CHECKBOX
    color_blind = st.checkbox("Accessibility mode")

    ### FIRST PATTERN FILL CHART###
    def plotly_chart():
        col3, col4 = st.columns([0.50, 0.50])

        
        st.sidebar.header("График fill тохиргоо")
        color_0 = st.sidebar.color_picker("0 - Үгүй утгын өнгө сонгох", "#648FFF")
        color_1 = st.sidebar.color_picker("1 - Тийм утгын өнгө сонгох", "#FE6100")
        pattern_0 = st.sidebar.selectbox("0 - Үгүй утгын хээ", ["/", "x", ".", "|", "-"], index=0)
        pattern_1 = st.sidebar.selectbox("1 - Тийм утгын хээ", ["x", "/", "|", "-", "."], index=1)
    
    
        xls_disease = pd.ExcelFile("disease_analysis_results 2.xlsx")
        k_sheets = [s for s in xls_disease.sheet_names if s.startswith('K')]

        with col3:
            selected_k_sheet = st.selectbox("\U0001F4D1 Хоол боловсруулах эрхтэн тогтолцооны өвчлөл сонгох (K...):", k_sheets, key="k_selection")

        df1 = pd.read_excel(xls_disease, sheet_name=selected_k_sheet)

        disease_columns_existing = []
    
        if df1.empty:
            st.warning("Энд өгөгдөл байхгүй байна.")
        else:
            first_col = df1.columns[0]
            df1[first_col] = df1[first_col].astype(str).str.strip().str.lower()
            values1 = df1[first_col]
        
            disease_columns = ['p_value', 'odds_ratio', 'adjusted_RR', 'ppv']
            disease_columns_existing = [col for col in disease_columns if col in df1.columns]

            xls = pd.ExcelFile("med_data_export.xlsx")
            matched_columns = []

            for sheet_name in xls.sheet_names:
                df2 = pd.read_excel(xls, sheet_name=sheet_name)
                if df2.empty:
                    continue

                for v in values1:
                    v_clean = v.strip().lower()
                    for col in df2.columns:
                        col_clean = col.strip().lower()
                        if v_clean in col_clean:
                            matched_columns.append((sheet_name, col))

            if matched_columns:
                with col3:
                    sheet_options = sorted(set([sheet for sheet, _ in matched_columns]))
                    selected_sheet = st.selectbox("Хамаарах хүснэгт сонгох:", sheet_options, key="table_selection")

                    filtered_columns = [col for sheet, col in matched_columns if sheet == selected_sheet]
                    selected_columns = st.multiselect("Графикаар харах багануудыг сонгох:", filtered_columns, default=filtered_columns[:3], key="selected_columns_disease_analysis")

                if selected_columns:
                    chart_df_list = []
                    for selected_column in selected_columns:
                        df_selected = pd.read_excel(xls, sheet_name=selected_sheet)
                        values = df_selected[selected_column].astype(str).str.strip()
                        counts = values.value_counts().sort_index()

                        chart_df = pd.DataFrame({
                            "Value": counts.index.astype(str),
                            "Count": counts.values,
                            "Column": [selected_column] * len(counts)
                        })

                        selected_column_clean = selected_column.strip().lower()
                        disease_row = df1[df1[first_col] == selected_column_clean]

                        if not disease_row.empty:
                            for col in disease_columns_existing:
                                chart_df[col] = disease_row[col].values[0]

                            chart_df_list.append(chart_df)

                    if chart_df_list:
                        final_df = pd.concat(chart_df_list, ignore_index=True)
        

                        with col3:
                            fig = px.bar(
                                final_df,
                                x="Column",
                                y="Count",
                                color="Value",
                                pattern_shape="Value",
                                pattern_shape_map={"0": pattern_0, "1": pattern_1},
                                color_discrete_map={"0": color_0, "1": color_1},
                                text="Count",
                                hover_data=["odds_ratio", "adjusted_RR", "p_value"],  # Hover дээр үзүүлэх нэмэлт мэдээлэл
                                title="K өвчний ач холбогдолт багана"
                            )
                            fig.update_layout(
                                barmode="stack", 
                                xaxis_title="Багана", 
                                yaxis_title="Тоо хэмжээ", 
                                height=500,
                                legend_title="Өвчин",
                                legend=dict(
                                    itemsizing='constant',
                                    title="Өвчин илрэл",
                                    # x=0.8, 
                                    # y=1,
                                    traceorder='normal',
                                    font=dict(family="Arial", size=12, color="black"),
                                    bgcolor="LightSteelBlue",
                                    bordercolor="Black",
                                    borderwidth=2
                                )
                            )
                            st.plotly_chart(fig, use_container_width=True)
                    else:
                        with col3:
                            st.warning("Сонгосон баганууд disease_analysis файлд таарахгүй байна.")
                else:
                    with col3:
                        st.warning("Багануудыг сонгоогүй байна, багана сонгох хэсгээс сонгоно уу!")
            else:
                with col3:
                    st.warning("Таарсан багана олдсонгүй.")

        with col4:
            st.markdown("Хоол боловсруулах өвчний BD_with_one_hot_diagnoses хүснэгтийн дата")

        excel_file = 'BD_with_one_hot_diagnoses.xlsx'
        if not os.path.exists(excel_file):
            st.error(f"'{excel_file}' файл олдсонгүй.")
        else:
            xls = pd.ExcelFile(excel_file)
            sheet_names = xls.sheet_names
            all_data = []

            for sheet in sheet_names:
                df = pd.read_excel(xls, sheet_name=sheet)
                k_columns = [col for col in df.columns if str(col).startswith("K")]

                for col in k_columns:
                    if set(df[col].dropna().unique()).issubset({0, 1}):
                        counts = df[col].value_counts().to_dict()
                        all_data.append({"sheet": sheet, "column": col, "column_id": f"{sheet} | {col}", "value": "0", "count": counts.get(0, 0)})
                        all_data.append({"sheet": sheet, "column": col, "column_id": f"{sheet} | {col}", "value": "1", "count": counts.get(1, 0)})

            if all_data:
                chart_df = pd.DataFrame(all_data)
                all_column_ids = sorted(chart_df['column_id'].unique())
                with col4:
                    selected_columns = st.multiselect("\U0001F4CC Баганууд сонгох (sheet | column)", options=all_column_ids, default=all_column_ids[:1], key="selected_colums_k_analysis")

                if selected_columns:
                    filtered_df = chart_df[chart_df['column_id'].isin(selected_columns)].copy()
                    filtered_df['value'] = filtered_df['value'].astype(str)

                    for col in disease_columns_existing:
                        # filtered_df[col] = filtered_df['column_id'].map(lambda x: df1[df1[first_col] == x][col].values[0] if not df1[df1[first_col] ==x].empty else None)
                        filtered_df.loc[:, col] = filtered_df['column'].str.strip().str.lower().map(
                            lambda col_name: df1[df1[first_col] == col_name][col].values[0]
                            if not df1[df1[first_col] == col_name].empty else None
                        )

                    with col4:
                        st.subheader("📊 Сонгосон багануудын Stacked Bar Chart")
                        fig2 = px.bar(
                            filtered_df,
                            x="column_id",
                            y="count",
                            color="value",
                            pattern_shape="value",
                            pattern_shape_map={"0": pattern_0, "1": pattern_1},
                            color_discrete_map={"0": color_0, "1": color_1},
                            text="count",
                            title="K өвчний BD_with_one_hot_diagnoses хүснэгтийн график"
                        )
                        fig2.update_layout(
                            barmode="stack", 
                            xaxis_title="Sheet | Багана", 
                            yaxis_title="Тоо хэмжээ", 
                            height=500,
                            legend_title="Өвчин",
                            legend=dict(
                                itemsizing='constant',
                                title="Өвчин илрэл",
                                traceorder='normal',
                                font=dict(family="Arial", size=12, color="black"),
                                bgcolor="LightSteelBlue",
                                bordercolor="Black",
                                borderwidth=2
                        )   
                        )
                        st.divider()
                        st.plotly_chart(fig2, use_container_width=True)
                else:
                    st.info("Эхлээд жагсаалтаас баганууд сонгоно уу.")
            else:
                st.warning("K-ээр эхэлсэн one-hot баганууд олдсонгүй.")
        
    
    ### SECOND CHART OPTION###
    def altair_chart():
        col3, col4 = st.columns([0.50, 0.50])
        col_graph1, col_graph2 = st.columns(2)

        # 📂 disease_analysis файлын sheet-үүдийг шалгах
        xls_disease = pd.ExcelFile("disease_analysis_results 2.xlsx")
        k_sheets = [s for s in xls_disease.sheet_names if s.startswith('K')]

        with col3:
            selected_k_sheet = st.selectbox("📑 Хоол боловсруулах эрхтэн тогтолцооны өвчлөл сонгох (K...):", k_sheets, key = "k_selection")

        # Сонгосон K sheet-ийг унших
        df1 = pd.read_excel(xls_disease, sheet_name=selected_k_sheet)

        # first_col баганын нэрийг шалгах
        if df1.empty:
            st.warning("Энд өгөгдөл байхгүй байна.")
        else:
            first_col = df1.columns[0]
            df1[first_col] = df1[first_col].astype(str).str.strip().str.lower()
            values1 = df1[first_col]  # values1 зөв үүсгэх

            # p, rr, or, ppv баганууд шалгах
            disease_columns = ['p_value', 'odds_ratio', 'adjusted_RR', 'ppv']
            disease_columns_existing = [col for col in disease_columns if col in df1.columns]

            # 📂 med_data файл унших
            xls = pd.ExcelFile("med_data_export.xlsx")
            matched_columns = []

            # Таарсан багануудыг хайх
            for sheet_name in xls.sheet_names:
                df2 = pd.read_excel(xls, sheet_name=sheet_name)

                # Хоосон sheet-ийг шалгах
                if df2.empty:
                    continue  # Хоосон sheet-ийг үл тооцно

                # Өгөгдлийг зөв цэвэрлэж, урд болон ард байгаа орон зайг устгах
                for v in values1:
                    v_clean = v.strip().lower()  
                    for col in df2.columns:
                        col_clean = col.strip().lower()  
                        if v_clean in col_clean:
                            matched_columns.append((sheet_name, col))

            # UI сонголтууд
            if matched_columns:
                with col3:
                    sheet_options = sorted(set([sheet for sheet, _ in matched_columns]))
                    selected_sheet = st.selectbox("Хамаарах хүснэгт сонгох:", sheet_options, key="table_selection")

                # with col4:
                    filtered_columns = [col for sheet, col in matched_columns if sheet == selected_sheet]
                    selected_columns = st.multiselect("Графикаар харах багануудыг сонгох:", filtered_columns, default=filtered_columns[:3])

                if selected_columns:
                    # бүх сонгогдсон багануудыг нэгэн зэрэг графикт харуулна
                    chart_df_list = []
                    for selected_column in selected_columns:
                        df_selected = pd.read_excel(xls, sheet_name=selected_sheet)
                        values = df_selected[selected_column].astype(str).str.strip()
                        counts = values.value_counts().sort_index()
                        
                        chart_df = pd.DataFrame({
                            "Value": counts.index,
                            "Count": counts.values,
                            "Column": [selected_column] * len(counts)
                        })
                
                        # 🎯 disease_analysis дээрээс утгуудыг олох
                        selected_column_clean = selected_column.strip().lower()
                        # disease_row = df1[df1[first_col] == selected_column_clean]
                        disease_row = df1[df1[first_col].str.strip().str.lower() == selected_column_clean]

                        if not disease_row.empty:
                            for col in disease_columns_existing:
                                # chart_df[col] = disease_row[col].values[0]
                                value = disease_row[col].values[0] if not disease_row[col].empty else None
                                chart_df[col] = value

                            chart_df_list.append(chart_df)  # Бүх багануудын графикийг жагсаалтад нэмэх

                    # Нийтлэн зурсан бүх графикуудыг нэг дор харуулах
                    if chart_df_list:
                        final_df = pd.concat(chart_df_list, ignore_index=True)

                        bar = alt.Chart(final_df).mark_bar(size=30).encode(
                            x=alt.X("Column:N", title="Багана"),
                            y=alt.Y("Count:Q", title="Тоо хэмжээ", stack='zero'),
                            color=alt.Color("Value:N", title="Утга", scale=alt.Scale(domain=['0', '1'], range=['#648FFF', '#DC267F'])),
                            tooltip=["Value", "Count"] + disease_columns_existing
                        )
                    
                        text = alt.Chart(final_df).mark_text(
                            align="center",
                            baseline="middle",
                            dx=0,
                            dy=5,
                            color="#FEFE62"
                        ).encode(
                            x=alt.X("Column:N", title="Багана"),
                            y=alt.Y("Count:Q", title="Тоо хэмжээ"),
                            detail="Value:N",
                            text=alt.Text("Count:Q")
                        )

                        chart = (bar+text).properties(
                            width='container',
                            height=400,
                            title="K өвчний ач холбогдолт багана"
                        )
        
                        # 1-Р ГРАФИК: disease_analysis үндэслэлтэй график
                        with col3:
                            st.divider()
                            # st.altair_chart(chart, use_container_width=True)
                    else:
                        with col3:
                            st.warning("Сонгосон баганууд disease_analysis файлд таарахгүй байна.")
                else:
                    with col3:
                        st.warning("Багануудыг сонгоогүй байна, багана сонгох хэсгээс сонгоно уу!")
            else:
                with col3:
                    st.warning("Таарсан багана олдсонгүй.")

        with col4:
            st.markdown("Хоол боловсруулах өвчний BD_with_one_hot_diagnoses хүснэгтийн дата")

        # Excel файл
        excel_file = 'BD_with_one_hot_diagnoses.xlsx'

        # Файл шалгах
        if not os.path.exists(excel_file):
            st.error(f"'{excel_file}' файл олдсонгүй.")
        else:
            xls = pd.ExcelFile(excel_file)
            sheet_names = xls.sheet_names

            all_data = []

            for sheet in sheet_names:
                df = pd.read_excel(xls, sheet_name=sheet)

                k_columns = [col for col in df.columns if str(col).startswith("K")]

                for col in k_columns:
                    if set(df[col].dropna().unique()).issubset({0, 1}):
                        counts = df[col].value_counts().to_dict()
                        all_data.append({
                            "sheet": sheet,
                            "column": col,
                            "column_id": f"{sheet} | {col}",
                            "value": "0",
                            "count": counts.get(0, 0)
                        })
                        all_data.append({
                            "sheet": sheet,
                            "column": col,
                            "column_id": f"{sheet} | {col}",
                            "value": "1",
                            "count": counts.get(1, 0)
                        })

            if all_data:
                chart_df = pd.DataFrame(all_data)

                # Multiselect: хэрэглэгч аль багануудыг харахыг сонгоно
                all_column_ids = sorted(chart_df['column_id'].unique())
                with col4:
                    selected_columns = st.multiselect(
                        "📌 Баганууд сонгох (sheet | column)",
                        options=all_column_ids,
                        default=all_column_ids[:1]  # эхний 1-г default сонгоно
                    )


                if selected_columns:
                    filtered_df = chart_df[chart_df['column_id'].isin(selected_columns)]

                    with col4:
                        st.subheader("📊 Сонгосон багануудын Stacked Bar Chart")
               
                    bar2 = alt.Chart(filtered_df).mark_bar(size=30).encode(
                        x=alt.X('column_id:N', title='Sheet | Багана', sort=None),
                        y=alt.Y('count:Q', title='Тоо ширхэг', stack='zero'),
                        color=alt.Color('value:N', title='Утга', scale=alt.Scale(domain=['0','1'], range=['#648FFF','#DC267F'])),
                        tooltip=['sheet', 'column', 'value', 'count']
                    )
                
                    text2 = alt.Chart(filtered_df).mark_text(
                        align="center",
                        baseline="middle",
                        dx=0,
                        dy=0,
                        color="#FEFE62",
                    ).encode(
                        x=alt.X("column_id:N"),
                        y=alt.Y("count:Q"),
                        detail="value:N",
                        text=alt.Text("count:Q")
                    )

                    chart2 = (bar2+text2).properties(
                        width='container',
                        height=400,
                        title="K өвчний BD_with_one_hot_diagnoses хүснэгтийн график"
                    )
              
                    # 2-Р ГРАФИК: one-hot багануудын stacked chart
                    # with col4:
                        # st.divider()
                        # st.altair_chart(chart2, use_container_width=True)
                    with col_graph1:
                        st.altair_chart(chart, use_container_width=True)
                    with col_graph2:
                        st.altair_chart(chart2, use_container_width=True)
                else:
                    st.info("Эхлээд жагсаалтаас баганууд сонгоно уу.")
            else:
                st.warning("K-ээр эхэлсэн one-hot баганууд олдсонгүй.")
        
        return


    if not color_blind:
        altair_chart()
    else: 
        plotly_chart()




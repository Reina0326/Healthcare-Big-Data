import streamlit as st
import pandas as pd 
import datetime
from PIL import Image
import plotly.graph_objects as go 
import altair as alt
from streamlit_autorefresh import st_autorefresh
import os

def show_descriptive_statistics():
    st.markdown('<style>div.block-container{padding-top:3rem;}</style>', unsafe_allow_html=True)
    image = Image.open('mnums.png')

    col1, col2 = st.columns([0.1,0.9])
    with col1:
        st.image(image,width=100)

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
    with col2:
        st.markdown(html_title, unsafe_allow_html=True)

        file_path = "med_data_export.xlsx"

    st_autorefresh(interval=60000, key="data_refresh")

    if  st.button("🔄 Шинэчлэх"):
        st.session_state.prev_mtime = 0
        st.rerun()    

    if "prev_mtime" not in st.session_state:
        st.session_state.prev_mtime = 0
    
    current_mtime = os.path.getmtime(file_path)
    
    if current_mtime != st.session_state.prev_mtime:
        xls = pd.ExcelFile(file_path)
        st.session_state.xls = xls
        st.session_state.prev_mtime = current_mtime
    else:
        xls = st.session_state.get("xls", pd.ExcelFile(file_path))

    EXCLUDE_SHEETS = {"user_information", "users", "insomnia_web", "isma_web"}

    col3, col4, col5 = st.columns([0.1,0.45,0.45])
    with col3:
        box_date = str(datetime.datetime.now().strftime("%d %B, %Y"))
        st.write(f"Last updated by: \n {box_date}")

    def get_sheets():
        return [sheet for sheet in xls.sheet_names if sheet not in EXCLUDE_SHEETS]

    def fetch_data(sheet_name):
        return pd.read_excel(xls, sheet_name=sheet_name)

    def descriptive_stats(df):
        df = df.drop(columns=["user_id"], errors="ignore")
        return df.describe().T

    def plot_stacked_bar(df, sheet_name):
        df = df.select_dtypes(include=['number']).drop(columns=["user_id"], errors="ignore")
        df = df.drop(columns=["Patient age"], errors="ignore")

        if df.empty:
            st.warning(f"'{sheet_name}' хүснэгтэд тоон өгөгдөл алга.")
            return

        counts = df.apply(lambda col: col.value_counts().reindex([0, 1], fill_value=0)).T
        counts = counts.reset_index().melt(id_vars="index", var_name="Value", value_name="Count")
        counts["Value"] = counts["Value"].map({0: "Үгүй", 1: "Тийм"})

        
        column_order = (
            counts[~counts["index"].isin(["Patient age"])]
            .groupby("index")["Count"]
            .sum()
            .sort_values(ascending=False)
            .index
            .tolist()
        )

        chart_type = st.radio("График төрөл сонгох:", ["Bar Chart", "Line Chart", "Scatter Plot"])
        color_blind = st.checkbox("Accessibility mode")

        if color_blind:
            st.sidebar.header("График fill тохиргоо")
            color_0 = st.sidebar.color_picker("0 - Үгүй утгын өнгө сонгох", "#648FFF")
            color_1 = st.sidebar.color_picker("1 - Тийм утгын өнгө сонгох", "#FE6100")
            pattern_0 = st.sidebar.selectbox("0 - Үгүй утгын хээ", ["/", "x", ".", "|", "-"], index=0)
            pattern_1 = st.sidebar.selectbox("1 - Тийм утгын хээ", ["x", "/", "|", "-", "."], index=1)
        

        height = len(counts["index"].unique())*25

        if not color_blind:
            if chart_type == "Bar Chart":
                bar = alt.Chart(counts).mark_bar(size=15).encode(
                    x=alt.X("Count:Q", title="Count"),
                    y=alt.Y("index:N", title="Columns", sort=column_order),
                    color=alt.Color("Value:N", scale=alt.Scale(domain=["Үгүй", "Тийм"], range=["#648FFF","#DC267F"])),
                    tooltip=["index", "Value", "Count"]
                )

                text = alt.Chart(counts).mark_text(
                    align="left",
                    baseline="middle",
                    dx=5, 
                    color="#FEFE62"
                ).encode(
                    x=alt.X("Count:Q"),
                    y=alt.Y("index:N", sort=column_order),
                    detail="Value:N",
                    text=alt.Text("Count:Q")
                )

                chart = (bar+text).properties(
                    width=1000,
                    height=height,
                    title=f"{sheet_name}-Хүснэгтийн график"
                ).configure_view(
                    strokeWidth=0.1
                ).interactive()

                st.altair_chart(chart, use_container_width=True)
            elif chart_type == "Line Chart":
                chart = alt.Chart(counts).mark_line(point=True).encode(
                    x=alt.X("Count:Q", title="Count"),
                    y=alt.Y("index:N", title="Columns", sort="-x"),
                    color=alt.Color("Value:N", scale=alt.Scale(domain=["Үгүй","Тийм"], range=["#648FFF","#DC267F"])),
                    tooltip=["index","Value","Count"]
                ).properties(
                    width=1000,
                    height=height,
                    title=f"{sheet_name} - хүснэгтийн график"
                ).interactive()
    
                st.altair_chart(chart, use_container_width=True)

            else:
                chart = alt.Chart(counts).mark_circle(size=60).encode(
                    x=alt.X("Count:Q", title="Count"),
                    y=alt.Y("index:N", title="Columns", sort="-x"),
                    color=alt.Color("Value:N", scale=alt.Scale(domain=["Үгүй","Тийм"], range=["#648FFF","#DC267F"])),
                    tooltip=["index","Value","Count"]
                ).interactive()

                st.altair_chart(chart, use_container_width=True)
        else:
            import plotly.express as px

            fig = go.Figure()
            values = ["Тийм", "Үгүй"]  
            patterns = [pattern_1, pattern_0]
            colors = [color_1, color_0]

            for val, pattern, color in zip(values, patterns, colors):
                subset = counts[counts["Value"] == val]
                subset = subset.set_index("index").reindex(column_order).reset_index()
                fig.add_bar(
                    y=subset["index"],
                    x=subset["Count"],
                    name=val,
                    orientation='h',
                    marker=dict(
                        color=color,
                        pattern=dict(shape=pattern
                                     )
                    )
                )

            fig.update_layout(
                barmode="stack",
                title=f"{sheet_name} - Pattern Fill Graph",
                height=height + 200,
                yaxis=dict(categoryorder="array", categoryarray=column_order[::-1]),
                xaxis_title="Count",
                yaxis_title="Columns"
            )
            st.plotly_chart(fig, use_container_width=True)

    st.title("Эрүүл мэндийн их өгөгдлийн Descriptive Statistics")
    sheets = get_sheets()
    selected_sheet = st.selectbox("Асуулгаас сонгох", sheets, key="desc_sheet")

    if selected_sheet:
        with col4:
            with st.expander("Өгөгдлийн хүснэгтийг харах"):
                data = fetch_data(selected_sheet)
                st.write("### Өгөгдөл", data.head())

        with col5:
            with st.expander("Descriptive Statistics -ийн хүснэгтийг харах"):
                stats = descriptive_stats(data)
                st.write("### Descriptive Statistics", stats)

        plot_stacked_bar(data, selected_sheet)



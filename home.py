import streamlit as st
import pandas as pd
from openpyxl import load_workbook
from streamlit_elements import elements, mui, nivo, dashboard

def level_diseace():

    with elements("new_elements"):
        mui.Typography(
          "Хүн амын эрүүл мэндийн их өгөгдөл",
          variant = "h3",
          align = "center",
          sx={
            "fontWeight": "bold"
          }
        )


    def assign_isma_description(row_sum):

        if row_sum <= 4:
            counter["minimum"] += 1
            return "Стрессээр өвчлөх магадлал бага"
        elif row_sum < 14:
            counter["middle"] += 1 
            return "Стресстэй холбоотой эрүүл мэнд, сэтгэц, бие махбодын өвчин тусах магадлал өндөр."
        else:
            counter["high"] += 1
            return "Таны стрессийн түвшин маш өндөр байна."

    def assign_isi_description(row_sum):

        if row_sum <= 7:
            counter["minimum"] += 1
            return "Нойргүйдэл байхгүй"
        elif row_sum <= 14:
            counter["middle"] += 1
            return "Нойргүйдэл бага зэрэг"
        elif row_sum <= 21:
            counter["high"] += 1
            return "Дунд зэрэг нойргүйдэлтэй"
        else:
            counter["very_high"] += 1
            return "Нойргүйдлийн зэрэг хүнд явцтай" 

    def assign_chronic_fatigue_description(row_sum):

        if row_sum <= 10:
            counter["minimum"] += 1
            return "Архаг ядаргаагүй"
        elif row_sum <= 24:
            counter["middle"] += 1
            return "Бага зэргийн ядралттай"
        elif row_sum <= 51:
            counter["high"] += 1
            return "Дунд зэргийн ядралттай"
        else:
            counter["very_high"] += 1
            return "Хүнд хэлбэрийн ядралттай"
    
    pd.set_option('future.no_silent_downcasting', True)
    try:
        file_path = "med_data_export.xlsx"
        wb = load_workbook(filename=file_path, data_only=True)
    
        sheets = ["isma","isi","chronic_fatigue"]
        dfs = {}

        for sheet in sheets:
            ws = wb[sheet]
            data = ws.values
            columns = next(data)
            df = pd.DataFrame(data, columns=columns)

            df.columns = df.columns.str.strip()
    
            df["Row of Sum"] = df.drop('user_id', axis=1).sum(axis=1,numeric_only=True)
            df = df[df["Row of Sum"] != 0]
            dfs[sheet] = df

    except Exception as e:
        print(f"Excel-ээс уншихад алдаа гарлаа:{e}")

    pie_data = {}

    for sheet in sheets:
        df = dfs[sheet]
        
        
        counter = {
        "minimum": 0,
        "middle": 0,
        "high": 0, 
        "very_high": 0
        }

        if sheet == "isma":
            df['Тайлбар'] = df["Row of Sum"].apply(assign_isma_description)
        elif sheet == "isi":
            df['Тайлбар'] = df["Row of Sum"].apply(assign_isi_description)
        elif sheet == "chronic_fatigue":
            df["Тайлбар"] = df["Row of Sum"].apply(assign_chronic_fatigue_description)

        parts = len(df["Row of Sum"])
        pie_data[sheet] = {
            "Магадлал бага": counter["minimum"],
            "Магадлал дунд": counter["middle"],
            "Магадлал их": counter["high"],
            "Маш өндөр": counter["very_high"],
            "parts": parts
        }

    layout = [
        dashboard.Item("isma_chart", 0,0,4,4),

        dashboard.Item("isi_chart",4,0,4,4),

        dashboard.Item("chronic_chart",8,0,4,4),
    ]

    DATA = [
        {"id": "Магадлал бага", "value": pie_data["isma"]["Магадлал бага"]},
        {"id": "Магадлал дунд", "value": pie_data["isma"]["Магадлал дунд"]},
        {"id": "Магадлал их", "value": pie_data["isma"]["Магадлал их"]}
    ]

    col1, col2 = st.columns([0.50, 0.50])
    with elements("dashboard"):
        with dashboard.Grid(layout, draggable=False, resizable=False):
            with col1:
                nivo.Pie(
                    key="isma_chart",
                    data = [
                        {"id": "Стрессийн түвшин - Магадлал бага", "value": pie_data["isma"]["Магадлал бага"]},
                        {"id": "Стрессийн түвшин - Магадлал дунд", "value": pie_data["isma"]["Магадлал дунд"]},
                        {"id": "Стрессийн түвшин - Магадлал их", "value": pie_data["isma"]["Магадлал их"]}
                    ],
                    margin={"top": 40, "right": 80, "bottom": 80, "left": 80},
                    innerRadius=0.1,
                    padAngle=0.7,
                    cornerRadius=3,
                    legends=[
                        {
                            "anchor": "bottom",           # Тайлбарын байрлал: top / bottom / left / right
                            "direction": "column",           # row эсвэл column
                            "translateY": 56,             # Доош түлхэх хэмжээ
                            "itemWidth": 100,
                            "itemHeight": 18,
                            "itemTextColor": "#999",
                            "symbolSize": 18,
                            "symbolShape": "circle",      # square, circle, diamond
                        }
                    ]
                )

            nivo.Pie(
                key="isi_chart",
                data=[
                    {"id": "Нойргүйдлийн түвшин - Магадлал бага", "value": pie_data["isi"]["Магадлал бага"]},
                    {"id": "Нойргүйдлийн түвшин - Магадлал дунд", "value": pie_data["isi"]["Магадлал дунд"]},
                    {"id": "Нойргүйдлийн түвшин - Магадлал их", "value": pie_data["isi"]["Магадлал их"]},
                    {"id": "Нойргүйдлийн түвшин - Маш өндөр", "value": pie_data["isi"]["Маш өндөр"]}
                ],
                margin={"top": 40, "right": 80, "bottom": 80, "left": 80},
                innerRadius=0.5,
                padAngle=0.7,
                cornerRadius=3,
                enableArcLinkLabels=True,
                arcLinkLabel="id",
                arcLinkLabelsSkipAngle=10,
                arcLinkLabelsDiagonalLength=12,
                arcLinkLabelsStraightLength=8,
                arcLinkLabelsTextOffset=6,
                arcLinkLabelsTextColor="black",
                arcLinkLabelsThickness=1,
                arcLinkLabelColor={"from": "color"},
                legends=[
                    {
                        "anchor": "bottom",           # Тайлбарын байрлал: top / bottom / left / right
                        "direction": "column",           # row эсвэл column
                        "translateY": 56,             # Доош түлхэх хэмжээ
                        "itemWidth": 100,
                        "itemHeight": 18,
                        "itemTextColor": "#999",
                        "symbolSize": 18,
                        "symbolShape": "circle",      # square, circle, diamond
                    }
                ]

            )
            nivo.Pie(
                key="chronic_chart",
                    data=[
                        {"id": "Архаг ядаргаа - Магадлал бага", "value": pie_data["chronic_fatigue"]["Магадлал бага"]},
                        {"id": "Архаг ядаргаа - Магадлал дунд", "value": pie_data["chronic_fatigue"]["Магадлал дунд"]},
                        {"id": "Архаг ядаргаа - Магадлал их", "value": pie_data["chronic_fatigue"]["Магадлал их"]},
                        {"id": "Архаг ядаргаа - Маш өндөр", "value": pie_data["chronic_fatigue"]["Маш өндөр"]}
                    ],
                    margin={"top": 40, "right": 80, "bottom": 80, "left": 80},
                    innerRadius=0.5,
                    padAngle=0.7,
                    cornerRadius=3,
                    enableArcLinkLabels=True,
                    arcLinkLabel="id",
                    arcLinkLabelsSkipAngle=10,
                    arcLinkLabelsDiagonalLength=12,
                    arcLinkLabelsStraightLength=8,
                    arcLinkLabelsTextOffset=6,
                    arcLinkLabelsTextColor="black",
                    arcLinkLabelsThickness=1,
                    arcLinkLabelColor={"from": "color"},
                    legends=[
                    {
                        "anchor": "bottom",           # Тайлбарын байрлал: top / bottom / left / right
                        "direction": "column",           # row эсвэл column
                        "translateY": 56,             # Доош түлхэх хэмжээ
                        "itemWidth": 100,
                        "itemHeight": 18,
                        "itemTextColor": "#999",
                        "symbolSize": 18,
                        "symbolShape": "circle",      # square, circle, diamond
                    }
                ]
            )



   



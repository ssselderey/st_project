import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
from io import BytesIO

st.set_page_config(page_title="Анализ Apple и чаевых", layout="wide")

st.title("Анализ данных о котировках Apple и исследование по чаевым")

# боковая настройка
st.sidebar.header("Настройки")

# загружаем данные Apple
st.sidebar.subheader("Данные Apple AAPL")
period = st.sidebar.selectbox("Выберите период для данных Apple", options=["1mo", "3mo", "6mo", "1y", "2y", "5y"], index=3)
interval = st.sidebar.selectbox("Интервал данных", options=["1d", "1wk", "1mo"], index=0)

@st.cache_data
def apple_data(period, interval):
    data = yf.download("AAPL", period=period, interval=interval)
    data.reset_index(inplace=True)
    #проверяем, есть ли MultiIndex по столбцам сброс
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = ['_'.join(col).strip('_') for col in data.columns.values]
    return data

apple_data_new = apple_data(period, interval)

# показываем датафрейм Apple и какие есть колонки в нем
st.write("Данные Apple", apple_data_new.tail())
st.write("Колонки apple_data:", apple_data_new.columns.tolist())

# визуал графиков и пояснения
st.subheader("График котировок Apple - ")
st.write(" это визуальное отображение изменения цены акций компании Apple (AAPL) на фондовом рынке за определённый период времени.")
st.write("График котировок показывает, как цена менялась за последние дни, недели или месяцы. На графике по оси X откладывается время (дата, часы), а по оси Y — цена акции.")

#берем колонки Date и Close_AAPL цена закрытия
fig_apple = px.line(apple_data_new, x='Date', y='Close_AAPL', title='Цена закрытия AAPL')
st.plotly_chart(fig_apple, use_container_width=True)

# добавляем кнопку для скачивания графика в формате png
img_bytes = fig_apple.to_image(format="png")
st.sidebar.download_button(
    label="Скачать график котировок Apple",
    data=img_bytes,
    file_name="apple_price.png",
    mime="image/png"
)

# загружаем tips.csv
st.sidebar.subheader("Загрузка вашего CSV (tips.csv)")
uploaded_file = st.sidebar.file_uploader("Загрузите CSV файл", type=['csv'])

if uploaded_file is not None:
    tips_df = pd.read_csv(uploaded_file)
    st.write("Данные из загруженного CSV файла:", tips_df.head())
    st.subheader("График чаевых vs счета")

    # проверяем колонки
    if {'total_bill', 'tip'}.issubset(tips_df.columns):
        fig_tips = px.scatter(tips_df, x='total_bill', y='tip', color='sex', color_discrete_map={'Male': "#5649E0", 'Female': "#df4ac6"}, title='Чаевые в зависимости от счета')
        st.plotly_chart(fig_tips, use_container_width=True)

        # создаем кнопку для скачивания графика
        img_tips_bytes = fig_tips.to_image(format="png")
        st.sidebar.download_button(
            label="Скачать график чаевых",
            data=img_tips_bytes,
            file_name="tips_scatter.png",
            mime="image/png"
        )
    else:
        st.warning("В загруженном файле отсутствуют колонки 'total_bill' и 'tip' для визуализации.")
else:
    st.info("Загрузите CSV-файл с данными чаевых, чтобы увидеть графики.")

import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import style
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

@st.cache_data()
def apple_data(period, interval):
    data = yf.download("AAPL", period=period, interval=interval, threads=False)
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
st.subheader("График котировок Apple")
st.write(" это визуальное отображение изменения цены акций компании Apple (AAPL) на фондовом рынке за определённый период времени.")
st.write("""
График котировок отображает изменение цены акций Apple (AAPL) на фондовом рынке.
По оси X — дата, по оси Y — цена закрытия.
""")

#берем колонки Date и Close_AAPL цена закрытия

plt.style.use('dark_background')
fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(apple_data_new['Date'], apple_data_new['Close_AAPL'], color='#5C59C5', linewidth=2.5, label='Цена закрытия')

ax.set_facecolor('#1e1e1e')
fig.patch.set_facecolor('#1e1e1e')
ax.set_title("Цена закрытия AAPL", fontsize=16, color='white', pad=15)
ax.set_xlabel("Дата", fontsize=12, color='white')
ax.set_ylabel("Цена $", fontsize=12, color='white')
ax.tick_params(colors='white')
ax.grid(True, linestyle='--', alpha=0.3)
ax.legend(facecolor='#2e2e2e', edgecolor='white')


st.pyplot(fig)


# добавляем кнопку для скачивания графика в формате png
buf = BytesIO()
fig.savefig(buf, format="png", facecolor=fig.get_facecolor())
st.sidebar.download_button(
    label="Скачать график (PNG)",
    data=buf.getvalue(),
    file_name="apple_chart.png",
    mime="image/png"
)

plt.close(fig)

# загружаем tips.csv
st.sidebar.subheader("Загрузка вашего CSV (tips.csv)")
uploaded_file = st.sidebar.file_uploader("Загрузите CSV файл", type=['csv'])

if uploaded_file is not None:
    tips_df = pd.read_csv(uploaded_file)

    st.subheader("Данные по чаевым")
    st.dataframe(tips_df.head(), use_container_width=True)

    if {'total_bill', 'tip', 'sex'}.issubset(tips_df.columns):
        st.subheader("График: Чаевые vs Счёт")

        fig_tips = px.scatter(
            tips_df,
            x='total_bill',
            y='tip',
            color='sex',
            title='Чаевые в зависимости от счёта',
            color_discrete_map={'Male': "#5649E0", 'Female': "#df4ac6"},
            template='plotly_dark'
        )

        st.plotly_chart(fig_tips, use_container_width=True)

        st.sidebar.info("График Plotly не сохраняется как PNG из-за ограничений среды.\n\nМожно сохранить как изображение вручную (иконка в правом верхнем углу графика).")
    else:
        st.warning("В файле должны быть колонки 'total_bill', 'tip' и 'sex'.")
else:
    st.info("Загрузите CSV-файл с чаевыми для визуализации.")

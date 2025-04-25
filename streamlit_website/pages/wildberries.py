import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import requests
import os
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="Wildberries Аналитика", layout="wide")
primary_color = "#5a188a"

st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display:none;}
    </style>
    """, unsafe_allow_html=True)
st.markdown(
    f"<h1 style='text-align:center; color:{primary_color}'>Wildberries Аналитика</h1>",
    unsafe_allow_html=True
)

with st.form("user_form"):
    req_type = st.selectbox(
        "Тип запроса",
        ("Поиск", "Категория", "Продавец"),
        help="Выберите тип запроса"
    )
    if req_type == "Поиск":
        query_text = st.text_input("Текст запроса", placeholder="Введите ключевые слова для поиска")
    else:
        query_text = st.text_input("Ссылка", placeholder="Вставьте ссылку на категорию или продавца")

    num = st.number_input(
        "Количество результатов",
        min_value=1, max_value=1000, value=100, step=1,
        help="Сколько товаров загрузить"
    )

    order = st.selectbox(
        "Порядок сортировки",
        ("По популярности", "Сначала дешевые", "Сначала дорогие", "По рейтингу", "По новинкам")
    )

    submit = st.form_submit_button("ЗАПРОСИТЬ")

endpoints = {
    "Поиск": "api/v1/wildberries/search",
    "Категория": "api/v1/wildberries/category",
    "Продавец": "api/v1/wildberries/seller"
}
endpoint = endpoints[req_type]

if req_type == "Поиск":
    params = {
        "text": query_text,
        "num": int(num),
        "order": order
    }
else:
    params = {
        "link": query_text,
        "num": int(num),
        "order": order
    }

def fetch_api(url, params):
    try:
        response = requests.post(url, json=params, timeout=60)
        if response.status_code == 200:
            return response.json(), None
        return None, f"Ошибка API {response.status_code}: {response.text}"
    except Exception as e:
        return None, f"Ошибка соединения: {e}"

if submit:
    api_url = f"http://{os.getenv('API_GATEWAY_HOST')}:{os.getenv('API_GATEWAY_PORT')}/{endpoint}"
    with st.spinner("Загружаем данные..."):
        result, error = fetch_api(api_url, params)
    if error:
        st.error(error)
    elif result and result.get("data"):
        data = result["data"]
        filename = result.get("filename") or "data"
        df = pd.DataFrame(data)
        rename_map = {
            "product_id": "ProductId",
            "name": "Name",
            "brand": "Brand",
            "price": "Price",
            "discount_price": "DiscountPrice",
            "rating": "Rating",
            "reviews": "Reviews"
        }
        df = df.rename(columns=rename_map)
        
        st.success(f"✅ Получен файл: **{filename}**. Всего позиций: {len(df)}")

        st.markdown("### 📊 Аналитика по брендам")
        col1, col2, col3 = st.columns(3)

        with col1:
            top_brands = df["Brand"].fillna("НетБренда").value_counts().nlargest(10)
            plt.figure(figsize=(5, 4))
            top_brands.plot(kind="bar", color=primary_color)
            plt.title("ТОП-10 брендов (товары)")
            plt.ylabel("Количество товаров")
            plt.xticks(rotation=45, ha='right')
            st.pyplot(plt)
            plt.clf()

        with col2:
            mean_prices = (
                df[['Brand', 'Price']]
                .assign(Price=pd.to_numeric(df['Price'], errors='coerce'))
                .groupby("Brand")["Price"]
                .mean()
                .fillna(0)
                .sort_values(ascending=False)
                .head(10)
            )
            plt.figure(figsize=(5, 4))
            mean_prices.plot(kind="bar", color=primary_color)
            plt.title("Средняя цена (ТОП-10 брендов)")
            plt.ylabel("Средняя цена")
            plt.xticks(rotation=45, ha='right')
            st.pyplot(plt)
            plt.clf()

        with col3:
            top_reviews = (
                df[['Brand', 'Reviews']]
                .assign(Reviews=pd.to_numeric(df['Reviews'], errors='coerce'))
                .groupby("Brand")["Reviews"]
                .sum()
                .fillna(0)
                .sort_values(ascending=False)
                .head(10)
            )
            plt.figure(figsize=(5, 4))
            top_reviews.plot(kind="bar", color=primary_color)
            plt.title("Отзывы (ТОП-10 брендов)")
            plt.ylabel("Количество отзывов")
            plt.xticks(rotation=45, ha='right')
            st.pyplot(plt)
            plt.clf()

        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Скачать CSV",
            data=csv,
            file_name=f"{filename}.csv",
            mime="text/csv",
            use_container_width=True
        )

        st.markdown("### 📄 Все товары")
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.warning("Нет данных по вашему запросу или API вернул пустой результат.")
else:
    st.info("Введите условия запроса и нажмите **ЗАПРОСИТЬ**.")


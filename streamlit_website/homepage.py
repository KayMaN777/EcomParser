import streamlit as st
from styles import style
from components import WB_SVG, OZON_SVG, YM_SVG, ADV1, ADV2, ADV3

st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    .st-emotion-cache-18ni7ap {display: none;}
    .stDeployButton {display:none;}
    .stActionButtonIcon {display: none;}
    </style>
""", unsafe_allow_html=True)

st.markdown(style, unsafe_allow_html=True)

st.markdown('<div class="main-title">E-com parser</div>', unsafe_allow_html=True)
st.markdown(
    '''<div class="main-subtitle">
    Хотите увеличить продажи? Не знаете, какой товар выбрать для реализации на маркетплейсе?<br>
    Решение есть — самое время задуматься о конкурентном анализе и изучить свободные ниши.
    </div>''', unsafe_allow_html=True)

st.markdown('<div class="marketplaces-title">Работаем с популярными маркетплейсами</div>', unsafe_allow_html=True)
st.markdown(f'''
    <div class="markets-row">
      <span class="market-ic-box">{WB_SVG}</span>
      <span class="market-ic-box">{OZON_SVG}</span>
      <span class="market-ic-box">{YM_SVG}</span>
    </div>
''', unsafe_allow_html=True)

st.markdown('<div class="section-adv">', unsafe_allow_html=True)
st.markdown('<div class="adv-title">Наши преимущества</div>', unsafe_allow_html=True)
st.markdown(
    '''<div class="adv-text">В современном мире, где интернет-торговля стремительно развивается, конкуренция между
онлайн-магазинами достигает невиданных масштабов. Покупатели становятся все более требовательными, а рынок насыщается новыми игроками и рекламными предложениями. Чтобы выйти на новый уровень, важно уметь анализировать конкурентов и контролировать ассортимент. Мы предоставляем удобные инструменты для сбора и анализа данных с популярных маркетплейсов: Wildberries, Ozon и Яндекс.Маркет. Наш сервис отличается скоростью, доступностью и удобством для всех пользователей.</div>''', unsafe_allow_html=True
)

st.markdown(f'''
    <div class="adv-row">
        <div class="adv-item">
            {ADV1}
            <div class="adv-item-title">Высокая производительность</div>
            <div class="adv-item-desc">Наш сервис анализирует тысячи товаров на маркетплейсах максимально быстро</div>
        </div>
        <div class="adv-item">
            {ADV2}
            <div class="adv-item-title">Доступность</div>
            <div class="adv-item-desc">Ищите и сравнивайте товары с любого устройства, в любое время и из любой точки</div>
        </div>
        <div class="adv-item">
            {ADV3}
            <div class="adv-item-title">Удобство</div>
            <div class="adv-item-desc">Интуитивный интерфейс даже для новичков. Получайте отчеты и аналитику в пару кликов!</div>
        </div>
    </div>
''', unsafe_allow_html=True)
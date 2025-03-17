import streamlit as st
import yahooquery as yq
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

symbols = ["ALL", "VIV", "SAN", "NMS", "AMD"]

def get_stock_data(symbol, period):
    stock = yq.Ticker(symbol)
    hist = stock.history(period=period).reset_index()
    return hist

def get_financials(symbol):
    stock = yq.Ticker(symbol)
    return stock.summary_detail.get(symbol, {})

def get_current_price(symbol):
    stock = yq.Ticker(symbol)
    return stock.price.get(symbol, {}).get("regularMarketPrice", "N/A")

def get_previous_close(symbol):
    stock = yq.Ticker(symbol)
    return stock.price.get(symbol, {}).get("regularMarketPreviousClose", "N/A")

st.set_page_config(layout="wide", page_title="Dashboard Financeiro Interativo")
st.title("📊 Dashboard Financeiro Interativo")

st.sidebar.header("🔍 Configurações")

time_periods = {"1 mês": "1mo", "3 meses": "3mo", "6 meses": "6mo", "1 ano": "1y", "5 anos": "5y"}
selected_period = st.sidebar.selectbox("Selecione o período histórico", list(time_periods.keys()), index=3)

graph_type = st.sidebar.selectbox("Selecione o tipo de gráfico", ["Linha", "Candlestick"])

if graph_type == "Candlestick":
    selected_stock = st.sidebar.selectbox("Selecione uma empresa", symbols)
    selected_stocks = [selected_stock]
else:
    selected_stocks = st.sidebar.multiselect("Selecione as empresas para comparação", symbols, default=symbols)

price_data = {stock: get_current_price(stock) for stock in symbols}
previous_close_data = {stock: get_previous_close(stock) for stock in symbols}

for stock in symbols:
    current_price = price_data.get(stock, "N/A")
    previous_close = previous_close_data.get(stock, "N/A")
    
    if isinstance(current_price, (int, float)) and isinstance(previous_close, (int, float)):
        if current_price > previous_close:
            color = "#28a745"
        elif current_price < previous_close:
            color = "#dc3545"
        else:
            color = "#ffc107"
    else:
        color = "#6c757d"
    
    st.sidebar.markdown(f"<span style='color: {color}; font-weight: bold;'>{stock}: ${current_price}</span>", unsafe_allow_html=True)

st.subheader("📉 Comparação de Preços de Fechamento")
all_data = []
for stock in selected_stocks:
    data = get_stock_data(stock, time_periods[selected_period])
    if not data.empty:
        data["Stock"] = stock
        all_data.append(data)

if all_data:
    df_combined = pd.concat(all_data, ignore_index=True)
    
    color_map = {
        "AMD": "#FF0000",
        "ALL": "#0000FF",
        "VIV": "#800080",
        "SAN": "#FFA500",
        "NMS": "#008080"
    }
    
    if graph_type == "Linha":
        fig = px.line(
            df_combined, 
            x="date", 
            y="close", 
            color="Stock", 
            title=f"Comparação de Preços de Fechamento - {selected_period}",
            color_discrete_map=color_map
        )
    else:
        stock = selected_stocks[0]
        stock_data = df_combined[df_combined["Stock"] == stock]
        fig = go.Figure()
        fig.add_trace(go.Candlestick(
            x=stock_data["date"],
            open=stock_data["open"],
            high=stock_data["high"],
            low=stock_data["low"],
            close=stock_data["close"],
            name=stock,
            increasing_line_color='green',
            decreasing_line_color='red'
        ))
        fig.update_layout(title=f"Gráfico Candlestick - {selected_period}", xaxis_title="Data", yaxis_title="Preço")
    
    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("Não foi possível obter dados históricos.")

st.subheader("📊 Resumo Financeiro das Empresas Selecionadas")
cols = st.columns(len(selected_stocks))
for col, stock in zip(cols, selected_stocks):
    with col:
        st.markdown(f"### {stock}")
        financials = get_financials(stock)
        if financials:
            df_financials = pd.DataFrame.from_dict(financials, orient='index', columns=["Valor"])
            st.dataframe(df_financials, height=400)
        else:
            st.warning(f"Não foi possível obter os dados financeiros de {stock}.")

st.write("Feito por: Ana, Eduardo, Higor e Jhonatan")
st.write("BIG DATA FOR FINANCE PROJECT")
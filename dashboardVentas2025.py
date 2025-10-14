import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go # Import graph_objects for potential future use or if needed for specific chart types

# --- Data Loading ---
# In a real Streamlit app, you might upload the file or read from a more persistent storage
file_path = 'Orders Final.xlsx'
try:
    df_orders = pd.read_excel(file_path)
    st.success("Data loaded successfully!")
except FileNotFoundError:
    st.error(f"Error: File not found at {file_path}. Please make sure the file is in the correct location.")
    st.stop() # Stop the app if data loading fails

# --- Data Processing ---
# Group by Product Name and sum Sales
product_sales = df_orders.groupby('Product Name')['Sales'].sum().sort_values(ascending=False)

# Select the top 5 products (adjust n as needed)
top_n_sales = 5
top_sales_products = product_sales.head(top_n_sales)

# Group by Product Name and sum Profit
product_profit = df_orders.groupby('Product Name')['Profit'].sum().sort_values(ascending=False)

# Select the top 5 products with the highest profit (adjust n as needed)
top_n_profit = 5
top_profit_products = product_profit.head(top_n_profit)


# --- Visualization ---

st.title("Product Performance Analysis")

# Plotly Express bar chart for Top Selling Products
fig_sales = px.bar(top_sales_products, x=top_sales_products.index, y=top_sales_products.values,
             labels={'x':'Product Name', 'y':'Total Sales'},
             title=f'Top {top_n_sales} Best-Selling Products')
fig_sales.update_layout(xaxis_tickangle=-90) # Rotate labels for readability

st.plotly_chart(fig_sales, use_container_width=True)


# Plotly Express bar chart for Top Profit Products
fig_profit = px.bar(top_profit_products, x=top_profit_products.index, y=top_profit_products.values,
                    labels={'x':'Product Name', 'y':'Total Profit'},
                    title=f'Top {top_n_profit} Products by Profit')
fig_profit.update_layout(xaxis_tickangle=-90) # Rotate labels for readability

st.plotly_chart(fig_profit, use_container_width=True)

# You can add more visualizations or analysis here for your Streamlit app
# For example, you could add charts for sales/profit by category, region, etc.

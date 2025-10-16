import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# --- Data Loading ---
file_path = 'Orders Final.xlsx'
try:
    df_orders = pd.read_excel(file_path)
    st.success("Data loaded successfully!")
except FileNotFoundError:
    st.error(f"Error: File not found at {file_path}. Please make sure the file is in the correct location.")
    st.stop() # Stop the app if data loading fails

# --- Helper Function for Text Wrapping ---
def wrap_text(text, width):
    words = text.split()
    lines = []
    current_line = []
    for word in words:
        if len(" ".join(current_line + [word])) <= width:
            current_line.append(word)
        else:
            lines.append(" ".join(current_line))
            current_line = [word]
    if current_line:
        lines.append(" ".join(current_line))
    return "<br>".join(lines)

# --- Streamlit App Layout and Filtering ---
st.title("Product Performance Analysis")

st.sidebar.header("Filters")

# Add a region filter in the sidebar
regions = df_orders['Region'].unique().tolist()
regions.insert(0, "Todas") # Add "Todas" option at the beginning

selected_region = st.sidebar.selectbox("Select Region", regions)

# Filter data based on selected region
if selected_region == "Todas":
    filtered_df = df_orders
else:
    filtered_df = df_orders[df_orders['Region'] == selected_region]

# Add a state filter in the sidebar, dependent on the selected region
states = filtered_df['State'].unique().tolist()
states.insert(0, "Todas") # Add "Todas" option at the beginning

selected_state = st.sidebar.selectbox("Select State", states)

# Further filter data based on selected state
if selected_state != "Todas":
    filtered_df = filtered_df[filtered_df['State'] == selected_state]

# Add a checkbox to show/hide the filtered DataFrame
show_dataframe = st.checkbox("Show Filtered Data")

# Conditionally display the filtered DataFrame
if show_dataframe:
    st.write("Filtered Data:")
    st.dataframe(filtered_df)

# --- Data Processing on Filtered Data ---
# Group by Product Name and sum Sales
product_sales = filtered_df.groupby('Product Name')['Sales'].sum().sort_values(ascending=False)

# Select the top 5 products (adjust n as needed)
top_n_sales = 5
top_sales_products = product_sales.head(top_n_sales)

# Group by Product Name and sum Profit
product_profit = filtered_df.groupby('Product Name')['Profit'].sum().sort_values(ascending=False)

# Select the top 5 products with the highest profit (adjust n as needed)
top_n_profit = 5
top_profit_products = product_profit.head(top_n_profit)

# --- Visualization ---

# Plotly Graph Objects bar chart for Top Selling Products with wrapped labels
sales_product_data = list(top_sales_products.items())
wrapped_sales_product_names = [wrap_text(name, 20) for name, sales in sales_product_data] # Adjust width as needed

fig_sales = go.Figure(data=[go.Bar(x=wrapped_sales_product_names, y=[sales for name, sales in sales_product_data])])

fig_sales.update_layout(
    title=f'Top {top_n_sales} Best-Selling Products ({selected_region}, {selected_state})',
    xaxis_title='Product Name',
    yaxis_title='Total Sales',
    xaxis_tickangle=0 # Set tick angle back to 0 since we are wrapping
)

st.plotly_chart(fig_sales, use_container_width=True)

# Plotly Graph Objects bar chart for Top Profit Products with wrapped labels
profit_product_data = list(top_profit_products.items())
wrapped_profit_product_names = [wrap_text(name, 20) for name, profit in profit_product_data] # Adjust width as needed

fig_profit = go.Figure(data=[go.Bar(x=wrapped_profit_product_names, y=[profit for name, profit in profit_product_data])])

fig_profit.update_layout(
    title=f'Top {top_n_profit} Products by Profit ({selected_region}, {selected_state})',
    xaxis_title='Product Name',
    yaxis_title='Total Profit',
    xaxis_tickangle=0 # Set tick angle back to 0 since we are wrapping
)

st.plotly_chart(fig_profit, use_container_width=True)

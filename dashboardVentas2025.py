import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import pydeck
import io # Import io for reading string as file

# --- Data Loading and Date Conversion ---
# In a real Streamlit app, you might upload the file or read from a more persistent storage
file_path = 'Orders Final.xlsx'
try:
    df_orders = pd.read_excel(file_path)
    st.success("Data loaded successfully!")

    # Drop the "Ship date" column if it exists
    if 'Ship date' in df_orders.columns:
        df_orders = df_orders.drop('Ship date', axis=1)
        print("Column 'Ship date' dropped.")

    # Define the base date for timedelta conversion (common for Excel)
    base_date = pd.to_datetime('1899-12-30')

    # Convert "Order Date" and "Ship Date" from timedelta to datetime by adding the base date
    # We will add checks to ensure the columns are indeed timedelta before attempting the conversion
    if 'Order Date' in df_orders.columns and pd.api.types.is_timedelta64_ns_dtype(df_orders['Order Date']):
        df_orders['Order Date'] = base_date + df_orders['Order Date']
        print("'Order Date' converted from timedelta to datetime.")
    else:
        print("'Order Date' column is not in timedelta format or not found.")

    if 'Ship Date' in df_orders.columns and pd.api.types.is_timedelta64_ns_dtype(df_orders['Ship Date']):
        df_orders['Ship Date'] = base_date + df_orders['Ship Date']
        print("'Ship Date' converted from timedelta to datetime.")
    else:
        print("'Ship Date' column is not in timedelta format or not found.")


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
    filtered_df_region = df_orders
else:
    filtered_df_region = df_orders[df_orders['Region'] == selected_region]

# Add a state filter in the sidebar, dependent on the selected region
states = filtered_df_region['State'].unique().tolist()
states.insert(0, "Todas") # Add "Todas" option at the beginning

selected_state = st.sidebar.selectbox("Select State", states)

# Further filter data based on selected state
if selected_state == "Todas":
    filtered_df_state = filtered_df_region
else:
    filtered_df_state = filtered_df_region[filtered_df_region['State'] == selected_state]

# Add a date range filter
min_date = filtered_df_state['Order Date'].min() if not filtered_df_state.empty else pd.to_datetime('2015-01-01')
max_date = filtered_df_state['Order Date'].max() if not filtered_df_state.empty else pd.to_datetime('2020-12-31')

start_date = st.sidebar.date_input('Start Date', min_value=min_date.date(), max_value=max_date.date(), value=min_date.date())
end_date = st.sidebar.date_input('End Date', min_value=min_date.date(), max_value=max_date.date(), value=max_date.date())

# Convert date inputs to datetime
start_date = pd.to_datetime(start_date)
end_date = pd.to_datetime(end_date)

# Filter data by date range
filtered_df = filtered_df_state[(filtered_df_state['Order Date'] >= start_date) & (filtered_df_state['Order Date'] <= end_date)].copy()


# Add a checkbox to show/hide the filtered DataFrame in the sidebar
show_dataframe = st.sidebar.checkbox("Show Filtered Data")

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

# --- Data Processing for PyDeck Chart ---
# Group the filtered_df DataFrame by the 'State' column and calculate the sum of 'Sales' for each state.
if not filtered_df.empty:
    state_sales = filtered_df.groupby('State')['Sales'].sum().reset_index()
else:
    state_sales = pd.DataFrame(columns=['State', 'Sales']) # Create an empty DataFrame with expected columns

# Load a dataset containing state names and their corresponding latitude and longitude coordinates.
# Using a sample data string for US states with lat/lon
csv_data = """State,Latitude,Longitude
Alabama,32.3182,86.9023
Alaska,64.2008,149.4937
Arizona,33.4484,112.0740
Arkansas,35.2010,91.8318
California,36.7783,119.4179
Colorado,39.5501,105.7821
Connecticut,41.5978,72.7554
Delaware,38.9158,75.5197
Florida,27.6648,81.5158
Georgia,32.1656,83.3113
Hawaii,19.8968,155.5828
Idaho,44.0682,114.7420
Illinois,40.6331,89.3733
Indiana,40.5512,85.6024
Iowa,41.8778,93.0977
Kansas,39.0469,95.6734
Kentucky,37.8393,84.2700
Louisiana,30.9843,91.9623
Maine,45.2350,69.4507
Maryland,39.0458,76.6122
Massachusetts,42.4072,71.3824
Michigan,42.7326,84.5361
Minnesota,45.6945,93.9002
Mississippi,32.3547,89.3985
Missouri,37.9643,91.7092
Montana,46.8797,110.3626
Nebraska,41.4925,99.9018
Nevada,39.8796,115.3870
New Hampshire,43.1939,71.5724
New Jersey,40.0583,74.4057
New Mexico,34.9727,105.0324
New York,40.7128,74.0060
North Carolina,35.7596,79.0193
North Dakota,47.5515,101.0020
Ohio,40.4173,82.9071
Oklahoma,35.0078,97.0929
Oregon,43.8041,120.5542
Pennsylvania,41.2033,77.1945
Rhode Island,41.5801,71.4774
South Carolina,33.8361,81.1637
South Dakota,43.9695,99.9018
Tennessee,35.5175,86.5804
Texas,31.9686,99.9018
Utah,39.3210,111.0937
Vermont,44.5588,72.5778
Virginia,37.4316,78.4469
Washington,47.4009,121.4905
West Virginia,38.5976,80.4549
Wisconsin,43.7840,88.7879
Wyoming,42.7560,107.3025
"""
state_geo_df = pd.read_csv(io.StringIO(csv_data))

# Merge the sales data with the geographical coordinates DataFrame based on the state names.
state_sales_geo = pd.merge(state_sales, state_geo_df, on='State', how='left')

# Handle potential missing values or mismatches by displaying states that didn't merge
if not state_sales_geo.empty and state_sales_geo['Latitude'].isnull().any():
    missing_states = state_sales_geo[state_sales_geo['Latitude'].isnull()]['State'].tolist()
    # In Streamlit, you might want to display this as a warning to the user
    # st.warning(f"Could not find geographical coordinates for the following states: {missing_states}")
    # For now, we will just print it to the console during testing
    print(f"Warning: Could not find geographical coordinates for the following states: {missing_states}")
    # Optionally, you could drop these rows or handle them differently
    state_sales_geo.dropna(subset=['Latitude', 'Longitude'], inplace=True)

# --- PyDeck Visualization ---
st.subheader("Total Sales by State")

# Define a PyDeck layer using ColumnLayer
# Map 'Sales' to the height of the columns
# Map 'Longitude' and 'Latitude' to the position
# Use a color scale based on Sales
layer = pydeck.Layer(
    'ColumnLayer',
    data=state_sales_geo,
    get_position='[Longitude, Latitude]',
    get_elevation='Sales',
    elevation_scale=0.01, # Adjust scale as needed for visualization
    radius=5000, # Adjust radius as needed
    get_fill_color='[255, 165, 0, Sales / state_sales_geo["Sales"].max() * 255]', # Example: Orange color, transparency based on Sales
    pickable=True,
    extruded=True,
)

# Define the initial view state for the map
view_state = pydeck.ViewState(
    latitude=39.8283,  # Approximate center of the US
    longitude=-98.5795, # Approximate center of the US
    zoom=3.5,          # Adjust zoom level as needed
    pitch=50,          # Adjust pitch for 3D effect
)

# Create a pydeck.Deck object
deck = pydeck.Deck(
    layers=[layer],
    initial_view_state=view_state,
    map_style='mapbox://styles/mapbox/light-v9' # Optional: choose a map style
)

# Display the PyDeck map in Streamlit
st.pydeck_chart(deck, use_container_width=True)


# --- Other Visualizations (Top Selling and Top Profit Products) ---

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

# You can add more visualizations or analysis here for your Streamlit app
# For example, you could add charts for sales/profit by category, region, etc.

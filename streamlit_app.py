# streamlit_app.py

# Import python packages
import streamlit as st
#from snowflake.snowpark.functions import col

# --- App header ---
st.title(f"Customize Your Smoothie :cup_with_straw: {st.__version__}")
st.write(
    "Choose the fruits you want in your custom Smoothie!"
)

# --- Inputs ---
name_on_order = st.text_input('Name on Smoothie')
st.write('The name on your Smoothie will be:', name_on_order if name_on_order else "—")

# --- Snowflake connection ---
# Requires a [connections.snowflake] block in secrets (see below)
cnx = st.connection("snowflake")
session = cnx.session()

# Pull fruit options from Snowflake (Snowpark DataFrame -> list)
fruit_df_sp = (
    session.table("smoothies.public.fruit_options")
           .select(col('FRUIT_NAME'))
           .sort(col('FRUIT_NAME'))
)
fruit_options = [r["FRUIT_NAME"] for r in fruit_df_sp.collect()]  # list of strings

# Show source table (optional, as a DataFrame)
# Convert to Pandas for display; Snowpark DataFrame isn't directly displayable as tabular in Streamlit
st.dataframe(
    data=fruit_df_sp.to_pandas(),
    use_container_width=True
)

# --- Ingredient selector ---
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    options=fruit_options,
    max_selections=5
)

# --- Submit order ---
if ingredients_list and name_on_order:
    # Join ingredients with commas
    ingredients_string = ", ".join(ingredients_list)

    # Parameterized INSERT to avoid SQL injection
    # Ensure the orders table exists with columns (ingredients STRING, name_on_order STRING)
    time_to_order = st.button('Submit Order')
    if time_to_order:
        session.sql(
            "INSERT INTO smoothies.public.orders(ingredients, name_on_order) VALUES (?, ?)",
            params=[ingredients_string, name_on_order]
        ).collect()
        st.success('Your Smoothie is ordered! ✅')
elif ingredients_list and not name_on_order:
    st.info("Please enter the name on the Smoothie before submitting.")

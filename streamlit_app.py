#Version 3

# streamlit_app.py

import streamlit as st

st.set_page_config(page_title="Customize Your Smoothie", page_icon="🥤")

# --- App header ---
st.title(f"Customize Your Smoothie :cup_with_straw:")
st.write("Choose the fruits you want in your custom Smoothie!")

# --- Inputs ---
name_on_order = st.text_input("Name on Smoothie")
st.write("The name on your Smoothie will be:", name_on_order if name_on_order else "—")

# --- Try to enable Snowflake (optional) ---
session = None
col = None

# Try importing Snowpark's 'col' (ok to continue if not installed)
try:
    from snowflake.snowpark.functions import col as sf_col  # type: ignore
    col = sf_col
except Exception:
    col = None  # Snowflake not installed

# Try creating a Snowflake session via Streamlit connection (ok to continue if not configured)
if col is not None:
    try:
        # Requires [connections.snowflake] in Streamlit secrets (see below)
        cnx = st.connection("snowflake")
        session = cnx.session()
    except Exception:
        session = None

# --- Load fruit options ---
fruit_options = None

if session is not None and col is not None:
    try:
        # Use uppercase identifiers to match Snowflake's unquoted default resolution
        fruit_df_sp = (
            session.table("SMOOTHIES.PUBLIC.FRUIT_OPTIONS")
                   .select(col("FRUIT_NAME"))
                   .sort(col("FRUIT_NAME"))
        )
        # Convert Snowpark result to a Python list
        fruit_options = [r["FRUIT_NAME"] for r in fruit_df_sp.collect()]

        # Optional: show the source table by converting to pandas
        try:
            st.dataframe(fruit_df_sp.to_pandas(), use_container_width=True)
        except Exception:
            # If pandas extra isn't available, skip the table display gracefully
            pass

    except Exception as e:
        st.warning("Could not load fruits from Snowflake; switching to demo list.")
        fruit_options = None

# Fallback demo data when Snowflake isn't available
if fruit_options is None:
    #st.info("Running in demo mode (Snowflake not configured).")
    fruit_options = [
        "Apple", "Banana", "Blueberry", "Mango",
        "Strawberry", "Pineapple", "Spinach", "Kale"
    ]

# --- Ingredient selector ---
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    options=fruit_options,
    max_selections=5
)

# --- Submit order ---
if ingredients_list and name_on_order:
    ingredients_string = ", ".join(ingredients_list)
    time_to_order = st.button("Submit Order")
    if time_to_order:
        if session is not None:
            try:
                session.sql(
                    "INSERT INTO SMOOTHIES.PUBLIC.ORDERS(INGREDIENTS, NAME_ON_ORDER) VALUES (?, ?)",
                    params=[ingredients_string, name_on_order]
                ).collect()
                st.success("Your Smoothie is ordered! ✅")
            """
            except Exception as e:
                st.error("Tried to submit to Snowflake but failed.")
                st.exception(e)
            """    

        else:
            pass
            #st.warning("Demo mode: not connected to Snowflake. Order not saved.") -- might use it later
elif ingredients_list and not name_on_order:
    st.info("Please enter the name on the Smoothie before submitting.")

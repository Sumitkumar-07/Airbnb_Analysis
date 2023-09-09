import pandas as pd
import pymongo
import streamlit as st
import plotly.express as px
from streamlit_option_menu import option_menu
from PIL import Image

# Setting up page configuration
icon = Image.open("logo.png")
st.set_page_config(page_title="Airbnb Data Visualization | By Sumit Kumar",
                   page_icon=icon,
                   layout="wide",
                   initial_sidebar_state="expanded",
                   menu_items={'About': """# This dashboard app is created by *Sumit Kumar*!
                                        Data has been gathered from MongoDB Atlas"""}
                   )

# Creating option menu in the sidebar
with st.sidebar:
    selected = option_menu("Menu", ["Home", "Overview", "Visualization", "Explore"],
                           icons=["house", "graph-up-arrow", "bar-chart-line", "binoculars"],
                           menu_icon="menu-button-wide",
                           default_index=0,
                           styles={"nav-link": {"font-size": "20px",
                                                "text-align": "left",
                                                "margin": "-1px",
                                                "--hover-color": "#BBAC5D"},
                                   "nav-link-selected": {
                                       "background-color": "#FF5A5F"}}
                           )

# Define your MongoDB Atlas connection parameters
database_name = "sample_airbnb"  # Replace with your database name
collection_name = "listingsAndReviews"  # Replace with your collection name

# CREATING CONNECTION WITH MONGODB ATLAS AND RETRIEVING THE DATA
client = pymongo.MongoClient("ENTER_YOUR_MONGODB_ATLAS_CONNECTION_STRING")
db = client.sample_airbnb
col = db.listingsAndReviews

# Connect to the MongoDB Atlas cluster with a timeout
try:
    client.admin.command('ping')
    st.success("You successfully connected to MongoDB Atlas!")
except pymongo.errors.ServerSelectionTimeoutError as e:
    st.error(f"Error connecting to MongoDB: {e}")
except Exception as e:
    st.error(f"An error occurred: {e}")




# READING THE CLEANED DATAFRAME
df = pd.read_csv('Airbnb_data.csv')

# HOME PAGE
if selected == "Home":
    # Title
    st.markdown(
        '<h1 style="color:#B05300; font-size:50px; font-weight:bold; text-align:center; text-decoration: underline;">AIRBNB ANALYSIS</h1>',
        unsafe_allow_html=True
    )

    col1, col2 = st.columns(2, gap='medium')
    col1.markdown(
        "## <span style='color:#81B44E'>🔲Domain</span> : <span style='color:#BBAC5D'>Travel Industry, Property Management, and Tourism</span>",
        unsafe_allow_html=True
    )

    col1.markdown(
        "## <span style='color:#81B44E'>🔲Technologies used</span> : <span style='color:#BBAC5D'>Python, Pandas, Plotly, Streamlit, MongoDB</span>",
        unsafe_allow_html=True
    )

    col1.markdown(
        "## <span style='color:#81B44E'>🔲Overview</span> : <span style='color:#BBAC5D'>To analyze Airbnb data using MongoDB Atlas, perform data cleaning and preparation, develop interactive visualizations, and create dynamic plots to gain insights into pricing variations, availability patterns, and location-based trends.</span>",
        unsafe_allow_html=True
    )

    col2.markdown("#   ")
    col2.markdown("#   ")
    col2.image("airbnb.png")

# OVERVIEW PAGE
if selected == "Overview":
    tab1, tab2 = st.tabs(["$\huge 📝 RAW DATA $", "$\huge🚀 INSIGHTS $"])

    # RAW DATA TAB
    with tab1:
        # RAW DATA
        col1, col2 = st.columns(2)
        if col1.button("Click to view Raw data"):
            col1.write(col.find_one())
        # DATAFRAME FORMAT
        if col2.button("Click to view Dataframe"):
            col1.write(col.find_one())
            col2.write(df)

    # INSIGHTS TAB
    with tab2:
        # GETTING USER INPUTS
        country = st.sidebar.multiselect('Select a Country :',
                                         sorted(df.Country.unique()),
                                         sorted(df.Country.unique()))
        prop = st.sidebar.multiselect('Select Property type :',
                                      sorted(df.Property_type.unique()),
                                      sorted(df.Property_type.unique()))
        room = st.sidebar.multiselect('Select Room type :',
                                      sorted(df.Room_type.unique()),
                                      sorted(df.Room_type.unique()))
        price = st.slider('Select Price :', df.Price.min(), df.Price.max(),
                          (df.Price.min(), df.Price.max()))

        # Add the code to get price_min and price_max
        price_min = float(df['Price'].min())
        price_max = float(df['Price'].max())

        # Create the slider widget for price
        price = st.slider('Select Price :', price_min, price_max,
                          (price_min, price_max), key='overview_price_slider')

        # CONVERTING THE USER INPUT INTO QUERY
        query = f'Country in {country} & Room_type in {room} & Property_type in {prop} & Price >= {price[0]} & Price <= {price[1]}'

        # CREATING COLUMNS
        col1, col2 = st.columns(2, gap='medium')

        with col1:
            # TOP 10 PROPERTY TYPES BAR CHART
            df1 = df.query(query).groupby(
                ["Property_type"]).size().reset_index(
                name="Listings").sort_values(by='Listings', ascending=False)[
                  :10]
            fig = px.bar(df1,
                         title='Top 10 Property Types :',
                         x='Listings',
                         y='Property_type',
                         orientation='h',
                         color='Property_type',
                         color_continuous_scale=px.colors.sequential.Agsunset)
            st.plotly_chart(fig, use_container_width=True)

            # TOP 10 HOSTS BAR CHART
            df2 = df.query(query).groupby(["Host_name"]).size().reset_index(
                name="Listings").sort_values(by='Listings', ascending=False)[
                  :10]
            fig = px.bar(df2,
                         title='Top 10 Hosts with Highest number of Listings :',
                         x='Listings',
                         y='Host_name',
                         orientation='h',
                         color='Host_name',
                         color_continuous_scale=px.colors.sequential.Agsunset)
            fig.update_layout(showlegend=False)
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            # TOTAL LISTINGS IN EACH ROOM TYPES PIE CHART
            df1 = df.query(query).groupby(["Room_type"]).size().reset_index(
                name="counts")
            fig = px.pie(df1,
                         title='Total Listings in each Room_types :',
                         names='Room_type',
                         values='counts',
                         color_discrete_sequence=px.colors.sequential.Rainbow
                         )
            fig.update_traces(textposition='outside', textinfo='value+label')
            st.plotly_chart(fig, use_container_width=True)

            # TOTAL LISTINGS BY COUNTRY CHOROPLETH MAP
            country_df = df.query(query).groupby(['Country'], as_index=False)[
                'Name'].count().rename(columns={'Name': 'Total_Listings'})
            fig = px.choropleth(country_df,
                                title='Total Listings in each Country :',
                                locations='Country',
                                locationmode='country names',
                                color='Total_Listings',
                                color_continuous_scale=px.colors.sequential.Plasma
                                )
            st.plotly_chart(fig, use_container_width=True)

# VISUALIZATION PAGE
if selected == "Visualization":
    st.markdown("## <span style='color:#81B44E'>📊 Data Visualization :</span>",
                unsafe_allow_html=True)

    st.image("visual.webp", use_column_width=True)

    st.sidebar.header("Visualization Options:⬇️")

    # Add visualization options here
    st.sidebar.subheader("Descriptive Analysis")
    if st.sidebar.checkbox("Display Descriptive Stats"):
        st.subheader("Descriptive Statistics")
        st.write(df.describe())

    st.sidebar.subheader("Target Analysis")
    if st.sidebar.checkbox("Display Histogram of Target Column"):
        target_column = st.sidebar.selectbox("Select target column:", df.columns)
        st.subheader(f"Histogram of {target_column}")
        fig = px.histogram(df, x=target_column)
        st.plotly_chart(fig)

    st.sidebar.subheader("Distribution of Numerical Columns")
    if st.sidebar.checkbox("Display Distribution of Numerical Columns"):
        num_columns = df.select_dtypes(exclude='object').columns
        selected_num_cols = st.sidebar.multiselect("Select numerical columns for distribution plots:", num_columns)
        for col in selected_num_cols:
            st.subheader(f"Distribution of {col}")
            fig = px.histogram(df, x=col)
            st.plotly_chart(fig)

    st.sidebar.subheader("Count Plots of Categorical Columns")
    if st.sidebar.checkbox("Display Count Plots of Categorical Columns"):
        cat_columns = df.select_dtypes(include='object').columns
        selected_cat_cols = st.sidebar.multiselect("Select categorical columns for count plots:", cat_columns)
        for col in selected_cat_cols:
            st.subheader(f"Count Plot of {col}")
            fig = px.histogram(df, x=col, color_discrete_sequence=['indianred'])
            st.plotly_chart(fig)

    st.sidebar.subheader("Box Plots")
    if st.sidebar.checkbox("Display Box Plots"):
        num_columns = df.select_dtypes(exclude='object').columns
        selected_num_cols = st.sidebar.multiselect("Select numerical columns for box plots:", num_columns)
        for col in selected_num_cols:
            st.subheader(f"Box Plot of {col}")
            fig = px.box(df, y=col)
            st.plotly_chart(fig)

    st.sidebar.subheader("Outlier Analysis")
    if st.sidebar.checkbox("Display Outlier Analysis"):
        st.subheader("Outlier Analysis")
        st.write("Number of Outliers:")
        st.write(df.select_dtypes(exclude='object').apply(lambda x: sum((x - x.mean()) > 2 * x.std())))

    st.sidebar.subheader("Variance of Target with Categorical Columns")
    if st.sidebar.checkbox("Display Variance of Target with Categorical Columns"):
        st.subheader("Variance of Target with Categorical Columns")
        model_type = st.sidebar.radio("Select Problem Type:", ("Regression", "Classification"))
        target_column = st.sidebar.selectbox("Select target column:", df.columns)
        cat_columns = df.select_dtypes(include='object').columns
        selected_cat_cols = st.sidebar.multiselect("Select categorical columns for analysis:", cat_columns)
        for col in selected_cat_cols:
            if model_type == "Regression":
                st.subheader(f"Box Plot of {target_column} vs {col}")
                fig = px.box(df, y=target_column, x=col)
                st.plotly_chart(fig)
            else:
                st.subheader(f"Histogram of {target_column} by {col}")
                fig = px.histogram(df, x=target_column, color=col)
                st.plotly_chart(fig)

# EXPLORE PAGE
if selected == "Explore":
    st.markdown(
        "## <span style='color:#CB56A4; font-size:50px;'>Explore more about the Airbnb data :</span>",
        unsafe_allow_html=True
    )

    # GETTING USER INPUTS
    country = st.sidebar.multiselect('Select a Country :',
                                     sorted(df.Country.unique()),
                                     sorted(df.Country.unique()))
    prop = st.sidebar.multiselect('Select Property type :',
                                  sorted(df.Property_type.unique()),
                                  sorted(df.Property_type.unique()))
    room = st.sidebar.multiselect('Select Room type :',
                                  sorted(df.Room_type.unique()),
                                  sorted(df.Room_type.unique()))
    price = st.slider('Select Price :', df.Price.min(), df.Price.max(),
                      (df.Price.min(), df.Price.max()))

    # CONVERTING THE USER INPUT INTO QUERY
    query = f'Country in {country} & Room_type in {room} & Property_type in {prop} & Price >= {price[0]} & Price <= {price[1]}'

    # HEADING 1
    st.markdown("## <span style='color:#CB56A4'>Price Analysis :</span>",
                unsafe_allow_html=True)

    # CREATING COLUMNS
    col1, col2 = st.columns(2, gap='medium')

    with col1:
        # AVG PRICE BY ROOM TYPE BARCHART
        pr_df = df.query(query).groupby('Room_type', as_index=False)[
            'Price'].mean().sort_values(by='Price')
        fig = px.bar(data_frame=pr_df,
                     x='Room_type',
                     y='Price',
                     color='Price',
                     title='Avg Price in each Room type :'
                     )
        st.plotly_chart(fig, use_container_width=True)

        # HEADING 2
        st.markdown(
            "## <span style='color:#CB56A4'>Availability Analysis :</span>",
            unsafe_allow_html=True)

        # AVAILABILITY BY ROOM TYPE BOX PLOT
        fig = px.box(data_frame=df.query(query),
                     x='Room_type',
                     y='Availability_365',
                     color='Room_type',
                     title='Availability by Room_type :'
                     )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        # AVG PRICE IN COUNTRIES SCATTERGEO
        country_df = df.query(query).groupby('Country', as_index=False)[
            'Price'].mean()
        fig = px.scatter_geo(data_frame=country_df,
                             locations='Country',
                             color='Price',
                             hover_data=['Price'],
                             locationmode='country names',
                             size='Price',
                             title='Avg Price in each Country :',
                             color_continuous_scale='agsunset'
                             )
        col2.plotly_chart(fig, use_container_width=True)

        # BLANK SPACE
        st.markdown("#   ")
        st.markdown("#   ")

        # AVG AVAILABILITY IN COUNTRIES SCATTERGEO
        country_df = df.query(query).groupby('Country', as_index=False)[
            'Availability_365'].mean()
        country_df.Availability_365 = country_df.Availability_365.astype(int)
        fig = px.scatter_geo(data_frame=country_df,
                             locations='Country',
                             color='Availability_365',
                             hover_data=['Availability_365'],
                             locationmode='country names',
                             size='Availability_365',
                             title='Avg Availability in each Country :',
                             color_continuous_scale='agsunset'
                             )
        st.plotly_chart(fig, use_container_width=True)

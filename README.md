# YouTube-Data-Harvesting-and-Warehousing-using-SQL-and-Streamlit

## :blue_book:Introduction
* The project about Building a simple dashboard or UI using Streamlit.
* Retrieve YouTube channel data with the help of  YouTube API.
* Stored the data in SQL database(warehousing),with the help of XAMPP control panel.
* enabling querying of the data using SQL and Visualize the data within the Streamlit.
  
### Domain : :iphone: *Social Media*

### :art: Skills Takeaway :
__Python scripting, Data Collection, Streamlit, API integration, Data Management using SQL__

### :blue_book: Overview
#### :ear_of_rice: Data Harvesting:
* Utilizing the YouTube API to collect data such as video details, channel information, playlists, and comments.
#### :inbox_tray:Data Storage:
* Setting up a local MySQL database using XAMPP.
* Creating tables to store the harvested YouTube data.
* Using SQL scripts to insert the collected data into the database.
#### :bar_chart:Data Analysis and Visualization:
* Developing a Streamlit application to interact with the SQL database.
* Creating visualizations and performing analysis on the stored YouTube data

### :wrench: Technology and Tools
* Python 3.12.2
* XAMPP
* MYSQL
* Youtube API
* Streamlit
* Plotly

### :book: Packages and Libraries
* google-api-python-client 👉 import googleapiclient.discovery
* mysql-connector-python 👉 import mysql.connector
* SQLAlchemy  👉 from sqlalchemy import create_engine
* pandas 👉 import pandas as pd
* streamlit  👉 import streamlit as st
* streamlit_option_menu 👉 from streamlit_option_menu import option_menu
* plotly 👉 import plotly.express as px
* pillow 👉 from PIL import Image
  
### 📘  Features
#### 📚 Data Collection:
* The data collection process involved retrieving various data points from YouTube using the YouTube Data API. Retrieve channel information, videos details, playlists and comments.
#### 💾 Database Storage
* The collected YouTube data was tranformed into pandas dataframe and befor that the XAMPP conntrol panel create a new database and table creation. with the help of sqlalchemy the data's are inserted to the respective tables and The database could be accessed and managed using X
* Data Analysis: Perform queries on the SQL data warehouse.
* Data Visualization: Presents data in visually appealing charts and graphs using Plotly.
* Streamlit App: Interactive dashboard for querying and visualizing the YouTube data.

### 📘 Usage
* Enter a YouTube channel ID or name in the input field in Data collection option from sidebar menu.
* Click the "View Details" button to fetch and display channel information.
* Click the "Upload to MySQL" button to store channel data in the SQL database.
* Select Analysis and Visualization options from the sidebar menu to analyze and visualize data.

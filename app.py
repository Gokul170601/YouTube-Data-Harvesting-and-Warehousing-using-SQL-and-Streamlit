import streamlit as st
from PIL import Image
from streamlit_option_menu import option_menu
import plotly.express as px

import googleapiclient.discovery
from googleapiclient.errors import HttpError


import pandas as pd
import re

import mysql.connector
from sqlalchemy import create_engine


#API key connection to interact with youtube API
api_service_name = "youtube"
api_version = "v3"
api_Key="AIzaSyDQzomtxdvz9Jhr5oAKcdPRh8xk1r1AVZA"
youtube = googleapiclient.discovery.build(api_service_name, api_version, developerKey=api_Key)

#mycurser and engine created to intreact with MYSQL Database
mydb = mysql.connector.connect(host="localhost",user="root",password="")
mycursor = mydb.cursor(buffered=True)
engine = create_engine("mysql+mysqlconnector://root:@localhost/youtube")

#to create and use the database in MYSQL database 
mycursor.execute('create database if not exists youtube')
mycursor.execute('use youtube')

#setting up streamlit page and adding name to it
icon=Image.open("youtube.png")
st.set_page_config(page_title='YouTube Data Harvesting and Warehousing',
                    page_icon=icon,
                    layout='wide',
                    initial_sidebar_state='expanded',
                    menu_items={'About': '''This streamlit application was developed by M.Gokul.
                                Contact_e-mail:gokulgokul6847@gmail.com'''})

#setting up streamlit sidebar menu with optins
with st.sidebar:
    selected =option_menu("Main Menu",
                        ["Home","Data collection and upload","MYSQL Database","Analysis using SQL", "Data Visualization"],
                        icons=["house","cloud-upload","database", "filetype-sql", "bar-chart-line"],
                        menu_icon="menu-up",
                        orientation="vertical")

# Setting up the option "Home" in streamlit page
if selected == "Home":
    st.title(':red[You]Tube :blue[Data Harvesting & Warehousing using SQL]')
    st.subheader(':blue[Domain :] Social Media')
    st.subheader(':blue[Overview :]')
    st.markdown('''Build a simple dashboard or UI using Streamlit and 
                retrieve YouTube channel data with the help of the YouTube API.
                Stored the data in an SQL database(warehousing) managed by XAMPP control panel,
                enabling querying of the data using SQL.Visualize the data within the Streamlit app to uncover insights,
                trends with the YouTube channel data''')
    st.subheader(':blue[Skill Take Away :]')
    st.markdown(''' Python scripting,Data Collection,API integration,Data Management using SQL,Streamlit''')
    st.subheader(':blue[About :]')
    st.markdown('''Hello! I'm Gokul, a MBA graduate with a keen interest in data science and analytics.
                Currently on an exciting journey into the world of data science,
                this is my first project title as YouTube data harvesting and warehousing using SQL, 
                where I explored the vast realm of YouTube data to extract meaningful insights.
                This experience ignited my passion for data-driven decision-making and deepened my understanding of
                data extraction techniques and Database management.''')
    st.subheader(':blue[Contact:]')
    st.markdown('#### linkedin: www.linkedin.com/in/gokul-m-j17')
    st.markdown('#### Email : gokulgokul6847@gmail.com')

# Function to Retrieve channel information from Youtube
def channel_information(channel_id):
    request = youtube.channels().list(
    part="snippet,contentDetails,statistics",
    id=channel_id)
    response = request.execute()

    for i in response['items']:
        channel_data= dict(
            channel_name=i['snippet']['title'],
            Channel_id=i["id"],
            channel_Description=i['snippet']['description'],
            channel_Thumbnail=i['snippet']['thumbnails']['default']['url'],
            channel_playlist_id=i['contentDetails']['relatedPlaylists']['uploads'],
            channel_subscribers=i['statistics']['subscriberCount'],
            channel_video_count=i['statistics']['videoCount'],
            channel_views=i['statistics']['viewCount'],
            channel_publishedat=i['snippet']['publishedAt'])
    return (channel_data)

# Function to Retrieve playlist information of channel from Youtube
def playlist_information(channel_id):
    playlist_info=[]
    nextPageToken=None
    try:
        while True:
            request = youtube.playlists().list(
                        part="snippet,contentDetails",
                        channelId=channel_id,
                        maxResults=50,
                        pageToken=nextPageToken
                    )
            response = request.execute()
        
            for i in response['items']:
                data=dict(
                    playlist_id=i['id'],
                    playlist_name=i['snippet']['title'],
                    publishedat=i['snippet']['publishedAt'],
                    channel_ID=i['snippet']['channelId'],
                    channel_name=i['snippet']['channelTitle'],
                    videoscount=i['contentDetails']['itemCount'])
                playlist_info.append(data)
                nextPageToken=response.get('nextPageToken')
            if nextPageToken is None:
                break
    except HttpError as e:
        error_message = f"Error retrieving playlists: {e}"   # Handle specific YouTube API errors
        st.error(error_message)
    return (playlist_info)

#Function to Retrieve video ids of a channel from Youtube
def get_video_ids(channel_id):
    response= youtube.channels().list( part="contentDetails",
                                        id=channel_id).execute()
    playlist_videos=response['items'][0]['contentDetails']['relatedPlaylists']['uploads']
    
    next_page_token=None
    
    videos_ids=[]
    
    while True:
        response1=youtube.playlistItems().list(
            part="snippet",
            playlistId=playlist_videos,
            maxResults=50,
            pageToken=next_page_token).execute()
        
        for i in range (len(response1['items'])):
            videos_ids.append(response1['items'][i]['snippet']['resourceId']['videoId'])
            next_page_token=response1.get('nextPageToken')
        
        if next_page_token is None:
            break
    return (videos_ids)

#Function to Retrieve video information of all video IDS from Youtube
def video_information(video_IDS):
    video_info=[]
    for video_id in video_IDS:
        response= youtube.videos().list(
                        part="snippet,contentDetails,statistics",
                        id=video_id).execute()
        
        for i in response['items']:
                data=dict(
                        channel_id=i['snippet']['channelId'],
                        video_id=i['id'],
                        video_name=i['snippet']['title'],
                        video_Description=i['snippet']['description'],
                        Thumbnail=i['snippet']['thumbnails']['default']['url'],
                        Tags=i['snippet'].get('tags'),
                        publishedAt=i['snippet']['publishedAt'],
                        Duration=convert_duration(i['contentDetails']['duration']),
                        View_Count=i['statistics']['viewCount'],
                        Like_Count=i['statistics'].get('likeCount'),
                        Favorite_Count=i['statistics'].get('favoriteCount'),
                        Comment_Count=i['statistics']['commentCount'],
                        Caption_Status=i['contentDetails']['caption'] 
                        )
                video_info.append(data)
    return(video_info)

#Function to convert Duration from ISO 8601 format to HH:MM:SS format
def convert_duration(duration): 
        regex = r'PT(\d+H)?(\d+M)?(\d+S)?'
        match = re.match(regex, duration)
        if not match:
                return '00:00:00'
        hours, minutes, seconds = match.groups()
        hours = int(hours[:-1]) if hours else 0
        minutes = int(minutes[:-1]) if minutes else 0
        seconds = int(seconds[:-1]) if seconds else 0
        total_seconds = hours * 3600 + minutes * 60 + seconds
        return '{:02d}:{:02d}:{:02d}'.format(int(total_seconds / 3600), int((total_seconds % 3600) / 60), int(total_seconds % 60))

#Function to Retrieve comments information of all video IDS from Youtube
def comments_information(video_IDS):
    comments_info=[]
    try:
        for video_id in video_IDS:
            request = youtube.commentThreads().list(
            part="snippet",
            videoId=video_id,
            maxResults=100)
            response = request.execute()

            for i in response.get('items',[]):
                data=dict(
                            video_id=i['snippet']['videoId'],
                            comment_id=i['snippet']['topLevelComment']['id'],
                            comment_text=i['snippet']['topLevelComment']['snippet']['textDisplay'],
                            comment_author=i['snippet']['topLevelComment']['snippet']['authorDisplayName'],
                            comment_publishedat=i['snippet']['topLevelComment']['snippet']['publishedAt'])
                comments_info.append(data)
    except HttpError as e:
        if e.resp.status == 403 and e.error_details[0]["reason"] == 'commentsDisabled':
                st.error("comments diabled for some videos")
    return (comments_info)


#setting up the option "Data collection and upload" in streamlit page
if selected == "Data collection and upload":
    st.subheader(':blue[Data collection and upload]')
    st.markdown('''
                - Provide channel ID in the input field.
                - Clicking the 'View Details' button will display an overview of youtube channel.
                - Clicking 'Upload to MYSQL database' will store the extracted channel information,
                Playlists,Videos,Comments in MYSQL Database''')
    st.markdown('''
                :red[note:] ***you can get the channel ID :***
                open youtube - go to any channel - go to about - share cahnnel - copy the channel ID''')
    
    channel_ID = st.text_input("**Enter the channel ID in the below box :**")
    
    if st.button("View details"): # Shows the channel information from Youtube
        with st.spinner('Extraction in progress...'):
            try:
                extracted_details = channel_information(channel_id=channel_ID)
                st.write('**:blue[Channel Thumbnail]** :')
                st.image(extracted_details.get('channel_Thumbnail'))
                st.write('**:blue[Channel Name]** :', extracted_details['channel_name'])
                st.write('**:blue[Description]** :', extracted_details['channel_Description'])
                st.write('**:blue[Total_Videos]** :', extracted_details['channel_video_count'])
                st.write('**:blue[Subscriber Count]** :', extracted_details['channel_subscribers'])
                st.write('**:blue[Total Views]** :', extracted_details['channel_views'])
            except HttpError as e:
                if e.resp.status == 403 and e.error_details[0]["reason"] == 'quotaExceeded':
                    st.error(" API Quota exceeded. Please try again later.")
            except:
                st.error("Please ensure to give valid channel ID")
            
    
    if st.button("Upload to MYSQL database"): # upload the youtube retrieved data into MYSQL database

        with st.spinner('Upload in progress...'):
            try:
                #to create a channel table in sql database
                mycursor.execute('''create table if not exists channel( channel_name VARCHAR(100) ,
                                channel_id VARCHAR(50) PRIMARY KEY,channel_Description VARCHAR(1000),channel_Thumbnail VARCHAR(100),
                                channel_playlist_id VARCHAR(50),channel_subscribers BIGINT,channel_video_count BIGINT,
                                channel_views BIGINT,channel_publishedat DATETIME)''')
                
                #to create a playlist table in sql database
                mycursor.execute('''create table if not exists playlist(playlist_id VARCHAR(50) PRIMARY KEY,playlist_name VARCHAR(100),
                                publishedat DATETIME,channel_id VARCHAR(50),channel_name VARCHAR(100),videoscount BIGINT)''')
                
                #to create videos table in sql database
                mycursor.execute('''create table if not exists videos(channel_id VARCHAR(50),video_id VARCHAR(50)primary key,
                                video_name VARCHAR(100),video_Description VARCHAR(500),Thumbnail VARCHAR(100),Tags VARCHAR(250),
                                publishedAt DATETIME,Duration VARCHAR(10),View_Count BIGINT,Like_Count BIGINT,Favorite_Count BIGINT,
                                Comment_Count BIGINT,Caption_Status VARCHAR(10),
                                FOREIGN KEY (channel_id) REFERENCES channel(channel_id))''')
                
                #to create comments table in sql database
                mycursor.execute('''create table if not exists comments(video_id VARCHAR(50),comment_id VARCHAR(50),comment_text TEXT,
                                comment_author VARCHAR(50),comment_publishedat DATETIME,FOREIGN KEY (video_id) REFERENCES videos(video_id))''')
                
                #Transform corresponding data's into pandas dataframe
                df_channel=pd.DataFrame(channel_information(channel_id=channel_ID),index=[0])
                df_playlist=pd.DataFrame(playlist_information(channel_id=channel_ID))
                df_videos=pd.DataFrame(video_information(video_IDS= get_video_ids(channel_id=channel_ID)))
                df_comments=pd.DataFrame(comments_information(video_IDS=get_video_ids(channel_id=channel_ID)))
                
                #load the dataframe into tabel in SQL Database
                df_channel.to_sql('channel',engine,if_exists='append',index=False)
                df_playlist.to_sql('playlist',engine,if_exists='append',index=False)
                df_videos['Tags'] = df_videos['Tags'].apply(lambda x: ', '.join(x) if isinstance(x, list) else '')
                df_videos.to_sql('videos',engine,if_exists='append',index=False)
                df_comments.to_sql('comments',engine,if_exists='append',index=False)
                mydb.commit()
                st.success('channel information,playlists,videos,comments are uploaded successfully')
            except :
                st.error('channel already uploaded or exist in MYSQL Database')

# Function to retrieve channel name from SQL DB
def fetch_channel_names():
    mycursor.execute("SELECT channel_name FROM channel")
    channel_names = [row[0] for row in mycursor.fetchall()]
    return channel_names

# Function to Fetch all the related data from SQL DB
def load_channel_data(channel_name):
    # Fetch channel data
    mycursor.execute("SELECT * FROM channel WHERE channel_name = %s", (channel_name,))
    out= mycursor.fetchall()
    channel_df = pd.DataFrame(out, columns=[i[0] for i in mycursor.description]).reset_index(drop=True)
    channel_df.index +=1

    # Fetch playlists data
    mycursor.execute("SELECT * FROM playlist WHERE channel_id = %s", (channel_df['channel_id'].iloc[0],))
    out = mycursor.fetchall()
    playlists_df = pd.DataFrame(out, columns=[i[0] for i in mycursor.description]).reset_index(drop=True)
    playlists_df.index +=1

    # Fetch videos data
    mycursor.execute("SELECT * FROM videos WHERE channel_id = %s", (channel_df['channel_id'].iloc[0],))
    out= mycursor.fetchall()
    videos_df = pd.DataFrame(out, columns=[i[0] for i in mycursor.description]).reset_index(drop=True)
    videos_df.index +=1

    # Fetch comments data
    mycursor.execute("SELECT * FROM comments WHERE video_id IN (SELECT video_id FROM videos WHERE channel_id = %s)",
                    (channel_df['channel_id'].iloc[0],))
    out = mycursor.fetchall()
    comments_df = pd.DataFrame(out, columns=[i[0] for i in mycursor.description]).reset_index(drop=True)
    comments_df.index +=1

    return channel_df,playlists_df,videos_df,comments_df

# Setting up the option "MYSQL Database" in streamlit page 
if selected =="MYSQL Database":
    st.subheader(':blue[MYSQL Database]')
    st.markdown('''__You can view the channel details along with the playlist,videos,comments in table format 
                    which is stored in MYSQL database__''')
    try:
        channel_names = fetch_channel_names()
        selected_channel = st.selectbox(':red[Select Channel]', channel_names) 
    
        if selected_channel:
            channel_info,playlist_info,videos_info,comments_info = load_channel_data(selected_channel)

        st.subheader(':blue[Channel Table]')
        st.write(channel_info)
        st.subheader(':blue[Playlists Table]')
        st.write(playlist_info)
        st.subheader(':blue[Videos Table]')
        st.write(videos_info)
        st.subheader(':blue[Comments Table]')
        st.write(comments_info)
    except:
        st.error('Database is empty ')

# Function to excute Query of 1st Question 
def sql_question_1():
    mycursor.execute('''SELECT channel.channel_name,videos.video_name
                        FROM videos 
                        JOIN channel ON channel.Channel_id = videos.Channel_id
                        ORDER BY channel_name''')
    out=mycursor.fetchall()
    Q1= pd.DataFrame(out, columns=['Channel Name','Videos Name']).reset_index(drop=True)
    Q1.index +=1
    st.dataframe(Q1)

# Function to excute Query of 2nd Question 
def sql_question_2():
    mycursor.execute('''SELECT DISTINCT channel_name,COUNT(videos.video_id) as Total_Videos 
                        FROM channel 
                        JOIN videos on Channel.channel_id = videos.channel_id
                        GROUP BY channel_name 
                        ORDER BY Total_videos DESC''')
    out=mycursor.fetchall()
    Q2= pd.DataFrame(out, columns=['Channel Name','Total Videos']).reset_index(drop=True)
    Q2.index +=1
    st.dataframe(Q2)

# Function to excute Query of 3rd Question 
def sql_question_3():
    mycursor.execute('''SELECT channel.Channel_name,videos.Video_name, videos.View_Count as Total_Views
                        FROM videos
                        JOIN channel ON channel.Channel_id = videos.Channel_id
                        ORDER BY videos.View_Count DESC
                        LIMIT 10;''')
    out=mycursor.fetchall()
    Q3= pd.DataFrame(out, columns=['Channel Name','Videos Name','Total Views']).reset_index(drop=True)
    Q3.index +=1
    st.dataframe(Q3)

# Function to excute Query of  4th Question 
def sql_question_4():
    mycursor.execute('''SELECT videos.video_name,videos.comment_count as Total_Comments
                    FROM videos
                    ORDER BY videos.comment_count DESC''')
    out=mycursor.fetchall()
    Q4= pd.DataFrame(out, columns=['Videos Name','Total Comments']).reset_index(drop=True)
    Q4.index +=1
    st.dataframe(Q4)

# Function to excute Query of 5th Question 5
def sql_question_5():
    mycursor.execute('''SELECT channel.channel_name,videos.video_name,videos.like_count as Highest_likes FROM videos 
                    JOIN channel ON videos.channel_id=channel.channel_id
                    WHERE like_count=(SELECT MAX(videos.like_count) FROM videos v WHERE videos.channel_id=v.channel_id
                    GROUP BY channel_id)
                    ORDER BY Highest_likes DESC''')
    out=mycursor.fetchall()
    Q5= pd.DataFrame(out, columns=['Channel Name','Videos Name','Likes']).reset_index(drop=True)
    Q5.index +=1
    st.dataframe(Q5)    

# Function to excute Query of 6th Question 
def sql_question_6():
    mycursor.execute('''SELECT videos.video_name,videos.like_count as Likes
                    FROM videos
                    ORDER BY videos.like_count DESC''')
    out=mycursor.fetchall()
    Q6= pd.DataFrame(out, columns=['Videos Name','Likes']).reset_index(drop=True)
    Q6.index +=1
    st.dataframe(Q6)

# Function to excute Query of 7th Question 
def sql_question_7():
    mycursor.execute('''SELECT channel.channel_name,channel.channel_views as Total_views
                    FROM channel
                    ORDER BY channel.channel_views DESC  ''')
    out=mycursor.fetchall()
    Q7= pd.DataFrame(out, columns=['Channel Name','Total views']).reset_index(drop=True)
    Q7.index +=1
    st.dataframe(Q7)

# Function to excute Query of 8th Question 
def sql_question_8():
    mycursor.execute('''SELECT DISTINCT channel.channel_name
                    FROM channel
                    JOIN videos ON  videos.channel_id=channel.channel_id
                    WHERE YEAR(videos.PublishedAt) = 2022 ''')
    out=mycursor.fetchall()
    Q8= pd.DataFrame(out, columns=['Channel Name']).reset_index(drop=True)
    Q8.index +=1
    st.dataframe(Q8)

# Function to excute Query of 9th  Question 
def sql_question_9():
    mycursor.execute('''SELECT channel.channel_name,
                    TIME_FORMAT(SEC_TO_TIME(AVG(TIME_TO_SEC(TIME(videos.Duration)))), "%H:%i:%s") AS Duration
                    FROM videos
                    JOIN channel ON videos.channel_id=channel.channel_id
                    GROUP BY channel_name ''')
    out=mycursor.fetchall()
    Q9= pd.DataFrame(out, columns=['Chanel Name','Duration']).reset_index(drop=True)
    Q9.index +=1
    st.dataframe(Q9)

# Function to excute Query of 10th Question 
def sql_question_10():
    mycursor.execute('''SELECT channel.channel_name,videos.video_name,videos.comment_count as Total_Comments
                    FROM videos
                    JOIN channel ON channel.channel_id=videos.channel_id
                    ORDER BY videos.comment_count DESC''')
    out=mycursor.fetchall()
    Q10= pd.DataFrame(out, columns=['Channel Name','Videos Name','Comments']).reset_index(drop=True)
    Q10.index +=1
    st.dataframe(Q10)

# Setting up the option "Analysis using SQL" in streamlit page 
if selected == 'Analysis using SQL':
    st.subheader(':blue[Analysis using SQL]')
    st.markdown('''You can analyze the collection of YouTube channel data stored in a MySQL database.
                Based on selecting the listed questions below, the output will be displayed in a table format''')
    Questions = ['Select your Question',
        '1.What are the names of all the videos and their corresponding channels?',
        '2.Which channels have the most number of videos, and how many videos do they have?',
        '3.What are the top 10 most viewed videos and their respective channels?',
        '4.How many comments were made on each video, and what are their corresponding video names?',
        '5.Which videos have the highest number of likes, and what are their corresponding channel names?',
        '6.What is the total number of likes and dislikes for each video, and what are their corresponding video names?',
        '7.What is the total number of views for each channel, and what are their corresponding channel names?',
        '8.What are the names of all the channels that have published videos in the year 2022?',
        '9.What is the average duration of all videos in each channel, and what are their corresponding channel names?',
        '10.Which videos have the highest number of comments, and what are their corresponding channel names?' ]
    
    Selected_Question = st.selectbox(' ',options=Questions)
    if Selected_Question =='1.What are the names of all the videos and their corresponding channels?':
        sql_question_1()
    if Selected_Question =='2.Which channels have the most number of videos, and how many videos do they have?':
        sql_question_2()
    if Selected_Question =='3.What are the top 10 most viewed videos and their respective channels?': 
        sql_question_3()
    if Selected_Question =='4.How many comments were made on each video, and what are their corresponding video names?':
        sql_question_4()  
    if Selected_Question =='5.Which videos have the highest number of likes, and what are their corresponding channel names?':
        sql_question_5() 
    if Selected_Question =='6.What is the total number of likes and dislikes for each video, and what are their corresponding video names?':
        st.write('**:red[Note]:- Dislike property was made private as of December 13, 2021.**')
        sql_question_6()   
    if Selected_Question =='7.What is the total number of views for each channel, and what are their corresponding channel names?':
        sql_question_7()
    if Selected_Question =='8.What are the names of all the channels that have published videos in the year 2022?':
        sql_question_8()
    if Selected_Question =='9.What is the average duration of all videos in each channel, and what are their corresponding channel names?':
        sql_question_9()
    if Selected_Question =='10.Which videos have the highest number of comments, and what are their corresponding channel names?':
        sql_question_10()

# Setting up the option "Data Visualization" in streamlit page 
if selected == "Data Visualization":
    st.subheader(':blue[Data Visualization]')
    st.markdown('''you can view statistical analyses of YouTube channels along with visualizations''')

    Option = st.selectbox(' ',['Select to view ',
                        '1.Channels with Subscriber Count',
                        '2.Channels with highest No Of Videos',
                        '3.Channels with Top 10 viewed videos',
                        '4.Channels with Total Views',
                        '5.channels with Average videos duration',
                        '6.Year wise Performance of each Channel'])
    
    if Option =='1.Channels with Subscriber Count':
        with st.spinner('Ploting in progress...'):
            def plot_ques_1():
                    mycursor.execute('''SELECT channel_name,channel_subscribers 
                                    FROM channel
                                    ORDER BY channel_subscribers DESC''')
                    out=mycursor.fetchall()
                    df=pd.DataFrame(out, columns=['Channel Name','Subscribers Count'])
                    fig = px.bar(df, x='Channel Name', y='Subscribers Count',color='Channel Name',text='Subscribers Count',
                                title='Channels with Subscriber Count')
                    st.plotly_chart(fig, use_container_width=True)
            plot_ques_1()
    
    if Option == '2.Channels with highest No Of Videos':
        def plot_ques_2():
                mycursor.execute('''SELECT channel_name,channel_video_count as Total_Videos 
                            FROM channel 
                            ORDER BY channel_video_count DESC''')
                out=mycursor.fetchall()
                df=pd.DataFrame(out, columns=['Channel Name','Total Videos'])
                fig =px.bar(df, x='Channel Name', y='Total Videos',color='Channel Name',text='Total Videos',
                            title='Channels with highest No Of Videos')
                st.plotly_chart(fig,use_container_width=True)
        plot_ques_2()
    
    if Option =='3.Channels with Top 10 viewed videos':
        def plot_ques_3():
            mycursor.execute('''SELECT channel.Channel_name,videos.Video_name, videos.View_Count as Total_Views
                            FROM videos
                            JOIN channel ON channel.Channel_id = videos.Channel_id
                            ORDER BY videos.View_Count DESC
                            LIMIT 10;''')
            out=mycursor.fetchall()
            df=pd.DataFrame(out, columns=['Channel Name','Videos Name','Total Views'])
            fig=px.bar(df, x='Total Views', y='Videos Name', color='Channel Name',text='Total Views',
                        orientation='h', title='Top 10 Viewed Videos for Each Channel')
            st.plotly_chart(fig,use_container_width=True)
        plot_ques_3()

    if Option =='4.Channels with Total Views':
        def plot_ques_4():
            mycursor.execute('''SELECT channel.channel_name,channel.channel_views as Total_views
                    FROM channel
                    ORDER BY channel.channel_views DESC  ''')
            out=mycursor.fetchall()
            df= pd.DataFrame(out, columns=['Channel Name','Total Views'])
            fig=px.bar(df, x='Total Views', y='Channel Name', color='Channel Name',text='Total Views',
                        title='Channels with Total Views')
            st.plotly_chart(fig,use_container_width=True)
        plot_ques_4()

    if Option =='5.channels with Average videos duration':
        def plot_ques_5():
            mycursor.execute('''SELECT channel.channel_name,
                            TIME_FORMAT(SEC_TO_TIME(AVG(TIME_TO_SEC(TIME(videos.Duration)))), "%H:%i:%s") AS Duration
                            FROM videos
                            JOIN channel ON videos.channel_id=channel.channel_id
                            GROUP BY channel_name ORDER BY Duration ASC ''')
            out=mycursor.fetchall()
            df= pd.DataFrame(out, columns=['Channel Name','Average Duration'])
            fig=px.bar(df, x='Channel Name', y='Average Duration', color='Channel Name',text='Average Duration',
                        title='Channels with Average Duration')
            st.plotly_chart(fig,use_container_width=True)
        plot_ques_5()

    if Option =='6.Year wise Performance of each Channel':
        def plot_ques_6():
            mycursor.execute('''SELECT DISTINCT Year(videos.publishedAt) AS Years, COUNT(videos.video_id) AS Total_videos,
                            SUM(videos.Like_Count) AS Total_Likes,
                            SUM(videos.view_count) as Total_views, 
                            SUM(videos.comment_count) AS Total_comments, channel.channel_name
                            FROM videos 
                            LEFT JOIN channel ON videos.channel_id = channel.channel_id 
                            GROUP BY channel_name, Years''')
            out=mycursor.fetchall()
            df= pd.DataFrame(out, columns=['Years','Total videos','Likes','Views','Total Comments','Channel Name'])
            fig=px.line(df, x='Years', y='Total videos', color='Channel Name',markers=True,
                        title='Year wise uploaded videos')
            st.plotly_chart(fig)

            fig1=px.line(df, x='Years', y='Likes', color='Channel Name',markers=True,
                        title='Year wise Likes')
            st.plotly_chart(fig1)

            fig2=px.line(df, x='Years', y='Views', color='Channel Name',markers=True,
                        title='Year wise Views')
            st.plotly_chart(fig2)

            fig3=px.line(df, x='Years', y='Total Comments', color='Channel Name',markers=True,
                        title='Year wise Comments')
            st.plotly_chart(fig3)
        plot_ques_6()

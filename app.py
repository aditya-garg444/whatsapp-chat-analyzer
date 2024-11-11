import streamlit as st
import helper
import preprocessor
import matplotlib.pyplot as plt
import seaborn as sns

plt.rcParams['font.family'] = 'Segoe UI Emoji'
st.set_page_config(
    page_title="WhatsApp Chat Analyzer"
)
st.sidebar.title("WhatsApp Chat Analyzer")

uploaded_file = st.sidebar.file_uploader("Choose a file")
if uploaded_file is not None:
    if uploaded_file.type not in ["text/plain"]:
        st.error("Please upload a valid text file.")
    else:
        bytes_data = uploaded_file.getvalue()
        data = bytes_data.decode("utf-8")
        df = preprocessor.preprocess(data)

        # st.dataframe(df)

        # sidebar list
        user_list = df['user'].unique().tolist()
        user_list.remove('group_notification')
        user_list.sort()
        user_list.insert(0, "Overall")

        selected_users = st.sidebar.multiselect("Show analysis wrt", user_list, default=[user_list[0]])
        # sidebar dates
        min_date = df['only_date'].min()
        max_date = df['only_date'].max()
        start_date = st.sidebar.date_input("Select start date", value=min_date, min_value=min_date, max_value=max_date)
        end_date = st.sidebar.date_input("Select end date", value=max_date, min_value=min_date, max_value=max_date)

        if st.sidebar.button("Show Analysis"):
            df = helper.get_filtered_data(selected_users, df, start_date, end_date)
            st.dataframe(df)
            # top-statistics
            num_messages, num_words, num_media_messages, num_links = helper.bring_stats(df)
            st.title("Top Statistics")
            col1, col2, col3, col4 = st.columns([1.5, 1, 1, 1])
            with col1:
                st.header("Total Messages")
                st.title(num_messages)
            with col2:
                st.header("Total Words")
                st.title(num_words)
            with col3:
                st.header("Media files")
                st.title(num_media_messages)
            with col4:
                st.header("Links Shared")
                st.title(num_links)

            # daily-timeline
            daily_timeline = helper.get_daily_timeline(df)
            st.title("Daily Timeline")
            fig, ax = plt.subplots()
            ax.plot(daily_timeline['only_date'], daily_timeline['num_messages'], color='red')
            ax.set_xlabel("Date")
            ax.set_ylabel("Number of Messages")
            plt.xticks(rotation='vertical')
            ax.set_title("Number of messages sent each day")
            st.pyplot(fig)

            # month-timeline
            month_timeline = helper.get_month_timeline(df)
            st.title("Monthly Timeline")
            fig, ax = plt.subplots()
            ax.plot(month_timeline['time'], month_timeline['num_messages'], color='green')
            ax.set_ylabel("Number of Messages")
            plt.xticks(rotation='vertical')
            ax.set_title("Number of messages sent each month")
            st.pyplot(fig)

            # activity-map
            st.title("Activity Map")
            col1, col2 = st.columns(2)
            # week-activity
            with col1:
                week_map = helper.get_week_map(df)
                st.header("WeekDay Map")
                fig, ax = plt.subplots()
                ax.bar(week_map['day_name'], week_map['num_messages'])
                ax.set_xlabel("Week Days")
                ax.set_ylabel("Number of messages")
                plt.xticks(rotation='vertical')
                ax.set_title("Total Number of messages sent on each weekday")
                st.pyplot(fig)

            # month-activity
            with col2:
                month_map = helper.get_month_map(df)
                st.header("Month Map")
                fig, ax = plt.subplots()
                ax.bar(month_map['month_name'], month_map['num_messages'], color='green')
                ax.set_xlabel("Month")
                ax.set_ylabel("Number of messages")
                plt.xticks(rotation='vertical')
                ax.set_title("Total Number of messages sent in a month")
                st.pyplot(fig)

            # Activity heat map
            st.header("Hourly Map")
            heat_map = helper.get_heat_map(df)
            fig, ax = plt.subplots()
            ax = sns.heatmap(heat_map, cmap='RdYlGn', cbar_kws={'label': 'Number of Messages'})
            st.pyplot(fig)

            if "Overall" in selected_users:
                x, new_df = helper.most_busy_users(df)
                fig, ax = plt.subplots()

                st.title('Most Busy Users')
                col1, col2 = st.columns([1, 1])
                with col1:
                    ax.bar(x.index, x.values, color='red')
                    ax.set_ylabel("Number of messages")
                    plt.xticks(rotation='vertical')
                    ax.set_title("Total Number of messages sent by top 5 users")
                    st.pyplot(fig)
                with col2:
                    st.dataframe(new_df)

            # Wordcloud creation
            df_wc = helper.create_word_cloud(df)
            st.title("Wordcloud")
            fig, ax = plt.subplots()
            ax.imshow(df_wc)
            ax.axis('off')
            st.pyplot(fig)

            # wc_image = df_wc.to_image()
            # Optionally resize the image using PIL
            # resized_image = wc_image.resize((800, 400))  # Adjust width and height as needed

            # Display the image in Streamlit using st.image
            # st.image(resized_image)

            # Most common word analysis
            most_common_df = helper.most_common_words(df)
            fig, ax = plt.subplots()
            st.title('Most common words')
            ax.barh(most_common_df[0], most_common_df[1])
            ax.set_xlabel("Number of times used")
            plt.xticks(rotation='vertical')
            ax.set_title("Most Common Words used")
            st.pyplot(fig)

            # Emoji Analysis
            emoji_df, num_emojis = helper.get_emoji_df(df)
            st.title('Emoji Analysis')
            col1, col2 = st.columns(2)
            with col1:
                st.header("Total Emojis")
                st.header(num_emojis)
                st.dataframe(emoji_df)
            with col2:
                fig, ax = plt.subplots()
                ax.pie(emoji_df[1].head(), labels=emoji_df[0].head(), autopct="%0.2f")
                ax.set_title("Top 5 Emoji usage percentage")
                st.pyplot(fig)

            # sentiment-analysis
            st.title("Sentiment Analysis")
            # st.markdown("<h1 style='text-align: center;'><u>Sentiment Analysis</u></h1>", unsafe_allow_html=True)

            # daily-analysis
            st.title("Daily Analysis")
            sentiments_daily_timeline = helper.get_sentiments_daily_timeline(df)
            fig, ax = plt.subplots()
            ax.plot(sentiments_daily_timeline['only_date'], sentiments_daily_timeline['sentiment'], color='black')
            plt.xticks(rotation='vertical')
            ax.set_ylabel("Sentiment Score")

            ax.axhline(y=0.05, color='green', linestyle='--', label='Positive (> 0.05)')
            ax.axhline(y=-0.05, color='red', linestyle='--', label='Negative (< -0.05)')
            ax.axhline(y=0, color='blue', linestyle='--', label='Neutral (-0.05 to 0.05)')
            ax.legend(loc='upper right')

            ax.set_title("Average Sentiment score on each day")
            st.pyplot(fig)

            # month-analysis
            st.title("Monthly Analysis")
            sentiments_monthly_timeline = helper.get_sentiments_monthly_timeline(df)
            fig, ax = plt.subplots()
            ax.plot(sentiments_monthly_timeline['time'], sentiments_monthly_timeline['sentiment'])
            plt.xticks(rotation='vertical')
            ax.set_ylabel("Sentiment Score")

            ax.axhline(y=0.05, color='green', linestyle='--', label='Positive (> 0.05)')
            ax.axhline(y=-0.05, color='red', linestyle='--', label='Negative (< -0.05)')
            ax.axhline(y=0, color='blue', linestyle='--', label='Neutral (-0.05 to 0.05)')
            ax.legend(loc='upper right')

            ax.set_title("Average Sentiment score each month")
            st.pyplot(fig)

            # activity-map
            st.title("Sentiment Map")
            col1, col2 = st.columns(2)

            # week-wise-sentiment-map
            with col1:
                st.header("WeekDay Map")
                sentiment_weekly_map = helper.get_sentiments_weekly_map(df)
                fig, ax = plt.subplots()
                bars = ax.bar(sentiment_weekly_map['day_name'], sentiment_weekly_map['sentiment'])
                plt.xticks(rotation='vertical')
                ax.set_ylabel("Sentiment Score")

                for bar in bars:
                    yval = bar.get_height()
                    if yval > 0.05:
                        label = 'Positive'
                        bar.set_color('green')
                    elif yval < -0.05:
                        label = 'Negative'
                        bar.set_color('red')
                    else:
                        label = 'Neutral'
                        bar.set_color('blue')

                    ax.text(bar.get_x() + bar.get_width() / 2, yval, label, ha='center', va='bottom', color='black')
                ax.set_title("Average Sentiment Score by Weekday")
                st.pyplot(fig)

            # month-wise-sentiment-map
            with col2:
                st.header("Month Map")
                sentiment_month_map = helper.get_sentiments_month_map(df)
                fig, ax = plt.subplots()
                bars = ax.bar(sentiment_month_map['month_name'], sentiment_month_map['sentiment'])
                plt.xticks(rotation='vertical')
                ax.set_ylabel("Sentiment Score")

                for bar in bars:
                    yval = bar.get_height()
                    if yval > 0.05:
                        label = 'Positive'
                        bar.set_color('green')
                    elif yval < -0.05:
                        label = 'Negative'
                        bar.set_color('red')
                    else:
                        label = 'Neutral'
                        bar.set_color('blue')

                    ax.text(bar.get_x() + bar.get_width() / 2, yval, label, ha='center', va='bottom', color='black')
                ax.set_title("Average Sentiment Score by Month")
                st.pyplot(fig)

from urlextract import URLExtract
from wordcloud import WordCloud
from collections import Counter
import pandas as pd
import emoji


def get_filtered_data(selected_users, df, start_date, end_date):
    ''' if selected_user != "Overall":
        df = df[df['user'] == selected_user] '''
    if "Overall" not in selected_users:
        df = df[df['user'].isin(selected_users)]

    df = df[(df['only_date'] >= start_date) & (df['only_date'] <= end_date)]
    return df


def bring_stats(df):
    # Number of messages
    num_messages = df.shape[0]

    # Number of words and links
    words = []
    links = []
    extractor = URLExtract()
    for mes in df['message']:
        words.extend(mes.split())
        links.extend(extractor.find_urls(mes))

    num_words = len(words)
    num_links = len(links)

    # Number of media messages
    num_media_messages = df[df['message'] == '<Media omitted>\n'].shape[0]

    return num_messages, num_words, num_media_messages, num_links


def get_daily_timeline(df):
    timeline = df.groupby('only_date').count()['message'].reset_index()
    timeline.rename(columns={'message': 'num_messages'}, inplace=True)

    return timeline


def get_month_timeline(df):
    timeline = df.groupby(['year', 'month_number', 'month_name']).count()['message'].reset_index()
    time = []
    for i in range(timeline.shape[0]):
        time.append(timeline['month_name'][i] + '-' + str(timeline['year'][i]))
    timeline['time'] = time
    timeline.drop(columns=['year', 'month_name', 'month_number'], inplace=True)
    timeline.rename(columns={'message': 'num_messages'}, inplace=True)

    return timeline


def get_week_map(df):
    messages_per_day = df.groupby('day_name').count()['message'].reset_index()

    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    messages_per_day['day_name'] = pd.Categorical(messages_per_day['day_name'], categories=day_order, ordered=True)
    messages_per_day = messages_per_day.sort_values('day_name')
    messages_per_day.rename(columns={'message': 'num_messages'}, inplace=True)

    return messages_per_day


def get_month_map(df):
    messages_per_month = df.groupby(['month_number', 'month_name']).count()['message'].reset_index()
    messages_per_month.rename(columns={'message': 'num_messages'}, inplace=True)
    messages_per_month.drop(columns=['month_number'])

    return messages_per_month


def get_heat_map(df):
    user_heatmap = df.pivot_table(index='day_name', columns='period', values='message', aggfunc='count').fillna(0)
    periods = [
        '00-1', '1-2', '2-3', '3-4', '4-5', '5-6',
        '6-7', '7-8', '8-9', '9-10', '10-11', '11-12',
        '12-13', '13-14', '14-15', '15-16', '16-17',
        '17-18', '18-19', '19-20', '20-21', '21-22',
        '22-23', '23-00'
    ]
    user_heatmap = user_heatmap.reindex(columns=periods, fill_value=0)
    days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    user_heatmap = user_heatmap.reindex(days_order)

    return user_heatmap


def most_busy_users(df):
    df = df[df['user'] != 'group_notification']
    df = df[df['message'] != '<Media omitted>\n']
    x = df['user'].value_counts().head()
    df = round((df['user'].value_counts() / df.shape[0]) * 100, 2).reset_index().rename(
        columns={'index': 'name', 'user': 'percent'})

    return x, df


def create_word_cloud(df):
    df = df[df['user'] != 'group_notification']
    df = df[df['message'] != '<Media omitted>\n']

    f = open('stop_hinglish.txt', 'r')
    stop_words = f.read()

    def remove_stop_words(message):
        y = []
        for word in message.lower().split():
            if word not in stop_words:
                y.append(word)
        return " ".join(y)

    wc = WordCloud(width=500, height=500, min_font_size=10, background_color='white')
    df['message'] = df['message'].apply(remove_stop_words)
    df_wc = wc.generate(df['message'].str.cat(sep=" "))

    return df_wc


def most_common_words(df):
    f = open('stop_hinglish.txt', 'r')
    stop_words = f.read()

    temp = df[df['user'] != 'group_notification']
    temp = temp[temp['message'] != '<Media omitted>\n']

    words = []
    for message in temp['message']:
        for word in message.lower().split():
            if word not in stop_words:
                words.append(word)

    most_common_df = pd.DataFrame(Counter(words).most_common(20))

    return most_common_df


def get_emoji_df(df):
    emojis = []
    for mes in df['message']:
        emojis.extend([c for c in mes if emoji.is_emoji(c)])

    num_emojis = len(emojis)
    emoji_df = pd.DataFrame(Counter(emojis).most_common(len(Counter(emojis))))

    return emoji_df, num_emojis


def get_sentiments_daily_timeline(df):
    sentiment_daily_timeline = df.groupby('only_date')['sentiment'].mean().reset_index()

    return sentiment_daily_timeline


def get_sentiments_monthly_timeline(df):
    sentiment_monthly_timeline = df.groupby(['year', 'month_number', 'month_name'])['sentiment'].mean().reset_index()
    time = []
    for i in range(sentiment_monthly_timeline.shape[0]):
        time.append(sentiment_monthly_timeline['month_name'][i] + '-' + str(sentiment_monthly_timeline['year'][i]))
    sentiment_monthly_timeline['time'] = time
    sentiment_monthly_timeline.drop(columns=['year', 'month_name', 'month_number'], inplace=True)

    return sentiment_monthly_timeline


def get_sentiments_weekly_map(df):
    weekly_map = df.groupby('day_name')['sentiment'].mean().reset_index()
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    weekly_map['day_name'] = pd.Categorical(weekly_map['day_name'], categories=day_order, ordered=True)
    weekly_map = weekly_map.sort_values('day_name')

    return weekly_map


def get_sentiments_month_map(df):
    weekly_map = df.groupby(['year', 'month_number', 'month_name'])['sentiment'].mean().reset_index()
    weekly_map.drop(columns=['year', 'month_number'])

    return weekly_map


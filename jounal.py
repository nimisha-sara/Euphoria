import sqlite3
from wordcloud import WordCloud


def create_table():
    connection = sqlite3.connect('journal.db')
    cursor = connection.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS JOURNAL
                        (ID  TEXT KEY     NOT NULL,
                        NAME           TEXT    NOT NULL,
                        DATE            TEXT     NOT NULL,
                        ENTRY        TEXT,
                        MOOD_RATING         TEXT,
                        STRESS_RATING   TEXT);'''
                )
    connection.commit()
    connection.close()


def insert_record(_id, name, date, entry, mood_rating, stress_rating):
    connection = sqlite3.connect('journal.db')
    cursor = connection.cursor()
    cursor.execute("insert into journal (id, name, date, entry, mood_rating, stress_rating) values (?, ?, ?, ?, ?, ?)",
            (_id, name, date, entry, mood_rating, stress_rating));
    connection.commit()
    connection.close()


def get_records_by_id(_id):
    connection = sqlite3.connect('journal.db')
    cursor = connection.cursor()
    cursor.execute("SELECT * from JOURNAL WHERE id=?", (_id,))
    result = cursor.fetchall()
    return result

def get_mood_by_day(_id):
    connection = sqlite3.connect('journal.db')
    cursor = connection.cursor()
    cursor.execute("SELECT id, date, mood_rating, stress_rating from JOURNAL WHERE id=?", (_id,))
    result = cursor.fetchall()
    return result


def mood_stress_table(_id):
    mood = [[], [], [], [], [], [], [], [], [], [], [], []]
    stress = [[], [], [], [], [], [], [], [], [], [], [], []]
    for j in range(12):
        for _ in range(31):
            mood[j].append('null')
            stress[j].append('null')

    res = get_mood_by_day(_id)
    for l in res:
        date = l[1].split('-')
        month, day = int(date[1]), int(date[2])
        mood[month-1][day-1] = l[2]
        stress[month-1][day-1] = l[3]
    return mood, stress

def check_entry(_date, _id):
    connection = sqlite3.connect('journal.db')
    cursor = connection.cursor()
    cursor.execute("SELECT * from JOURNAL WHERE date=? and id=?", (_date, _id,))
    result = cursor.fetchall()
    if len(result) == 1:
        return True # entry already complete
    return False

def word_cloud(text):
    wordcloud = WordCloud(width = 800, height = 400, colormap="BuPu", background_color='#111212', random_state=10)
    wordcloud.generate(text)
    wordcloud.to_file('static\cloud.png')

# entry = "What is Lorem Ipsum? Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry's standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled it to make a type specimen book. It has survived not only five centuries, but also the leap into electronic typesetting, remaining essentially unchanged. It was popularised in the 1960s with the release of Letraset sheets containing Lorem Ipsum passages, and more recently with desktop publishing software like Aldus PageMaker including versions of Lorem Ipsum."

_date = '2022-06-01'
check_entry(_date, '114745746400472596331')
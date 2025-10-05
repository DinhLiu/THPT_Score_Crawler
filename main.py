import os
from requests_html import HTMLSession
import psycopg2
from dotenv import load_dotenv

# Load environment variables from a .env file if present
load_dotenv()

ALL_SUBJECTS = [
    "Toán", "Ngữ văn", "Vật lý", "Hóa học", "Sinh học",
    "Lịch sử", "Địa lý", "GDCD", "Ngoại ngữ"
]

session = HTMLSession()

# Database connection parameters read from environment variables with sensible defaults
DB_NAME = os.environ.get('THPTQG_DB_NAME', 'thptqg_2025')
DB_USER = os.environ.get('THPTQG_DB_USER', 'postgres')
DB_PASSWORD = os.environ.get('THPTQG_DB_PASSWORD', 'dinhhieu21')
DB_HOST = os.environ.get('THPTQG_DB_HOST', 'localhost')
DB_PORT = int(os.environ.get('THPTQG_DB_PORT', 5432))

connection = psycopg2.connect(database=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT)
cursor = connection.cursor()

DELETE_QUERY = "DELETE FROM scores;"
cursor.execute(DELETE_QUERY)

def crawl_id(province_code, order_num):
    URL = f'https://diemthi.vnexpress.net/index/detail/sbd/{province_code:02d}{order_num:06d}/year/2025'
    try:
        r = session.get(URL, timeout=10)
    except Exception as e:
        print(f"Request error: {e}")
        return None

    if r.status_code != 200:
        return None

    student_info = r.html.find('.o-detail-thisinh', first=True)
    if student_info:
        return student_info
    return None

def get_score(student_info):
    scores = {subject: -1 for subject in ALL_SUBJECTS}
    rows = student_info.find('tbody tr')
    
    for row in rows:
        cols = row.find('td')
        subject = cols[0].text.strip()
        score = cols[1].text.strip()
        if subject in scores:
            scores[subject] = score
            
    return scores


def crawl_page():
    STOP_RANGE = 5
    for province_id in range(40, 42):
        null_page = 0
        id = 1
        while null_page < STOP_RANGE:
            student_info = crawl_id(province_id, id)
            if student_info:
                load_scores(get_score(student_info))
                id += 1
                null_page = 0
            else:
                null_page += 1

def load_scores(scores):
    QUERY = """
        INSERT INTO scores (
            math, literature, physics, chemistry, biology,
            history, geography, civic_education, foreign_language
        )
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s);
    """
    values = (
        safe_float(scores["Toán"]),
        safe_float(scores["Ngữ văn"]),
        safe_float(scores["Vật lý"]),
        safe_float(scores["Hóa học"]),
        safe_float(scores["Sinh học"]),
        safe_float(scores["Lịch sử"]),
        safe_float(scores["Địa lý"]),
        safe_float(scores["GDCD"]),
        safe_float(scores["Ngoại ngữ"])
    )
    cursor.execute(QUERY, values)
    connection.commit()

def safe_float(value):
    try:
        return float(value)
    except (ValueError, TypeError):
        return None


if __name__ == "__main__":
    crawl_page()
    cursor.close()
    connection.close()
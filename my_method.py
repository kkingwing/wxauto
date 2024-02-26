from config import CON

import pandas as pd
from sqlalchemy import create_engine
from datetime import datetime


def write_to_sql(df):
    con = create_engine(CON)
    pd.io.sql.to_sql(df, name='wechat_msg', con=con, if_exists='append', index=False)  # 追加写入


def read_sql_info_brief():
    sql = "SELECT * FROM `info_brief`;"
    con = create_engine(CON)
    df = pd.read_sql(sql=sql, con=con)  # 读取sql，获取内容。
    return df


def today():
    today = datetime.now().strftime('%Y-%m-%d')
    return today

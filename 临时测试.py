
import pandas as pd
from sqlalchemy import create_engine

CON = 'mysql://root:huanqlu0123@39.98.120.220:3306/spider?charset=utf8mb4'  # 阿里ECS，这里的编码很重要，要写为mb4

def write_to_sql(df):
    con = create_engine(CON)
    # df['说话者'] = df['说话者'].str.encode('utf8')  # 转换说话者列的编码
    pd.io.sql.to_sql(df, name='wechat_msg', con=con, if_exists='append', index=False)  # 追加写入

df = pd.read_excel('本次获取内容.xlsx')
write_to_sql(df)

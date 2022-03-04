import mysql.connector


def get_connection():
    connection=mysql.connector.connect(
        host='yh-db.clidqfc4u35c.ap-northeast-2.rds.amazonaws.com',
        database = 'yh_Scooter_DB',
        user = 'yh_Scooter_DB',
        password = '2105'
    )
    return connection
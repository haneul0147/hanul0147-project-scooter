class Config :
    JWT_SECRET_KEY = 'yh@1234'
    ACCESS_KEY = "AKIAW5QZZAQHEJCUXX5E"
    SECRET_ACCESS = "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"
    JWT_ACCESS_TOKEN_EXPIRES = False
    S3_BUCKET = "hanul0147-project-scooter-kr"
    S3_LOCATION = 'https://{}.s3.amazonaws.com/'.format(S3_BUCKET)
    client_id = "yXy8TnGociszhVoAosXY" # 개발자센터에서 발급받은 Client ID 값
    client_secret = "FjZIhhpIeN" # 개발자센터에서 발급받은 Client Secret 값
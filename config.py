class Config :
    JWT_SECRET_KEY = 'yh@1234'
    JWT_ACCESS_TOKEN_EXPIRES = False
    ACCESS_KEY = "AKIAW5QZZAQHEJCUXX5E"
    SECRET_ACCESS = "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"
    
    S3_BUCKET = "hanul0147-project-scooter"
    S3_LOCATION = 'https://{}.s3.amazonaws.com/'.format(S3_BUCKET)
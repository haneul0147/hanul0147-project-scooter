from datetime import datetime
from http import HTTPStatus
from msilib.schema import Error
from flask import Flask
from config import Config
from flask_restful import Resource, Api
from flask_restful import reqparse
from flask import Flask, request, redirect, jsonify
from werkzeug.utils import secure_filename
import os
from mysql_connection import get_connection

import boto3, botocore


ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

app = Flask(__name__)
api = Api(app)
# 환경변수 셋팅
app.config.from_object(Config)


# app.config['UPLOAD_FOLDER'] = 'files' # 데이터폴더 이미 있어야함.
# app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024


class FileUpload(Resource):
    def post(self) :

        # image, content
        #content = request.form.get('content')

        # form-data 의 file 형식에서 데이터 가져오는 경우
        if 'image' not in request.files:
            
            return {'error':'파일을 업로드 하세요'}, 400
         
        file = request.files['image']

        if file.filename == '':
            
            return {'error':'파일명을 정확히 입력하세요'}, 400

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)

            # 파일명은, 유니크하게 해줘야, S3에 업어쳐지지 않고 올라갈수있다.
            current_time = datetime.now()            
            current_time = current_time.isoformat().replace(':', '_')
            filename = 'photo_' + current_time + '.jpg'

            # 파일을 파일시스템에 저장하는 코드 : S3에 올릴거니까, 코멘트처리
            # file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            # S3에 올리는 코드 작성
            s3 = boto3.client('s3', 
                        aws_access_key_id = Config.ACCESS_KEY,
                        aws_secret_access_key = Config.SECRET_ACCESS )
            try :
                s3.upload_fileobj(
                                file, 
                                Config.S3_BUCKET,
                                filename,
                                ExtraArgs = { 'ACL' : 'public-read',
                                            'ContentType' : file.content_type}
                                )
            except Exception as e :
                return {'error' : str(e)}   

        client=boto3.client('rekognition', 'us-east-1',
                        aws_access_key_id = Config.ACCESS_KEY,
                        aws_secret_access_key = Config.SECRET_ACCESS)#boto3 로부터 클라이언트를 받음
        
        response = client.detect_labels(Image={'S3Object':{'Bucket':Config.S3_BUCKET,'Name':filename}},
        MaxLabels=1)

        try :
            # 1. DB 에 연결
            connection = get_connection()
           
            # 2. 쿼리문 만들고
            query = '''insert into scooter
                        (img_url)
                        values
                        (%s);'''
            # 파이썬에서, 튜플만들때, 데이터가 1개인 경우에는 콤마를 꼭
            # 써준다.
            record = (Config.S3_LOCATION + filename,)
            
            # 3. 커넥션으로부터 커서를 가져온다.
            cursor = connection.cursor()

            # 4. 쿼리문을 커서에 넣어서 실행한다.
            cursor.execute(query, record)

            # 5. 커넥션을 커밋한다.=> 디비에 영구적으로 반영하라는 뜻.
            connection.commit()

        except Error as e:
            print('Error ', e)
            # 6. username이나 email이 이미 DB에 있으면,
            
            return {'error' : '포스팅 에러입니다.'} , HTTPStatus.BAD_REQUEST
        finally :
            if connection.is_connected():
                cursor.close()
                connection.close()
                print('MySQL connection is closed')     


        for label in response['Labels']:
            label_dict = {}
            label_dict['Name'] = label['Name']
           

        return{'result':label_dict}

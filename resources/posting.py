from datetime import datetime
from http import HTTPStatus
from flask import Flask
import jwt
from config import Config
from flask_restful import Resource, Api
from flask_jwt_extended import jwt_required,get_jwt_identity
from flask import Flask, request, redirect, jsonify
from werkzeug.utils import secure_filename
from mysql_connection import get_connection
import os
from resources.papagoAPI import PaPago


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
   @jwt_required()
   def post(self) :

        user_id = get_jwt_identity()
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

        client=boto3.client('rekognition', 'ap-northeast-2',
                        aws_access_key_id = Config.ACCESS_KEY,
                        aws_secret_access_key = Config.SECRET_ACCESS)#boto3 로부터 클라이언트를 받음
        
        response = client.detect_labels(Image={'S3Object':{'Bucket':Config.S3_BUCKET,'Name':filename}},
        MaxLabels=12)

        try :
            # 1. DB 에 연결
            connection = get_connection()
           
            # 2. 쿼리문 만들고
            query = '''insert into scooter
                        (user_id,img_url)
                        values
                        (%s,%s);'''
            # 파이썬에서, 튜플만들때, 데이터가 1개인 경우에는 콤마를 꼭
            # 써준다.
            record = (user_id,Config.S3_LOCATION + filename)
            
            # 3. 커넥션으로부터 커서를 가져온다.
            cursor = connection.cursor()

            # 4. 쿼리문을 커서에 넣어서 실행한다.
            cursor.execute(query, record)

            # 5. 커넥션을 커밋한다.=> 디비에 영구적으로 반영하라는 뜻.
            connection.commit()

            # 6. 사진안에 있으면 안되는 이미지 이름이 있는 DB를 가져온다.
            query = '''select name from labels;'''
            
            # 7. 커넥션으로부터 커서를 가져온다.
            cursor = connection.cursor()

            # 8. 쿼리문을 커서에 넣어서 실행한다.
            cursor.execute(query)

            # select 문은 아래 내용이 필요하다.
            record_list = cursor.fetchall()
            print(record_list)
            # for 문을 통해 리스트안에 튜플을 원하는 값을 빼서 
            # 리스트로만 가져오는 코드
            record = []
            i = []
            for i in record_list:
                record.append(i[0])

        except Exception as e:
            print('Error ', e)
            # 6. username이나 email이 이미 DB에 있으면,
            
            return {'error' : '포스팅 에러입니다.'} , HTTPStatus.BAD_REQUEST
        finally :
            if connection.is_connected():
                cursor.close()
                connection.close()
                print('MySQL connection is closed')     
        
        result=[]

        for label in response['Labels']:
            # label_dict = {}
            # label_dict['Name'] = label['Name']
            # label_dict['Confidence']=label['Confidence']
            result.append(label['Name'])
            print(result)
        
        lastresult = []
        if "Scooter" in result:
            print("if 문 스쿠터 ")
            for lastresult in result :
                print("for 문 스쿠터 ")
                if lastresult in record:
                    print("if 비교문 스쿠터 ")
                    lastresult=PaPago(lastresult)
                    answer="주차하는 곳에 있으면 안되는 물체인\'"+ lastresult +"\'(이)가 있어요!!! "
                    Number = 200
                    break
                    
                else:
                    answer ="잘 주차 하셨습니다!!!"
                    Number = 201
        else : 
            answer = "전동 킥보드가 잘 보이지 않아요 다시 찍어주세요!!!"
            Number = 202



        return {'answer':answer,"Number":Number}

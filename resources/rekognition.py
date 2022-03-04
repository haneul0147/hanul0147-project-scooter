from flask import request
from flask.json import jsonify
from flask_restful import Resource
from http import HTTPStatus

from mysql_connection import get_connection
from mysql.connector.errors import Error

from flask_jwt_extended import jwt_required, get_jwt_identity

from werkzeug.utils import secure_filename

import boto3 
from config import Config

from datetime import date, datetime

class LabelResource(Resource):
    def get(self) :
        
        img_url= request.args.get('img_url')
        # http://~
        img_url_list=img_url.split('/')
        photo = img_url_list[-1]

        bucket=Config.S3_BUCKET # Cofig에 들어있는 버킷
        
        # 'us-east-1' => 내 S3의 리전
        client=boto3.client('rekognition','us-east-1' ,
                     aws_access_key_id = Config.ACCESS_KEY,
                        aws_secret_access_key = Config.SECRET_ACCESS )

        response = client.detect_labels(Image={'S3Object':{'Bucket':bucket,'Name':photo}},
        MaxLabels=10)

        print(response['Labels'])

        result = []
        for label in response['Labels']:
            label_dict = {}
            label_dict['Name'] = label['Name']
            label_dict['Confidence']=label['Confidence']
            result.append(label_dict)

        return {'result':result}
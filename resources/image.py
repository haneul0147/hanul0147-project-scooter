from flask import Flask, request
from flask.cli import run_command
from config import Config
from flask_restful import Api, Resource
from werkzeug.utils import secure_filename
import os

# 파일 확장자명을 우리가 조정할수 있다.
ALLOWED_EXTENSIONS = set( ['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'] )

def allowed_file(filename) :
    return '.' in filename and filename.rsplit('.',1)[1].lower() in ALLOWED_EXTENSIONS


class FileUploadResource(Resource) :
    def post(self) :

        print('1')
        
        if 'photo' not in request.files:
            return {'error' : '파일을 보내세요'}, 400
        
        file = request.files['photo']

        # 파일명이 정상인지 체크
        if file.filename == '' :
            return {'error' : '파일명이 이상합니다.'}, 400
        
        if file and allowed_file(file.filename) :
            filename = secure_filename(file.filename)
            file.save('./files', filename)

        return {'result':'잘 저장되었습니다.'}
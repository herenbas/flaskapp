import base64
import datetime
import json

import cv2
import face_recognition
import numpy as np
from flask import Flask, jsonify, request
from pymongo import MongoClient
from waitress import serve

app = Flask(__name__)
# ---- LOCAL DB BAĞLANTİSİ------


#HOST = 'localhost'
#PORT = 27017
#client = MongoClient(HOST, PORT)
#database = client.FaceTemps
#fData = database.dData
#pData = database.tData
#
#
# print("Sunucu Bilgisi:" + str(client.server_info()))
# print("Uygulama hazır ")

# ATLAS DB BAĞLATİSİ---------

client = MongoClient("mongodb+srv://herenbas:14081984Aa.@facecluster.sckg3.mongodb.net/FaceTemps?retryWrites=true&w=majority")
db = client.FaceTemps
fData = db.tData

print("----------------------------------------------------OKKKK-------------------------------")


@app.route('/create_template', methods=['POST'])
def create_template():
    try:

        img_base_64 = request.form['img_base_64']
        name = request.form['name']
        surname = request.form['surname']
        s_number = request.form['s_number']
        isOk = request.form['isOK']
        print(request)
        im_bytes = base64.b64decode(img_base_64)
        im_arr = np.frombuffer(im_bytes, dtype=np.uint8)
        img = cv2.imdecode(im_arr, flags=cv2.IMREAD_COLOR)

        input_image_encoding = face_recognition.face_encodings(img)[0]

        fDat = {
            "name": name,
            "surname": surname,
            "s_number": s_number,
            "isOk": isOk,
            "FaceImage": input_image_encoding.tolist(),

        }

        x = fData.insert_one(fDat)
        r_dat1 = []
        r_dat = [{
            "record_id": str(x.inserted_id),
            "insertStatus": "OK",
            "insertTime": str(datetime.datetime.now())
        }]
        r_dat1.append(fDat)

        return jsonify(r_dat)

    except RuntimeError:
        return RuntimeError


@app.route('/match', methods=['POST'])
def send_match():

        img_base64 = request.form['img_base_64']

        im_bytes = base64.b64decode(img_base64)
        im_arr = np.frombuffer(im_bytes, dtype=np.uint8)
        img = cv2.imdecode(im_arr, flags=cv2.IMREAD_COLOR)
        print(request)
        input_image_encoding = face_recognition.face_encodings(img)[0]
        print(input_image_encoding)
       # face_landmarks_list = face_recognition.face_landmarks(img)
      #  print(json.dumps(face_landmarks_list)) #yüz listesi
        known_encodings = []
        known_names = []
        known_oid = []

        cur = fData.find({})  # değişti
        for item in cur:
            known_encodings.append(np.array(item["FaceImage"]))
            known_names.append(item["pid"])  # değişti
            known_oid.append(item["_id"])
        face_distances = face_recognition.face_distance(known_encodings, input_image_encoding)

        sonuc = []
        # sonuc1 = [{}]
        for i, face_distance in enumerate(face_distances):
            if (format(face_distance < 0.5) == 'True'):
                dictionary = {'isim': known_names[i], 'eslesmeSonucu': format(face_distance < 0.5),
                              'skor': str(face_distance),
                              "Id": str(known_oid[i])}

                sonuc.append(dictionary)




        return (json.dumps(sonuc))




@app.route('/')
def hello_world():  # put application's code here
    return 'Hello World!'

    # if __name__ == '__main__':
    # app.run()


@app.route('/find_person', methods=['POST'])
def f_person():
    try:

        p_id = request.form['p_id']

        img_base64_gelen = request.form['img_base_64']

        jsonString = ""

        im_bytes = base64.b64decode(img_base64_gelen)
        im_arr = np.frombuffer(im_bytes, dtype=np.uint8)


        img = cv2.imdecode(im_arr, flags=cv2.IMREAD_COLOR)  #beklenen_şekilde

        input_image_encoding = face_recognition.face_encodings(img)[0]


        quer = {"pid": p_id}
        f_data = fData.find(quer)
        known_encodings = []
        known_oid = []
        for r_data in f_data:
            known_encodings.append(np.array(r_data['FaceImage']))
            known_oid.append(r_data["_id"])
        face_distances = face_recognition.face_distance(known_encodings, input_image_encoding)

        #print(known_encodings)
        #sonuc = []

        for i, face_distance in enumerate(face_distances):
            if format(face_distance < 0.5) == 'True':
                dictionary = {'isim': p_id, 'eslesmeSonucu': format(face_distance < 0.5), 'skor': str(face_distance),
                              "Id": str(known_oid[i])}
                jsonString = json.dumps(dictionary, indent=4)
                # sonuc.append("isim: "+p_id)
                # sonuc.append("match_result:" + format(face_distance < 0.5))
                # sonuc.append("confidance:" + str(face_distance))
                return jsonString
                print(jsonStirng)

                #return json.dumps(dictionary)
            else:
                jsonString = "ESLESME YOK"

    except RuntimeError:
        jsonString = str(RuntimeError)
        #return jsonify(str(RuntimeError))

        # return (json.dumps(str(r_data['FaceImage'])))
    return json.dumps("ESLESME YOK")
@app.route('/analiz', methods=["POST"])
def analiz():
    img_base64_image = request.form['img_base_64']


  #  sonuc = deepface.DeepFace.analyze(img_base64_image)
  #  return json.dumps(sonuc)
@app.route('/enroll_person', methods=['POST'])
def enroll_person():
    img_base_64 = request.form['img_base_64']
    pid = request.form['p_id']

    im_bytes = base64.b64decode(img_base_64)
    im_arr = np.frombuffer(im_bytes, dtype=np.uint8)
    img = cv2.imdecode(im_arr, flags=cv2.IMREAD_COLOR)

    input_image_encoding = face_recognition.face_encodings(img)[0]

    pDat = {
        "pid": pid,
        "FaceImage": input_image_encoding.tolist(),

    }

    x = fData.insert_one(pDat)
    r_dat1 = []
    r_dat = [{
        "record_id": str(x.inserted_id),
        "insertStatus": "OK",
        "insertTime": str(datetime.datetime.now())
    }]
    r_dat1.append(pDat)

    return jsonify(r_dat)


#serve(app, host='45.76.43.212', port=9099, threads=5)
serve(app, host="127.0.0.1", port="9099", threads=5)

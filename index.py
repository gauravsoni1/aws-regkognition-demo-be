from flask import Flask, json, request, jsonify, make_response
from flask import Response
import boto3
from botocore.exceptions import ClientError
from flask.helpers import flash
from werkzeug.utils import secure_filename
from flask_cors import CORS, cross_origin
# from werkzeug.wrappers import response

api = Flask(__name__)
CORS(api)
rekognition_client = boto3.client("rekognition")
s3_client = boto3.client('s3')
S3 = boto3.resource("s3")
bucket = S3.Bucket("python-project-gaurav")


@api.route("/images", methods=['GET', 'OPTIONS'])
def get_images():
    allS3Objects = bucket.objects.all()
    s3Objs = []
    for obj in allS3Objects:
        tempObj = {}
        tempObj['name'] = obj.key
        tempObj['size'] = obj.size
        s3Objs.append(tempObj)
    response = jsonify(s3Objs)
    return response


@api.route('/images', methods=['POST'])
def upload_file():
    if ("file" not in request.files):
        return Response("{'msg':'File not found in the request'}", status=400, mimetype='application/json')

    file = request.files['file']
    if (file.filename == ""):
        return "Please select a file"

    if file:
        file.filename = secure_filename(file.filename)
        output = uploadFileToS3(file)
        return str(output)


# Find facial features
@api.route("/face/detect", methods=['POST'])
def detectFace():
    jsonData = request.json
    response = rekognition_client.detect_faces(
        Attributes=["ALL"],
        Image={
            'S3Object': {
                'Bucket': 'python-project-gaurav',
                'Name': jsonData['file']
            }
        }
    )
    return jsonify(response)

# Create a collection to index the faces
@api.route("/collection", methods=["POST"])
def createCollection():
    response = rekognition_client.create_collection(
        CollectionId="faces",
        Tags={}
    )
    return jsonify(response)

# Index the faces in a image
@api.route("/indexface", methods=['POST'])
def indexFace():
    response = rekognition_client.index_faces(
        CollectionId='faces',
        ExternalImageId= "GroupPhoto2.jpeg",
        Image={'S3Object': {
            'Bucket': 'python-project-gaurav', 'Name': 'GroupPhoto2.jpeg'}},
        QualityFilter="AUTO",
        DetectionAttributes=['ALL'])
    return jsonify(response)

# Find the faces in the collection
@api.route("/findface", methods=["POST"])
def findFace():
    response = rekognition_client.search_faces_by_image(
        CollectionId='faces',
        Image={'S3Object': {'Bucket': 'python-project-gaurav',
                            'Name': 'original_gaurav.jpeg'}},
    )
    return jsonify(response)


def uploadFileToS3(file):
    try:
        # filename = file.filename
        s3_client.upload_fileobj(
            file, "python-project-gaurav", file.filename)
        return "File upload success"
    except (ClientError) as e:
        return False


if __name__ == '__main__':
    api.run()

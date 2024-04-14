from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Animals, Images, Videos
from .serializers import *
from gridfs import GridFS
from django.http import HttpResponse
from io import BytesIO
from PIL import Image
from .mongo_connect import db
from .models import User
from bson.objectid import ObjectId
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth.hashers import make_password
from rest_framework import status
from difflib import SequenceMatcher
import jwt
import datetime
import cv2
import numpy as np
import nltk
from django.db.models.query import QuerySet
from django.utils import encoding
import base64
import nltk
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
# Authentication/Authorization API's


class RegisterViewAPI(APIView):
    def post(self, request):
        first_name = request.data['first_name']
        last_name = request.data['last_name']
        username = request.data['username']
        password = request.data['password']
        email = request.data['email']
        # user_type = request.data['user_type']
        user_type = 1
        hashed_pwd = make_password(password=password)
        user = User(username=username,
                    password=hashed_pwd,
                    user_type=user_type,
                    email=email,
                    first_name=first_name, last_name=last_name
                    )
        user.save()
        response = Response()
        response.data = {
            'detail': 'New User added.'
        }
        return response


class LoginViewAPI(APIView):
    def post(self, request):
        username = request.data['username']
        password = request.data['password']
        user = User.objects.filter(username=username).first()

        if user is None:
            raise AuthenticationFailed('User Not Found!')

        if not user.check_password(password):
            raise AuthenticationFailed('Incorrect Password!')

        payload = {
            'id': user.id,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=60),
            'iat': datetime.datetime.utcnow()
        }

        serializer = UserSerializer(user)
        print(serializer.data)

        token = jwt.encode(payload, 'secret', algorithm='HS256')
        response = Response()
        response.set_cookie(key='jwt', value=token, httponly=True)

        response.data = {
            'jwt': token,
            'user_details': serializer.data
        }

        return response


class isAuthAPI(APIView):
    def get(sef, request):
        token = request.COOKIES.get('jwt')
        if not token:
            raise AuthenticationFailed('Unauthenticated!')

        try:
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Unauthenticated!')

        user = User.objects.filter(id=payload['id']).first()
        serializer = UserSerializer(user)
        return Response({
            'response': serializer.data
        })


class LogoutView(APIView):
    def post(self, request):
        response = Response()
        response.delete_cookie('jwt')
        response.data = {
            'message': 'Logout Successful'
        }
        return response


class UserViewAPI(APIView):
    def authenticate(self, request):
        token = request.COOKIES.get('jwt')
        if not token:
            raise AuthenticationFailed('Unauthenticated!')

        try:
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Unauthenticated!')

        return payload

    def cursorToDict(self, cursor):
        columns = [col[0] for col in cursor.description]
        return [
            dict(zip(columns, row))
            for row in cursor.fetchall()
        ]


class InsertAnimalsAPI(APIView):
    def post(self, request):
        try:
            c_name = request.data['common_name']
            s_name = request.data['scientific_name']
            classi = request.data['classification']
            habitat = request.data['habitat']
            diet = request.data['diet']
            desc = request.data['desc']
            life = request.data['life']
            threats = request.data['threats']
            animal = Animals(commonName=c_name, scientificName=s_name, classification=classi,
                             habitat=habitat, diet=diet, physicalDescription=desc, lifespan=life, threats=threats)
            animal.save()
            response = Response()
            response.data = {
                'detail': 'New animal added.'
            }
            return response

        except Exception as e:
            print(e)
            response = Response()
            response.status_code = 405
            response.data = {
                'detail': 'Could not add new animal.'
            }
            return response


class UploadImageAPI(APIView):
    def post(self, request):
        image = request.FILES.get('img')
        caption = request.data.get('caption')
        # contributor = request.data.get('contributer')
        contributor = 1
        new_image = Images(image=image, contributer=contributor, caption=caption)
        new_image.save()
        return Response({'status': 'success'}, status=status.HTTP_201_CREATED)

        # list = [{
        #     "file": con....
        #     ""
        # }]

        # return Response({'status': list}, status=status.HTTP_201_CREATED)


class GetImageAPI(APIView):
    def post(self, request):
        # TODO: Get this id by running some query
        id = request.data.get('id')
        # file_id = '64316e345f1f7547d488bbf4'
        img = Images.objects.get(ImageId=id)
        file_id = str(img.image)
        fs = GridFS(db)
        file = fs.get(ObjectId(str(file_id)))
        file_content = file.read()
        # print(file_content)
        # img = Image.open(BytesIO(file_content))
        # img.show()
        # response = HttpResponse(file_content, content_type='image/jpeg')
        # response['Content-Disposition'] = 'attachment; filename=%s' % file_id
        image_base64 = base64.b64encode(file_content).decode('utf-8')
        response = Response()
        response.data = {
            "file_content": image_base64,
            "caption": img.caption,
            "contributer": img.contributer,
            "reviewer": img.reviewer,
            'content_type': 'image/*'
        }
        return response


class UploadArticleAPI(APIView):
    def post(self, request):
        title = request.data.get('title')
        content = request.data.get('content')
        article = Articles(title=title, article=content)
        article.save()
        return Response({'status': 'success'}, status=status.HTTP_201_CREATED)


class GetArticleAPI(APIView):
    def post(self, request):
        # TODO: Take id from request, return the title and content of the article
        id = request.data.get('id')
        print(id)
        article = Articles.objects.get(ArticleId=id)
        response = Response()
        response.data = {
            'title': article.title,
            'content': article.article,
            'createdAt': article.date,
            'contributor': article.contributer,
            'reviewer': article.reviewer
        }
        return response


class UploadVideoAPI(APIView):
    def post(self, request):
        # Create a new Video instance from the request data
        video = request.FILES.get('video')
        caption = request.data.get('caption')
        # contributor = request.data.get('contributer')
        # thumbnail = request.FILES.get('thumbnail')

        video = Videos(
            video_file=video,
            caption=caption,
            # contributor=1
            # thumbnail=thumbnail
        )

        video.save()
        return Response({'status': 'success'}, status=status.HTTP_201_CREATED)


class GetVideoAPI(APIView):
    def post(self, request):
        # TODO: Get this id by running some query
        id = request.data.get('id')
        # file_id = '6432c9ed5c5a7e968c754441'
        vid = Videos.objects.get(VideoId=id)
        file_id = vid.video_file
        fs = GridFS(db)
        file = fs.get(ObjectId(file_id))
        file_content = file.read()

        # Return the file data as a response
        # response = HttpResponse(file_content, content_type='video/mp4')
        # response['Content-Disposition'] = 'attachment; filename=%s' % file_id
        video_base64 = base64.b64encode(file_content).decode('utf-8')
        response = Response()
        response.data = {
            "file_content": video_base64,
            "caption": vid.caption,
            "contributer": vid.contributor,
            "reviewer": vid.reviewer,
            'content_type': 'video/*'
        }
        return response


class SearchAPI(APIView):
    def similar(a, b):
        return SequenceMatcher(None, a, b).ratio()

    def post(self, request):
        print(request.data)
        query = request.data.get('query')
        # content_type = request.data.get('content_type')
        type = request.data.get('type')
        # nltk.download('averaged_perceptron_tagger')
        # nltk.download('punkt')
        # function to test if something is a noun
        def is_noun(pos): return pos[:2] == 'NN'
        # do the nlp stuff
        tokenized = nltk.word_tokenize(query)
        nouns = [word for (word, pos) in nltk.pos_tag(tokenized) if is_noun(pos)]
        print(nouns)

        matched_animals_id = []
        matched_plants_id = []
        arts_id = []
        imgs_id = []
        vids_id = []
        for noun in nouns:
            noun = noun.lower()
            print(noun)

            # images
            if type == 2:
                for image in list(Images.objects.all()):
                    if image.tags is None:
                        continue
                    if SearchAPI.similar(noun, image.tags) > 0.6:
                        print(noun+" "+image.tags)
                        imgs_id.append(image.ImageId)
            # videos
            elif type == 3:
                for video in list(Videos.objects.all()):
                    if video.tags is None:
                        continue
                    if SearchAPI.similar(noun, video.tags) > 0.6:
                        print(noun+" "+video.tags)
                        vids_id.append(video.VideoId)
            # articles
            else:
                for article in list(Articles.objects.all()):
                    if article.tags is None:
                        continue
                    if SearchAPI.similar(noun, article.tags) > 0.6:
                        print(noun+" "+article.tags)
                        arts_id.append(article.ArticleId)

                print("animals")
                for animal in list(Animals.objects.all()):
                    # print("inside")
                    # print(animal.commonName)
                    if animal.commonName is None:
                        continue

                    if SearchAPI.similar(noun, animal.commonName) > 0.6:
                        print(noun+" "+animal.commonName)
                        matched_animals_id.append(animal.AnimalId)
                print("plants")
                for plant in list(Plants.objects.all()):
                    if plant.commonName is None:
                        continue

                    if SearchAPI.similar(noun, plant.commonName) > 0.6:
                        print(noun+" "+animal.commonName)
                        matched_plants_id.append(plant.PlantId)
        result = []

        if type == 2:
            imgs_id = list(set(imgs_id))
            print(imgs_id)

            for id in imgs_id:
                img = Images.objects.get(ImageId=id)
                fs = GridFS(db)
                print(img.image)
                file = fs.get(ObjectId(str(img.image)))
                print("here")
                file_content = file.read()
                image_base64 = base64.b64encode(file_content).decode('utf-8')
                print("here2")
                tempdict = {
                    "id": img.ImageId,
                    "file_content": image_base64,
                    "caption": img.caption,
                    "contributor": img.contributer,
                    "reviewer": img.reviewer
                }
                result.append(tempdict)

        elif type == 3:
            vids_id = list(set(vids_id))
            print(vids_id)

            for id in vids_id:
                # print("here")
                vid = Videos.objects.get(VideoId=id)
                # print("here2")
                fs = GridFS(db)
                print(vid.video_file)
                file = fs.get(ObjectId(str(vid.video_file)))

                file_content = file.read()
                # print(file_content)
                video_base64 = base64.b64encode(file_content).decode('utf-8')
                # print(video_base64)
                # print(file_content)
                tempdict = {
                    "id": vid.VideoId,
                    "file_content": video_base64,
                    "caption": vid.caption,
                    "contributor": vid.contributor,
                    "reviewer": vid.reviewer
                }
                result.append(tempdict)

        else:
            articles_list = []
            arts_id = list(set(arts_id))
            for id in arts_id:
                article = Articles.objects.get(ArticleId=id)
                tempdict = {
                    "id": id,
                    "content": article.article,
                    "title": article.title,
                    "createdAt": article.date,
                    "contributor": article.contributer
                }
                articles_list.append(tempdict)

            matched_animals_id = list(set(matched_animals_id))
            matched_plants_id = list(set(matched_plants_id))
            animals = list(Animals.objects.filter(AnimalId__in=matched_animals_id).values())
            plants = list(Plants.objects.filter(PlantId__in=matched_plants_id).values())
            result = {
                "articles": articles_list,
                "info": {"animals": animals,
                         "plants": plants}
            }

            # Retrieve articles/images/videos whose tag_id matches with any of the above id in lists
        # tag="mango"
        # images=Images.objects.filter(tags__icontains=tag)
        # print(images.count())

        print("out of loop")
        # print(matched_animals_id)
        # print(matched_plants_id)
        # response = HttpResponse(content=file_content, content_type='image/jpeg')
        # response['Content-Disposition'] = 'attachment; filename=%s' % file_id
        # return response
        return Response({'status': result}, status=status.HTTP_201_CREATED)


# class InsertTag(APIView):
#     def post(self, request):
#         type = request.data.get('type')
#         objId = request.data.get('objId')
#         tags = list(request.data.get('tags'))
#         obj = Tags(type=type,objId=objId,tags=tags)
#         obj.save()
#         return Response({'status': "success"}, status=status.HTTP_201_CREATED)


# show animal list and show plant list

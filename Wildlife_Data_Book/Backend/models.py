from django.db import models
# from djongo import models
from gridfs import GridFS
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from .mongo_connect import db


class User(AbstractUser):
    USER_TYPE_CHOICES = (
        (1, 'Contributor'),
        (2, 'Organization'),
        (3, 'Expert_Reviewer')
    )

    # Redundant fields start
    first_name = models.CharField(max_length=64, null=True)
    last_name = models.CharField(max_length=64, null=True)
    email = models.CharField(max_length=64, null=True)
    is_staff = models.CharField(max_length=64, null=True)
    is_active = models.IntegerField(default=True)
    date_joined = models.CharField(max_length=64, null=True)
    # Redundant fields end

    # id = models.AutoField(primary_key=True)
    user_type = models.PositiveSmallIntegerField(choices=USER_TYPE_CHOICES)
    password = models.CharField(max_length=256)
    username = models.CharField(max_length=64, unique=True)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['user_type']


class Animals(models.Model):
    AnimalId = models.AutoField(primary_key=True)
    commonName = models.CharField(max_length=255)
    scientificName = models.CharField(max_length=255)
    classification = models.CharField(max_length=255)
    habitat = models.CharField(max_length=255)
    diet = models.CharField(max_length=255)
    physicalDescription = models.CharField(max_length=255)
    lifespan = models.CharField(max_length=255)
    threats = models.CharField(max_length=255)


class Plants(models.Model):
    PlantId = models.AutoField(primary_key=True)
    commonName = models.CharField(max_length=255)
    scientificName = models.CharField(max_length=255)
    classification = models.CharField(max_length=255)
    habitat = models.CharField(max_length=255)
    uses = models.CharField(max_length=255)
    physicalDescription = models.CharField(max_length=255)
    lifespan = models.CharField(max_length=255)
    threats = models.CharField(max_length=255)

# class Intermediate_string(models.Model):
#     data=models.CharField(primary_key=True,max_length=255,blank=True)

#     class Meta:
#         managed=False

# class Intermediate_int(models.Model):
#     type =models.IntegerField()
#     objId=models.IntegerField()

#     class Meta:
#         abstract=True

# class Tags(models.Model):
#     id = models.AutoField(primary_key=True)
#     type = models.IntegerField()  # 0 for animals, 1 for plants
#     objId = models.IntegerField() # Id of animal/plant object
#     tags = models.ArrayField(model_container=Intermediate_string)  # tags


class Images(models.Model):
    fs = GridFS(db)
    ImageId = models.AutoField(primary_key=True)
    caption = models.CharField(max_length=255)
    image = models.FileField()
    tags = models.CharField(max_length=255)
    numId = models.IntegerField()
    contributer = models.IntegerField()
    reviewer = models.IntegerField()
    reviewed = models.BooleanField()
    finalised = models.BooleanField()
    date = models.DateField()

    def save(self, *args, **kwargs):
        if self.pk is None:
            fs = GridFS(db)
            file_id = fs.put(self.image.file, filename=self.image.name)
            self.image = str(file_id)
        super().save(*args, **kwargs)

    # def set_tags(self, tag_list):
    #     self.tags=tag_list
    #     self.save()

    # def get_tags(self):
    #     return self.tags


class Videos(models.Model):
    VideoId = models.AutoField(primary_key=True)
    caption = models.CharField(max_length=255)
    video_file = models.FileField()
    tags = models.CharField(max_length=255)
    numId = models.IntegerField()
    contributor = models.IntegerField()
    reviewer = models.IntegerField()
    reviewed = models.BooleanField()
    finalised = models.BooleanField()
    date = models.DateField()
    thumbnail = models.FileField()

    def save(self, *args, **kwargs):
        if self.pk is None:
            # Connect to MongoDB and get GridFS instance
            fs = GridFS(db)
            # Save the video file to GridFS
            file_id = fs.put(self.video_file.read(), filename=self.video_file.name)
            # Update the video model to store the GridFS file ID
            self.video_file = str(file_id)

            # thumbnail
            thumbnail_file_id = fs.put(self.thumbnail.read(), filename=self.thumbnail.name)
            self.thumbnail = str(thumbnail_file_id)

        super().save(*args, **kwargs)

    # def set_tags(self, tag_list):
    #     self.tags=tag_list
    #     self.save()

    # def get_tags(self):
    #     return self.tags


class Articles(models.Model):
    ArticleId = models.AutoField(primary_key=True)
    # caption = models.CharField(max_length=255)
    title = models.TextField()
    article = models.TextField()
    tags = models.CharField(max_length=255)
    numId = models.IntegerField()
    contributer = models.IntegerField()
    reviewer = models.IntegerField()
    reviewed = models.BooleanField()
    finalised = models.BooleanField()
    date = models.DateField()

    # def set_tags(self, tag_list):
    #     self.tags=tag_list
    #     self.save()

    # def get_tags(self):
    #     return self.tags


class Feedback(models.Model):
    TYPE_CHOICES = {
        (1, 'Article'),
        (2, 'Image'),
        (3, 'Video')
    }
    id = models.AutoField(primary_key=True)
    contendId = models.IntegerField()
    type = models.SmallIntegerField(choices=TYPE_CHOICES)
    feedback = models.CharField(max_length=255)

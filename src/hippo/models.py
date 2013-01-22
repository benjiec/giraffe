from django.db import models
from django.db import utils
import giraffe.features
import datetime
import re


class Feature_Type(models.Model):
    type = models.CharField(max_length=64)

    def __unicode__(self):
        return self.type

    def save(self):
        if self.type not in Feature_Type_Choices.labels():
          raise Exception("Invalid type: %s, expecting one of %s" % (
                            self.type,
                            ' '.join(Feature_Type_Choices.labels())))

    class Meta:
        verbose_name = "Feature Type"


class Feature(models.Model):

    type = models.ForeignKey(Feature_Type)
    name = models.CharField(max_length=32,db_index=True)
    sequence = models.TextField()
    last_modified = models.DateTimeField(auto_now=True,db_index=True)

    def save(self):
        self.sequence = giraffe.features.clean_dna_sequence(self.sequence, True)
        return super(Feature,self).save()

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ('type', 'name')


class Feature_Database(models.Model):

    name = models.CharField(max_length=64,unique=True)
    features = models.ManyToManyField(Feature, blank=True, null=True)
    last_built = models.DateTimeField(null=True,blank=True)

    def __unicode__(self):
       return self.name

    class Meta:
        verbose_name = "Feature Database"


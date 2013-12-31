from django.db import models

# Create your models here.
class PWMController(models.Model):
  description = models.CharField(max_length = 128)
  i2c_bus = models.IntegerField()
  i2c_address = models.IntegerField()
  frequency = models.IntegerField()

  class Meta(object):
    unique_together = ("i2c_bus", "i2c_address")

class PWMPort(models.Model):
  controller = models.ForeignKey( PWMController )
  port = models.IntegerField()
  high = models.IntegerField()
  low  = models.IntegerField()

  class Meta(object):
    unique_together = ("controller", "port")


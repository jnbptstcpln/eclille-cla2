import re

from django.db import models
from django.contrib.auth.models import User
from cla_web.utils import current_school_year


class UserInfos(models.Model):
    """
        The UserInfo model extends user by adding new properties
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="infos")
    cursus = models.CharField(max_length=100, null=True)
    promo = models.IntegerField()

    class Colleges(models.TextChoices):
        G1 = 'g1', 'G1'
        G2 = 'g2', 'G2'
        G3 = 'g3', 'G3'
        IE1_IE2 = 'ie1/ie2', 'IE1/IE2'
        IE3 = 'ie3', 'IE3'
        IE4 = 'ie4', 'IE4'
        IE5 = 'ie5', 'IE5'

    def is_from_centrale(self):
        return re.match(r'^G\d.*', self.cursus)

    def is_from_iteem(self):
        return re.match(r'^IE\d.*', self.cursus)

    @property
    def college(self):
        if self.promo <= current_school_year()+1:
            return self.Colleges.G3 if self.is_from_centrale() else self.Colleges.IE5
        elif self.promo == current_school_year()+2:
            return self.Colleges.G2 if self.is_from_centrale() else self.Colleges.IE4
        elif self.promo == current_school_year()+3:
            return self.Colleges.G1 if self.is_from_centrale() else self.Colleges.IE3
        elif self.promo == current_school_year()+4:
            return self.Colleges.IE1_IE2
        elif self.promo == current_school_year()+5:
            return self.Colleges.IE1_IE2

from django.db import models


class Story(models.Model):
    name = models.CharField(max_length=2000, null=False)
    source = models.URLField(max_length=2000, null=False)
    profile_choices = (
        ('kindle', 'Kindle 201..'),
        ('kindle_dx', 'Kindle DX'),
        ('kindle_fire', 'Kindle Fire'),
        ('kindle_oasis', 'Kindle Oasis 1,2'),
        ('kindle_pw', 'Kindle Paperwhite 1,2'),
        ('kindle_pw3', 'Kindle Paperwhite 3'),
        ('kindle_voyage', 'Kindle Voyage')
    )
    profile = models.CharField(max_length=20,
                               choices=profile_choices,
                               default='kindle_pw3')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.name)

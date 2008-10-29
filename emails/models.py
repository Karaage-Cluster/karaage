from django.db import models

class EmailTemplate(models.Model):
    name = models.CharField(max_length=100, help_text="Do not change")
    description = models.CharField(max_length=200)
    subject = models.CharField(max_length=100)
    body = models.TextField(help_text="DONT PAY MUCH ATTENTION TO THIS - Variables available:<br/>{{ requester }} - person requesting<br/>{{ reciever }} - person recieveing the email<br/>{{ project }} - project<br/>{{ site }} - link to site")
    
    class Meta:
        permissions = (
            ("send_email", "Can send email"),
        )

    def __unicode__(self):
        return self.name
    

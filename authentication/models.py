from django.db import models
from django.contrib.auth.models import User
import uuid
from django.db import models
from django.utils import timezone
import rsa
import base64

class BaseModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class Hashkeys(BaseModel):
  ip_address = models.GenericIPAddressField(unique=True)
  public_key = models.BinaryField()
  private_key = models.BinaryField()
  @staticmethod
  def create_hash(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    try:
      instance = Hashkeys.objects.get(ip_address=ip)
    except:
      (pubkey, privkey) = rsa.newkeys(1024)
      instance = Hashkeys.objects.create(ip_address=ip,public_key=pubkey.save_pkcs1(format='PEM'),private_key=privkey.save_pkcs1(format='PEM'))
      instance.save()
    return instance.public_key
  @staticmethod
  def decript(request,base64_str):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    encrypted = base64.b64decode(base64_str)
    try:
      instance = Hashkeys.objects.get(ip_address=ip)
      privkey = rsa.PrivateKey.load_pkcs1(instance.private_key)
      message = rsa.decrypt(encrypted, privkey).decode('utf8')
      return message
    except rsa.pkcs1.DecryptionError:
        return None;

class AdminModel(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=50, blank=True)
    def __str__(self):
      return str(self.user.username)
      

class TeacherModel(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE,related_name="teacher")
    role = models.CharField(max_length=100, blank=True)
    def __str__(self):
      return str(self.user.first_name)+" "+str(self.user.last_name)
      

# class StudentModel(BaseModel):
#     user = models.OneToOneField(User, on_delete=models.CASCADE)
#     def __str__(self):
#       return str(self.user.username)
      

class ClassModel(BaseModel):
    name = models.CharField(max_length=50, blank=True)
    def __str__(self):
      return str(self.name)

class SubjectModel(BaseModel):
  name = models.CharField(max_length=50, blank=True)
  class_name = models.ForeignKey(ClassModel,on_delete=models.CASCADE)
  teacher = models.ForeignKey(TeacherModel,blank=True,on_delete=models.SET_NULL,null=True)
  def __str__(self):
      return str(self.name)
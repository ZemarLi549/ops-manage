from rest_framework.renderers import JSONRenderer
from . import encoders


class MyJSONRenderer(JSONRenderer):
    encoder_class = encoders.JSONEncoder

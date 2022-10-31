from flask import Blueprint

visual_perception=Blueprint('visual_perception', __name__,template_folder="templates", static_folder="static")
from . import views


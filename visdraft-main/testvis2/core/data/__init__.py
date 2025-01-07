"""Data module for handling data sources"""
from flask import Blueprint

data_bp = Blueprint('data', __name__)

from . import routes
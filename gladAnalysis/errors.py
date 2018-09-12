"""ERRORS"""
from flask import jsonify


class Error(Exception):
    """Generic error that we can return to user"""

    def __init__(self, detail, status=400):
        self.detail = detail
        self.status = status

    @property
    def serialize(self):
        return jsonify(errors=[{
            'status': self.status,
            'detail': self.detail
        }]), self.status

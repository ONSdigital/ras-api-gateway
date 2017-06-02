from flask import request, jsonify, make_response
from ras_api_gateway.proxy_router import router

def get_secret(*args, **kwargs):
    """Test endpoint"""
    return make_response(jsonify("This is a secret"), 200)

def register(details):
    """Test endpoint"""
    code, msg = router.register(details)
    return make_response(jsonify(msg), code)

def unregister(host):
    """Test endpoint"""
    return make_response(jsonify("unregister"), 200)

def status(*args, **kwargs):
    """Test endpoint"""
    code, msg = router.status()
    return make_response(jsonify(msg), code)

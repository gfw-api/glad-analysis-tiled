from flask import jsonify

from gladAnalysis.routes.api.v1.glad_router import glad_analysis_endpoints
from gladAnalysis.routes.api.v1.custom_geom_router import custom_geom_endpoints


def error(status=400, detail='Bad Request'):
    return jsonify(errors=[{
        'status': status,
        'detail': detail
    }]), status

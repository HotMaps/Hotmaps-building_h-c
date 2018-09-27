"""
This is the list of method that will be used by the api
"""

import logging

import os

from extensions.api.api import Namespace
from flask_restplus_patched import Resource

from . import schemas, parameters
from ..common import custom_fields

from ..common.FEAT.F23_dh_grid import F_23
from werkzeug import secure_filename

log = logging.getLogger(__name__)
api = Namespace('buildinghc', 'building hc')

@api.route('/f23')
@api.route('/Heat-Density-Maps/Scaling-HDM')
class F107(Resource):
    @api.response(schemas.F23Schema())
    @api.parameters(parameters.F23Parameter())

    def post(self, args):
        path = "/data/modules/common"
        data_warehouse = path + os.sep + 'AD/data_warehouse'
        payload = args['payload']
        region = payload['region']
        start_year = payload['start_year']
        last_year = payload['last_year']
        depr_time = payload['depreciation_time']
        dh_connection_rate_1st_year = payload['dh_connection_rate_1st_year']
        dh_connection_rate_last_year = payload['dh_connection_rate_last_year']
        accumulated_energy_saving = payload['accumulated_energy_saving']
        interest_rate = payload['interest_rate']
        grid_cost_ceiling = payload['grid_cost_ceiling']
        inShapefile = data_warehouse + os.sep + region + '.shp'
        case_study = [inShapefile, start_year, last_year, depr_time,
                      accumulated_energy_saving, dh_connection_rate_1st_year,
                      dh_connection_rate_last_year, interest_rate, grid_cost_ceiling]
        output_dir = path + os.sep + 'Outputs/' + str(grid_cost_ceiling)+'_'+str(dh_connection_rate_last_year)+'_'+str(accumulated_energy_saving)
        
        asdf = secure_filename(str(grid_cost_ceiling)+'_'+str(dh_connection_rate_last_year)+'_'+str(accumulated_energy_saving))
        output_dir = os.path.join(path, 'Outputs', asdf)

        try:
            f_23_ret = F_23.execute(case_study, output_dir)
        except:
            f_23_ret = {"attention": "something went wrong"}

        # response need to be defined in schema
        return {"response": f_23_ret}

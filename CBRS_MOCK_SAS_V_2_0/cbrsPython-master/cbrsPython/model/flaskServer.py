from flask import Flask,request,jsonify,g,redirect,url_for,abort
from controllers.ENodeBController import ENodeBController
import Utils.Consts as consts
from collections import OrderedDict
import json
from controllers.CLIUtils.enums import StepStatus
from __builtin__ import True
app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

enodeBController = ENodeBController(None)
@app.route('/v2.0/<typeOfCalling>/',methods=['POST'])
def sent_Flask_Req_To_Server(typeOfCalling):
    '''
    the method get any post request sent from the CBSD that the url includes '/cbsd/<typeOfCalling>/' 
    send to the engine the request and after verification at the engine side sent the response from the engine 
    to the CBSD side    
    '''
    logger = enodeBController.engine.loggerHandler
    json_dict = json.loads(request.data,object_pairs_hook=OrderedDict)
    logger.start_Step(json_dict,typeOfCalling)
    while (not enodeBController.engine.check_Last_Step_In_All_CBRS()):
        response = enodeBController.linker_Between_Flask_To_Engine(json_dict,typeOfCalling)
        if("ERROR" in str(response)): ### if engine get an error while validate the request the flask will sent a shutdown call for the flask server
            return redirect(url_for(consts.SHUTDOWN_FUNCTION_NAME, validationMessage=str(response)))
        logger.finish_Step(response,typeOfCalling,StepStatus.PASSED)           
        return jsonify(response)
    return redirectShutDownDueToFinishOfTest()
        
@app.route('/shutdown', methods=['GET', 'POST'])
def shutdown():
    '''
    the method get a validation error message and send 400 response to CBSD with the current message  
    or send message that all the steps of the current test had been finished and you need to upload a new csv file 
    '''
    logger = enodeBController.engine.loggerHandler
    app.app_context()
    func = request.environ.get(consts.NAME_OF_SERVER_WERKZUG)
    func()
    if("ERROR" in str(request.args['validationMessage'])):
        logger.finish_Step("the server shot down because :  " + str(request.args['validationMessage']),False,StepStatus.FAILED)
        return abort(400, str(request.args['validationMessage']))
    return consts.SERVER_SHUT_DOWN_MESSAGE + consts.TEST_HAD_BEEN_FINISHED_FLASK

def redirectShutDownDueToFinishOfTest():
        return redirect(url_for(consts.SHUTDOWN_FUNCTION_NAME, validationMessage=consts.TEST_HAD_BEEN_FINISHED_FLASK))
import ssl
def runFlaskServer(host,port,ctx):
    app.run(host,port,threaded=True,ssl_context=ctx)
        

    




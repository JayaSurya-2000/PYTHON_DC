from .main import app, auth, queryInterestes, sendVerificationEmail, get_ai_response, get_the_image, assist1_id, assist2_id, assist3_id
from flask import request, Response
import simplejson
import json
import random
import hashlib
from datetime import datetime as dt
from .userManagement import *

startTime = dt.now()


@app.route('/')
@auth.login_required
def welcome():
    """Displays welcome message"""
    return 'Welcome to home page'


@app.route('/status')
def status():
    """Used for health check"""
    return 'Server is up!'

@app.route('/uptime')
def uptime():
    """Displays a message with server up time.
    It is used for health check and no authentication is required for this endpoint"""

    currentTime = dt.now()
    tDelta = currentTime - startTime
    deltaHours = int(tDelta.seconds / 3600)
    deltaMinz = int((tDelta.seconds % 3600) / 60)
    deltaSeconds = (tDelta.seconds % 3600) % 60
    return f'Server is up and running for: {deltaHours}hrs {deltaMinz}min {deltaSeconds}sec'


@app.route('/get-interests', methods=['GET', 'POST'])
@auth.login_required
def getInterests():
    """
    Get interests for a given person (email_md5)
    :return:
    """

    if request.method == 'GET':
        args = request.args
        first_name = args.get('f_name', None)
        last_name = args.get('l_name', None)
        email_address = args.get('email', None)
        email_md5 = args.get('email_md5', None)
        zync_cookie = args.get('zync_cookie', '')
    elif request.method == 'POST':
        if not request.data:
            return "[ERROR]: Request should contain data which is used as input"
        else:
            reqJ = json.loads(request.data)
        first_name = reqJ.get('f_name', None)
        last_name = reqJ.get('l_name', None)
        email_address = reqJ.get('email', None)
        email_md5 = reqJ.get('email_md5', None)
        zync_cookie = reqJ.get('zync_cookie', '')


    if email_address:
        email_value = hashlib.md5(email_address.strip().lower().encode('utf-8')).hexdigest()
    elif email_md5:
        email_value = email_md5
    else:
        email_value = hashlib.md5('test@test.com'.strip().lower().encode('utf-8')).hexdigest()

    # from_summary = 'y' if args.get('from_summary', None) is None else args.get('from_summary')
    from_summary = 'y'
    return queryInterestes(email_value, zync_cookie, from_summary)
    


@app.route('/get-persona', methods=['GET', 'POST'])
@auth.login_required
def getPersona():
    """
    Get the marketing strategy from openAI along with image.
    """
    
    persona_var = {}

    if request.method == 'GET':
        args = request.args
        email_address = args.get('email', None)
        email_md5 = args.get('email_md5', None)
    elif request.method == 'POST':
        if not request.data:
            return "[ERROR]: Request should contain data which is used as input"
        else:
            reqJ = json.loads(request.data)
        email_address = reqJ.get('email', None)
        email_md5 = reqJ.get('email_md5', None)
    
    if email_address:
        email_value = hashlib.md5(email_address.strip().lower().encode('utf-8')).hexdigest()
    elif email_md5:
        email_value = email_md5
    else:
        email_value = hashlib.md5('test@test.com'.strip().lower().encode('utf-8')).hexdigest()

    interests = queryInterestes(email_value)
    persona_var['interests'] = json.loads(interests)
    persona_var['persona_var'] = get_ai_response(assist1_id, interests)

    return simplejson.dumps(persona_var)
    

@app.route('/get-marketing-strategy', methods=['GET', 'POST'])
@auth.login_required
def getMarketingStrategy():
    """
    Get the marketing strategy from openAI along with image.
    """
    mk_stat = {}
    if request.method == 'GET':
        args = request.args
        persona_var = args.get('persona_var', None)
        product = args.get('product', None)
    elif request.method == 'POST':
        if not request.data:
            return "[ERROR]: Request should contain data which is used as input"
        else:
            reqJ = json.loads(request.data)
        persona_var = reqJ.get('persona_var', None)
        product = reqJ.get('product', None)
    
    prompt = f"{persona_var}\n\nProduct:{product}"
    
    mk_stat['marketing_strategy'] =  get_ai_response(assist2_id, prompt)
    return simplejson.dumps(mk_stat)


@app.route('/get-image', methods=['GET', 'POST'])
@auth.login_required
def getImage():
    if request.method == 'GET':
        args = request.args
        persona_var = args.get('persona_var', None)
        marketing_strategy = args.get('marketing_strategy', None)
        product = args.get('product', None)
    elif request.method == 'POST':
        if not request.data:
            return "[ERROR]: Request should contain data which is used as input"
        else:
            reqJ = json.loads(request.data)
        persona_var = reqJ.get('persona_var', None)
        marketing_strategy = reqJ.get('marketing_strategy', None)
        product = reqJ.get('product', None)

    img_data = {}
    prompt_for_prompt_for_img = f"{persona_var}\n\n{marketing_strategy}\n\nProduct:{product}"
    img_prompt = get_ai_response(assist3_id, prompt_for_prompt_for_img)

    print(img_prompt)

    img_data['img_url'] = get_the_image(img_prompt)
    
    return simplejson.dumps(img_data)


@app.route('/send-verification-email', methods=['GET', 'POST'])
@auth.login_required
def verifyEmail():
    """
    Get interests for a given person (email_md5)
    :return:
    """
    
    if request.method == 'GET':
        args = request.args
        n = args.get('n', None)
        e = args.get('e', None)
        sendersEmail = args.get('sendersEmail', None)
        sendersName = args.get('sendersName', None)
    elif request.method == 'POST':
        if not request.data:
            return "[ERROR]: Request should contain data which is used as input"
        else:
            reqJ = json.loads(request.data)
        n = reqJ.get('n', None)
        e = reqJ.get('e', None)
        sendersEmail = reqJ.get('sendersEmail', None)
        sendersName = reqJ.get('sendersName', None)

    return sendVerificationEmail(sendersName, sendersEmail, n, e)



# @app.route('/get-piq-brands', methods=['POST'])
# @auth.login_required
# def getPIQBrands():
#     """Returns top upward/downward trending piq-brands filtered by:
#         1. Current and previous week average brand visit.
#         2. Percent change.
#         3. Vertical (optional)."""
#
#     if not request.data:
#         return "[ERROR]: Request should contain data which is used as input"
#     else:
#         reqJ = json.loads(request.data)
#     trend = reqJ['trend']
#     if trend:
#         if trend == 'up':
#             trendSD = 'GRT_SD'
#         elif trend == 'down':
#             trendSD = 'LST_SD'
#         else:
#             return "Trend parameter should be 'up' or 'down'."
#     else:
#         return "[ERROR]: 'trend' key is mandatory in the request data."
#     cutoff = reqJ.get('cutoff', 5)
#     limit = reqJ.get('limit', 100000)
#     vertical = reqJ.get('vertical', None)
#     finalResult = []
#     if not vertical:
#         query = f"SELECT " \
#                 f"BRAND_ID AS ID, MASTER_METRIC_TYPE AS METRIC_TYPE, MASTER_METRIC_NAME AS METRIC_NAME, " \
#                 f"MASTER_VERTICAL AS VERTICAL, PERCENT AS CURRENT_WOW_PERCENT, MASTER_POS_ACTION AS POS_ACTION, " \
#                 f"MASTER_NEG_ACTION AS NEG_ACTION " \
#                 f"FROM DCHUB.BI.PIQ_VISITS_WEEKLY_MP_SPARK_API " \
#                 f"WHERE MASTER_METRIC_TYPE = 'piq_brand' AND CURR_WEEK_AVG_BRAND_VISIT > 5000 AND " \
#                 f"PREV_WEEK_AVG_BRAND_VISIT > 5000 AND {trendSD} = TRUE AND ABS(PERCENT) > {cutoff} AND ABS(PERCENT) <= 300" \
#                 f"ORDER BY ABS(PERCENT) DESC LIMIT {limit}"
#     else:
#         query = f"SELECT " \
#                 f"BRAND_ID AS ID, MASTER_METRIC_TYPE AS METRIC_TYPE, MASTER_METRIC_NAME AS METRIC_NAME, " \
#                 f"MASTER_VERTICAL AS VERTICAL, PERCENT AS CURRENT_WOW_PERCENT, MASTER_POS_ACTION AS POS_ACTION, " \
#                 f"MASTER_NEG_ACTION AS NEG_ACTION " \
#                 f"FROM DCHUB.BI.PIQ_VISITS_WEEKLY_MP_SPARK_API " \
#                 f"WHERE MASTER_METRIC_TYPE = 'piq_brand' AND CURR_WEEK_AVG_BRAND_VISIT > 5000 AND " \
#                 f"PREV_WEEK_AVG_BRAND_VISIT > 5000 AND {trendSD} = TRUE AND ABS(PERCENT) > {cutoff} AND ABS(PERCENT) <= 300" \
#                 f"MASTER_VERTICAL = '{vertical}' " \
#                 f"ORDER BY ABS(PERCENT) DESC LIMIT {limit}"
#     qRes = execute_db_query(query)
#     for rec in qRes:
#         entry = {}
#         for key in rec.keys():
#             entry[key] = rec[key]
#         finalResult.append(entry)
#     return simplejson.dumps(finalResult)
#
#
# @app.route('/get-piq-verticals', methods=['POST'])
# @auth.login_required
# def getPIQVerticals():
#     """Returns top upward/downward trending piq-verticals filtered by:
#             1. Current and previous week average brand visit.
#             2. Percent change.
#             3. Vertical (optional)."""
#
#     if not request.data:
#         return "[ERROR]: Request should contain data which is used as input"
#     else:
#         reqJ = json.loads(request.data)
#     trend = reqJ['trend']
#     if trend:
#         if trend == 'up':
#             trendSD = 'GRT_SD'
#         elif trend == 'down':
#             trendSD = 'LST_SD'
#         else:
#             return "Trend parameter should be 'up' or 'down'."
#     else:
#         return "[ERROR]: 'trend' key is mandatory in the request data."
#     cutoff = reqJ.get('cutoff', 5)
#     limit = reqJ.get('limit', 100000)
#     vertical = reqJ.get('vertical', None)
#     finalResult = []
#     if not vertical:
#         query = f"SELECT " \
#                 f"PIQ_CAT_ID AS ID, MASTER_METRIC_TYPE AS METRIC_TYPE, MASTER_METRIC_NAME AS METRIC_NAME, " \
#                 f"MASTER_VERTICAL AS VERTICAL, PERCENT AS CURRENT_WOW_PERCENT, MASTER_POS_ACTION AS POS_ACTION, " \
#                 f"MASTER_NEG_ACTION AS NEG_ACTION " \
#                 f"FROM DCHUB.BI.PIQ_VERTICAL_SIZE_WEEKLY_MP_SPARK_API " \
#                 f"WHERE MASTER_METRIC_TYPE = 'piq_category' AND {trendSD} = TRUE AND " \
#                 f"ABS(PERCENT) > {cutoff} AND ABS(PERCENT) <= 300 ORDER BY ABS(PERCENT) DESC LIMIT {limit}"
#     else:
#         query = f"SELECT " \
#                 f"PIQ_CAT_ID AS ID, MASTER_METRIC_TYPE AS METRIC_TYPE, MASTER_METRIC_NAME AS METRIC_NAME, " \
#                 f"MASTER_VERTICAL AS VERTICAL, PERCENT AS CURRENT_WOW_PERCENT, MASTER_POS_ACTION AS POS_ACTION, " \
#                 f"MASTER_NEG_ACTION AS NEG_ACTION " \
#                 f"FROM DCHUB.BI.PIQ_VERTICAL_SIZE_WEEKLY_MP_SPARK_API " \
#                 f"WHERE MASTER_METRIC_TYPE = 'piq_category' AND {trendSD} = TRUE AND " \
#                 f"ABS(PERCENT) > {cutoff} AND ABS(PERCENT) <= 300 AND MASTER_VERTICAL = '{vertical}' ORDER BY ABS(PERCENT) DESC LIMIT {limit} "
#     qRes = execute_db_query(query)
#     for rec in qRes:
#         entry = {}
#         for key in rec.keys():
#             entry[key] = rec[key]
#         finalResult.append(entry)
#     return simplejson.dumps(finalResult)
#
#
# @app.route('/get-zcode-segments', methods=['POST'])
# @auth.login_required
# def getPIQSegments():
#     """Returns top upward/downward trending segments/segment-categories filtered by:
#             1. Current and previous week average brand visit.
#             2. Percent change.
#             3. Metric type.
#             4. Vertical (optional)."""
#
#     if not request.data:
#         return "[ERROR]: Request should contain data which is used as input"
#     else:
#         reqJ = json.loads(request.data)
#     trend = reqJ['trend']
#     if trend:
#         if trend == 'up':
#             trendSD = 'GRT_SD'
#         elif trend == 'down':
#             trendSD = 'LST_SD'
#         else:
#             return "Trend parameter should be 'up' or 'down'."
#     else:
#         return "[ERROR]: 'trend' key is mandatory in the request data."
#     metricType = reqJ.get('metricType', 'zcode_brand')
#     cutoff = reqJ.get('cutoff', 5)
#     limit = reqJ.get('limit', 100000)
#     vertical = reqJ.get('vertical', None)
#     finalResult = []
#     if trendSD == 'GRT_SD':
#         trendClause = 'PERCENT > 0'
#         audienceSize = '20000'
#     elif trendSD == 'LST_SD':
#         trendClause = 'LST_SD = TRUE'
#         audienceSize = '100000'
#
#     if not vertical:
#         query = f"SELECT SEGMENT_CODE AS ID, MASTER_METRIC_TYPE AS METRIC_TYPE, MASTER_METRIC_NAME AS METRIC_NAME, " \
#                     f"MASTER_VERTICAL AS VERTICAL, PERCENT AS CURRENT_WOW_PERCENT, MASTER_POS_ACTION AS POS_ACTION, " \
#                     f"MASTER_NEG_ACTION AS NEG_ACTION " \
#                 f"FROM DCHUB.BI.SEGMENT_SIZE_WEEKLY_MP_SPARK_API " \
#                     f"WHERE MASTER_METRIC_TYPE = '{metricType}' AND CURR_WEEK_AVG_AUDIENCE_SIZE > {audienceSize} AND " \
#                         f"PREV_WEEK_AVG_AUDIENCE_SIZE > {audienceSize} AND " \
#                         f"{trendClause} AND ABS(PERCENT) > {cutoff} AND ABS(PERCENT) <= 300 " \
#                     f"ORDER BY ABS(PERCENT) DESC LIMIT {limit}"
#     else:
#         query = f"SELECT SEGMENT_CODE AS ID, MASTER_METRIC_TYPE AS METRIC_TYPE, MASTER_METRIC_NAME AS METRIC_NAME, " \
#                     f"MASTER_VERTICAL AS VERTICAL, PERCENT AS CURRENT_WOW_PERCENT, MASTER_POS_ACTION AS POS_ACTION, " \
#                     f"MASTER_NEG_ACTION AS NEG_ACTION " \
#                 f"FROM DCHUB.BI.SEGMENT_SIZE_WEEKLY_MP_SPARK_API " \
#                     f"WHERE MASTER_METRIC_TYPE = '{metricType}' AND MASTER_VERTICAL = '{vertical}' AND " \
#                         f"CURR_WEEK_AVG_AUDIENCE_SIZE > {audienceSize} AND " \
#                         f"PREV_WEEK_AVG_AUDIENCE_SIZE > {audienceSize} AND " \
#                         f"{trendClause} AND ABS(PERCENT) > {cutoff} AND ABS(PERCENT) <= 300 " \
#                     f"ORDER BY ABS(PERCENT) DESC LIMIT {limit}"
#
#     qRes = execute_db_query(query)
#     for rec in qRes:
#         entry = {}
#         for key in rec.keys():
#             entry[key] = rec[key]
#         finalResult.append(entry)
#     # finalResult.append({'query': f"{query}"})
#     return simplejson.dumps(finalResult)

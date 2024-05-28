from flask import Flask
from flask_httpauth import HTTPBasicAuth
from snowflake.connector import connect as sfConnect, DictCursor
import configparser
from passlib.apps import custom_app_context
import os
import simplejson
import json
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import boto3
from botocore.exceptions import ClientError
from openai import OpenAI
from time import sleep

assist1_id = 'asst_2bvy3VtOLpyUCyMyxRlJDH26'
assist2_id = 'asst_xyI167E4CxaF5parpBQ1qw8q'
assist3_id = 'asst_8A3UHo8x65BN28LaPcuWh4j0'

# Get the credetials from AWS secrets manager
def get_param(param_name, region_name=None):
    region_name = "us-east-1" if region_name is None else region_name

    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name='ssm',
        region_name=region_name
    )

    try:
        param = client.get_parameter(Name=param_name, WithDecryption=True)
    except ClientError as e:
        raise e
    
    # To avoid nasty behviour of json as python accepts only double quotes in the json string
    param_value = json.loads(param['Parameter']['Value'].replace('\'', '"'))
    return param_value


#Fetching DB credentials
db_param_name = '/zeta-global/bizops/dcis/prod/tools/zoe_chatbot/db/sf'
db_creds = get_param(db_param_name)

#Fetching SMTP credentials
smtp_param_name = '/zeta-global/bizops/dcis/prod/tools/zoe_chatbot/smtp'
smtp_creds = get_param(smtp_param_name)

#Fetching openAI api-key
open_ai_api_key_name = '/zeta-global/bizops/dcis/prod/tools/zoe_chatbot/openai/api_key'
open_ai_api_key = get_param(open_ai_api_key_name)

def sendVerificationEmail(recieverName, recieverEmail, n, e):

    smtp_host = smtp_creds['smtp_host']
    smtp_port = smtp_creds['smtp_port']
    smtp_user = smtp_creds['smtp_user']
    smtp_passwd = smtp_creds['smtp_passwd']

    context = ssl.create_default_context()
    smtpObj = smtplib.SMTP(smtp_host, smtp_port)
    smtpObj.ehlo()
    smtpObj.starttls(context=context)
    smtpObj.ehlo()
    smtpObj.login(user=smtp_user, password=smtp_passwd)

    sender = 'Chatbotzeta <zx-reporting@zetainteractive.com>'
    receivers = recieverEmail.split(',')

    message = MIMEMultipart('alternative')
    message['Subject'] = 'ChatBotZeta - Please validate your email.'
    message['From'] = sender
    message['To'] = ','.join(receivers)
    message.add_header('mailer_id', 'CHATBOT')
    html_body = f"""
    <html><body>
    <div style="background-color:#e6eaff;padding:20px;border-radius:20px">
    <h4>Hi {recieverName},</h4>
    <h4>I have received a request to validate your email on <a href="https://chatbotzeta.com" target="_blank">chatbotzeta.com</a>. To confirm the request and proceed further, please click on  <a href="https://staging.d2flbniour34r2.amplifyapp.com/openApi-v2?n={n}&e={e}&v=1" target="_blank">this link</a>. If you have not requested this, please ignore this message.</h4>
    <h4>Waiting For You,<br/><a href="https://chatbotzeta.com" target="_blank">ChatBotZeta</h4>
    </div>
    </body></html>
    """
    message.attach(MIMEText(html_body, 'html'))
    try:
        smtpObj.sendmail(sender, receivers, message.as_string())
        return "Message has been sent."
    except Exception as e:
        return f"Message could not be sent. Mailer Error: {e}"
    finally:
        smtpObj.quit()


def execute_db_query(query):
    with sfConnect(
        user=db_creds['username'],
        password=db_creds['password'],
        account=db_creds['accountid']
        ) as ctx:
        cs = ctx.cursor(DictCursor)
        cs.execute(query)
        return cs.fetchall()

def queryInterestes(email_value=None, zync_cookie=None, from_summary='y'):
    if from_summary == 'y' or from_summary == 'Y':
        query = f"select (select listagg(distinct segment_name, ',') from dchub.temp.zoe_dc_intender_audience_no_seg_name where email_md5 = '{email_value}') as zcodes, (select listagg(distinct p_code_name, ',') from DCHUB.TEMP.ZOE_CHATBOAT_PCODE_90DAY_FINAL_WITH_NAME where email_md5 = '{email_value}') as pcodes, (select listagg(distinct fieldshortdescription, ',') from dchub.temp.zoe_chatboat_tu_data where email_md5 = '{email_value}') as tu_ids, (select listagg(distinct segment_name, ',') from dchub.temp.ZOE_ZYNC_COOKIE_FINAL where cookie = '{zync_cookie}') as zync_cookie_ids"
    else:
        # TODO: The following query is just a dummy. It is no used and also, don't use it. We should remove this as of now until decided further.
        query = f"select segment_name from datacloud_external.dcp_private.datacloud_intender_audience_state_orc where date_part = 'dt=2023-01-01' and email_md5 = {email_value} ORDER by last_date_seen DESC, segment_score DESC LIMIT 5"

    qRes = execute_db_query(query)
    interests = {}
    # values = []
    for rec in qRes:
        interests['zcodes'] = rec['ZCODES'].split(',')
        interests['pcodes'] = rec['PCODES'].split(',')
        interests['tu_ids'] = rec['TU_IDS'].split(',')
        interests['zync_cookie_ids'] = rec['ZYNC_COOKIE_IDS'].split(',')
    # pcodes = ['Competence','Technical','Corporate','Successful','Leader','Confident','Down-to-earth','Family-oriented','Small-town','Honest','Sincere','Sophistication','Real','Wholesome','Original','Cheerful','Sentimental','Friendly','Daring','Trendy','Exciting','Cool','Sincerity','Young','Imaginative','Unique','Up-to-date','Independent','Contemporary','Upper-class','Glamorous','Good-looking','Charming','Excitement','Feminine','Smooth','Outdoorsy','Masculine','Western','Tough','Rugged','Ruggedness','Reliable','Hard-working','Secure','Intelligent']
    # final_pcodes = random.sample(pcodes, 5)
    # interests['pcodes'] = final_pcodes
    return simplejson.dumps(interests)


def get_ai_response(assist_id, in_msg):

    # Create an opeaAI client
    client = OpenAI(api_key=open_ai_api_key['api_key'])

    # Create a thread
    thread = client.beta.threads.create()

    try:
        # Create a message and add it to thread
        client.beta.threads.messages.create(
            thread_id = thread.id,
            role='user',
            content=in_msg
        )

        run = client.beta.threads.runs.create(
            thread_id = thread.id,
            assistant_id = assist_id
        )

        while run.status != 'completed':
            run = client.beta.threads.runs.retrieve(
                thread_id = thread.id,
                run_id = run.id
            )
            sleep(2)
            

        # Retrive messages added by the assistant to the thread
        all_messages = client.beta.threads.messages.list(
            thread_id = thread.id
        )

        # pattern = re.compile(r'.*Generated Image: (.*)\n\n.*')
        # m = pattern.match(all_messages.data[0].content[0].text.value)
        # print(m.group(1))

        return all_messages.data[0].content[0].text.value
    
    finally:
        # Deleting the thread
        client.beta.threads.delete(thread_id=thread.id)
        client.close()



def get_the_image(img_prompt):

    # Create an opeaAI client
    client = OpenAI(api_key=open_ai_api_key['api_key'])

    img = client.images.generate(
        model='dall-e-3',
        prompt=img_prompt,
        size='1024x1024',
        quality='standard',
        n=1,
    )
    client.close()

    return img.data[0].url


app = Flask(__name__)
auth = HTTPBasicAuth()

@auth.verify_password
def check_password(user, passwd):
    if user:
        fetchUserQuery = "SELECT PASSWORD FROM DCHUB.BI.MP_SPARK_API_USERS WHERE USER_NAME = '{}'".format(user)
        q_res = execute_db_query(fetchUserQuery)
        if len(q_res) > 0:
            return custom_app_context.verify(passwd, q_res[0]['PASSWORD'])
        else:
            return False

@auth.get_user_roles
def getUserRoles(user):
    if user:
        fetchRolesQuery = "SELECT ROLE FROM DCHUB.BI.MP_SPARK_API_USERS WHERE USER_NAME = '{}'".format(user['username'])
        q_res = execute_db_query(fetchRolesQuery)
        if len(q_res) > 0:
            return q_res[0]['ROLE'].split(',')
        else:
            return False
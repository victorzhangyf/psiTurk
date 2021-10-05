from __future__ import generator_stop
from flask import Blueprint, jsonify, make_response, request, current_app as app, send_file
from flask.json import JSONEncoder
from flask_restful import Api, Resource
from psiturk.dashboard import login_required
from psiturk.services_manager import psiturk_services_manager as services_manager
from psiturk.models import Participant, Campaign, Hit
from psiturk.experiment import app
from psiturk.psiturk_exceptions import *
from psiturk.amt_services_wrapper import WrapperResponse
from psiturk.amt_services import MTurkHIT
from psiturk.db import db_session
from psiturk.models import Base as DBModel
from apscheduler.job import Job
from apscheduler.triggers.base import BaseTrigger
import datetime
import pytz
import json
from io import BytesIO
import zipfile
from pytz.tzinfo import BaseTzInfo

api_blueprint = Blueprint('api', __name__, url_prefix='/api')

class CustomApi(Api):
    """
    For custom error handling
    """
    def handle_error(self, exception):

        message = exception.message if (hasattr(exception, 'message') and
                                        exception.message) else str(exception)
        return jsonify({
            'exception': type(exception).__name__,
            'message': message
        }), 400

api = CustomApi()


@api_blueprint.errorhandler(Exception)
def handle_exception(exception):
    message = exception.message if (hasattr(exception, 'message') and
                                    exception.message) else str(exception)
    # raise exception
    return jsonify({
        'exception': type(exception).__name__,
        'message': message
    }), 400


class PsiturkJSONEncoder(JSONEncoder):  # flask's jsonencoder class
    def default(self, obj):
        if isinstance(obj, (PsiturkException, WrapperResponse)):
            return obj.to_dict()

        if isinstance(obj, Exception):
            return {
                'exception': type(obj).__name__,
                'message': str(obj)
            }

        if isinstance(obj, datetime.timedelta):
            return str(obj)

        if isinstance(obj, MTurkHIT):
            return obj.__dict__

        if isinstance(obj, DBModel):
            return obj.object_as_dict()

        if isinstance(obj, (Job, BaseTrigger)):
            return obj.__getstate__()

        if isinstance(obj, BaseTzInfo):
            return str(obj)

        return JSONEncoder.default(self, obj)


api_blueprint.json_encoder = PsiturkJSONEncoder


@api.representation('application/json')
def output_json(data, code, headers=None):
    resp = make_response(jsonify(data), code)
    resp.headers.extend(headers or {})
    return resp


@api_blueprint.before_request
@login_required
def before_request():
    pass


class ServicesManager(Resource):
    def get(self):
        _return = {
            'mode': 'unavailable',
            'codeversion': 'unavailable',
            'amt_balance': 'unavailable',
            'aws_access_key_id': 'unavailable'
        }
        try:
            _return['mode'] = services_manager.mode
            _return['codeversion'] = services_manager.codeversion
            _return['amt_balance'] = services_manager.amt_balance
            _return['aws_access_key_id'] = services_manager.config.get('AWS Access',
                                                                       'aws_access_key_id')
        except PsiturkException:
            pass
        return _return


class AssignmentList(Resource):
    def get(self, assignment_id=None):
        all_workers = [worker.object_as_dict(filter_these=['datastring']) for worker in
                       Participant.query.filter(Participant.mode != 'debug').all()]
        return all_workers


class AssignmentsAction(Resource):


    # GET: For downloading data
    def get(self, action):
        """
        """

        # ACTION: Download data
        #  assignment: the assignment id for which to download data
        if action == 'datadownload':
            assignmentid = request.args.get('assignmentid')
            fields = ['question_data', 'trial_data', 'event_data']
            participant = Participant.query.filter(Participant.assignmentid == assignmentid).first()
            mem_file = BytesIO()
            with zipfile.ZipFile(mem_file, 'w', compression = zipfile.ZIP_DEFLATED) as zf:
                write_data_to_zip(participant, fields, zf)
            mem_file.seek(0)
            return send_file(mem_file, attachment_filename = participant.workerid + '_data.zip', as_attachment=True)


    def post(self, action=None):
        """
        """

        # ACTION: Approve
        #  assignments: a list of assignment ids to approve
        #  all_studies: approve in mturk even if not in local db?
        if action == 'approve':
            assignments = request.json['assignments']
            all_studies = request.json['all_studies']
            _return = []
            for assignment in assignments:
                try:
                    response = services_manager.amt_services_wrapper \
                        .approve_assignment_by_assignment_id(assignment, all_studies)
                    _return.append({
                        "assignment": assignment,
                        "success": response.status == "success",
                        "message": str(response)})
                except Exception as e:
                    _return.append({
                        "assignment": assignment,
                        "success": False,
                        "message": str(e)})
            return _return

        # ACTION: Reject
        #  assignments: a list of assignment ids to reject
        #  all_studies: reject in mturk even if not in local db?
        elif action == 'reject':
            assignments = request.json['assignments']
            all_studies = request.json['all_studies']
            _return = []
            for assignment in assignments:
                try:
                    response = services_manager.amt_services_wrapper \
                        .reject_assignment(assignment, all_studies)
                    _return.append({
                        "assignment": assignment,
                        "success": response.status == 'success',
                        "message": str(response)})
                except Exception as e:
                    _return.append({
                        "assignment": assignment,
                        "success": False,
                        "message": str(e)})
            return _return

        # ACTION: Bonus
        #  assignments: a list of assignment ids to bonus
        #  all_studies: bonus in mturk even if not in local db?
        #  amount: a float value to bonus, or "auto" for auto-bonusing from local
        #  reason: a string reason to send to the worker
        elif action == 'bonus':
            assignments = request.json['assignments']
            all_studies = request.json['all_studies']
            amount = request.json['amount']
            reason = request.json['reason']
            _return = []
            for assignment in assignments:
                try:
                    resp = services_manager.amt_services_wrapper \
                        .bonus_assignment_for_assignment_id(
                            assignment, amount, reason, all_studies)
                    _return.append({
                        "assignment": assignment,
                        "success": resp.status == 'success',
                        "message": str(resp)})
                except Exception as e:
                    _return.append({
                        "assignment": assignment,
                        "success": False,
                        "message": str(e)})
            return _return

        # ACTION: Data
        #  assignments: a list of assignment ids to retrieve data for
        elif action == 'data':
            assignments = request.json['assignments']
            _return = {}
            for assignment_id in assignments:
                p = Participant.query.filter_by(assignmentid=assignment_id).first()
                q_data = json.loads(p.datastring)["questiondata"]
                e_data = json.loads(p.datastring)["eventdata"]
                t_data = json.loads(p.datastring)["data"]
                jsonData = {
                    'question_data': [{
                        'questionname': q,
                        'response': json.dumps(q_data[q])} for q in q_data],
                    'event_data': [{
                        'eventtype': e['eventtype'],
                        'interval': e['interval'],
                        'value': e['value'],
                        'timestamp': e['timestamp']} for e in e_data],
                    'trial_data': [{
                        'current_trial': t['current_trial'],
                        'dateTime': t['dateTime'],
                        'trialdata': json.dumps(t['trialdata'])} for t in t_data]
                }
                _return[assignment_id] = jsonData
            return _return

        elif action == 'approve_all':
            response = services_manager.amt_services_wrapper.approve_all_assignments()
            if not response.success:
                raise response.exception
            return response.data['results']

        elif action == 'bonus_all':
            if 'reason' not in data or not data['reason']:
                raise APIException(message='bonus reason is missing!')

            response = services_manager.amt_services_wrapper.bonus_all_local_assignments(
                amount='auto', reason=data['reason'])
            if not response.success:
                raise response.exception
            return response.data['results'], 201

        else:
            raise APIException(message='action `{}` not recognized!'.format(action))


class HitResource(Resource):
    def patch(self, hit_id):
        data = request.json
        if 'is_expired' in data and data['is_expired']:
            response = services_manager.amt_services_wrapper.expire_hit(hit_id)
            if not response.success:
                raise response.exception
        if 'action' in data:
            if data['action'] == 'approve_all':
                response = services_manager.amt_services_wrapper.approve_assignments_for_hit(hit_id)
                if not response.success:
                    raise response.exception
        return services_manager.amt_services_wrapper.get_hit(hit_id).data, 201

    def delete(self, hit_id):
        response = services_manager.amt_services_wrapper.delete_hit(hit_id)
        if not response.success:
            raise response.exception
        return '', 204


class HitList(Resource):
    def get(self, status=None):
        if status == 'active':
            hits = services_manager.amt_services_wrapper.get_active_hits().data
        else:
            hits = services_manager.amt_services_wrapper.get_all_hits().data
        hits = [hit.__dict__ for hit in hits]
        return hits


class HitsAction(Resource):
    def get(self, action=None):
        if action == 'expire_all':
            response = services_manager.amt_services_wrapper.expire_all_hits()
            if response.success:
                return response.data['results'], 201
            else:
                raise response.exception

        elif action == 'delete_all':
            response = services_manager.amt_services_wrapper.delete_all_hits()
            if response.success:
                return response.data['results'], 201
            else:
                raise response.exception

        elif action == 'approve_all':
            hits = services_manager.amt_services_wrapper.get_all_hits().data

            _return = []
            for hit in hits:
                hit_response = services_manager.amt_services_wrapper.approve_assignments_for_hit(
                    hit.options['hitid'], all_studies=True)
                _return.append(hit_response)
            return _return, 201

        else:
            raise APIException(message='action `{}` not recognized!'.format(action))


class CampaignResource(Resource):
    def get(self, campaign_id):
        campaign = Campaign.query.filter(Campaign.id == campaign_id).one()
        return campaign

    def patch(self, campaign_id):
        campaign = Campaign.query.filter(Campaign.id == campaign_id).one()
        data = request.json
        did_something = False
        if 'is_active' in data and campaign.is_active and not data['is_active']:
            campaign.end()
        elif 'goal' in data:
            goal = data['goal']

            completed_count = Participant.count_completed(
                codeversion=services_manager.codeversion,
                mode=services_manager.mode)

            assert goal > completed_count, 'Goal {} must be greater than current completed {}.'.format(
                goal, completed_count)

            campaign.set_new_goal(goal)

        return campaign


class CampaignList(Resource):
    def get(self):
        campaigns = Campaign.query.filter(Campaign.codeversion == services_manager.codeversion,
                                          Campaign.mode == services_manager.mode).all()
        return campaigns

    def post(self):
        data = request.json
        # check if one already exists that is active...
        if Campaign.active_campaign_exists():
            raise APIException(
                message='Active campaign already exists. Cancel that campaign first in order to create a new one.')
        codeversion = services_manager.codeversion
        mode = services_manager.mode
        campaign = Campaign.launch_new_campaign(codeversion=codeversion, mode=mode, **data)
        return campaign, 201



class TaskResource(Resource):
    def delete(self, task_id):
        app.apscheduler.remove_job(str(task_id))
        return '', 204


class TaskList(Resource):
    def get(self):
        tasks = app.apscheduler.get_jobs()
        return tasks

    def post(self):
        data = request.json
        mode = services_manager.mode
        if data['name'] == 'approve_all':
            # check if we already have an 'approve_all'
            if app.apscheduler.get_job('approve_all'):
                raise APIException(message='`approve_all` job already exists')

            from psiturk.tasks import do_approve_all

            job = app.apscheduler.add_job(
                id='approve_all',
                args=[mode],
                func=do_approve_all,
                trigger='interval',
                minutes=max(int(float(data['interval']) * 60), 30),
                next_run_time=datetime.datetime.now(pytz.utc)
            )
            return job, 201

        raise APIException(message='task name `{}` not recognized!'.format(data['name']))


class WorkerResource(Resource):
    def get(self, worker_id):
        p = Participant.query.filter(Participant.workerid == worker_id).one()
        return p.toAPIData()


class WorkerList(Resource):

    def get(self, codeversion=None):
        '''
        Returns workers from the local database

        codeversion:
            the codeversion on which to filter retrieved workers
        '''

        query = Participant.query
        if codeversion:
            query = query.filter(Participant.codeversion == codeversion)
        _return = query.all()
        return [p.toAPIData() for p in _return]


# --------------------------- DATA WRITING HELPERS --------------------------- #

# Writes data to an open zipfile
def write_data_to_zip(participant, fields, zf, prefix=''):
    for field in fields:
        output = get_datafile(participant, field)
        zf.writestr(prefix + field + '.csv', output)

def get_datafile(participant, datatype):
    contents = {
        "trial_data": {
            "function": lambda p: p.get_trial_data(),
            "headerline": "uniqueid,currenttrial,time,trialData\n"
        },
        "event_data": {
            "function": lambda p: p.get_event_data(),
            "headerline": "uniqueid,eventtype,interval,value,time\n"
        },
        "question_data": {
            "function": lambda p: p.get_question_data(),
            "headerline": "uniqueid,questionname,response\n"
        },
        }
    ret = contents[datatype]["headerline"] + contents[datatype]["function"](participant)
    return ret


# ------------------------------ RESOURCE ADDING ----------------------------- #

# Services Manager
api.add_resource(ServicesManager, '/services_manager', '/services_manager/')

# Assignments
api.add_resource(AssignmentList, '/assignments', '/assignments/')
api.add_resource(AssignmentsAction, '/assignments/action/<action>')

# Hits
api.add_resource(HitResource, '/hit/<hit_id>')
api.add_resource(HitList, '/hits/', '/hits/status/<status>')
api.add_resource(HitsAction, '/hits/action/<action>')

# Campaigns
api.add_resource(CampaignResource, '/campaign/<campaign_id>')
api.add_resource(CampaignList, '/campaigns', '/campaigns/')

# Tasks
api.add_resource(TaskResource, '/task/<task_id>')
api.add_resource(TaskList, '/tasks', '/tasks/')

# Workers
api.add_resource(WorkerList, '/workers', '/workers/', '/workers/codeversion/<codeversion>')
api.add_resource(WorkerResource, '/worker/<worker_id>')

api.init_app(api_blueprint)

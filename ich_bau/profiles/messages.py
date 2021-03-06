﻿# messages

import json

# message types

MSG_NOTIFY_TYPE_ASK_ACCEPT_ID = 1
MSG_NOTIFY_TYPE_USER_WANT_JOIN_ID = 2

MSG_NOTIFY_TYPE_PROJECT_CHANGED_ID = 20
MSG_NOTIFY_TYPE_PROJECT_MILESTONE_CHANGED_ID = 30
MSG_NOTIFY_TYPE_PROJECT_TASK_CHANGED_ID = 40
MSG_NOTIFY_TYPE_PROJECT_TASK_ASSIGNED_ID = 45
MSG_NOTIFY_TYPE_PROJECT_TASK_UNASSIGNED_ID = 46
MSG_NOTIFY_TYPE_PROJECT_TASK_NEW_COMMENT_ID = 50
MSG_NOTIFY_TYPE_PROJECT_TASK_CHANGED_COMMENT_ID = 51

MSG_NOTFY_TYPES = {

MSG_NOTIFY_TYPE_ASK_ACCEPT_ID,
MSG_NOTIFY_TYPE_USER_WANT_JOIN_ID,

MSG_NOTIFY_TYPE_PROJECT_CHANGED_ID,
MSG_NOTIFY_TYPE_PROJECT_MILESTONE_CHANGED_ID,
MSG_NOTIFY_TYPE_PROJECT_TASK_CHANGED_ID,
MSG_NOTIFY_TYPE_PROJECT_TASK_ASSIGNED_ID,
MSG_NOTIFY_TYPE_PROJECT_TASK_UNASSIGNED_ID,
MSG_NOTIFY_TYPE_PROJECT_TASK_NEW_COMMENT_ID,
MSG_NOTIFY_TYPE_PROJECT_TASK_CHANGED_COMMENT_ID
}

MSGS = {
MSG_NOTIFY_TYPE_ASK_ACCEPT_ID : "You are asked to accept the membership of '{0}' project team!",
MSG_NOTIFY_TYPE_USER_WANT_JOIN_ID : "User want to join the '{0}' project",
MSG_NOTIFY_TYPE_PROJECT_CHANGED_ID : "Changes in the '{0}' project.",
MSG_NOTIFY_TYPE_PROJECT_MILESTONE_CHANGED_ID : "Changes in the milestone '{0}' of '{1}' project.",
MSG_NOTIFY_TYPE_PROJECT_TASK_CHANGED_ID : "Changes in the task '{0}' of '{1}' project",

MSG_NOTIFY_TYPE_PROJECT_TASK_ASSIGNED_ID : "You are assigned at a '{0}' task of '{1}' project.",
MSG_NOTIFY_TYPE_PROJECT_TASK_UNASSIGNED_ID : "You are unassigned from a '{0}' task of '{1}' project.",

MSG_NOTIFY_TYPE_PROJECT_TASK_NEW_COMMENT_ID : "New comment in the task '{0}' of '{1}' project",
MSG_NOTIFY_TYPE_PROJECT_TASK_CHANGED_COMMENT_ID : "Changed comment in the task '{0}' of '{1}' project",
}

# JSON KEYS

MSG_NOTIFY_JSON_KEY_TYPE = 'msg_type'
MSG_NOTIFY_JSON_KEY_PROJECT_NAME = 'project_name'
MSG_NOTIFY_JSON_KEY_MILESTONE_PROJECT_NAME = 'milestone_name'
MSG_NOTIFY_JSON_KEY_TASK_PROJECT_NAME = 'task_name'

def project_msg2json_str( arg_msg_type, arg_project_name = None, arg_milestone_name = None, arg_task_name = None ):
    d = { MSG_NOTIFY_JSON_KEY_TYPE : arg_msg_type }
    if arg_project_name:
        d[MSG_NOTIFY_JSON_KEY_PROJECT_NAME] = arg_project_name
    if arg_milestone_name:
        d[MSG_NOTIFY_JSON_KEY_MILESTONE_PROJECT_NAME] = arg_milestone_name
    if arg_task_name:
        d[MSG_NOTIFY_JSON_KEY_TASK_PROJECT_NAME] = arg_task_name

    # тестовый прогон
    j = json.dumps( d )
    if decode_json2msg(j):
        return j
    else:
        return None

# function to decode the json to message or to title
def decode_json2something( arg_str, only_title = False ):
    try:
        j_obj = json.loads( arg_str )
        key_type = j_obj[MSG_NOTIFY_JSON_KEY_TYPE]
        if key_type in ( MSG_NOTIFY_TYPE_ASK_ACCEPT_ID, MSG_NOTIFY_TYPE_PROJECT_CHANGED_ID, MSG_NOTIFY_TYPE_USER_WANT_JOIN_ID ):
            if only_title:
                return j_obj[MSG_NOTIFY_JSON_KEY_PROJECT_NAME]
            else:
                return MSGS[key_type].format(j_obj[MSG_NOTIFY_JSON_KEY_PROJECT_NAME])
        else:
            if key_type == MSG_NOTIFY_TYPE_PROJECT_MILESTONE_CHANGED_ID:
                if only_title:
                    return j_obj[MSG_NOTIFY_JSON_KEY_MILESTONE_PROJECT_NAME]
                else:
                    return MSGS[key_type].format(j_obj[MSG_NOTIFY_JSON_KEY_MILESTONE_PROJECT_NAME],j_obj[MSG_NOTIFY_JSON_KEY_PROJECT_NAME])
            else:
                if key_type in (MSG_NOTIFY_TYPE_PROJECT_TASK_CHANGED_ID, MSG_NOTIFY_TYPE_PROJECT_TASK_ASSIGNED_ID, MSG_NOTIFY_TYPE_PROJECT_TASK_UNASSIGNED_ID, MSG_NOTIFY_TYPE_PROJECT_TASK_NEW_COMMENT_ID, MSG_NOTIFY_TYPE_PROJECT_TASK_CHANGED_COMMENT_ID):
                    if only_title:
                        return j_obj[MSG_NOTIFY_JSON_KEY_TASK_PROJECT_NAME]
                    else:
                        return MSGS[key_type].format(j_obj[MSG_NOTIFY_JSON_KEY_TASK_PROJECT_NAME],j_obj[MSG_NOTIFY_JSON_KEY_PROJECT_NAME])
    except:
        return None

def decode_json2msg( arg_str ):
    return decode_json2something( arg_str )

def decode_json2title( arg_str ):
    return decode_json2something( arg_str, True )

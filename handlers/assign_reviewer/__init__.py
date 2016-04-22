from eventhandler import EventHandler
import re
import ConfigParser
import os

COLLABORATORS_CONFIG_FILE = os.path.join(os.path.dirname(__file__), '../../collaborators.ini')

def get_collaborators_config():
    config = ConfigParser.ConfigParser()
    config.read(COLLABORATORS_CONFIG_FILE)
    return config

def get_collaborators(api):
    config = get_collaborators_config()
    repo = api.owner + '/' + api.repo

    try:
        return [username for (username, _) in config.items(repo)]
    except ConfigParser.NoSectionError:
        return [] # No collaborators

# If the user specified a reviewer, return the username, otherwise returns None.
def find_reviewer(commit_msg):
    reviewer_re = re.compile("\\b[rR]\?[:\- ]*@([a-zA-Z0-9\-]+)")
    match = commit_msg and reviewer_re.search(commit_msg)
    if not match:
        return None
    return match.group(1)

# Return a collaborator's username if there is one in the config file. Otherwise, return None.
def choose_reviewer(api, pull_number):
    collaborators = get_collaborators(api)
    if not collaborators:
        return None

    return collaborators[pull_number % len(collaborators)]

welcome_msg = "Thanks for the pull request, and welcome! The Servo team is excited to review "\
              "your changes, and you should hear from @%s (or someone else) soon."

class AssignReviewerHandler(EventHandler):
    def on_pr_opened(self, api, payload):
        # If the pull request already has an assignee, don't try to set one ourselves.
        if payload["pull_request"]["assignee"] is not None:
            return
        reviewer = find_reviewer(payload["pull_request"]["body"]) \
            or choose_reviewer(api, payload["pull_request"]["number"])
        # Add welcome message for new contributors
        author = payload["pull_request"]['user']['login']
        if api.is_new_contributor(author):
            api.post_comment(welcome_msg % reviewer)
        api.set_assignee(reviewer)

    def on_new_comment(self, api, payload):
        if not self.is_open_pr(payload):
            return

        reviewer = find_reviewer(payload["comment"]["body"])
        if reviewer:
            api.set_assignee(reviewer)


handler_interface = AssignReviewerHandler

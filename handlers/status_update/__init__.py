import time
from eventhandler import EventHandler

PR_UPDATE_MSG = "New code was committed to pull request."


def manage_pr_state(api, payload):
    labels = api.get_labels()

    for label in ["S-awaiting-merge",
                  "S-tests-failed",
                  "S-needs-code-changes"]:
        if label in labels:
            api.remove_label(label)
    if "S-awaiting-review" not in labels:
        api.add_label("S-awaiting-review")

    if payload["action"] == "synchronize" and "S-needs-rebase" in labels:
        mergeable = payload['pull_request']['mergeable']
        # If mergeable is null, the data wasn't available yet.
        # Once it is, mergeable will be either true or false.
        while mergeable is None:
            time.sleep(1)  # wait for GitHub to finish determine mergeability
            pull_request = api.get_pull()
            mergeable = pull_request['mergeable']

        if mergeable:
            api.remove_label("S-needs-rebase")

    if payload["action"] == "synchronize":
        api.post_comment(PR_UPDATE_MSG)


class StatusUpdateHandler(EventHandler):
    def on_pr_opened(self, api, payload):
        manage_pr_state(api, payload)

    def on_pr_updated(self, api, payload):
        manage_pr_state(api, payload)

    def on_pr_closed(self, api, payload):
        if payload['pull_request']['merged']:
            api.remove_label("S-awaiting-merge")

    def on_build_status(self, api, payload):
        if payload['context'] == 'continuous-integration/travis-ci/pr':
            if payload['state'] == 'failure' or payload['state'] == 'error':
                api.add_label("S-needs-code-changes")

handler_interface = StatusUpdateHandler

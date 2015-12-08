from eventhandler import EventHandler

reftest_required_msg = 'These commits modify layout code, but no reftests are modified. Please consider adding a reftest!'

class MissingTestHandler(EventHandler):
    def on_pr_opened(self, api, payload):
        diff = api.get_diff()
        layout_changed = False
        for line in diff.split('\n'):
            if self.tests_present(line):
                return
            if self.layout_changed(line):
                layout_changed = True

        if layout_changed:
            self.warn(reftest_required_msg)

    def tests_present(self, line):
        return (
            line.startswith('diff --git') and
            (line.find('tests/ref') > -1
                or line.find('tests/wpt') > -1))

    def layout_changed(self, line):
        return (
            line.startswith('diff --git') and
            line.find('components/layout/') > -1)

handler_interface = MissingTestHandler

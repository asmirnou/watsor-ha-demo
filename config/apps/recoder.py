import hassapi as hass
import adbase as ad
import subprocess as sp
import traceback
from datetime import timedelta


class Recoder(hass.Hass):
    COMMAND = "command"
    SUBSCRIPTIONS = "subscriptions"
    CHECK_INTERVAL = "check_interval"

    ATTR_STATE = "state"
    ATTR_LIFECYCLE = "lifecycle"

    LOG_LEVEL_DEBUG = "DEBUG"
    LOG_LEVEL_ERROR = "ERROR"

    def initialize(self):
        self.process = None
        self.checker = None

        self.command = self.args[self.COMMAND]
        self.subscriptions = self.args[self.SUBSCRIPTIONS]

        for entity_id in self.subscriptions:
            self.subscribe(entity_id=entity_id, state=self.subscriptions[entity_id])

    def subscribe(self, entity_id, state):
        if self.get_state(entity_id) == state:
            self.start(entity_id=entity_id, attribute=self.ATTR_STATE, old=None, new=state, kwargs={})

        self.listen_state(self.start, entity_id, new=state)
        self.listen_state(self.stop, entity_id, old=state)

    @ad.app_lock
    def start(self, entity_id, attribute, old, new, kwargs):
        if self.process is not None or \
                not all(map(lambda key: self.get_state(key) == self.subscriptions[key], self.subscriptions)):
            return

        try:
            self.log("Start recording due to '{}' {} changed from '{}' to '{}'".format(entity_id, attribute, old, new))

            self.log(" ".join(self.command), level=self.LOG_LEVEL_DEBUG)
            self.process = sp.Popen(self.command)

            interval = int(self.args.get(self.CHECK_INTERVAL, 10))
            self.checker = self.run_every(self.check, self.get_now() + timedelta(seconds=interval), interval)
        except:
            self.error(traceback.format_exc(), level=self.LOG_LEVEL_ERROR)

    @ad.app_lock
    def stop(self, entity_id, attribute, old, new, kwargs):
        if self.process is None:
            return

        try:
            self.log("Stop recording due to '{}' {} changed from '{}' to '{}'".format(entity_id, attribute, old, new))

            self.cancel_timer(self.checker)
            self.checker = None

            self.process.terminate()
            self.process.wait()
            self.process = None
        except:
            self.error(traceback.format_exc(), level=self.LOG_LEVEL_ERROR)

    def check(self, kwargs):
        if self.process is None or self.process.poll() is None:
            return

        self.stop(self.COMMAND, attribute=self.ATTR_STATE, old="running", new="terminated", kwargs={})
        self.start(self.COMMAND, attribute=self.ATTR_STATE, old="running", new="terminated", kwargs={})

    def terminate(self):
        self.stop(self.__class__.__name__, attribute=self.ATTR_LIFECYCLE, old="running", new="terminating", kwargs={})

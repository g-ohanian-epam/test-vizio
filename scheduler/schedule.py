import threading
import time
from abc import ABC, abstractmethod
from datetime import datetime, timedelta

from enum import Enum


class TVStates(Enum):
    ACTIVE = "active"
    STANDBY = "standby"
    OFF = "off"


class TV:
    STATE = TVStates.OFF


class Firmware:
    @staticmethod
    def wake_up_at(wake_up_time):
        # wake up the tv
        pass


class AbstractBaseScheduler(ABC):
    def __init__(self, tv: TV) -> None:
        self.tv = tv
        self._stop_event = threading.Event()

    def stop(self):
        self._stop_event.set()

    @abstractmethod
    def start(self, *args, **kwargs):
        pass


class HourlyScheduler(AbstractBaseScheduler):
    SLEEP_SECONDS = 1

    def start(self, *args, **kwargs) -> None:
        def hourly_task():
            while not self._stop_event.is_set():
                if self.tv.STATE == TVStates.ACTIVE:
                    self._improve_actions()
                time.sleep(self.SLEEP_SECONDS)
        th = threading.Thread(target=hourly_task)
        th.start()
        return th

    def _improve_actions(self) -> dict:
        return {"message": "Actions are improved"}


class NightlyScheduler(AbstractBaseScheduler):

    def start(self, *args, **kwargs) -> None:
        def nightly_update_task():
            while not self._stop_event.is_set():
                now = datetime.now()
                midnight = now.replace(hour=0, minute=0, second=0, microsecond=0)
                if now >= midnight:
                    midnight += timedelta(days=1)
                time.sleep((midnight - now).total_seconds())
                if self.tv.STATE == TVStates.ACTIVE or self.tv.STATE == TVStates.STANDBY:
                    self._check_software()

        threading.Thread(target=nightly_update_task, daemon=True).start()

    def _check_software(self) -> dict:
        # call software update check daemon
        return {"message": "Daemon is called"}


class CustomScheduler(AbstractBaseScheduler):
    def __init__(self, tv: TV, hour: int, minute: int, app_name: str) -> None:
        super().__init__(tv)
        self._hour = hour
        self._minute = minute
        self.app_name = app_name

    def start(self, *args, **kwargs) -> None:
        def prog_alarm_task():
            while not self._stop_event.is_set():
                now = datetime.now()
                alarm_time = now.replace(
                    hour=self._hour,
                    minute=self._minute,
                    second=0,
                    microsecond=0
                )
                if now >= alarm_time:
                    alarm_time += timedelta(days=1)
                time.sleep((alarm_time - now).total_seconds())
                if self.tv.STATE == TVStates.ACTIVE or self.tv.STATE == TVStates.STANDBY:
                    self._launch_program(now)

        threading.Thread(target=prog_alarm_task, daemon=True).start()

    def _launch_program(self, launch_time) -> dict:
        Firmware.wake_up_at(launch_time)
        return {"message": "program is launched"}


class CustomSchedulerHolder:
    schedulers = {}

    def add_scheduler(self, alarm_event) -> CustomScheduler:
        if existing_scheduler := self.schedulers.get(alarm_event['app_name']):
            return existing_scheduler
        scheduler = CustomScheduler(
            TV(),
            app_name=alarm_event['app_name'],
            hour=int(alarm_event['hour']),
            minute=int(alarm_event['minute'])
        )
        CustomSchedulerHolder.schedulers[scheduler.app_name] = scheduler
        return scheduler

    def remove_scheduler(self, app_name) -> None:
        try:
            scheduler = CustomSchedulerHolder.schedulers.pop(app_name)
            scheduler.stop()
        except KeyError as e:
            print(e)


if __name__ == "__main__":
    tv = TV()
    hourly = HourlyScheduler(tv)
    # nightly = NightlyScheduler(tv)

    th:threading.Thread = hourly.start()
    is_alive = True
    a = 1
    while is_alive:
        print(th.is_alive())
        if a > 10:
            hourly.stop()
        a += 1

    # nightly.start()


    def on_prog_alarm_update(event: dict):  # this function is subscribed to the System Registry
        action = event['action']
        holder = CustomSchedulerHolder()
        if action == 'start':
            return holder.add_scheduler(event)
        if action == 'stop':
            return holder.remove_scheduler(event['app_name'])

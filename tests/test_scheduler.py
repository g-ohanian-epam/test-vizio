from datetime import datetime

from scheduler.schedule import HourlyScheduler, NightlyScheduler, CustomScheduler, CustomSchedulerHolder


class TestHourlyScheduler:
    def test_start(self, off_tv):
        scheduler = HourlyScheduler(off_tv)
        scheduler.start()
        assert scheduler._stop_event.is_set() is False

    def test_improve_actions(self, off_tv):
        scheduler = HourlyScheduler(off_tv)
        actions = scheduler._improve_actions()
        assert actions == {"message": "Actions are improved"}

    def test_stop(self, off_tv):
        scheduler = HourlyScheduler(off_tv)
        scheduler.start()
        scheduler.stop()
        assert scheduler._stop_event.is_set() is True


class TestNightlyScheduler:
    def test_start(self, off_tv):
        scheduler = NightlyScheduler(off_tv)
        scheduler.start()
        assert scheduler._stop_event.is_set() == False

    def test_check_software(self, off_tv):
        scheduler = NightlyScheduler(off_tv)
        check_result = scheduler._check_software()
        assert check_result == {"message": "Daemon is called"}

    def test_stop(self, off_tv):
        scheduler = NightlyScheduler(off_tv)
        scheduler.start()
        scheduler.stop()
        assert scheduler._stop_event.is_set() is True


class TestCustomScheduler:

    def test_start(self, off_tv):
        scheduler = CustomScheduler(off_tv, 7, 0, "news")
        scheduler.start()
        assert scheduler._stop_event.is_set() is False

    def test_launch_program(self, off_tv):
        scheduler = CustomScheduler(off_tv, 7, 0, "news")
        message = scheduler._launch_program(datetime.now())
        assert message == {"message": "program is launched"}


class TestCustomSchedulerHolder:
    def test_add_scheduler(self):
        holder = CustomSchedulerHolder()
        alarm_event = {'app_name': 'news', 'hour': 7, 'minute': 0}
        scheduler = holder.add_scheduler(alarm_event)
        assert scheduler is not None
        assert scheduler.app_name == 'news'

        holder = CustomSchedulerHolder()
        alarm_event = {'app_name': 'netflix', 'hour': 6, 'minute': 0}
        holder.add_scheduler(alarm_event)

        assert len(holder.schedulers.items()) == 2

    def test_remove_scheduler(self):
        holder = CustomSchedulerHolder()
        alarm_event = {'app_name': 'news', 'hour': 7, 'minute': 0}
        holder.add_scheduler(alarm_event)
        holder.remove_scheduler('news')
        assert 'news' not in holder.schedulers

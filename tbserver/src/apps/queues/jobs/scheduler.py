from apscheduler.schedulers.background import BackgroundScheduler
from apps.core.services.model_status import *
from ..models import TBRunTrigger
from apps.core.services.tb_pusher import TBPusher

scheduler = BackgroundScheduler()
scheduler.start()
# scheduler.print_jobs()


class JobController(TBPusher):

    @classmethod
    def job_notify_driver_before_expire(cls, order, trigger: TBRunTrigger):
        try:
            scheduler.add_job(
                order.job_notify_driver, 'date',
                run_date=trigger.time_run, id=str(trigger.unique_id), args=[order, trigger]
            )
        except Exception as e:
            print("Exception job_notify_driver_before_expire..........", e.args, type(e.args))
            trigger.logger(status=JobStatus.FAILED, e=str(e.args))

    @classmethod
    def job_order_accept_scheduler(cls, order, trigger: TBRunTrigger):
        try:
            scheduler.add_job(
                order.job_force_update_order_status, 'date',
                run_date=trigger.time_run, id=str(trigger.unique_id), args=[order, trigger]
            )
        except Exception as e:
            print("Exception job_order_accept_scheduler..........", e.args, type(e.args))
            trigger.logger(status=JobStatus.FAILED, e=str(e.args))

    @classmethod
    def job_show_package_to_offer(cls, package, trigger: TBRunTrigger):
        try:
            scheduler.add_job(
                package.job_show_package_to_drivers, 'date',
                run_date=trigger.time_run, id=str(trigger.unique_id), args=[trigger])
            scheduler.print_jobs()
        except Exception as e:
            print(f"Exception job_show_package_to_offer......{e.args}{str(e.args)}", trigger)
            trigger.logger(status=JobStatus.FAILED, e=str(e.args))

    @classmethod
    def job_redistribution_of_package(cls, package, trigger: TBRunTrigger):
        try:
            scheduler.add_job(
                package.job_create_sub_package, 'date',
                run_date=trigger.time_run, id=str(trigger.unique_id), args=[package, trigger])
            scheduler.print_jobs()
        except Exception as e:
            print(f"Exception job_show_package_to_offer......{e.args}{str(e.args)}", trigger)
            trigger.logger(status=JobStatus.FAILED, e=str(e.args))

    @classmethod
    def trigger_force_show_package_to_offer(cls, trigger: TBRunTrigger):
        try:
            trigger_job = scheduler.get_job(str(trigger.unique_id))
            if trigger_job:
                now = datetime.now(tz=pytz.UTC)
                trigger_job.modify(next_run_time=now)
        except Exception as e:
            print(f"Exception job_show_package_to_offer......{e.args}{str(e.args)}", trigger)
            trigger.logger(status=JobStatus.FAILED, e=str(e.args))

    @classmethod
    def remove_trigger(cls, trigger: TBRunTrigger):
        try:
            trigger_job = scheduler.get_job(str(trigger.unique_id))
            if trigger_job:
                trigger_job.remove()
                trigger.remove()
        except Exception as e:
            print(f"Exception job_show_package_to_offer......{e.args}{str(e.args)}", trigger)
            trigger.logger(status=JobStatus.FAILED, e=str(e.args))


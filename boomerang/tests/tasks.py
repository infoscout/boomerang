from boomerang.boomerang import BoomerangTask


class SimpleBoomerangTask(BoomerangTask):

    @staticmethod
    def perform_async(job, integers):
        for _ in integers:
            if job:
                job.increment_progress()


class FailingBoomerangTask(BoomerangTask):

    @staticmethod
    def perform_async(job, integers):
        for i in integers:
            if i == 5:
                raise ValueError("Cannot handle value of 5")
            if job:
                job.increment_progress()

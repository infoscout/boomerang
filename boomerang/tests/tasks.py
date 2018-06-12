from boomerang.boomerang import BoomerangTask


class SimpleBoomerangTask(BoomerangTask):

    @staticmethod
    def perform_async(job, integers):
        for _ in integers:
            job.increment_progress()

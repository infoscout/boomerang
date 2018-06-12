from boomerang.boomerang import BoomerangTask


class SimpleBoomerangTask(BoomerangTask):

    def get_goal_size(self, num_iterations):
        return num_iterations

    @staticmethod
    def perform_async(job, num_iterations):
        for _ in range(num_iterations):
            job.increment_progress()

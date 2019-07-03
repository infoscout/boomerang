# -*- coding: utf-8 -*-
from __future__ import unicode_literals

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


class ResumeableBoomerangTask(BoomerangTask):

    @staticmethod
    def perform_async(job, integers, _current_progress):
        for _ in integers:
            if job:
                job.increment_progress()


class ResumableFailingBoomerangTask(BoomerangTask):

    @staticmethod
    def perform_async(job, integers, _current_progress):
        for i in integers:
            if i == 5:
                raise ValueError("Cannot handle value of 5")
            if job:
                job.increment_progress()

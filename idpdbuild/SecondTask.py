from waflib import Task


class SecondTask(Task.Task):
    run_str = "echo Second"

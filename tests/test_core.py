import pytest
from voxshell.core import CommandRunner

def test_command_runner_success():
    runner = CommandRunner("echo 'hello voxshell'")
    return_code, output = runner.run()
    assert return_code == 0
    assert "hello voxshell" in output

def test_command_runner_failure():
    runner = CommandRunner("non_existent_command_12345")
    return_code, output = runner.run()
    assert return_code != 0

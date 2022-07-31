import contextlib
import os


@contextlib.contextmanager
def with_pip_tools_custom_compile_command_as_mvenv_compile():
    """
    Temporarily patches the environment to set:
    CUSTOM_COMPILE_COMMAND="mvenv compile"
    :return:
    """
    current_value = os.getenv("CUSTOM_COMPILE_COMMAND")
    os.environ["CUSTOM_COMPILE_COMMAND"] = "mvenv compile"
    yield
    if current_value is not None:
        os.environ["CUSTOM_COMPILE_COMMAND"] = current_value

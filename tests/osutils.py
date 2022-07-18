def is_not_found_output(output: str) -> bool:
    # not found on Linux and some Mac
    # No such file or directory on Mac 11.2 zsh
    return "not found" in output or "No such file or directory" in output

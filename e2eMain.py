import sys
from graphicalInterface import runVisualMode, inititalizeUI
from consoleInterface import runCLIMode


if __name__ == "__main__":

    args = sys.argv[1:]
    if len(args) == 0:
        print("User did not pass any arguments (launching GUI-mode)")
        window = inititalizeUI()
        runVisualMode(window)
        window.close()

    if len(args) > 0:
        print("User specified following arguments (launching CLI-mode):")
        print(args)
        runCLIMode(args)


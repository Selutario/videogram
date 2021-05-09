PYTHON = python3

# .PHONY defines parts of the makefile that are not dependant on any specific file
# This is most often used to store functions
.PHONY = help setup test run clean

.DEFAULT_GOAL = help

help:
	@echo "---------------HELP-----------------"
	@echo "To setup the project type make setup"
	@echo "To run the project type make run"
	@echo "------------------------------------"

setup:

	@echo "Checking if project files are generated..."
	${PYTHON} -m pip install -e .
	${PYTHON} installer.py
	@echo "\nDone! You can start the bot with 'make run' and upload your first video by typing '/upload' to the bot."

run:
	${PYTHON} main.py
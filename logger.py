"""Simple file logger."""

def log(message):
	with open('test.log', 'a+') as f:
		if message[-1] != '\n':
			message = message + '\n'
		f.write(message)
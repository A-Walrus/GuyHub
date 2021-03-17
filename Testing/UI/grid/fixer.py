with open("test.py","r") as f:
	s = f.read()
	s = s.replace('    ','\t')
	print(s)
	with open("testt.py","w") as f:
		f.write(s)
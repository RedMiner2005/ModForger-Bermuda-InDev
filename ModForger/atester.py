file = open("pydata.py", "r")
zip = open("forge.zip", "rb")
# print(list(zip.read()))
blah = list(zip.read())
# print(blah)
zip.close()
dat = file.read()
fil = open("pydata.py", "w")
dat = dat.replace("1892639248", str(blah))
# print(dat)
fil.write(dat)
import pydata, zipfile
file = open("PythonProj.zip", "x")
file.close()
file = open("PythonProj.zip", "w")
file.write(pydata.pydata)
file.close()
zip = zipfile.ZipFile('PythonProj.zip', 'r')
zip.extractall()
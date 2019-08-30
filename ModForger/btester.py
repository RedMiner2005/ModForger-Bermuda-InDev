import pydata
zip = open("forge1.zip", "wb")
zip.write(bytes(pydata.forgedata))
zip.close()
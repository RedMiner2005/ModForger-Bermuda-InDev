import RMFbase, pydata
from RMFbase import colorama
from time import sleep
import atexit

name = "ModForger"
version = "0.2.0"
author = "RedMiner2005"
mcver = "1.14.3"
hascolor = True
indev = True

colorama.init()
RMFbase.os.system("cls")

LOGGER = RMFbase.Logger(hascolor)

def exitf():
    LOGGER.endlog()

atexit.register(exitf)

print(colorama.Fore.RED + author + "'s " + name + colorama.Style.RESET_ALL + "\nVersion " + colorama.Fore.LIGHTGREEN_EX + version + "\n" + colorama.Style.RESET_ALL + "Built for Minecraft " + colorama.Fore.CYAN + mcver + colorama.Style.RESET_ALL + ".")

sleep(3)

RMFbase.os.system("cls")
print(colorama.Fore.RED + author + "'s " + name + colorama.Style.RESET_ALL + "\n")

ForgerEngine = RMFbase.RMFEngine(LOGGER)
ForgerEngine.registerextensions()
while True:  # Blahness
    RMFbase.os.system("cls")
    print(colorama.Fore.RED + author + "'s " + name + colorama.Style.RESET_ALL + "\n")
    firstline = RMFbase.PyInquirer.prompt(pydata.firstline)
    if(firstline["firstline"] == "Create a new project"):
        if not indev:
            baseans = RMFbase.PyInquirer.prompt(pydata.baseqs)
        else:
            baseans = {"group": "com.RedMiner2005.sea", "display": "The Sea Mod", "version": "0.1.0", "folder": ""}
        project = RMFbase.Project(baseans["group"], baseans["display"], baseans["version"], baseans["folder"], ForgerEngine)
        pydata.createoptions[0]["choices"].append(project.getcreate())
        for extensionid, extension in ForgerEngine.extensions.items():
            LOGGER.log(str(extension) + " = " + str(extension["project"]))
            pydata.createoptions[0]["choices"].append(extension["project"].getcreate())
            LOGGER.log("'{0}' Appended".format(extension["project"].getcreate()))
        createopt = RMFbase.PyInquirer.prompt(pydata.createoptions)
        createopt = createopt["createopt"]
        LOGGER.log("createopt = {0}".format(createopt))
        if (createopt == project.getcreate()):
            project.createf()
            LOGGER.log("Project Create Function Run.", result=RMFbase.ActionResult.SUCCESS)
        for extensionid, extension in ForgerEngine.extensions.items():
            LOGGER.log(str(extension) + " = " + str(extension["project"]))
            project1 = project.exportproject(extension["project"])
            if(createopt == project1.getcreate()):
                project1.createf()
                LOGGER.log("Create Function Run.", result=RMFbase.ActionResult.SUCCESS)
    elif (firstline["firstline"] == "Exit"):
        RMFbase.os.system("cls")
        RMFbase.sys.exit()
    input("Press Enter to continue..")
    
    
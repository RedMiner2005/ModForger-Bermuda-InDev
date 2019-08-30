import os, json, enum, importlib, toml, colorama, PyInquirer, datetime, sys, inspect

# Development
indev = False


def indevf():
    print("Mod Forger Engine for Minecraft 1.14.3\nCreated by RedMiner2005.")
    ex = RMFEngine()
    ex.registerextensions()


class PackageType(enum.Enum):
    JAVA = 0
    RESOURCE = 1
    ROOT = 2


class ActionResult(enum.Enum):
    SUCCESS = 0
    FAILURE = 1
    INFO = 2
    WARNING = 3


class Project():
    loggername = "WorkspaceForger"
    username = ""
    modid = ""
    group = ""
    display = ""
    version = ""
    folder = ""
    engineinst = None

    def __init__(self, group, display, version, folder, engineinst):
        self.group = group.lower()
        self.username = str(group).split(".")[-2]
        self.modid = str(str(group).split(".")[-1]).lower()
        self.display = display
        self.version = version
        self.folder = self.getValidFolder(folder)
        self.engineinst = engineinst
        self.engineinst.logger.log(" || ".join(["Hello!", group, display, version, folder, str(engineinst)]), self.loggername)

    def exportproject(self, projclass):
        proja = projclass(self.group, self.display, self.version, self.folder, self.engineinst)
        return proja

    def getValidFolder(self, folder):
        if (os.path.exists(folder)):
            i = 0
            folder = str(folder).replace("\\", "/")
            if (not folder.endswith("/")):
                folder = str(folder) + "/"
            return folder
        else:
            self.engineinst.logger.log("getValidFolder Failed", self.loggername, ActionResult.FAILURE)
            return ActionResult.FAILURE

    def getbase(self, typepackage):
        if (typepackage == PackageType.RESOURCE):
            return self.folder + "src/main/resources/"
        elif (typepackage == PackageType.ROOT):
            return self.folder
        else:
            return self.folder + "src/main/java/" + self.group.replace(".", "/") + "/"

    def getfolder(self, data1):
        data1 = str(data1)
        dat = data1.split(".")
        desttype = PackageType.RESOURCE if dat[0] == "resources" else PackageType.ROOT if dat[
                                                                                              0] == "root" else PackageType.JAVA
        dat.pop(0)
        base = self.getbase(desttype).replace(self.group.replace(".", "/") + "/", "") if not "/".join(dat).__contains__(
            "--/") else self.getbase(desttype)
        data = base + "/".join(dat).replace("--/", "").replace("||/", self.modid + "/") + "/"
        return data
        # return getJavaBase() + data1 if typePackage == PackageType.RESOURCE else getResourceBase(folder) + data1

    def gradlew(self, command):
        os.system("cd " + self.folder + " && gradlew " + command)

    def genfile(self, datakey, destaddr, **kwargs):
        datafile = open(self.engineinst.getkeyword("files/" + datakey), "r")
        data = datafile.read()
        datafile.close()
        keys = self.engineinst.getkeyword("project")
        for key in keys:
            if (not keys[key].startswith("//")):
                data = data.replace(keys[key], getattr(self, key))
        for argk, argv in kwargs.items():
            argk = argk.replace("_", "/")
            keyword = self.engineinst.getkeyword(argk)
            if (keyword.startswith("//")):
                data = data.replace(keyword, argv + "\n" + keyword)
            else:
                data = data.replace(keyword, argv)
        destfileaddr = self.getfolder(".".join(destaddr.split("."))).split("/")
        destfileaddr.pop(-1)
        destfileaddr[-2:] = [".".join(destfileaddr[-2:])]
        destfilename = destfileaddr[-1]
        destfileaddr = "/".join(destfileaddr)
        destfilenoname = destfileaddr.replace(destfilename, "")
        if (not os.path.isdir(destfilenoname)):
            os.makedirs(destfilenoname)
        destfile = open(destfileaddr, "w")
        destfile.write(data)
        destfile.close()

    def checkfiles(self, *destaddrs):
        result = True
        for destaddr in destaddrs:
            destfileaddr = self.getfolder(".".join(destaddr.split("."))).split("/")
            destfileaddr.pop(-1)
            destfileaddr[-2:] = [".".join(destfileaddr[-2:])]
            destfilename = destfileaddr[-1]
            destfileaddr = "/".join(destfileaddr)
            if (os.path.isfile(destfileaddr)):
                self.engineinst.logger.log("File {0} Found".format(destfilename), self.loggername, ActionResult.SUCCESS)
                result = True if not result else False
            self.engineinst.logger.log("File {0} Not Found".format(destfilename), self.loggername, ActionResult.FAILURE)
            result = False

    def genpackages(self, *packages):
        for package in packages:
            p = self.getfolder(package)
            if (not p == ActionResult.FAILURE):
                os.makedirs(p)
            else:
                return ActionResult.FAILURE

    def createf(self):
        if not self.checkfiles("resources.assets.||.lang.en_us.json", "java.--.Main.java", "java.--.config.Config.java"):
            self.genfile("GradleBuild", "root.build.gradle")
            self.genfile("GradleProperties", "root.gradle.properties")
            self.genfile("TomlMods", "resources.META-INF.mods.toml")
            self.genfile("USLang", "resources.assets.||.lang.en_us.json")
            self.genfile("Main", "java.--.Main.java")
            self.genfile("Config", "java.--.config.Config.java")
            self.genpackages("java.--.lists", "resources.assets.||.textures.item", "resources.assets.||.textures.block",
                             "resources.assets.||.models.item", "resources.assets.||.models.block",
                             "resources.data.||.recipes", "resources.data.||.loot_tables", "resources.data.||.tags")
        self.gradlew("eclipse")
        self.gradlew("genEclipseRuns")
        self.engineinst.logger.log("Create Function Finished", self.loggername, ActionResult.SUCCESS)
        return ActionResult.SUCCESS

    @staticmethod
    def getcreate():
        return "Setup your mod. (This sets up your mod for eclipse, creates the main and config classes)"

    def loadf(self):
        self.gradlew("build")
        self.engineinst.logger.log("Load Function Finished", self.loggername)
        return ActionResult.SUCCESS

    @staticmethod
    def getload():
        return "Build your mod. (This exports your mod)"

    @staticmethod
    def getdata():
        return {"name": "WorkspaceForger", "id": "workspace", "project": Project}

class RMFEngine():
    keywordloc = "data/keywords.json"
    extensionpath = "extensions/"
    logger = None
    datareg = {"base": []}

    extensions = {}

    def getValidFolder(self, folder):
        if (os.path.exists(folder)):
            i = 0
            folder = str(folder).replace("\\", "/")
            if (not folder.endswith("/")):
                folder = str(folder) + "/"
            return folder
        else:
            self.logger.log("getValidFolder Failed", "ForgerEngine", ActionResult.FAILURE)
            return ActionResult.FAILURE

    def __init__(self, logger, keywordloc="data/keywords.json", extensionpath="extensions/"):
        self.keywordloc = keywordloc
        self.extensionpath = self.getValidFolder(extensionpath)
        self.logger = logger
        self.logger.log("Finished Setup of The Engine", "ForgerEngine", ActionResult.SUCCESS)

    def getkeyword(self, address):
        address = str(address)
        if (address.count("/") == 1):
            addresslist = address.split("/")
            datafile = open(self.keywordloc, "r")
            keyworddata = json.load(datafile)
            parent = keyworddata["rmkeywords"]
            for keycat in parent:
                if (keycat == addresslist[0]):
                    cat = parent[keycat]
                    for key in cat:
                        if (key == addresslist[1]):
                            return cat[key]
        else:
            datafile = open(self.keywordloc, "r")
            keyworddata = json.load(datafile)
            parent = keyworddata["rmkeywords"]
            for keycat in parent:
                if (keycat == address):
                    return parent[keycat]
        self.logger.log("getkeyword() Failed", "ForgerEngine", ActionResult.FAILURE)
        return ActionResult.FAILURE

    def returninst(self, module_name, inst_name):
        module = importlib.import_module(module_name)
        programclass = getattr(module, inst_name)
        return programclass

    def registerextensions(self):
        extfolder = self.extensionpath
        extensionslist = self.extensions
        if (not self.getValidFolder(extfolder) == ActionResult.FAILURE):
            for (dirpath, dirnames, filenames) in os.walk(extfolder):
                for dirname in dirnames:
                    for (dirpath1, dirnames1, filenames1) in os.walk(extfolder + dirname):
                        for filename1 in filenames1:
                            if (filename1 == "extension.py"):
                                inst = self.returninst(
                                    extfolder.replace("/", ".") + dirname + "." + filename1.replace(".py", ""),
                                    "getdata")
                                inst1 = dict(inst())
                                inst0 = dict(inst1)
                                inst1.__delitem__("id")
                                extensionslist[inst0["id"]] = inst1
        else:
            self.logger.log("getValidFolder() Failed", "ForgerEngine(registerextensions)", ActionResult.FAILURE)
            return ActionResult.FAILURE
        self.logger.log("Extensions Registered, ExtensionList - " + str(self.extensions), "ForgerEngine")
        return extensionslist


class Properties():
    ui = True
    nonuifile = ""

    def getValidFolder(self, folder):
        if (os.path.exists(folder)):
            i = 0
            folder = str(folder).replace("\\", "/")
            if (not folder.endswith("/")):
                folder = str(folder) + "/"
            return folder
        else:
            return ActionResult.FAILURE

    def get(self, isui=True, nonuifolder="", *args):
        q = []
        nonuifolder = self.getValidFolder(nonuifolder)
        for arg in args:
            q.append(arg)
        if (isui):
            return PyInquirer.prompt(q)
        else:
            file = open(nonuifolder + "rmtemp.json", "r")
            return json.load(file)

    def input(self, id, message, validate=lambda val: True):
        q = {
            "type": "input",
            "name": id,
            "message": message,
            "validate": validate
        }
        return q


class Logger():
    hascolor = True
    logpath = "logs/"
    logfile = None

    def __init__(self, hascolor=False, logpath="logs/"):
        self.hascolor = hascolor
        self.logpath = logpath
        if not os.path.isdir(self.logpath): os.makedirs(self.logpath)
        if not os.path.isfile(self.logpath + "rmlog_" + str(datetime.date.today()) + ".txt"):
            logfile = open(self.logpath + "rmlog_" + str(datetime.date.today()) + ".txt", "x")
            logfile.close()
        logfile = open(self.logpath + "rmlog_" + str(datetime.date.today()) + ".txt", "a")
        logfile.write("ModForger's log ----- " + str(datetime.datetime.now()) + "\n_________________________________________"
                                                                           + "\n")
        self.logfile = logfile

    def log(self, msg, sender="ModForger", result: ActionResult = ActionResult.INFO):
        c = colorama.Fore.LIGHTCYAN_EX
        if (result == ActionResult.SUCCESS):
            c = colorama.Fore.LIGHTGREEN_EX
        elif (result == ActionResult.FAILURE):
            c = colorama.Fore.LIGHTRED_EX
        elif (result == ActionResult.WARNING):
            c = colorama.Fore.LIGHTYELLOW_EX
        else:
            result = ActionResult.INFO
        if self.hascolor:
            msg = c + "[{1}/{0}] ".format(str(result).replace("ActionResult.", "").lower().capitalize(),
                                            sender) + colorama.Style.RESET_ALL + msg
        else:
            msg = "[{1}/{0}] ".format(str(result).replace("ActionResult.", "").lower().capitalize(),
                                            sender) + msg
        self.logfile.write(msg + "\n")

    def readlog(self):
        log = open(self.logfile.name, "r").read()
        return log

    def endlog(self):
        self.logfile.write("\n_________________________________________\n\n\n")

if (indev):
    indevf()

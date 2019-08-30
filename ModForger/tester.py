import enum
import importlib
import json
import os

group = "com.someone.test"

class PackageType(enum.Enum):
    JAVA = 0
    RESOURCE = 1
    ROOT = 2

class ActionResult(enum.Enum):
    SUCCESS = 0
    FAILURE = 1

class Project():
    username = ""
    modid = ""
    group = ""
    display = ""
    version = ""
    folder = ""

    def __init__(self, group, display, version, folder):
        self.group = group.lower()
        self.username = str(self.group).split(".")[-2]
        self.modid = str(str(self.group).split(".")[-1]).lower()
        self.display = display
        self.version = version
        self.folder = self.getValidFolder(folder)

    def exportproject(self, projclass, **data):
        proja = projclass(self.group, self.display, self.version, self.folder)
        return proja

    def getValidFolder(self, folder):
        if(os.path.exists(folder)):
            i = 0
            folder = str(folder).replace("\\", "/")
            if(not folder.endswith("/")):
                folder = str(folder) + "/"
            return folder
        else:
            return ActionResult.FAILURE

    def getPackageBase(self, typepackage):
        if(typepackage == PackageType.RESOURCE):
            return self.folder + "src/main/resources/"
        elif(typepackage == PackageType.ROOT):
            return self.folder
        else:
            return self.folder + "src/main/java/" + self.group.replace(".", "/") + "/"

    def getfolder(self, data1):
        data1 = str(data1)
        dat = data1.split(".")
        desttype = PackageType.RESOURCE if dat[0] == "resources" else PackageType.ROOT if dat[0] == "root" else PackageType.JAVA
        dat.pop(0)
        base = self.getPackageBase(desttype).replace(self.group.replace(".", "/") + "/", "") if not "/".join(dat).__contains__("--/") else self.getPackageBase(desttype)
        data = base + "/".join(dat).replace("--/", "").replace("||/", self.modid + "/") + "/"
        return data
        #return getJavaBase() + data1 if typePackage == PackageType.RESOURCE else getResourceBase(folder) + data1

    def gradlew(self, command):
        os.system("cd " + self.folder + " && gradlew " + command)

    def genfile(self, datakey, destaddr, engineinst, **kwargs):
        datafile = open(engineinst.getkeyword("files/" + datakey), "r")
        data = datafile.read()
        datafile.close()
        keys = engineinst.getkeyword("project")
        for key in keys:
            if(not keys[key].startswith("//")):
                data = data.replace(keys[key], getattr(self, key))
        for argk, argv in kwargs.items():
            argk = argk.replace("_", "/")
            keyword = engineinst.getkeyword(argk)
            if(keyword.startswith("//")):
                data = data.replace(keyword, argv + "\n" + keyword)
            else:
                data = data.replace(keyword, argv)
        destfileaddr = self.getfolder(".".join(destaddr.split("."))).split("/")
        destfileaddr.pop(-1)
        destfileaddr[-2:] = [".".join(destfileaddr[-2:])]
        destfilename = destfileaddr[-1]
        destfileaddr = "/".join(destfileaddr)
        destfilenoname = destfileaddr.replace(destfilename, "")
        if(not os.path.isdir(destfilenoname)):
            os.makedirs(destfilenoname)
        destfile = open(destfileaddr, "w")
        destfile.write(data)
        destfile.close()

class RMFEngine():
    keywordloc = "data/keywords"
    extensionloc = "extensions/"
    createf = {}
    loadf = {}
    datareg = {"base":[]}

    extensions = {}

    def getValidFolder(self, folder):
        if(os.path.exists(folder)):
            i = 0
            folder = str(folder).replace("\\", "/")
            if(not folder.endswith("/")):
                folder = str(folder) + "/"
            return folder
        else:
            return ActionResult.FAILURE

    def __init__(self, keywordloc, extensionloc):
        self.keywordloc = keywordloc
        self.extensionloc = self.getValidFolder(extensionloc)

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
        return ActionResult.FAILURE

    def returninst(self, module_name, inst_name):
        module = importlib.import_module(module_name)
        programclass = getattr(module, inst_name)
        instance = programclass()
        return instance

    def registerextensions(self):
        extfolder = self.extensionloc
        extensionslist = self.extensions
        if(not self.getValidFolder(extfolder) == ActionResult.FAILURE):
            for (dirpath, dirnames, filenames) in os.walk(extfolder):
                for dirname in dirnames:
                    #print(dirname)
                    for (dirpath1, dirnames1, filenames1) in os.walk(extfolder + dirname):
                        for filename1 in filenames1:
                            print(filename1)
                            if(filename1 == "extension.py"):
                                inst = self.returninst(extfolder.replace("/", ".") + dirname + "." + filename1.replace(".py", ""), "getdata")
                                inst1 = dict(inst)
                                inst1.__delitem__("registryname")
                                extensionslist[inst["registryname"]] = inst1
        else:
            return ActionResult.FAILURE
        return extensionslist

    def registerAll(self, data_inst, extfolder, funcregister, datregister):
        #dat = data_inst()
        for key in ["name", "registryname", "customproject"]:
            print(key)
            if(not dict(data_inst).__contains__(key)):
                return ActionResult.FAILURE
        return data_inst

print("Mod Forger Engine for Minecraft 1.14.3\nCreated by RedMiner2005.")
ex = RMFEngine()
ex.registerextensions()

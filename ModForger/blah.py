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

    def getbase(self, typepackage):
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
        base = self.getbase(desttype).replace(self.group.replace(".", "/") + "/", "") if not "/".join(dat).__contains__("--/") else self.getbase(desttype)
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

    def createf(self, engine):
        self.genfile("GradleBuild", "root.build.gradle", engine)
        self.genfile("GradleProperties", "root.gradle.properties", engine)
        self.genfile("TomlMods", "resources.META-INF.mods.toml", engine)
        self.gradlew("eclipse")
        self.gradlew("genEclipseRuns")
        self.genfile("USLang", "resources.assets.||.lang.en_us.json", engine)
        self.genfile("Main", "java.--.Main.java", engine)
        self.genfile("Config", "java.--.config.Config.java", engine)
        return ActionResult.SUCCESS

    def getcreate(self):
        return "Setup your mod. (This sets up your mod for eclipse, creates the main and config classes)"

    def loadf(self, engine):
        self.gradlew("runClient")
        return ActionResult.SUCCESS

    def getload(self):
        return "Build your mod. (This exports your mod)"
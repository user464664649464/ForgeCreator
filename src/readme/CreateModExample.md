[返回](../readme.md)

# 创建模组
# _**!!!这是非常重要的一步！！请你严格按照以下伪代码编写代码。**_
<script>
$modDirectory = 用户在本IDE中选择的目录/{modid}pack/
$modid = 用户在本IDE中输入的模组ID
$basePackageName = 用户在本IDE中输入的基础包名
$MainClassName = {modid}.firstLetterUpper()+Mod
$modAuthor = 用户在本IDE中输入的模组作者
$modName = 用户在本IDE中输入的模组显示名称

#const FORGEMDK = "forge-1.16.5-36.2.34-mdk"
function createMod(){
    if(path:=find_java8()){
        setenv("JAVA_HOME",path)
        setenv("PATH",getenvName("JAVA_HOME")+"/bin")
        write(
            {modDirectory}/{FORGEMDK}/gradle.properties:{
                org.gradle.java.home=path{path_set="/"}
            }
        )
    }else{
        warn_messagebox("未找到Java 8，开始下载...")
        download(
            "https://download.java.net/java/GA/jdk8/8u202-b08/132a6a48125f401594e99225a186db59/jdk-8u202-windows-x64.exe",
            {modDirectory}/temp/jdk-8u202-windows-x64.exe
        )
        run(
            {modDirectory}/temp/jdk-8u202-windows-x64.exe /s
        )
    }
    copy(
        sys.argv[0].__dirname__/res/nullpack/*,
        {modDirectory}/*
    );
    config();
    build();
}
function config(){
    rename(
        {modDirectory}/{FORGEMDK}/src/main/java/com/:{
            yang/mod/YangMod.java
            -> {basePackageName}/{modid}/{MainClassName}.java
        },
        {modDirectory}/{FORGEMDK}/src/main/resources/:{
            assets/yangmod/ -> assets/{modid}mod/,
            data/yangmod/ -> data/{modid}mod/
        }
    )
    replace(
        {modDirectory}/{FORGEMDK}/src/main/resources/META-INF/mods.toml:{
            modId="yangmod" -> modId = "{modid}mod",
            displayName="朝阳Mod" -> displayName = "{modName}",
            authors="朝阳" -> authors = "{modAuthor}",
            description='''这是一个简单的Mod
            This is a long form description of the mod. You can write whatever you want here
            
            Have some lorem ipsum.
            
            Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed mollis lacinia magna. Orci varius natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus. Sed sagittis luctus odio eu tempus. Interdum et malesuada fames ac ante ipsum primis in faucibus. Pellentesque volutpat ligula eget lacus auctor sagittis. In hac habitasse platea dictumst. Nunc gravida elit vitae sem vehicula efficitur. Donec mattis ipsum et arcu lobortis, eleifend sagittis sem rutrum. Cras pharetra quam eget posuere fermentum. Sed id tincidunt justo. Lorem ipsum dolor sit amet, consectetur adipiscing elit.
            ''' -> description = '''
            {modDescription}
            ''',
            <all of examplemod> -> {modid}mod
        }
        {modDirectory}/{FORGEMDK}/src/main/java/com/{basePackageName}/{modid}mod/{MainClassName}.java:{
            @Mod("yangmod") -> @Mod("{modid}mod"),
            <all of YangMod> -> {MainClassName}
        }
        {modDirectory}/{FORGEMDK}/build.gradle:{
            <all of={
                modid -> {modid}mod
                yourname -> {basePackageName}
                examplemod -> {modid}mod
            }/>
        }
    )
}
function getenvName(name){
    return "%{name}%" if(system == "Windows") else "${name}"
}
function find_java8(){
    path = system.env["PATH"]
    for(p in path.split(sys.path_sep())){
        if(is_javapath(p)){
            echos = run(
                p+"/java -version"
            )
            if(is_java8Info(echos)){
                return p
            }
        }
    }else{
        return None
    }
}
function build(max=5){
    catches:{
        run(
            {modDirectory}/{FORGEMDK}/gradlew.bat genIntellijRuns
        )
    }if(catched){
        if(max<=0){
            log("构建失败")
            return
        }
        try_fix()
        build(max-1)
    }else{
        return
    }
}
</script>
# ***当用户创建完成后，应当自动打开模组！
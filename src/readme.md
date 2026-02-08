let $modDirectory = 用户在本IDE中选择的目录

warn "请不要让我运行你可以直接调用的工具"
# （注意，千万千万不要不小心添加修改res/nullpack的逻辑，代码所做的所有操作均在{modDirectory}\forge-1.16.5-36.2.34-mdk目录下进行）
# ***除了这里列出的以外，其他的方法请不要实现！开发者尚未打算实现它。***
# 模组信息的获取请直接读取{modDirectory}/{FORGEMDK}/src/main/resources/META-INF/mods.toml
# However, 方块、物品等信息需要在mod.json读写，因为直接在java源文件中读取较为困难
when(program_started){
    get(UAC,from="user_agent")
}
<Attention >
      目前的菜单仅有三项
      <Attention new=List<QMenu>, UseLanguageSystem=True>
          文件:
          - 新建...[创建模组](./readme/CreateModExample.md)
<let read="请认真阅读其中的内容">请跳转./readme/CreateModExample.md</let>
          - 打开...
          编辑:
          - 创建...[方块信息添加要求](./readme/BlockExample.md)
<let read="请认真阅读其中的内容">请跳转./readme/BlockExample.md</let>
              - 方块
                  - 继承自...
                  - 自定义...
              - 物品
              - 配方
              - 声音
              - 命令
              - 标签...
          运行:[添加“运行”菜单](./readme/runExample.md)
<let read="请认真阅读其中的内容">请跳转./readme/runExample.md</let>
          - 编译...
      </Attention>
  </Attention>


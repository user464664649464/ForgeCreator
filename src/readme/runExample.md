[返回](../readme.md)

# 添加“运行”菜单
- 其中的子菜单为Run...
  - 点击后，检查用户是否打开/创建了文件
  <if con=UserFileSelected || UserCreatedFile>
      gradlew runClient
  <else >
      弹出Error提示框("请先打开/创建文件")
  </endif>
  

$modDirectory = 用户在本IDE中选择的目录
$basePackage = 用户在本IDE中输入的基础包名
$modid = 用户在本IDE中输入的模组ID
$MainClassName = 用户在本IDE中输入的主类名
$ItemGroupClassName = 用户在本IDE中输入的物品分组类名
$TabIcon = 用户输入的将要被作为TAB图标的方块/物品ID
$TabIconType = 用户输入的将要被作为TAB图标的方块/物品ID的类型（值为ModBlocks或ModItems）
$ItemGroupID = ItemGroupClassName.firstLetterlower()
<UI must contain these && use Chinese>
    ! 其他的项请自己设计
    <InputBox>{ItemGroupClassName}</InputBox>
    <InputBox>{TabIcon}</InputBox>
    <ChoiceBox>{TabIconType}</ChoiceBox>
</UI>

这是一个{ItemGroupClassName}.java的内容示例
```java
package com.{basePackage}.{modid}mod.group;

import com.{basePackage}.{modid}mod.{MainClassName};
import net.minecraft.item.ItemGroup;
import net.minecraft.item.ItemStack;

public class {ItemGroupClassName} {
     public static final ItemGroup TAB = new ItemGroup("{ItemGroupID}") {
        @Override
        public ItemStack createIcon() {
            return new ItemStack({TabIconType}.{TabIcon}.get());
        }
    };
}
```
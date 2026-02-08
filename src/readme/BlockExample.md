[返回](../readme.md)

$modDirectory = 用户在本IDE中选择的目录
$basePackage = 用户在本IDE中输入的基础包名
$modid = 用户在本IDE中输入的模组ID
$MainClassName = 用户在本IDE中输入的主类名
$ItemGroupClassName = 用户在本IDE中输入的物品分组类名
$ItemGroupID = ItemGroupClassName.firstLetterlower()
$BlockClassName = 用户在本IDE中输入的方块类名
$blockID = 用户在本IDE中输入的方块ID
# Create-Block-继承自...的java实现
- 当没有block文件夹时，在{modDirectory}\forge-1.16.5-36.2.34-mdk\src\main\java\com\{basePackage}\{modid}mod\
- 创建一个新的block文件夹，并添加ModBlocks.java
- 内容示例
```java
package com.{basePackage}.{modid}mod.block;

import com.{basePackage}.{modid}mod.{MainClassName};


import com.{basePackage}.{modid}mod.group.{ItemGroupClassName};

import net.minecraft.block.AbstractBlock;
import net.minecraft.block.{继承自的主类名};
import net.minecraft.block.material.Material;
import net.minecraft.item.BlockItem;
import net.minecraft.item.Item;
import net.minecraftforge.common.ToolType;
import net.minecraftforge.eventbus.api.IEventBus;
import net.minecraftforge.fml.RegistryObject;
import net.minecraftforge.registries.DeferredRegister;
import net.minecraftforge.registries.ForgeRegistries;

import java.util.Arrays;
import java.util.function.Supplier;

public class ModBlocks {
    public static final DeferredRegister<Block> BLOCKS = DeferredRegister.create(ForgeRegistries.BLOCKS, {MainClassName}.MOD_ID);
    
    // 注册方块的代码...

    private static <T extends Block> RegistryObject<T> registerBlock(String name, Supplier<T> block) {
        RegistryObject<T> tro = BLOCKS.register(name, block);
        registerBlockItem(name, tro);
        return tro;
    }

    private static <T extends Block> void registerBlockItem(String name, RegistryObject<T> block) {
        ModItems.ITEMS.register(
            name, () -> new BlockItem(
                block.get(),
                new Item.Properties().group({ItemGroupClassName}.TAB)
            )
        );
    }
}

```
其中的TAB是物品分组，需要在...src\main\java\com\{basePackage}\{modid}mod\group\{ItemGroupClassName}.java中定义

检查是否有ItemGroup，如果没有则弹出新建ItemGroup的向导
用户必须完成此向导，然后返回到方块新建向导。
关于此向导的更多信息，请移步[ItemGroup新建向导](./readme/ItemGroupExample.md)

如果有：在当前窗口列出所有已有的ItemGroup，用户可以选择其中一个。右边加一个“新建..”
弹出ItemGroup新建向导，用户完成后，返回到方块新建向导。
方块新建向导要求添加选择ItemGroup项。

方块材质说明
 -  Material AIR - 空气
 -  Material STRUCTURE_VOID - 结构虚空
 -  Material PORTAL - 传送门
 -  Material CARPET - 地毯
 -  Material PLANTS - 植物
 -  Material OCEAN_PLANT - 海洋植物
 -  Material TALL_PLANTS - 高大植物
 -  Material NETHER_PLANTS - 下界植物
 -  Material SEA_GRASS - 海草
 -  Material WATER - 水
 -  Material BUBBLE_COLUMN - 气泡柱
 -  Material LAVA - 岩浆
 -  Material SNOW - 雪
 -  Material FIRE - 火
 -  Material MISCELLANEOUS - 杂项
 -  Material WEB - 蜘蛛网
 -  Material REDSTONE_LIGHT - 红石灯
 -  Material CLAY - 黏土
 -  Material EARTH - 泥土
 -  Material ORGANIC - 有机物
 -  Material PACKED_ICE - 打包冰
 -  Material SAND - 沙子
 -  Material SPONGE - 海绵
 -  Material SHULKER - 潜影贝
 -  Material WOOD - 木材
 -  Material NETHER_WOOD - 下界木材
 -  Material BAMBOO_SAPLING - 竹子树苗
 -  Material BAMBOO - 竹子
 -  Material WOOL - 羊毛
 -  Material TNT - TNT
 -  Material LEAVES - 树叶
 -  Material GLASS - 玻璃
 -  Material ICE - 冰
 -  Material CACTUS - 仙人掌
 -  Material ROCK - 岩石
 -  Material IRON - 铁
 -  Material SNOW_BLOCK - 雪块
 -  Material ANVIL - 铁砧
 -  Material BARRIER - 屏障
 -  Material PISTON - 活塞
 -  Material CORAL - 珊瑚
 -  Material GOURD - 葫芦
 -  Material DRAGON_EGG - 龙蛋
 -  Material CAKE - 蛋糕
* AbstractBlock.Properties常用方法说明：
     * 1. create(Material material) - 创建Properties对象，指定方块材质
     * 2. hardnessAndResistance(float hardness, float resistance) - 设置硬度和爆炸抗性
     *    - hardness: 破坏方块所需时间（0.05为瞬间破坏，3.0为钻石镐破坏石头的时间）
     *    - *resistance: 爆炸抗性（0.0为无抗性，1000.0为基岩抗性）
     * 3. harvestLevel(int level) - 设置挖掘所需工具等级
     *    - 0: 木/金工具
     *    - 1: 石质工具
     *    - 2: 铁质工具
     *    - 3: 钻石工具
     *    - 4:  Netherite工具（1.16+）
     * 4. harvestTool(ToolType tool) - 设置挖掘所需工具类型
     *    - ToolType.PICKAXE: 镐
     *    - ToolType.AXE: 斧
     *    - ToolType.SHOVEL: 铲
     *    - ToolType.HOE: 锄
     * 5. setLightLevel(Function<BlockState, Integer> lightLevel) - 设置发光等级
     *    - 范围：0（不发光）到15（最大亮度）
     * 6. sound(SoundType sound) - 设置方块音效类型
     *    - SoundType.STONE: 石头音效
     *    - SoundType.WOOD: 木头音效
     *    - SoundType.METAL: 金属音效
     *    - SoundType.GLASS: 玻璃音效
     *    - SoundType.GRAVEL: 沙砾音效等
     * 7. noDrops() - 设置方块被破坏时不掉落任何物品
     * 8. notSolid() - 设置方块为非固体，不阻挡光线和实体移动
     * 9. ticksRandomly() - 设置方块随机进行tick更新
     * 10. waterlogged() - 设置方块可以被水淹没
     * 11. noCollision() - 设置方块无碰撞体积
     * 12. setRequiresTool() - 设置方块挖掘时需要工具
     * 13. slipperiness(float value) - 设置方块光滑度（默认0.6，冰为0.98）
     * 14. jumpFactor(float value) - 设置跳跃因子（影响跳跃高度，默认1.0）
     * 15. speedFactor(float value) - 设置移动速度因子（默认1.0）
     * 16. strength(float strength) - 同时设置硬度和爆炸抗性为相同值
### 方块创建示例
```java
public static final RegistryObject<{继承自的类名}> {blockID.upper()} = registerBlock(
        "{blockID}",
        () -> new {继承自的类名}(
            AbstractBlock.Properties.create(Material.{指定的材质})
                .hardnessAndResistance(1f)
                .harvestLevel(0)
                ...
        )
    );
```

# 不要忘了导入！
# 示例
```java
package com.{basePackage}.{modid}mod;


import com.{basePackage}.{modid}mod.block.ModBlocks;
```
# 添加ModItems.java

- 当没有item文件夹时，在{modDirectory}\forge-1.16.5-36.2.34-mdk\src\main\java\com\{basePackage}\{modid}mod\
- 创建一个新的item文件夹，并添加ModItems.java
- 在ModItems.java中添加以下代码：
```java
package com.{basePackage}.{modid}mod.item;

import com.{basePackage}.{modid}mod.ModBlocks;
import net.minecraft.item.Item;
import net.minecraftforge.fml.RegistryObject;

public class ModItems {
    public static final DeferredRegister<Item> ITEMS = DeferredRegister.create(ForgeRegistries.ITEMS, {MainClassName}.MOD_ID);

}
```
# 在{MainClassName}类中注册方块和物品
```java
...
   public {MainClassName}() {//构造函数名需要和类名一致
        // Register the setup method for modloading
        IEventBus modEventBus = FMLJavaModLoadingContext.get().getModEventBus();

        // Register the blocks
        ModBlocks.BLOCKS.register(modEventBus);
        // Register the items
        ModItems.ITEMS.register(modEventBus);



        modEventBus.addListener(this::setup);
        // Register the enqueueIMC method for modloading
        modEventBus.addListener(this::enqueueIMC);
        // Register the processIMC method for modloading
        modEventBus.addListener(this::processIMC);
        // Register the doClientStuff method for modloading
...
```
# 添加blockState
创建{modDirectory}\forge-1.16.5-36.2.34-mdk\src\main\resources\assets\{modid}\blockstates\{方块ID}.json
内容如下（默认）：
```json
{
    "variants": {
        "": {
            "model": "{modid}:block/{方块ID}"
        }
    }
}
```
# 添加模型（当选择的父类是Block）
创建{modDirectory}forge-1.16.5-36.2.34-mdk\src\main\resources\assets\{modid}\models\block\{方块ID}.json
内容如下（默认）：
```json
{
    "parent": "block/cube_all",
    "textures": {
        "all": "{modid}:texture/{方块ID}"
    }
}
```
# 添加掉落物模型
创建{modDirectory}forge-1.16.5-36.2.34-mdk\src\main\resources\assets\{modid}\models\item\{方块ID}.json
内容如下（默认）：
```json
{
    "parent": "block/{方块ID}"
}
```
# 添加战利品表（需要在创建模组的过程中把战利品表设为默认选择）
创建{modDirectory}\forge-1.16.5-36.2.34-mdk\src\main\resources\assets\{modid}\loot_tables\blocks\{方块ID}.json
内容如下（默认）：
```json
{
    "type": "minecraft:block",
    "pools": [
        {
            "rolls": 1,
            "entries": [
                {
                    "type": "minecraft:item",
                    "name": "{modid}:{方块ID}"
                }
            ]
        }
    ]
}
```
# 添加方块信息到{modDirectory}\mod.json
```json
{
"blocks": [
        {
            "name": "{方块ID}",
            "material": "{指定的材质}",
            "hardness": <硬度（在mod.json中使用浮点数存储，没有"f"，因为json和java语法不同）>,
            "resistance": <爆炸抗性（在mod.json中使用浮点数存储，没有"f"，因为json和java语法不同）>,
            "harvestLevel": <挖掘等级（整数）>,
            "harvestTool": "<挖掘工具（例如：pickaxe, axe, shovel等）>",
            "lightValue": <亮度（整数，范围0-15）>,
            "lightOpacity": <透明度（整数，范围0-255）>,
            "creativeTab": "{modid}",
            "textureName": "{modid}:block/{方块ID}",
            "model": "{modid}:block/{方块ID}",
            "defaultState": {
                "axis": "<默认方向（例如：y, x, z）>"
            },
            "variants": [
                "（字符串里的方括号表示可选，下同）[key=value]",{
                    "model": "{modid}:block/{方块ID}",
                    ...
                }
            ],
            "tileEntity": {
                "type": "{modid}:{方块ID}_entity",
                "class": "net.minecraft.tileentity.TileEntityType"
            }
        }
  ]
}
```
# 添加Itemgroup信息到mod.json（如果新建了ItemGroup）
```json
{
  "itemGroups": [
    {
      "name": "{ItemGroupID}"
    },
    ...
  ]
}
```
# 之后，提示用户选择贴图文件（提示用户尽量是1:1的文件），格式必须为png
将用户选择的png复制到{modDirectory}\forge-1.16.5-36.2.34-mdk\src\main\resources\assets\{modid}\texture\block\{方块ID}.png

# 最后，为read()方法添加能读取上述信息并显示的逻辑（所有的key使用中文显示），更新显示
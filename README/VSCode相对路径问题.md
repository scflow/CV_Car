# VS Code   相对路径问题

## 1 概述

​	vs code中的相对路径指定不是执行文件的相对路径，而是执行文件夹的相对路径。这是vs code的特性之一。

​	因此在执行相对路径文件时，会报错文件不存在。

​	Error reading file

![Screenshot01](..\Picture\README File\Screenshot01.png)

## 2 解决

#### 2.1 改为相对的相对路径(不推荐)

​	将文件路径改为相对于所打开的文件夹的相对路径

> [!NOTE]
>
> 注意：Windows用户注意把`\`改为 `/`

#### 2.2 更改设置(推荐)

​	打开vs code设置，搜索"终端"or“terminal”，选择“python“，勾选”Execute In File Dir“保存后即可生效

![Screenshot02](..\Picture\README File\Screenshot02.png)

![Screenshot03](..\Picture\README File\Screenshot03.png)

参考链接：https://blog.csdn.net/CSDN_push/article/details/135947235
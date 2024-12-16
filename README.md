# CV Car

## 简介

树莓派循迹小车，实现功能包括循迹，停车，避障。完成度六七成的样子。

## 仓库地址

| 仓库   | 地址                               |
| ------ | ---------------------------------- |
| Github | https://github.com/scflow/CV_Car   |
| Gitee  | https://gitee.com/gongjc-xy/CV_Car |

## 运行设备

树莓派4B(Raspiberry4B)

## 所需环境

python3(所需pip包见requirements.txt)

### 选配

如果需要使用[Network RC远程遥控](https://network-rc.esonwong.com/)，系统建议使用raspios-buster-armhf，三者建议均对上，否则大概率访问不了，下载镜像 [2021-12-02-raspios-buster-armhf.zip](https://downloads.raspberrypi.org/raspios_oldstable_armhf/images/raspios_oldstable_armhf-2021-12-02/2021-12-02-raspios-buster-armhf.zip)，详情见[树莓派上安装-network-rc](https://network-rc.esonwong.com/guide.html#%E6%A0%91%E8%8E%93%E6%B4%BE%E4%B8%8A%E5%AE%89%E8%A3%85-network-rc)。

当然，如果不需要，推荐64位Ubuntu

## 代码思路

- **循线**: 与传统循线类似，通过膨胀复制滤波等操作获得大致线条，然后使用霍夫变换拟合直线，并计算数据转化为边线对象，效果还不错，就是只能转化为直线，太弯弯绕绕或者直角拐弯肯定不行，边线上顶点取平均值记中点，通过PID与卡尔曼滤波综合控制舵机
- **校正**: 摄像头存在一定畸变，干扰拟合，因此使用了校正，具体方法CSDN上有，但如果需求不是那么强烈也可以不矫正，实测运行时python校正一次20ms左右
- **目标检测**: 起初是用的特征匹配，如果性能足够的话还是可以的，但是树莓派性能还是差了点，实时性不够，所以几乎不可用，后来换了模型，采用的https://github.com/dog-qiuqiu/FastestDet这个的目标检测模型，比较轻量化，也适合简单物体检测
- **颜色单一物体检测**: 参考了车流量检测的代码，将单色物体HSV过滤后，腐蚀后膨胀，融合成一个整体，避免反光等原因识别出多个小的
- **日志**:使用了loguru库，同时代码中通过单帧图片保存保留关键帧图片，便于后续分析

## 项目运行

### 安装准备

```bash
git clone https://gitee.com/gongjc-xy/CV_Car.git
cd CV_Car
chmod +x ./install.sh
./install.sh
```

如果一切顺利，接下来就可以尝试运行，run2是执行代码的指令，run2 后增加对应该文件夹下python文件也可执行对应python代码

```bash
run2
```

## 实测表现

- 运行时大概有17帧左右，如果有识别任务可能只有10或者更低
- 循线效果还行，断断续续的线也能走，但是如果遇到光斑效果依旧较差
- 检测效果一般，稳定性不强

## 小Tips

Network RC远程遥控驾驶远程往往是需要代理服务器的，但是如果服务器网络一般，远程遥控就会很卡，体验感是非常差的

代理其实是相当于把这个端口号与服务器的对应端口号绑定(当然我讲的可能不对)，本来我们也是可以用WiFi连接下的地址192.168.xxx.xxx:8088之类的进行连接，但假如访问网页的设备没连接这个WiFi，那就连不上，因为这是局域网，而如果想要随处可连，其实完全可以绕过代理，走公网。

最主要的其实是这个端口号，通过设备IP地址加该端口号便可以访问，ipv4与ipv6都是可以的，ipv4一般情况下是只有局域网的，公网数量有限，在小车上几乎不可能有的，ipv6呢，由于其数量庞大，同时可以分配局域网和公网，当然，公网ipv6不是永久的，每隔一段时间便会换一个。

终端中输入ifconfig(windows是ipconfig)即可查看，如下图(图片取自[Windows 10 Insider build 14965 中的 ifconfig 和网络连接枚举支持](https://devblogs.microsoft.com/commandline/ifconfig-and-network-connection-enumeration-support-in-windows-10-insider-build-14965/)),inet就是ipv4的地址，而inet6自然就是ipv6了，fe80开头那段就是局域网的，剩下的就是公网ip了，ipv6加端口号访问网站百度搜一搜就行，[inet6地址]:端口号![ifconfig截图](https://devblogs.microsoft.com/wp-content/uploads/sites/33/2019/02/ifconfig-600x416.png)

如果是走流量、基站，一般都会给公网ipv6，如果是WiFi，就要看支不支持了，这不好说，有的可能并不会开通ipv6。所以远程遥控还是要推荐走4G/5G

单次公网ipv6租期有限，而且作为玩具小车，安全隐患还是不大的，还担心可以结合运维面板配下防火墙




如果代码运行有问题，可能是版本问题，也可能是我提交的代码有问题，漏交了或者错交了，代码问题可以提issue反馈，或者发邮件给我
后期大概率也不会改动代码了，代码看起来挺多，但是很烂，功能后面越写越分不清，代码命名混乱，但我觉得有几个思路还是可以的，如果有什么问题想问的，可以发邮件给我，hyperslip@outlook.com
#升级工具
这是为cocos2d-x引擎开发者提供的升级工具，方便大家从低版本直接升级到最新版本的引擎（也支持升级到指定的引擎版本）。支持cocos2d-x/lua/js项目。

这是一个脚本工具，在终端执行，目前仅支持Mac平台，windows平台支持开发中。升级范围包括ios/mac/android平台，win32/win8/linux未充分验证。

##如何使用

升级过程使用了一些辅助工具，点击查看[准备工作](#prepare)。

#####如果你的游戏对引擎源码没有修改，或者只做过少量修改，推荐使用下面的命令行升级，简称为A方案：

	$ python A/cocos_upgrade.py -d /Users/testProject -n testProject -v 3.5
	
-d 游戏工程目录，请使用工程全路径。

-n 游戏工程名称，请注意工程名有时与目录名称不一致，建议参考xcode工程名。

-v 要升级的引擎版本，请查看[支持的版本](#jump2)。

`特别提醒：升级后的工程目录在/Users/testProjectUpgrade`


#####如果你的游戏对引擎有修改，推荐使用下面的命令行升级，简称为B方案：


	$ python B/cocos_upgrade.py -s /Users/cocos2d-x-3.2 -d /Users/cocos2d-x-3.5 -p /Users/testProject -n testProject

-s 原引擎目录，请使用全路径。如果你的游戏基于cocos2d-x-3.2，请先下载解压到本地硬盘。[请到这里下载。](http://www.cocos2d-x.org/download/version)

-d 要升级引擎目录，请使用全路径。如果你的游戏要升级到cocos2d-x-3.5，请先下载解压到本地硬盘。[请到这里下载。](http://www.cocos2d-x.org/download/version)


-p 待升级的工程目录，请使用全路径。

-n 游戏工程名称，请注意工程名有时与目录名称不一致，建议参考xcode工程名。

`特别提醒：升级后的工程目录在/Users/testProjectUpgrade/Target/testProject`


##<a name="prepare">准备工作
#####1 保证git能正常运行，执行如下命令行查看。
	$ git version
	git version 1.9.3 (Apple Git-50)
#####2 把以下内容加入~/.bash_profile 或 ~/.zshrc

	export LC_CTYPE=C 
	export LANG=C

如升级过程遇到下面这个问题，请检查上面的内容是否加入成功。

sed: RE error: illegal byte sequence

#####3 安装wiggle
	$ sudo apt-get install -y wiggle
	or
	$ brew install -y wiggle
	
	$ wiggle --version
	wiggle 1.0 2013-08-23 GPL-2+ http://neil.brown.name/wiggle/
	
如果你没有brew，请运行下面的命令安装

	ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"


#####4 下载安装

[点击下载Diffmerge](https://sourcegear.com/diffmerge/downloads.php)，这是一个免费软件。

#####5 配置Diffmerge命令行
	$ sudo cp /Applications/DiffMerge.app/Contents/Resources/diffmerge.sh /usr/bin
	$ diffmerge.sh
	
#####6 安装python
	$ python --version 
	Python 2.7.6

#####7 下载原引擎版本和目标引擎版本
比如你的游戏基于cocos2d-x 3.2，希望升级到cocos2d-x 3.5，那就下载3.2和3.5。

[请到这里下载。](http://www.cocos2d-x.org/download/version)


##<a name="jump2">支持的版本

目前只支持从低版本升级到高版本，版本在以下范围内才能升级。

	cocos2d-x(C++/Lua): 3.0 3.1 3.2 3.3 3.4 3.5
	cocos2d-Js: v3.0 v3.1 v3.2 v3.3 v3.5
	
	
如果你的版本不在以上范围内，也可以自己制作升级补丁进行，[自定义升级](#jump1)。

	
##升级说明
A方案升级工具会在游戏工程基础上，自动合并新版本引擎源码和工程配置(.pbproj/.mk/.sln）等内容，同时会产生文件冲突（与修改引擎文件）。`请解决冲突后编译运行`。如果冲突太多，无法解决，请使用B方案。

B方案会替换引擎相关目录，自动合并新版本引擎源码和工程配置(.pbproj/.mk/.sln）等内容，自动记录游戏工程中修改了引擎的代码，并通过Diffmerge工具对修改内容进行对比，帮助开发者合并代码。以下是Diffmerge工具的介绍

#####Diffmerge
窗口内有三个打开的文件界面，左边是你的游戏工程文件，右边是引擎HelloWorld工程文件（即默认初始代码），中间是升级后的游戏工程文件，我们分别称为L文件、R文件和C文件。


只要三个文件中有任意两个内容不一致，Diffmerge就会用颜色标记出来，一般我们只需要处理界面最左边竖条内标记为`红色`的部分－－－那表示L与R不一致，同时L与C也不一样，这些就是开发者在原来引擎基础上修改的代码。开发者需要判断L文件中的内容，如何合并到C文件中。
![Mou icon](https://github.com/calfjohn/cocosUpgrade/blob/SemiAutomatic/images/Compare3files.jpeg?raw=true)


#####异常情况：

这种表示二进制文件不同，这种情况不用关注，直接关闭退出Diffmerge。

![Mou icon](https://github.com/calfjohn/cocosUpgrade/blob/SemiAutomatic/images/BinaryCompare.jpg?raw=true)


这种表示在升级后的工程内，这个文件不存在了，开发者需要判断是否需要手动把这个文件从游戏工程中拷贝到升级后的工程内。处理完成后关闭这个提示。

![Mou icon](https://github.com/calfjohn/cocosUpgrade/blob/SemiAutomatic/images/NotFoundFile.jpg?raw=true)


##<a name="jump1">自定义升级
例如，你的游戏工程是基于cocos2d-x 3.1.1开发，希望升级到3.5，那么你需要下载引擎Cocos2d-x 3.1.1和cocos2d-x 3.5到本地硬盘，利用下面的工具制作补丁文件。

	$ python A/cocos_make_patch.py -s 3.1.1引擎目录 -d 3.5引擎目录 -o /Users/patchFilePath -l cpp

-s 引擎版本，请使用全路径。

-d 引擎版本，请使用全路径。

-o 升级文件输出目录

-l 工程类型，js/lua/cpp

`生成的文件0001-Upgrade.patch在输出目录下`。

最后调用cocos_upgrade2.py来调用补丁进行升级。

	$ python A/cocos_upgrade2.py -d /Users/testProject -n testProject -p /Users/patchFilePath/0001-Upgrade.patch


-d 游戏工程目录，请使用工程全路径。

-n 游戏工程名称，请注意工程名有时与目录名称不一致，建议参考xcode工程名。

-p 升级用补丁，升级用补丁的文件全路径。此文件可到[服务器](http://www.cocos2d-x.org)下载

`特别提醒：升级工作是在游戏工程的副本上进行的，副本目录是/Users/testProjectUpgrade`
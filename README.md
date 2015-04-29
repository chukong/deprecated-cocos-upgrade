
#<a name="jumpA">升级引擎工具A篇

##适用范围
对引擎源码没有修改或扩展的cocos2d-x/lua/js项目，或者只做过少量修改。否则请查看[升级引擎工具B篇](#jumpB)。目前仅支持Mac平台，windows平台支持开发中。

##准备工作
#####1 保证git能正常运行
	$ git version
	git version 1.9.3 (Apple Git-50)
#####2 以下内容加入~/.bash_profile 或 ~/.zshrc

	export LC_CTYPE=C 
	export LANG=C

这是为了解决这个问题
sed: RE error: illegal byte sequence

#####3 安装wiggle
	$ sudo apt-get install -y wiggle
	or
	$ brew install -y wiggle
	
	$ wiggle --version
	wiggle 1.0 2013-08-23 GPL-2+ http://neil.brown.name/wiggle/
	
如果你没有brew，请运行下面的命令安装

	ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"


##如何使用

有两种升级方式，请按自己的情况选择。

####第一种方式，会根据游戏工程的引擎版本自动寻找下载对应的升级文件。

	$ python cocos_upgrade.py -d /Users/testProject -n testProject -v 3.5
	
-d 游戏工程目录，请使用工程全路径。

-n 游戏工程名称，请注意工程名有时与目录名称不一致，建议参考xcode工程名。

-v 要升级的引擎版本，请查看[支持的版本](#jump2)。


####第二种方式，你需要自行指定升级文件，不过你可以自己创建符合自己需求的升级文件，请查看[制作升级文件](#jump1)。

	$ python cocos_upgrade2.py -d /Users/testProject -n testProject -p /Users/test30-35.diff


-d 游戏工程目录，请使用工程全路径。

-n 游戏工程名称，请注意工程名有时与目录名称不一致，建议参考xcode工程名。

-p 升级用补丁，升级用补丁的文件全路径。此文件可到[cocos官方网站下载(未完成)](http://www.cocos2d-x.org)下载，也可以自行制作。

`特别提醒：升级工作是在游戏工程的副本上进行的，副本目录是/Users/testProjectUpgrade`


##<a name="jump1">制作升级文件
例如，你的游戏工程是基于Cocos2d-x 3.2
开发，希望升级到3.5，那么你需要下载Cocos2d-x 3.2和Cocos2d-x 3.5，利用下面的工具制作补丁文件，生成的文件0001-Upgrade.patch在输出目录下。

	$ python cocos_make_patch.py -s 3.2引擎目录 -d 3.5引擎目录 -o /Users/patchFilePath -l cpp

-s 基于3.2引擎版本，请使用全路径。

-d 基于3.5引擎版本，请使用全路径。

-o 升级文件输出目录

-l 工程类型，js/lua/cpp

最后调用cocos_upgrade2.py来调用补丁进行升级。

	
##升级说明
升级工具会在游戏工程基础上，自动合并新版本引擎源码和工程配置(.pbproj/.mk/.sln）等内容，同时会产生文件冲突（与修改引擎文件）。

`请解决冲突后编译运行`。

如果冲突太多，无法解决，请阅读[升级引擎工具B篇](#jumpB)。


#<a name="jumpB">升级引擎工具B篇

##适用范围
所有cocos2d-x/lua/js项目。用此工具升级，需开发者自行对比升级后的差异。希望自动升级请查看[升级引擎工具A篇。](#jumpA)。目前仅支持Mac平台，windows平台支持开发中。

##准备工作
#####1 下载安装

[点击下载Diffmerge](https://sourcegear.com/diffmerge/downloads.php)，这是一个免费软件。

#####2 配置Diffmerge命令行
	$ sudo cp /Applications/DiffMerge.app/Contents/Resources/diffmerge.sh /usr/bin
	$ diffmerge.sh
	
#####3 安装python
	$ python --version 
	Python 2.7.6

#####4 下载原引擎版本和目标引擎版本
比如你的游戏基于cocos2d-x 3.2，希望升级到cocos2d-x 3.5，那就下载3.2和3.5。

[请到这里下载。](http://www.cocos2d-x.org/download/version)

#####5 保证git能正常运行
	$ git version
	git version 1.9.3 (Apple Git-50)
#####6 以下内容加入~/.bash_profile 或 ~/.zshrc
	export LC_CTYPE=C 
	export LANG=C

#####7 安装wiggle
	$ sudo apt-get install -y wiggle
	or
	$ brew install -y wiggle
	
	$ wiggle --version
	wiggle 1.0 2013-08-23 GPL-2+ http://neil.brown.name/wiggle/
	
##如何使用

	$ python cocos_upgrade.py -s /Users/cocos2d-x-3.2 -d /Users/cocos2d-x-3.5 -p /Users/testProject -n testProject

-s 原引擎目录，请使用全路径。

-d 目标引擎目录，请使用全路径。

-p 待升级的工程目录，请使用全路径。

-n 游戏工程名称，请注意工程名有时与目录名称不一致，建议参考xcode工程名。

`特别提醒：升级工作是在游戏工程的副本上进行的，副本目录是/Users/testProjectUpgrade/target/testProject`
	
##升级说明
#####1 升级工具会替换引擎目录，修改游戏工程配置(.pbproj/.mk/.sln等）文件

#####2 自动记录游戏工程中引擎相关修改，并通过Diffmerge工具对修改内容进行对比，帮助开发者合并代码。

#####3 Diffmerge窗口内有三个打开的文件界面，左边是你的游戏工程文件，右边是引擎HelloWorld工程文件（即默认初始代码），中间是升级后的游戏工程文件，我们分别称为L文件、R文件和C文件。


只要三个文件中有任意两个内容不一致，Diffmerge就会用颜色标记出来，一般我们只需要处理界面最左边竖条内标记为`红色`的部分－－－那表示L与R不一致，同时L与C也不一样，这些就是开发者在原来引擎基础上修改的代码。开发者需要判断L文件中的内容，如何合并到C文件中。
![Mou icon](https://github.com/calfjohn/cocosUpgrade/blob/SemiAutomatic/images/Compare3files.jpeg?raw=true)


#####4 Diffmerge有一些异常情况如下：

这种表示二进制文件不同，这种情况不用关注，直接关闭退出Diffmerge。

![Mou icon](https://github.com/calfjohn/cocosUpgrade/blob/SemiAutomatic/images/BinaryCompare.jpg?raw=true)


这种表示在升级后的工程内，这个文件不存在了，开发者需要判断是否需要手动把这个文件从游戏工程中拷贝到升级后的工程内。处理完成后关闭这个提示。

![Mou icon](https://github.com/calfjohn/cocosUpgrade/blob/SemiAutomatic/images/NotFoundFile.jpg?raw=true)


##<a name="jump2">支持的版本

目前只支持从低版本升级到高版本，版本在以下范围内才能升级。

	Cocos2d-x(C++/Lua): 3.0 3.1 3.2 3.3 3.4 3.5
	Cocos2d-Js: v3.0 v3.1 v3.2 v3.3 v3.5

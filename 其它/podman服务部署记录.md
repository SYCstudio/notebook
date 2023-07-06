# podman服务部署记录

不小心删库了，重新部署一些服务，记录一下踩的坑

## koel
数据库有文件权限问题，一旦将数据库文件映射到本地文件目录，就连接不上，推断是它代码有问题  
在 podman 里设置为新建卷挂载即可，不过这样就不能持久化了  
这玩意 bug 挺多的，平时不要随便动，能用就行了

## sharelatex
固定版本为 3.5.6 更新的版本似乎有数据库连接问题（推测仍然是权限问题）

默认的 sharelatex 版本是精简版的，下面使之支持中文和 minted

下载 tlmgr 更新脚本： `wget http://mirror.ctan.org/systems/texlive/tlnet/update-tlmgr-latest.sh`  
更新 tlmgr：`sh update-tlmgr-latest.sh -- --upgrade`  
更换到国内源：`tlmgr option repository https://mirrors.tuna.tsinghua.edu.cn/CTAN/systems/texlive/tlnet/`  
tlmgr 自更新：`tlmgr update --self --all`  
安装完整版 texlive：`tlmgr install scheme-full`  

将字体安装到 /usr/share/font 目录下，然后使用 `mkfontscale`,`mkfontdir`,`fc-cache -fv` 刷新（需要包 `ttf-mscorefonts-installer` 和 `fontconfig`

安装支持 minted 包的 pygments：`python3-pygments
`
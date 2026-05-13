##  Runner 设置

### 下载并配置 Gitlab-runner

1. 在 Gitlab-runner 主页下载 gitlab-runner。推荐先使用 `curl` 下载，然后移动到 `/usr/local/bin` ，之后再使用 `sudo` 执行。
2. 创建用户`sudo useradd --comment 'GitLab Runner' --create-home gitlab-runner --shell /bin/bash`
3. 安装为 system service `sudo gitlab-runner install --working-directory=/home/gitlab-runner` `sudo gitlab-runner start`
### 为 Repo 注册 Runner

1. 在 gitlab 对应 repo 界面，进入 `Settings -> CI/CD -> Runner` 找到 `registration token` 
2. 执行 `gitlab-runner register`
3. 然后会进入一个交互界面，依次输入 gitlab 的地址和之前的 `registration token`。注意这里的 tags，需要与 repo 界面的一致，或者之后在 repo 中设置允许无 tag 匹配也可以运行。
4. 在选择 `executor` 界面选择 Docker 作为后端。

执行 `gitlab-runner status` 、 `gitlab-runner list` 和 `gitlab-runner verify` 均可以查看注册是否成功。  

### 其他配置

所有的 Gitlab runner 配置均会在 `/etc/gitlab-runner/config.toml` 内，在注册成功后，如果需要修改某个 Runner 的配置，可以直接从这里修改。

在最外层可以用 `concurrent=x` 配置最大可并行次数。  
在 `[runners.docker]` 内设置 `pull_policy = ["if-not-present"]` 允许 docker 先检查本地镜像缓存，避免每次都从远端拉取镜像。

下面时一个包含两个 runner 的例子，设置 `concurrent=4` 且均有限使用本地 docker  缓存。

```toml
concurrent = 4
check_interval = 0
connection_max_age = "15m0s"
shutdown_timeout = 0

[session_server]
  session_timeout = 1800

[[runners]]
  name = "autosketch-runner"
  url = "http://gitlab.xxx.com"
  id = 2
  token = "114514"
  token_obtained_at = 2026-04-22T08:07:35Z
  token_expires_at = 0001-01-01T00:00:00Z
  executor = "docker"
  [runners.cache]
    MaxUploadedArchiveSize = 0
    [runners.cache.s3]
      AssumeRoleMaxConcurrency = 0
    [runners.cache.gcs]
    [runners.cache.azure]
  [runners.docker]
    tls_verify = false
    image = "python:3.13"
    privileged = false
    disable_entrypoint_overwrite = false
    oom_kill_disable = false
    disable_cache = false
    volumes = ["/cache"]
    volume_keep = false
    pull_policy = ["if-not-present"]
    shm_size = 0
    network_mtu = 0

[[runners]]
  name = "gitlabrunner-for-node"
  url = "http://gitlab.xxx.com"
  id = 3
  token = "1919810"
  token_obtained_at = 2026-05-09T11:48:18Z
  token_expires_at = 0001-01-01T00:00:00Z
  executor = "docker"
  [runners.cache]
    MaxUploadedArchiveSize = 0
    [runners.cache.s3]
      AssumeRoleMaxConcurrency = 0
    [runners.cache.gcs]
    [runners.cache.azure]
  [runners.docker]
    tls_verify = false
    image = "node:24"
    privileged = false
    disable_entrypoint_overwrite = false
    oom_kill_disable = false
    disable_cache = false
    volumes = ["/cache"]
    volume_keep = false
    pull_policy = ["if-not-present"]
    shm_size = 0
    network_mtu = 0

```

## Trouble Shooting

### 生成 Artifact 时，报错413 Request Entity Too Large

整个链路上存在一环对 HTTP 的文件大小做了限制，需要从 nginx 和 gitlab 两个角度寻找问题。  

Nginx：查找是否有 `client_max_body` 设置，如果没有，则需要显示设置大小，比如 `client_max_body 500m` 
Gitlab：在 UI 界面，查找 `Admin Area -> Settings -> CI/CD` 中 `Maximum artifacts size` 的设置，将其设置为合适的大小。

### Gitlab-runner 注册成功，且在 repo 界面能够看到，但触发 Action 时显示 Pipeline 卡住

可能是 action 的 tags 没有和 Runner 匹配上。进入repo 的 `Settins -> CI/CD -> Runner` 对应 Runner 的配置，将 `Run untagged jobs` 勾选，允许 Tag 不匹配的任务执行
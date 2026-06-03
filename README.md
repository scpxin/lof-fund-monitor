# LOF 基金溢价监控系统

监控 LOF 基金溢价率，每日自动推送到微信。

## 功能

- 实时监控 LOF 基金溢价率
- 自动获取申购限额信息
- 每日定时推送到微信
- 高溢价/折价自动预警
- 支持 Server 酱和 PushPlus 两种推送方式（均免费）
- **支持 GitHub Actions 云端运行（完全免费）**

## 快速开始

### 方式一：GitHub Actions 云端运行（推荐）

无需本地服务器，24 小时自动运行。

#### 步骤 1：创建 GitHub 仓库

1. 在 GitHub 创建新仓库（私有或公开均可）
2. 将此项目代码 push 到仓库

#### 步骤 2：配置 Secret

在 GitHub 仓库中：

1. 进入 **Settings** → **Secrets and variables** → **Actions**
2. 点击 **New repository secret**
3. 添加以下 Secret：

| Name | Value |
|------|-------|
| `SERVER_CHAN_KEY` | `SCT358776TaSj8FQJvORlEsSowbyCRqjyLim` |

#### 步骤 3：配置 Variables（可选）

如需自定义配置，添加以下 Variables：

| Name | Value | 说明 |
|------|-------|------|
| `PUSH_METHOD` | `server_chan` | 推送方式 |
| `PREMIUM_RATE_THRESHOLD` | `1.0` | 溢价率阈值 |
| `LOF_FUND_CODES` | `["161706","163406",...]` | JSON 数组格式的基金代码列表 |

#### 步骤 4：启用 Actions

1. 进入 **Actions** 标签页
2. 点击 **I understand my workflows, go ahead and enable them**
3. 手动触发一次测试：点击 **LOF Fund Monitor** → **Run workflow**

#### 步骤 5：查看运行时间

默认配置：
- **交易日 15:30**（下午收盘后）
- **交易日 20:00**（晚间加推一次）

修改时间需编辑 `.github/workflows/monitor.yml` 中的 cron 表达式。

### 方式二：本地运行

```bash
pip install -r requirements.txt
```

### 方式二：本地运行

```bash
pip install -r requirements.txt
python scheduler.py --once
```

### Cron 表达式参考

| 时间 | Cron 表达式 |
|------|-----------|
| 每天 9:30（开盘） | `30 1 * * *` |
| 每天 15:30（收盘） | `30 7 * * *` |
| 工作日 9:30 | `30 1 * * 1-5` |
| 工作日 15:30 | `30 7 * * 1-5` |
| 每 4 小时一次 | `0 */4 * * *` |

注意：cron 使用 UTC 时间，中国时间 = UTC + 8

## 手动触发

在 GitHub Actions 页面可以手动触发运行，无需等待定时任务。

**方式一：Server 酱（推荐）**

1. 访问 https://sct.ftqq.com 注册登录
2. 绑定微信公众号（关注"方糖"公众号）
3. 获取 `SCKEY`

**方式二：PushPlus**

1. 访问 http://www.pushplus.plus 注册登录
2. 获取 `token`

### 3. 配置文件

复制环境变量配置：

```bash
cp .env.example .env
```

编辑 `.env` 文件：

```bash
SERVER_CHAN_KEY=你的 SCKEY
PUSH_PLUS_TOKEN=你的 PushPlus Token
PUSH_METHOD=server_chan
PREMIUM_RATE_THRESHOLD=1.0
PUSH_TIME=15:30
```

### 4. 运行

**测试运行（立即执行一次）：**

```bash
python scheduler.py --once
```

**启动定时任务（后台运行）：**

```bash
nohup python scheduler.py > monitor.log 2>&1 &
```

## 免费推送方案对比

| 方案 | 每日限额 | 优点 | 缺点 |
|------|----------|------|------|
| Server 酱 | 多条免费 | 稳定、配置简单 | 需要关注公众号 |
| PushPlus | 每月限额 | 支持模板丰富 | 限额较严格 |
| 企业微信 | 无限制 | 完全免费 | 需要配置企业微信 |

## GitHub Actions 额度

- 免费账户：**2000 分钟/月**
- 每次运行约 1-2 分钟
- 每天运行 2 次 ≈ 60 分钟/月，额度充足

## 许可证

MIT License

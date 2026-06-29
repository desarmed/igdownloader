[English](README.md) · [Português](README.pt-BR.md) · [Español](README.es.md) · **中文**

---

# IG Baixador

个人桌面端 Instagram 内容下载器（支持 Windows 和 macOS）。
它运行**在你自己的电脑上、用你自己的 IP 和你已登录的会话**——正因如此，当公共下载网站（SnapInsta、iGram 等）宕机时，它依然能用。

粘贴一个或多个链接即可一次性下载。视频会导出为**带声音的单个 MP4 文件**（内置 ffmpeg——你无需额外安装任何东西）。

## 能下载什么
- **Reels 和视频**（主打功能）——带音频的 MP4
- 信息流里的照片和多图轮播
- 快拍和精选（需配置好 cookies）
- 整个主页（粘贴主页链接即可）

## 如何使用
1. 打开 **IG Baixador**（Windows：`IG-Baixador.exe`；Mac：打开 `.dmg`，把应用拖进去，并在**第一次打开时右键 → 打开**）。
2. **Cookies（首次使用）：** Instagram 只会向已登录用户提供内容，而 Chrome 不允许自动读取它的 cookies。因此请这样做：
   - 在 Chrome 中安装 **"Get cookies.txt LOCALLY"** 扩展（免费，本地运行）。
   - 打开已登录的 `instagram.com`，让该标签页处于最前，点击扩展图标 → **Export**。
   - 在应用中点击 **"选择 cookies.txt"**，选中刚下载的文件。
   - 应用内的 **"❔ 如何使用"** 按钮里也有这套操作步骤。
3. 粘贴一个或多个链接（每行一个），点击 **"全部下载"**。每个链接都会在队列里变成一行，并显示进度。

## 开发

需要 Python 3.11+。

```bash
python -m venv .venv
.venv\Scripts\pip install -r requirements-dev.txt   # pytest, pyinstaller
.venv\Scripts\pip install -r requirements.txt       # customtkinter

# 内置的外部二进制文件（不纳入版本控制）——下载到 bin/win/：
curl -L -o bin/win/gallery-dl.exe https://github.com/mikf/gallery-dl/releases/download/v1.31.10/gallery-dl.exe
curl -L -o bin/win/yt-dlp.exe     https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp.exe
# + ffmpeg.exe 和 ffprobe.exe（例如 gyan.dev 的静态构建）放到 bin/win/

.venv\Scripts\python -m pytest -q          # 测试
.venv\Scripts\python -m ig_baixador        # 启动窗口

# 构建 .exe（在仓库根目录运行）：
.venv\Scripts\pyinstaller build\ig-baixador.spec --noconfirm --distpath dist --workpath build\work
```

**macOS** 版应用（`.dmg`）由 GitHub Actions（工作流 `build-mac.yml`）在 macOS runner 上生成——无法从 Windows 编译出 Mac 版应用。

## 工作原理
以 **customtkinter** 作为外壳（界面），底层以 **gallery-dl** 为主引擎，**yt-dlp** 作为备用，并用 **ffmpeg** 把音频和视频合并到一起。会话完全来自 cookies（来自浏览器或某个 `cookies.txt`）——应用**从不索要用户名/密码**。

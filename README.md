# 303720的Python能力训练

信息安全基础能力训练的两个练习程序：网页单词提取与 bind shell。

## 环境依赖

- Python 3.x
- [click](https://click.palletsprojects.com/)
- [requests](https://requests.readthedocs.io/)
- [beautifulsoup4](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)

安装依赖：

```bash
pip install click requests beautifulsoup4
```

## 练习一：网页单词提取（wordextractor.py）

爬取网页并提取其中的单词，生成密码词表，支持常见密码变形。

### 用法

```bash
python wordextractor.py --url <URL> [--length <N>] [--output <FILE>] [--depth <N>]
```

### 参数说明

| 参数 | 简写 | 说明 |
| --- | --- | --- |
| `--url` | `-u` | 目标网页 URL（必填） |
| `--length` | `-l` | 最小单词长度，`0` 表示不限制（默认 `0`） |
| `--output` | `-o` | 将词表写入文件而非打印到控制台 |
| `--depth` | `-d` | 爬取深度，仅跟随同域名链接（默认 `0`） |

### 示例

```bash
python wordextractor.py --url https://example.com --length 5 --output wordlist.txt
```

## 练习二：bind shell（bindshell.py）

在目标机器上监听指定端口，等待远程连接并提供命令行界面。

### 用法

```bash
python bindshell.py [--port <PORT>] [--threaded]
```

### 参数说明

| 参数 | 简写 | 说明 |
| --- | --- | --- |
| `--port` | `-p` | 监听端口（默认 `4444`） |
| `--threaded` | `-t` | 多线程并发处理多个客户端 |

### 示例

在目标机器上启动：

```bash
python bindshell.py --port 4444
```

在攻击机上使用 netcat 连接：

```bash
nc <目标IP> 4444
```

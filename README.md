# 文档提取免费版

当前正式版本为`v1.0.0`。这是一个完全离线的Codex基础技能，用于把本地文字型PDF和DOCX整理成可由Excel直接打开的固定字段CSV。

## 功能边界

- 支持：文本PDF、DOCX。
- 单次最多：10个受支持文件。
- 输出：UTF-8 BOM CSV。
- 固定字段：文件名、格式、标题、字符数、页数或段落数、文本预览、状态、错误。
- 不联网、不上传文档、不需要API Key。

不支持扫描PDF、PNG/JPG、自定义YAML、字段证据、置信度、人工复核表、断点恢复和商业支持。

## 运行示例

```powershell
python -m pip install -r requirements.txt
python .\scripts\generate_examples.py
```

示例结果生成到`examples/output/提取结果.csv`。全部示例均由程序合成，不含客户资料。

处理自己的文件：

```powershell
python .\skills\document-extractor-lite\scripts\extract_lite.py `
  --input-dir "D:\待处理文档" `
  --output "D:\处理结果\提取结果.csv"
```

## 安装为Codex技能

下载Release ZIP并校验同名`.sha256`文件后解压，然后在解压目录运行：

```powershell
powershell -ExecutionPolicy Bypass -File .\install.ps1
```

默认安装到`%USERPROFILE%\.codex\skills\document-extractor-lite`。卸载：

```powershell
powershell -ExecutionPolicy Bypass -File .\uninstall.ps1
```

## 免费版与专业版

| 能力 | 免费版 | 专业版 |
|---|---:|---:|
| 文本PDF、DOCX | 是 | 是 |
| 单次文件数 | 10 | 无固定免费版限制 |
| PNG/JPG与扫描PDF | 否 | 是 |
| 客户YAML字段 | 否 | 是 |
| 证据与置信度 | 否 | 是 |
| 四表Excel | 否 | 是 |
| 复核队列 | 否 | 是 |
| 断点恢复 | 否 | 是 |
| 安装升级失败回滚 | 否 | 是 |

专业版咨询：在本仓库创建标题以“专业版咨询”开头的Issue。请勿在Issue中上传真实文档、个人信息、密钥或客户数据。

## 许可

本仓库采用[PolyForm Noncommercial License 1.0.0](LICENSE.md)，允许非商业用途；商业使用、转售、付费交付或集成到商业服务前必须另行取得授权。

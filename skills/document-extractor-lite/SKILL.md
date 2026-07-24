---
name: document-extractor-lite
description: 离线批量提取文本PDF和DOCX的固定基础信息并导出UTF-8 CSV。用户要求快速整理本地文字型PDF或Word、生成可由Excel打开的基础清单，且单次文件不超过10个时使用。不支持扫描件、图片、自定义字段模板、证据表或断点恢复。
---

# 文档提取免费版

## 执行

1. 确认输入目录只包含本次要处理的文本PDF和DOCX。
2. 运行：

   ```powershell
   python scripts/extract_lite.py --input-dir <输入目录> --output <提取结果.csv>
   ```

3. 核对命令返回的`processed`、`success`和`failed`。
4. 报告CSV绝对路径及失败文件，不把输入或输出提交GitHub。

## 固定输出

CSV固定包含：

- 文件名
- 格式
- 标题
- 字符数
- 页数或段落数
- 文本预览
- 状态
- 错误

CSV使用UTF-8 BOM，便于Windows Excel直接打开中文。

## 边界

- 单次最多处理10个受支持文件；超过时停止且不生成部分结果。
- 只支持文字型PDF和DOCX，不支持PNG、JPG、JPEG或扫描PDF。
- 只使用固定字段，不读取客户YAML。
- 不生成证据与置信度工作表，不支持断点恢复。
- 不调用外部API，不读取密钥、Cookie或Token。
- 不破解加密PDF；损坏、加密或空白文档写入失败行。

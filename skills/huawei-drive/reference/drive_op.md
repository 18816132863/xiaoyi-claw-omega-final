# 云盘操作

描述如何查询云盘信息，支持查询云空间总大小和支持云盘上传的剩余空间大小。

## 查询云盘大小

查询云盘的空间大小信息，并返回 Markdown 信息描述。

### 执行步骤

1. 用户提及查询云盘信息，查询云盘空间大小时执行
2. 调用 `huawei_drive.py` 指定命令`query`进行查询

### 输出格式
```
云盘空间详情如下
总空间：200 GB
已用空间：30 GB
可用空间：170 GB
```
> 调用命令查询到的大小单位为Byte，输出格式按空间大小转化为按TB/GB/MB/KB为单位。

如果云盘信息中的`userCapacity`（总空间）等于0或者`available_space`（可用空间）小于等于0时，提示用户购买云空间套餐

### CLI 命令示例

```bash
# 查询云盘空间详情（总空间，已用空间，剩余空间）
python huawei_drive.py --command query --key space
```

```bash
# 查询云盘剩余可用空间
python huawei_drive.py --command query --key available_space
```


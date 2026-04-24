# Huawei-Drive 命令快速参考

## 查询命令

### 查询空间详情

```bash
huawei_drive.py --command query --key space
```

> 该命令返回云盘总空间，已用空间已经剩余可用空间，单位为Byte

### 查询可用空间

```bash
huawei_drive.py --command query --key available_space
```

> 该命令返回int类型，表示云空间剩余可用空间，单位为Byte

### 查询文件是否存在

```bash
huawei_drive.py --command query --file_name <file_name>
```

> 若查询失败则返回失败原因，若查询成功则返回文件详细信息

### 查询文件夹`小艺Claw`是否存在

```bash
huawei_drive.py --command query_folder --file_name 小艺Claw
```

## 文件上传命令

### 文件覆盖上传

```bash
huawei_drive.py --command upload --mode overwrite --path <file_path>
```

> 该命令在`/root/小艺Claw`目录下上传文件，若文件已存在则覆盖原有文件

### 文件重命名上传

```bash
huawei_drive.py --command upload --mode rename --path <file_path>
```

> 该命令在`/root/小艺Claw`目录下上传文件，若文件已存在则重命名上传文件

## 文件夹命令

### 创建 小艺Claw 文件夹

```bash
huawei_drive.py --command create --folder_name 小艺Claw
```

> 该命令在云盘根路径下创建`小艺Claw`文件夹

## 查询文件列表

```bash
huawei_drive.py --command query --key file_list
```

该命令查询云盘`小艺Claw`文件夹下的所有文件列表
# 第一阶段：使用 Python 3.9 作为基础镜像
FROM python:3.9-alpine3.20 as builder

# 设置工作目录
WORKDIR /app

# 安装 binutils 和其他必要的构建工具 和 PyInstaller
RUN apk add --no-cache binutils build-base && pip install --no-cache-dir pyinstaller

# 复制 Python 依赖文件
COPY requirements.txt .

# 安装 Python 依赖和 
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目文件
COPY main.py utils.py ./

# 使用 PyInstaller 打包 Python 应用
RUN pyinstaller --onefile main.py

# 第二阶段：运行阶段
FROM alpine:3.20

# 设置工作目录
WORKDIR /app
# 安装时区数据
RUN apk add --no-cache tzdata
# 复制从第一阶段构建的可执行文件
COPY --from=builder /app/dist/main /app/
COPY sql /app/sql
# 设置容器的默认命令
CMD ["/app/main"]
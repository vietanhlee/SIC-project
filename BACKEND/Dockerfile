# Backend Dockerfile for FastAPI
FROM python


# Nhận biến ARG để xác định dùng GPU hay CPU
ARG DEVICE=cpu


# chỉ định thư mục làm việc để chạy lệnh
WORKDIR /app

# Install git
RUN apt-get update && apt-get install -y git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0
COPY requirements_cpu.txt ./
RUN pip install --no-cache-dir -r requirements_cpu.txt

# Copy backend code
COPY . .
# ❗ Lưu ý: EXPOSE chỉ mang tính mô tả, không thực sự publish cổng — cần
EXPOSE 8000

CMD ["uvicorn", "fast_api:app", "--host", "0.0.0.0", "--reload"]
# --host 0.0.0.0: Cho phép truy cập từ bên ngoài container.

# docker build -t myapp-gpu --build-arg DEVICE=gpu .

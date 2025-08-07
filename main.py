from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
import os
from pathlib import Path

app = FastAPI(title="文件下载服务", description="提供当前目录文件下载服务")

# 获取当前目录的绝对路径
CURRENT_DIR = Path.cwd()


@app.get("/")
async def root():
    """根路径，显示可用的文件列表"""
    files = []
    for file_path in CURRENT_DIR.iterdir():
        if file_path.is_file() and not file_path.name.startswith("."):
            files.append(
                {
                    "filename": file_path.name,
                    "size": file_path.stat().st_size,
                    "download_url": f"/download?filename={file_path.name}",
                }
            )

    return {
        "message": "文件下载服务",
        "current_directory": str(CURRENT_DIR),
        "available_files": files,
        "usage": "使用 /download?filename=文件名 来下载文件",
    }


@app.get("/download")
async def download_file(filename: str):
    """下载指定文件"""
    # 构建文件完整路径
    file_path = CURRENT_DIR / filename

    # 检查文件是否存在
    if not file_path.exists():
        raise HTTPException(status_code=404, detail=f"文件 '{filename}' 不存在")

    # 检查是否为文件（不是目录）
    if not file_path.is_file():
        raise HTTPException(status_code=400, detail=f"'{filename}' 不是一个文件")

    # 安全检查：确保文件在当前目录内（防止路径遍历攻击）
    try:
        file_path.resolve().relative_to(CURRENT_DIR.resolve())
    except ValueError:
        raise HTTPException(status_code=403, detail="访问被拒绝")

    # 返回文件响应
    return FileResponse(
        path=file_path, filename=filename, media_type="application/octet-stream"
    )


@app.get("/files")
async def list_files():
    """列出所有可下载的文件"""
    files = []
    for file_path in CURRENT_DIR.iterdir():
        if file_path.is_file() and not file_path.name.startswith("."):
            files.append(
                {
                    "filename": file_path.name,
                    "size": file_path.stat().st_size,
                    "download_url": f"/download?filename={file_path.name}",
                }
            )

    return {"files": files}


if __name__ == "__main__":
    import uvicorn

    print(f"服务将从目录启动: {CURRENT_DIR}")
    print("访问 http://localhost:8000 查看可用文件")
    print("使用 http://localhost:8000/download?filename=文件名 下载文件")
    uvicorn.run(app, host="0.0.0.0", port=8000)

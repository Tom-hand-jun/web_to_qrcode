# -*- coding: utf-8 -*-
"""
网址二维码转化器
Python + Tkinter + qrcode + Pillow
"""

import tkinter as tk
from tkinter import messagebox, filedialog
from urllib.parse import urlparse
import qrcode
from PIL import Image, ImageTk


# -------------------- 网址解析 --------------------
def normalize_url(raw: str):
    """
    解析并规范化用户输入的网址。
    返回规范化后的 URL 字符串；无法解析时返回 None。
    """
    if raw is None:
        return None

    text = raw.strip()
    if not text:
        return None

    # 不允许空白字符
    if any(ch.isspace() for ch in text):
        return None

    # 如果没有协议头，默认补 https://
    if "://" not in text:
        text = "https://" + text

    try:
        parsed = urlparse(text)
    except Exception:
        return None

    # 只接受 http/https
    if parsed.scheme not in ("http", "https"):
        return None

    # 必须有主机名
    if not parsed.netloc:
        return None

    host = parsed.hostname
    if not host:
        return None

    # 简单校验：域名至少有一个点，或者是 localhost / IP / IPv6
    if host != "localhost" and "." not in host:
        if ":" not in host:      # IPv6 里会包含冒号
            return None

    return text


# -------------------- 自定义函数：网址转图片 --------------------
def web_to_pic(url: str) -> Image.Image:
    """
    将网址转换成二维码图片。
    返回 PIL Image 对象。
    """
    qr = qrcode.QRCode(
        version=None,                 # 自动选择版本
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    # 转为标准 PIL Image，方便后续缩放和保存
    return img.convert("RGB")


# -------------------- 主窗口 --------------------
root = tk.Tk()
root.title("网址二维码转化器")
root.geometry("520x220")
root.resizable(False, False)

# 输入框提示
tk.Label(root, text="请输入网址：", font=("Microsoft YaHei UI", 11)).pack(pady=(20, 5))
entry = tk.Entry(root, width=60, font=("Microsoft YaHei UI", 11))
entry.pack(pady=5, padx=20)
entry.focus()

# 按钮区域
btn_frame = tk.Frame(root)
btn_frame.pack(pady=20)


def clear_input():
    """清空输入框"""
    entry.delete(0, tk.END)
    entry.focus()


def save_image(img: Image.Image, parent_window: tk.Toplevel):
    """保存二维码图片，支持多种格式"""
    file_path = filedialog.asksaveasfilename(
        parent=parent_window,
        title="保存二维码图片",
        defaultextension=".png",
        filetypes=[
            ("PNG 图片", "*.png"),
            ("JPEG 图片", "*.jpg;*.jpeg"),
            ("BMP 图片", "*.bmp"),
            ("GIF 图片", "*.gif"),
            ("所有文件", "*.*"),
        ],
    )
    if not file_path:
        return

    try:
        ext = file_path.lower().rsplit(".", 1)[-1] if "." in file_path else "png"
        save_img = img
        if ext in ("jpg", "jpeg"):
            save_img = img.convert("RGB")   # JPEG 不支持 RGBA
        save_img.save(file_path)
        messagebox.showinfo("保存成功", f"图片已保存到：\n{file_path}", parent=parent_window)
    except Exception as e:
        messagebox.showerror("保存失败", f"无法保存图片：\n{e}", parent=parent_window)


def show_qr_window(img: Image.Image, url: str):
    """弹出新窗口展示二维码，并带有保存按钮"""
    win = tk.Toplevel(root)
    win.title("二维码")
    win.resizable(True, True)

    # 获取屏幕尺寸，保证窗口能完整显示
    screen_w = win.winfo_screenwidth()
    screen_h = win.winfo_screenheight()
    max_w = int(screen_w * 0.8)
    max_h = int(screen_h * 0.8)

    # 如果图片太大，按比例缩小
    img_w, img_h = img.size
    if img_w > max_w or img_h > max_h:
        ratio = min(max_w / img_w, max_h / img_h)
        new_w = int(img_w * ratio)
        new_h = int(img_h * ratio)
        display_img = img.resize((new_w, new_h), Image.LANCZOS)
    else:
        display_img = img

    photo = ImageTk.PhotoImage(display_img)

    # 图片标签
    img_label = tk.Label(win, image=photo)
    img_label.image = photo          # 保持引用，防止被垃圾回收
    img_label.pack(padx=10, pady=10)

    # 网址说明
    tk.Label(win, text=url, font=("Microsoft YaHei UI", 9),
             fg="#666", wraplength=400).pack(pady=(0, 10))

    # 保存按钮
    save_btn = tk.Button(
        win,
        text="保存图片",
        font=("Microsoft YaHei UI", 11),
        command=lambda: save_image(img, win),
    )
    save_btn.pack(pady=(0, 15))

    # 设置窗口大小，使其恰好容纳图片和按钮
    win.update_idletasks()
    req_w = max(win.winfo_reqwidth(), 300)
    req_h = win.winfo_reqheight()
    win.geometry(f"{req_w}x{req_h}")
    win.minsize(300, 200)


def start_convert():
    """开始转换按钮逻辑"""
    raw = entry.get()

    # if 文本框无内容
    if not raw.strip():
        messagebox.showwarning("提示", "请输入网址")
        entry.focus()
        return

    # elif 文本框内容无法解析
    url = normalize_url(raw)
    if url is None:
        messagebox.showerror("错误", "无效的网址，请检查输入内容")
        entry.focus()
        return

    # else：调用自定义函数生成二维码
    try:
        img = web_to_pic(url)
    except Exception as e:
        messagebox.showerror("错误", f"生成二维码失败：\n{e}")
        return

    # 弹出新窗口展示
    show_qr_window(img, url)


# 按钮
clear_btn = tk.Button(btn_frame, text="清空输入框", width=12,
                      font=("Microsoft YaHei UI", 11), command=clear_input)
clear_btn.pack(side=tk.LEFT, padx=10)

convert_btn = tk.Button(btn_frame, text="开始转换", width=12,
                        font=("Microsoft YaHei UI", 11), command=start_convert)
convert_btn.pack(side=tk.LEFT, padx=10)

# 回车键触发转换
entry.bind("<Return>", lambda event: start_convert())

root.mainloop()
# -*- coding: utf-8 -*-
"""
修复 Whisper 自动转写报错：
"The generation config is outdated and is thus not compatible with the `task` argument to `generate`"

原因：whisper-large-v3-turbo 模型目录里的 generation_config.json 缺失或为旧格式，
Breeze TTS2 克隆模式调 whisper 转写时触发。

用法（在 ComfyUI 的 Python 环境里运行，即 ComfyUI 启动器使用的 python）：
    python fix_whisper_generation_config.py
    python fix_whisper_generation_config.py D:/path/to/whisper-large-v3-turbo

不传模型目录时脚本自动在 HuggingFace 默认缓存中查找 whisper 模型。
需要联网下载官方 generation_config（网络受限时使用本地代理 http://127.0.0.1:21882）。
"""
import os
import sys

PROXY = "http://127.0.0.1:21882"

def find_whisper_model_dirs():
    home = os.path.expanduser("~")
    cache = os.path.join(home, ".cache", "huggingface", "hub")
    out = []
    if not os.path.isdir(cache):
        return out
    for name in os.listdir(cache):
        if "whisper" in name.lower() or "openai" in name.lower():
            snap = os.path.join(cache, name, "snapshots")
            if os.path.isdir(snap):
                for s in sorted(os.listdir(snap)):
                    out.append(os.path.join(snap, s))
    return out

def main():
    model_dir = sys.argv[1] if len(sys.argv) > 1 else None
    if not model_dir:
        cands = find_whisper_model_dirs()
        if not cands:
            print("未找到 whisper 模型缓存目录，请把模型目录作为参数传入：")
            print("  python fix_whisper_generation_config.py <模型目录>")
            sys.exit(1)
        model_dir = cands[0]
        print("自动定位模型目录:", model_dir)
    else:
        print("使用指定模型目录:", model_dir)

    # 设置代理（如已配置 HF 代理可忽略）
    os.environ.setdefault("HTTP_PROXY", PROXY)
    os.environ.setdefault("HTTPS_PROXY", PROXY)
    os.environ.setdefault("http_proxy", PROXY)
    os.environ.setdefault("https_proxy", PROXY)

    from transformers import GenerationConfig

    print("正在从 HuggingFace 获取官方 generation config ...")
    cfg = GenerationConfig.from_pretrained("openai/whisper-large-v3-turbo")
    cfg.save_pretrained(model_dir)
    target = os.path.join(model_dir, "generation_config.json")
    print("修复完成，已写入:", target)

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import subprocess
import sys
import os
from pathlib import Path


def convert_with_ime(input_file, output_file, ahk_script="kanakanji.ahk"):
    """
    入力ファイルからひらがなを読み込み、AutoHotkeyスクリプトでIME変換し、
    結果を出力ファイルに保存する
    """
    
    # AutoHotkeyの実行ファイルパスを検索
    ahk_exe = find_autohotkey()
    if not ahk_exe:
        print("Error: AutoHotkey.exe が見つかりません", file=sys.stderr)
        sys.exit(1)
    
    # AHKスクリプトの存在確認
    if not os.path.exists(ahk_script):
        print(f"Error: {ahk_script} が見つかりません", file=sys.stderr)
        sys.exit(1)
    
    # 入力ファイルを読み込み
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            input_lines = [line.strip() for line in f if line.strip()]
    except Exception as e:
        print(f"Error reading input file: {e}", file=sys.stderr)
        sys.exit(1)
    
    # 出力ファイルを準備
    results = []
    
    # AutoHotkeyプロセスを起動
    print(f"Processing {len(input_lines)} lines...")
    
    try:
        process = subprocess.Popen(
            [ahk_exe, ahk_script],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding='utf-8'
        )
        
        # 各行を処理
        for i, line in enumerate(input_lines, 1):
            print(f"Converting line {i}/{len(input_lines)}: {line[:30]}...", end='\r')
            
            # AHKスクリプトに送信
            process.stdin.write(line + '\n')
            process.stdin.flush()
            
            # 結果を受信
            result = process.stdout.readline().strip()
            results.append(result)
        
        # プロセスを終了
        process.stdin.close()
        process.wait(timeout=5)
        
        print("\nConversion completed.")
        
    except subprocess.TimeoutExpired:
        process.kill()
        print("\nError: AutoHotkey process timeout", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"\nError during conversion: {e}", file=sys.stderr)
        sys.exit(1)
    
    # 結果を出力ファイルに保存
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            for result in results:
                f.write(result + '\n')
        print(f"Results saved to: {output_file}")
    except Exception as e:
        print(f"Error writing output file: {e}", file=sys.stderr)
        sys.exit(1)


def find_autohotkey():
    """
    AutoHotkey.exeのパスを検索する
    """
    common_paths = [
        r"C:\Program Files\AutoHotkey\AutoHotkey.exe",
        r"C:\Program Files (x86)\AutoHotkey\AutoHotkey.exe",
        os.path.expanduser(r"~\AppData\Local\Programs\AutoHotkey\AutoHotkey.exe"),
    ]
    
    for path in common_paths:
        if os.path.exists(path):
            return path
    
    # PATH環境変数から検索
    import shutil
    ahk_path = shutil.which("AutoHotkey.exe")
    return ahk_path


def main():
    parser = argparse.ArgumentParser(
        description='IMEを使用してひらがなを漢字に変換するツール'
    )
    parser.add_argument(
        'input_file',
        help='入力ファイル（ひらがな、1行1フレーズ）'
    )
    parser.add_argument(
        '-o', '--output',
        required=True,
        help='出力ファイル（変換結果）'
    )
    parser.add_argument(
        '--ahk-script',
        default='kanakanji.ahk',
        help='AutoHotkeyスクリプトのパス（デフォルト: kanakanji.ahk）'
    )
    
    args = parser.parse_args()
    
    convert_with_ime(args.input_file, args.output, args.ahk_script)


if __name__ == '__main__':
    main()

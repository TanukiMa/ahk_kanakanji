#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
kanakanji.py - IMEを使用してひらがなを漢字に変換するツール

使用方法:
    python kanakanji.py input.txt -o output.txt
    python kanakanji.py input.txt -o output.txt --sleep-convert 700  # 変換待ち時間を調整
"""

import argparse
import subprocess
import sys
import os
import shutil
from pathlib import Path


def find_autohotkey():
    """
    AutoHotkey.exeのパスを検索する
    
    Returns:
        str: AutoHotkey.exeのフルパス、見つからない場合はNone
    """
    # 一般的なインストールパスを検索
    common_paths = [
        r"C:\Program Files\AutoHotkey\AutoHotkey.exe",
        r"C:\Program Files\AutoHotkey\v1.1.37.02\AutoHotkey.exe",
        r"C:\Program Files\AutoHotkey\v1.1.36.02\AutoHotkey.exe",
        r"C:\Program Files (x86)\AutoHotkey\AutoHotkey.exe",
        os.path.expanduser(r"~\AppData\Local\Programs\AutoHotkey\AutoHotkey.exe"),
    ]
    
    for path in common_paths:
        if os.path.exists(path):
            return path
    
    # PATH環境変数から検索
    ahk_path = shutil.which("AutoHotkey.exe")
    if ahk_path:
        return ahk_path
    
    return None


def convert_with_ime(input_file, output_file, ahk_script="kanakanji.ahk", 
                     sleep_convert=None, verbose=False):
    """
    入力ファイルからひらがなを読み込み、AutoHotkeyスクリプトでIME変換し、
    結果を出力ファイルに保存する
    
    Args:
        input_file (str): 入力ファイルパス（ひらがな、1行1フレーズ）
        output_file (str): 出力ファイルパス
        ahk_script (str): AutoHotkeyスクリプトのパス
        sleep_convert (int): 変換処理後の待ち時間（ミリ秒）
        verbose (bool): 詳細情報を表示
    """
    
    # AutoHotkeyの実行ファイルパスを検索
    ahk_exe = find_autohotkey()
    if not ahk_exe:
        print("Error: AutoHotkey.exe が見つかりません", file=sys.stderr)
        print("https://www.autohotkey.com/ からダウンロードしてインストールしてください", file=sys.stderr)
        sys.exit(1)
    
    if verbose:
        print(f"Using AutoHotkey: {ahk_exe}")
    
    # AHKスクリプトの存在確認
    if not os.path.exists(ahk_script):
        print(f"Error: {ahk_script} が見つかりません", file=sys.stderr)
        sys.exit(1)
    
    # IME.ahkの存在確認
    ime_ahk_path = os.path.join(os.path.dirname(os.path.abspath(ahk_script)), "IME.ahk")
    if not os.path.exists(ime_ahk_path):
        print(f"Error: IME.ahk が見つかりません", file=sys.stderr)
        print(f"Expected location: {ime_ahk_path}", file=sys.stderr)
        sys.exit(1)
    
    # 入力ファイルを読み込み
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            input_lines = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"Error: 入力ファイル '{input_file}' が見つかりません", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error reading input file: {e}", file=sys.stderr)
        sys.exit(1)
    
    if not input_lines:
        print("Warning: 入力ファイルが空です", file=sys.stderr)
        sys.exit(1)
    
    print(f"Processing {len(input_lines)} lines...")
    if sleep_convert:
        print(f"Custom convert sleep time: {sleep_convert}ms")
    else:
        print(f"Using default convert sleep time: 500ms (Microsoft IME optimized)")
    print("(処理中はNotepadウィンドウが前面に表示されます)")
    print()
    
    results = []
    
    try:
        # AutoHotkeyプロセスを起動
        cmd = [ahk_exe, ahk_script]
        
        # カスタム待ち時間を指定
        if sleep_convert:
            cmd.append(str(sleep_convert))
        
        if verbose:
            print(f"Command: {' '.join(cmd)}")
        
        process = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding='utf-8'
        )
        
        # 各行を処理
        for i, line in enumerate(input_lines, 1):
            # 進捗表示
            print(f"[{i:3d}/{len(input_lines)}] Converting: {line[:40]:<40}", end='\r')
            
            # AHKスクリプトに送信
            process.stdin.write(line + '\n')
            process.stdin.flush()
            
            # 結果を受信
            result = process.stdout.readline().strip()
            
            # INFO行をスキップ
            while result.startswith("INFO:"):
                if verbose:
                    print(f"\n{result}")
                result = process.stdout.readline().strip()
            
            results.append(result)
            
            if verbose:
                print(f"\n  Input:  {line}")
                print(f"  Output: {result}")
        
        # プロセスを終了
        process.stdin.close()
        process.wait(timeout=10)
        
        print("\n")
        print("✓ Conversion completed.")
        
    except subprocess.TimeoutExpired:
        process.kill()
        print("\nError: AutoHotkey process timeout", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        process.kill()
        print("\n\nInterrupted by user", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"\nError during conversion: {e}", file=sys.stderr)
        if process:
            process.kill()
        sys.exit(1)
    
    # 結果を出力ファイルに保存
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            for result in results:
                f.write(result + '\n')
        print(f"✓ Results saved to: {output_file}")
    except Exception as e:
        print(f"Error writing output file: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description='IMEを使用してひらがなを漢字に変換するツール（Microsoft IME最適化版）',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  # デフォルト設定で実行（Microsoft IME最適化: 500ms）
  python kanakanji.py input.txt -o output.txt
  
  # 変換待ち時間を調整（重いIMEや長い文字列の場合）
  python kanakanji.py input.txt -o output.txt --sleep-convert 700
  
  # 詳細情報を表示
  python kanakanji.py input.txt -o output.txt --verbose
  
待ち時間調整の目安:
  - Microsoft IME（デフォルト）: 500ms
  - Microsoft IME（重い場合）: 700-1000ms
  - Google日本語入力: 300-400ms
  - Mozc4med: 300-500ms（辞書サイズによる）
  
注意:
  - 処理中はNotepadウィンドウが前面に表示されます
  - 現在アクティブなIMEを使用します
  - IME.ahkが同じディレクトリに必要です
        """
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
    parser.add_argument(
        '--sleep-convert',
        type=int,
        metavar='MILLISECONDS',
        help='変換処理後の待ち時間（ミリ秒）。デフォルト: 500（Microsoft IME最適化値）'
    )
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='詳細情報を表示'
    )
    
    args = parser.parse_args()
    
    convert_with_ime(
        args.input_file,
        args.output,
        args.ahk_script,
        args.sleep_convert,
        args.verbose
    )


if __name__ == '__main__':
    main()

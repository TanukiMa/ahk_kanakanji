# ime_comparison_test.py
import subprocess
import csv
import time
import os
import sys
from datetime import datetime

def find_autohotkey():
    """AutoHotkeyの実行ファイルを探す"""
    possible_paths = [
        r"C:\Program Files\AutoHotkey\AutoHotkey.exe",
        r"C:\Program Files\AutoHotkey\AutoHotkeyU64.exe",
        r"C:\Program Files\AutoHotkey\AutoHotkeyU32.exe",
        r"C:\Program Files (x86)\AutoHotkey\AutoHotkey.exe",
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            return path
    
    print("エラー: AutoHotkeyが見つかりません")
    print("https://www.autohotkey.com/ からダウンロードしてください")
    return None

def test_ime_conversion(ahk_path, hiragana, max_retries=2):
    """IME変換テストを実行"""
    for attempt in range(max_retries):
        try:
            process = subprocess.Popen(
                [ahk_path, 'ime_test_universal.ahk', hiragana],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            stdout, stderr = process.communicate(timeout=40)
            result = stdout.decode('utf-8', errors='ignore').strip()
            
            # エラーチェック
            if result.startswith('ERROR:'):
                print(f"    ⚠ {result}")
                if attempt < max_retries - 1:
                    print(f"    リトライ中... ({attempt + 1}/{max_retries})")
                    time.sleep(2)
                    continue
                return None
            
            return result
            
        except subprocess.TimeoutExpired:
            print(f"    ⚠ タイムアウト")
            process.kill()
            if attempt < max_retries - 1:
                print(f"    リトライ中... ({attempt + 1}/{max_retries})")
                time.sleep(2)
                continue
            return None
        except Exception as e:
            print(f"    ⚠ エラー: {e}")
            return None
    
    return None

def main():
    # AutoHotkeyのパス確認
    ahk_path = find_autohotkey()
    if not ahk_path:
        sys.exit(1)
    
    # スクリプトファイル確認
    if not os.path.exists('ime_test_universal.ahk'):
        print("エラー: ime_test_universal.ahk が見つかりません")
        sys.exit(1)
    
    print("=" * 70)
    print("IME比較テストプログラム")
    print("=" * 70)
    print(f"AutoHotkey: {ahk_path}")
    print(f"作業ディレクトリ: {os.getcwd()}")
    print()
    
    # テストデータ
    test_words = [
        'いがくようご',
        'けんさけっか',
        'しんだん',
        'ちりょう',
        'かんじゃ',
        'しょうじょう',
        'けんさ',
        'びょういん'
    ]
    
    # テスト対象IME
    imes = [
        'Microsoft IME',
        'Mozc',
        'Google日本語入力'
    ]
    
    # 全結果を格納
    all_results = []
    
    print("テスト対象:")
    for i, ime in enumerate(imes, 1):
        print(f"  {i}. {ime}")
    print(f"\nテスト単語数: {len(test_words)}")
    print(f"総テスト数: {len(imes)} × {len(test_words)} = {len(imes) * len(test_words)}")
    print()
    
    # 各IMEごとにテスト
    for ime_index, ime_name in enumerate(imes, 1):
        print("=" * 70)
        print(f"【{ime_index}/{len(imes)}】 {ime_name} のテスト")
        print("=" * 70)
        print()
        print(f"準備:")
        print(f"  1. タスクバーの言語アイコンから「{ime_name}」に切り替えてください")
        print(f"  2. IMEが「{ime_name}」になっていることを確認してください")
        print(f"  3. 他のアプリケーションをすべて閉じてください")
        print()
        print("⚠ 注意: テスト中はキーボード・マウスを操作しないでください")
        print()
        
        input(f"準備ができたらEnterキーを押してください...")
        
        print(f"\n5秒後にテスト開始します...")
        for i in range(5, 0, -1):
            print(f"  {i}...", end='', flush=True)
            time.sleep(1)
        print(" 開始！\n")
        
        # 各単語をテスト
        ime_results = []
        for word_index, word in enumerate(test_words, 1):
            print(f"  [{word_index}/{len(test_words)}] 入力: {word}", end=' ', flush=True)
            
            result = test_ime_conversion(ahk_path, word)
            
            if result:
                converted = result != word
                status = "✓" if converted else "×"
                print(f"→ {result} {status}")
                
                all_results.append({
                    'ime': ime_name,
                    'input': word,
                    'output': result,
                    'converted': '成功' if converted else '失敗'
                })
                ime_results.append(converted)
            else:
                print(f"→ (取得失敗) ×")
                all_results.append({
                    'ime': ime_name,
                    'input': word,
                    'output': '(エラー)',
                    'converted': 'エラー'
                })
                ime_results.append(False)
            
            time.sleep(1.5)
        
        # IMEごとのサマリー
        success_count = sum(ime_results)
        success_rate = (success_count / len(test_words)) * 100
        print()
        print(f"  {ime_name} 結果: {success_count}/{len(test_words)} 成功 ({success_rate:.1f}%)")
        print()
        
        # 次のIMEに移る前に少し待機
        if ime_index < len(imes):
            time.sleep(2)
    
    # 結果をCSVに保存
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    csv_filename = f'ime_comparison_{timestamp}.csv'
    
    with open(csv_filename, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['ime', 'input', 'output', 'converted'])
        writer.writeheader()
        writer.writerows(all_results)
    
    # 最終サマリー
    print("=" * 70)
    print("テスト完了！")
    print("=" * 70)
    print()
    print("結果サマリー:")
    
    for ime_name in imes:
        ime_data = [r for r in all_results if r['ime'] == ime_name]
        success = sum(1 for r in ime_data if r['converted'] == '成功')
        total = len(ime_data)
        rate = (success / total * 100) if total > 0 else 0
        print(f"  {ime_name:25s}: {success:2d}/{total:2d} ({rate:5.1f}%)")
    
    print()
    print(f"詳細結果: {csv_filename}")
    print()
    
    # Rで統計解析を実行するか確認
    if os.path.exists('analyze_ime_results.R'):
        print("統計解析を実行しますか？")
        response = input("R統計解析を実行する場合は 'y' を入力: ")
        if response.lower() == 'y':
            print("\nR統計解析を実行中...")
            try:
                subprocess.run(['Rscript', 'analyze_ime_results.R', csv_filename])
            except Exception as e:
                print(f"R実行エラー: {e}")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n中断されました")
        sys.exit(0)

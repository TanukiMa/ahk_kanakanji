; kanakanji.ahk - IME自動変換スクリプト (同一ウィンドウ使い回し)
#NoEnv
#SingleInstance Force
SetBatchLines, -1
SendMode Input

; IME.ahkをインクルード
#Include IME.ahk

; Notepadを起動して準備
PrepareNotepad()

; 標準入力から1行ずつ読み取って処理
Loop
{
    input := ReadStdIn()
    if (input = "")
        break
    
    ; 変換処理
    result := ConvertWithIME(input)
    
    ; 標準出力に書き出し
    FileAppend, %result%`n, *, UTF-8
}

ExitApp

; Notepadを準備する関数
PrepareNotepad()
{
    global notepadHwnd
    
    ; 既存のNotepadを探す
    IfWinExist, ahk_exe notepad.exe
    {
        WinGet, notepadHwnd, ID, ahk_exe notepad.exe
    }
    Else
    {
        ; 新規起動
        Run, notepad.exe
        WinWait, ahk_exe notepad.exe, , 5
        if ErrorLevel
        {
            FileAppend, ERROR: Failed to launch Notepad`n, *, UTF-8
            ExitApp
        }
        WinGet, notepadHwnd, ID, ahk_exe notepad.exe
    }
    
    ; ウィンドウをアクティブ化
    WinActivate, ahk_id %notepadHwnd%
    WinWaitActive, ahk_id %notepadHwnd%, , 3
    
    ; 内容をクリア
    Send, ^a
    Send, {Delete}
    Sleep, 50
}

; IMEで変換する関数
ConvertWithIME(text)
{
    global notepadHwnd
    
    ; ウィンドウがまだ存在するか確認
    IfWinNotExist, ahk_id %notepadHwnd%
    {
        PrepareNotepad()
    }
    
    ; アクティブ化
    WinActivate, ahk_id %notepadHwnd%
    WinWaitActive, ahk_id %notepadHwnd%, , 2
    
    ; 内容をクリア
    Send, ^a
    Sleep, 30
    Send, {Delete}
    Sleep, 30
    
    ; IMEをオンにする
    IME_SET(1, "ahk_id " . notepadHwnd)
    Sleep, 100
    
    ; ひらがなを入力
    SendInput, %text%
    Sleep, 150
    
    ; スペースキーで変換（最初の候補を選択）
    Send, {Space}
    Sleep, 150
    
    ; Enterで確定
    Send, {Enter}
    Sleep, 100
    
    ; 結果を取得（全選択してクリップボードにコピー）
    Clipboard := ""  ; クリップボードをクリア
    Send, ^a
    Sleep, 50
    Send, ^c
    Sleep, 100
    
    ; クリップボードの内容を取得（タイムアウト付き）
    timeout := 0
    Loop, 20
    {
        if (Clipboard != "")
            break
        Sleep, 50
        timeout++
    }
    
    result := Clipboard
    
    ; IMEをオフにする（次の入力のために）
    IME_SET(0, "ahk_id " . notepadHwnd)
    
    return result
}

; 標準入力から読み取る関数
ReadStdIn()
{
    static hStdIn := DllCall("GetStdHandle", "int", -10, "ptr")
    VarSetCapacity(buf, 8192)
    
    if !DllCall("ReadFile", "ptr", hStdIn, "ptr", &buf, "uint", 8192, "uint*", bytesRead, "ptr", 0)
        return ""
    
    if (bytesRead = 0)
        return ""
    
    result := StrGet(&buf, bytesRead, "UTF-8")
    ; 改行を除去
    result := RegExReplace(result, "\r?\n$", "")
    return result
}
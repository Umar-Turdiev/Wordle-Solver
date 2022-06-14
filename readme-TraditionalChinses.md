# Wordle 解題小幫手

很難解Wordle？或者你想要一種更簡單的方法來縮小可能的答案？

你來對地方了，這是給你的。

這個Wordle解題小幫手是用Python編寫的，它使用etropy提供你可以快速縮小答案範圍的單字。

## 如何使用它 ？

1. 這段程式是用Python 3.8編寫的，所以任何相同或更高版本都可以工作。

1. 下載[最新版本](https://github.com/Umar-Turdiev/Wordle-Solver/releases/tag/1.0.0)。

1. 把檔案解壓縮。

1. 安裝依賴的第三方程式庫：

    ```sh
    pip3 安裝 wordfreq matplotlib
    ```

1. 在`assist`模式下運行小幫手：

    ```sh
    python3 ./main.py assist
    ```

## 有用的參數選項

* 沒有參數：將像傳統的Wordle遊戲一樣運行。

* `assist`：會給你單詞進入你的 Wordle 遊戲，並等待你提供回合的結果。圓形結果的格式：🟩 綠格子=2，🟨 黃格子=1，⬛️ 黑格子=0。例如你輸入'tares'，結果是⬛️🟩🟨⬛️⬛️，你將輸入`02100`。

* `sim`：為指定的開場詞模擬遊戲。

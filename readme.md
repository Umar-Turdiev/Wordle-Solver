# Wordle Solver

Having a hard time solving Wordle ? Or you want an easier way to narrow down the possible answers ?

Well this is for you.

This Wordle solver were written in Python, it uses entropy to provide you words that can quickly narrow down the answers.

## How to use it ?

1. This code was written in Python 3.8, so anything equal or higher should work.

1. Clone this repository:

    ```sh
    git clone https://github.com/Umar-Turdiev/Wordle-Solver.git
    ```

1. Install dependencies:

    ```sh
    pip3 install wordfreq matplotlib
    ```

1. Run the solver in `assist` mode:

    ```sh
    python3 ./main.py assist
    ```

## Useful argument options

* no argument: Will run like a traditional Wordle game.

* `assist`: Will give you the word to enter to your Wordle game, and waut for you to feed the result of the round. Format for the round result: 🟩 green block = 2, 🟨 yellow block = 1, ⬛️ black block = 0. For example you entered 'tares', and the result is ⬛️🟩🟨⬛️⬛️, you'll enter `02100`.

* `sim`: Simulate games for designated opening words.

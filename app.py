# These should be all the imports you need:
from flask import Flask, render_template, request, redirect, url_for
import random

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.debug = True

with open('words.txt', encoding='utf-8') as file:
    words = file.read().strip().split("\n")


def get_word(last_word_w_hint):
    word = ''
    for x in last_word_w_hint:
        word += x[0]
    return word


def guess_to_hint(guess, secret):
    """Given a `guess` and a `secret` word as strings, it returns a list with one tuple for
    each letter in the guess, where the first item is the letter, and the second item is one
    of the strings `correct`, `wrong` or `misplaced`, describing what applies for that letter.
    """
    result = []
    for idx, letter in enumerate(guess):
        actual = secret[idx]
        if actual == letter:
            result.append((letter, 'correct'))
        elif letter in secret:
            result.append((letter, 'misplaced'))
        else:
            result.append((letter, 'wrong'))
    return result


secret_word = random.choice(words)
words_guessed = []
history_of_words = []


@app.route("/reset_game", methods=['GET'])
def game_finished():
    global secret_word, words_guessed  # noqa: PLW0603

    secret_word = random.choice(words)
    words_guessed = []
    
    return redirect(url_for('index_get'))


@app.route("/", methods=['GET'])
def index_get():
    """When the user visit the root of the website with a GET request and starts/resume the game,
    or when the user POSTs a new guess."""
    last_guessed_word = None

    print(secret_word)
    if words_guessed:
        guessed_word_w_hint = words_guessed[-1]
        last_guessed_word = get_word(guessed_word_w_hint)
        
    return render_template("game.html",
                           words_guessed=words_guessed,
                           secret_word=secret_word,
                           guessed_word=(last_guessed_word))# type: ignore


@app.route("/", methods=['POST'])
def index_post():

    guessed_word = request.form.get("guess")
    
    if guessed_word not in words:
        result = True
    else:
        result = False
        word_and_hints = guess_to_hint(guessed_word, secret_word)
        words_guessed.append(word_and_hints)

    if guessed_word == secret_word:
        tries = str(len(words_guessed))
        history_of_words.append((secret_word, tries + ' guesses!'))
    elif (len(words_guessed) == 15 and guessed_word in words and guessed_word != secret_word):
        history_of_words.append((secret_word, 'failed'))

    return render_template("game.html",
                           words_guessed=words_guessed,
                           guessed_wrong=result,
                           secret_word=secret_word,
                           guessed_word=guessed_word)


@app.route("/history", methods=['GET'])
def show_history():
    """Show history of the attempts the user made."""
    return render_template("history.html", history_of_words=history_of_words)


if __name__ == '__main__':
    app.run()

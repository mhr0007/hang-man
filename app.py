import socketio as socketio
from flask import Flask, render_template
from random_word import RandomWords
import random
import math
from flask_socketio import SocketIO, emit

app = Flask(__name__)
socketio = SocketIO(app)

words = RandomWords()

# Game State
random_word = ""
current_display = ""
score = 0
high_score = 0
lives = 5


def game_init():
    global random_word, current_display, lives
    
    lives = 5  

    random_word = words.get_random_word().lower()
    print(f"New random word: {random_word}")
    
    word_len = len(random_word)
    hint_len = math.floor(word_len / 2)
    char_list = list(random_word)

    temp_word = ["_"] * word_len
    hint_indices = random.sample(range(word_len), hint_len)
    for index in hint_indices:
        temp_word[index] = char_list[index]
    
    current_display = "".join(temp_word)
    print(f"Initial hint: {current_display}")
    
    return random_word, current_display, lives, score



@app.route("/")
def home():
    random_word, current_display, lives, score = game_init()
    return render_template("index.html", correct_word=random_word, 
                           current_display=current_display, 
                           score=score, lives=lives, high_score=high_score)


@socketio.on("key")
def handle_key(data):
    global random_word, current_display, score, high_score, lives
    
    key = data.get("key", "").lower()
    print(f"Key received: {key}")
    
    # Update the word display
    updated_display = list(current_display)
    correct_guess = False
    
    for i, char in enumerate(random_word):
        if char == key and current_display[i] == "_":
            updated_display[i] = key
            correct_guess = True
    
    # Update lives and score
    if correct_guess:
        if "_" not in updated_display:
            # Full word guessed correctly
            score += 1
            game_over = True
            won = True
            if(high_score <= score): high_score = score
        else:
            game_over = False
            won = False
    else:
        lives -= 1
        game_over = lives <= 0
        won = False
    
    # Update the current display
    current_display = "".join(updated_display)
    print(f"Updated display: {current_display}, Lives: {lives}, Score: {score}")
    
    # Send the updated display, score, and lives back to the client
    emit("key_response", {
        "word": current_display,
        "score": score,
        "high_score": high_score,
        "lives": lives,
        "game_over": game_over,
        "won": won,
        "correct_word": random_word  # Always send the current word for accurate display
    })


@socketio.on("reset_game")
def reset_game(data=None):
    global score
    print("Resetting game...")

    # Only reset score if explicitly told (i.e., it's "Play Again")
    if data and data.get("play_again_type") == "reset":
        score = 0

    new_word, new_display, new_lives, _ = game_init()
    emit("new_game", {
        "word": new_display,
        "score": score,
        "high_score": high_score,
        "lives": new_lives,
        "correct_word": new_word
    })



if __name__ == "__main__":
    socketio.run(app, debug=True)

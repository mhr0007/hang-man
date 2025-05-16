reset_image = () => {
    return "../static/images/hang-man-5.png";
};

$(window).on("load", function(){
    $(".preloader").hide();
    $(".man img").attr("src", reset_image());
    $(".play_again").hide();
    $(".score").hide();
    $(".win").hide();
    $(".loose").hide();
});

$(".btn").on("click", function(){
    $(".btn").hide();
    $(".score").show();
    $(".attempt").show();
    $(".attempt span").html(5);
    $(".score span").html(0);
    $(".high_score").show();
    $(".word").show();
    $(".man img").attr("src", reset_image());

    
    const socket = io();

    // Handle keypress events
    $(document).keydown(function (e) { 
        if (e.key.length === 1 && /[a-zA-Z]/.test(e.key)) {
            socket.emit("key", { key: e.key });
            console.log("Key sent:", e.key);
        }
    });

    // Handle server response
    socket.on("key_response", function(data) {
    console.log("Updated word:", data.word);
    $(".var_word").text(data.word);
    $(".score span").text(data.score);
    $(".attempt span").text(data.lives);
    
    // Always update high score
    $(".high_score span").text(data.high_score);
    
    // Update hangman image
    $(".man img").attr("src", `../static/images/hang-man-${data.lives}.png`);

    if (data.game_over) {
        $(document).off("keydown");

        if (data.won) {
            $(".play_again").text("Next Word ➔");
            $(".win h3").html(`<span>Correct: </span>${data.correct_word}`);
            $(".win").show();
        } else {
            $(".play_again").text("Play Again ↺");
            $(".loose h3").html(`<span>Game Over ! </span>The word was: ${data.correct_word}`);
            $(".loose").show();
        }

        $(".play_again").show();
    }
});


    // Reset the game on "Play Again" button click
    $(".play_again").on("click", function(){
    const playAgainType = $(this).text().includes("Next Word") ? "next_word" : "reset";
    socket.emit("reset_game", { play_again_type: playAgainType });

    $(".win").hide();
    $(".loose").hide();
    $(".play_again").hide();
    $(".btn").hide();
    $(".score").show();
    $(".attempt").show();
    $(".word").show();
    $(".man img").attr("src", reset_image());

    if (playAgainType === "reset") {
        $(".score span").html(0);
    }
});


    // Handle new game state from server
    socket.on("new_game", function(data) {
        console.log(data.correct_word);
        $(".var_word").text(data.word);
        $(".score span").text(data.score);
        $(".attempt span").text(data.lives);
        $(".man img").attr("src", reset_image());
    });
});

"""
Color Vision Check - a Drafter website that screens for red-green,
blue-yellow, and total color blindness using dotted test images.

HOW TO USE THIS FILE
- Parts marked "DONE FOR YOU" are the harder parts. Read the comments so
  you understand them (you'll explain your site in your video!).
- Parts marked "TODO" are yours, like a homework problem. Work top to
  bottom: the dataclasses MUST be done first or nothing else will run.
- The images were made by make_plates.py (already run; see that file).
"""
from drafter import *
from dataclasses import dataclass

# ---------------------------------------------------------------------------
# Global constants (allowed by the rules because they never change)
# ---------------------------------------------------------------------------
TEST_TYPES = ["red-green", "blue-yellow", "total"]
PASSING_PERCENT = 80   # below this, we recommend an eye doctor

# TODO 1: Fill in your site information. Each argument is a string,
# except `links`, which is a list of strings (put your video link there).
set_website_title("Beyond Red & Green")
set_site_information(
    author="Elinor Handel <ehandel@udel.edu>",
    description="This is color vision testing site that looks for red-green, "
                "blue-yellow, and total color blindness and suggests "
                "whether to see an eye doctor.",
    sources=["https://www.nei.nih.gov/learn-about-eye-health/"
             "eye-conditions-and-diseases/color-blindness",
             "Machado, Oliveira & Fernandes (2009), A Physiologically-based "
             "Model for Simulation of Color Vision Deficiency"],
    planning=["Repository.pdf"],
    links=["https://github.com/YOUR-USERNAME/YOUR-REPO",
           "YOUR VIDEO LINK"]
)
hide_debug_information()
set_website_framed(False)

# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------
# TODO 2: Write the Plate dataclass. Use EXACTLY these field names and
# types, in this order, because ALL_PLATES below depends on them:
#     image_file (str)      - path to the dotted image
#     correct_answer (str)  - the number hidden in the image
#     test_type (str)       - "red-green", "blue-yellow", or "total"
#     user_answer (str)     - what the user typed ("" until answered)
@dataclass
class Plate:
    image_file: str # path to the dotted image
    correct_answer: str # the number hidden in the image
    test_type: str # "red-green", "blue-yellow", or "total"
    user_answer: str # what the user typed ("" until answered)


# TODO 3: Write the State dataclass with these six fields, in this order:
#     user_name (str), test_type (str), plates (list[Plate]),
#     current_index (int), score (int), show_feedback (bool)
@dataclass
class State:
    user_name: str
    test_type: str
    plates: list[Plate]
    current_index: int
    score: int
    show_feedback: bool


# ---------------------------------------------------------------------------
# DONE FOR YOU: every plate image the site can show.
# These match the images make_plates.py created. In each test, plate 1 is
# a "control" plate that everyone should be able to read; the others are
# designed so the number disappears for that type of color blindness.
# ---------------------------------------------------------------------------
ALL_PLATES = [
    Plate(image_file="images/red_green_1.png", correct_answer="12",
          test_type="red-green", user_answer=""),
    Plate(image_file="images/red_green_2.png", correct_answer="8",
          test_type="red-green", user_answer=""),
    Plate(image_file="images/red_green_3.png", correct_answer="29",
          test_type="red-green", user_answer=""),
    Plate(image_file="images/red_green_4.png", correct_answer="74",
          test_type="red-green", user_answer=""),
    Plate(image_file="images/red_green_5.png", correct_answer="6",
          test_type="red-green", user_answer=""),
    Plate(image_file="images/blue_yellow_1.png", correct_answer="15",
          test_type="blue-yellow", user_answer=""),
    Plate(image_file="images/blue_yellow_2.png", correct_answer="3",
          test_type="blue-yellow", user_answer=""),
    Plate(image_file="images/blue_yellow_3.png", correct_answer="42",
          test_type="blue-yellow", user_answer=""),
    Plate(image_file="images/blue_yellow_4.png", correct_answer="9",
          test_type="blue-yellow", user_answer=""),
    Plate(image_file="images/blue_yellow_5.png", correct_answer="57",
          test_type="blue-yellow", user_answer=""),
    Plate(image_file="images/total_1.png", correct_answer="23",
          test_type="total", user_answer=""),
    Plate(image_file="images/total_2.png", correct_answer="4",
          test_type="total", user_answer=""),
    Plate(image_file="images/total_3.png", correct_answer="86",
          test_type="total", user_answer=""),
    Plate(image_file="images/total_4.png", correct_answer="7",
          test_type="total", user_answer=""),
    Plate(image_file="images/total_5.png", correct_answer="35",
          test_type="total", user_answer=""),
]


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------
def make_fresh_plate(plate: Plate) -> Plate:
    """Return a new copy of a plate with a blank user answer.

    DONE FOR YOU - why this matters: if start_test put the plates from
    ALL_PLATES straight into state.plates, both lists would hold the SAME
    objects. Then saving a user_answer would also change ALL_PLATES (our
    "constant"!), and a retake would show the old answers. Making a new
    Plate keeps the original list untouched.
    """
    return Plate(plate.image_file, plate.correct_answer, plate.test_type, "")


def percent_correct(score: int, total: int) -> float:
    """Return the score as a percentage of the total (0 if total is 0)."""
    # TODO 4: If total is 0, return 0.0 (you can't divide by zero!).
    # Otherwise return score divided by total, times 100.
    if total == 0:
        return 0.0
    else:
        return (score/total)*100



def current_plate(state: State) -> Plate:
    """Return the plate the user is currently looking at. (DONE FOR YOU)"""
    return state.plates[state.current_index]


def feedback_page(state: State, plate: Plate) -> Page:
    """Build the Feedback page for the plate that was just answered."""
    # TODO 5: Use an if statement:
    #   - if plate.user_answer equals plate.correct_answer, the message is
    #     "Correct!"
    #   - otherwise the message is "Not quite. The answer was " plus the
    #     correct answer.
    # Return a Page with a Header, the message, and
    # Button("Next", next_question).
    if plate.user_answer==plate.correct_answer:
        message = "Correct!"
    else:
        message = "Not quite. The answer was " + plate.correct_answer
    return Page(state, [
        Header("Feedback"),
        message,
        Button("Next", next_question),
    ])


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
@route
def index(state: State) -> Page:
    """Show the home page with the name, test type, and feedback inputs."""
    # TODO 6: Return a Page with:
    #   - a Header with your site's name and a short welcome sentence
    #   - "Your name:" and TextBox("name", state.user_name)
    #   - "Choose a test:" and SelectBox("chosen_test", TEST_TYPES)
    #   - CheckBox("wants_feedback", True) and the text
    #     "Show me if each answer was right"
    #   - Button("Start Test", start_test)
    #   - Button("Instructions", instructions)
    #   - Button("Learn More", learn_more)
    # The names "name", "chosen_test", "wants_feedback" MUST match the
    # parameter names of start_test exactly.
    return Page(state, [
        Header("Beyond Red & Green"),
        Paragraph("Welcome to an improved way to check your color vision!"),
        Paragraph("This website tests more than just red-green color"
                  " blindness! We test blue-yellow and total as well."),
        Paragraph("Please enter your name:",
        TextBox("name", state.user_name)),
        Paragraph("Please choose a test:",
        SelectBox("chosen_test", TEST_TYPES)),
        Paragraph(CheckBox("wants_feedback", True),
        "Show me if my answer is correct"),
        Button("Start the Test", start_test),
        Button("Instructions", instructions),
        Button("Learn More", learn_more),
    ])


@route
def instructions(state: State) -> Page:
    """Show tips for setting up the screen before taking a test."""
    # TODO 7: Return a Page with a Header and a BulletedList of tips:
    # turn off night mode / blue light filters, turn brightness up,
    # sit about an arm's length from the screen, and don't zoom in.
    # Add Button("Back", index).
    return Page(state, [
        Header("Tips and Tricks"),
        BulletedList([
            "turn off night mode and or blue light filters",
            "turn brightness up",
            "sit about an arm's length from the screen",
            "do not zoom in",
        ]),
        Button("Back", index)
    ])


@route
def start_test(state: State, name: str, chosen_test: str,
               wants_feedback: bool) -> Page:
    """Save the user's choices, load matching plates, and show question 1."""
    # TODO 8: Save name, chosen_test, and wants_feedback into the matching
    # state fields. Set score and current_index to 0, and set
    # state.plates to an empty list.
    state.user_name = name
    state.test_type = chosen_test
    state.show_feedback = wants_feedback
    state.score = 0
    state.current_index = 0
    state.plates = []
    # TODO 9 (your loop for filtering): loop over ALL_PLATES. If a plate's
    # test_type equals chosen_test, append make_fresh_plate(plate) to
    # state.plates.
    for plate in ALL_PLATES:
        if plate.test_type == chosen_test:
            state.plates.append(make_fresh_plate(plate))
    # DONE FOR YOU: routes can return another route's page.
    return show_question(state)


@route
def show_question(state: State) -> Page:
    """Show the current plate image, the question count, and an answer box."""
    plate = current_plate(state)
    # TODO 10: Make a string like "Question 2 / 5". Hint: current_index
    # starts at 0, so add 1. len(state.plates) is the total. Use str().
    question_num = str(state.current_index + 1)
    question_total = str(len(state.plates))
    question_count = "Question " + question_num + " / " + question_total
    return Page(state, [
        Header("What number do you see?"),
        question_count,
        # DONE FOR YOU: shows the image file at 300 x 300 pixels.
        Image(plate.image_file, 300, 300),
        "Type the number (leave it blank if you can't see one):",
        TextBox("answer"),
        Button("Submit", submit_answer),
    ])


@route
def submit_answer(state: State, answer: str) -> Page:
    """Record and check the user's answer, then show feedback or move on."""
    plate = current_plate(state)
    # .strip() removes accidental spaces, so " 12 " counts as "12".
    plate.user_answer = answer.strip()
    # TODO 11: If plate.user_answer equals plate.correct_answer, add 1 to
    # state.score.
    if plate.user_answer == plate.correct_answer:
        state.score += 1
    # TODO 12: If state.show_feedback is True, return
    # feedback_page(state, plate). Otherwise return next_question(state).
    if state.show_feedback:
        return feedback_page(state, plate)
    else:
        return next_question(state)


@route
def next_question(state: State) -> Page:
    """Move to the next plate, or to the results after the last plate."""
    # TODO 13: Add 1 to state.current_index. Then, if the current_index is
    # greater than or equal to len(state.plates), return results(state).
    # Otherwise return show_question(state).
    state.current_index += 1
    if state.current_index >= len(state.plates):
        return results(state)
    else:
        return show_question(state)


@route
def results(state: State) -> Page:
    """Show the score, an eye doctor recommendation, and an answer review."""
    percent = percent_correct(state.score, len(state.plates))

    # TODO 14: If percent is less than PASSING_PERCENT, set recommendation
    # to a message suggesting they see an eye doctor about possible
    # <state.test_type> color blindness. Otherwise, set it to a message
    # saying their results look typical.
    if percent < PASSING_PERCENT:
        recommendation = ("Contact your eye doctor about possible " + 
        state.test_type + " color blindness.")
    else:
        recommendation = ("Your " + state.test_type + " results look typical. "
        "If you still notice trouble with colors, talk to an eye doctor.")
    # TODO 15 (your required loop over the State list): start with
    # rows = []. Loop over state.plates, and for each plate append a list
    # with 3 items: the plate number (a counter starting at 1),
    # plate.correct_answer, and plate.user_answer.
    # Tip: if user_answer is "", show "(blank)" instead.
    rows = []
    plate_number = 1
    for plate in state.plates:
        answer_shown = plate.user_answer
        if answer_shown == "":
            answer_shown = "[blank]"
        rows.append([plate_number, plate.correct_answer, answer_shown])
        plate_number += 1
    name_shown = state.user_name
    if name_shown == "":
        name_shown = "Hey there"
    score_message = (name_shown + ", you got " + str(state.score) + " out of "
                     + str(len(state.plates)) + " correct (" + str(percent) + "%).")
    return Page(state, [
        Header("Your Results"),
        score_message,
        recommendation,
        # DONE FOR YOU: turns your rows into a table with column titles.
        Table(rows, header=["Plate", "Correct answer", "Your answer"]),
        "This is a screening tool, not a medical diagnosis. Only an eye "
        "doctor can diagnose color blindness.",
        Button("Retake", retake),
        Button("Learn More", learn_more),
    ])


@route
def retake(state: State) -> Page:
    """Reset the test progress and return to the home page."""
    # TODO 16: Set user_name to "", plates to [], current_index to 0, and
    # score to 0. Then return index(state).
    state.user_name = ""
    state.plates = []
    state.current_index = 0
    state.score = 0
    return index(state)


@route
def learn_more(state: State) -> Page:
    """Explain the types of color blindness and link to eye-care resources."""
    # TODO 17: Return a Page that explains, in your own words:
    #   - red-green (protanopia / deuteranopia, the most common)
    #   - blue-yellow (tritanopia, rare)
    #   - total color blindness (achromatopsia, very rare)
    # Add at least one Link, e.g.
    #   Link("National Eye Institute",
    #        "https://www.nei.nih.gov/learn-about-eye-health/"
    #        "eye-conditions-and-diseases/color-blindness")
    # and Button("Home", index).
    return Page(state, [
        Header("Let's Learn More About Color Blindness"),
        "Many color blind people can still see many colors; they just"
        " mix up specific colors. Most cases of color blindness are"
        " actually inherited, but it can also develop from eye diseases,"
        " injuries, or from taking certain medications.",
        Header("Red-Green Color Blindness", 2),
        "This is the most common type. Protanopia is when the"
        " red sensing cones in the eye do not work. This makes"
        " red colors look brown and darker. Deuteranopia is when"
        " the green sensing cones do not work. It can be hard to"
        " tell the difference between red/green, brown/green,"
        " orange/yellow, and purple/blue with this type.",
        Header("Blue-Yellow Color Blindness", 2),
        "This form, where blue sensing cones do not work, is called"
        " tritanopia. This type is very rare; roughly 1 in 10,000"
        " people have it. It makes it hard to tell apart blue/green"
        " and yellow/pink or violet.",
        Header("Total Color Blindness", 2),
        "This type of color blindness, achromatopsia, causes"
        " people to see almost only shades of gray. This type"
        " is even more rare than tritanopia with only 1 in"
        " 30,000 people having it. The people affected can be"
        " sensitive to bright light, because their eyes rely on"
        " rod cells, which work best in dimmer light.",
        Header("Where to Get Help", 2),
        "You can go to an optometrist or ophthalmologist"
        " to do a full color vision exam. This is worth"
        " looking into as these eye conditions can cause"
        " trouble at school, work, or even just driving.",
        Link("National Eye Institute: Color Blindness",
             "https://www.nei.nih.gov/learn-about-eye-health/"
             "eye-conditions-and-diseases/color-blindness"),
        Button("Home", index),
    ])


# ---------------------------------------------------------------------------
# Unit tests (every route needs at least one)
# ---------------------------------------------------------------------------
def blank_state() -> State:
    """Return a State with nothing filled in yet, for testing."""
    return State("", "", [], 0, 0, False)


# DONE FOR YOU - example tests. A route returns a Page, and page.state is
# the State after the route ran, so you can check that fields changed.
test_page = start_test(blank_state(), "Elinor", "blue-yellow", True)
assert_equal(test_page.state.user_name, "Elinor")
assert_equal(len(test_page.state.plates), 5)
assert_equal(test_page.state.plates[0].correct_answer, "15")

test_page = submit_answer(test_page.state, " 15 ")
assert_equal(test_page.state.score, 1)

# TODO 18: Write at least one test for every other route, plus
# percent_correct. Ideas:
#   - percent_correct(3, 4) should be 75.0, and percent_correct(0, 0) 0.0
assert_equal(percent_correct(3, 4), 75.0)
assert_equal(percent_correct(0, 0), 0.0)
assert_equal(percent_correct(4, 4), 100.0)
# DONE FOR YOU: starts the website with an empty State.
start_server(blank_state())


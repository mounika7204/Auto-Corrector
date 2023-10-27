from flask import Flask, request, render_template,redirect
import language_tool_python
from autocorrect import Speller
from nltk.tokenize import word_tokenize


app = Flask(__name__)
speller = Speller()
language_tool = language_tool_python.LanguageTool('en-US')


@app.route('/', methods=['GET', 'POST'])
def front_page():
    if request.method == 'POST':
        return redirect('/home')
    return render_template('index.html')


@app.route('/home', methods=['GET', 'POST'])
def home():
    score = None
    original_text = ""
    corrected_text = ""
    spelling_mistakes = []
    grammar_mistakes = []

    if request.method == 'POST':
        original_text = request.form['original_text']
        corrected_text, spelling_mistakes, grammar_mistakes = correct_text(original_text,speller,language_tool)
        score = calculate_score(original_text, corrected_text)

    return render_template('home.html', original_text=original_text, corrected_text=corrected_text,
                           score=score, spelling_mistakes=spelling_mistakes, grammar_mistakes=grammar_mistakes)

def correct_text(text, speller, language_tool):
    words = word_tokenize(text)
    corrected_words = []
    spelling_mistakes = []
    grammar_mistakes = []

    for word in words:
        corrected_word = speller(word) 
        if corrected_word != word:
            spelling_mistakes.append((word, corrected_word))
        corrected_words.append(corrected_word)

    corrected_text = ' '.join(corrected_words)
    corrected_text = language_tool.correct(corrected_text)
    grammar_mistakes = language_tool.check(text)
    for i in grammar_mistakes:
        if i == "Possible spelling mistake found.":
            grammar_mistakes.remove(i)
    return corrected_text, spelling_mistakes, grammar_mistakes


def calculate_score(original_text, corrected_text):
    words = word_tokenize(original_text)
    corrected_words = word_tokenize(corrected_text)
    correct_words = sum(1 for w, c in zip(words, corrected_words) if w == c)
    total_words = len(words)
    score = (correct_words / total_words) * 100
    return score

if __name__ == '__main__':
    app.run(debug=True)
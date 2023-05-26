import openai, re, random, os, time, csv

from config import OPENAI_API_KEY

csv_file = 'CompTIA-APlus-220-1101.csv'
openai.api_key = OPENAI_API_KEY
current_row_number = None

def attempt(openai_API_call):
    try:
        # Make your OpenAI API request here
        return openai_API_call
    except openai.error.RateLimitError as e:
        # Retry the request if RateLimitError occurs
        retry_after = e.response.headers.get('Retry-After')
        if retry_after:
            retry_after = int(retry_after)
            print(f"Rate limited. Retrying after {retry_after} seconds.")
            time.sleep(retry_after)
            return attempt(openai_API_call)  # Pass the openai_API_call argument
        else:
            # Retry immediately if Retry-After header is not present
            print("Rate limited. Retrying immediately.")
            return attempt(openai_API_call)  # Pass the openai_API_call argument


def clear_screen(text=None):
    # Check if the platform is Windows
    if os.name == 'nt':
        os.system('cls')
    else:
        # For Unix-based systems (Linux, macOS, etc.)
        os.system('clear')
    
    if text is None:
        text = "TestBudy (v1) by James Paul Knox"

    columns, _ = os.get_terminal_size()
    header_line = '=' * columns
    program_info = text.center(columns)

    print(header_line)
    print(program_info)
    print(header_line)
    print()

def regexQuiz(completion_string):
    # Given the completion, parse the string into a dictionary

    # Remove all newlines from the string
    completion_string = completion_string.replace('\n', '')

    # Use regular expressions to extract the question and choices
    matches = re.findall(r'Q:\s*(.+?)(?=[ABCD]:|$)', completion_string)
    question = matches[0].strip()

    choices = re.findall(r'[ABCD]:\s*(.+?)(?=[ABCD]:|$)', completion_string)
    choices = [choice.strip() for choice in choices]

    # Randomize the order of choices
    random.shuffle(choices)

    # Create the dictionary with the question and choices
    result = {
        'question': question,
        'choices': choices
    }

    # Return the result
    return result


def createQuiz(learning_objective):
    # Given a learning objective, generate a question and choices in one go
    clear_screen("Please wait while the AI creates a question...")
    print("""
        TestBudy is an GPT powered CompTIA A+ exam study tool
        Copyright (C) 2023  James Paul Knox

        

        This program is free software: you can redistribute it and/or modify
        it under the terms of the GNU General Public License as published by
        the Free Software Foundation, either version 3 of the License, or
        (at your option) any later version.
        
        This program is distributed in the hope that it will be useful,
        but WITHOUT ANY WARRANTY; without even the implied warranty of
        MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
        GNU General Public License for more details.
        
        You should have received a copy of the GNU General Public License
        along with this program.  If not, see <https://www.gnu.org/licenses/>.\n\n
        """)
    prompt = f"""
    Q: What is the capital city of France?\n
    A: Paris\n
    B: London\n
    C: Rome\n
    D: Berlin\n\n\n\n

    Please generate a multiple-choice question with four choices about {learning_objective}\n\n

    Q: [QUESTION]\n
    A: [CORRECT_CHOICE_A]\n
    B: [INCORRECT_CHOICE_B]\n
    C: [INCORRECT_CHOICE_C]\n
    D: [INCORRECT_CHOICE_D]
    """
    completion_string = str(attempt(openai.Completion.create(engine='text-davinci-003', prompt=prompt, max_tokens=250, temperature=1))['choices'][0]['text'])
    return regexQuiz(completion_string)

def promptQuestion(question_dict):
    # Given the output from regexQuiz (dict w/ 1 "question" and list of 4 "choices")
    # Display to the user and get their answer
    clear_screen("Answer This Question")
    output = "QUESTION:\n"
    output += question_dict["question"] + "\n\n"
    output += "CHOICES:\n"
    for index, choice in enumerate(question_dict["choices"], start=1):
        output += f"{index}. {choice}\n"

    print(output)
    
    user_choice = int(input("Enter your answer (1,2,3,4, or type your own): "))
    if user_choice in range(1, len(question_dict["choices"]) + 1):
        selected_choice = question_dict["choices"][user_choice - 1]
    else:
        selected_choice = str(user_choice)
    print("You selected:", selected_choice)

    gradeAnswer(output, selected_choice)

def gradeAnswer(question_and_choices, student_answer):
    messages = [
            {"role": "system", "content": "You are a helpful tutor."},
            {"role": "assistant", "content": question_and_choices},
            {"role": "user", "content": student_answer},
            {"role": "system", "content": "Respond only with \"TRUE\" if the user is correct. Respond only with \"FALSE\" if the user is incorrect."}
            ]

    true_count = 0
    false_count = 0
    threshold = 3

    while true_count < threshold and false_count < threshold:
        chat_response = str(attempt(openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=messages))['choices'][0]['message']['content'])
        
        if 'true' in chat_response.lower():
            true_count += 1
        elif 'false' in chat_response.lower():
            false_count += 1
        else:
            print("Unexpected output. Trying again...")

    # Determine the final result based on the count
    if true_count == threshold:
        user_correct = "correct"
        print(f"GRADE: Correct! ({true_count}:{false_count})")
        recordCorrectness(True)
    else:
        user_correct = "not correct"
        print(f"GRADE: Not Correct. ({true_count}:{false_count})")
        recordCorrectness(False)
    
    ask_question_prompt = str(input("Ask the chatbot a question. Send a blank message at any time for the next question: "))
    if ask_question_prompt is "":
        print("Next Question")
        pass
    else:
        messages = [
            {"role": "system", "content": "You are a helpful and friendly tutor, quizzing the user and answering their questions."},
            {"role": "assistant", "content": question_and_choices},
            {"role": "user", "content": f"I think the answer is: {student_answer}"},
            {"role": "assistant", "content": f"I think your answer is {user_correct}. Do you have any questions you'd like to ask? I'm happy to help you learn!"},
            {"role": "user", "content": ask_question_prompt},
            ]
        chatSession(messages)

def chatSession(messages):
    clear_screen("OpenAI GPT 3.5 Turbo API Chatbot")
    for message in messages:
        print(f"{str(message['role'].upper())}:  {message['content']}")
        print()
    
    print("[PLEASE NOTE: Send a blank message at any time to exit chat session and go to next question]")
    while True:
        assistant_reply = attempt(openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=messages))['choices'][0]['message']['content']
        print()
        print(f"ASSISTANT:  {assistant_reply}")
        print()
        messages.append({"role": "assistant", "content": assistant_reply})
        print()
        user_reply = str(input("USER:  "))
        if user_reply == "":
            break
        else:
            messages.append({"role": "user", "content": user_reply})
        



def chooseLearningObjective():
    global current_row_number

    # Read the CSV file and calculate scores for each learning objective
    with open(csv_file, 'r') as file:
        reader = csv.reader(file)
        headers = next(reader)  # Skip the header row
        learning_objectives = []
        scores = []

        for row_number, row in enumerate(reader, start=1):
            learning_objective = row[0]
            correct_answers = int(row[1])
            incorrect_answers = int(row[2])

            # Calculate the score based on the number of correct and incorrect answers
            score = (incorrect_answers + 1) / (correct_answers + 1)
            learning_objectives.append(learning_objective)
            scores.append(score)

        # Choose a learning objective based on the scores
        chosen_learning_objective = random.choices(learning_objectives, weights=scores)[0]

        # Find the row number of the chosen learning objective
        current_row_number = learning_objectives.index(chosen_learning_objective) + 1

        return chosen_learning_objective

def recordCorrectness(is_correct):
    if current_row_number is None:
        raise ValueError("No learning objective has been read yet.")

    # Update the CSV file based on the provided is_correct value
    with open(csv_file, 'r+') as file:
        reader = csv.reader(file)
        rows = list(reader)

        # Increment the appropriate column based on the is_correct value
        if is_correct:
            rows[current_row_number][1] = str(int(rows[current_row_number][1]) + 1)
        else:
            rows[current_row_number][2] = str(int(rows[current_row_number][2]) + 1)

        # Write the updated rows back to the CSV file
        file.seek(0)
        writer = csv.writer(file)
        writer.writerows(rows)

clear_screen()
while True:
    promptQuestion(createQuiz(chooseLearningObjective()))

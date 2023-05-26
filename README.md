# TestBudy
TestBudy is a study tool powered by GPT-3 that helps you prepare for exams by generating multiple-choice questions based on learning objectives. It provides interactive feedback and guidance through a chat-based interface.

## Usage
Clone the repository:

  ```git clone https://github.com/your-username/TestBudy.git```


Install the required dependencies:

  ```pip install openai```
  
Create or update the CSV file that contains the learning objectives for your exam. The CSV file should have the following format:
```
  Learning Objective,Correct Answers,Incorrect Answers
  Objective 1,0,0
  Objective 2,0,0
  ...
```
  
You can provide your own CSV file or modify the existing one to adapt the tool to your specific exam.

Obtain an OpenAI API key and update the OPENAI_API_KEY variable in the config.py file.

## Run the program:

```python testbudy.py```

The program will display a multiple-choice question based on a randomly chosen learning objective from the CSV file. You can select an answer by entering the corresponding number (1, 2, 3, or 4) or by typing your own answer. The program will use the OpenAI GPT-3 model to grade your answer and provide feedback. The grading system considers any of the correct choices as a correct answer. You can also provide custom answers like "1 and 4" or "all of the above". The program will continue asking questions in a loop until you exit by pressing Ctrl+C.

The program will automatically update the CSV file based on the correctness of your answers. The scores for each learning objective will be incremented accordingly.

## License
TestBudy is licensed under the GNU General Public License v3.0. You can find a copy of the license in the LICENSE file.

*Please note that TestBudy is provided as-is without any warranty. Use it at your own risk.*

## Author
TestBudy is developed by James Paul Knox.

## Contributing
Contributions to TestBudy are welcome! If you find any issues or have suggestions for improvements, please open an issue or submit a pull request on the GitHub repository.

## Acknowledgments
TestBudy utilizes OpenAI's Davincii-003 language model for generating questions and GPT 3.5 Turbo for providing interactive feedback.

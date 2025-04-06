# Funky Coder

**Funky Coder** is a Python-based AI assistant that generates Python functions—with documentation and test cases—with a twist! It brings a laid-back, So-Cal vibes mode to your coding sessions, complete with creative and witty messages. Whether you're in the mood for a chill, slang-filled experience or a more traditional command interface, Funky Coder has got you covered.

## Features

- **Dynamic Function Generation:** Interact with Funky Coder to create Python functions tailored to your instructions.
- **Dual Mode Experience:**
  - **Normal Mode:** Standard interface with clear, traditional commands.
  - **Slang Mode:** Switch to a groovy, So-Cal slang mode for a fun, relaxed vibe.
- **Thematic Help Output:** Displays randomized greetings, taglines, and descriptions that change each time you need a refresher.
- **Built-In Commands:**
  - **>help / >vibes:** Show detailed help with available commands.
  - **>exit / >quit / >peaceout:** Quit the conversation.
  - **>save / >stash:** Save the conversation to a file.
  - **>code / >ripcord:** Extract the last block of code from the conversation.
  - **>clear / >wipeout:** Clear the screen.
  - **>history / >flashback:** Review conversation history.
  - **>slang / >socal and >normal / >normie:** Toggle between Funky Slang Mode and Normal Mode.

## Getting Started

1. **Installation:**
   - Ensure you have Python 3.7 or newer installed.
   - Clone the repository:
     ```bash
     git clone https://github.com/YOUR_USERNAME/funky-coder.git
     ```
   - Change into the repository directory:
     ```bash
     cd funky-coder
     ```
   - (Optional) Create and activate a virtual environment:
     ```bash
     python3 -m venv venv
     source venv/bin/activate  # on macOS/Linux
     venv\Scripts\activate  # on Windows
     ```
     or better yet, install `pyve` in your user (~) directory and let that handle the virtual environment for you (see https://github.com/pointmatic/pyve):
     ```bash
     ~/pyve.sh --init
     ```
   - Install required dependencies if available (e.g., via pyproject.toml).

2. **Configuration:**
   - Create a `.env` file and set your OpenAI API key:
     ```
     OPENAI_API_KEY=your-api-key-here
     ```

3. **Running Funky Coder:**
   - Execute the program with:
     ```bash
     python funky_coder.py
     ```
   - Follow the on-screen instructions and use commands prefixed with `>` to interact.

## Usage Examples

- To view help:
  ```
  >help
  ```
- To switch to Funky Slang Mode:
  ```
  >slang
  ```
- To extract a code block and save to a file:
  ```
  >code my_function.py
  ```
- To exit Funky Coder:
  ```
  >exit
  ```

## Contributing

Contributions are welcome! Fork the repository, make changes, and submit pull requests.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

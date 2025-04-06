#!/usr/bin/env python3

# This file creates a simple agent that generates a Python function with documentation using LiteLLM completion.
# In the initial prompt, the agent only generates the function to fulfill the user's request.
# In subsequent prompts the user can request documentation (function description, parameter descriptions, return value description, example usage, and edge cases). 
# The user can also request test cases for the function (basic functionality, edge cases, error cases, performance, security, concurrency, various input scenarios)
# 
# Requirements:
# - LiteLLM completion
# - Python 3.x
# - OpenAI API key
# - Maintain conversation context
# - Use a simple agent class to handle the conversation
# - Print each step of the conversation
# - Save the final version to a Python file
# - Simple text-based interface

import os
import re
import dotenv
from litellm import completion
from typing import List, Dict, Any
from dotenv import load_dotenv
import json
import random

EXPECTED_API_KEY_NAME = "OPENAI_API_KEY"

data = {
    'system_message': {
        'normal': """You are a helpful assistant that generates Python functions with documentation and test cases.
When asked to write a function, first write the function code with minimal comments.
When asked for documentation or tests, improve the existing function accordingly.""",
        'slang': """You are a funky coder that generates Python functions with documentation and test cases.
When asked to write a function, first write the function code with minimal comments.
When asked for documentation or tests, improve the existing function accordingly. Communicate in a funky, creative way, leaning on Southern Californian slang and memes.""",
    },
    'commands': {
        'help': {
            'description': "Show this message",
            'slang': 'vibes',
            'slang_description': "Need a refresher? Pulls up this chill guide. 🧘‍♂️",
        },
        'exit': {
            'description': "Quit the conversation",
            'slang': 'peaceout',
            'slang_description': "Dip outta the convo like a skater ghostin\' a bad sesh. 🛹'",
        },
        'save': {
            'description': "Save conversation",
            'slang': 'stash',
            'slang_description': "Save your convo, like stashing snacks in your van. 🍪'",
        },
        'code': {
            'description': "Extract and save the last block code",
            'slang': 'ripcord',
            'slang_description': "Snag the latest code block and save it like a digital mixtape. 💾'",
        },
        'history': {
            'description': "Show conversation history",
            'slang': 'flashback',
            'slang_description': "Relive all the deep talks we had. Total memory lane moment. 🧠",
        },
        'clear': {
            'description': "Wipe the screen",
            'slang': 'wipeout',
            'slang_description': "Clear the screen like a fresh wipeout at Huntington Pier. 🌊",
        },
        'reset': {
            'description': "Reset the conversation",
            'slang': 'newwave',
            'slang_description': "Reset the conversation and start cruisin' fresh. 🏄‍♀️",
        },
        'slang': {
            'description': "Show commands in Southern California slang",
            'slang': 'socal',
            'slang_description': "This is totes normal, dude. No need to be all gangsta.",
        },
        'normal': {
            'description': "Show commands in normal American English",
            'slang': 'normie',
            'slang_description': "If you wanna be all old school, we can do that.",
        },
    },
    'welcomes': [
        "Welcome to the Funky Coder!",
        "🌴 Welcome to Funky Coder, Brah! 🌴",
        "🎯 You're in the zone, Brah! 🎯",
        "🌊 Yo dawg, you just paddled into Funky Coder! 🌊",
        "🕶️ Welcome aboard the Codewave Express, dude! 🕶️",
        "🐢 Cowabunga, coder! You've entered Funky Mode. 🐢",
        "🎧 Step into Funky Coder—where the keyboard's always hot and the vibes are hotter. 🎧",
        "🛹 What's crackin', script slinger? Welcome to Funky Coder HQ. 🛹",
        "🏄‍♂️ Funky Coder's in the house, and you just walked in barefoot. 🏄‍♂️",
        "🍍 Aloha, byte surfer—welcome to the code-side of paradise! 🍍",
        "🦩 Yo yo yo! Funky Coder just popped a wheelie for your arrival. 🦩",
        "💿 Welcome to Funky Coder, where even the bugs wear sunglasses. 💿",
        "🧃 Funky Coder's in session--crack open a LaCroix and let's get cookin'. 🧃",
        "🌊 Yo, coder! The surf's up and the scripts are flowing. 🌊",
        "🐚 Welcome to the dojo of dank code, my dude. 🐚",
        "🏄‍♀️ Whoa! You just stepped into the function zone. 🏄‍♀️",
        "🧘‍♂️ Chill, breathe, and ride the Python wave. 🧘‍♂️",
        "🚴 Welcome to the codeboard, shredder! 🚴",
        "🦈 Jaws ain't the only thing out here crunching—Funky Coder is in session. 🦈",
        "🐢 Easy there, ninja—Funky Coder's got your back. 🐢",
        "🌅 The tide brought you here for a reason. Let's code. 🌅",
        "🛹 Kick-push into creativity. Welcome aboard! 🛹",
        "💽 Sup code surfer, welcome to the byte-side. 💽",
        "🌴 The code breeze is warm, the vibes immaculate. 🌴",
        "🐬 Splash into something beautiful—Funky Coder awaits. 🐬",
        "🍹 Vibe check: passed. Welcome to the coding lounge. 🍹",
        "🎧 Drop in and drop code—this is your jam space. 🎧",
        "🌈 Funky Coder just got funkier with you in it. 🌈",
        "🕶️ Code in shades, dreams in color—welcome.",
        "💾 Load in, zone out, and ride the logic wave. 💾",
        "🧃 Sip the script juice and settle in. 🧃",
        "🔮 Funky Coder has summoned you. The prophecy begins. 🔮",
        "🔊 Plug in. Turn up. Type away. 🔊",
        "✨ Welcome to the Matrix, but make it Malibu. ✨",
        "🍔 Grab a burger, drop a function. 🍔",
        "🧜‍♂️ Half-dev, half-mermaid? You belong here.",
        "📟 Paging you to code heaven. Come on in. 📟",
        "🌀 Welcome to the flow state, legend. 🌀",
        "🔥 It's lit. You're here. Let's create. 🔥",
        "📀 You just unlocked Dev Mode: Funkadelic Edition. 📀",
        "🍀 Good vibes only. Code flows freely. 🍀",
        "🎮 Controller's in your hand now—start the game. 🎮",
        "🧋 Funky Coder on deck, and the code's delicious. 🧋",
        "🐠 Swim into the function reef, it's lush in here. 🐠",
        "🚀 Welcome to orbit, Captain Coder. 🚀",
        "🎢 Strap in. This is a full-stack thrill ride. 🎢",
        "💫 You've landed where magic meets logic. 💫",
        "💌 You've got mail. It says: 'Let's vibe and code.' 💌",
        "🧤 Gloves off. Code on. 🧤",
        "🦑 Welcome to the deep end of the dev pool. 🦑",
        "🕺 Dance your fingers across the keyboard, friend. 🕺",
        "🐉 You're in the den of the funky dragon. 🐉",
        "💡 Lightbulb's on. Let's light up the code night. 💡",
        "🐾 Trailblazer spotted. Enter the dev jungle. 🐾",
        "🍦 Chill code ahead. Brain freeze optional. 🍦",
        "🍕 Welcome, pie-thon master. 🍕",
        "🛸 UFO sighting confirmed—you're out of this world. 🛸",
        "💥 Pow! You just landed in the code dojo. 💥",
        "🎲 Roll the dev dice, champ. 🎲",
        "🏖️ Devcation starts now. Relax and write code.",
        "🧢 No cap, this is the dopest code zone. 🧢",
        "🦄 Whoa, a mythical dev has appeared! 🦄",
        "🍕 Welcome, pie-thon master. 🍕",
        "🛸 UFO sighting confirmed—you're out of this world. 🛸",
        "💥 Pow! You just landed in the code dojo. 💥",
        "🏖️ Devcation starts now. Relax and write code.",
        "🧢 No cap, this is the dopest code zone. 🧢",
        "🦄 Whoa, a mythical dev has appeared! 🦄",
        "👾 Game on. Funky Coder has entered the chat. 👾",
    ],
    'taglines': [
        "The world's first Python AI functionista with a So-Cal vibes mode.",
        "Where Python flows smoother than a Venice Beach sunset. 😎",
        "Spitting Python smoother than a skate trick at Venice Bowl. 🛹",
        "Code that vibes harder than a beach bonfire playlist. 🔥",
        "Where each function is toastier than a Santa Monica tan. ☀️",
        "It's like if Tony Hawk did tech support. 🦅",
        "Python so chill, it might start its own yoga class. 🧘‍♂️",
        "Like a smoothie made of code and stardust. 🌀",
        "Where 'syntax error' means you're just not stoked enough. 🌈",
        "Like debugging in flip-flops—relaxed but deadly. 🩴💀",
        "We sling scripts with more flavor than a taco truck. 🌮",
        "Where your Python gets spiritual and surfs the astral stack. 🧘‍♀️🌊",
        "Where you can code without a net, and the only rule is: no rules. 🌊",
        "Where your logic surfs and your bugs bail.",
        "Code so fresh it wears sunscreen.",
        "Smooth as a longboard glide on glassy water.",
        "Not just Python—Pyth-fun.",
        "Like a TED Talk with flip-flops.",
        "Code with flow, not with fear.",
        "Cranking out functions like a frozen yogurt machine.",
        "Where the compiler wears board shorts.",
        "Debugging never felt so Zen.",
        "Chill code for hot minds.",
        "Like building sandcastles, but with logic.",
        "Stack traces? More like beach traces.",
        "Python that smells like ocean breeze and caffeine.",
        "It's not spaghetti code—it's linguine with soul.",
        "Dev with vibes. Push with pride.",
        "Where bugs meet their mellow demise.",
        "Code that skips like a stone across a lake.",
        "More chill than a hammock on Catalina.",
        "Keyboard surfers welcome.",
        "Where your logic earns sunglasses.",
        "It's not just syntax—it's an artform, bro.",
        "No bugs, just hugs.",
        "Code that flows like kombucha in Silver Lake.",
        "It's like VS Code took a yoga retreat.",
        "Functions with flavor.",
        "Python with punchlines.",
        "Where if-statements ride tubes.",
        "Relax. Funky Coder's got the aux cord.",
        "It's not recursion, it's reincarnation.",
        "You write. I vibe. We ship.",
        "Code so smooth it should DJ.",
        "Where loops do ollies.",
        "Where Git commits feel like mixtapes.",
        "Float like a function, sting like a throw.",
        "IDE: Immaculate Developer Energy.",
        "Python served with lime and a twist.",
        "No cubicles, just creative current.",
        "A little chaotic, a lotta cool.",
        "Compiler-approved chill.",
        "Your imagination, our execution.",
        "Ride the code wave or get swept.",
        "Debugging in board shorts since forever.",
        "IDE-powered, vibe-tested.",
        "Like pair programming with a dolphin.",
        "Escape the ordinary. Enter the loop.",
        "Turn thoughts into scripts and vibes into versions.",
        "Breakpoints? More like breakbeats.",
        "Syntax and serotonin.",
        "Step into the smoothstack.",
        "It's not work if it feels like surfing.",
    ],
    'descriptions': [
        """This coding assistant generates Python functions. 
Continue to give instructions until you are satisfied with the final code.
Plus, you can ask the agent to generate documentation and test cases.""",
        """This gnarly code wizard whips up Python functions like a burrito stand slaps together carne asada.
Just keep throwin' Funky Coder your ideas till you're vibin' with the final product.
Need docs or tests? Say less—we gotchu.""",
        """This code conjurer crafts Python magic while catching waves in the background. 
Just toss your idea into the void and watch the function rise like a sea breeze. 
Docs and tests? Totally doable, my dude.""",
        """Funky Coder's got the sauce: just toss out your logic and we'll funkify it into a Python jam. 
Want docs and test cases too? We're already on it.""",
        """Feed Funky Coder your dreams, and it'll spit out Python like a DJ drops beats at a warehouse rave. 
Docs? Tests? Like, duh.""",
        """Say what you want built, and this digital homie will code it faster than you can say...
'pass the avocado toast.' Extra features? All day.""",
        """Tell Funky Coder your wildest function fantasy. 
We'll turn it into pure script nectar. 
Documentation and testing? Already manifested, fam.""",
        """Python generator. Vibe curator. Taco enthusiast. 
Funky Coder lives to serve your logic. Wanna test it or write docs? 
Yup, we got skills.""",
        """Chuck your ideas into the Funk Pit and let this coder wizard remix them into dope Python code. 
Extras like docs & tests? You betcha.""",
        """No stress, just press: 
Funky Coder will take your thoughts and render 'em into Python gold, like a neural-net barista. 
Docs + tests = yes.""",
        """Hit me with your best function. 
I'll crank the knobs, twist the loops, and drop some righteous Python. 
Docs and tests? Totally tubular.""",
        """You dream it, Funky Coder codes it...
then decks it out with sweet docs and clean test cases like frosting on a code cake.""",
        """Funky Coder turns your brainwaves into bytewaves. 
Drop an idea, get back a Python function, and keep riffing 'til it's just right. 
Docs and test cases? Totally on deck.""",
        """Got a function in mind? 
We'll sauce it up, remix it till it's perfect...
and drop some docs and tests on top like guac—no extra charge.""",
        """Type it. Funk it. Ship it. 
Funky Coder keeps going until your code slaps. 
Docs and tests? Already in the blender.""",
        """You pitch the function, we make it fabulous—then tweak it till you're vibin'. 
Want docs and test cases too? We're already on it.""",
        """Just tell Funky what's on your mind.
We'll crank the code out, update it as you go, and drop those docs and test files like pros.""",
        """Python's our language. Vibes are our dialect. 
You bring the ideas, we bring the functions, docs, and endless fine-tuning.""",
        """Ideas in, magic out. 
You can keep tweaking 'til the groove feels right. 
Docs and tests? You got it, captain.""",
        """This ain't just a script generator--it's a code-side cabana. 
Drop your instructions, refine the results, and snag docs and tests too.""",
        """Like your very own genie, but it speaks Python and vibes hard. 
Keep the wishes coming—we'll deliver code, tests, and docs on repeat.""",
        """You talk, we code. 
You nod, we doc. 
You vibe, we test. 
And if it ain't there yet, we keep rolling.""",
        """Think of a function. Now make it cooler. 
That's what we do--build it, improve it, test it, and doc it 'til it's beach-ready.""",
        """Pour your brain into the prompt and we'll pour back a script smoothie. 
Need tweaks? Keep 'em coming. Docs? Done.""",
        """Bringing the beach to your bash shell--one Python function at a time. 
Keep the flow going till you're stoked, with docs and test vibes included.""",
        """You dream it, we Python it...
then test it, doc it, and keep polishing until it's art.""",
        """Instructions go in. Glorious, tested, doc'd code comes out. 
Keep that feedback flowing, we're not done 'til it's fire.""",
        """Say it out loud. Funky Coder translates it to Python...
then tweaks it on the fly, and serves up full docs and test cases.""",
        """A chill zone where code flows and tests follow. 
Keep sending instructions and we'll ride the function wave with you.""",
        """Wanna vibe and build? Toss your thoughts over here. 
We'll keep riffing 'til it's just right--with docs and tests, naturally.""",
        """Tell us what you want, and we'll drop a code bomb with flavor...
plus polish it with tests and docstrings till it's pristine.""",
        """Talk to Funky, get logic. 
Need revisions? Just say so. Docs and tests? We live for 'em.""",
        """You muse, we manifest. Keep the ideas coming.
We'll refine, doc, and test until it's legendary.""",
        """Think of us like a Python-powered food truck for your dev brain. 
We take your orders, remix them 'til they slap, and serve docs/tests on the side.""",
        """We're like ChatGPT's funky cousin with a coding hobby. 
Keep chatting--we'll write, revise, document, and test like champs.""",
        """Code wizardry with a splash of Baja blast. 
We'll keep brewing until your function hits--and back it up with docs and tests.""",
        """Code with no stress, tests with no mess. 
Just keep the instructions coming and we'll groove our way to greatness.""",
        """This bot eats instructions and poops beautiful code...
complete with documentation and test cases, and it never stops till you're happy.""",
        """One prompt and you're off to the function races. 
Keep steering and we'll keep tuning, testing, and documenting your way to gold.""",
        """Python prose so clean you could wax it. 
Just keep the prompts coming--we'll iterate and deliver test-ready beauty.""",
        """Toss in some logic--get a whole party back. 
We'll funk the code, revise it on demand, and dress it up with docs and tests.""",
        """Ask us anything. Seriously. Anything. 
Code happens. Revisions happen. Docs and tests happen too.""",
        """Don't code alone. 
Funky Coder is your rubber duck with swagger. 
Say your piece, watch it turn into tested, doc'd, legit code.""",
        """Forget the rules.
Build wild, test strong, doc smooth. 
Keep the prompts flowing till you feel the magic.""",
        """When your brain's in the zone, we catch the code. 
We'll keep building until you're vibing--and toss in docs and tests just because.""",
        """Our functions slap harder than a wave at The Wedge. 
We'll keep iterating till they slap perfect--with docs and tests to boot.""",
        """Got a problem? We'll solve it with Python and pizzazz. 
Keep the instructions rolling, and we'll doc and test every version.""",
        """Dev with less grind and more groove. 
Keep feeding ideas, and we'll build it out--fully documented and tested.""",
        """Push the limits. Pull the vibes. 
We'll generate functions, refine them, and slap tests and docs on top like whipped cream.""",
        """From idea to implementation without the burnout...
with docs and tests to keep your flow tight. We'll revise till it shines.""",
        """Just tell us what you want, no filter. 
We'll translate, refactor, and wrap it up in testable, documented code.""",
        """It's a full-stack of chill with every function. 
Keep customizing, and we'll test and doc it till it's chef's kiss.""",
        """Serving up logic on a hot platter with test sauce. 
Drop a prompt, guide the groove, and we'll keep it cooking.""",
        """You drop the beats, we build the bars—in Python. 
You remix the track, we doc and test the whole set.""",
        """Insert thoughts. Get funk. Repeat. 
We'll ride with you till it's done, complete with docs and test files.""",
        """Docs and tests? Yeah, they're on the house. 
So are infinite iterations and hot-off-the-grill Python functions.""",
        """Say hello to your new mellow dev BFF. 
We'll code, revise, test, and doc until your vision's on point.""",
        """The chillest way to build the dopest stuff. 
Keep chatting, we'll keep coding--with full test coverage and docs, of course.""",
        """Like co-writing code with a golden retriever and a monk. 
We'll fetch your ideas, refactor with wisdom, and toss in tests/docs with every fetch.""",
        """Syntax meets sunsets in every session. 
Feed the vibe and we'll keep going—fully documented, tested, and finessed.""",
        """Instructions in. Test-covered code out. Like magic. 
Need more? Just say the word.""",
        """Making Python code groovy again--one prompt at a time. 
And we won't stop till the code's fire and the docs sing.""",
    ]
}

class FunkyCoder:
    def __init__(self, api_key: str, system_message: str, model: str = "openai/gpt-4o", max_tokens: int = 1500, temperature: float = 0.7):
        """
        Initialize the FunkyCoder with API key and configuration settings.
        
        Args:
            api_key: OpenAI API key
            system_message: Initial system instructions for the agent
            model: LLM model to use
            max_tokens: Maximum tokens for completion
            temperature: Temperature for completion (0-1)
        """
        self.__conversation = [{"role": "system", "content": system_message}]
        self.__api_key = api_key
        self.__model = model
        self.__max_tokens = max_tokens
        self.__temperature = temperature

    def set_system_message(self, system_message: str) -> None:
        self.__conversation.append({"role": "system", "content": system_message})

    def prompt(self, user_input: str) -> str:
        """
        Send a prompt to the LLM and get a response.
        
        Args:
            user_input: The user's input text
            
        Returns:
            The assistant's response
        """
        self.__conversation.append({"role": "user", "content": user_input})
        try:
            response = completion(
                messages = self.__conversation,
                model = self.__model,
                temperature = self.__temperature,
                max_tokens = self.__max_tokens,
                top_p = 1,
                frequency_penalty = 0,
                presence_penalty = 0
            )
            assistant_response = response.choices[0].message.content
            self.__conversation.append({"role": "assistant", "content": assistant_response})
            return assistant_response
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            print(error_msg)
            return error_msg
    
    def save_to_file(self, filename: str):
        """
        Save the entire conversation to a file.
        
        Args:
            filename: Path to the output file
        """
        try:
            with open(filename, "w") as file:
                for message in self.__conversation:
                    role = message["role"]
                    content = message["content"]
                    file.write(f"=== {role.upper()} ===\n{content}\n\n")
            print(f"Conversation saved to {filename}")
        except Exception as e:
            print(f"Error saving file: {str(e)}")
    
    def extract_code(self) -> str:
        """
        Extract Python code from the conversation.
        
        Returns:
            String containing all Python code found in the conversation
        """
        code_blocks = []
        pattern = r"```python\n(.*?)```"
        
        for message in self.__conversation:
            if message["role"] == "assistant":
                matches = re.findall(pattern, message["content"], re.DOTALL)
                code_blocks.extend(matches)

        return code_blocks[-1:][0] if code_blocks else None
    
    def save_code_to_file(self, filename: str) -> bool:
        """
        Extract code from the conversation and save it to a Python file.
        
        Args:
            filename: Path to the output Python file
            
        Returns:
            True if successful, False otherwise
        """
        code = self.extract_code()
        if not code:
            print("No code found in the conversation.")
            return False
            
        try:
            with open(filename, "w") as file:
                file.write(code)
            print(f"Code saved to {filename}")
            return True
        except Exception as e:
            print(f"Error saving code: {str(e)}")
            return False
    
    def reset_conversation(self, keep_system_message: bool = True):
        """
        Reset the conversation history.
        
        Args:
            keep_system_message: Whether to keep the system message
        """
        system_message = self.__conversation[0] if keep_system_message else None
        self.__conversation = [system_message] if system_message else []
        print("Conversation reset.")
    
    def show_history(self):
        """Print the conversation history."""
        for idx, message in enumerate(self.__conversation):
            role = message["role"]
            if role == "system":
                continue
            print(f"\n--- Message {idx} ({role}) ---")
            print(message["content"])

def is_valid_filename(filename: str) -> bool:
    """
    Check if the filename is valid.
    
    Args:
        filename: The filename to check
        
    Returns:
        True if valid, False otherwise
    """
    invalid_chars = r'<>:"/\\|?*'
    return not any(char in filename for char in invalid_chars)

def get_header(is_slang: bool = False) -> str:
    if is_slang:
        return """
-------------------------------
| 🕺 F U N K Y  C O D E R 🧠 |
-------------------------------"""
    else:
        return """
-------------------------------
|    F U N K Y  C O D E R    |
-------------------------------"""

def get_welcome(is_slang: bool = False) -> str:
    if is_slang:
        return random.choice(data["welcomes"][1:])
    else:
        return data["welcomes"][0]

def get_tagline(is_slang: bool = False) -> str:
    if is_slang:
        return random.choice(data["taglines"][1:])
    else:
        return data["taglines"][0]

def get_description(is_slang: bool = False) -> str:
    if is_slang:
        return random.choice(data["descriptions"][1:])
    else:
        return data["descriptions"][0]

def get_slang(command: str) -> str:
    return data["commands"][command]["slang"]

def get_help_commands(is_slang: bool = False) -> str:
    if is_slang:
        output = """🛠️ Funky System Moves
Here's the menu of righteous commands:"""
    else:
        output = "System Commands:"
    for command in data["commands"]:
        if is_slang:
            output += f"\n>{get_slang(command)} -- {data['commands'][command]['slang_description']}"
        else:
            output += f"\n>{command} -- {data['commands'][command]['description']}"
    return output

def get_examples(is_slang: bool = False) -> str:
    if is_slang:
        return """📦 Examples for the Groovy Newbies
You: >stash surf_log.txt  
You: >ripcord beachbot.py  
You: >peaceout"""
    else:
        return """Examples:
You: >save conversation.txt  
You: >code my_function.py  
You: >exit"""

def get_system_command_instruction(is_slang: bool = False) -> str:
    if is_slang:
        return """🎮 Game Rules (a.k.a. Commands)
-------------------------------
Start your magic spells with a > to make the system do stuff instead of chatting with the coder homie."""
    else:
        return """How to use the System Commands
-------------------------------
Use the '>' character to signal a system command (instead of instructions for Funky Coder)."""

def get_exit_message(is_slang: bool = False) -> str:
    if is_slang:
        return "\n>Ciao baby!\n"
    else:
        return "\n>Goodbye!\n"

def get_user_call_to_action(is_slang: bool = False) -> str:
    if is_slang:
        return "🔥 Let's cook up a Python function that slaps.\nNow it's your turn! I'm listening..."
    else:
        return "Let's work on a Python function together!\nI'm here to do the coding."

def show_help(is_slang: bool = False):
    print(get_header(is_slang))
    print("\n" + get_welcome(is_slang))
    print("\n" + get_tagline(is_slang))
    print("\n" + get_description(is_slang))
    print("\n" + get_system_command_instruction(is_slang))
    print("\n" + get_help_commands(is_slang))
    print("\n" + get_examples(is_slang))
    print("\n" + get_user_call_to_action(is_slang))

def get_system_message(is_slang: bool = False) -> str:
    if is_slang:
        return data["system_message"]["slang"]
    else:
        return data["system_message"]["normal"]

def main():
    is_slang = False

    load_dotenv(override=True)
    api_key = os.environ.get(EXPECTED_API_KEY_NAME)
    if not api_key:
        print(f"Error: {EXPECTED_API_KEY_NAME} environment variable not set.")
        return

    system_message = get_system_message(is_slang)

    # Create the agent
    agent = FunkyCoder(api_key, system_message)
    is_first_user_input = True

    # Start the conversation
    
    while True:
        if is_first_user_input:
            show_help()
            is_first_user_input = False
            
        user_input = input("\nYou: ")

        # check for commands
        if user_input.startswith(">"):
            command = user_input[1:].strip()
            if command.lower() == "help" or command.lower() == data["commands"]["help"]["slang"]:
                show_help()
                continue
            if command.lower() == "exit" or command.lower() == "quit" or command.lower() == data["commands"]["exit"]["slang"]:
                break # exit the loop
            elif command.lower().startswith("save ") or command.lower().startswith(data["commands"]["save"]["slang"]+" "):
                filename = command[5:].strip()
                agent.save_to_file(filename)
                continue
            elif command.lower().startswith("code ") or command.lower().startswith(data["commands"]["code"]["slang"]+" "):
                filename = command[5:].strip()
                agent.save_code_to_file(filename)
                continue
            elif command.lower() == "clear" or command.lower() == data["commands"]["clear"]["slang"]:
                os.system("cls" if os.name == "nt" else "clear")
                continue
            elif command.lower() == "history" or command.lower() == data["commands"]["history"]["slang"]:
                agent.show_history()
                continue
            elif command.lower() == "slang" or command.lower() == data["commands"]["slang"]["slang"]:
                is_slang = True
                show_help(is_slang)
                agent.set_system_message(get_system_message(is_slang))
                continue
            elif command.lower() == "normal" or command.lower() == data["commands"]["normal"]["slang"]:
                is_slang = False
                show_help(is_slang)
                agent.set_system_message(get_system_message(is_slang))
                continue
        else:
            response = agent.prompt(user_input)
            print(f"\nAgent: {response}")
    
    print("\n", get_exit_message(is_slang))

if __name__ == "__main__":
    main()

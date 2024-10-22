import tkinter as tk
from tkinter import scrolledtext
import subprocess
import re

class LlamaGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("Llama Model Interface")

        # Set the initial dark background color of the main window
        self.master.configure(bg='#2E2E2E')

        # Define a font size
        self.font_size = 12  # You can adjust this value as needed
        self.font = ('Arial Rounded MT Bold', self.font_size)

        # Output Textbox with dark background and light text
        self.output_text = scrolledtext.ScrolledText(
            master, width=125, height=25, wrap=tk.WORD,
            bg='#3B3B3B', fg='white', font=self.font,
            selectbackground='lightblue',  # Background color when selecting text
            selectforeground='black'  # Text color when selecting text
        )
        self.output_text.pack(pady=10)

        # Create tags for highlighting
        self.output_text.tag_configure("user", foreground="white", background="#3B3B3B")  # User messages in white
        self.output_text.tag_configure("bot", foreground="cyan", background="#3B3B3B")      # Bot responses in cyan

        # Input Frame to hold prompt entry and button
        self.input_frame = tk.Frame(master, bg='#2E2E2E')  # Set frame background to dark
        self.input_frame.pack(pady=10)

        # Input Label with light text
        self.label = tk.Label(self.input_frame, text="Enter your prompt:", bg='#2E2E2E', fg='white', font=self.font)
        self.label.pack(side=tk.LEFT)

        # Input Textbox (using ScrolledText for scrollability) with dark background and light text
        self.prompt_entry = scrolledtext.ScrolledText(
            self.input_frame, width=100, height=3, wrap=tk.WORD,
            bg='#3B3B3B', fg='white', insertbackground='white', font=self.font,
            selectbackground='lightblue',  # Background color when selecting text
            selectforeground='black'  # Text color when selecting text
        )
        self.prompt_entry.pack(side=tk.LEFT, padx=5)

        # Send Button with light text
        self.send_button = tk.Button(self.input_frame, text="Send", command=self.generate_response, bg='#3B3B3B', fg='white', font=self.font)
        self.send_button.pack(side=tk.LEFT)

        # Bind Enter key to the generate_response method
        self.prompt_entry.bind("<Return>", self.submit_prompt)

        # Initialize conversation history
        self.conversation_history = []
        self.first_prompt = True  # Flag to track the first prompt

        # Loading Label
        self.loading_label = tk.Label(master, text="Loading...", bg='#2E2E2E', fg='cyan', font=self.font)
        self.loading_label.pack(pady=10)
        self.loading_label.pack_forget()  # Initially hide the loading label

    def submit_prompt(self, event):
        """Called when Enter key is pressed."""
        self.generate_response()

    def generate_response(self):
        prompt = self.prompt_entry.get("1.0", tk.END).strip()  # Get all text from ScrolledText
        if prompt:
            # Disable the button and input field while processing
            self.send_button.config(state=tk.DISABLED)
            self.prompt_entry.config(state=tk.DISABLED)

            # Show loading label
            self.loading_label.pack(pady=10)

            # Run the Ollama command in a separate thread to avoid blocking the UI
            self.master.after(100, self.run_ollama_and_display_response, prompt)

    def run_ollama_and_display_response(self, prompt):
        """Runs the Ollama command and displays the response."""
        response = self.run_ollama(prompt)
        cleaned_string = re.sub(
            r'failed to get console mode for (stdout|stderr): The handle is invalid.\s*', '',
            response
        )
        
        # Append to conversation history
        self.conversation_history.append((prompt, cleaned_string))
        
        # Check if this is the first prompt and format output accordingly
        if not self.first_prompt:
            self.output_text.insert(tk.END, "\n", "user")  # Add a new line before subsequent prompts
        self.output_text.insert(tk.END, f"You: {prompt}", "user")  # Insert user message

        # Start gradual output of the bot response
        self.output_text.insert(tk.END, f"\nBot: ", "bot")  # Add newline before bot response
        self.output_bot_response(cleaned_string)

        # Hide loading label and enable input
        self.loading_label.pack_forget()
        self.send_button.config(state=tk.NORMAL)
        self.prompt_entry.config(state=tk.NORMAL)

        # Clear input field after bot response is fully displayed
        self.prompt_entry.delete("1.0", tk.END)  # Clear the ScrolledText

        # Update the first prompt flag
        self.first_prompt = False

    def output_bot_response(self, response):
        """Outputs the bot response gradually, preserving structure."""
        # Split by spaces but keep track of newlines and whitespace
        words = response.split(' ')
        self.current_word_index = 0

        def display_next_word():
            if self.current_word_index < len(words):
                word = words[self.current_word_index]
                
                # Check for newlines and insert them as necessary
                if word == '':
                    # If the word is empty, we encountered consecutive spaces, we just skip it
                    self.current_word_index += 1
                    return display_next_word()

                # Insert the word with cyan highlight
                self.output_text.insert(tk.END, word, "bot")  
                self.current_word_index += 1
                
                # Add a space if it's not the last word
                if self.current_word_index < len(words):
                    self.output_text.insert(tk.END, ' ', "bot")  # Add a space between words
                
                self.output_text.yview(tk.END)  # Scroll to the end
                self.master.after(100, display_next_word)  # Adjust the delay for speed
            else:
                # Enable the button after processing
                self.send_button.config(state=tk.NORMAL)

        display_next_word()  # Start displaying words

    def run_ollama(self, prompt):
        """Runs the Ollama command and returns the model's output."""
        try:
            # Set creationflags to subprocess.CREATE_NO_WINDOW to avoid console window
            result = subprocess.run(
                ["ollama", "run", "llama3.2:1b-instruct-q3_K_M", prompt],
                stdout=subprocess.PIPE,  # Capture standard output
                stderr=subprocess.PIPE,   # Capture standard error
                text=True,                # Capture output as text
                check=True,               # Raise an error if the command fails
                creationflags=subprocess.CREATE_NO_WINDOW  # Suppress console window
            )
            return result.stdout.strip()  # Return the model's output
        except subprocess.CalledProcessError as e:
            return f"Error: {e.stderr.strip()} \n\n"

if __name__ == "__main__":
    root = tk.Tk()
    gui = LlamaGUI(root)
    root.mainloop()

import tkinter as tk
from tkinter import scrolledtext
import threading
import Llama_API 

class LlamaGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("Llama Model Interface")
        self.master.configure(bg='#2E2E2E')  # Dark background

        # Font settings
        self.font = ('Arial Rounded MT Bold', 12)

        # Create a top frame to hold the "New" and "Stop" buttons
        self.top_frame = tk.Frame(master, bg='#2E2E2E')
        self.top_frame.pack(fill=tk.X, pady=5, padx=5)

        # New Button to clear chat session
        self.new_button = tk.Button(
            self.top_frame, text="New", command=self.clear_session,
            bg='cyan', fg='black', font=self.font, activebackground='gray'
        )
        self.new_button.pack(side=tk.LEFT, padx=5)

        # Stop Button to halt the model response
        self.stop_button = tk.Button(
            self.top_frame, text="Stop", command=self.stop_response,
            bg='cyan', fg='black', font=self.font, activebackground='gray'
        )
        self.stop_button.pack(side=tk.LEFT, padx=5)

        # Output Textbox (Scrollable)
        self.output_text = scrolledtext.ScrolledText(
            master, width=125, height=25, wrap=tk.WORD,
            bg='#3B3B3B', fg='white', font=self.font,
            selectbackground='lightblue', selectforeground='black'
        )
        self.output_text.pack(pady=10)
        self.output_text.tag_configure("user", foreground="white")
        self.output_text.tag_configure("bot", foreground="cyan")

        # Input Frame
        self.input_frame = tk.Frame(master, bg='#2E2E2E')
        self.input_frame.pack(pady=10)

        # Label for input prompt
        self.label = tk.Label(self.input_frame, text="Enter your prompt:", bg='#2E2E2E', fg='white', font=self.font)
        self.label.pack(side=tk.LEFT)

        # Input Textbox (Scrollable)
        self.prompt_entry = scrolledtext.ScrolledText(
            self.input_frame, width=100, height=3, wrap=tk.WORD,
            bg='#3B3B3B', fg='white', insertbackground='white', font=self.font,
            selectbackground='lightblue', selectforeground='black'
        )
        self.prompt_entry.pack(side=tk.LEFT, padx=5)
        self.prompt_entry.bind("<Return>", self.submit_prompt)  # Bind Enter key

        # Send Button
        self.send_button = tk.Button(
            self.input_frame, text="Send", command=self.generate_response,
            bg='cyan', fg='black', font=self.font, activebackground='gray'
        )
        self.send_button.pack(side=tk.LEFT)

        # Loading Label (Initially hidden)
        self.loading_label = tk.Label(master, text="Generating...", bg='#2E2E2E', fg='cyan', font=self.font)
        self.loading_label.pack(pady=10)
        self.loading_label.pack_forget()

        # Track first prompt and active response thread
        self.first_prompt = True
        self.response_thread = None  # Track the response thread
        self.stop_requested = False  # Track if stop has been requested
        self.is_generating = False  # Track if a response is currently being generated

        # Bind Ctrl + N and Ctrl + S keyboard shortcuts
        self.master.bind("<Control-n>", self.clear_session_event)
        self.master.bind("<Control-s>", self.stop_response_event)

    def submit_prompt(self, event=None):
        """Called when the Enter key is pressed."""
        self.generate_response()

    def generate_response(self):
        """Handles the user input and displays bot response."""
        prompt = self.prompt_entry.get("1.0", tk.END).strip()  # Get user input
        if prompt:
            if not self.first_prompt:
                self.output_text.insert(tk.END, "\n", "user")  # Add newline between prompts

            self.output_text.insert(tk.END, f"You: {prompt}\n", "user")  # Insert user message
            self.prompt_entry.delete("1.0", tk.END)  # Clear input field

            # Disable input while processing
            self.send_button.config(state=tk.DISABLED)
            self.prompt_entry.config(state=tk.DISABLED)
            self.new_button.config(state=tk.DISABLED)  # Disable the New button
            self.loading_label.pack()  # Show loading label

            # Reset stop request flag
            self.stop_requested = False
            self.is_generating = True  # Set generating flag

            # Create a thread to fetch response to avoid blocking the UI
            self.response_thread = threading.Thread(target=self.fetch_bot_response_chunks, args=(prompt,))
            self.response_thread.start()

            self.first_prompt = False  # Update first prompt flag

    def fetch_bot_response_chunks(self, prompt):
        """Fetches the bot response using the Llama API from Llama_API module."""
        try:
            response = Llama_API.get_response(prompt, stream=True)  # Use the API function

            self.output_text.insert(tk.END, "Bot: ", "bot")  # Insert bot prefix

            # Display chunks as they arrive
            self.display_response_chunks(response)
        except Exception as e:
            self.output_text.insert(tk.END, f"\nError: {str(e)}\n", "bot")
            self.reset_input_state()

    def display_response_chunks(self, response):
        """Displays each chunk of the response as it arrives."""
        try:
            for chunk in response:
                if self.stop_requested:
                    self.output_text.insert(tk.END, "\n[Response Stopped]\n", "bot")
                    break  # Stop processing further chunks

                content = chunk.get('message', {}).get('content', '')
                self.output_text.insert(tk.END, content, "bot")
                self.output_text.yview(tk.END)  # Scroll to the end
                self.master.update_idletasks()  # Update UI immediately

            # Reset input state after completion
            self.reset_input_state()
        except Exception as e:
            self.output_text.insert(tk.END, f"\nError: {str(e)}\n", "bot")
            self.reset_input_state()

    def reset_input_state(self):
        """Re-enables the input fields and hides the loading label."""
        self.loading_label.pack_forget()
        self.send_button.config(state=tk.NORMAL)
        self.prompt_entry.config(state=tk.NORMAL)
        self.new_button.config(state=tk.NORMAL)  # Re-enable the New button
        self.is_generating = False  # Clear generating flag

    def clear_session(self):
        """Clears the chat session and resets the interface."""
        self.output_text.delete("1.0", tk.END)  # Clear chat box
        self.first_prompt = True  # Reset first prompt flag
        self.stop_requested = False  # Reset stop flag

        # Reset button colors
        self.new_button.config(bg='gray')
        self.master.after(200, lambda: self.new_button.config(bg='cyan'))

        self.send_button.config(bg='cyan')
        self.stop_button.config(bg='cyan')

    def clear_session_event(self, event):
        """Handles Ctrl + N keyboard event to clear session."""
        if not self.is_generating:  # Check if the model is not generating
            self.clear_session()

    def stop_response(self):
        """Stops the bot's response."""
        if self.response_thread and self.response_thread.is_alive():
            self.stop_requested = True  # Set stop flag

        # Change Stop button color temporarily
        self.stop_button.config(bg='gray')
        self.master.after(200, lambda: self.stop_button.config(bg='cyan'))

    def stop_response_event(self, event):
        """Handles Ctrl + S keyboard event to stop response."""
        self.stop_response()

if __name__ == "__main__":
    root = tk.Tk()
    gui = LlamaGUI(root)
    root.mainloop()

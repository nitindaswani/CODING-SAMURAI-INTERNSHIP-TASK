import random
import tkinter as tk
from tkinter import messagebox


class NumberGuessingGame:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Number Guessing Game")
        self.root.geometry("420x320")
        self.root.resizable(False, False)

        self.min_number = 1
        self.max_number = 100
        self.max_attempts = 10

        self.target_number = random.randint(self.min_number, self.max_number)
        self.attempts = 0

        self._build_ui()

    def _build_ui(self) -> None:
        title = tk.Label(
            self.root,
            text="Guess The Number",
            font=("Segoe UI", 18, "bold"),
            pady=10,
        )
        title.pack()

        instructions = tk.Label(
            self.root,
            text=f"Enter a number between {self.min_number} and {self.max_number}.",
            font=("Segoe UI", 11),
        )
        instructions.pack()

        self.attempts_label = tk.Label(
            self.root,
            text=f"Attempts: {self.attempts}/{self.max_attempts}",
            font=("Segoe UI", 11),
            pady=10,
        )
        self.attempts_label.pack()

        self.entry = tk.Entry(self.root, font=("Segoe UI", 12), justify="center")
        self.entry.pack(pady=8)
        self.entry.bind("<Return>", lambda _event: self.check_guess())

        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=8)

        submit_btn = tk.Button(
            button_frame,
            text="Submit Guess",
            font=("Segoe UI", 10, "bold"),
            command=self.check_guess,
            width=14,
        )
        submit_btn.grid(row=0, column=0, padx=6)

        restart_btn = tk.Button(
            button_frame,
            text="Restart",
            font=("Segoe UI", 10, "bold"),
            command=self.restart_game,
            width=10,
        )
        restart_btn.grid(row=0, column=1, padx=6)

        self.feedback_label = tk.Label(
            self.root,
            text="Start guessing!",
            font=("Segoe UI", 12),
            fg="#1b5e20",
            pady=10,
        )
        self.feedback_label.pack()

    def _update_attempts(self) -> None:
        self.attempts_label.config(text=f"Attempts: {self.attempts}/{self.max_attempts}")

    def check_guess(self) -> None:
        guess_text = self.entry.get().strip()

        if not guess_text:
            messagebox.showwarning("Input Error", "Please enter a number.")
            return

        if not guess_text.isdigit():
            messagebox.showwarning("Input Error", "Only numeric values are allowed.")
            return

        guess = int(guess_text)
        if guess < self.min_number or guess > self.max_number:
            messagebox.showwarning(
                "Input Error",
                f"Please enter a number between {self.min_number} and {self.max_number}.",
            )
            return

        self.attempts += 1
        self._update_attempts()

        if guess < self.target_number:
            self.feedback_label.config(text="Too Low! Try again.", fg="#b71c1c")
        elif guess > self.target_number:
            self.feedback_label.config(text="Too High! Try again.", fg="#b71c1c")
        else:
            self.feedback_label.config(
                text=f"Correct! You guessed it in {self.attempts} attempts.",
                fg="#1b5e20",
            )
            messagebox.showinfo("You Win", "Great job! Click Restart to play again.")
            return

        if self.attempts >= self.max_attempts:
            messagebox.showinfo(
                "Game Over",
                f"No attempts left. The correct number was {self.target_number}.",
            )
            self.feedback_label.config(
                text=f"Game Over! Number was {self.target_number}.",
                fg="#b71c1c",
            )

        self.entry.delete(0, tk.END)

    def restart_game(self) -> None:
        self.target_number = random.randint(self.min_number, self.max_number)
        self.attempts = 0
        self._update_attempts()
        self.feedback_label.config(text="New game started!", fg="#1b5e20")
        self.entry.delete(0, tk.END)


def main() -> None:
    root = tk.Tk()
    NumberGuessingGame(root)
    root.mainloop()


if __name__ == "__main__":
    main()

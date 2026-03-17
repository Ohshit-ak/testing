"""Main entry point for the MoneyPoly game. Handles player setup and starts the game loop."""
from moneypoly.game import Game

def get_player_names():
    """Prompt the user to enter player names, separated by commas. Returns a list of names."""
    print("Enter player names separated by commas (minimum 2 players):")
    raw = input("> ").strip()
    names = [n.strip() for n in raw.split(",") if n.strip()]
    return names


def main():
    """Main function to set up and run the MoneyPoly game."""
    names = get_player_names()
    try:
        game = Game(names)
        game.run()
    except KeyboardInterrupt:
        print("\n\n  Game interrupted. Goodbye!")
    except ValueError as exc:
        print(f"Setup error: {exc}")


if __name__ == "__main__":
    main()

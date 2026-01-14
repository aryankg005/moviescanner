import moviesearcher
import parent
import os

def main():
    # Clear screen for better look
    os.system('cls' if os.name == 'nt' else 'clear')
    
    query = input("Enter movie name: ")
    movies = moviesearcher.search_imdb(query)

    if not movies:
        print("No results found.")
        return

    print("\n--- Found Movies ---")
    for i, m in enumerate(movies[:8], start=1):
        print(f"{i}. {m['display']}")
    
    choice = int(input("\nSelect movie number: ")) - 1
    selected = movies[choice]
    
    print(f"\nAnalyzing: {selected['display']}")
    print("1. Gore & Violence\n2. Nudity & Sexual Content")
    cat_input = input("Selection: ")
    category = "violence" if cat_input == "1" else "nudity"
    
    print(f"\n--- Loading {category.upper()} Details ---\n")
    severity, details = parent.get_advisory_details(selected['id'], category)
    
    print(f"OVERALL RATING: {severity.upper()}\n")
    print("DETAILED INCIDENTS:")
    
    if not details:
        print("• No specific descriptions available.")
    else:
        for entry in details:
            # Print as a bullet point with a newline for readability
            print(f"• {entry}")
            print("-" * 10) # Small divider between incidents

if __name__ == "__main__":
    main()
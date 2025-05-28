from rich.console import Console
from rich.text import Text

console = Console()

# --- Pixel Art Generation Settings ---
BLOCK = "█"
EMPTY = " "

# Colors
MAIN_COLOR_STYLE = "bold #1D428A"   # Darker NBA Blue for letters
RULE_LINE_COLOR_STYLE = "bold #1D428A" # Same blue for rule lines

# Letter definitions (7 rows high)
LETTERS = {
    'C': [
        " ##### ",
        " #     ",
        " #     ",
        " #     ",
        " #     ",
        " #     ",
        " ##### "
    ],
    'H': [
        " #   # ",
        " #   # ",
        " #   # ",
        " ##### ",
        " #   # ",
        " #   # ",
        " #   # "
    ],
    'A': [
        " ##### ",
        " #   # ",
        " #   # ",
        " ##### ",
        " #   # ",
        " #   # ",
        " #   # "
    ],
    'T': [
        "#######",
        "  ###  ",
        "  ###  ",
        "  ###  ",
        "  ###  ",
        "  ###  ",
        "  ###  "
    ],
    'N': [
        "##   ##",
        "###  ##",
        "#### ##",
        "## ####",
        "## ### ",
        "##  ## ",
        "##   ##"
    ],
    'B': [
        " ####  ",
        " #   # ",
        " #   # ",
        " ####  ",
        " #   # ",
        " #   # ",
        " ####  "
    ],
    ' ': [
        "   ",
        "   ",
        "   ",
        "   ",
        "   ",
        "   ",
        "   "
    ]
}

LETTER_HEIGHT = 7

GLITCH_OFFSET_X = 2 # This will only apply if any letters are targeted for glitch
GLITCH_ROWS_INDICES = [2, 3, 4]

# Define which letters to apply the glitch effect to
GLITCH_TARGETS_WORD1 = {}  # No glitch for "CHAT"
GLITCH_TARGETS_WORD2 = {}  # No glitch for "NBA" (removed 'B')

def generate_styled_art(text_part1, text_part2, console_instance):
    words_data = []

    for char_code in text_part1:
        is_glitched = char_code in GLITCH_TARGETS_WORD1
        words_data.append({
            'char': char_code,
            'is_glitched': is_glitched,
            'definition': LETTERS.get(char_code)
        })
    
    words_data.append({
        'char': ' ',
        'is_glitched': False, # Space is never glitched
        'definition': LETTERS.get(' ')
    })
    
    for char_code in text_part2:
        is_glitched = char_code in GLITCH_TARGETS_WORD2
        words_data.append({
            'char': char_code,
            'is_glitched': is_glitched,
            'definition': LETTERS.get(char_code)
        })

    canvas_width_chars = 0
    for char_data in words_data:
        if char_data['definition']:
            canvas_width_chars += len(char_data['definition'][0])
    
    # Calculate max possible width considering potential glitch (even if none active)
    # If no letters are glitched, GLITCH_OFFSET_X won't effectively add width if is_glitched is false for all.
    # However, to be safe for canvas sizing, we include it. The actual_render_width will trim later.
    max_possible_glitch_for_any_letter = 0
    if GLITCH_TARGETS_WORD1 or GLITCH_TARGETS_WORD2: # Check if any glitch is active
        max_possible_glitch_for_any_letter = GLITCH_OFFSET_X

    canvas_width = canvas_width_chars + max_possible_glitch_for_any_letter
    canvas_height = LETTER_HEIGHT

    EMPTY_CELL_DATA = (EMPTY, None)
    canvas = [[EMPTY_CELL_DATA for _ in range(canvas_width)] for _ in range(canvas_height)]

    current_x_base = 0

    for char_data in words_data:
        char_definition = char_data['definition']
        is_glitched = char_data['is_glitched']

        if not char_definition:
            # Fallback for space or undefined characters
            current_x_base += len(LETTERS[' '][0]) if char_data['char'] == ' ' else 3
            continue
            
        char_def_width = len(char_definition[0])
        
        for r_idx, row_str in enumerate(char_definition):
            # Glitch shift will be 0 if is_glitched is False
            glitch_shift = GLITCH_OFFSET_X if is_glitched and r_idx in GLITCH_ROWS_INDICES else 0
            for c_idx, pixel in enumerate(row_str):
                if pixel == '#':
                    cr = r_idx 
                    cc = current_x_base + c_idx + glitch_shift
                    if 0 <= cr < canvas_height and 0 <= cc < canvas_width:
                        canvas[cr][cc] = (BLOCK, MAIN_COLOR_STYLE)
        
        current_x_base += char_def_width

    # Determine the actual maximum width used on the canvas
    actual_render_width = 0
    for r in range(canvas_height):
        for c in range(canvas_width - 1, -1, -1): # Iterate from right to left
            if canvas[r][c][0] != EMPTY:
                actual_render_width = max(actual_render_width, c + 1)
                break # Found the last character in this row
    
    # If nothing was drawn, default to a small width to avoid issues
    if actual_render_width == 0 and canvas_width_chars > 0 :
        actual_render_width = canvas_width_chars


    output_lines_text = []
    for r in range(canvas_height):
        line_text_obj = Text()
        has_content_in_row = False
        # Iterate up to the actual content width to avoid trailing spaces in Text object
        for c in range(actual_render_width): 
            char_to_print, style = canvas[r][c]
            line_text_obj.append(char_to_print, style=style if style else "")
            if char_to_print != EMPTY:
                has_content_in_row = True
        
        # Only add line if it has content or is within the defined letter height
        # This ensures all 7 rows are printed, even if a row of a letter is all spaces
        if has_content_in_row or r < LETTER_HEIGHT :
             output_lines_text.append(line_text_obj)

    # Trim empty Text objects from the bottom, just in case
    final_lines_to_print = []
    for line_obj in reversed(output_lines_text):
        if line_obj.plain.strip() or final_lines_to_print: # Keep if non-space or if we've kept subsequent lines
            final_lines_to_print.append(line_obj)
    final_lines_to_print.reverse()


    for line_text_obj in final_lines_to_print:
        console_instance.print(line_text_obj)


def print_banner():
    console.rule(style=RULE_LINE_COLOR_STYLE)
    generate_styled_art("CHAT", "NBA", console)
    console.rule(style=RULE_LINE_COLOR_STYLE)

if __name__ == "__main__":
    print_banner()
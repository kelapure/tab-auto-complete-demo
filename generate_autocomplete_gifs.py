import os
import random
from PIL import Image, ImageDraw, ImageFont

class GifGenerator:
    def __init__(self, config):
        self.config = config
        self.width = 1400
        self.height = 220
        self.font_size = 24
        self.font = self._load_font()
        
    def _load_font(self):
        # Prioritize macOS monospace fonts for that authentic terminal look
        candidates = [
            "/System/Library/Fonts/Monaco.ttf",
            "/System/Library/Fonts/Menlo.ttc",
            "/Library/Fonts/Courier New.ttf",
            "/System/Library/Fonts/Supplemental/Courier New.ttf",
            "arial.ttf"
        ]
        for path in candidates:
            if os.path.exists(path):
                try:
                    return ImageFont.truetype(path, self.font_size)
                except Exception:
                    continue
        return ImageFont.load_default()

    def generate(self, filename):
        frames = []
        fps = 30
        duration_sec = 5.0
        total_frames = int(duration_sec * fps)

        # Colors (Hex equivalents)
        BG_COLOR = (0, 0, 0)
        TEXT_GREY = (128, 128, 128)
        TEXT_DARK_GREY = (96, 96, 96)
        TEXT_WHITE = (230, 230, 230)
        TEXT_YELLOW = (220, 220, 170) # DCDCAA
        TEXT_BLUE = (86, 156, 214)    # 569CD6
        TEXT_RED = (206, 145, 120)    # CE9178
        TEXT_PURPLE = (197, 134, 192) # C586C0
        BORDER_GREY = (51, 51, 51)    # 333333
        CURSOR_COLOR = (204, 204, 204)

        # Content
        input_text = self.config.get('input_text', "")
        suggestion_text = self.config.get('suggestion_text', "")

        # Timing
        t_start_type = 0.5
        t_finish_type = 2.0
        t_show_suggest = 2.4
        t_accept = 3.8

        print(f"Generating {filename}...")

        for f in range(total_frames):
            t = f / fps
            
            img = Image.new('RGB', (self.width, self.height), color=BG_COLOR)
            draw = ImageDraw.Draw(img)
            
            # --- Static UI ---
            
            # Top Left
            draw.text((20, 15), "Using: 1 GEMINI.md file", font=self.font, fill=TEXT_GREY)
            
            # Top Right
            accept_msg = "accepting edits"
            toggle_msg = " (shift + tab to toggle)"
            accept_w = draw.textlength(accept_msg, font=self.font)
            toggle_w = draw.textlength(toggle_msg, font=self.font)
            
            right_margin = 20
            draw.text((self.width - right_margin - accept_w - toggle_w, 15), accept_msg, font=self.font, fill=TEXT_YELLOW)
            draw.text((self.width - right_margin - toggle_w, 15), toggle_msg, font=self.font, fill=TEXT_GREY)
            
            # Bottom Left
            draw.text((20, 170), "~/projects/tab-auto-complete-demo", font=self.font, fill=TEXT_BLUE)
            
            # Bottom Right Area
            auto_txt = "auto"
            auto_w = draw.textlength(auto_txt, font=self.font)
            draw.text((self.width - 20 - auto_w, 170), auto_txt, font=self.font, fill=TEXT_PURPLE)
            
            sandbox_txt = "no sandbox"
            docs_txt = " (see /docs)"
            sandbox_w = draw.textlength(sandbox_txt, font=self.font)
            docs_w = draw.textlength(docs_txt, font=self.font)
            
            # Positioned relative to "auto" with padding
            # Let's give it about 300px spacing as simulated
            ref_x = self.width - 20 - auto_w - 350
            draw.text((ref_x, 170), sandbox_txt, font=self.font, fill=TEXT_RED)
            draw.text((ref_x + sandbox_w, 170), docs_txt, font=self.font, fill=TEXT_GREY)
            
            # --- Prompt Box ---
            box_x, box_y = 20, 60
            box_w, box_h = self.width - 40, 80
            
            # Simple rectangle for border
            draw.rectangle([box_x, box_y, box_x + box_w, box_y + box_h], outline=BORDER_GREY, width=2)
            
            # --- Dynamic Content ---
            
            # Logic
            current_input = ""
            if t > t_start_type:
                if t < t_finish_type:
                    ratio = (t - t_start_type) / (t_finish_type - t_start_type)
                    char_count = int(len(input_text) * ratio)
                    current_input = input_text[:char_count]
                else:
                    current_input = input_text
            
            show_ghost = (t >= t_show_suggest and t < t_accept)
            is_accepted = (t >= t_accept)
            
            final_text = current_input
            if is_accepted:
                final_text = input_text + suggestion_text
                # Box Flash
                if t < t_accept + 0.1:
                    draw.rectangle([box_x+2, box_y+2, box_x+box_w-2, box_y+box_h-2], fill=(30, 30, 30))

            # Draw Prompt Text
            text_start_x = box_x + 20
            text_start_y = box_y + 25 # Vertically centered
            
            prompt_sym = "> "
            draw.text((text_start_x, text_start_y), prompt_sym, font=self.font, fill=TEXT_YELLOW)
            prompt_w = draw.textlength(prompt_sym, font=self.font)
            
            draw.text((text_start_x + prompt_w, text_start_y), final_text, font=self.font, fill=TEXT_WHITE)
            input_w = draw.textlength(final_text, font=self.font)
            
            if show_ghost:
                draw.text((text_start_x + prompt_w + input_w, text_start_y), suggestion_text, font=self.font, fill=TEXT_DARK_GREY)
            
            # Cursor
            cursor_x = text_start_x + prompt_w + input_w
            
            should_blink = True
            if t > t_start_type and t < t_finish_type:
                should_blink = False
                cursor_visible = True
            elif is_accepted and t < t_accept + 0.2:
                cursor_visible = True
            else:
                cursor_visible = (int(t * 2.5) % 2 == 0)
                
            if cursor_visible:
                # Block cursor
                draw.rectangle([cursor_x, text_start_y, cursor_x + 12, text_start_y + self.font_size], fill=CURSOR_COLOR)

            frames.append(img)

        frames[0].save(
            filename,
            save_all=True,
            append_images=frames[1:],
            optimize=False,
            duration=int(1000/fps),
            loop=0
        )
        print(f"Saved {filename}")

# --- Configurations ---

config_alpha = {
    'input_text': 'git commit -m "perf:',
    'suggestion_text': ' improve database query performance by adding indexes to frequently accessed columns and optimizing ORM relationships'
}

config_beta = {
    'input_text': "design",
    'suggestion_text': ' a highly available, fault-tolerant microservices architecture leveraging Kubernetes for container orchestration and Kafka for asynchronous communication'
}

config_gamma = {
    'input_text': "plan",
    'suggestion_text': ' a comprehensive cloud migration strategy from on-premise infrastructure to Google Cloud Platform, including data transfer, application refactoring, and rollback procedures'
}

if __name__ == "__main__":
    gen = GifGenerator(config_alpha)
    gen.generate("autocomplete_alpha.gif")
    
    gen = GifGenerator(config_beta)
    gen.generate("autocomplete_beta.gif")
    
    gen = GifGenerator(config_gamma)
    gen.generate("autocomplete_gamma.gif")


if __name__ == "__main__":
    gen = GifGenerator(config_alpha)
    gen.generate("autocomplete_alpha.gif")
    
    gen = GifGenerator(config_beta)
    gen.generate("autocomplete_beta.gif")
    
    gen = GifGenerator(config_gamma)
    gen.generate("autocomplete_gamma.gif")

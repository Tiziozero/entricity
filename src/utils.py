def get_contrasting_color(color):
    # Simple logic to get a contrasting color
    r, g, b, _ = color
    brightness = (r*0.299 + g*0.587 + b*0.114)
    if brightness > 128:
        return 0x000000
    else:
        return 0xffffff

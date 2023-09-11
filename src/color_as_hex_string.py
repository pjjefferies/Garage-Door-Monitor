from src.controller.color_constants import colors


def color_as_hex_string(color: str | int | tuple[int, int, int]) -> str:
    """
    Convert one of the following formats to output format
        Input:   '0xeed5b7'
                 '#eed5b7'
                 15652279
                 'BISQUE2'
                 (238, 213, 183)
        Output:  '#eed5b7'
    """
    if isinstance(color, str):
        if color.startswith(("0x", "0X")):
            if len(color) == 8:
                try:
                    int(color[2:4], 16)
                    int(color[4:6], 16)
                    int(color[6:8], 16)
                    color = "".join(("#" + color[2:]))
                    return color
                except ValueError:
                    raise ValueError(
                        "0x format must contain 3 valid 2 character hex strings"
                    )
            else:
                raise ValueError(
                    "0x format must contain 3 valid 2 character hex strings"
                )
        if color.startswith("#"):
            if len(color) == 7:
                try:
                    int(color[1:3], 16)
                    int(color[3:5], 16)
                    int(color[5:7], 16)
                    return color
                except ValueError:
                    raise ValueError(
                        "# format must contain 3 valid 2 character hex strings"
                    )
            else:
                raise ValueError(
                    "# format must contain 3 valid 2 character hex strings"
                )
        if color in colors:
            return colors[color.lower()].hex_format()  # e.g.
        else:
            return "#000000"  # Assum Black
        return color
    if isinstance(color, list) and len(color) == 3:
        try:
            red, green, blue = (int(x) for x in color)
            if 0 <= red <= 255 and 0 <= green <= 255 and 0 <= blue <= 255:
                return f"#{hex(red)[-2:]}{hex(green)[-2:]}{hex(blue)[-2:]}"
            raise ValueError
        except ValueError:
            raise ValueError("Int list members must be 0-255 range")
    if isinstance(color, int) and 0 <= color < 2**24:
        color = hex(color)
        return f"#{'0' * (8 - len(color))}{color[2:]}"
    raise ValueError(
        f"No valid color value/name could be found. '{str(color)}' was supplied"
    )

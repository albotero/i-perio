class Colors:
    color_list = {
        'purple': '\033[95m',
        'cyan': '\033[96m',
        'darkcyan': '\033[36m',
        'blue': '\033[94m',
        'green': '\033[92m',
        'yellow': '\033[93m',
        'red': '\033[91m',
        'bold': '\033[1m',
        'underline': '\033[4m',
        'end': '\033[0m'
        }

    def style_str(text, styles = []):
       for style in styles:
           text = '{}{}'.format(Colors.color_list[style], text)
       return '{}{}'.format(text, Colors.color_list['end'])

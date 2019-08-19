import random


def do_hug(target, sender):
    chosen_msg = random.choice(HugMessages)
    chosen_msg = chosen_msg.replace('%%target%%', str(target))
    chosen_msg = chosen_msg.replace('%%sender%%', str(sender))
    return chosen_msg


HugMessages = [
    'Хэй, %%target%%! Тебя только-что обнял **%%sender%%**! **(｡>﹏<｡)**',
    'Ой, как это мило! **%%sender%%** обнял %%target%% :heart:',
    'Ой-ой, %%target%%, кажется... Тебя только что обнял **%%sender%%**! **(≧◡≦)**',
    '***%%sender%%*** *обнимает %%target%%*',
    '**%%sender%%** устроаивает время обнимашек! %%target%%, иди, обниму **(っ˘ω˘ς )**',
]

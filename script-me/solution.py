from pwn import *
import subprocess

context.log_level = 'info'

io = remote('2018shell2.picoctf.com', 61344)
log.debug(io.recvuntil('Let\'s start with a warmup.'))
io.recvline()

with log.progress('Solving') as progress:

  while True:

    problem = io.recvline().strip()

    expression = problem.split('=')[0].strip()

    progress.status(expression)

    try:
      answer = subprocess.check_output(['./ParenCode', expression]).strip()
    except:
      log.warn('solver failed for input: %s', expression)
      break

    io.recvuntil('> ')
    io.sendline(answer)

    result = io.recvline(keepends=False)

    if result == 'Correct!':
      progress.status(result)
      io.recvline()
    elif result == 'Sorry that\'s not correct.':
      io.recvline()
      log.warn(io.recvline(keepends=False))
      log.warn(io.recvline(keepends=False))
      progress.failure("We failed!")
      break
    else:
      log.error(result)
      break

    final_line = io.recvline()

    if final_line.startswith('Congratulations, here\'s your flag: '):
      flag = final_line.strip().split(' ')[-1]
      progress.success(flag)
      break

io.close()

